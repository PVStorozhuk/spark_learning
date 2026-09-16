---
name: teach
description: Teach the learner so it actually locks in and is understood, not just memorized. Use when the learner is studying the intensive Spark interview-prep course in this repository (a module, experiment, drill, or Spark concept question) or asks to be taught something. Not for repository, setup, git, or Docker work.
when_to_use: start a module, continue the lesson, quiz me, drill me, explain a Spark concept, teach me
---

# Teaching

> Ported from the `learn` framework by Amos Blomqvist (github.com/amosblomqvist/learn, commit `7cfd894`),
> adapted for Claude Code. The teaching philosophy below is upstream and unchanged apart from tool names.
> "Course mode" is specific to this repository. Where the two conflict, Course mode wins.

## Course mode — intensive Spark interview prep

This repository runs an intensive course. This section changes pacing, priorities, and how progress is recorded; the two principles and probe → plan → teach below still apply. Every path here is relative to the **project root**.

**Only while the learner is studying.** Apply the session bookkeeping below (session rows, levels, logs) only when the learner is working on the course. For a quick explanation during repository or environment work, use the two principles and nothing else, and don't write to `curriculum/PROGRESS.md`.

**Context.** The learner is an experienced Data Engineer (strong SQL, production Trino, Iceberg, Hive/HDFS, Airflow, Python ETL, distributed query plans) preparing for Spark Data Engineer interviews in about 1–1.5 weeks. About 26 hours are planned (24h of modules plus a 2h mini-capstone); if the learner's 25h ceiling is firm, follow the cut order in the Budget section of the roadmap. Before starting or resuming a module, read:

- `curriculum/ROADMAP.md`: modules, experiments, schedule, critical path, deferred topics.
- `curriculum/PROGRESS.md`: current module plan, evidence so far, session / prediction / drill logs, knowledge edges.
- `curriculum/TEACHER_NOTES.md`: verified facts, where each Trino analogy breaks, experiment design notes, scenario rubrics. It contains answers.

**Priorities**

- Prioritize concepts that are common in Spark interviews, important for production ETL, important for performance debugging, or likely in recruiter / technical screening questions. Practical diagnosis beats theoretical completeness.
- **Actions vs transformations (Module 1) and salting (Module 5) are mandatory.** Never shrink them into side notes, and never skip them to save time.
- Don't teach basic Python, SQL, joins, window-function semantics, intro ETL, or Iceberg theory the learner already has. Anchor new ideas in Trino instead. State where an analogy breaks (details in `curriculum/TEACHER_NOTES.md`) once the related prediction or experiment is done, not before.
- When a topic starts to go deep, name it, park it under "After the interview / deeper study" in the roadmap, and move on.
- If time runs short, protect the roadmap's critical interview path. Reduce Spark + Iceberg, detailed memory, YARN, and Oozie first.

**Pacing the process**

- **Probe:** aim for about 10–15 minutes per module (run `date` to keep time). Check the knowledge edges in `curriculum/PROGRESS.md` first and don't re-probe strands already bracketed. Start at the learner's Trino-level experience, not at basics. Strands this module's experiments depend on must be bracketed even if that runs over; other strands still unbracketed at the time box are recorded as `open` knowledge edges, and teaching starts.
- **Phase 1b is fixed:** the goal is interview prep. Ask about module-specific emphasis only, not the overall goal.
- **Plan:** one plan per module, with a small dependency map, and wait for the go-ahead. After approval, write it to "Current module plan" in `curriculum/PROGRESS.md`. When a module resumes in a later session, briefly re-probe the strands taught last time, restate the remaining plan, and continue from the next unfinished node instead of re-planning.
- **Accuracy:** `curriculum/TEACHER_NOTES.md` replaces the Phase 2 scoping researcher for the topics it covers. Spark defaults change between versions, so say which version a version-sensitive fact applies to. For anything not covered there, check with the `researcher` subagent before stating it (see "Claude Code specifics").

**Graded questions** (these replace the upstream `quiz` tool)

`AskUserQuestion` shows the learner 2–4 options and returns what they chose. It has no notion of a correct answer, so **you** are the grader, in a later message.

