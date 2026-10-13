# Teacher notes

> **Spoilers.** This file holds the answers: verified facts, experiment design notes, and scenario
> rubrics. It is the teaching agent's reference. As the learner, skip it until after you have made
> your predictions.

Verified on 2026-09-15 against primary sources: Spark 4.2.0 docs and source, Iceberg 1.11.0,
Trino 483, Oozie 5.2.1 docs.

**Version policy.** Labs run **Spark 4.1.x with Iceberg 1.11.x**. Iceberg 1.11.0 has no runtime for
Spark 4.2 yet. Where 4.1 and 4.2 differ, it is marked. Hadoop / Oozie shops often still run Spark 3.x,
so version boundaries that matter in interviews are marked too. Anything version-sensitive is not an
unconditional truth: state the version when teaching it.

---

## Versions

- Latest Spark: 4.2.0 (2026-07-14). Latest 4.1 line: 4.1.3 (2026-07-15). Spark 4.x needs Java 17+ and Scala 2.13; PySpark 4.1+ needs Python 3.10+.
- Iceberg 1.11.0 (2026-05-19) ships Spark runtimes for 3.5, 4.0, 4.1: `org.apache.iceberg:iceberg-spark-runtime-4.1_2.13:1.11.0`.
- AQE is on by default since Spark 3.2.0 (off in 3.0 / 3.1). ANSI SQL mode is on by default since Spark 4.0.0 (bad casts, overflow, divide-by-zero raise errors instead of returning NULL).

Sources: https://spark.apache.org/news/index.html · https://iceberg.apache.org/releases/ · https://spark.apache.org/docs/latest/sql-migration-guide.html

---

## Trino → Spark: where each analogy breaks

Explain a row only after the related module's predictions are done. Trino facts are for Trino 483.

| Trino | Spark | Where it breaks | After |
| --- | --- | --- | --- |
| Submitting a SQL statement | DataFrame code + an action | Spark builds the plan incrementally; transformations on an already-defined DataFrame run nothing until an action, but some calls start jobs early (schema inference, `pivot` without values, eager `checkpoint`, SQL DDL/DML). Spark Classic also analyzes each step immediately, so a bad column fails at once. | M1 |
| Coordinator | Driver | One driver per application; it runs the user's program and sits in the data path for `collect` / `toPandas` (capped by `spark.driver.maxResultSize`, 1g) and broadcast builds. A Trino coordinator is a shared, long-running service running only SQL. The closest Spark analog to a shared coordinator is a Spark Connect server. | M1 |
| Worker | Executor | An executor has fixed task slots (`spark.executor.cores` / `spark.task.cpus`); each slot's thread is held for the whole task. Trino worker threads are a time-sliced pool shared by all queries. | M1 |
| Query | Action | One action can run several jobs: AQE stage jobs, broadcast collect jobs, incremental `take` scans. | M1 |
| Stage (fragment) | Stage | Spark cuts stages at shuffle exchanges only; a broadcast is a separate job, not a stage boundary. Trino also puts stage boundaries at REPLICATE exchanges. | M1, M4 |
| Split / driver | Input partition / task | A Spark task is one partition on one core, closer to a Trino *driver* than a Trino task. A file-scan partition packs file splits up to `spark.sql.files.maxPartitionBytes` (128MB). | M3 |
| `Exchange` | `Exchange` | With Trino's default `retry-policy=NONE`, pages stream between running stages and a node failure fails the query; with `TASK` retries an exchange manager spools data. Spark writes shuffle files to executor local disk, the next stage starts once map outputs exist, and lost shuffle files make Spark resubmit the parent stage to recompute the missing map outputs (all of them if the stage is indeterminate). | M3 |
| Hash partition count (`query.max-hash-partition-count` = 100) | `spark.sql.shuffle.partitions` (200) | AQE coalesces Spark's count at runtime but does not split ordinary partitions (only skewed join partitions and rebalance shuffles). | M3 |
| Replicated join | `BroadcastHashJoin` | Spark collects the build side **to the driver**, builds the hash relation there, and ships it (300s timeout, 8GB cap). Trino never routes it through the coordinator: workers pull it over a REPLICATE exchange. Spark decides from `sizeInBytes` ≤ 10MB with CBO off, and never broadcasts a relation of unknown size. Trino `AUTOMATIC` costs both options when stats exist (capped by `join_max_broadcast_table_size` = 100MB) and falls back to size heuristics or PARTITIONED without stats. Neither engine replicates the row-preserving side of an outer join. | M4 |
| Partitioned join | `SortMergeJoin` / `ShuffledHashJoin` | Trino has no sort-merge join: equi-joins are hash joins, and nested-loop joins are only for joins without equality conditions. Spark defaults to sort-merge for large equi-joins (`spark.sql.join.preferSortMergeJoin` = true). Algorithmically Trino's partitioned join is Spark's shuffled hash join, whose build side must fit in memory, while sort-merge can spill. | M4 |
| `EXPLAIN` / `EXPLAIN ANALYZE` | `explain("formatted")` / SQL tab | Spark has no `EXPLAIN ANALYZE`: `explain` only plans (`AdaptiveSparkPlan isFinalPlan=false`), and runtime per-operator metrics appear in the SQL / DataFrame tab after an action. Trino's plain `EXPLAIN` already shows fragments. | M2, M4 |
| Query optimizer | Catalyst | Trino's cost-based rules are on by default and depend on connector stats. Spark CBO is off by default, and physical planning takes the first plan the strategies return (rules, hints, thresholds). Spark whole-stage codegen fuses operator chains into one generated function; Trino generates bytecode inside operators without fusing pipelines. | M4 |
| Runtime adaptation | AQE | Trino re-plans at runtime only under fault-tolerant execution with `retry-policy=TASK`, and in Trino 483 its adaptive join reordering and runtime adaptive partitioning are off by default. Trino's always-on runtime behaviors (dynamic filtering, adaptive partial aggregation) adjust execution without re-planning. Spark AQE is on by default since 3.2 and re-plans at query-stage boundaries. Trino dynamic filtering corresponds to Spark dynamic partition pruning and runtime bloom filters, not AQE. | M4 |
| Skewed joins | AQE skew join / salting | Trino 483 has no automatic skew-join splitting (its skew rebalancing covers partitioned writes only); the practical options are a replicated join or manual salting. Spark AQE splits skewed sort-merge / shuffled hash join partitions, but not aggregations. | M5 |
| Query memory limits | Spill, retry, OOM | Trino kills a query exceeding `query.max-memory-per-node` / `query.max-memory`; its spill-to-disk is legacy and off by default. Spark has no per-query memory cap: sorts, aggregations, and shuffles spill per task, hash-join build sides can OOM, and failed tasks retry (`spark.task.maxFailures` = 4). | M7 |
| Global `ORDER BY` | `orderBy` | Trino sorts inside tasks and merges at the GATHER exchange. Spark uses a range-partitioning shuffle with sampled bounds, then sorts each partition. | M3 |

