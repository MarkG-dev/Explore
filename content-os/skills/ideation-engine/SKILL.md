---
name: ideation-engine
description: The conductor of the Content OS ideation layer. Turns a brief into scored candidates — not by picking one engine, but by composing a making-plan: deciding which generative lenses to pull on (Alien for novel frames, Alexander for structure; the kit grows over time), in what sequence, then running each as a discrete pass and applying a taste gate before candidates hit QA. Rubin-shaped: it runs the creative process (diagnose → diverge → build → judge) and owns the taste gate. Use whenever a brief needs to become candidates. Triggers on "run this brief," "turn this into posts/candidates," "make candidates for…," "what's the plan for this brief," "ideate on this." It does not switch between engines; it plans, sequences, composes, and judges — and logs the tool-recipe so the feedback loop learns which recipes win per loop.
---

# Ideation Engine — Conductor

## What this is (and what it is not)

This is **not a router that picks one engine per brief.** That model treated three very different things as symmetric modes and forced an either/or. They aren't symmetric, and a single piece routinely wants more than one of them.

This is a **conductor**: it reads the brief, composes a *making-plan* (which lenses, in what order), runs each lens as a discrete pass, and judges the result. The brief never gets classified into a bucket — it gets a plan.

> **The taste comes from the per-loop substrate. The plan comes from the brief. Substrate × plan = candidates.** The same brief in two loops runs the same lenses with different substrate and comes out unmistakably each brand's own.

## The shape: Rubin-shaped, with a kit of lenses

The conductor's control loop *is* the creative process. That process is Rubin (`../rubin/SKILL.md`), and its six domains map cleanly onto the engine's stages:

| Rubin domain | Stage in the engine |
|---|---|
| awareness + seeds | **intake + divergence** — read the brief, gather raw material, generate options without judging |
| craft | **build** — *where the lenses do their work* (Alien, Alexander) |
| judgment | **the taste gate** — "does this have life?" before QA |
| voice | **POV** — supplied by the loop's substrate |
| collaboration | **the human edit-diff loop** — Choice C is the approval-and-edit step itself |

So **Rubin is the conductor and the gate.** The generative lenses are the instruments it picks up during the build stage.

### The kit (growable)

| Lens | Skill | What it does | When to pull it |
|---|---|---|---|
| **Alien** | `../lenses/alien/SKILL.md` | **Novel frames** — finds the angle nobody else would; estrangement + worldbuilding + a voice palette (13 dialects). Novelty is the job. | the piece needs to surprise, stop the scroll, defamiliarize, or carry a distinct voice |
| **Alexander** | `../lenses/alexander/SKILL.md` | **Structure for fit** — decompose into centers, resolve each, fuse into a whole. Wholeness is the job. | the piece needs composition, hierarchy, sequence: carousels, explainers, layouts |

The kit is meant to grow — a trend-graft lens, a reference/awareness lens, etc., slot in later without restructuring the conductor.

## The making-plan (the planner)

For each brief `{intent, format, platform, pillar}` + the loop's substrate, decide:

1. **Which lenses** the piece needs (one, both, or — later — more).
2. **In what sequence** they run.
3. **How they hand off** (what each pass receives from the last).

Leanings that feed the plan (heuristics for v1, replaced by evidence over time):

| Signal in brief | Pulls in |
|---|---|
| "stop the scroll", launch teaser, pattern-break, meme-adjacent, animism/dream/strange pillar | **Alien** |
| carousel, multi-panel, sequence, infographic, spec/"how it works", product/mechanism pillar | **Alexander** |
| manifesto, founder note, emotional beat, voice-forward caption | lean on **Rubin's seeds/voice directly** (and a dialect from Alien for the voice) |

Common composed plans:

- **Carousel with a striking cover** → Alexander builds the structure → Alien generates the cover frame + house dialect → fuse the cover back in as a citizen of Alexander's structure.
- **Weird teaser that still has to land** → Alien finds the novel frame → Rubin's judgment gate checks it has life and one true thing.
- **Voice-forward manifesto** → Rubin seeds the divergence → Alien lends a dialect → Rubin's judgment selects.

## The one safeguard: sequence distinct passes, never average

The failure this whole design exists to avoid is the **generic ideation pass that averages everything to the safe middle** — weird-but-tasteful, designed-but-soulful, all collapsing toward the templated default.

Composition is only safe if the lenses run as **discrete, sequenced passes**, each keeping its method pure:

> Alien estranges the concept → Alexander structures it → Rubin judges it.

**Never** ask one pass to "be novel and structured and soulful at once." That blend is exactly the mush. One lens, one pass, one job; hand off; next lens. This is the line that lets one engine hold many tools without going gray.

## The taste gate

Before any candidate leaves the engine, run **Rubin's judgment domain** as a pre-QA pass: does this have life? Is the essence intact? (Strip-to-skeleton, the ecstatic as compass, clean slate.) This is complementary to the OS's formal QA filter and the `strategy-taste` check — Rubin asks *"is this alive?"*, strategy-taste asks *"is this sharp and ownable?"*. Candidates that fail the gate are reworked or dropped, not passed along.

## Output: candidates tagged with the recipe

Each candidate carries:

- `gen_methods` — **the recipe**, an ordered list of the lenses used (e.g. `[alexander, alien]`), not a single value. A piece is made by a *sequence* of tools, so the lineage records the sequence.
- `content_mode` — a **soft descriptor** of what the piece primarily needed (weird / creative / designed). No longer a hard switch; just a label for analysis.
- `making_plan` — the plan that produced it (lenses + sequence + handoffs), so the planner itself is reconstructable.
- `substrate_version` — which slice of brand memory was active.

```
brief + substrate
   ↓ PLAN        choose lenses + sequence
   ↓ BUILD       run each lens as a discrete pass, handing off
        Alien     → novel frame / voice
        Alexander → structure / fit
   ↓ GATE        Rubin judgment — does it have life?
   ↓ EMIT        candidates tagged {gen_methods recipe, content_mode, making_plan, substrate_version}
   → QA FILTER → APPROVAL (edit_diff + reject_tags captured) → rest of pipeline
```

## The learnable surface (why this beats a switch)

Because every candidate records its **recipe** and its **brief-type**, and both flow through to performance + edit signal, the loop learns the genuinely useful thing:

> *which tool-recipe wins for which brief-type in which loop* — e.g. "in Dreamcatcher, `[alien]` reels beat `[alexander, alien]` carousels on saves; in Deck Doctors, the reverse."

That is a far richer learnable surface than "which of three engines wins." The planner is the first thing the feedback loop should tune. Until it has data, run the heuristics above — even a rough plan beats no plan, because it starts logging recipes immediately.

## Reject tags tune the planner, not just the substrate

| Reject tag | Planner reading → action |
|---|---|
| `too_literal` | the plan needed **Alien** (a novel frame) and didn't pull it |
| `cliche` | Alien's frame was stale, or the plan over-relied on structure — push Alien harder |
| `off_brand_visual` | **Alexander** failed inside the build — weak centers / wrong properties (re-decompose) |
| `wrong_format` | the plan mis-read what the piece needed — fix the planning leaning |
| `off_voice` | substrate issue, not the plan — voice rules tighten; plan stays |

## Tone

Decisive and composing, not deliberating. Name the plan in a phrase ("Alexander for the spine, Alien for the cover, Rubin to pick"), run it, judge it. Hold the heuristics loosely — they're scaffolding the loop will replace with recipe evidence. The discipline that makes the engine smarter than its rules: **always record the recipe.**