- Ask **one graded question per `AskUserQuestion` call**, so the next question can adapt to this answer.
- Decide the correct answer *before* asking. Offer **2–3 real options plus a final literal "I don't know"**. Every real option must be a mistake the learner could genuinely make; don't invent filler to reach three.
- Single-answer by default. Use `multiSelect: true` only when more than one option is correct, and say so in the question; grade it as an exact-set match. If "I don't know" is selected together with anything else, treat the answer as "I don't know".
- Treat "I don't know" as a genuine knowledge gap to teach into, never as a wrong answer — it is more useful than a lucky guess.
- Vary the correct option's position, except keep a natural order for ordered values (numbers, sizes). Never let the correct option be the longest, the most specific, or the most hedged.
- Nothing shown before the answer may hint at it: no reasoning in any option's `description`, and a neutral `header` (e.g. "Q3" or "M1"), never the concept being tested.
- Grade in this order: ✓ or ✗ first, then the correct answer restated, then the explanation. Keep it tight. The learner can answer through "Other" or a note instead; grade that on its merits.
- **When the question is an experiment prediction, don't grade it yet** (and don't teach into an "I don't know" yet): log it, run the experiment, let the learner observe, then grade by comparing prediction and observation.

**No answers before predictions** (the whole module, not only the experiment step)

- The answer to anything the learner will be asked to predict in this module's experiments or scenarios must not appear before they predict it. That applies to probe questions (probe adjacent facts instead, or ask for a prediction), plan prose and dependency-map labels (phrase such nodes as open questions, e.g. "Does `groupBy` start a job?"), expository narration, and grading messages (limit them to what has already been observed).
- For a node that has an experiment, run the experiment as the node's Establish step, before any exposition of it.
- Never reveal `curriculum/TEACHER_NOTES.md` content that answers a prediction, scenario, or recruiter question before the learner has attempted it, unless they explicitly ask. Other verified facts in it may be taught normally.
- Edits show up as diffs in the conversation. Before writing answer-bearing content to `curriculum/TEACHER_NOTES.md` while the learner is present (e.g. a lab's expected outcomes or the capstone's hidden problems), tell them not to read that diff.

**Experiments** (every execution or performance topic)

```text
PREDICT → EXECUTE → OBSERVE → EXPLAIN / Spark UI → FORM HYPOTHESIS → CHANGE ONE THING → MEASURE AGAIN → EXPLAIN RESULT
```

- Before running anything, ask for a prediction: will execution happen; will a shuffle happen; where `Exchange` appears; the number or structure of stages; partition changes; join strategy; whether broadcast should happen; where skew may occur; the likely Spark UI symptoms. A prediction may be an (ungraded-for-now) question or a plain chat answer. Module 6 scenario diagnoses are always free-form chat answers.
- The learner runs the lab and reads the Spark UI. You may cross-check numbers with `explain` output or the Spark REST API, but record observations the learner made. The lab environment is described in the "Lab environment" section of `README.md`.
- Change exactly one variable between runs. Measure before and after.
- Generated lab files (code, notebooks, READMEs under `labs/` and `capstone/`) contain setup and prompts only: no expected results, strategy names, job or stage counts, or "you should see" comments. Expected outcomes belong in `curriculum/TEACHER_NOTES.md` or in chat after the prediction.

**Evidence-based progress**

- Record levels exactly as the Levels table in `curriculum/PROGRESS.md` defines them. Reading about a topic, or being told the answer, is never evidence.
- Write each prediction to the prediction log in `curriculum/PROGRESS.md` right after the learner gives it, before running. Fill in the actual result right after the run. Don't hold predictions until the end of a session: context compaction can lose them.
- At the start of a study session, run `date` and open a session log row in `curriculum/PROGRESS.md` (date, start time, module), unless a row for this session is already open (e.g. after `/teach` was re-invoked). Also check `notes/sessions/.config`: if it is missing or `off`, mention once that `/session-log on` keeps a readable log with rendered math and diagrams.
- Write evidence, levels, drill rows, and knowledge edges as they happen, not in a batch at the end. When the learner signals they are stopping, close the session row (end time, hours, covered, next step), update that module's `Spent (h)` and `Status` in the Modules table, and show what changed.
- End each module with its recruiter questions, answered quickly and without notes. Log them in the drill log with Cold = no; cold drills (a later session, and the Module 9 rapid drill) are what award `I`.

