# Lab 02 — DataFrames + Spark SQL essentials

Runs in JupyterLab (http://localhost:8888), folder `/workspace/labs/02_dataframes_sql`. Spark UI: http://localhost:4040.
Uses the Module 1 datasets in `/opt/data/m1/` (run `labs/01_execution_model/00_make_data.py` first if they are missing).

| Notebook | Question |
| --- | --- |
| `01_sql_vs_df.ipynb` | The same query written as `spark.sql(...)` and as DataFrame API calls: do they produce the same physical plan? What about a differently shaped SQL for the same result? |
| `02_udf_vs_native.ipynb` | A built-in expression vs a Python UDF doing the same thing: what changes in the plan, and in runtime? |

Each **PREDICT** prompt is answered in chat before the cell is run. Shut the previous notebook's kernel down before
starting the next one (one SparkSession holds all cluster cores).
