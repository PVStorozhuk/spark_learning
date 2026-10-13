"""Generate the Module 3 dataset into /opt/data/m3/.

Run from the repository root:
    docker compose exec jupyter spark-submit labs/03_partitions_shuffle/00_make_data.py
"""
from pyspark.sql import SparkSession, functions as F

BASE = "/opt/data/m3"
N_ORDERS = 24_000_000
N_CUSTOMERS = 10_000
N_FILES = 16

spark = SparkSession.builder.appName("m3-make-data").getOrCreate()

orders = (
    spark.range(0, N_ORDERS, numPartitions=N_FILES)
    .withColumnRenamed("id", "order_id")
    .withColumn("customer_id", (F.pmod(F.hash("order_id"), F.lit(N_CUSTOMERS))).cast("int"))
    .withColumn("shop_id", (F.pmod(F.hash(F.col("order_id") * 7), F.lit(50))).cast("int"))
    .withColumn("amount", F.round(F.rand(seed=3) * 500 + 1, 2))
    .withColumn("order_date", F.date_add(F.lit("2026-01-01"), (F.pmod(F.hash(F.col("order_id") * 13), F.lit(240))).cast("int")))
    .withColumn("note", F.md5(F.col("order_id").cast("string")))
)

orders.write.mode("overwrite").parquet(f"{BASE}/orders_big")

df = spark.read.parquet(f"{BASE}/orders_big")
print(f"orders_big: {df.count():,} rows in {len(df.inputFiles())} files")
spark.stop()
print("DATA READY")
