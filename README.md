# Spark for production Data Engineers

A hands-on learning repository for going from Trino + Iceberg + Airflow experience to
confidently building, reading, and tuning **production Spark ETL**.

It is currently in **intensive interview-prep mode**: about 26 hours planned (24h of modules plus a 2h
mini-capstone) over 1–1.5 weeks, prioritizing
what Spark interviews, production ETL, and performance debugging actually need. This is not a Python,
SQL, or generic ETL primer; it focuses on Spark's execution model, physical plans, the Spark UI,
shuffles, joins, AQE, skew and salting, executor memory, and Spark + Iceberg.

## Layout

| Path | Purpose |
| --- | --- |
| `curriculum/ROADMAP.md` | Modules, experiments, schedule, critical interview path, deferred topics |
| `curriculum/PROGRESS.md` | Evidence-based progress, prediction log, drill log, knowledge edges |
| `curriculum/TEACHER_NOTES.md` | Verified facts and answers for the teaching agent (**spoilers**) |
| `labs/NN_topic/` | One lab per module, generated when the module starts |
| `capstone/` | Mini-capstone: diagnose and fix a deliberately slow retail pipeline |
| `data/` | Small local files only (git-ignored); lab datasets live in the Docker `lab-data` volume |
| `compose.yaml`, `env/` | Lab environment: Spark 4.1 standalone cluster + Iceberg (see below) |
| `.claude/` | The teaching system for Claude Code: skills, subagents, session-log hook, settings |
| `CLAUDE.md`, `AGENTS.md` | Always-on context: course files, and when to teach vs. just do repo work |
| `.pi/` | Upstream `learn` framework, unmodified, kept as the reference for the port |
| `notes/` | Personal, git-ignored: session logs and diagrams (open it as an Obsidian vault if you like) |

## Teaching framework

The course is taught by **Claude Code** (desktop app or CLI) with a port of the
[amosblomqvist/learn](https://github.com/amosblomqvist/learn) framework. The upstream is vendored
unmodified in `.pi/` (commit `7cfd894`, 2026-08-26, `.git` removed); it targets the pi agent, which
cannot use a Claude subscription.

| In `.claude/` | What it does | Upstream (pi) equivalent |
| --- | --- | --- |
| `skills/teach/` | Probe → plan → teach, plus this course's **Course mode** (pacing, priorities, predict-first experiments, no-spoiler rules, evidence-based progress) | `skills/teach/` |
| `skills/visualize/` + `agents/mermaid-maker.md`, `agents/svg-maker.md` | Diagrams, rendered to PNG and checked by looking at them (`render.py`: mermaid-cli via `npx`; SVG via `rsvg-convert` or headless Edge/Chrome) | `skills/visualize/`, makers, `visual-tools` extension |
| `agents/researcher.md` | Web fact-checking with built-in WebSearch / WebFetch | `agents/researcher.md` (needed OpenRouter + extra web tools) |
| `hooks/session-log.ps1` + `skills/session-log/` | Markdown log of prompts, Claude's text, and questions with answers in `notes/sessions/`, toggled with `/session-log on`, `off`, or a vault folder | `md-log` extension |
| built-in `AskUserQuestion` | Multiple-choice and graded questions; Claude grades afterwards (predictions only after the experiment) | `quiz`, `ask-user-question` extensions |
| `settings.json` | Hook registration and pre-approved permissions for routine lesson steps (deleting lab volumes always asks) | trust prompt, `.pi/settings.json` |

### Studying

Prerequisites: Claude Code (desktop app or CLI), Docker Desktop, Python 3, Node.js (for Mermaid diagrams),
Microsoft Edge or Chrome (for SVG diagrams), and optionally Obsidian for reading the session log.

1. Start the lab environment and run its smoke test (see below).
2. Optional, once: warm up the diagram renderer, which downloads mermaid-cli and a headless browser:
   `npx -y @mermaid-js/mermaid-cli@11.17.0 --version`
3. `/session-log on`, then open `notes/` as an Obsidian vault to read lessons with rendered math and diagrams.
4. `/teach`, then say which module to start. Run `/teach` again after a compaction.

### What differs from the pi version

- Graded answers arrive in Claude's next message instead of instantly inside the question popup.
  Option shuffling and the "I don't know" choice are rules in the skill rather than tool features.
- Subagents can't ask you anything and run in the background (visible in the tasks pane), not in
  interactive terminal panes. Claude waits for their reports before using them.
- The session log starts when you turn it on (no backfill). Claude's text written earlier in a turn is
  recovered from the session transcript, whose format Anthropic documents as internal; if that ever
  breaks, the log falls back to Claude's final reply per turn.
- As before, math, Mermaid, and `![[...]]` embeds render in Obsidian, not in the chat window.
- Gained: the researcher and the diagram makers work on native Windows, with no WSL, tmux, or API key.
- The subagents' `omitClaudeMd` setting needs Claude Code 2.1.271 or later; on older versions they
  still see this repo's `CLAUDE.md`, which is harmless for them.

## Lab environment

Docker Compose runs a small real cluster, so executors, shuffles, spill, and skew are observable:

| Service | What it is | URL |
| --- | --- | --- |
| `spark-master` | Standalone master | http://localhost:8080 |
| `spark-worker-1`, `spark-worker-2` | Workers, 4 cores / 8GB each (4 executors of 2 cores / 3GB) | http://localhost:8081, http://localhost:8082 |
| `jupyter` | JupyterLab; the Spark driver runs here | http://localhost:8888 |
| (running app) | Spark UI of the active SparkSession | http://localhost:4040 (4041… for more) |
| `spark-history` | History Server for finished apps | http://localhost:18080 |
| `iceberg-catalog-db` | Postgres holding the Iceberg JDBC catalog `lab` | internal only |

Versions: Spark 4.1.3, Java 17, Python 3.10, Iceberg 1.11.0 (Iceberg has no Spark 4.2 runtime yet).
Ports are bound to `127.0.0.1` only.

```bash
docker compose up -d                                   # build (first time) and start
docker compose exec jupyter spark-submit env/smoke_test.py   # verify: ends with SMOKE TEST PASSED
docker compose down                                    # stop (data volumes are kept)
docker compose down -v                                 # stop and delete all lab data
```

- `labs/` and `capstone/` are mounted at `/workspace/` in the Jupyter container. Datasets live in the `lab-data`
  volume at `/opt/data`, and Iceberg tables in the `warehouse` volume, shared by driver and executors.
- Iceberg tables are addressed as `lab.<namespace>.<table>`; `lab` is the default catalog.
- A SparkSession claims all cluster cores. Call `spark.stop()` (or shut the notebook kernel down) before
  starting another application, or the second one waits for resources.
- In Git Bash, avoid absolute container paths in `docker compose exec` commands (Git Bash rewrites `/workspace/...`
  into a Windows path); use paths relative to `/workspace`, or prefix the command with `MSYS_NO_PATHCONV=1`.

## Status

Curriculum designed and lab environment verified. Next: labs, one module at a time.
