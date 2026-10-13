"""Scenario 2 — a nightly report job.

Run from the repository root, once per run date:
    docker compose exec jupyter spark-submit labs/06_spark_ui_troubleshooting/scenario_2/nightly_report.py 2026-09-30
"""
import sys
import time

from pyspark.sql import SparkSession, functions as F

run_date = sys.argv[1]

spark = SparkSession.builder.appName(f"nightly_customer_report {run_date}").getOrCreate()

orders = spark.read.parquet("/opt/data/m3/orders_big")
customers = spark.read.parquet(f"/opt/data/m6/customers/dt={run_date}")

enriched = orders.join(customers, "customer_id")

reports = {
    "by_country": ["country"],
    "by_tier": ["tier"],
    "by_country_tier": ["country", "tier"],
    "by_shop_country": ["shop_id", "country"],
    "by_date_tier": ["order_date", "tier"],
    "by_date_country": ["order_date", "country"],
}

out = f"/opt/data/m6/out/dt={run_date}"
t0 = time.perf_counter()
for name, keys in reports.items():
    (
        enriched.groupBy(*keys)
        .agg(F.sum("amount").alias("total_amount"), F.count("*").alias("orders"))
        .write.mode("overwrite")
        .parquet(f"{out}/{name}")
    )
print(f"nightly_customer_report {run_date}: {time.perf_counter() - t0:.1f}s")

spark.stop()
