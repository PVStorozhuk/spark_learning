"""Smoke test for the lab environment.

Run from the repository root:
    docker compose exec jupyter spark-submit env/smoke_test.py
"""
import time

import pandas
import pyarrow
from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("smoke-test").getOrCreate()
sc = spark.sparkContext

print(f"Spark {spark.version} | pandas {pandas.__version__} | pyarrow {pyarrow.__version__}")
print(f"master: {sc.master}")

# Executors register asynchronously; wait briefly for all of them.
for _ in range(30):
    executors = sc._jsc.sc().getExecutorMemoryStatus().size() - 1  # minus the driver
    if executors >= 4:
        break
    time.sleep(1)
print(f"executors: {executors}")

df = spark.range(0, 2_000_000).withColumn("k", F.col("id") % 100)
print(f"groups: {df.groupBy('k').count().count()}")

spark.sql("CREATE NAMESPACE IF NOT EXISTS lab.smoke")
spark.sql("DROP TABLE IF EXISTS lab.smoke.events PURGE")
spark.sql("CREATE TABLE lab.smoke.events (id BIGINT, k BIGINT) USING iceberg PARTITIONED BY (bucket(4, k))")
df.writeTo("lab.smoke.events").append()

spark.createDataFrame([(1, 999)], "id BIGINT, k BIGINT").createOrReplaceTempView("updates")
spark.sql("""
    MERGE INTO lab.smoke.events t
    USING updates s ON t.id = s.id
    WHEN MATCHED THEN UPDATE SET t.k = s.k
""")

print(f"rows: {spark.table('lab.smoke.events').count()}")
print(f"data files: {spark.table('lab.smoke.events.files').count()}")
print("snapshots:", [r.operation for r in spark.table("lab.smoke.events.snapshots").orderBy("committed_at").collect()])

spark.sql("DROP TABLE lab.smoke.events PURGE")
spark.sql("DROP NAMESPACE lab.smoke")
spark.stop()
print("SMOKE TEST PASSED")
