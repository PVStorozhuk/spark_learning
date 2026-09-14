# Spark for production Data Engineers

A hands-on learning repository for going from Trino + Iceberg + Airflow experience to
confidently building, reading, and tuning **production Spark ETL**.

This is not a Python, SQL, or generic ETL primer. It assumes distributed query plans,
partitioning, and broadcast vs partitioned joins are already familiar, and focuses on what is
specific to Spark: its execution model, physical plans, the Spark UI, shuffles, joins, AQE, skew,
executor memory, and Spark + Iceberg pipelines.

## Layout

| Path | Purpose |
| --- | --- |
| `curriculum/ROADMAP.md` | Target competencies and the ordered list of labs |
| `curriculum/PROGRESS.md` | Lab status and knowledge-edge notes |
| `labs/NN_topic/` | One hands-on lab per topic |
| `capstone/` | End-to-end Spark + Iceberg project that ties the labs together |
| `data/` | Locally generated datasets (contents are git-ignored) |
| `.pi/` | Teaching framework (see below) |

## Teaching framework

`.pi/` is vendored from [amosblomqvist/learn](https://github.com/amosblomqvist/learn) at commit
`7cfd894` (2026-08-26), with its `.git` directory removed. It is otherwise unmodified.

It is a configuration for the [pi](https://github.com/earendil-works/pi) coding agent: run `pi`
from the repository root. The `teach` skill drives each topic as probe → plan → teach, using the
`quiz` and `ask-user-question` extensions; `md-log` mirrors a session to a markdown file.
The researcher and visual-maker subagents need a subagent extension; see `.pi/README.md`.

## Status

Bootstrapped only. Runtime setup (Spark / Java / Iceberg versions) and lab content come next.
