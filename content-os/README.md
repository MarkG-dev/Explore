# Content OS — Ideation Engine & Creative Lenses

The ideation core of the AI Content OS: **one conductor** that turns a brief into candidates by composing a *making-plan* — deciding which generative **lenses** to pull on, in what sequence — then judging the result. It is **not** a router that picks one engine per brief; it plans, sequences, composes, and gates.

> This README is the source of truth for the **current** architecture. It supersedes the "router picks one of three engines" framing in `docs/execution-engine.md`, which was the earlier model. The docs remain as reference for the rest of the OS (lineage schema, learning loop, pipeline).

```
brief + substrate
   │
   ▼  PLAN     choose lenses + sequence
   ▼  BUILD    run each lens as a discrete pass, handing off
   │             Alien     → novel frame / voice
   │             Alexander → structure / fit
   ▼  GATE     Rubin judgment — does it have life?
   ▼  EMIT     candidates tagged {gen_methods recipe, content_mode, making_plan, substrate_version}
   → QA filter → human approval (edit_diff + reject_tags) → rest of pipeline
```

The plan comes from the **brief**; the taste comes from the per-loop **substrate**. *Substrate × plan = candidates.*

## The architecture in one breath

- **Rubin is the conductor and the taste gate** — the ideation engine is Rubin-shaped (diagnose → diverge → build → judge). It is not a peer of the other two.
- **Alien and Alexander are the generative lenses** the conductor pulls on during the build stage. The kit is meant to grow.
- **Composition is by sequenced passes, never averaging.** Alien estranges → Alexander structures → Rubin judges, as discrete operations. One blended "be novel + structured + soulful at once" prompt collapses to mush — that's the failure this whole design avoids.

## Layout

```
content-os/
├── README.md                      ← you are here (current architecture)
├── docs/
│   ├── content-os-plan.md          consolidated system plan (learning loop, lineage schema, pipeline)
│   └── execution-engine.md         earlier spec (router-picks-one; superseded by this README)
└── skills/
    ├── ideation-engine/  SKILL.md           the conductor — plans, sequences, gates; logs the recipe
    ├── rubin/            SKILL.md            the conductor's process + taste gate (Rick Rubin)
    └── lenses/
        ├── alien/        SKILL.md + refs     novel frames — novelty via estrangement + worldbuilding + 13 dialects
        └── alexander/    SKILL.md + refs     structure for fit — decomposition + constructive diagrams (Christopher Alexander)
```

## The lenses

| Lens | The job | Built from |
|------|---------|------------|
| **Alien** | **Novel frames** — find the angle nobody else would; novelty that reveals, not noise | *Alien + Worldbuilding + Dialects* (13 tonal archetypes) |
| **Alexander** | **Structure for fit** — composed wholeness where form carries meaning (carousels, sequences, layouts) | Christopher Alexander, *Notes on the Synthesis of Form* |

**Alien** introduces an *interference pattern* (a novel frame) that stops the scroll. **Alexander** builds a *gravity of structure* (fit) that makes a piece whole. They are deliberate opposites and compose constantly; **Rubin** is the process that wields them and the taste that judges them.

## How a brief flows

1. **Plan.** The conductor reads `{intent, format, platform, pillar}` + the loop's substrate and composes a making-plan: which lenses, in what order, how they hand off.
2. **Build.** Each lens runs as a discrete pass with the substrate as taste context. Example plan: *Alexander builds the carousel spine → Alien generates a novel cover frame → fuse the cover back into the structure.*
3. **Gate.** Rubin's judgment domain checks the candidates have life before they leave the engine.
4. **Emit.** Candidates carry a **recipe** (`gen_methods: [alexander, alien]`), a soft `content_mode` descriptor, the `making_plan`, and the `substrate_version`. They flow to the QA filter → human approval (where `edit_diff` + `reject_tags` are captured) → the rest of the pipeline in `docs/content-os-plan.md`.
5. **Learn.** Performance + edit signal, partitioned by **recipe** and **brief-type**, tune the planner and the lenses over time.

## The learnable surface

Because every candidate records its recipe and brief-type, the loop learns *which tool-recipe wins for which brief-type in which loop* — a far richer signal than "which of three engines won." The planner is the first thing the feedback loop should tune; until then it runs heuristics, logging recipes from day one.

## Build status

| Component | Status |
|---|---|
| Ideation engine (conductor + planner + gate) | ✅ built — `skills/ideation-engine/` |
| Rubin (conductor backbone + taste gate) | ✅ wired in — `skills/rubin/` (substrate-aware per loop) |
| Alien lens (novel frames) | ✅ built — `skills/lenses/alien/` (frame-shift moves · worldbuilding · 13 dialects · gates) |
| Alexander lens (structure) | ✅ built — `skills/lenses/alexander/` (fit & misfit · decomposition · constructive diagrams · realization & life) |

**Next:** the lineage store + review tool — lock the schema (with the recipe as a first-class field), then ship a deliberately ugly approval view to start banking `edit_diff` immediately. See the database/review approach notes.