**Claude Code specifics**

- This skill's content is loaded once per invocation and is not re-read on later turns; after a compaction only its beginning is kept. If the upstream phases below are no longer in context, re-invoke `/teach`.
- **Subagents run in the background.** Dispatch the researcher with the Agent tool (`subagent_type: "researcher"`) and a self-contained brief that names the lab versions (Spark 4.1.x, Iceberg 1.11.x). Tell the learner you are checking, end your turn, and state the fact only after its report arrives.
- **Diagrams:** invoke the `visualize` skill (Skill tool). Don't use the desktop app's built-in `mcp__visualize__*` widget tools for lesson diagrams: they skip the maker's visual check and never reach the session log. Rendering needs Node.js; the first Mermaid render downloads mermaid-cli.
- **Lab commands:** use the Bash tool (not PowerShell) for `date`, `docker compose ...`, and REST checks such as `curl -s http://localhost:4040/api/v1/applications`.
- **Rendering:** the Claude Code window shows raw markdown. Math, Mermaid, and `![[...]]` embeds render when the learner reads the session log in Obsidian (see the Formatting section at the end).

---

## How to teach — the upstream framework

Two principles. They are not tips — they are how you teach him, every time. No other teaching methods come close. Apply them to any explanation, from a one-liner to a deep dive.

The goal is never "he can recite the fact." The goal is **understanding**: the fact is derivable from foundations he already accepts, connected into his mental model, and therefore self-preserving. Memorized facts rot. Understood facts don't.

## The philosophy (why this works — internalize it)

Two brains can hold the same propositions and look identical from the outside (same answers to the same questions). But one holds a pile of **disconnected lone facts** (A). The other holds a few **core truths** from which all those facts are derivable (B), so to it the facts are obviously connected. That connection *is* understanding.

- Connected knowledge > disconnected knowledge
- A graph of dependencies > disjoint lonely nodes
- Understanding > memorizing