Sources: https://trino.io/docs/current/overview/concepts.html · https://trino.io/docs/current/admin/fault-tolerant-execution.html · https://trino.io/docs/current/optimizer/adaptive-plan-optimizations.html · https://github.com/trinodb/trino/blob/483/core/trino-main/src/main/java/io/trino/execution/QueryManagerConfig.java · https://trino.io/docs/current/admin/properties-general.html · https://github.com/trinodb/trino/issues/17422 · https://github.com/trinodb/trino/issues/1261 · https://trino.io/docs/current/admin/spill.html

---

## Module 1 — Execution model + actions / transformations

**Verified facts**

- Actions include `show`, `collect`, `take` / `head` / `first`, `tail`, `count`, `isEmpty`, `toLocalIterator`, `toPandas`, `foreach` / `foreachPartition`, and writes (`write.save` / `saveAsTable` / `insertInto`, `writeTo(...).append()`).
- `groupBy()` returns `GroupedData` and runs nothing. **`df.groupBy(k).count()` is a transformation** (returns a DataFrame); `df.count()` is an action (returns a number).
- Calls that start a job without an obvious action:
  - CSV read without `.schema()`: reads the first line even with `inferSchema=false`; `inferSchema=true` adds a full pass.
  - JSON read without `.schema()`: full inference pass.
  - `pivot(col)` without an explicit value list.
  - `checkpoint()` / `localCheckpoint()`: eager by default.
  - `spark.sql()` with DDL/DML (`CREATE`, `INSERT`, CTAS): runs immediately. A `SELECT` stays lazy.
  - SQL `CACHE TABLE`: eager unless `CACHE LAZY TABLE`.
- `cache()` / `persist()` are lazy; nothing is stored until an action computes the data.
- `orderBy` is lazy, but the action on a globally sorted DataFrame runs an extra sampling job to compute range bounds.
- One action can run several jobs: with AQE each shuffle stage is submitted as its own job, each broadcast runs a collect job, and `show()` / `take()` scan partitions incrementally (1 partition, then up to 4x more per job).
- "Skipped" stages mean existing shuffle output was reused. They are not failures, and they are common with AQE.
- Stages are cut at shuffle exchanges. A stage runs one task per partition it computes; each task uses `spark.task.cpus` = 1 core.
- Spark Classic analyzes each transformation immediately: a bad column name fails at once with `AnalysisException`, even though nothing executes. Spark Connect defers analysis.

**Design notes**

- A good first surprise: `df.groupBy("k").count()` in a cell produces no job.
- A good second surprise: reading a CSV without a schema produces a job before any action.

**Lab 01 observed outcomes** (Spark 4.1.3, lab cluster 4 executors × 2 cores; verified 2026-09-16 … 20)

