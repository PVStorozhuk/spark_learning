# Lab 05 — Data skew + salting

Runs in JupyterLab (http://localhost:8888), folder `/workspace/labs/05_skew_salting`. Spark UI: http://localhost:4040.

## Data

Generated once from the repository root:

```bash
docker compose exec jupyter spark-submit labs/05_skew_salting/00_make_data.py
```

| Dataset | Contents |
| --- | --- |
| `/opt/data/m5/orders_skew` | 14,000,000 orders in 16 files; one customer holds a large share of them |
| `/opt/data/m4/customers_big` | the Module 4 dimension (2,000,000 customers, ~149 MiB) |

## Experiments

| Notebook | Question |
| --- | --- |
| `01_baseline.ipynb` | `orders_skew ⋈ customers_big` on `customer_id`: which stage shows the skew, in which metrics, and how bad is it? |
| `02_salting.ipynb` | Implement salting for that join yourself; verify the result; compare before/after. |
| `03_alternatives.ipynb` | The same join with AQE's skew handling on, and with a broadcast: when is salting unnecessary? |

Each **PREDICT** prompt is answered in chat before the cell is run. Shut the previous notebook's kernel down before
starting the next one. In the Stages tab, use *Summary Metrics* (min / median / max) and sort the *Tasks* table by duration.
