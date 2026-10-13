"""Generate the Module 1 datasets into /opt/data/m1/.

Run from the repository root:
    docker compose exec jupyter spark-submit labs/01_execution_model/00_make_data.py
"""
from pyspark.sql import SparkSession, functions as F

BASE = "/opt/data/m1"
N_ORDERS = 2_000_000
N_CUSTOMERS = 10_000

spark = SparkSession.builder.appName("m1-make-data").getOrCreate()

orders = (
    spark.range(0, N_ORDERS, numPartitions=8)
    .withColumnRenamed("id", "order_id")
    .withColumn("customer_id", (F.pmod(F.hash("order_id"), F.lit(N_CUSTOMERS))).cast("int"))
    .withColumn("shop_id", (F.pmod(F.hash(F.col("order_id") * 7), F.lit(50))).cast("int"))
    .withColumn("amount", F.round(F.rand(seed=1) * 500 + 1, 2))
    .withColumn("order_date", F.date_add(F.lit("2026-01-01"), (F.pmod(F.hash(F.col("order_id") * 13), F.lit(240))).cast("int")))
)

customers = (
    spark.range(0, N_CUSTOMERS)
    .withColumnRenamed("id", "customer_id")
    .withColumn("customer_id", F.col("customer_id").cast("int"))
    .withColumn("country", F.element_at(F.array(*[F.lit(c) for c in ["DE", "FR", "PL", "ES", "IT", "NL", "SE", "FI"]]), (F.pmod(F.col("customer_id"), F.lit(8)) + 1).cast("int")))
    .withColumn("segment", F.when(F.col("customer_id") % 10 == 0, "enterprise").when(F.col("customer_id") % 3 == 0, "smb").otherwise("consumer"))
)

orders.write.mode("overwrite").parquet(f"{BASE}/orders")
customers.coalesce(1).write.mode("overwrite").parquet(f"{BASE}/customers")
orders.coalesce(4).write.mode("overwrite").option("header", True).csv(f"{BASE}/orders_csv")

for name in ["orders", "customers", "orders_csv"]:
    fmt = "csv" if name.endswith("csv") else "parquet"
    reader = spark.read.option("header", True) if fmt == "csv" else spark.read
    print(f"{name}: {getattr(reader, fmt)(f'{BASE}/{name}').count():,} rows")

spark.stop()
print("DATA READY")
