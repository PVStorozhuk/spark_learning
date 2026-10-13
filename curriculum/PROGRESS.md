# Progress

Progress is **evidence-based**. Reading about a topic, or being told the answer, is not evidence.
A level is recorded only when its evidence is written down: in the competency's Evidence cell
(date + what happened), in a prediction log row, or in a drill log row.

I run the labs and read the Spark UI myself. The agent may cross-check numbers through `explain` output
or the Spark REST API, but `D` is recorded only for observations I made.

## Levels

| Level | Meaning | Evidence required |
| --- | --- | --- |
| `-` | Not yet | |
| `E` | Explained | Explained it in my own words and passed the graded check question. Evidence cell: date, what I explained, result |
| `D` | Demonstrated | Predicted first, ran it, observed the result in the plan or Spark UI; where a variable was changed, measured before and after. Evidence: prediction log rows (for rows with nothing to predict: an Evidence cell with the date and what I ran or located) |
| `I` | Interview-ready | Answered cold (not in the session where the topic was taught): correct, concise, no notes. Evidence: drill log row with Cold = yes |

- A `D` or `I` row needs `E` evidence first; `I` does not require `D`. Hands-on work has its own `D` rows, so talking alone never completes a module.
- `Target` is the level a competency needs. A module is `done` only when every non-optional row has reached its target.
- End-of-module recruiter answers are logged with Cold = no; they never award `I`.

## Modules

| # | Module | Priority | Budget (h) | Spent (h) | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Execution model + actions / transformations | critical | 2.5 | 6.2 | done (all `I` awarded 2026-09-30) |
| 2 | DataFrames + Spark SQL essentials | medium | 2.0 | 2.0 | done |
| 3 | Partitions and shuffle | high | 3.0 | 5.7 | taught; `I` pending cold drills |
| 4 | Joins + Catalyst + AQE | critical | 4.0 | 4.3 | taught; `I` pending cold drills |
| 5 | Data skew + salting | critical | 3.0 | 3.3 | taught; `I` pending cold drills |
| 6 | Spark UI + troubleshooting | critical | 3.5 | 3.2 | in progress |
| 7 | Memory + performance essentials | medium | 2.0 | | todo |
| 8 | Spark + Iceberg | medium | 2.5 | | todo |
| 9 | Production basics + recruiter review | medium | 1.5 | | todo |
| C | Mini-capstone | high | 2.0 | | todo |
| | **Total** | | **26.0** | | |

`Spent (h)` is the sum of that module's rows in the session log.

## Current module plan

The approved plan for the module in progress (overwritten when a new module starts). Node labels are phrased
as open questions, not answers.

- Module: 6 — Spark UI + troubleshooting
- Approved on: 2026-10-01 11:20
- Nodes (✓ done, → next):
  - ✓ A · The UI as a map: which tab answers which question (Jobs · Stages/Tasks · SQL · Executors · Environment · History Server); root: all time is in tasks, tasks → stages → plan operators — 11:55: first check ✗ (gaps between jobs attributed to executor GC), re-check ✓ (driver-side Python loop); driver anatomy, which hash tables spill, stage roles (Input / Shuffle Read / Shuffle Write / Output), GC time, caching explained on request
  - ✓ B · The learner's first-draft troubleshooting workflow — 12:25: v1 saved verbatim in `notes/troubleshooting_workflow.md` (SQL tab first → Stages metrics → fix; else gaps between stages / Executors)
  - ✓ S1 · 499 tasks take 15–25 s, one takes 12 min — likely causes? Then a broken lab job (`scenario_1.ipynb`) — 12:50: free-form named skew only; lab job diagnosed with guidance (scan stage, Input 345 MiB vs 114 MiB → one `.csv.gz`); workflow amended; check ✓ (normal data size → straggler, speculation helps)
  - ✓ S2 · A 20-minute job now takes 2 hours — how do you investigate? Then two runs of one job in the History Server — 13:30: lab diagnosed unaided (dimension 10× → BHJ flipped to SMJ); free-form skeleton sound but thin; workflow amended; check (config change → Environment tab) dismissed, still open
  - ✓ S3 · Shuffle partitions 200 → 20 made it much slower — why? Then a lab job (`scenario_3.ipynb`) — 14:15: named lost parallelism and that AQE can't help; missed the 11× working set and the 2 GB spill (taught from the measurements)
  - ✓ S4 · Executors spill heavily — is more executor memory the answer? — 14:30: free-form: "helps, not necessarily best; check where the spill happens; repartition" (missed uniform-vs-concentrated); check ✓ (all tasks → more partitions; one task → skew). Remaining memory levers left for Module 7 to derive
  - → W · The learner's final workflow, applied to all four
  - F · Recruiter drill
- Edges: Root→A→B; B→S1,S2,S3; S3→S4; S1,S2,S4→W→F

Previous module plan (Module 5, completed 2026-10-01):

- Module: 5 — Data skew + salting
- Approved on: 2026-09-30 21:00
- Nodes (✓ done, → next):
  - ✓ A · Skew = uneven buckets; the stage lasts as long as its biggest task; which operators suffer and which don't (root: M3 hash routing + M1-E) — 21:20: check ✓ (exact set: window yes; sum and broadcast join no)
  - ✓ E1 · Exp 1: a skewed join — which stage, which task metrics, how bad? — 2026-09-30: baseline + no-coalescing run logged (290 MiB / 6.04 M rows vs 2.8 MiB / 50 K median; 2 s vs 37 ms); check ✓ (400 cores: stage still waits for the hot task)
  - ✓ B · The fix menu derived from the mechanism — 22:15: map blocks, finer keys and the single-key folk rule discussed; check ✓ (20 MB dim → broadcast first)
  - ✓ E2 · Exp 2: implement salting; before/after — 2026-09-30 22:45: learner's implementation correct; balance 121× → 1.05×; warm 4.4 s → 2.8 s
  - ✓ C · Salting in detail: deterministic salt, hot keys only, outer joins, aggregations, drawbacks — 2026-10-01 10:02: check ✓ (LEFT JOIN: salt fact, replicate dim); random-salt risk, SQL versions (Trino / Hive), salt-column choice discussed
  - ✓ E3 · Exp 3: AQE skew join and broadcast on the same data — when is salting unnecessary? — 2026-10-01 10:40: both predicted and run (AQE 2.6 s, broadcast 3.3 s vs salted 2.8 s, plain 4.4 s); check ✓ (skewed collect_list aggregation → two-phase salting)
  - ✓ D · Recruiter drill — 2026-10-01: 5/5 correct in substance; Q2 mechanism and Q4 "when to avoid" to tighten
- Edges: M3-Q4,M1-E→A→E1→B; B→E2→C; B→E3; C,E3→D
- Module 5 complete 2026-10-01: all four D targets reached; three I targets at E (cold drill pending)

Previous module plan (Module 4, completed 2026-09-30):

- Module: 4 — Joins + Catalyst + AQE
- Approved on: 2026-09-29 11:35
- Nodes (✓ done, → next):
  - ✓ A · Two join layouts: co-partition both sides by shuffle, or copy the small side to every task (from M1-G: a task can only match rows it can see) — 11:50: check ✓ (free-form: all 24 M rows move in co-partitioning)
  - ✓ B · Two local algorithms: hash (build in memory) vs sort-merge (spills) → the strategy grid (no-equality cell left open for E3) — 11:55: check ✓ (20 GB hot partition: SHJ fails, SMJ spills); closes the Q1 probe edge
  - ✓ E1 · Exp 1: fact + dimension — default strategy? Forced alternatives (hints): stages, shuffle, runtime — 12:15: 3 predictions ✓ (BHJ 1.1 s < SHJ 2.9 s < SMJ 3.7 s); hints taught; check ✓ (broadcast hint on 5 GB: tries, fails on the driver)
  - ✓ E3 · Exp 3: no equality condition — what can Spark do? (variant: broadcast disabled) — 21:55: A/B CartesianProduct (unknown RDD size), variant C BNLJ (8 tasks, 2 M reads); grid completed; check ✓ (LEFT OUTER range join, 1 TB each → BNLJ broadcasting 1 TB)
  - ✓ D · How Spark picks: rules, thresholds, first match; what it knows about sizes (Catalyst end to end) — 2026-09-30 11:55: first check ✗ (chose SHJ for a 50 MB dim: reasoned about what is sensible, not the first-match list); re-check ✓ (threshold 100 MB → BHJ); why SMJ is preferred over SHJ explained
  - ✓ E2 · Exp 2: large-on-disk dimension filtered to small — static plan? AQE at runtime (off vs on)? Initial vs final plan; few-keys variant — 2026-09-30: 3 predictions logged (Run 1 ✓, Run 2 ✓ but missed the sunk fact shuffle, Run 3 ✗); check ✓ (broadcast hint avoids the fact shuffle)
  - ✓ F · Recruiter drill — 2026-09-30: 7 answers: 4 correct, 3 partial (when not to broadcast / hint guarantee; `explain` listed as an action; BNLJ vs CartesianProduct task count)
