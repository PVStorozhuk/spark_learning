---
name: visualize
description: "Add a correct, minimal visual to a lesson — a diagram or a precisely laid-out picture — that renders inline in the Obsidian session log. Use when an idea is genuinely clearer as a picture: a dependency graph, system/flow, sequence, state machine, tree, comparison, or a spatial/quantitative layout (task-duration bars, partition sizes, a number line). Outsources authoring+rendering to a maker subagent that verifies the image by looking at it, then you embed the returned file."
---

# Visualize

> Ported from github.com/amosblomqvist/learn (commit `7cfd894`) for Claude Code: subagent dispatch, render tooling, and log paths adapted.
> Use this skill (not the desktop app's `mcp__visualize__*` widget tools) for lesson diagrams.

A picture earns its place only when it shows something words can't — shape, structure, direction, relationship, geometry. This skill produces ONE such picture, guarantees it is **correct** (the maker renders it and looks at it before returning), and drops it into the lesson so it renders inline in the Obsidian session log (`notes/sessions/`).

You are the **creative director**. You decide the exact idea and distill it to its fewest carrying elements. A **maker subagent** does the authoring, rendering, visual verification, and saving, then returns a filename. You embed that filename in your reply.

## When to visualize (and when not to)

This teaching system builds a **dependency graph in the learner's head** — axioms at the root, derived facts hanging off them. A visual is powerful exactly when it makes that structure (or a geometry) visible. Reach for one when:

- The idea is a **structure or relationship**: dependencies, a system with parts and arrows, a flow/pipeline, a sequence of exchanges, a state machine, a tree/hierarchy, a comparison, a containment (what's inside vs outside).
- The idea is **spatial or geometric**: coordinate geometry, a number line, vectors, a function's shape, a physical arrangement.

Do NOT visualize when prose or a single equation already carries it. A decorative diagram that just restates the sentence next to it adds noise and a chance to be wrong. When in doubt, don't — a missing visual is cheaper than a false one.

## Choose the maker

Two maker subagents, defined in `.claude/agents/`:

- **`mermaid-maker`** — structural/relational visuals: dependency graphs, flowcharts, sequence/state/ER/class diagrams, trees, mindmaps, timelines. This is the default and fits the dependency-graph pedagogy directly.
- **`svg-maker`** — spatial/geometric visuals Mermaid can't lay out: exact coordinates, geometry figures, number lines, vectors, plots, custom shapes.

Rule of thumb: if it's *nodes-and-edges / relationships*, use mermaid-maker. If it's *positions-and-shapes / geometry*, use svg-maker.

## Brief the maker well: one idea, fewest elements

The most common failure is **cramming** — every extra label makes the picture harder to read AND harder to lay out correctly. Before briefing, prune to the fewest elements that carry the idea, and for each ask: *"if I delete this, is the idea still clear?"* If yes, delete it.

Give the maker the concept AND the concrete elements you want — not a vague topic, and not a long checklist.

- BAD: "make a diagram about how TCP works"
- GOOD: "graph TD: a node 'packet' at the top; arrows down to 'ordering' and 'retransmit on loss'; both arrows down into 'reliable stream'. No title. Show that reliability is built FROM packets, not alongside them."

Keep the idea intact but trust the maker to compose; if your brief lists more than ~5–7 elements, cut it first.

## Invoke

Dispatch the maker as a subagent (Agent tool, `subagent_type` set to the maker's name), with your brief as its whole task. It sees none of this conversation, so the brief must stand alone. Makers run in the background: dispatch the maker *before* you start the node's exposition, keep teaching, and embed the picture when its report arrives. Don't ask that node's check question until the picture is in:

```
Agent(subagent_type="mermaid-maker", prompt="<your minimal, concrete brief>")
```
```
Agent(subagent_type="svg-maker", prompt="<your minimal, concrete brief>")
```

The maker renders with `.claude/skills/visualize/render.py` — it authors the source, renders it to a PNG, **looks at the PNG and iterates until it is correct and clean**, publishes it into the vault with a unique filename, and returns:

```
RESULT:
filename: viz-<slug>-<timestamp>.png
path: <vault>/viz/viz-<slug>-<timestamp>.png
```

If it returns `RESULT: NONE`, it couldn't make a correct picture of the brief — simplify or rethink, or decide the visual isn't worth it. Never hand-author or fake a diagram yourself; correctness depends on the maker's render-and-inspect loop.

## Embed it in the lesson

Put the embed directly in your teaching reply, using Obsidian's wikilink embed with the returned **filename** (not the full path) and a display width:

```
![[viz-<slug>-<timestamp>.png|500]]
```

That's all. The session log hook mirrors your reply text into today's log file, and Obsidian resolves the embed by filename anywhere in the vault (the maker publishes into the `viz/` folder next to the session log: `notes/viz/` by default, with `notes/` as the vault) — so it renders inline in the lesson automatically. The Claude Code window does not render the embed, so also give the PNG's `path` in the same reply: the learner can open it from there. Width `|500` is a good default; use larger for dense diagrams. Introduce the visual in a sentence, then let it carry the idea — don't narrate every element back in prose.

## Why this is reliable

- The maker never returns a picture it hasn't **looked at**, so "renders fine but says something false" is caught before it reaches the learner.
- PNG embed means **what the maker verified is pixel-identical to what the learner sees** — no re-render drift.
- Unique filenames keep Obsidian's by-filename embed resolution unambiguous.

> The makers render through `.claude/skills/visualize/render.py` (Mermaid via `npx @mermaid-js/mermaid-cli`, whose first run downloads a headless browser; SVG via headless Edge/Chrome, or `rsvg-convert` when installed). You don't render anything yourself — you only brief the maker and embed the filename it returns.