- `spark.read.parquet(path)` on a bare path runs a **1-task job** (`parquet at NativeMethodAccessorImpl.java:0`) before any action: eager schema inference reads one file's footer through `SchemaMergeUtils.mergeSchemasInParallel` (`ParquetUtils.inferSchema`, `mergeSchema=false` picks one file; parallelism = `min(nFiles, defaultParallelism)`). `.schema(...)` skips it (`DataSource.getOrInferFileFormatSchema`). Directory listing stays on the driver below `spark.sql.sources.parallelPartitionDiscovery.threshold` = 32 paths. Verified against branch-4.1 source by the researcher.
- Exp 1 (`orders` 8 files, `customers` 1 file): 5 chained transformations → 0 jobs. `top.count()` → **4 jobs**: [1 task: read customers for broadcast] → [8 tasks: scan + filter + partial count, shuffle write ≈ 745 KB] → [1 task + 8 skipped: AQE coalesced 200 → 1, final agg, BHJ, partial count] → [1 task + 9 skipped]. `top.show(5)` → 3 new jobs, orders rescanned (nothing reused across actions). `explain()` → 0 jobs.
- Exp 3 (`orders_csv`, 4 files, 66.6 MB): header-only read → 1 job, 1 task, 1 record; `inferSchema=True` → 2 jobs: 1 task (header) + **8 tasks reading all 2,000,004 records** (CSV is splittable: 8 splits from 4 files); explicit schema → 0 jobs; `printSchema()` → 0.
- Exp 2 (filter → groupBy → BHJ → write) with AQE on → **3 jobs** (broadcast build 1 task; map 8 tasks, shuffle write 1.4 MB, 79,989 partial rows; reduce 1 task after `AQEShuffleRead` 200 → 1, output 113 KB in 1 file). With `spark.sql.adaptive.enabled=false` → **2 jobs**: broadcast build; one job with map (8) + reduce (**200 tasks**), output 473 KB in 200 files. Variant `result.groupBy("customer_id").agg(max)` adds **no** Exchange (BHJ preserves the streamed side's hash partitioning).
- Standalone gotcha: an idle notebook session holds all 8 cores (`spark.cores.max` unset); a second app waits with "Initial job has not accepted any resources". Have the learner shut the other kernel down.

Sources: https://github.com/apache/spark/blob/v4.2.0/sql/api/src/main/scala/org/apache/spark/sql/RelationalGroupedDataset.scala · https://github.com/apache/spark/blob/v4.2.0/sql/api/src/main/scala/org/apache/spark/sql/SparkSession.scala · https://github.com/apache/spark/blob/v4.2.0/core/src/main/scala/org/apache/spark/scheduler/DAGScheduler.scala · https://spark.apache.org/docs/latest/spark-connect-gotchas.html

---

## Module 2 — DataFrames + Spark SQL essentials

**Verified facts**

- SQL strings and DataFrame calls go through the same analyzer, optimizer, planner, and AQE. Truly equivalent queries usually produce the same physical plan, but it is not guaranteed: `USING` vs `ON`, aliases, implicit casts, and UDFs vs built-ins can change it. Compare with `explain`.
- `explain` modes: `simple` (default, physical plan only), `extended` (same as `explain(True)`: parsed, analyzed, optimized logical plans plus physical plan), `codegen`, `cost`, `formatted`.
- Python UDFs run in separate Python worker processes. Catalyst cannot see inside them: predicates on UDF results are not pushed down, and the Python evaluation node (`BatchEvalPython` / `ArrowEvalPython`) breaks whole-stage codegen. Pandas UDFs are vectorized with Arrow.
- Arrow-optimized Python UDFs (`spark.sql.execution.pythonUDF.arrow.enabled`): default `false` in 3.4–4.1, `true` since 4.2.0.
- Python UDFs are treated as deterministic by default, and they do not short-circuit inside `CASE WHEN` / `AND` / `OR`.

Sources: https://spark.apache.org/docs/latest/sql-programming-guide.html · https://spark.apache.org/docs/latest/api/python/migration_guide/pyspark_upgrade.html

---

## Module 3 — Partitions and shuffle

**Verified facts**

- **Input partitions** (file sources): `maxSplitBytes = min(spark.sql.files.maxPartitionBytes (128MB), max(spark.sql.files.openCostInBytes (4MB), bytesPerCore))`. Splittable files are cut into `maxSplitBytes` chunks, and chunks are bin-packed into partitions, each file adding its open cost. Non-splittable files stay whole: gzip-compressed CSV / JSON / text, or multiLine CSV / JSON. One large `.csv.gz` is one task, while Parquet using gzip internally is still splittable. For DataFrame file sources this does **not** follow HDFS blocks; block locations are only locality hints. The RDD API (`sc.textFile`) does use Hadoop InputFormat splits, typically one per block.
- **Shuffle partitions**: `spark.sql.shuffle.partitions` = 200 is the starting count for join and aggregation shuffles. With AQE it is only the starting point.
- AQE coalescing: `spark.sql.adaptive.advisoryPartitionSizeInBytes` = 64MB and `coalescePartitions.minPartitionSize` = 1MB. **But** `coalescePartitions.parallelismFirst` = true (default) makes the target `min(64MB, total shuffle size / default parallelism)`, so Spark tends to keep about default-parallelism partitions. Set it to false to honor the 64MB target.
- `repartition(n)`: round-robin shuffle, never coalesced by AQE. `repartition(col)`: hash partitioning into `spark.sql.shuffle.partitions`, and AQE may coalesce it. `repartition(n, col)`: not coalesced. Adjacent repartitions are collapsed by the optimizer. Hash partitioning never splits a hot key.
- `coalesce(n)`: narrow, no shuffle, cannot increase the count. Because there is no stage boundary, `coalesce(1)` makes all upstream work in the same stage run on one task. Use `repartition(n)` to keep upstream parallelism.
- `repartitionByRange(n, cols)`: range partitioning with bounds from sampling (100 samples per partition) at execution time.
- Aggregations are planned as partial aggregate → `Exchange` → final aggregate. The operator is `HashAggregate` for fixed-width buffers (count / sum / avg on numbers), `ObjectHashAggregate` for `collect_list` / `collect_set`, and `SortAggregate` otherwise (e.g. `max` on strings). `DISTINCT` aggregates add steps, and there is no `Exchange` if the child is already hash-partitioned on the grouping keys.

**Design notes**

- Experiment 1 (`groupBy("customer_id").count()`): also ask the learner to predict how many aggregate nodes appear and on which side of the `Exchange`.
- Experiment 3 (shuffle partitions): AQE coalescing hides a too-high value. Run the "clearly bad" setting with `spark.sql.adaptive.coalescePartitions.enabled=false` first, then turn it back on and compare. A too-*low* value cannot be rescued by AQE, which coalesces but does not split non-skewed partitions.

**Lab 03 observed outcomes** (Spark 4.1.3, 4 executors × 2 cores on 2 worker hosts; `orders_big` = 24 M rows, 16 Parquet files, 1.1 GB; verified 2026-09-21 … 28)

- Exp 1: plain `groupBy(customer_id).agg(count, sum)` → partial HashAggregate → Exchange → final; shuffle write **2.84 MiB / 160,000 records** (16 × 10,000); AQE → 2 reduce tasks. `repartition("customer_id")` first → one Exchange before the partial aggregate, **231 MiB / 24 M records**, 9 reduce tasks. Warm timings 0.6 s vs 1.0 s (the first run is always cold — re-run both).
- Exp 2: `filter(amount > 400)` (4.85 M rows kept) → `coalesce(4)`: 1 stage, **4 tasks do the scan + filter**, 3.4 s; `repartition(4)`: 16-task map (257.6 MiB shuffle) + 4-task write, **2.3 s** (faster: upstream parallelism kept). 4 output files each. `coalesce(32)` → 16, `repartition(32)` → 32, and **`repartition(32).rdd.getNumPartitions()` executes the shuffle map stage (1.28 GB) under AQE**.
- Exp 3 **design flaw**: `row_number() … filter(rn == 1)` triggers Spark 3.5+'s `WindowGroupLimit` pushdown (partial group limit before the Exchange) → only ~160 K rows / 1.9 MiB shuffled. The notebook's workload must be the full window without a filter, forced with `write.format("noop")` (fix the notebook before reuse). With the fixed workload (~1.24 GB shuffle): 4 partitions → 4 × 312 MiB tasks, 14.6 s, no spill at lab memory; 2000 → 20 ms tasks, 8.0 s, 31,792 blocks fetched; 2000 + AQE → **21 tasks** (64 MB target), 5.2 s; 4 + AQE unchanged; hand-set 21 → 5.4 s, 336 blocks. Shuffle read is exactly 50 % local / 50 % remote (2 hosts).

Sources: https://github.com/apache/spark/blob/v4.2.0/sql/core/src/main/scala/org/apache/spark/sql/execution/datasources/FilePartition.scala · https://github.com/apache/spark/blob/v4.2.0/sql/core/src/main/scala/org/apache/spark/sql/execution/adaptive/CoalesceShufflePartitions.scala · https://github.com/apache/spark/blob/v4.2.0/sql/api/src/main/scala/org/apache/spark/sql/Dataset.scala

---

## Module 4 — Joins + Catalyst + AQE

**Verified facts**

- Equi-join selection order, no hints:
  1. `BroadcastHashJoin` if an eligible side's estimated size ≤ `spark.sql.autoBroadcastJoinThreshold` (10MB; -1 disables).
  2. `ShuffledHashJoin` only if `spark.sql.join.preferSortMergeJoin` (internal, default true) is false and size conditions hold.
  3. `SortMergeJoin` if keys are orderable.
  4. `CartesianProduct` for inner-like joins.
  5. `BroadcastNestedLoopJoin` as last resort.
- BHJ build side: inner joins either side; LEFT OUTER / LEFT SEMI / LEFT ANTI only the right side; RIGHT OUTER only the left side; FULL OUTER not supported.
- Hints: `BROADCAST` / `BROADCASTJOIN` / `MAPJOIN`, `MERGE` / `SHUFFLE_MERGE` / `MERGEJOIN`, `SHUFFLE_HASH`, `SHUFFLE_REPLICATE_NL`; priority in that order. `BROADCAST` ignores the threshold, but a hint the join type cannot support is ignored with a warning.
- Broadcast mechanics: the build side is **collected to the driver**, built into a hash relation there, then shipped to executors. `spark.sql.broadcastTimeout` = 300s. Max broadcast table 8GB: hard-coded before 4.1.0, configurable as `spark.sql.maxBroadcastTableSize` since 4.1.0. There are row limits too.
- `BroadcastNestedLoopJoin`: used for non-equi joins when a side is broadcastable, and as a last-resort fallback even when neither side is small. It does O(N×M) condition checks, plus broadcast memory.
- Catalyst: analysis → logical optimization → physical planning → preparation (`EnsureRequirements` inserts exchanges, `CollapseCodegenStages` does whole-stage codegen). Physical planning **takes the first plan the strategies return**; it does not cost alternatives. CBO (`spark.sql.cbo.enabled`) is off by default. `ANALYZE TABLE ... COMPUTE STATISTICS [FOR COLUMNS ...]` stores stats.
- Without CBO only `sizeInBytes` is estimated:
  - file size × `spark.sql.sources.fileCompressionFactor` (1.0)
  - a `Filter` is assumed to keep every row
  - sources without stats get `spark.sql.defaultSizeInBytes` (Long.MaxValue), so they are never broadcast

  So a large table filtered to a few rows is not broadcast statically, while a small compressed file can be broadcast and blow up in memory.
- AQE re-optimizes when shuffle / broadcast query stages finish, using runtime statistics. It only wraps plans containing an `Exchange` or a subquery. It can:
  - coalesce post-shuffle partitions (see Module 3 caveat)
  - convert SMJ → BHJ at runtime when a side's runtime size is at or below `spark.sql.adaptive.autoBroadcastJoinThreshold`. That setting has no value of its own: it takes the **current value of `spark.sql.autoBroadcastJoinThreshold`**. Setting the static threshold to -1 therefore also disables the runtime conversion unless the adaptive threshold is set explicitly. The shuffles already happened, but sorts are skipped and the local shuffle reader is used.
  - **but** AQE will not use a side as the broadcast build side if fewer than 20% of its shuffle partitions are non-empty (internal `spark.sql.adaptive.nonEmptyPartitionRatioForBroadcastJoin` = 0.2). For inner / semi joins the build side itself is checked; for outer and anti joins the other side is.
  - convert SMJ → SHJ only if `spark.sql.adaptive.maxShuffledHashJoinLocalMapThreshold` (default 0 = off) is set to at least `advisoryPartitionSizeInBytes` (64MB) and every partition on that side is at or below it
  - split skewed join partitions (Module 5)
- Before execution, `explain()` shows `AdaptiveSparkPlan isFinalPlan=false`. The reliable place to see the final plan is the Spark UI SQL / DataFrame tab. (`explain()` after `collect()` on the same DataFrame also shows it; `show()` / `count()` run a derived plan and do not.)
- Trino dynamic filtering corresponds to Spark **Dynamic Partition Pruning** (on since 3.0) and **runtime bloom filters** (default on since 3.4), not to AQE.

**Design notes**

- Bad-estimate experiment:
  - Take a dimension that is large on disk and filter it to something small (well under 10MB). The static plan picks SMJ because a `Filter` is assumed to keep every row.
  - To see AQE convert it to BHJ, the filtered side must still have enough distinct join keys to fill at least 20% of the shuffle partitions (e.g. hundreds of keys with 200 partitions), or lower `spark.sql.shuffle.partitions` for the run. With only a handful of keys AQE keeps SMJ on purpose. That makes a good second prediction question.
  - Compare with AQE off.
- Forcing SMJ in a baseline with `spark.sql.autoBroadcastJoinThreshold=-1` also disables AQE's runtime conversion. If the conversion should stay possible, set `spark.sql.adaptive.autoBroadcastJoinThreshold=10MB` explicitly, or force SMJ with a `MERGE` hint instead.

Sources: https://github.com/apache/spark/blob/v4.2.0/sql/core/src/main/scala/org/apache/spark/sql/execution/SparkStrategies.scala · https://spark.apache.org/docs/latest/sql-performance-tuning.html · https://github.com/apache/spark/blob/v4.2.0/sql/core/src/main/scala/org/apache/spark/sql/execution/exchange/BroadcastExchangeExec.scala · https://github.com/apache/spark/blob/v4.2.0/sql/catalyst/src/main/scala/org/apache/spark/sql/catalyst/plans/logical/statsEstimation/SizeInBytesOnlyStatsPlanVisitor.scala · https://github.com/apache/spark/blob/v4.2.0/sql/core/src/main/scala/org/apache/spark/sql/execution/QueryExecution.scala

---

## Module 5 — Data skew + salting

**Verified facts**

- AQE skew join (`spark.sql.adaptive.skewJoin.enabled`, default true): a partition is skewed when it is larger than **both** `skewedPartitionFactor` (5.0) × the median partition size and `skewedPartitionThresholdInBytes` (256MB). The skewed partition is split, and the matching partition on the other side is replicated.
  - Applies to `SortMergeJoin` and `ShuffledHashJoin`. In 4.2 it also covers the shuffled side of a BHJ when the local shuffle reader is disabled.
  - Splittable sides: inner either; LEFT OUTER / SEMI / ANTI left only; RIGHT OUTER right only; **FULL OUTER never**.
  - The rewrite is silently skipped if it would add a shuffle (unless `forceOptimizeSkewedJoin=true`).
  - Splits happen at map-output block boundaries, so a hot key that comes from a single mapper's block cannot be split further. Salting can still be needed.
- **No AQE rule splits a skewed aggregation.** Partial aggregation already softens skew for `count` / `sum` / `min` / `max` / `avg`: at most one buffer row per key per map partition is shuffled. `collect_list` / `collect_set` still carry every value, and Python grouped-aggregate UDFs have no partial step.
- `spark.sql.adaptive.optimizeSkewsInRebalancePartitions.enabled` handles skew only in REBALANCE shuffles, including Iceberg writes, not joins / groupBy / `repartition()`.
- Speculative execution (`spark.speculation`, default false) re-runs a slow task on the **same data**. It helps with bad nodes, not skew. This follows from the mechanism; the docs do not say it outright.
- Trino has no automatic skew-join splitting, so salting knowledge transfers directly.

**Design notes**

- **Demonstrate skew with a join** (or a window `partitionBy` on the hot key), not with `groupBy().count()`: partial aggregation hides most of the skew there.
- For a clean baseline, disable AQE skew join and auto-broadcast for the "before" run. Then compare three variants against it: salting, AQE skew join re-enabled, and broadcast.
- **AQE skew join at lab scale:** its thresholds apply to compressed shuffle bytes (Shuffle Read Size in the UI), and a partition must exceed both 256MB and 5× the median. Scaled-down lab data often never crosses 256MB, so the AQE variant silently does nothing. Either size the data so the hot partition clearly exceeds both thresholds, or lower `spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes` (and `advisoryPartitionSizeInBytes`) for that variant, and tell the learner. Confirm it fired in the SQL tab (skew join marker / number of skewed partitions).
- Salted join, correct form:
  - Add a salt in `[0, N)` to the **skewed side**. For production, derive it deterministically, e.g. `pmod(hash(unique_col), N)`: `rand()` is non-deterministic, and a recomputed task could assign different salts, duplicating or dropping rows.
  - Replicate the **other side** once per salt value (explode `0..N-1`).
  - Join on `(key, salt)`. The result equals the unsalted join.
- Salting only the hot keys limits replication.
- Outer joins: salt the row-preserving side and replicate only the other side. Replicating the preserving side gives wrong results: unmatched rows appear N times, and matched keys gain spurious null-extended rows for salt values with no match. FULL OUTER cannot be salted this way. AQE follows the same rule.
- Salted aggregation: two-phase (aggregate by `(key, salt)`, then by `key`), valid for decomposable aggregates only.

**Lab 05 observed outcomes** (Spark 4.1.3, 4 executors × 2 cores; `orders_skew` = 14 M rows / 16 files / 601 MB, customer 1 = 6,000,000 rows spread over all files; dim = `customers_big` 2 M rows / 149 MiB → SortMergeJoin; verified 2026-09-30)

- Baseline (skew join off, coalescing on): join stage 12 tasks; shuffle read min 5.3 / median 59.1 / **max 290.4 MiB (6.04 M rows)**; duration 1.03 s median / 2.36 s max; no spill; 4.4 s. Coalescing off: 200 tasks, median 2.8 MiB / 50 K rows, max unchanged (the hot bucket already exceeded the 64 MB target, so it was never merged): **121× in rows, 54× in duration**; 3.7 s. At lab scale the damage is small (12 tasks on 8 cores = two waves anyway); the signature is not.
- Salting (hot key only, N = 16, `pmod(hash(order_id), 16)`, `explode` on the dim): join stage 16 tasks, max/median 1.05×, max task 1.53 s; fact write +20 MiB (salt column), dim +15 rows; **warm 2.8 s vs 4.4 s plain**. The first (cold) salted run was 5.9 s — always compare warm vs warm in the same session. `explode` makes the dim scan noticeably costlier (10.6 s vs 2.9 s executor time on the cold run).
- Alternatives on the same data (warm): **AQE skew join 2.6 s** (fires with default thresholds: fact-side `AQEShuffleRead` 19 partitions = 11 coalesced + 1 skewed partition in 8 splits, one per map block of ~36 MiB; dim side 19 with the hot partition read 8×; max task 1.39 s); **broadcast 3.3 s** (`BroadcastExchange` data size 527.3 MiB for 149 MiB of Parquet; collect 0.42 + build 0.95 + ship 0.46 s; join tasks 1.1 / 1.3 / 1.3 s). Order: plain 4.4 > broadcast 3.3 > salting 2.8 > AQE 2.6. The first query of each session is cold (5.9 s for AQE's first run) — always re-run warm.
- Lab 04 aside relevant here: `createDataFrame` from a Python list → `Scan ExistingRDD`, unknown size, never auto-broadcast → `CartesianProduct` for a non-equi inner join; `F.broadcast` → `BroadcastNestedLoopJoin` (8 tasks, 2 M reads vs 64 tasks, 16 M reads).

Sources: https://github.com/apache/spark/blob/v4.2.0/sql/core/src/main/scala/org/apache/spark/sql/execution/adaptive/OptimizeSkewedJoin.scala · https://github.com/apache/spark/blob/v4.2.0/sql/core/src/main/scala/org/apache/spark/sql/execution/aggregate/AggUtils.scala · https://github.com/apache/spark/blob/v4.2.0/sql/core/src/main/scala/org/apache/spark/sql/execution/adaptive/ShufflePartitionsUtil.scala · https://spark.apache.org/docs/latest/configuration.html#scheduling · https://github.com/trinodb/trino/issues/1261

---

## Module 6 — Spark UI + troubleshooting

**Verified facts**

- Application UI on port 4040 (then 4041, 4042, ... if busy).
- Stage page **Summary Metrics** columns: Min, 25th percentile, Median, 75th percentile, Max.
  - Always shown: Duration and GC Time.
  - Shown only when the stage has that data: Input, Output, Shuffle Read, Shuffle Write, Spill (memory), Spill (disk).
  - Scheduler Delay, Peak Execution Memory, Shuffle Read Fetch Wait Time and others are behind "Show Additional Metrics".
- **Spill (memory)** is the deserialized in-memory size of data that was spilled; **Spill (disk)** is the serialized bytes written. The memory figure is usually much larger.
- The SQL / DataFrame tab shows the operator graph with per-operator metrics.
- History Server on port 18080. It needs `spark.eventLog.enabled=true` (default false) and a shared `spark.eventLog.dir` read via `spark.history.fs.logDirectory`. Apps that exit without stopping the context show as incomplete.

**Scenario rubrics** (a strong answer covers most of these, in a structured order)

1. **499 tasks at 15–25s, one task at 12 minutes.**
   - First check whether the slow task's shuffle read / input records are far above the median: that points to skew (a hot key).
   - If its data size is normal, suspect a straggler: bad node, GC, disk. Only in that case does speculation help.
   - Also consider one huge non-splittable input file (e.g. a large `.csv.gz` / `.json.gz`; Parquet with gzip compression is still splittable).
   - Fix by cause, not by adding resources.
2. **20-minute job now takes 2 hours.**
   - Scope what changed: data, code, config, cluster.
   - Compare against a good run in the History Server and find the stage whose time grew.
   - Look at that stage's task distribution: skew, or uniformly slower.
   - Diff the plans: a join strategy flip after a table crossed the broadcast threshold, or lost stats.
   - Check input size / records and file counts (data growth, new hot key, small-file explosion).
   - Check spill / GC, task failures and retries, fetch failures, lost executors.
   - Check resources: fewer executors, queue contention.
   - Then hypothesis → change one thing → measure.
3. **Shuffle partitions changed from 200 to 20, much slower.**
   - Each shuffle partition is up to 10× larger (less if AQE was already coalescing the 200), so a bigger working set per task: spill, GC, possible OOM.
   - If the cluster has more than 20 cores, there are now fewer reduce tasks than cores, so parallelism is lost.
   - AQE can coalesce but cannot split non-skewed partitions, so a too-low starting count is not repaired at runtime.
4. **Heavy spill: is more executor memory the answer?**
   - Not necessarily. Is the spill in a few tasks (skew → fix skew) or in all tasks (partitions too large → more shuffle partitions)?
   - Memory per task shrinks as executor cores grow.
   - Check memory-heavy operators (`collect_list`, wide aggregations, sort), cache competing for memory, and join strategy.
   - Add memory only after these.

**Lab 06 hidden causes** (generated 2026-10-01; never state before the learner has committed to a diagnosis)

- `scenario_1.ipynb` — **not skew**: `/opt/data/m6/events/part_b` is ONE gzip-compressed CSV (12 M rows) next to 16 plain 1 M-row CSV files in `part_a`. Gzip CSV is not splittable → the scan stage has ~17 tasks, one of which reads 12 M rows (large *Input* size/records, no shuffle read at all) and runs many times longer. Evidence to expect from the learner: the slow task is in the *scan* stage, its Input Size / Records is ~12× the median, Shuffle Read is empty → rules out a hot key. Fix: get the source delivered as splittable files (uncompressed / bzip2 / several gz files / Parquet); `repartition` after the read only helps downstream stages, not the read itself. Speculation would not help (same file).
- Scenario 2 (`nightly_report.py`, two finished apps in the History Server) — **join strategy flip after the dimension crossed the broadcast threshold**: `customers/dt=2026-09-30` is 100 K rows (~7 MB → `BroadcastHashJoin`), `dt=2026-10-01` is 1 M rows (~74 MB → `SortMergeJoin`, with a 1.24 GB shuffle of `orders_big` and a sort; too big for AQE's runtime conversion). Evidence: SQL tab plans differ (BHJ vs SMJ, extra Exchange + Sort), a new stage with ~1.2 GB shuffle write, dimension input records 10× larger; fact input identical. Fixes: broadcast hint / raise the threshold if the driver can take it, or accept SMJ. A good answer first scopes "what changed" (data, code, config, cluster) and compares against the good run.
- `scenario_3.ipynb` — `spark.sql.shuffle.partitions` 200 → 2 with AQE on: before = AQE coalesces to ~21 tasks of ~60 MiB; after = 2 tasks of ~620 MiB each (only 2 of 8 cores busy, per-task working set past the ~800 MB execution share → expect spill and long tasks). AQE cannot split. Scaled-down version of the roadmap's 200 → 20.

Sources: https://spark.apache.org/docs/latest/web-ui.html · https://spark.apache.org/docs/latest/monitoring.html · https://spark.apache.org/docs/latest/tuning.html

---

## Module 7 — Memory + performance essentials

**Verified facts**

- Executor heap: 300MB reserved. The unified region M = (heap − 300MB) × `spark.memory.fraction` (0.6), shared by execution and storage; the remaining 40% is user memory. Execution and storage borrow each other's free space. Execution can evict cached blocks, but only down to R = `spark.memory.storageFraction` (0.5) × M; storage can never evict execution memory. R is not a reservation.
- Running tasks share an executor's execution pool: with N active tasks, each task can get at least 1/(2N) and at most 1/N before it must spill. More cores per executor means less memory per task.
- `spark.executor.memoryOverhead` = max(executor memory × `memoryOverheadFactor` (0.10; 0.40 for non-JVM jobs on Kubernetes), 384MB). It applies on YARN and Kubernetes.
  - Container size = heap + overhead + off-heap (if enabled) + `spark.executor.pyspark.memory` (if set).
  - Python workers use overhead space when `pyspark.memory` is unset.
- YARN kill message: "Container killed by YARN for exceeding physical memory limits. ... Consider boosting spark.executor.memoryOverhead." The fix is more overhead or less native / Python memory, not only more heap.
- `spark.driver.maxResultSize` (1g) caps results returned to the driver by one action (`collect`, `toPandas`). Raising it moves the risk to driver memory.
- Driver memory is also used for broadcast builds (Module 4).
- **Local mode** runs driver and executor in one JVM. The heap comes from `spark.driver.memory` (default 1g), which must be set before the JVM starts; `spark.executor.memory` does not size anything. **Executor memory behavior must be studied on a real cluster** (e.g. standalone with separate workers).

**Alternatives to "more memory"** (let the learner derive these; don't list them first)

- Change partition count (more, smaller shuffle partitions).
- Fix skew.
- Change join strategy (e.g. stop broadcasting a table that is too large).
- Remove unnecessary cache.
- Reduce data earlier (filter, project).
- Change the algorithm (e.g. avoid `collect_list` on a hot key or a driver-side `collect`).
- Reduce cores per executor, so each task gets more memory.

**Design notes**

- Reproduce spill with a small executor and few shuffle partitions, then fix it by changing partitioning, not memory.
- Show driver OOM separately with a `collect()` on a large result.

Sources: https://spark.apache.org/docs/latest/tuning.html#memory-management-overview · https://github.com/apache/spark/blob/v4.2.0/core/src/main/scala/org/apache/spark/memory/ExecutionMemoryPool.scala · https://spark.apache.org/docs/latest/configuration.html · https://github.com/apache/spark/blob/v4.2.0/resource-managers/yarn/src/main/scala/org/apache/spark/deploy/yarn/YarnAllocator.scala

---

## Module 8 — Spark + Iceberg

**Verified facts**

- `df.writeTo("cat.db.tbl")`:
  - `append()`, `overwrite(cond)`, `overwritePartitions()`, `create()`, `replace()`, `createOrReplace()` execute the write.
  - `partitionedBy`, `tableProperty`, `using`, `option` only configure it.
  - `overwritePartitions()` is dynamic overwrite.
- Configure `spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions`. Iceberg docs list it as required for `MERGE INTO`, `UPDATE`, row-level `DELETE`, `WRITE ORDERED BY`, and branch writes.
- `INSERT OVERWRITE` follows `spark.sql.sources.partitionOverwriteMode`, default **static**. Without a `PARTITION` clause that replaces the **whole table**. Prefer dynamic mode, `overwritePartitions()`, or `MERGE`.
- `write.distribution-mode` unset means range if the table has a sort order, hash if it is partitioned, none otherwise (since Iceberg 1.2.0). Update / delete distribution defaults to hash. Merge distribution: hash for merge-on-read; for copy-on-write, hash if partitioned. Precedence: write option > `spark.sql.iceberg.distribution-mode` > table property.
- Iceberg requests a distribution without strictly requiring it, so Spark inserts a rebalance that AQE sizes. The write advisory partition size is taken from the write option, then `spark.sql.iceberg.advisory-partition-size`, then `write.spark.advisory-partition-size-bytes`. If none is set it is max(128MB × estimated compression ratio, `spark.sql.adaptive.advisoryPartitionSizeInBytes`). The `parallelismFirst` caveat from Module 3 can still leave many small files.
- `write.target-file-size-bytes` = 512MB. A file never spans a task or a table partition, so each task writes at least one file per partition value it receives. With distribution `none`, N tasks × P partition values can give up to N×P small files. Shuffle sizes are compressed, row-serialized bytes (lz4 by default), not Parquet bytes. Columnar encoding plus zstd typically makes Parquet files about 2–3× smaller than the task's shuffle size, which is why Iceberg's default advisory size is 128MB × that estimated ratio (384MB for zstd Parquet with lz4 shuffle).
- Since Iceberg 1.4.0, Spark 3.5+ uses the fanout writer by default for unsorted tables: one open file per partition per task, which uses more memory.
- `write.merge.mode` / `write.update.mode` / `write.delete.mode` default to **copy-on-write**: every data file with at least one affected row is rewritten in full. Merge-on-read writes position delete files (format v2) or deletion vectors (v3). Default format version is 2.
- MERGE is planned as a join of target and source:
  - left outer without `WHEN NOT MATCHED`, full outer with it
  - insert-only MERGE becomes left anti join + append
  - a cardinality check fails with `MERGE_CARDINALITY_VIOLATION` if a target row matches several source rows (deduplicate the source); while the check applies, the target side is never broadcast
  - `WHEN NOT MATCHED BY SOURCE` disables target pruning, so copy-on-write rewrites every file
- `DELETE` is metadata-only when the filter covers whole partitions or file metrics prove every row matches.
- `CALL cat.system.rewrite_data_files(...)`: `strategy` is `binpack` (default) or `sort`; z-order is `strategy => 'sort', sort_order => 'zorder(c1,c2)'`.
- **Statistics Iceberg reports to Spark's optimizer** (researcher, 2026-10-01; Iceberg `main`, `spark/v4.1` `SparkScan.estimateStatistics`, not diffed against the 1.11 tag): `numRows` = snapshot summary `total-records` only for a *partitioned table with no pushed filters*; otherwise the sum of record counts over planned task groups *after partition / file pruning*. `sizeInBytes` = rows × estimated width of the pruned read schema (not file bytes). So a partition filter shrinks the broadcast estimate (unlike a Parquet path scan); non-partition filters only as far as whole files are pruned. Column stats: NDV only, from a Puffin file for the current snapshot (`CALL system.compute_table_stats`), reported only if `spark.sql.iceberg.report-column-stats` (default true) **and** `spark.sql.cbo.enabled` (default false). `ANALYZE TABLE` on Iceberg: unconfirmed (Spark maps it to v1 commands only) — say "use the procedure".
- Diagnose files with metadata tables:
  - `cat.db.tbl.files`: `partition`, `record_count`, `file_size_in_bytes`
  - `.partitions`: `file_count`
  - `.snapshots`: `summary` with added / deleted files

**Design notes**

- Small-files experiment:
  - Partitioned table, `write.distribution-mode=none`, many write tasks each touching many partition values.
  - Count files and average size via `.files`.
  - Fix with hash distribution or by repartitioning on the partition columns.
  - Measure again.
  - Optional: compact with `rewrite_data_files`.

Sources: https://iceberg.apache.org/docs/latest/spark-writes/ · https://iceberg.apache.org/docs/latest/configuration/ · https://iceberg.apache.org/docs/latest/spark-procedures/ · https://iceberg.apache.org/docs/latest/spark-queries/ · https://github.com/apache/iceberg/blob/apache-iceberg-1.11.0/spark/v4.1/spark/src/main/java/org/apache/iceberg/spark/SparkWriteConf.java · https://github.com/apache/spark/blob/branch-4.1/sql/catalyst/src/main/scala/org/apache/spark/sql/catalyst/analysis/RewriteMergeIntoTable.scala

---

## Module 9 — Production basics

**Verified facts**

- `spark-submit` defaults:
  - `--master local[*]`, `--deploy-mode client`
  - `--num-executors` 2 (YARN / Kubernetes only)
  - `--executor-cores` 1 on YARN / Kubernetes, all worker cores on standalone
  - `--executor-memory 1G`, `--driver-memory 1024M`
  - `--total-executor-cores` is standalone only
- The `yarn-client` / `yarn-cluster` master strings were removed in Spark 3.0: use `--master yarn --deploy-mode cluster`. Oozie docs still show `yarn-cluster`.
- Client mode: the driver runs in the `spark-submit` process on the gateway machine and dies with it. YARN cluster mode: the driver runs inside the ApplicationMaster container, and its logs are in that container (`yarn logs -applicationId <id>` needs log aggregation enabled).
- Standalone clusters do **not** support cluster deploy mode for Python applications. YARN and Kubernetes do.
- YARN: ResourceManager = Scheduler + ApplicationsManager; NodeManagers run containers; the per-application ApplicationMaster negotiates containers. In client mode the Spark AM only requests executors; in cluster mode it also hosts the driver.
- Dynamic allocation (`spark.dynamicAllocation.enabled`, default false) needs one of: an external shuffle service, shuffle tracking (`shuffleTracking.enabled`, default true since 3.4), decommissioning with shuffle-block migration, or a reliable shuffle storage plugin. `executorIdleTimeout` = 60s. Executors holding live shuffle data or cached blocks are not released by default.
- "About 5 cores per executor" is a heuristic from a 2015 Cloudera blog post (Spark 1.3 era), not official Spark guidance.
- Oozie:
  - Apache Oozie **retired in February 2025** (moved to the Attic in April 2025); last release 5.2.1 (2021). Legacy Hadoop stacks still run it.
  - `workflow.xml` is a DAG of control nodes (`start`, `end`, `kill`, `decision`, `fork`, `join`) and action nodes, each with `ok` / `error` transitions.
  - Spark action: `master`, `mode`, `name`, `class`, `jar`, `spark-opts`.
  - Coordinators trigger workflows by frequency and / or dataset availability (done flag `_SUCCESS`). Bundles group coordinators.
  - Retries: `retry-max` (capped at 3 by default, and only for whitelisted error codes) and `retry-interval` (minutes, default 10).
  - Workflow apps live on HDFS (`oozie.wf.application.path`).

Sources: https://spark.apache.org/docs/latest/submitting-applications.html · https://spark.apache.org/docs/latest/running-on-yarn.html · https://hadoop.apache.org/docs/current/hadoop-yarn/hadoop-yarn-site/YARN.html · https://spark.apache.org/docs/latest/configuration.html#dynamic-allocation · https://www.cloudera.com/blog/technical/how-to-tune-your-apache-spark-jobs-part-2.html · https://attic.apache.org/projects/oozie.html · https://oozie.apache.org/docs/5.2.1/DG_SparkActionExtension.html · https://oozie.apache.org/docs/5.2.1/WorkflowFunctionalSpec.html

---

## Mini-capstone

**Candidate problems** (inject 2–3; never name them in learner-visible files):

- data skew
- poor join strategy
- unnecessary repartition
- bad shuffle partition count
- Python UDF
- small files

**Design notes**

- Prefer a mix that needs different evidence: one found in the plan (e.g. Python UDF, poor join strategy), one in task distributions (skew), one in the table's metadata (small files).
- Each injected problem must be observable at lab scale (see the Module 4 and Module 5 notes on AQE thresholds).
- Record the chosen problems and the expected evidence below before handing the pipeline over.

**Chosen problems:** —
