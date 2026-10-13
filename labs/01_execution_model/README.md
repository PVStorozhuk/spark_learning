# Lab 01 — Execution model + actions / transformations

Everything runs in JupyterLab (http://localhost:8888); this folder is `/workspace/labs/01_execution_model`
inside the container. The Spark UI of the running notebook is at http://localhost:4040.

## Setup (once)

From the repository root:

```bash
docker compose exec jupyter spark-submit labs/01_execution_model/00_make_data.py
```

This writes into `/opt/data/m1/`:

| Dataset | Format | Contents |
| --- | --- | --- |
| `orders` | Parquet, 8 files | 2,000,000 orders: `order_id`, `customer_id`, `shop_id`, `amount`, `order_date` |
| `customers` | Parquet | 10,000 customers: `customer_id`, `country`, `segment` |
| `orders_csv` | CSV with header, 4 files | the same orders, for Experiment 3 |

## Experiments

Open the notebooks in order. Each cell that matters is preceded by a **PREDICT** prompt: write your
prediction in chat *before* running the cell, then run it and read the Spark UI.

| Notebook | Question |
| --- | --- |
| `01_lazy.ipynb` | Chain transformations: does anything run? What changes when one action is added? |
| `02_pipeline.ipynb` | filter → groupBy → join → write: how many jobs, stages, tasks? Where are the shuffle boundaries? |
| `03_csv_schema.ipynb` | Reading the same CSV with and without a schema: how many jobs before any action? |

Only one SparkSession can hold the cluster's cores at a time: run `spark.stop()` (last cell) or shut the
kernel down before opening the next notebook.
