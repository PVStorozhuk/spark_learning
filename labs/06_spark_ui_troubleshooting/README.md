# Lab 06 — Spark UI + troubleshooting

Runs in JupyterLab (http://localhost:8888), folder `/workspace/labs/06_spark_ui_troubleshooting`.

| UI | URL |
| --- | --- |
| Running application | http://localhost:4040 |
| History Server (finished applications) | http://localhost:18080 |
| Spark master | http://localhost:8080 |

## Data

Generated once from the repository root (also uses `/opt/data/m3/orders_big` and `/opt/data/m4/customers_big`):

```bash
docker compose exec jupyter spark-submit labs/06_spark_ui_troubleshooting/00_make_data.py
```

## Scenarios

Each scenario is a job that misbehaves. The task is the same every time: find out **why** from the Spark UI, and
write it down as

```text
Symptom → Where I looked → Evidence (numbers) → Hypothesis → What I would change → How I would verify
```

| Scenario | What you get |
| --- | --- |
| 1 | `scenario_1.ipynb`: a report job over an events directory that takes longer than its data volume suggests. |
| 2 | Two finished runs of `scenario_2/nightly_report.py` in the History Server: the run for 2026-09-30 and the run for 2026-10-01. The second took several times longer. |
| 3 | `scenario_3.ipynb`: the same job run twice with one configuration value changed. |

Give your diagnosis in chat before asking for the answer. Shut the previous notebook's kernel down before starting the next one.
