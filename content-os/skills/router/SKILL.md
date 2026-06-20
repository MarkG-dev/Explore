---
name: router
description: The ideation + execution engine for the Content OS — the dispatcher at the IDEATION + EXECUTION node of the pipeline. Reads an approved brief, classifies it into a dominant content_mode (weird / creative / designed), and routes it to the engine built for that mode (Alien Worlds / Rubin / Alexander), optionally with a secondary engine. Use whenever a brief needs to become candidates. Triggers on "run this brief," "turn this into posts/candidates," "what engine should this go to," "route this," "make candidates for…," or any content brief entering the pipeline. The router does not generate; it classifies and dispatches, and it logs gen_method so the feedback loop can learn the right routing per loop over time.
---

# Router — Ideation + Execution Engine

## Why this exists

"Make a post" is not one task. A weird scroll-stopper, a piece carried by voice and feeling, and a tightly composed carousel are three different *kinds* of making, and the methods that produce them well are different — often opposite. A single generic ideation pass averages them into mush: weird-but-tasteful, designed-but-soulful, creative-but-structured all collapse toward the safe middle — exactly the templated default the substrate is trying to escape.

So this engine **does not generate. It routes**, then hands the brief to the methodology built for that mode. Each engine is a skill with its own internal process. The router's only job is to read the brief and pick the right one (or a primary + secondary).

> The **mode** is chosen per brief. The **taste** (voice rules, visual grammar) comes from the per-loop substrate. **Mode × substrate = candidates.** The same brief run in two loops uses the same engine but different substrate, and comes out unmistakably each brand's own.

## The three engines

| content_mode | Engine | Skill | The job |
|---|---|---|---|
| **weird** | Alien Worlds | `../alien-worlds/SKILL.md` | Surprise, defamiliarize, stop the scroll, break pattern. **Novelty is the job.** |
| **creative** | Rubin | `../rubin/SKILL.md` | Carried by voice, feeling, taste, resonance. The piece has to *move* someone. **Soul is the job.** |
| **designed** | Alexander | `../alexander/SKILL.md` | Composed/structured — carousels, sequences, layouts, systematic visual sets. Form carries meaning. **Structure is the job.** |

## How This Skill Works

Given a brief `{intent, format, platform, pillar}` + the active loop's substrate:

### Step 1 — Classify content_mode

Read the brief against the three definitions, then weigh the signals:

| Signal in brief | Leans |
|---|---|
| intent = "stop the scroll", launch teaser, pattern-break, meme-adjacent | **weird** |
| intent = manifesto, story, emotional beat, voice-forward caption, founder note | **creative** |
| format = carousel, multi-panel, infographic, spec sheet, sequence | **designed** |
| pillar = animism / dream / strange | **weird** or **creative** |
| pillar = product, mechanism, "how it works" | **designed** |

Pick the **dominant** mode. These are heuristics for v1; they get replaced by evidence over time (see "The router is learnable" below).

### Step 2 — Assign primary (+ optional secondary)

- **Primary** = the dominant mode's engine. Always assigned.
- **Secondary** = optional, only when one part of the piece needs a different kind of making than the whole. Classic case: a *designed* carousel whose cover needs a *weird* hook → **Alexander** builds the structure, **Alien Worlds** generates the cover frame, then it's fused back in as a citizen of Alexander's structure. **Don't force a secondary** — most briefs are single-engine.

### Step 3 — Dispatch with substrate

Invoke the chosen engine skill(s) with the active loop's substrate as context:

- **Alien Worlds** → which dialect(s) are house vs. banned, tonal guardrails, the loop's "strange."
- **Rubin** → voice/tone rules, banned moves, exemplars (Rubin runs substrate-aware per loop, not brand-agnostic).
- **Alexander** → the loop's visual grammar / form-grammar (itself a pattern language) and platform-format specs.

### Step 4 — Tag and emit

Each returned candidate is tagged `gen_method = {alien_worlds | rubin | alexander}` and carries its `content_mode`, `substrate_version`, and (if used) which engine produced which part. These flow into the lineage record (Stage 2 of `content-os-plan.md` §4) and onward to the QA filter → approval.

```
INPUT:  brief {intent, format, platform, pillar} + loop substrate
   ↓ classify content_mode  (weird | creative | designed)
   ↓ dispatch  primary (+ optional secondary)
        weird     → Alien Worlds
        creative  → Rubin
        designed  → Alexander
   ↓ run engine(s) with substrate
OUTPUT: N candidates, each tagged gen_method = {engine}
   → QA FILTER → APPROVAL (edit_diff + reject_tags captured) → rest of pipeline
```

## The router is learnable (the part that matters over time)

Because every candidate stores `gen_method` and flows through to performance + edit signal, the loop learns **which engine wins for which brief type in which loop.** Over months the heuristic table above gets replaced by evidence:

> "In the Dreamcatcher loop, weird-routed reels outperform creative-routed 2:1 on saves; in Deck Doctors, the reverse."

**The router is the first thing the feedback loop should tune.** Until then, run the heuristics — even dumb routing beats no routing, because it starts logging `gen_method` immediately so the loop can begin learning.

## Reject tags route the router, not just the substrate

Some reject tags from the approval step implicate the *engine choice*, not the brand memory. When a tag recurs on a brief type, adjust routing:

| Reject tag | Engine reading → router action |
|---|---|
| `too_literal` | should have routed **weird** (Alien Worlds), not designed/creative |
| `cliche` | the creative engine needs fresher seeds, or route **weird** for novelty |
| `off_brand_visual` | Alexander decomposition failed — weak centers / wrong properties (engine quality, re-decompose) |
| `wrong_format` | router **mis-classified mode** — fix the routing heuristic |
| `off_voice` | substrate issue, not engine — route stays, voice rules tighten |

So the tag taxonomy does double duty: it tunes the substrate *and* the router/engine selection.

## Routing Logic (quick reference)

- "Stop the scroll" / teaser / pattern-break → **Alien Worlds**.
- Manifesto / founder note / emotional beat / voice-forward caption → **Rubin**.
- Carousel / sequence / spec / "how it works" → **Alexander**.
- Designed piece that needs a strange cover → **Alexander primary + Alien Worlds secondary**.
- Animist/dream/strange pillar → **weird or creative**; let intent break the tie (does it need to *surprise* or to *move*?).
- Genuinely ambiguous mode → route to the primary and let the loop's accumulating `gen_method` evidence settle it next time; don't agonize, log and learn.

## Tone

Decisive and light. The router's value is a fast, defensible classification, not a deliberation — pick the mode, name why in a phrase, dispatch. Hold the heuristics loosely: they are scaffolding the feedback loop will replace with evidence. The discipline is to *always tag* `gen_method`, because the tag is what makes the router smarter than its rules.
