# Lab 03 — Partitions and shuffle

Runs in JupyterLab (http://localhost:8888), folder `/workspace/labs/03_partitions_shuffle`. Spark UI: http://localhost:4040.

## Setup (once)

From the repository root:

```bash
docker compose exec jupyter spark-submit labs/03_partitions_shuffle/00_make_data.py
```

Writes `/opt/data/m3/orders_big`: 24,000,000 orders in 16 Parquet files (`order_id`, `customer_id`, `shop_id`,
`amount`, `order_date`, `note`).

## Experiments

| Notebook | Question |
| --- | --- |
| `01_groupby_shuffle.ipynb` | `groupBy("customer_id")`: where is the `Exchange`, how many aggregate nodes, what do shuffle write / read look like per task? What changes if the data is `repartition`ed by the key first? |
| `02_repartition_coalesce.ipynb` | `repartition(n)` vs `coalesce(n)` on the same pipeline: which one shuffles, and what happens to the stage upstream? |
| `03_shuffle_partitions.ipynb` | `spark.sql.shuffle.partitions` set to a bad value on purpose, with AQE coalescing off and on, then a chosen value: task counts, per-task shuffle read, spill, duration. |

Each **PREDICT** prompt is answered in chat before the cell is run. Shut the previous notebook's kernel down before
starting the next one. In the Stages tab, use *Summary Metrics* (min / median / max per task) and the *Tasks* table.
