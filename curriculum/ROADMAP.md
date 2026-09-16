# Roadmap: intensive Spark interview prep

## Mode

| | |
| --- | --- |
| Duration | 1–1.5 weeks |
| Budget | **26h planned**: 24h of modules + 2h mini-capstone. Against a 25h ceiling, see [Budget](#budget) |
| Goal | Spark Data Engineer interviews; production Spark ETL and job optimization |
| Target stack | Hadoop / HDFS, Spark, Iceberg, Hive, batch ETL, Oozie, Jenkins / Bitbucket |
| Emphasis | Execution reasoning and troubleshooting, not PySpark syntax |
| Not taught | Basic Python, SQL, joins, window-function semantics, intro ETL, Iceberg theory already known |
| Labs run on | Spark 4.1.x + Iceberg 1.11.x on a multi-executor cluster; Spark 3.x differences called out |

Labs are generated one module at a time, when that module starts. They contain setup and prompts, never expected results.
Answers and verified facts for the teaching agent live in `TEACHER_NOTES.md` (spoilers: read it after predicting, not before).

## Objectives → modules

| By the end I can… | Module |
| --- | --- |
| Explain how Spark executes a job; transformations vs actions; lazy evaluation | 1 |
| Distinguish narrow and wide transformations; explain jobs, stages, tasks, partitions | 1, 3 |
| Predict when shuffle occurs | 3 |
| Understand physical plans; explain Catalyst | 2, 4 |
| Understand common join strategies; explain AQE | 4 |
| Diagnose data skew; explain and implement salting | 5 |
| Use the Spark UI to investigate slow jobs; diagnose common performance problems | 6 |
| Reason about executor memory, spill, and OOM | 7 |
| Understand Spark + Iceberg interaction | 8 |
| Write production-style Spark ETL | 8, 9, capstone |
| Answer common recruiter / interview questions quickly and clearly | all, drilled in 9 |

## How experiments run

Performance and execution topics are learned by experiment, not lecture:

```text
PREDICT → EXECUTE → OBSERVE → EXPLAIN / Spark UI → FORM HYPOTHESIS → CHANGE ONE THING → MEASURE AGAIN → EXPLAIN RESULT
```

Before each run I predict some of:
- whether execution happens at all
- whether a shuffle happens, and where `Exchange` appears
- the number and structure of stages
- how partition counts change
- the join strategy, and whether broadcast should happen
- where skew may occur
- the Spark UI symptoms I expect

The answer is not revealed before I predict, unless I ask. I run the lab and read the Spark UI myself.
Each prediction and its outcome goes into the prediction log in `PROGRESS.md`.

## Trino → Spark anchors

Spark ideas are anchored in Trino concepts I already know. **None of these analogies is exact.** Where each one
breaks is discussed in the session, after the related module's predictions.

| Trino | Spark | Explored in |
| --- | --- | --- |
| Submitting a SQL statement | DataFrame code + an action | 1 |
| Coordinator / worker | Driver / executor | 1 |
| Query / stage / task / split | Action / job / stage / task / partition | 1, 3 |
| `Exchange` | `Exchange` | 3 |
| Hash partition count | `spark.sql.shuffle.partitions` | 3 |
| `EXPLAIN` / `EXPLAIN ANALYZE` | `explain("formatted")` / Spark UI SQL tab | 2, 4 |
| Replicated join | `BroadcastHashJoin` | 4 |
| Partitioned join | Shuffle-based joins (`SortMergeJoin`, `ShuffledHashJoin`) | 4 |
| Query optimizer | Catalyst | 4 |
| Runtime adaptation / dynamic filtering | AQE / dynamic partition pruning | 4 |
| Skewed joins | Skew handling and salting | 5 |
| Query memory limits | Executor memory, spill, OOM | 7 |

---

## Modules

### Module 1 — Execution model + actions / transformations

**2.5h · critical (interview-critical)**

**Topics:** SparkSession, driver, executor, application, transformation, action, lazy evaluation, DAG, job,
stage, task, partition, narrow transformation, wide transformation, shuffle boundary.

```text
transformations → build logical work → action → Spark executes → job → stages → tasks
```

- Calls to classify as transformation or action: `df.collect()`, `df.count()`, `df.filter(...)`, `df.groupBy(...)`, `df.join(...)`, `df.repartition(...)`, `df.select(...)`, `df.show()`, `df.take()`, `df.withColumn(...)`, and writing / output calls (`df.write...`, `df.writeTo(...).append()`).
- Why wide transformations often introduce a shuffle, and why that can create a stage boundary.
- Which calls start work, and when.

**Experiments**
1. Chain transformations. Predict whether anything runs. Watch the Jobs tab, then add one action.
2. For a pipeline with filter → groupBy → join → write, predict jobs, stages, tasks, and shuffle boundaries. Compare with the Spark UI DAG.
3. Read the same CSV with and without a schema. Predict the number of jobs before any action.

**Done when:** given a small PySpark pipeline, I can identify transformations, actions, lazy portions, likely
shuffle boundaries, stage boundaries, and approximate task behavior.

**Recruiter questions**
- What is a transformation? What is an action?
- Why is Spark lazy?
- Does `groupBy()` immediately execute? Is `df.groupBy("k").count()` an action?
- What starts a Spark job?
- Narrow vs wide transformation?
- Why can a wide transformation create another stage?
- Can one action produce more than one job?

### Module 2 — DataFrames + Spark SQL essentials

**2h · medium, move quickly**

**Topics:** `select`, `filter`, `withColumn`, `groupBy` / `agg`, `join`, `Window` / `row_number` (PySpark API
only; semantics already known), `when`, `col`, `lit`, built-in functions, `spark.sql()`, `df.explain("formatted")`.
No long syntax exercises.

**Central question:** does equivalent Spark SQL and DataFrame API code typically end up using the same Spark
execution engine and similar physical plans?

Also, briefly: why native Spark expressions are generally preferable to unnecessary Python UDFs.

**Experiments**
1. Write one query as `spark.sql("SELECT ...")` and as `df.select(...)...`. Predict, then compare `explain("formatted")` plans.
2. *Optional, only if ahead of time:* a native expression vs a Python UDF doing the same thing. Predict, then compare plans and runtime.

**Done when:** I can read `explain("formatted")`, answer the central question with evidence, and explain why
native expressions beat unnecessary Python UDFs.

**Recruiter questions**
- Is Spark SQL faster or slower than the DataFrame API?
- Why avoid Python UDFs? What would you use instead?
- What do the `explain` modes show?

### Module 3 — Partitions and shuffle

**3h · high**

These are four different things and are never synonyms:

| Kind | Question it answers |
| --- | --- |
| Input partitions | How is the data read split into scan tasks? |
| Spark execution partitions | How many tasks run in a given stage? |
| Shuffle partitions | How many partitions does data land in after an `Exchange`? |
| Iceberg table partitions | How is the table's data physically organized in files? |

**Topics:** Spark partitions, parallelism, shuffle, `Exchange`, shuffle read, shuffle write, `repartition()`,
`coalesce()`, `spark.sql.shuffle.partitions`. `repartitionByRange()` if time allows.

**Experiments**
1. `df.groupBy("customer_id").count()`: predict whether a shuffle happens, why rows must be redistributed, and where `Exchange` appears.
2. `repartition()` vs `coalesce()`: predict when each one might trigger a shuffle and what happens to upstream parallelism.
3. `spark.sql.shuffle.partitions`: start from a clearly inappropriate value, change it to a more appropriate one, and observe task behavior.

**Done when:** given a physical plan, I can point out every shuffle and explain why it exists.

**Recruiter questions**
- What causes a shuffle? What are shuffle read and shuffle write?
- `repartition()` vs `coalesce()`?
- What does `spark.sql.shuffle.partitions` control, and does AQE change it?
- Is a Spark partition the same as a Hive / Iceberg partition?
- How many tasks will reading 10GB of Parquet create?

### Module 4 — Joins + Catalyst + AQE

**4h · critical**

**Topics:** logical plan, optimized logical plan, physical plan, Catalyst, statistics, join planning, AQE.

| Join strategy | Depth |
| --- | --- |
| `BroadcastHashJoin` | Know well |
| `SortMergeJoin` | Know well |
| `ShuffledHashJoin` | Know when Spark picks it over `SortMergeJoin`, and its risks |
| `BroadcastNestedLoopJoin` | No deep study: recognize it and understand why it can be dangerous |

- Broadcasting: `broadcast(dim)` and broadcast hints.
- Why Spark broadcasts a table, and why broadcasting can avoid a large shuffle.
- Why Spark might choose `SortMergeJoin`.
- Why a bad estimate can result in an inefficient plan.
- AQE: runtime statistics, post-shuffle partition coalescing, skew handling, runtime changes to some join strategies; initial plan vs final plan.

**Experiments**
1. Large fact + small dimension. Predict the strategy, run it, then force alternative strategies. Compare stages, shuffle write, and runtime.
2. A bad size estimate: predict the static plan and what AQE will do at runtime; run with AQE on vs off.
3. A join without an equality condition: predict the join strategy.
4. Compare an AQE initial plan with its final plan in the SQL tab.

**Done when:** given a Spark join plan and table-size information, I can explain why Spark selected the strategy
and propose alternatives.

**Recruiter questions**
- `BroadcastHashJoin` vs `SortMergeJoin`?
- When does Spark use `ShuffledHashJoin` instead of `SortMergeJoin`?
- When should you not broadcast? Is a broadcast hint guaranteed?
- What is Catalyst? What happens between a DataFrame and executed code?
- What is AQE, and what can it change at runtime?
- Why would Spark pick a bad join strategy?
- What is `BroadcastNestedLoopJoin` and why can it be dangerous?

### Module 5 — Data skew + salting

**3h · critical (interview-critical, not optional)**

Start from a deliberately skewed dataset (scaled to the lab machine, keeping the imbalance):

```text
customer_id     row count
1               50,000,000
2                  100,000
3                   90,000
4                  110,000
...
```

Partitioning by this key can produce something like:

```text
Task 1      10 sec
Task 2       9 sec
...
Task 199    10 sec
Task 200     6 minutes
```

**Topics**
- What data skew is, and how to identify it in the Spark UI.
- Possible solutions, and when each fits: broadcast the other side, AQE skew handling, filter earlier, pre-aggregate, choose a better key, salting.
- **Salting in detail:**
  - Turn a hot key like `customer_id = 123` into artificial subkeys `(123,0)`, `(123,1)`, …, `(123,9)`.
  - Distribute the large side's rows between the salts.
  - Handle the other side, which may need replicating across salt values.
- Drawbacks: extra complexity, replicated rows, potentially increased data volume, manual tuning, and it is unnecessary if AQE, broadcast, or pre-aggregation solves the problem.

**Interview conclusion:** salting is one tool for skew, not the automatic first solution.

**Experiments**
1. Skewed baseline: predict which stage, operator, and task metrics will show the skew; run and confirm in the UI.
2. Implement salting in PySpark. Compare before and after: task durations, partition sizes, runtime, shuffle behavior.
3. Compare salting with the other solutions on the same data.

**Done when:** I can explain why skew occurs, recognize it from task metrics, implement salting, measure
before/after, and explain when salting is not appropriate.

**Recruiter questions**
- What is data skew? How does it appear in the Spark UI?
- What is salting, and why does it work?
- Which side of a join do you salt? What happens to the other side?
- What are the disadvantages? When would you avoid salting?
- Does speculative execution help with skew?

### Module 6 — Spark UI + troubleshooting

**3.5h · critical (never removed, even if time is tight)**

**Inspect:** Jobs, Stages, Tasks, Executors, SQL, History Server.

**Metrics:** task duration; input records / bytes; output records / bytes; shuffle read; shuffle write;
memory spill; disk spill; GC time; partition / task size.

**Scenarios** (intentionally broken jobs, diagnosed before any answer is given)
1. 499 tasks take 15–25 seconds; 1 task takes 12 minutes. Likely causes?
2. A job normally runs in 20 minutes and suddenly takes 2 hours. Structured investigation?
3. Shuffle partition count was changed from 200 to 20 and performance became much worse. Why?
4. Executors show heavy spilling. Is increasing executor memory necessarily the correct solution?

**Done when:** I have written my own repeatable troubleshooting workflow, applied it to all four scenarios, and
diagnosed at least three of them on actual broken lab jobs.

**Recruiter questions**
- What do you inspect in the Spark UI, and in what order?
- One task is 20x slower than the others: what do you suspect?
- A Spark job became five times slower overnight: how do you investigate?
- What does spill mean? Memory spill vs disk spill?

### Module 7 — Memory + performance essentials

**2h · medium, compressed**

**Topics:** executor memory, driver memory, memory overhead, executor cores, partition sizing, garbage
collection, memory spill, disk spill, executor OOM, driver OOM. Focus on relationships, not config lists:

```text
very large partition → large task working set → memory pressure → GC / spill / OOM
```

OOM does **not** automatically mean "increase executor memory". The alternatives are derived during the module.

**Experiments**
1. Reproduce spill, then reduce it without adding memory. Measure both runs.
2. *Budget cut 2:* trigger a driver-side failure and explain how it differs from an executor-side one.

**Done when:** I can explain the memory chain above, distinguish driver OOM from executor OOM by cause, and
argue for fixes other than more memory.

**Recruiter questions**
- Driver OOM vs executor OOM: typical causes?
- What is memory overhead used for?
- How do executor cores affect memory per task?
- Spill vs OOM?

### Module 8 — Spark + Iceberg

**2.5h · medium (Spark-side integration only)**

**Topics:** `df.writeTo("catalog.schema.table").append()` and DataFrameWriterV2; `INSERT`, `MERGE`, `DELETE`,
`UPDATE`; write distribution; file sizing; metadata tables for diagnosis.
Snapshots and manifests only where they directly affect Spark behavior.

**Questions to answer**
- How do Spark execution partitions affect writes? How many files will Spark produce?
- Why do tiny files appear?
- Does Spark repartitioning equal Iceberg table partitioning?
- How can write distribution affect file sizes?
- What gets rewritten during `MERGE`? Why can `MERGE` be expensive?

**Experiments**
1. Intentionally produce too many small files; measure them through metadata tables; improve the write behavior; measure again.
2. *Budget cut 3 (becomes explanation only):* run a `MERGE`, predict which files are rewritten, then check the snapshot summary.

**Done when:** I can explain and demonstrate how Spark execution determines Iceberg file layout, and explain
what `MERGE` rewrites and costs.

### Module 9 — Production basics + recruiter review

**1.5h · medium (about 1h production, 0.5h drills)**

**Topics**
- `spark-submit`: driver, executors, executor cores, executor memory, dynamic allocation, client mode, cluster mode.
- YARN basics: ResourceManager, NodeManager, ApplicationMaster, containers.
- Oozie, briefly (*Budget cut 1:* about 10 minutes): workflow, actions, Spark action, dependencies, basic scheduling / orchestration, retry and failure concepts.

**Rapid drill** (timed, cold, no notes; logged in `PROGRESS.md`)
- What is an action? What is a transformation?
- Narrow vs wide transformation? Why is Spark lazy?
- What causes shuffle? What creates another stage?
- What is Catalyst? What is AQE?
- `BroadcastHashJoin` vs `SortMergeJoin`?
- What is data skew? What is salting? When would you use salting?
- `repartition()` vs `coalesce()`?
- What does spill mean? What do you inspect in the Spark UI?
- One task is 20x slower than the others: what do you suspect?
- A Spark job became five times slower overnight: how do you investigate?
- Plus, as time allows, recruiter questions from Modules 1–8.

### Mini-capstone

**2h · high**

Synthetic retail data: `orders`, `order_items`, `products`, `shops`, `customers`.

```text
orders → join order_items → join products → join shops → aggregate daily metrics → write Iceberg table
```

The pipeline ships with 2–3 hidden performance problems drawn from topics in Modules 2–8.

Diagnose with `explain("formatted")`, the Spark UI, runtime measurements, shuffle metrics, and task
distributions. Optimize one variable at a time and document each problem:

```text
Problem → Evidence → Hypothesis → Change → Before metrics → After metrics → Explanation
```

---

## Schedule

A guide, not a hard plan; the teaching agent adapts to progress.

| Day | Focus | Hours |
| --- | --- | --- |
| 1 | M1: actions / transformations, lazy evaluation, jobs / stages / tasks | 2.5 |
| 2 | M2: DataFrames + SQL; M3 part 1: partition kinds, first shuffle experiment | 3.0 |
| 3 | M3 part 2: `repartition` / `coalesce`, shuffle partitions; M4 part 1: join strategies | 3.5 |
| 4 | M4 part 2: joins, Catalyst, AQE | 2.5 |
| 5 | M5: data skew, salting | 3.0 |
| 6 | M6: Spark UI, broken-job troubleshooting | 3.5 |
| 7 | M7: memory, performance troubleshooting | 2.0 |
| 8 | M8: Spark + Iceberg | 2.5 |
| 9 | M9: production Spark, YARN, Oozie; mini-capstone | 3.0 |
| 10 | M9: recruiter drills; weak areas; review | 0.5 + slack |
| | **Total** | **26.0** |

## Budget

The module targets add up to 24h, plus 2h for the mini-capstone: 26h, which is 1h over a 25h ceiling.
If the ceiling is firm, cut from the topics the critical path allows to shrink (Spark + Iceberg, detailed
memory, YARN / Oozie), in this order:

| Cut | Saves |
| --- | --- |
| M9: Oozie to about 10 minutes | 0.5h |
| M7: drop experiment 2 (driver-side failure); keep the memory chain and the spill experiment | 0.5h |
| M8: experiment 2 (`MERGE`) becomes explanation only; keep the small-files experiment | 0.5h |
| **Resulting total** | **24.5h** |

## Critical interview path

If time becomes even shorter, protect these first, in this order:

```text
Actions / transformations → Lazy evaluation → Jobs / stages / tasks → Partitions → Shuffle → Joins
→ Catalyst / AQE → Data skew → Salting → Spark UI → Performance troubleshooting
```

Spark + Iceberg, detailed memory topics, YARN, and Oozie may be reduced if absolutely necessary.

## After the interview / deeper study

Postponed, not deleted. Pick up here if the core curriculum finishes early.

- RDD API
- Deeper Spark internals (scheduler, memory manager, shuffle implementation)
- Scan-level optimizations: column pruning, predicate pushdown, file-scan planning, whole-stage codegen
- Serialization tuning (Kryo)
- Deep JVM GC tuning
- Detailed cluster sizing formulas
- Advanced YARN administration (queues, capacity scheduler)
- Advanced scheduler internals (fair scheduler pools, speculation tuning)
- Obscure join hints; the cost-based optimizer and table statistics in depth
- Dynamic partition pruning and runtime bloom filters in depth
- Hot-key isolation (processing hot keys on a separate path)
- Storage-partitioned joins with Iceberg
- Deeper Iceberg internals: copy-on-write vs merge-on-read trade-offs, format v3, deletion vectors, row lineage, branching, maintenance procedures
- Advanced caching and storage levels
- Pandas UDFs and Arrow UDFs in depth
- Production ETL engineering: packaging (`--py-files`, archives, virtualenvs), configuration strategy, testing Spark jobs, backfills, idempotent incremental Iceberg pipelines
- Orchestration beyond Oozie basics: Airflow with Spark, Jenkins / Bitbucket CI/CD for Spark jobs
- Event logs and History Server operations
- Spark Connect; Kubernetes deployment; Kerberos and security
- Advanced streaming topics (Structured Streaming)
- Full production-sized capstone

## Open decisions

- How lab datasets are generated (into the `lab-data` volume), including skewed distributions.
