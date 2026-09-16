---
name: session-log
description: Turn the markdown session log on or off, or point it at an Obsidian vault folder. Replaces the upstream md-log command.
disable-model-invocation: true
argument-hint: "on | off | <absolute directory for the log files>"
---

# Session log

The hook `.claude/hooks/session-log.ps1` appends the learner's prompts, your text, and every question
with its answer to a daily markdown file. It reads one setting from `notes/sessions/.config`.

Argument: `$ARGUMENTS`

Write exactly one line to `notes/sessions/.config` (create the folder if needed; use the Write tool):

- `on` (or no argument): write `on`. Logs go to `notes/sessions/<date>.md`, diagrams to `notes/viz/`.
  The learner opens `notes/` as an Obsidian vault.
- `off`: write `off`. Existing log files stay.
- a directory: write its absolute path, with `~` expanded and no quotes. Create the directory if it does not
  exist. Logs go to `<dir>/<date>.md`, diagrams to `<dir>/viz/`, so both stay inside that vault.
  Warn against using the repository root itself as a vault: `curriculum/TEACHER_NOTES.md` contains answers.

Then confirm in one or two sentences: whether logging is on, and the full path of today's log file.
Logging starts from the next message; earlier parts of this session are not backfilled.
