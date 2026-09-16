# AGENTS.md

This repository is an intensive Spark interview-prep course (about 1–1.5 weeks).

- When the learner is studying, teach with the `teach` skill (`.claude/skills/teach/SKILL.md`), including its "Course mode" section. If it is not loaded, load it before any teaching turn, and again after context compaction.
- Not every session is a lesson: for repository or environment work (setup, Docker, git, editing course files), just do the work.
- Curriculum: `curriculum/ROADMAP.md`. Progress and evidence: `curriculum/PROGRESS.md`. Teacher reference: `curriculum/TEACHER_NOTES.md` (contains answers; Course mode says when they may be revealed). Paths are relative to the project root.
- Generate a lab in `labs/NN_*/` only when the learner reaches that module. The lab environment is described in the "Lab environment" section of `README.md` (Docker Compose cluster; code runs in the `jupyter` container under `/workspace`).
