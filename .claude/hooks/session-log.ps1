# Session log hook: the Claude Code replacement for the upstream pi md-log extension.
# Appends your prompts, Claude's text, and questions with their answers, in order, to a markdown
# file that Obsidian (or any markdown viewer) can render: notes/sessions/<date>.md by default.
#
# Controlled by notes/sessions/.config, written by the /session-log skill:
#   missing or "off" -> disabled;  "on" -> notes/sessions/;  anything else -> that directory
#   (absolute, or relative to the project root).
#
# Events (see .claude/settings.json):
#   UserPromptSubmit            -> your prompt
#   PreToolUse(AskUserQuestion) -> Claude's text so far in the turn, then the question (before you answer)
#   PostToolUse(AskUserQuestion)-> your answer
#   Stop                        -> the rest of Claude's text in the turn
# Text written earlier in a turn is recovered from the session transcript. Anthropic documents
# that file's format as internal; if reading it fails, the hook falls back to the final reply.
#
# It must never print to stdout (UserPromptSubmit stdout would be injected into the conversation)
# and must always exit 0 (a failing hook must not disturb the lesson).

function Get-LogDir([string]$root) {
    $config = Join-Path $root 'notes\sessions\.config'
    if (-not (Test-Path -LiteralPath $config)) { return $null }
    $value = ([IO.File]::ReadAllText($config)).Trim().Trim('"')
    if (-not $value -or $value -eq 'off') { return $null }
    if ($value -eq 'on') { return (Join-Path $root 'notes\sessions') }
    if ([IO.Path]::IsPathRooted($value)) { return $value }
    return (Join-Path $root $value)
}

function Format-Time($isoTimestamp) {
    try { return ([DateTimeOffset]::Parse([string]$isoTimestamp)).LocalDateTime.ToString('HH:mm') }
    catch { return (Get-Date -Format 'HH:mm') }
}

function Read-SharedText([string]$path) {
    $stream = [IO.File]::Open($path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
    try { return (New-Object IO.StreamReader($stream, [Text.Encoding]::UTF8)).ReadToEnd() }
    finally { $stream.Dispose() }
}

function Test-IsPrompt($entry) {
    if ($entry.type -ne 'user' -or $entry.isMeta -or $entry.isSidechain -or $entry.isCompactSummary) { return $false }
    $content = $entry.message.content
    if ($content -is [string]) { return $true }
    foreach ($block in @($content)) { if ($block.type -eq 'tool_result') { return $false } }
    return $true
}

# The current turn: the id of its opening prompt, and its assistant text blocks, oldest first.
function Get-Turn([string]$transcript) {
    $lines = (Read-SharedText $transcript) -split "`n"
    $found = New-Object System.Collections.ArrayList
    $boundary = $null
    for ($i = $lines.Count - 1; $i -ge 0; $i--) {
        $line = $lines[$i].Trim()
        if (-not $line) { continue }
        try { $entry = $line | ConvertFrom-Json } catch { continue }  # e.g. a line still being written
        if (Test-IsPrompt $entry) { $boundary = $entry.uuid; break }
        if ($entry.type -ne 'assistant' -or $entry.isSidechain) { continue }
        $index = 0
        foreach ($block in @($entry.message.content)) {
            if ($block.type -eq 'text' -and $block.text.Trim()) {
                $found.Insert(0, [pscustomobject]@{
                    Id = "$($entry.uuid):$index"; Text = $block.text.Trim(); Time = (Format-Time $entry.timestamp)
                })
            }
            $index++
        }
    }
    return [pscustomobject]@{ Boundary = $boundary; Texts = $found }
}

function Get-Hash([string]$text) {
    $bytes = [Security.Cryptography.SHA1]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes($text))
    return [BitConverter]::ToString($bytes).Replace('-', '')
}

function Get-Answers($e) {
    if ($e.tool_input.answers) { return $e.tool_input.answers }
    if ($e.tool_response.answers) { return $e.tool_response.answers }
    return $null
}

function Add-Text([string]$path, [string]$text) {
    $utf8 = New-Object Text.UTF8Encoding($false)
    for ($try = 0; $try -lt 10; $try++) {
        try { [IO.File]::AppendAllText($path, $text, $utf8); return }
        catch [IO.IOException] { Start-Sleep -Milliseconds 100 }
    }
    throw "could not append to $path"
}

