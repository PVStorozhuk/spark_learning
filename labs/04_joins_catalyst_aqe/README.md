# Lab 04 — Joins + Catalyst + AQE

Runs in JupyterLab (http://localhost:8888), folder `/workspace/labs/04_joins_catalyst_aqe`. Spark UI: http://localhost:4040.

## Data

Reuses `/opt/data/m1/orders`, `/opt/data/m1/customers` (Module 1) and `/opt/data/m3/orders_big` (Module 3). One new
table, generated once from the repository root:

```bash
docker compose exec jupyter spark-submit labs/04_joins_catalyst_aqe/00_make_data.py
```

| Dataset | Contents |
| --- | --- |
| `/opt/data/m4/customers_big` | 2,000,000 customers: `customer_id`, `tier`, `country`, two wide profile columns |

## Experiments

| Notebook | Question |
| --- | --- |
| `01_join_strategies.ipynb` | Fact + small dimension: which strategy by default? What changes when other strategies are forced? |
| `02_non_equi.ipynb` | A join with no equality condition: what can Spark do? And with broadcasting disabled? |
| `03_bad_estimate_aqe.ipynb` | A dimension that is large on disk but small after a filter: what does the static plan choose, what does AQE do at runtime, and what differs between the initial and the final plan? |

Each **PREDICT** prompt is answered in chat before the cell is run. Shut the previous notebook's kernel down before
starting the next one.
