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
| 1 | Execution model + actions / transformations | critical | 2.5 | | todo |
| 2 | DataFrames + Spark SQL essentials | medium | 2.0 | | todo |
| 3 | Partitions and shuffle | high | 3.0 | | todo |
| 4 | Joins + Catalyst + AQE | critical | 4.0 | | todo |
| 5 | Data skew + salting | critical | 3.0 | | todo |
| 6 | Spark UI + troubleshooting | critical | 3.5 | | todo |
| 7 | Memory + performance essentials | medium | 2.0 | | todo |
| 8 | Spark + Iceberg | medium | 2.5 | | todo |
| 9 | Production basics + recruiter review | medium | 1.5 | | todo |
| C | Mini-capstone | high | 2.0 | | todo |
| | **Total** | | **26.0** | | |

`Spent (h)` is the sum of that module's rows in the session log.

## Current module plan

The approved plan for the module in progress (overwritten when a new module starts). Node labels are phrased
as open questions, not answers.

- Module: —
- Approved on: —
- Nodes (✓ done, → next): —

## Competency evidence

### 1. Execution model + actions / transformations

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Classify every call in a pipeline as transformation or action, before running it | I | - | |
| Explain lazy evaluation and why Spark is lazy | I | - | |
| Show which calls start a job and which do not (Spark UI Jobs tab) | D | - | |
| Experiment 3: predict the job count for a CSV read with and without a schema, before any action | D | - | |
| Predict jobs, stages, and tasks for a small pipeline and check against the Spark UI | D | - | |
| Explain narrow vs wide, and why a wide transformation can create a stage boundary | I | - | |

### 2. DataFrames + Spark SQL essentials

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Compare physical plans of equivalent `spark.sql()` and DataFrame API code | D | - | |
| Read the sections of `explain("formatted")` | E | - | |
| Explain why native expressions beat unnecessary Python UDFs | E | - | |
| *Optional:* compare plan and runtime of a native expression vs a Python UDF | D | - | |

### 3. Partitions and shuffle

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Distinguish input, execution, shuffle, and Iceberg table partitions | I | - | |
| Experiment 1: predict shuffle and `Exchange` placement for `groupBy().count()` | D | - | |
| Experiment 2: `repartition()` vs `coalesce()`, and when each shuffles | D | - | |
| Experiment 3: inappropriate vs better `spark.sql.shuffle.partitions`, with task metrics | D | - | |
| Point at every shuffle in a physical plan and explain why it exists | I | - | |

### 4. Joins + Catalyst + AQE

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Name Catalyst phases and find them in `explain` output | E | - | |
| Fact + dimension under different strategies: predict, run, compare | D | - | |
| Explain why Spark picked a join strategy, given plan and table sizes, and propose alternatives | I | - | |
| Explain when `ShuffledHashJoin` is used instead of `SortMergeJoin`, and its risks | I | - | |
| Show how a bad size estimate leads to an inefficient plan, and what AQE does about it | D | - | |
| Compare AQE initial vs final plan and explain what changed | D | - | |
| Recognize `BroadcastNestedLoopJoin` and explain why it can be dangerous | E | - | |

### 5. Data skew + salting

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Explain why skew occurs | I | - | |
| Recognize skew from task metrics in the Spark UI | D | - | |
| Implement salting on a skewed join | D | - | |
| Measure before/after: task durations, partition sizes, runtime, shuffle behavior | D | - | |
| Compare salting with the other solutions on the same data | D | - | |
| Explain which side is salted and what happens to the other side | I | - | |
| Explain drawbacks and when not to salt | I | - | |

### 6. Spark UI + troubleshooting

| Competency | Target | Level | Evidence |
| --- | --- | --- | --- |
| Find each key metric in Jobs, Stages, Tasks, Executors, SQL, and the History Server | D | - | |
| Diagnose at least three scenarios on actual broken lab jobs: evidence → hypothesis → change → before/after | D | - | |
| Write my own troubleshooting workflow and apply it to all four scenarios | D | - | |
| Scenario 1: one task far slower than 499 others | I | - | |
| Scenario 2: 20-minute job now takes 2 hours, structured investigation | I | - | |
| Scenario 3: shuffle partitions 200 → 20 made it slower | I | - | |
| Scenario 4: heavy spill, is more executor memory the answer? | I | - | |

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

## Prediction log

One row per prediction, written **before** the run; Actual and the explanation are filled in right after it.
A before/after comparison uses two rows.

| Date | Module | Experiment | Prediction | Actual | Why they differ |
| --- | --- | --- | --- | --- | --- |

## Drill log

| Date | Question | Competency | Cold? | Correct? | Concise? | Follow-up |
| --- | --- | --- | --- | --- | --- | --- |

## Knowledge edges

Recorded from each probe phase: what is solid (floor) and where understanding runs out (ceiling).
Strands still unbracketed are marked `open`.

| Date | Strand | Solid | Breaks at |
| --- | --- | --- | --- |

## Open questions

