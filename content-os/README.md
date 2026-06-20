# Content OS — Execution Engine & Creative Skills

The ideation + execution core of the AI Content OS: a **router** that classifies each brief and dispatches it to one of **three creative engines**, each a skill encoding a different way of making something good.

```
brief ──▶ ROUTER ──▶ classify content_mode ──▶ dispatch to engine(s) ──▶ N candidates (gen_method tagged)
                         weird    → Alien Worlds
                         creative → Rubin
                         designed → Alexander
```

The mode is chosen **per brief**; the taste comes from the **per-loop substrate**. *Mode × substrate = candidates.*

## Layout

```
content-os/
├── README.md                  ← you are here
├── docs/
│   ├── content-os-plan.md      consolidated system plan (the learning loop, lineage schema, pipeline)
│   └── execution-engine.md     spec for this layer (router + three engines)
└── skills/
    ├── router/        SKILL.md            the engine — classifies brief, dispatches, logs gen_method
    ├── alien-worlds/  SKILL.md + refs     weird mode — defamiliarization via worldbuilding
    ├── rubin/         SKILL.md            creative mode — Rick Rubin creative-process conductor
    └── alexander/     SKILL.md + refs     designed mode — fit via decomposition (Christopher Alexander)
```

## The three engines

| Mode | Engine | The job | Built from |
|------|--------|---------|------------|
| **weird** | **Alien Worlds** | genuine, coherent strangeness — surprise, defamiliarize, stop the scroll | *Alien + Worldbuilding + Dialects* (13 tonal archetypes) + `execution-engine.md` §3 |
| **creative** | **Rubin** | voice, feeling, taste — work that has to *move* someone | Rick Rubin, *The Creative Act* (provided as the structural template) |
| **designed** | **Alexander** | composed structure where form carries meaning — carousels, sequences, layouts | Christopher Alexander, *Notes on the Synthesis of Form* + `execution-engine.md` §5 |

**Alien Worlds** introduces an *interference pattern* (estrangement). **Alexander** builds a *gravity of structure* (fit). They are deliberate opposites; **Rubin** is the soul in the middle. The router decides which a brief needs — and learns the right routing per loop over time from the `gen_method` signal on every candidate.

## How a brief flows

1. **Router** reads `{intent, format, platform, pillar}` + the loop's substrate → classifies `content_mode` → dispatches to the primary engine (and an optional secondary, e.g. an Alexander carousel with an Alien Worlds cover).
2. The **engine** runs its own method with the substrate as taste context and returns **N candidates**, each tagged `gen_method`.
3. Candidates flow to the **QA filter → human approval** (where `edit_diff` + `reject_tags` are captured) → the rest of the pipeline in `docs/content-os-plan.md`.
4. Performance + edit signal, partitioned by `gen_method`, **tune the router and the engines** over time.

## Build status

| Component | Status |
|---|---|
| Router (heuristic v1) | ✅ built — `skills/router/` |
| Alien Worlds (weird) | ✅ built — `skills/alien-worlds/` (estrangement taxonomy · worldbuilding · 13 dialects · gates) |
| Alexander (designed) | ✅ built — `skills/alexander/` (fit & misfit · decomposition · constructive diagrams · realization & life) |
| Rubin (creative) | ✅ wired in — `skills/rubin/` (canonical conductor; runs substrate-aware per loop) |

Next per `docs/execution-engine.md` §7: wire candidates into the lineage schema (`content-os-plan.md` §4) and let the feedback loop start replacing the router's heuristics with evidence.