- Edges: M1-G→A→B; B→E1; B→E3; M2-C,B→D→E2; E1,E3,E2→F
- Module 4 complete 2026-09-30 20:00: all D and E targets reached; both I targets at E (cold drill pending)

Previous module plan (Module 3, completed 2026-09-28):

- Module: 3 — Partitions and shuffle (Modules 1 and 2 plans completed; M1 `I` levels pending cold drills, deferred by the learner until after Module 3)
- Approved on: 2026-09-21 10:50
- Nodes (✓ done, → next):
  - ✓ A · Four kinds of partition: input / execution / shuffle / Iceberg table — each answers a different question, each has its own source of the number (root) — 11:05: check ✓ (Iceberg one-day filter: splits of that day's files, then shuffle.partitions)
  - ✓ B · Input partitions: files → splits → bin-packed partitions (maxPartitionBytes, openCost, splittable or not) — 11:15: check ✓ (16 partitions for 16 × 69 MB files); explained the CSV 4 files → 8 tasks from Module 1
  - ✓ C · Exp 1: `groupBy(customer_id)` — where is the Exchange, how many aggregate nodes, shuffle write / read per task? Variant: `repartition(customer_id)` first — 11:55: 2 predictions logged (2.84 MiB vs 231 MiB; partial aggregation; fair re-run 0.6 s vs 1.0 s); check ✓ (collect_list ≈ B)
  - ✓ D · Exp 2: `repartition(n)` vs `coalesce(n)` — which one shuffles? What happens to the stage upstream? — 2026-09-26: 3 predictions logged (coalesce(4) 3.4 s on 4 tasks vs repartition(4) 2.3 s; `.rdd` under AQE ran a 1.28 GB shuffle); partitions-as-task-descriptions, shuffle file layout, map-output statistics, reduce locality explained on request; check ✓ (repartition(10) after an expensive filter)
  - ✓ E · Exp 3: `spark.sql.shuffle.partitions` set badly — too low, too high (AQE coalescing off), then on, then a chosen value — 2026-09-28: original workload hit WindowGroupLimit (design flaw, fixed with a full `row_number` + noop sink); A–E logged (4 → 14.6 s, 2000 → 8.0 s, 2000+AQE → 21 tasks 5.2 s, 4+AQE unchanged, own 21 → 5.4 s); local vs remote shuffle bytes explained; check ✓ (2 TB at 200 → 200 × 10 GB)
  - ✓ F · Recruiter drill — 2026-09-28: 5/5 correct in substance; Q1 cause and Q2 consequences to tighten
- Edges: M1-E→A→B; A,M1-H→C; C→D; C→E; B,D,E→F
- Module 3 complete 2026-09-28 23:10: all D targets reached; both I targets at E (cold drill pending)

## Competency evidence

### 1. Execution model + actions / transformations

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Classify every call in a pipeline as transformation or action, before running it | I | I | 2026-09-16: derived the return-type definition from Exp 1; classified distinct / toPandas / isEmpty correctly (exact set). 2026-09-30 cold drill: correct and concise (Cold = yes) |
| Explain lazy evaluation and why Spark is lazy | I | I | 2026-09-20: drill answers 2, 4, 7 correct; checks A3, Q4, Q5, Cold 2 passed. 2026-09-30 cold drill: "so the plan has all the steps and can be optimized" — correct and concise (Cold = yes) |
| Show which calls start a job and which do not (Spark UI Jobs tab) | D | D | 2026-09-16: Exp 1 rows in the prediction log — predicted 6 steps, ran them, read the Jobs tab (0 jobs for 5 chained transformations; 4 jobs for `count()`; 3 for `show(5)`; 0 for `explain()`) |
| Experiment 3: predict the job count for a CSV read with and without a schema, before any action | D | D | 2026-09-17: Exp 3 rows in the prediction log — predicted A–D, ran, read the Jobs tab (1 / 2 / 0 / 0 jobs; full 66.6 MB pass for `inferSchema`); explained why a CSV needs a job for its header ("no metadata in the file") |
| Predict jobs, stages, and tasks for a small pipeline and check against the Spark UI | D | D | 2026-09-19/20: Exp 2 rows in the prediction log — predicted jobs / stages / tasks / Exchange / join, ran the write, read Jobs, Stages and SQL tabs (3 jobs; stages 1·8·1 tasks + 1 skipped; one Exchange at the aggregation, AQEShuffleRead 200→1; BroadcastHashJoin). Misses were the AQE/broadcast job packaging; plan structure predicted correctly |
| Explain narrow vs wide, and why a wide transformation can create a stage boundary | I | I | 2026-09-20: drill answers 5, 6 correct; checks G2 and H passed; Exp 2 Variant predicted correctly. 2026-09-30 cold drill: wide = needs rows from other tasks, so data must land before the next stage — correct and concise (Cold = yes) |

### 2. DataFrames + Spark SQL essentials

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Compare physical plans of equivalent `spark.sql()` and DataFrame API code | D | D | 2026-09-20: Exp 1 rows in the prediction log — predicted, ran, compared `explain("formatted")` for A/B/C and read join input rows in the SQL tab (identical plans for same shape; join-first SQL keeps its shape, 741,717 vs 10,000 rows into the join) |
| Read the sections of `explain("formatted")` | E | E | 2026-09-20: probe Q1 ✗ (analyzed vs optimized) → node C taught; check ✓ (column pruning = optimizer); read three formatted plans node for node in Exp 1 and located the first differing node |
| Explain why native expressions beat unnecessary Python UDFs | E | E | 2026-09-21: probe Q3/Q4 ✗ (thought built-ins run in Python) → nodes A and D taught; explained "pandas has higher fixed cost per batch, lower per-row cost" in own words; check ✓ (built-ins first when a UDF blocks pushdown) |
| *Optional:* compare plan and runtime of a native expression vs a Python UDF | D | D | 2026-09-20: Exp 2 rows in the prediction log — predicted extra nodes / pushdown / order, ran, read `BatchEvalPython` / `ArrowEvalPython` and `PushedFilters` from the plans, measured 2 M and 20 M rows (0.58 / 2.05 / 0.94 s) |

### 3. Partitions and shuffle

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Distinguish input, execution, shuffle, and Iceberg table partitions | I | E | 2026-09-28: probe Q1/Q5 ✗ → node A taught; check ✓ (Iceberg one-day filter → splits, then shuffle.partitions); drill answers 4 and 5 correct |
| Experiment 1: predict shuffle and `Exchange` placement for `groupBy().count()` | D | D | 2026-09-21: Exp 1 rows in the prediction log — predicted Exchange / HashAggregate placement and shuffle size for plain groupBy and for repartition-then-groupBy, ran both, read Shuffle Write / Read totals and per-task records in the Stages tab (2.84 MiB / 160 K vs 231 MiB / 24 M), fair re-run timed |
| Experiment 2: `repartition()` vs `coalesce()`, and when each shuffles | D | D | 2026-09-25/26: Exp 2 rows in the prediction log — predicted jobs / stages / tasks / shuffle for coalesce(4) and repartition(4) and the coalesce(32) / repartition(32) counts, ran, read Jobs and Stages tabs (1 stage of 4 tasks, no shuffle, 3.4 s vs 16 + 4 tasks, 257 MiB shuffle, 2.3 s; 16 / 32; 4 files each) |
| Experiment 3: inappropriate vs better `spark.sql.shuffle.partitions`, with task metrics | D | D | 2026-09-28: Exp 3 rows in the prediction log — predicted A–D (and C's task count from the formula), ran, read reduce-stage task counts, shuffle read quantiles, spill and durations (4 tasks × 312 MiB 14.6 s; 2000 × 0.6 MiB 8.0 s; AQE 21 × 61 MiB 5.2 s; 4 + AQE unchanged); chose 21 by size → 5.4 s |
| Point at every shuffle in a physical plan and explain why it exists | I | E | 2026-09-28: located every Exchange in M1 Exp 2, M3 Exp 1 and Exp 3 plans and explained each (partial/final aggregate, repartition, window, WindowGroupLimit); checks C and E ✓; drill Q1 cause phrasing to fix |

### 4. Joins + Catalyst + AQE

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Name Catalyst phases and find them in `explain` output | E | E | 2026-09-20/30: M2 node C check ✓ (column pruning happens in the optimizer; read the sections of `explain`), M4 node D (strategy selection as first match in physical planning) re-check ✓ |
| Fact + dimension under different strategies: predict, run, compare | D | D | 2026-09-29: Exp 1 rows in the prediction log — predicted strategy / exchanges / sorts / order of runtimes for default, merge and shuffle_hash, ran, read join nodes and shuffle writes (BHJ 1.1 s, SHJ 2.9 s, SMJ 3.7 s) |
| Explain why Spark picked a join strategy, given plan and table sizes, and propose alternatives | I | E | 2026-09-30: node D re-check ✓ (walked the first-match list), E1 / E2 checks ✓ (broadcast hint on 5 GB; hint avoids the fact shuffle); drill answers 1, 6 correct, 3 half |
| Explain when `ShuffledHashJoin` is used instead of `SortMergeJoin`, and its risks | I | E | 2026-09-29/30: node B check ✓ (20 GB hot partition: SHJ fails, SMJ spills); drill answer 2 correct (risk to be added) |
| Show how a bad size estimate leads to an inefficient plan, and what AQE does about it | D | D | 2026-09-30: Exp 2 rows in the prediction log — predicted static and adaptive strategies, ran AQE off / on, read `explain("cost")` (Filter 147 MiB = Relation 147 MiB vs 0.42 MiB actual) and the executed plans (SMJ 5.2 s → BHJ 2.6 s, fact shuffle still written) |
| Compare AQE initial vs final plan and explain what changed | D | D | 2026-09-30: Exp 2 Runs 2 and 3 — reported the initial SMJ and the final plan (BroadcastExchange, no Sort, fact Exchange still present); asked why the fact was still shuffled and why three keys kept SMJ; both explained from the stage metrics |
| Recognize `BroadcastNestedLoopJoin` and explain why it can be dangerous | E | E | 2026-09-29: Exp 3 (CartesianProduct vs BroadcastNestedLoopJoin observed and explained: N × M comparisons, last-resort fallback); check ✓ (LEFT OUTER range join on 1 TB tables → BNLJ trying to broadcast 1 TB) |

### 5. Data skew + salting

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Explain why skew occurs | I | E | 2026-09-30/10-01: probe Q1 ✗ (blamed the join algorithm) → node A; checks A (window yes, sum / broadcast no) and E1 (400 cores) ✓; drill answers 1, 5 correct |
| Recognize skew from task metrics in the Spark UI | D | D | 2026-09-30: Exp 1 rows in the prediction log — predicted stage and signature, ran, read the join stage's Summary Metrics (max 290 MiB / 6.04 M rows vs median 2.8 MiB / 50 K rows; 2 s vs 37 ms) with coalescing on and off |
| Implement salting on a skewed join | D | D | 2026-09-30: wrote the salted join in `02_salting.ipynb` (deterministic `pmod(hash(order_id), 16)` on hot keys only, `explode` replication on the dim, join on `(customer_id, salt)`); correctness cell: 6 M / 8 M rows identical to the plain join |
| Measure before/after: task durations, partition sizes, runtime, shuffle behavior | D | D | 2026-09-30: Exp 2 row in the prediction log — max/median shuffle read 290 / 59 MiB → 61 / 59 MiB; max task 2.36 s → 1.53 s; fact write +20 MiB, dim +15 rows; warm runtime 4.4 s → 2.8 s |
| Compare salting with the other solutions on the same data | D | D | 2026-10-01: Exp 3 rows in the prediction log — predicted and ran AQE skew join (1 skewed partition, 8 splits, 2.6 s) and broadcast (527 MiB build, 3.3 s) against plain 4.4 s and own salting 2.8 s; read the skew metrics on both AQEShuffleRead nodes |
| Explain which side is salted and what happens to the other side | I | E | 2026-10-01: probe Q3 ✓; implemented it (Exp 2); node C check ✓ (LEFT JOIN: salt fact, replicate dim); drill answer 3 correct |
| Explain drawbacks and when not to salt | I | E | 2026-10-01: node B check ✓ (broadcast first for a 20 MB dim), E3 check ✓ (salted two-phase aggregation when AQE can't split); drill answer 4 correct on drawbacks, "when to avoid" to add |

### 6. Spark UI + troubleshooting

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Find each key metric in Jobs, Stages, Tasks, Executors, SQL, and the History Server | D | - | |
| Diagnose at least three scenarios on actual broken lab jobs: evidence → hypothesis → change → before/after | D | - | |
| Write my own troubleshooting workflow and apply it to all four scenarios | D | - | |
| Scenario 1: one task far slower than 499 others | I | E | 2026-10-01: free-form answer (skew only) → lab job diagnosed (non-splittable gz: slow task in the scan stage, Input 3× / records 6× the median); own amendment "first see where the task difference happened: after a shuffle → skew, otherwise something else"; check ✓ (normal data size → straggler, speculation helps) |
| Scenario 2: 20-minute job now takes 2 hours, structured investigation | I | E | 2026-10-01: free-form skeleton (compare with previous runs; expected growth?; compare stages); diagnosed the two History Server runs unaided (dimension grew → BHJ flipped to SMJ); proposed fixes (rule out code change, expected growth?, broadcast hint, shuffled hash); the Environment-tab check still open |
| Scenario 3: shuffle partitions 200 → 20 made it slower | I | E | 2026-10-01: diagnosed `scenario_3.ipynb` (2 tasks, lost parallelism, AQE can't help); spill / working-set half taught from his own run (623 MiB per task, 2 GB spilled); S4 check ✓ |
| Scenario 4: heavy spill, is more executor memory the answer? | I | E | 2026-10-01: "helps, but not necessarily the best solution; check where the spill is happening; repartition"; check ✓ (uniform spill → more partitions; one task → skew) |

### 7. Memory + performance essentials

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Explain the chain: very large partition → large task working set → memory pressure → GC / spill / OOM | I | - | |
| Reproduce spill, then reduce it without adding memory | D | - | |
| Distinguish driver OOM from executor OOM by cause | I | - | |
| Argue why OOM does not automatically mean more executor memory, with alternatives | I | - | |

### 8. Spark + Iceberg

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Write with `writeTo()` / DataFrameWriterV2 and SQL `INSERT` / `MERGE` / `UPDATE` / `DELETE` (the `MERGE` part is explanation only if Budget cut 3 applies) | D | - | |
| Small files: produce too many, measure via metadata tables, improve, measure again | D | - | |
| Explain how execution partitions and write distribution determine file count and size | I | - | |
| Explain what `MERGE` rewrites and why it can be expensive | I | - | |

### 9. Production basics + recruiter review

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Explain `spark-submit` resources, client vs cluster mode, dynamic allocation | I | - | |
| Explain YARN components and executor container sizing | E | - | |
| Explain Oozie workflow, Spark action, coordinator, retries | E | - | |
| Full rapid-drill set: every question listed in the Module 9 rapid drill has a Cold = yes, Correct = yes row | I | - | |

### Mini-capstone

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Diagnose and fix each hidden problem, one variable at a time, with a full write-up | D | - | |

## Session log

| Date | Module | Start–end | Hours | Covered | Next step |
| --- | --- | --- | --- | --- | --- |
| 2026-09-16 | 1 | 20:05–21:35 | 1.5 | Probe (4 edges recorded); plan approved; lab 01 generated + data; nodes A, B (Exp 1, 6 predictions), C (definition by return type). Side facts: Parquet read runs a 1-task schema-inference job; path vs catalog door; what a shuffle is | Node D: Exp 3 (`03_csv_schema.ipynb`) — predictions A–D requested, not yet given |
| 2026-09-17 | 1 | 16:29–18:10 | 1.7 | Cold re-check (`groupBy().count()` ✗, repaired); node D (Exp 3, 4 predictions; JSON check ✗, catalog check ✓); nodes E, F, G, H with checks; Exp 2 predictions logged (5 rows). Side: standalone app holds all cores → "Initial job has not accepted any resources" | Node I: run the Exp 2 write in `02_pipeline.ipynb`, report UI; then cold re-check + recruiter drill (J) |
| 2026-09-18 | 1 | 19:36–19:40 | 0.1 | Status recap only; nothing run | Run the Exp 2 write |
| 2026-09-19 | 1 | 19:33–20:00 | 0.5 | Ran the Exp 2 write; 3 of 5 predictions graded (jobs, stages, tasks); explained AQE stage-by-stage jobs, skipped stages, WholeStageCodegen, filter fusion + pushdown | Exp 2: SQL-tab report (Exchange, join node) + Variant prediction; learner still unconvinced about multiple jobs per action |
| 2026-09-20 | 1 | 13:15–15:40 | 2.4 | Exp 2 finished (SQL tab: Exchange, BroadcastHashJoin; AQE-off change-one-thing ✓; Variant ✓); cold re-check ✓; recruiter drill 7/7 (2 to tighten); teacher notes updated with lab outcomes. Module 1 plan complete: all D targets reached, I pending | Cold-drill M1 `I` items at the start of a later session; continue with Module 2 |
| 2026-09-20 | 2 | 15:40–17:10 | 1.5 | Probe (3 edges); plan approved; lab 02 generated; nodes A, B, C; Exp 1 (3 predictions: same-shape plans identical, join-first SQL keeps its shape, 741,717 vs 10,000 rows into the join); Exp 2 (BatchEvalPython / ArrowEvalPython, no pushdown, timings at 2 M and 20 M rows); node D exposition delivered, check pending | Node D check → recruiter drill (F) → close Module 2 |
| 2026-09-21 | 2 | 10:11–10:45 | 0.5 | Partition-count / AQE questions answered; node D check ✓; recruiter drill 2/3 (explain modes incomplete); Module 2 closed (all targets reached). Learner deferred the M1 cold drill until after Module 3 | Module 3 |
| 2026-09-21 | 3 | 10:36–12:10 | 1.6 | Probe (2 edges); plan approved; lab 03 + 24 M-row data; nodes A, B; Exp 1 (partial aggregation: 2.84 MiB vs 231 MiB; fair re-run 0.6 s vs 1.0 s); check ✓; repartition use cases and AQE correction discussed | Node D: Exp 2 predictions (coalesce(4) vs repartition(4), coalesce(32)/repartition(32)) |
| 2026-09-23 | 3 | 18:57–19:10 | 0.2 | Driver explained concretely (kernel ↔ driver JVM in the jupyter container; client mode; ways to break it); status recap | Node D: Exp 2 predictions |
| 2026-09-25 | 3 | 10:50–11:00 | 0.2 | Links recap; Exp 2 predictions given (logged) | Run Exp 2 |
| 2026-09-26 | 3 | 15:35–16:45 | 1.2 | Exp 2 run + graded; deep-dive Q&A (partitions as task descriptions, `.rdd` under AQE, shuffle file layout, map-output statistics, reduce locality, coalesce vs repartition cases); node D check ✓ | Node E: Exp 3 predictions |
| 2026-09-28 | 3 | 10:38–23:10 (intermittent) | 2.5 (est.) | Exp 3 (WindowGroupLimit design flaw found and fixed; runs A–E); shuffle total / local vs remote bytes / partition sizing explained; node E check ✓; recruiter drill 5/5 (2 to tighten); Module 3 closed (D targets reached, I at E) | Module 4 (Joins + Catalyst + AQE): probe → plan. Cold drill for M1 + M3 `I` items after Module 4 (learner's choice). Keep deep-dives short; park them in the roadmap |
| 2026-09-29 | 4 | 11:14–? (end time not captured: `date` unavailable) | ~1.5 (est.) | Probe (3 edges: SHJ-can-spill, size from row stats, 100 MB threshold); plan approved; lab 04 + customers_big (149 MiB); nodes A, B, E1 (BHJ 1.1 s < SHJ 2.9 s < SMJ 3.7 s; hints); Exp 3 A/B (CartesianProduct: Python-list DataFrame has unknown size → never auto-broadcast; 64 tasks, orders read 8×); Spark vs Trino broadcast path | Exp 3 variant C prediction (`F.broadcast(bands)`: join node, BroadcastExchange, tasks/reads vs 64 / 16 M), then node D and Exp 2 |
| 2026-09-29 | 4 | 21:44–22:40 (est.) | 0.9 | Exp 3 variant C (BNLJ, 8 tasks / 2 M reads) ✓; grid completed; E3 check ✓; partition count vs size estimate (parallelize → default parallelism), Cartesian scaling; node D exposition (first-match strategy list, `sizeInBytes` sources, Catalyst end to end); why SMJ is preferred over SHJ | Node D check (dismissed twice, still open) → Exp 2 → drill → cold drill |
| 2026-09-30 | 4 | 10:34–12:45 (est.; app restart in between) | 1.5 | Node D check (✗ then ✓: walk the first-match list); Exp 2 three runs (Filter estimate = Relation 147 MiB; SMJ 5.2 s → AQE BHJ 2.6 s with fact shuffle still written; 3 keys keep SMJ: 20 % non-empty guard); join-side partition alignment, task = 1 core explained | E2 check → recruiter drill → cold drill |
| 2026-09-30 | 4 | 19:40–20:40 | 1.0 | E2 check ✓; recruiter drill (4 correct, 3 partial); Module 4 closed; cold drill for M1/M3: three `I` awarded (classify, laziness, narrow/wide), two M3 items stay E; Q&A: laziness vs Catalyst, AQE skew split, CartesianProduct vs BNLJ, shuffle file layout for a join, shuffle.partitions without AQE, repartition vs coalesce use cases, why AQE isn't optimal | Module 5: probe → plan |
| 2026-09-30 | 5 | 20:40–23:20 | 2.7 | Probe (4 edges); plan approved; lab 05 + orders_skew (14 M rows, 601 MB); nodes A, E1 (baseline + no-coalescing run), B; E2: learner implemented salting (correct; 121× → 1.05×; warm 4.4 s → 2.8 s); node C taught (random salt risk, SQL versions in Trino/Hive, choosing the salt column) | Node C check (open: LEFT JOIN — which side salted / replicated) → Exp 3 (`03_alternatives.ipynb`: AQE skew join, broadcast) → recruiter drill → Module 6 |
| 2026-10-01 | 5 | 10:00–10:37 | 0.6 | Node C check ✓; Exp 3 (AQE skew join: 1 skewed partition, 8 splits, 2.6 s; broadcast: 527 MiB build, 3.3 s); E3 check ✓; recruiter drill 5/5; Module 5 closed (D targets reached, I at E) | Module 6: probe → plan |
| 2026-10-01 | 6 | 11:08–14:18 | 3.2 | Probe (2 edges); plan; lab 06 (events gz, two History Server runs, scenario 3); node A; workflow v1 saved in `notes/troubleshooting_workflow.md`; S1 (gz, diagnosed with guidance), S2 (join flip, diagnosed unaided), S3 (200 → 2: parallelism + 2 GB spill), S4 check ✓. Side topics: driver anatomy, spill sources, stage roles, GC, caching, SQL hints / INSERT modes, statistics (Iceberg estimate verified by researcher), staging tables, History Server ↔ notebook. Learner left for an interview; an untaught briefing on M7–M9 essentials was given in chat (not evidence) | Resume Module 6 at node W (final workflow v2), S2 check (Environment tab), recruiter drill F; then Modules 7, 8, 9 and the capstone |

## Prediction log

One row per prediction, written **before** the run; Actual and the explanation are filled in right after it.
A before/after comparison uses two rows.

| Date | Module | Experiment | Prediction | Actual | Why they differ |
| --- | --- | --- | --- | --- | --- |
| 2026-09-16 | 1 | Exp 1 step 1: `spark.read.parquet` ×2 | 1 job ("for the driver") | 2 jobs, one per `read` call, 1 task each, named `parquet at …` (learner first read it as "1 per file"; orders has 8 files, job had 1 task) | metadata resolution (schema) can itself use the cluster; 1 job per read, not per file, not "for the driver" |
| 2026-09-16 | 1 | Exp 1 step 2: chain filter→withColumn→groupBy().count()→join→select | 0 jobs | 0 jobs | ✓ |
| 2026-09-16 | 1 | Exp 1 step 3: `select(col("amout"))` typo | error now | error immediately (analysis) | ✓ |
| 2026-09-16 | 1 | Exp 1 step 4: `top.count()` jobs / stages / tasks | 0 new jobs | 4 jobs: [1 task: read customers] → [8 tasks: scan orders 8 files, shuffle write 745 KB] → [1 task + 8 skipped: shuffle read, final agg, join, partial count] → [1 task + 9 skipped: final count] | `count()` is an action; one action = several jobs (broadcast job + one job per AQE shuffle stage); skipped stages = reused shuffle output; post-shuffle 1 task = AQE coalescing (parked for M3) |
| 2026-09-16 | 1 | Exp 1 step 5: `top.show(5)` | 1 new job; redoes all the work | 3 new jobs; orders rescanned with 8 completed tasks, 973 KB shuffle rewritten; customers re-read | job count ✗ (same reasons as step 4); redo ✓: nothing survives between actions without `cache()` |
| 2026-09-16 | 1 | Exp 1 step 6: `top.explain()` | 0 jobs (like EXPLAIN in Greenplum) | 0 jobs | ✓ |
| 2026-09-17 | 1 | Exp 3 read A: CSV, header only, no schema | 1 job ("no metadata in the file, so a job is needed") | 1 job, 1 task, 1 record read (header line); schema all strings | ✓ |
| 2026-09-17 | 1 | Exp 3 read B: CSV, `inferSchema=True` | not sure; probably 1 new job, 4 tasks (4 files) | 2 new jobs: 1 task (header line) + 8 tasks reading all 66.6 MB / 2,000,004 records; inferred int / double / date | inference = header read + a full pass at definition time; tasks follow splits, not files (M3) |
| 2026-09-17 | 1 | Exp 3 read C: CSV, explicit `.schema(...)` | 0 new jobs (schema is provided) | 0 jobs; declared types (BIGINT …) | ✓ |
| 2026-09-17 | 1 | Exp 3 `printSchema()` | not an action; it prints DataFrame metadata | 0 jobs | ✓ |
| 2026-09-17 | 1 | Exp 2 (filter→groupBy→join→write): jobs | 1 job | 3 jobs for the write (5 in the app: 2 are the Parquet schema-inference jobs from the reads) | one action = several jobs: broadcast build is its own job, and AQE submits each shuffle stage as its own job (same lesson as Exp 1) |
| 2026-09-17 | 1 | Exp 2: stages and what separates them | 4 stages ("filter, then shuffling of 2 tables") | 3 stages ran + 1 skipped: [read customers] · [scan+filter+partial agg → shuffle write 1.4 MB] · [shuffle read → final agg → join → write 113 KB]; the skipped one is the map stage listed again under job 4 | filter is narrow and fuses into the scan stage; only ONE shuffle (groupBy); customers is never shuffled; "4th" stage = reused shuffle output, not new work |
| 2026-09-17 | 1 | Exp 2: tasks per stage | 8 in stage 1, 8 in stage 2, 9 in stage 3 ("broadcast of the small one and aggregate") | 1 · 8 · 1 (+8 skipped) | customers = 1 file → 1 task; orders = 8 files → 8 tasks; post-shuffle 1 task = AQE coalesced 200 → 1 for a 1.4 MB shuffle (M3) |
| 2026-09-17 | 1 | Exp 2: where `Exchange` appears | "in the 3rd stage" | SQL tab (2026-09-20): one `Exchange` between the partial and final `HashAggregate` (200 partitions, 79,989 records / 1381 KiB written, then `AQEShuffleRead` coalesced to 1); plus a `BroadcastExchange` on the customers side (collect 757 ms, 1102 KiB) | ✓ in substance (one shuffle, at the aggregation); precision: an Exchange is the boundary between two stages, not inside one; BroadcastExchange is a different kind (no shuffle) |
| 2026-09-20 | 1 | Exp 2 change-one-thing: same write with `spark.sql.adaptive.enabled=false` | 2 jobs: [1 stage: read + broadcast customers], [2 stages: read orders + our operations]; last stage 200 tasks | 2 jobs: job 5 = 1 stage / 1 task (customers, 10,000 recs); job 6 = 2 stages: 8 tasks (scan, shuffle write 1.4 MB) + 200 tasks (shuffle read, agg, join, write 473 KB in 200 files) | ✓ all three; with AQE off the classic model holds: one job holds all shuffle-separated stages, and the reduce side keeps `spark.sql.shuffle.partitions` = 200 tasks (no coalescing) → 200 small output files (473 KB vs 113 KB) |
| 2026-09-20 | 1 | Exp 2 Variant: `result.groupBy("customer_id").agg(max("total"))` — shuffle `Exchange` count in the plan | same as `result`: 1 ("since we are grouping by customer_id") | 1: the original `Exchange hashpartitioning(customer_id, 200)`; the new final `HashAggregate` sits directly on `BroadcastHashJoin`; `n` pruned from the shuffle | ✓ — BHJ preserves the streamed side's partitioning; closes the Q6 probe edge with evidence |
| 2026-09-20 | 2 | Exp 1: SQL (CTE, same shape) vs DataFrame API | same physical plan; `sameSemantics` probably False ("the SQL needs to be parsed") | physical plans identical node for node; `sameSemantics` False | plan ✓; False ✓ but for the wrong reason: `sameSemantics` compares canonicalized *analyzed* plans (subquery aliases, projection nesting, ON vs USING still present), not optimized ones |
| 2026-09-20 | 2 | Exp 1: natural SQL (join first, group by all) vs DataFrame API | Catalyst rewrites it to aggregate-first; same physical plan | different: `BroadcastHashJoin` below the aggregate, as written | ✗ — Catalyst does local rewrites (pushdown, pruning, folding), not algebraic restructuring; no aggregate-through-join rule |
| 2026-09-20 | 2 | Exp 1: rows entering the join node, A/B vs C | "should be the same for all 3" | A/B: 10,000; C: 741,717 | ✗ — query shape decides the row volume through the join (74×); cheap here only because it is a broadcast join |
| 2026-09-20 | 2 | Exp 2: extra operator in the UDF plans | "a Python part for the UDF on the executors" (no node name; no distinction pandas vs plain) | `BatchEvalPython` (plain UDF) and `ArrowEvalPython` (pandas UDF) between Scan and Filter | ✓ in substance; names/transport (pickle vs Arrow) taught |
| 2026-09-20 | 2 | Exp 2: `PushedFilters` on the scan | native yes; UDF versions no ("Catalyst doesn't see inside a UDF: full scan, then UDF") | native: `[IsNotNull(amount)]` only; both UDF plans: none | ✓; subtlety: `floor(amount/100) == 3` is not pushable either (Parquet pushdown takes plain column comparisons), so the native scan only pushed IsNotNull |
| 2026-09-20 | 2 | Exp 2: runtime order (2 M rows, 250 k per task) | native < pandas UDF < Python UDF (no ratio given) | run 1 (warm-up): 1.93 / 1.30 / 0.91 s; run 2: native 0.17 s, Python UDF 0.47 s, pandas UDF 0.76 s | native fastest ✓ (≈3×); pandas slower than plain Python ✗ — at this scale fixed overheads dominate; not a valid conclusion → change one thing: 20 M rows |
| 2026-09-20 | 2 | Exp 2 change-one-thing: 20 M rows (2.5 M per task), same three filters | (no prediction given — ran directly) | native 0.58 s, Python UDF 2.05 s, pandas UDF 0.94 s | native 3.5× faster than the plain UDF; pandas UDF 2.2× faster than plain Python once per-row cost dominates fixed overhead |
| 2026-09-21 | 3 | Exp 1A: plain `groupBy(customer_id)` on orders_big | 1 Exchange between groupBy and aggregation; 1 HashAggregate, after the Exchange; 16 map tasks; reduce "probably the same number"; shuffle write: "no idea, depends on customer_id distribution" | 1 Exchange between a *partial* and a *final* HashAggregate (2 nodes); 16 map tasks; reduce 2 tasks (AQE: 2.84 MiB / 8 → 1 MB min); shuffle write 2.84 MiB / 160,000 records (16 × 10,000); wall 2.3 s (cold) | partial (map-side) aggregation for decomposable aggregates shrinks the shuffle 80×; AQE formula confirmed |
| 2026-09-21 | 3 | Exp 1B: `repartition(customer_id)` then the same groupBy | "probably the same"; maybe A keeps 16 tasks without AQE and B has fewer partitions | 2 Exchanges? no — 1 Exchange (the repartition), then partial + final HashAggregate back to back in the reduce task; shuffle write 231 MiB / 24 M records; reduce 9 tasks (231 / 8 ≈ 29 MB target); wall 1.5 s (warm cache) | the shuffle moved before the partial aggregate, defeating it: 80× more bytes; wall time inconclusive at lab scale (order effect) → fair re-run: A 0.6 s, B 1.0 s (warm, both) — the 80× fewer bytes wins even locally |
| 2026-09-25 | 3 | Exp 2A: `filter → coalesce(4) → write` | 1 job, 1 stage ("coalesce, then filter"), 4 tasks; no shuffle; (files not stated) | 1 job, 1 stage, 4 tasks reading all 24 M rows (4 of 8 cores busy); no shuffle; 194 MiB out; wall 3.4 s | ✓ — coalesce is narrow: the merge reaches back through the whole stage, so scan + filter ran on 4 tasks |
| 2026-09-25 | 3 | Exp 2B: `filter → repartition(4) → write` | 2 stages ("filter, then repartition"); (jobs, tasks, files, runtime not stated) | 2 jobs; 16-task map stage (scan + filter, shuffle write 257.6 MiB) + 4-task stage (shuffle read 257.6 MiB, 198 MiB out); wall 2.3 s — faster than A | learner expected coalesce to be faster; the shuffle cost less than the parallelism coalesce(4) lost |
| 2026-09-25 | 3 | Exp 2C: `coalesce(32)` / `repartition(32)` on 16 partitions | "coalesce will leave the same (16), repartition will repartition (32)" | 16 and 32 ✓; side effect: `repartition(32).rdd.getNumPartitions()` ran a 16-task job shuffle-writing 1.28 GB (AQE finalizes the plan by executing the query stages); `coalesce(32).rdd` ran nothing | `.rdd` on an AQE plan is not free |
| 2026-09-28 | 3 | Exp 3A (original workload: `row_number` + `filter(rn == 1)`), `shuffle.partitions=4`, coalescing off | 4 reduce tasks; shuffle read per task unknown ("can't estimate without the dataset size"); spill yes; slow | 4 tasks, 1,907 KiB / ~160 K records total (~475 KiB / ~40 K per task), no spill, 5.7 s | design flaw: Catalyst (Spark 3.5+) pushed a partial `WindowGroupLimit` below the Exchange (top-1 per customer per map task) — same idea as partial aggregation. Workload fixed: full `row_number` without filter, `write.format("noop")`; predictions below carried over unchanged |
| 2026-09-28 | 3 | Exp 3A (fixed workload): 4, coalescing off | (carried over) 4 reduce tasks; spill yes; slow | 4 tasks × ~312 MiB, task 10.9 s, no spill, wall 14.6 s (slowest) | tasks ✓, slow ✓, spill ✗ — fit in execution memory at lab scale; the cost was parallelism (4 of 8 cores idle) |
| 2026-09-28 | 3 | Exp 3B: 2000, coalescing off | 2000 reduce tasks; shuffle read slower than for 4 ("more files to read per partition"); probably no spill; scheduling takes time | 2000 tasks, median 0.6 MiB / 20 ms, no spill, wall 8.0 s | ✓ — per-task overhead (32,000 fetches vs 64); faster than A (all cores) but slower than C |
| 2026-09-28 | 3 | Exp 3C: 2000, coalescing on | AQE merges toward ~64 MB partitions; count unknown → after the hint (full shuffle ≈ 1,275.6 MiB): "around 20 tasks" | 21 tasks, median 61 MiB (min 24 MiB remainder), wall 5.2 s (fastest) | ✓ — target min(64 MB, 1,240/8) = 64 MB |
| 2026-09-28 | 3 | Exp 3E: learner's value, coalescing off | chose 21 ("by size, as calculated: ~64 MB per task"); no time prediction | 5.4 s (C with AQE: 5.2 s) | ✓ reasoning — hand-tuned count = AQE's; multiple of cores (16/24) would avoid a partial last wave |
| 2026-09-28 | 3 | Exp 3D: 4, coalescing on | nothing changes: AQE can only merge (and change joins), never split | 4 tasks × ~312 MiB, wall 10.1 s | ✓ — structure identical to A; time difference = warm cache |
| 2026-09-29 | 4 | Exp 3A: orders ⋈ bands on a range condition, defaults | broadcast (bands); nothing shuffled; (join node name not given) | `CartesianProduct Inner`, no Exchange, no BroadcastExchange; bands = `Scan ExistingRDD` (Python list → RDD → unknown size → never auto-broadcast); 3.2 s (cold) | broadcast ✗ (unknown size), no shuffle ✓ |
| 2026-09-29 | 4 | Exp 3B: same, `autoBroadcastJoinThreshold = -1` | "sends everything to 1 partition, since it can't shuffle on key"; probably SortMergeJoin | identical plan (`CartesianProduct`); 1.0 s (warm) | ✗ — no key to sort or co-partition by; Cartesian pairs partitions and tests every row pair |
| 2026-09-30 | 5 | Exp 1: orders_skew ⋈ customers_big (AQE skew join off, coalescing on) | SortMergeJoin; skew in the stage after the shuffle; one task far longer, the rest small and even; shuffle read: one task with the biggest amount (no numbers); spill probably yes; longer than M4 Exp 2 Run 1 (5.2 s) | SortMergeJoin; join stage 12 tasks: shuffle read min 5.3 / median 59.1 / max 290.4 MiB (93 K / 1.04 M / 6.04 M rows); duration 0.30 / 1.03 / 2.36 s; no spill; 4.4 s | strategy ✓, stage ✓, one-task signature ✓ (6× in rows, 2.3× in time); spill ✗ (hot bucket fits ~800 MB); runtime ✗ (14 M rows < 24 M; 12 tasks on 8 cores = two waves, hot task overlapped) — skew's damage is scale-dependent, its signature is not |
| 2026-09-30 | 5 | Exp 1 change-one-thing: AQE coalescing off | 200 tasks; median read smaller; max read smaller ("the coalesced task could have held other keys"); max/median ratio in rows bigger; runtime longer than 4.4 s | 200 tasks; median 2.8 MiB / 50 K rows, max 290.4 MiB / 6.04 M rows (121×); duration 37 ms median / 2 s max (54×); 3.7 s | 200 ✓, median ✓, ratio ✓; max ✗ (identical — the hot bucket was never merged, it already exceeded the target); runtime ✗ (faster: stage time ≈ longest task either way; small tasks pack the other cores better) |
| 2026-10-01 | 6 | Scenario 1, free-form (499 tasks 15–25 s, one 12 min): causes / checks / fixes | Causes: data skew or NULL values in the partitioning key, with AQE disabled, most rows landing in one partition. Checks: Stages tab — memory and time per task; whether AQE is on; whether partitions were empty. Fixes: turn AQE on, change the logic, broadcast hint if viable, salting; for empty partitions AQE or manual coalesce | rubric has three causes: key skew (shuffle read ≫ median), non-splittable input (input ≫ median in a scan stage), straggler node (normal data size; speculation helps only here) | one of three families named; no distinguishing metric |
| 2026-10-01 | 6 | Scenario 3 (`scenario_3.ipynb`: shuffle.partitions 200 → 2, AQE on) | "The second job wrote to 2 partitions, less parallelism. AQE doesn't help, it only helps when dealing with skew." | before: 22 tasks × ~57 MiB, 1.2–1.4 s, no spill, 5.7 s; after: 2 tasks × ~623 MiB, 18.7 s each, spill 1,984 MiB (memory) / 1,138 MiB (disk), peak execution memory 1,248 MiB, 20.0 s | parallelism ✓; AQE can't help ✓ but reason imprecise (it merges, never splits ordinary partitions); missed the working-set / spill half |
| 2026-10-01 | 6 | Scenario 2, free-form (20-minute job took 2 hours): investigation | "First compare the current run with previous runs — maybe the delta just got bigger and that is expected. If not, compare the stages between the runs, what is taking longer, and then figure out why." | rubric: scope what changed (data / plan / code-config / cluster / memory), compare with a good run, find the stage, uniform vs skewed, diff plans, hypothesis → one change → measure | sound skeleton (compare with a good run; find the stage); did not enumerate what can change |
| 2026-10-01 | 6 | Scenario 2, lab (two runs in the History Server) | "The table that used to be broadcast is now used for sort-merge; it got bigger." | 09-30: BroadcastHashJoin ×6, customers 100 K rows, shuffle 1.6 MiB, 8.6 s; 10-01: SortMergeJoin ×6 (+2 Sorts), customers 1 M rows, shuffle 1,616 MiB, executor time 97.5 s vs 28.9 s, 16.9 s | ✓ — correct cause, found unaided from the plans |
| 2026-10-01 | 6 | Scenario 1, lab job (`scenario_1.ipynb`) | Symptom: first HashAggregate slow; one task 9 s vs 2 s median / 75th → "probably skew"; fix: repartition by key then aggregate | scan stage, 9 tasks: slow task Input 345 MiB / 10.8 M records vs 114 MiB / 1.8 M median, 9.8 s vs 2.6 s, no shuffle read → one non-splittable `.csv.gz` (12 M rows) | symptom ✓; first hypothesis ✗; after being asked to check the stage's rows and the task's Input, reasoned "not by key — the scan built the partitions unevenly" and found the gz file himself |
| 2026-10-01 | 5 | Exp 3A: same join, AQE skew join on (defaults) | the hot partition qualifies (290 MiB > 256 MB and > 5× median); join-stage task count increases; duration lowers | fired: fact-side AQEShuffleRead 19 partitions = 11 coalesced + 1 skewed partition in 8 splits; dim side 19 (hot partition read 8×); join stage 19 tasks, max read 60.7 MiB, max task 1.39 s; warm 2.6 s | ✓ all three; splits = 8 map blocks of ~36 MiB (cut only between blocks) |
| 2026-10-01 | 5 | Exp 3B: `F.broadcast(customers_big)` | no slow task ("the data doesn't get distributed by key"); cost is on the driver ("it gets a big table"); faster than the others | BroadcastHashJoin BuildRight; join stage 8 tasks 1.1 / 1.3 / 1.3 s, no shuffle; BroadcastExchange data size 527.3 MiB (149 MiB on disk), collect 0.42 + build 0.95 + ship 0.46 s; 3.3 s | no slow task ✓, driver cost ✓; fastest ✗ — 1.8 s of broadcast overhead for a 2 M-row dim exceeds the skew it avoids (plain 4.4, salted 2.8, AQE 2.6, broadcast 3.3) |
| 2026-09-30 | 5 | Exp 2: salted join (hot key only, N_SALT = 16, deterministic salt, explode on dim) | max task ≈ 1/16 of baseline "a bit more, in that scope"; shuffle write bigger ("dim got more rows"); runtime a lot faster than 4.4 s | correct (6 M / 8 M rows match); join stage 16 tasks, read 39.4 / 58.6 / 61.3 MiB (max/median 1.05×), duration 1.16 / 1.53 s; fact write 722.1 MiB (+salt column), dim 153.7 MiB / 2,000,015 rows; wall 5.9 s (cold) | skew removed ✓; "1/16" ✗ — AQE coalescing re-packed the slices to ~60 MiB; shuffle growth ✓ but tiny (15 replicated rows); runtime ✗ — the stage already needed two ~1 s waves, so removing a 2.4 s straggler gained nothing, and `explode` made the dim scan costlier; warm re-run: **salted 2.8 s vs plain 4.4 s** (36 % faster) — the 5.9 s was cold start, salting did pay |
| 2026-09-30 | 4 | Exp 2 Run 1: orders_big ⋈ gold (filtered customers_big), AQE off | SortMergeJoin ("the optimizer doesn't know the sizes before launching") | SortMergeJoin, 2 Exchanges + 2 Sorts, 200 reduce tasks, 5.2 s; `explain("cost")`: Relation 147.0 MiB, Filter 147.0 MiB (actual gold: 5,000 rows, 0.42 MiB) | ✓ strategy; reason sharpened: the planner knows file bytes, but assumes a Filter keeps every row |
| 2026-09-30 | 4 | Exp 2 Run 2: same, AQE on | AQE sees gold is small and broadcasts it; the gold scan + filter stage (8 tasks) already ran and can't be removed; faster than Run 1 | initial SMJ → final BroadcastHashJoin, no Sort, local shuffle reader (16 tasks); fact still shuffle-wrote 1,239.7 MiB; 2.6 s | ✓ conversion and speed-up; missed that the fact shuffle is the sunk cost (both leaf stages are submitted together; AQE cannot un-run one). Static BHJ in Exp 1: 1.1 s |
| 2026-09-30 | 4 | Exp 2 Run 3: AQE on, filter keeps 3 customers | same plan as Run 2 (broadcast) | final SortMergeJoin; fact side filtered by the inferred `IN (1,2,3)` → 7,196 rows / 0.37 MiB shuffled; 0.8 s | ✗ — AQE does not convert when < 20 % of the build side's shuffle partitions are non-empty (3 of 200) |
| 2026-09-29 | 4 | Exp 3C: same range join with `F.broadcast(bands)` | "still the loop join, probably not CartesianProduct, since all the executors have the data"; BroadcastExchange yes; tasks and input records fewer than 64 / 16 M (no number) | `BroadcastNestedLoopJoin Inner BuildRight`; 8 tasks, 2,000,000 input records; 2.3 s | ✓ — broadcast removes re-reading, not the N × M comparisons |
| 2026-09-29 | 4 | Exp 1A: orders_big ⋈ customers, no hints | broadcast; exchange on the dim side; hash join building on dim; (jobs not stated) | `BroadcastHashJoin Inner BuildRight`, `BroadcastExchange` on customers, no shuffle; warm 1.1 s | ✓ |
| 2026-09-29 | 4 | Exp 1B: `dim.hint("merge")` | SortMergeJoin; both sides exchanged and sorted; shuffle write ≈ 1.1 GB (fact) + 3 KB (dim); slower than A | `SortMergeJoin`, Exchange on both sides (fact 1,239.7 MiB, dim 149.4 KiB), Sort both sides; warm 3.7 s | ✓ except dim shuffle size: row-format lz4 shuffle ≈ 50× the dictionary-encoded Parquet (3 KB) — on-disk size understates working size |
| 2026-09-29 | 4 | Exp 1C: `dim.hint("shuffle_hash")` | same exchanges/shuffle as B, no sorts implied; dim is the build side; slower than A, faster than B | `ShuffledHashJoin Inner BuildRight`, same shuffles, no Sort; warm 2.9 s | ✓ — A→C +1.8 s = fact shuffle; C→B +0.8 s = sorting 24 M rows |
| 2026-09-17 | 1 | Exp 2: join strategy / extra shuffle | broadcast of the small table; no shuffle for the join | SQL tab: `BroadcastHashJoin` with `BroadcastExchange` on customers (1 task, 10,000 rows, no shuffle write); the app's only shuffle is the aggregation's 1.4 MB | ✓ |

## Drill log

| Date | Question | Competency | Cold? | Correct? | Concise? | Follow-up |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-09-17 | Is `df.groupBy("k").count()` an action? What is its result? | M1 classify calls | yes | no ("an integer; a job ran") | n/a (multiple choice) | Re-taught: `GroupedData.count()` vs `DataFrame.count()`, classify by return type not name. Re-drill cold in the next session and in M9 |
| 2026-09-20 | Does `events.groupBy("user_id").count()` followed by a print prove the aggregation ran? | M1 classify calls | yes | yes ("counts is a DataFrame; nothing has run yet") | n/a (multiple choice) | Repaired cold; ask once more, free-form, in M9 |
| 2026-09-20 | What is a transformation? What is an action? | M1 classify calls | no | yes | no (wordy) | Lead with the return-type rule |
| 2026-09-20 | Why is Spark lazy? | M1 lazy evaluation | no | yes (gist) | yes, but vague | Say the cause: optimizer sees the whole plan (pushdown, pruning, fusion, join choice) |
| 2026-09-20 | Does `groupBy()` execute? Is `groupBy("k").count()` an action? | M1 classify calls | no | yes | yes | — |
| 2026-09-20 | What starts a Spark job? | M1 lazy evaluation | no | yes | yes | Optionally mention definition-time jobs (schema inference) |
| 2026-09-20 | Narrow vs wide? | M1 narrow / wide | no | yes (by symptom) | yes | Give the cause: one input partition vs many |
| 2026-09-20 | Why can a wide transformation create another stage? | M1 narrow / wide | no | yes | yes | Add the barrier: next partitions exist only after all upstream tasks finish |
| 2026-09-20 | Can one action produce more than one job? | M1 lazy evaluation | no | yes | yes | Rephrase "driver is used" as "broadcast collect job"; add AQE query stages, incremental show/take, sort sampling |
| 2026-09-21 | Is Spark SQL faster or slower than the DataFrame API? | M2 SQL vs DataFrame | no | yes | yes | Add "same logical plan → same Catalyst pipeline; only query shape matters" |
| 2026-09-21 | Why avoid Python UDFs? What instead? | M2 UDFs | no | yes (half) | yes | Name the three symptoms (no pushdown, breaks codegen, serialization) and built-in functions as the first replacement |
| 2026-09-21 | What do the `explain` modes show? | M2 explain | no | no (only simple/formatted; AQE caveat right) | — | Learn the five modes: simple, extended, formatted, codegen, cost |
| 2026-09-28 | What causes a shuffle? Shuffle read / write? | M3 shuffle in plans | no | partly (read/write ✓; cause stated as "data written to disk / partition count changes") | yes | Cause = an operator needs a distribution the current partitioning doesn't provide (groupBy, join, window, distinct, orderBy, repartition); coalesce changes the count without a shuffle |
| 2026-09-28 | `repartition()` vs `coalesce()`? | M3 Exp 2 | no | yes (thin) | yes | Add: shuffle + new stage + keeps upstream parallelism + can increase, vs narrow + decrease only + collapses the upstream stage (coalesce(1) trap) |
| 2026-09-28 | What does `spark.sql.shuffle.partitions` control; does AQE change it? | M3 shuffle partitions | no | yes | yes | Say "shuffles the planner inserts (joins, aggs, windows), not scans"; AQE merges, never splits (except skew joins) |
| 2026-09-28 | Spark partition = Hive / Iceberg partition? | M3 four kinds | no | yes | yes | Add the storage side: an Iceberg partition decides which files; its files become however many splits |
| 2026-09-28 | Tasks for reading 10 GB of Parquet? | M3 input partitions | no | yes ("~79–80, 128 MB each") | yes | Add "depends on layout: small files are bin-packed; big files split at 128 MB" |
| 2026-09-30 | `BroadcastHashJoin` vs `SortMergeJoin`? | M4 join strategy | no | yes | yes | Hash relation is built once on the driver, not per executor; add when each is chosen (10 MB threshold / default for large sides) |
| 2026-09-30 | When `ShuffledHashJoin` instead of `SortMergeJoin`? | M4 SHJ | no | yes | yes | Add AQE runtime conversion (opt-in) and the risk: build side can't spill |
| 2026-09-30 | When not to broadcast? Is a hint guaranteed? | M4 join strategy | no | half ("both small → sort-merge faster" wrong; hint question unanswered) | yes | Driver/executor memory, 8 GB cap, timeout, small-on-disk-large-in-memory, outer-join side; hint is dropped if the join type can't support it |
| 2026-09-30 | What is Catalyst? DataFrame → executed code? | M4 Catalyst | no | gist yes; error: listed `explain` as an action | no (mixed in laziness) | Give the pipeline in one line; `explain` runs nothing |
| 2026-09-30 | What is AQE; what can it change at runtime? | M4 AQE | no | yes | yes | Name the three: coalesce, join switch, skew split |
| 2026-09-30 | Why would Spark pick a bad join strategy? | M4 join strategy | no | yes (thin: "no statistics") | yes | Mechanism: sizeInBytes from file bytes, filter keeps everything, unknown size never broadcast, first match |
| 2026-09-30 | What is `BroadcastNestedLoopJoin`; why dangerous? | M4 BNLJ | no | mostly (confused task count with CartesianProduct) | yes | BNLJ keeps the streamed side's partitions; last-resort strategy even for two large sides |
| 2026-10-01 | What is data skew? How does it appear in the Spark UI? | M5 why skew occurs | no | yes | yes | Add the cause (hot key + hash partitioning) and "max ≫ median in shuffle read records / duration" |
| 2026-10-01 | What is salting, and why does it work? | M5 salting | no | yes (vague: "additional logic") | yes | State the mechanism: artificial sub-key 0..N−1, other side replicated N× |
| 2026-10-01 | Which side do you salt; what happens to the other side? | M5 which side | no | yes (incl. outer-join rule) | yes | Say "skewed side", not "big side" |
| 2026-10-01 | Disadvantages of salting; when to avoid it? | M5 drawbacks | no | yes on drawbacks; "when to avoid" not answered | yes | Avoid when broadcast / AQE skew join / pre-aggregation solves it; add extra shuffle column, N tuning, `(key, salt)` partitioning, no FULL OUTER |
| 2026-10-01 | Does speculative execution help with skew? | M5 why skew occurs | no | yes | yes | It launches a second copy rather than restarting; helps only slow nodes |
| 2026-09-30 | Transformation vs action; `groupBy("k").count()`? | M1 classify calls | yes | yes | yes | `I` awarded |
| 2026-09-30 | Why is Spark lazy? | M1 lazy evaluation | yes | yes | yes | `I` awarded |
| 2026-09-30 | Narrow vs wide; why a wide transformation creates a stage? | M1 narrow / wide | yes | yes (narrow described by symptom) | yes | `I` awarded; sharpen narrow = one input partition per output partition |
| 2026-09-30 | Four kinds of partition and where each number comes from | M3 four kinds | yes | half (execution + Iceberg; missed input and shuffle partitions) | yes | Stays `E`; re-drill in M9 |
| 2026-09-30 | Shuffles in `read → filter → groupBy(a) → join large on b → write`, and why | M3 shuffles in plans | yes | no (only the aggregation's Exchange; missed both join-side Exchanges on b) | — | Rule: each key-grouping operator needs its key's partitioning; count key changes per side. Stays `E`; re-drill in M9 |

## Knowledge edges

Recorded from each probe phase: what is solid (floor) and where understanding runs out (ceiling).
Strands still unbracketed are marked `open`.

| Date | Strand | Solid | Breaks at |
| --- | --- | --- | --- |
| 2026-09-16 | M1 driver / executor roles | executor slot model: cores = concurrent tasks (Q3 ✓) | driver's place in the data path: `collect()` result location → "I don't know" (Q1) |
| 2026-09-16 | M1 unit of work | slots per executor | task = one partition of one stage on one core; answered "one operator per executor" (Q2 ✗) |
| 2026-09-16 | M1 laziness | `cache()` lazy (Q4 ✓); `spark.sql` SELECT lazy vs CTAS eager (Q5 ✓) | `open` — deliberately not probed further; Experiments 1 and 3 sit on this edge |
| 2026-09-16 | M1/M3 shuffles | knows `groupBy` on a key needs a shuffle | exchange elision when the child is already hash-partitioned on the key: predicted 2 shuffles for groupBy→groupBy on the same key (Q6 ✗, actual 1) — closed 2026-09-20 by the Exp 2 Variant |
| 2026-09-20 | M2 reading `explain` | algorithms (`BroadcastHashJoin`) live in the Physical Plan (Q2 ✓) | the Analyzed vs Optimized logical plan split: chose Analyzed for "after Catalyst rewrites" (Q1 ✗) |
| 2026-09-20 | M2 where PySpark code executes | — (no floor found at this level) | systematic: thinks PySpark built-ins run in Python workers (Q4 ✗) and Python UDFs run on the driver (Q3 ✗); the "thin client to the JVM" model is missing |
| 2026-09-20 | M2 SQL layer | `spark.sql("SELECT …")` is lazy (M1 Q5 ✓) | thinks `createOrReplaceTempView` materializes the filter (Q5 ✗); a temp view is a name for a plan |
| 2026-09-21 | M3 input partitions | 80 × 128 MB Parquet files → 80 tasks (Q2 ✓); one `.csv.gz` → 1 task (Q3 ✓) | conflates Iceberg table partitions with Spark partitions: answered 365 tasks for a one-day filter on a day-partitioned table (Q1 ✗) |
| 2026-09-21 | M3 shuffle partitions | hash routing: customer 42 → `hash(42) mod 200` from every mapper (Q4 ✓) | scope of `spark.sql.shuffle.partitions`: thinks it sizes every stage (Q5 ✗); it sizes only post-Exchange stages |
| 2026-09-29 | M4 join algorithms | broadcast avoids shuffling the big side (M1 Exp 2 ✓) | Trino hash-join model: thinks a shuffled hash join can spill a too-large build side, sort-merge can't (Q1 ✗) |
| 2026-09-29 | M4 size estimates / threshold | knows small tables are broadcast automatically (M1) | thinks the estimate uses footer row counts × width (Q2 ✗; it is file bytes on disk); threshold recalled as 100 MB = Trino's default (Q3 ✗; Spark 10 MB) |
| 2026-09-29 | M4 broadcast eligibility | LEFT OUTER: only the right side can be broadcast (Q4 ✓) | `open` — hint semantics not probed (recruiter question, drilled at the end) |
| 2026-09-30 | M5 skew mechanism | knows a hot key makes one task slow | attributes it to the join algorithm ("sort-merge processes keys one at a time") rather than to hash partitioning (Q1 ✗) |
| 2026-09-30 | M5 aggregation vs join under skew | partial aggregation known from M3 Exp 1 | not applied to skew: expects the hot key's reduce task to receive 50 M rows for `groupBy().count()` (Q2 ✗; ~16 partial rows) |
| 2026-09-30 | M5 salting | the other side must be replicated once per salt (Q3 ✓) | `open` — implementation details (deterministic salt, outer joins, drawbacks) not probed |
| 2026-09-30 | M5 speculative execution | — | "I don't know" what speculation does to a skewed task (Q4) — taught; drill answer correct 2026-10-01 |
| 2026-10-01 | M6 spill metrics | knows spill = data that did not fit (M3, M5) | reads Spill (memory) / Spill (disk) as "stayed in RAM" vs "went to disk" (Q1 ✗); they are the same spilled data, deserialized size vs serialized size |
| 2026-10-01 | M6 UI navigation | Jobs / Stages / SQL tabs read fluently (M3–M5); finished apps → History Server (Q2 ✓) | Executors tab: "I don't know" where per-executor GC time is (Q3) |

## Open questions

