@AGENTS.md

## Claude Code

- Study sessions start with `/teach`; run it again after a compaction.
- Graded questions use `AskUserQuestion`, and you grade the answer afterwards. Experiment predictions are graded only after the experiment has run (see the teach skill).
- Fact-checking: the `researcher` subagent. Diagrams: the `visualize` skill, which dispatches `mermaid-maker` or `svg-maker`; not the desktop app's `mcp__visualize__*` widgets.
- Use the Bash tool (not PowerShell) for lab commands: `date`, `docker compose ...`, `curl -s http://localhost:...`.
- The learner turns the markdown session log on or off with `/session-log`.
