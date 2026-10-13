"""Generate the Module 5 dataset into /opt/data/m5/.

Run from the repository root:
    docker compose exec jupyter spark-submit labs/05_skew_salting/00_make_data.py
"""
from pyspark.sql import SparkSession, functions as F

BASE = "/opt/data/m5"
N_ORDERS = 14_000_000
N_FILES = 16
HOT_CUSTOMER = 1

spark = SparkSession.builder.appName("m5-make-data").getOrCreate()

orders = (
    spark.range(0, N_ORDERS, numPartitions=N_FILES)
    .withColumnRenamed("id", "order_id")
    .withColumn(
        "customer_id",
        F.when(F.col("order_id") % 7 < 3, F.lit(HOT_CUSTOMER))
        .otherwise(F.pmod(F.hash("order_id"), F.lit(10_000)) + 2)
        .cast("int"),
    )
    .withColumn("shop_id", (F.pmod(F.hash(F.col("order_id") * 7), F.lit(50))).cast("int"))
    .withColumn("amount", F.round(F.rand(seed=5) * 500 + 1, 2))
    .withColumn("order_date", F.date_add(F.lit("2026-01-01"), (F.pmod(F.hash(F.col("order_id") * 13), F.lit(240))).cast("int")))
    .withColumn("note", F.md5(F.col("order_id").cast("string")))
)

orders.write.mode("overwrite").parquet(f"{BASE}/orders_skew")

df = spark.read.parquet(f"{BASE}/orders_skew")
hot = df.filter(F.col("customer_id") == HOT_CUSTOMER).count()
print(f"orders_skew: {df.count():,} rows in {len(df.inputFiles())} files; customer {HOT_CUSTOMER}: {hot:,} rows")
spark.stop()
print("DATA READY")