$mutex = $null
try {
    $root = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { (Get-Location).Path }
    $logDir = Get-LogDir $root
    if (-not $logDir) { exit 0 }

    [Console]::InputEncoding = [Text.Encoding]::UTF8
    $raw = [Console]::In.ReadToEnd()
    if (-not $raw) { exit 0 }
    $e = $raw | ConvertFrom-Json
    $hookEvent = $e.hook_event_name
    $now = Get-Date -Format 'HH:mm'

    # Background notifications arrive as prompts; they are not the learner speaking.
    if ($hookEvent -eq 'UserPromptSubmit' -and "$($e.prompt)".TrimStart().StartsWith('<task-notification>')) { exit 0 }

    # Serialize concurrent hook runs (they may run in the background and overlap).
    $mutex = New-Object Threading.Mutex($false, 'Local\sparklab-session-log')
    try { [void]$mutex.WaitOne(15000) } catch [Threading.AbandonedMutexException] { }

    if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    $file = Join-Path $logDir ((Get-Date -Format 'yyyy-MM-dd') + '.md')
    if (-not (Test-Path -LiteralPath $file)) { Add-Text $file "# Session log $(Get-Date -Format 'yyyy-MM-dd')`n" }

    # Ids of assistant text blocks already written, per session.
    $stateFile = Join-Path $root "notes\sessions\.state-$($e.session_id).txt"
    $logged = @{}
    if (Test-Path -LiteralPath $stateFile) {
        foreach ($id in [IO.File]::ReadAllLines($stateFile)) { if ($id) { $logged[$id] = $true } }
    }

    $parts = New-Object System.Collections.ArrayList
    $newIds = New-Object System.Collections.ArrayList

    # Claude's text from this turn that is not in the log yet.
    $turn = $null
    if ($hookEvent -in @('Stop', 'PreToolUse', 'PostToolUse') -and $e.transcript_path -and (Test-Path -LiteralPath $e.transcript_path)) {
        try {
            $turn = Get-Turn $e.transcript_path
            foreach ($t in $turn.Texts) {
                if ($logged.ContainsKey($t.Id)) { continue }
                [void]$parts.Add("`n### $($t.Time) - Claude`n`n$($t.Text)`n")
                [void]$newIds.Add($t.Id)
            }
        } catch {
            [Console]::Error.WriteLine("session-log hook: transcript not readable, logging final reply only: $_")
        }
    }

    switch ($hookEvent) {
        'UserPromptSubmit' {
            if ($e.prompt) { [void]$parts.Add("`n---`n`n### $now - You`n`n$($e.prompt)`n") }
        }
        'Stop' {
            # The transcript may lag behind the final reply: add it unless this turn already has it.
            $final = "$($e.last_assistant_message)".Trim()
            if ($final) {
                $key = if ($turn -and $turn.Boundary) { "final:$($turn.Boundary):$(Get-Hash $final)" } else { $null }
                $alreadyIn = $false
                foreach ($p in $parts) { if ($p.Contains($final)) { $alreadyIn = $true } }
                if ($key -and $logged.ContainsKey($key)) {
                    # written by an earlier run for this turn
                } elseif ($alreadyIn) {
                    if ($key) { [void]$newIds.Add($key) }
                } else {
                    [void]$parts.Add("`n### $now - Claude`n`n$final`n")
                    if ($key) { [void]$newIds.Add($key) }
                }
            }
        }
        'PreToolUse' {
            $lines = @("", "### $now - Question", "")
            foreach ($q in @($e.tool_input.questions)) {
                $lines += "**$($q.question)**"
                foreach ($o in @($q.options)) { $lines += "- $($o.label)" }
                $lines += ""
            }
            [void]$parts.Add(($lines -join "`n"))
        }
        'PostToolUse' {
            $answers = Get-Answers $e
            $lines = @("")
            foreach ($q in @($e.tool_input.questions)) {
                $answer = if ($answers) { $answers.($q.question) } else { $null }
                if (-not $answer) { $answer = '(no answer recorded)' }
                $lines += "> **Answer:** $answer"
                $lines += ""
            }
            [void]$parts.Add(($lines -join "`n"))
        }
    }

    if ($parts.Count) { Add-Text $file ($parts -join '') }
    if ($newIds.Count) { Add-Text $stateFile (($newIds -join "`n") + "`n") }
} catch {
    # Never disturb the lesson; the error is visible with `claude --debug`.
    [Console]::Error.WriteLine("session-log hook: $_")
} finally {
    if ($mutex) { try { $mutex.ReleaseMutex() } catch { } ; $mutex.Dispose() }
}
exit 0