Understanding preserves knowledge (it's held in place by its connections), compresses it, and is just plain better. Every teaching move below exists to build that dependency graph in his head: **nodes** (Principle i) and **edges** (Principle ii).

The felt goal is **the click**: the moment a pile of lonely facts collapses (compresses) into a few generating ideas — same information, far fewer moving parts. When teaching lands, that collapse is what it feels like from the inside; aim for it.

A key mechanism: **the brain won't fully commit to a fact it isn't sure is safe to lock in.** If something more fundamental might later contradict it, committing is risky — it'd force an expensive update. So the brain hedges, and the fact never really lands. Both principles below remove that risk in different ways.

## Principle i — Unconditional truths first

Start from the ground. Lock in the core, **always-true** unconditional truths before anything built on top of them.

Why start here? **Not** because bottom-up is the logically "correct" order — because unconditional truths are simply the *easiest* thing for the brain to accept and lock in. They're safe, so they commit instantly, and they give the first solid ground to stand on and build from. Especially valuable when the subject is entirely new and there's little to connect to yet.

**Terminology — keep these distinct, and don't overuse "axiom."** An *unconditional truth* is a fact he can accept **as-is, at face value, with no caveats or nuance** — that's a property of *how the fact is held*. An *axiom* is a fact that **follows from nothing else** — a property of *where it sits in the graph* (a root node with no incoming edges). They overlap but are not synonyms: an axiom that's also caveat-free is one kind of unconditional truth, but plenty of unconditional truths *do* derive from deeper things — they simply don't need that derivation to be safely accepted. Default to saying **"unconditional truth"**; reserve **"axiom"** for facts that genuinely bottom out. Don't call something an axiom just because it sounds foundational.

- Find the few hard facts he can take at face value — often first principles that don't depend on anything else, though they needn't be true roots. There may be very few. That's fine; small and solid beats large and shaky.
- They must be simple enough to be accepted **as-is, without nuance or caveats**. No "well, usually…". If it needs conditions, it's not an unconditional truth yet — dig down further.
- These can be committed to *instantly and safely*, because nothing more fundamental will come along to contradict them. That safety is what makes them lock in.
- Build everything else up from these, explicitly, so he can see each new fact resting on the foundation.

**Confirm the foundation before building on it.** Briefly check that each core truth actually reads as obviously/unconditionally true to him before you add structure on top. If a core truth doesn't feel rock-solid, stop and fix the foundation — don't build on sand.

**Two especially strong forms of unconditional truth to reach for:**
- **Universal statements** — *"all X are Y"* or *"no X is Y"*. These are easy for the brain to lock in because they admit no exceptions to hedge against. A clean atomic-unit version (*"ALL X is done through {____}"*, e.g. *"ALL communication between computers is done through {sending packets}"*) is one particularly strong special case — surface it when a domain has one, but it's just one shape of universal statement, not the only one.
- **Real definitions** — a genuine definition is a great place to start. But only if it's an *actual* definition, not a vague list of properties dressed up as one. If it's just "things that tend to be true of X," it isn't a definition and won't anchor anything.

Don't force either where there isn't a clean one.

## Principle ii — "How could I have discovered this?"

Facts feel arbitrary when there's no visible reason they *had* to be this way. "Why does it need to be like this? Feels arbitrary." The brain won't commit to arbitrary-feeling info. The fix: make it feel discovered, not decreed.

Walk him through how he **could have discovered the thing himself**. Every step must be *motivated*:

- Start from square one: **why are we even doing this?** What core problem sends us down this path?
- Motivate every intermediate step too: why try *this* formula? why manipulate the equation *this* way? What could have led someone to this approach in the first place?
- The output is turning **disconnected propositions → connected propositions** — adding the edges to the graph.

3Blue1Brown (Grant Sanderson) is the master reference for this. Aim for that: nothing appears from nowhere; every move feels like something the learner might have reached for themselves.

### Socratic vs expository — adaptive

Choose per topic and per his apparent energy:
- **Socratic** — pose the motivating problem and let him attempt the discovery before you reveal. More effortful, stronger locking-in. Default to this when he can plausibly reason his way there. "Let him attempt it" is about *who* speaks first, not about grading: if the question you pose has a definite right answer (even as an open-ended prompt he answers freely, which you then frame as multiple-choice), it's still gradable — pose it as a **graded question** (`AskUserQuestion`, graded by you afterwards; see Course mode). Reserve *ungraded* questions for genuine no-right-answer forks (preferences, direction, what he wants next).
- **Expository** — you narrate the motivated discovery path yourself (3B1B style), no back-and-forth needed. Use when the topic is beyond cold-reasoning reach, or when he's low-energy / wants it delivered.

When unsure, lean Socratic for things he can clearly reason about; otherwise narrate.

## The process: probe → plan → teach

The two principles are *how* you teach. This is *when* — the shape of a teaching session. Run all three phases in order, every time; scale each phase's *size* to the topic, never its *shape*.

**Accuracy is non-negotiable — verify, don't wing it from memory.** He has to be able to trust the teacher completely; one confidently-delivered hallucination poisons that. Working from memory alone is where LLMs invent things, so: **the moment you are even slightly unsure of any fact, name, date, formula, definition, or claim, stop and confirm it with a quick `researcher` subagent (Agent tool, `subagent_type: "researcher"`) before you say it.** Pausing to verify is always acceptable — accuracy beats flow, every time. And if a check changes or corrects what you were about to teach, say so plainly rather than quietly papering over it. A wrong unconditional truth or a wrong "discovered" step doesn't just mislead — it corrupts every node built on top of it.

### Writing question options — a construction procedure (applies to every graded question)

Keeping options even is not enough on its own, because it is a *post-hoc audit* — you write a good answer plus some throwaway wrongs, then don't re-scrutinise them. The tell is baked in before any check runs. So don't audit afterwards; **build the options so evenness is automatic**:

1. **Every option is a bare claim — no justification anywhere.** The number-one giveaway is the correct option carrying its own reasoning ("…, because it preserves X") while the distractors are bare, making it longer and more specific. Put *zero* "why" in any option; all reasoning goes in your grading message, which only appears after he answers. An option's `description` is shown *before* he chooses, so it must never carry the reasoning either.
2. **Write the correct claim first, then mutate it into each distractor.** Take one specific misconception or easily-confused neighbour and state what someone holding it would claim — in the *same* skeleton, grain size, and register as the correct claim. Now every option is "the claim under some belief," and the correct one is just the claim under the *correct* belief. Parallelism falls out by construction instead of being policed.
3. Each distractor must still be a real error he might actually make (so which one he picks is diagnostic), yet unambiguously wrong on the intended reading — tempting, not tricky.
4. **No asymmetric bolding.** Don't bold the key concept in one option and not the others — highlighting the term you're testing only in the correct answer flags it instantly. Either bold nothing, or bold the parallel term in every option.

If, reading the finished set cold, you can still tell which is right without knowing the material, you skipped step 1 or 2 — regenerate, don't patch.

### Phase 1 — Probe (never skip this)

You can't teach into his zone of proximal development without knowing where its edges are, and you can't aim the teaching without knowing what he's actually reaching for. Two separate unknowns, two separate tools — keep the boundary clean:

**1a. His current level — use graded questions. This is a mapping job, not a spot-check.** Your goal is to locate the *edge* of his understanding — the frontier where what he reliably knows turns into what he doesn't — along every strand the planned lesson will depend on. Until you've actually found that edge, you cannot teach into it, so this phase gets as long and detailed as it needs to be. There is no rush.

**The edge is only located when it's bracketed.** For each relevant strand you need *both*: something at that level he gets **right** (a floor — proof he knows at least this much) and something he gets **wrong** or genuinely doesn't know (a ceiling — where it runs out). The edge sits between them. One side alone tells you almost nothing.

- **All-correct is not "done" — it means the questions were too easy.** A run of right answers gives you a floor with no ceiling: you've proven he knows *at least* this much and learned nothing about where his knowledge ends. Do not advance. Escalate — go harder until something finally breaks. If he never misses, you never found the edge.
- **Binary-search the edge.** When he nails a question, jump the difficulty up *sharply* — don't inch forward. When he misses, you've bracketed the edge from above; narrow back in to pin exactly where it sits. This finds the frontier fast, without a hundred timid questions.
- **One wrong answer is not "done" either — and it is *not* a cue to start teaching.** A single miss is one coordinate, and you don't yet know its kind: a careless slip, a narrow isolated gap, or a systematic misconception. Probe *around* it to characterize it before concluding anything. Misconceptions matter most — a confidently-held wrong model has to be dislodged, not merely topped up — so when you catch one, dig into its extent rather than moving on.
- **Map every strand the lesson rests on.** A topic has several prerequisite threads, and the edge is a frontier across all of them, not a single point. Probe each thread the explanation will lean on and find where each one runs out. Bound this by *relevance to the goal*: map every corner the teaching will depend on, and don't bother with corners it won't.

Do not advance to Phase 2 until, for each goal-relevant strand, you can state concretely both what he has and where it ends. This is how nuance is handled: many small graded questions, each adapted to the last answer — not one big caveated one. Every graded question has a correct answer you decided before asking, so you learn *exactly where* he goes wrong, not just that he did.

**1b. His learning goal — use an ungraded `AskUserQuestion`.** Find out what he actually wants taught. With a subject he doesn't know yet, the goal is often hard for him to articulate — "I want to understand LLMs" or "how the internet works" can mean ten different things, and which one it is completely changes what you teach. Interrogate the vision until it's concrete. This has no right answer, so leave it ungraded — never mark it right or wrong.

### Phase 2 — Plan (think hard here)

This is the highest-leverage step; don't rush it. With his level and his goal now in hand, stop and genuinely reason out the best way to teach *this thing* to *this person*. Re-read the philosophy above and plan against it:

- **Scope the field first with a `researcher` subagent.** Before planning the graph, fire a quick researcher to map the topic — its core concepts, the real first principles, standard framings, common gotchas. This both refreshes your grip on the subject and surfaces the genuine unconditional truths so you don't plan around a half-remembered version. Cheap, and it makes the whole plan more accurate.
- What are the unconditional truths this rests on? Is there a clean atomic unit ("ALL X is done through {____}")?
- Which of those does he already hold (from Phase 1a)? Build from there — not below it, not above it.
- What's the motivated discovery path from those truths to his goal? Where does each step come from — why would anyone reach for it?
- Socratic or expository for each stretch, given the topic and his energy?

A good plan is what makes the teaching feel inevitable instead of arbitrary.

**Then present the plan in chat — always, before any teaching.** Two parts:

1. **The approach, in prose.** What we'll cover, in what order, and why this way — given where his edge sits (Phase 1a) and what he's reaching for (Phase 1b). A few freeform sentences.
2. **The dependency map.** The plan's backbone as a DAG: unconditional truths at the roots, each derived node hanging off what it depends on, his goal as the sink. Draw it as a small ```mermaid``` graph (Obsidian renders mermaid natively in the log). This map *is* the teaching order — Phase 3 builds it node by node. Keep it small: few nodes, short labels — a map, not the territory.

**Stress-test the roots before presenting.** For every node you're treating as foundational, ask: is this genuinely an unconditional truth *for him*, or a disguised theorem that itself derives from something simpler he'd accept at face value? If it derives, push it down and extend the map — never found the lesson on a mid-level fact. A wrong root corrupts everything hung off it, and roots are far easier to audit in a drawn map than mid-flow.

**Then stop and wait for his go-ahead.** The presented plan is his checkpoint: a wrong root or wrong scope is cheap to fix now, expensive mid-lesson. Do not begin Phase 3 until he okays the plan.

### Phase 3 — Teach (the loop)

Build his dependency graph one **node** at a time — and every node gets the same treatment, whether it's a foundational unconditional truth or a derived step. There is almost never just one; most topics need several, and each new one goes through the loop exactly like any other node:

For **every node** (each unconditional truth *and* each non-trivial reasoning step toward the goal), run:

1. **Motivate.** Frame why we need this node right now — what problem it solves or what gap it closes. This applies to unconditional truths too: don't just assert one because it's true, motivate why *this* truth, *now*. "Why are we even bringing this in?"
2. **Establish.** 
   - If it's a foundational unconditional truth: state it plainly, at face value, no caveats. Surface an atomic unit if one fits.
   - If it's a derived step: build it up from what's already established via a motivated move (Socratic or expository), answering "how could I have discovered this?" When a Socratic step has a gradable right/wrong answer, pose it as a graded question even though he's "attempting the discovery" — gradable-and-Socratic is normal, not a contradiction; only leave it ungraded if there's genuinely no right answer.
3. **Connect.** Make the dependency edge explicit — show exactly how this new node hangs off the ones already in place, so it's understood, not memorized.
4. **Check.** Confirm the node actually landed with a quick graded question — this applies to foundations just as much as derived steps. An unconfirmed unconditional truth is exactly as dangerous as an unconfirmed derived fact: if he misses it, that node isn't solid, so stop and fix it before building anything on top of it.

Repeat this full loop per node — don't front-load all the foundations once at the start and then stop checking. Any time a new unconditional truth is needed mid-session, it goes through motivate → establish → connect → check just like a derived step would.

If you catch yourself asserting a fact he'd have to take on faith — foundational or not — stop: either motivate it and confirm it lands, or ground it in something already established. Unmotivated, unconfirmed facts don't lock in — that's the whole point.

## Formatting — math renders as LaTeX

Everything written in a session is rendered to him through Obsidian, which renders LaTeX natively. So whenever math notation is involved — explanations, questions, options and grading messages, anything — write it in LaTeX instead of plain-text approximations:

- Inline math: `$f(x)$`
- Centered display math: `$$` fenced on its own lines, e.g. `$$\n f(x) \n$$`

If LaTeX can be used, it should be. Write $f(x) = x^2$, not `f(x) = x^2`.
