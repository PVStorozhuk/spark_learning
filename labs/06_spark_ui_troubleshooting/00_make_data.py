"""Generate the Module 6 datasets into /opt/data/m6/.

Run from the repository root:
    docker compose exec jupyter spark-submit labs/06_spark_ui_troubleshooting/00_make_data.py
"""
from pyspark.sql import SparkSession, functions as F

BASE = "/opt/data/m6"

spark = SparkSession.builder.appName("m6-make-data").getOrCreate()

EVENT_TYPES = ["view", "click", "cart", "purchase", "refund", "search"]


def events(start, end, partitions):
    return (
        spark.range(start, end, numPartitions=partitions)
        .withColumnRenamed("id", "event_id")
        .withColumn("user_id", F.pmod(F.hash("event_id"), F.lit(100_000)).cast("int"))
        .withColumn("event_type", F.element_at(F.array(*[F.lit(t) for t in EVENT_TYPES]), (F.pmod(F.col("event_id"), F.lit(6)) + 1).cast("int")))
        .withColumn("amount", F.round(F.rand(seed=6) * 100, 2))
        .withColumn("payload", F.md5(F.col("event_id").cast("string")))
    )


events(0, 16_000_000, 16).write.mode("overwrite").csv(f"{BASE}/events/part_a")
events(16_000_000, 28_000_000, 1).write.mode("overwrite").option("compression", "gzip").csv(f"{BASE}/events/part_b")

customers = spark.read.parquet("/opt/data/m4/customers_big")
customers.filter(F.col("customer_id") < 100_000).coalesce(1).write.mode("overwrite").parquet(f"{BASE}/customers/dt=2026-09-30")
customers.filter(F.col("customer_id") < 1_000_000).coalesce(4).write.mode("overwrite").parquet(f"{BASE}/customers/dt=2026-10-01")

spark.stop()
print("DATA READY")
