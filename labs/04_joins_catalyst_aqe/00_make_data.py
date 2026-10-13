"""Generate the Module 4 dataset into /opt/data/m4/.

Run from the repository root:
    docker compose exec jupyter spark-submit labs/04_joins_catalyst_aqe/00_make_data.py
"""
from pyspark.sql import SparkSession, functions as F

BASE = "/opt/data/m4"
N_CUSTOMERS = 2_000_000

spark = SparkSession.builder.appName("m4-make-data").getOrCreate()

customers_big = (
    spark.range(0, N_CUSTOMERS, numPartitions=8)
    .select(F.col("id").cast("int").alias("customer_id"))
    .withColumn("tier", F.when((F.col("customer_id") < 10_000) & (F.col("customer_id") % 2 == 0), "gold").otherwise("standard"))
    .withColumn("country", F.element_at(F.array(*[F.lit(c) for c in ["DE", "FR", "PL", "ES", "IT", "NL", "SE", "FI"]]), (F.pmod(F.col("customer_id"), F.lit(8)) + 1).cast("int")))
    .withColumn("profile_a", F.md5(F.col("customer_id").cast("string")))
    .withColumn("profile_b", F.sha1(F.col("customer_id").cast("string")))
)

customers_big.write.mode("overwrite").parquet(f"{BASE}/customers_big")

df = spark.read.parquet(f"{BASE}/customers_big")
print(f"customers_big: {df.count():,} rows in {len(df.inputFiles())} files")
spark.stop()
print("DATA READY")
