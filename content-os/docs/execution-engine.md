# Execution Engine — Spec

*The ideation + generation core of the Content OS. Turns an approved brief into scored candidates by routing it through one of three creative engines, each encoding a different way of making something good.*

Companion to `content-os-plan.md`. This is the layer that sits at the **IDEATION + EXECUTION** node of the pipeline.

---

## 1. Why three engines instead of one

"Make a post" is not one task. A weird scroll-stopper, a piece carried by voice and feeling, and a tightly composed carousel are three different *kinds* of making, and the methods that produce them well are different — often opposite. A single generic ideation pass averages them into mush: weird-but-tasteful, designed-but-soulful, creative-but-structured all collapse toward the safe middle, which is exactly the templated default the substrate is trying to escape.

So the engine doesn't generate. It **routes**, then hands the brief to the methodology built for that mode. Each engine is a *skill* with its own internal process. The router's only job is to read the brief and pick the right one (or a primary + secondary).

> The mode is chosen **per brief**. The taste (voice rules, visual grammar) comes from the **per-loop substrate**. Mode × substrate = candidates. The same brief run in the Dreamcatcher loop and the Deck Doctors loop uses the same engine but different substrate, and comes out unmistakably each brand's own.

---

## 2. The Router

Classifies each brief into a dominant **content_mode** before any generation happens.

```
INPUT:  brief {intent, format, platform, pillar} + loop substrate
        ↓
CLASSIFY content_mode:
        weird     — needs to surprise, defamiliarize, stop the scroll,
                    break pattern. Novelty is the job.
        creative  — carried by voice, feeling, taste, resonance.
                    The piece has to *move* someone. Soul is the job.
        designed  — composed/structured. Carousels, sequences, layouts,
                    systematic visual sets. Form carries meaning. Structure is the job.
        ↓
DISPATCH to engine (primary, optional secondary):
        weird     → Alien Worlds
        creative  → Rubin
        designed  → Alexander
        ↓
OUTPUT: N candidates, each tagged gen_method = {engine}
```

**Routing signals (rough heuristics, refined by the loop over time):**

| Signal in brief | Leans |
|-----------------|-------|
| intent = "stop the scroll", launch teaser, pattern-break, meme-adjacent | weird |
| intent = manifesto, story, emotional beat, voice-forward caption, founder note | creative |
| format = carousel, multi-panel, infographic, spec sheet, sequence | designed |
| pillar = animism / dream / strange | weird or creative |
| pillar = product, mechanism, "how it works" | designed |

The router can assign **primary + secondary** (e.g. *designed* carousel whose cover needs a *weird* hook → Alexander builds the structure, Alien Worlds generates the cover frame). Secondary is optional; don't force it.

**The router itself is learnable.** Because every candidate stores `gen_method` and flows through to performance + edit signal, the loop learns *which engine wins for which brief type in which loop*. Over months the heuristics above get replaced by evidence: "in the Dreamcatcher loop, weird-routed reels outperform creative-routed 2:1 on saves; in Deck Doctors, the reverse." The router is the first thing the feedback loop should tune.

---

## 3. Engine A — Alien Worlds (weird)

**Status: to build.** `/mnt/skills/user/alien-worlds/SKILL.md` (proposed path)

**Job:** generate genuine, coherent strangeness — not random noise. The failure mode of "weird" content is arbitrary weird (quirk with no logic, which reads as try-hard). Alien Worlds produces *internally-consistent estrangement*: take the familiar subject and build it a world with its own rules, then report back from inside that world. The strangeness is load-bearing and self-consistent, which is what makes it feel uncanny rather than gimmicky.

**Core method (defamiliarization via worldbuilding):**
1. **Estrange the premise.** Take the brief's subject and ask: what if this object/idea were native to a world with one rule changed? (Dreams are currency. Stones remember. The device is alive and slightly bored.)
2. **Hold the rule consistently.** Every detail obeys the altered law. Consistency is what separates uncanny from random.
3. **Report from inside.** Write/visualize as a dispatch from that world, not a description of it. The reader is dropped in, not toured around.
4. **Return one true thing.** The weirdness has to land a real feeling or insight about the actual subject, or it's empty spectacle. The alien world is a lens on the real one.

**When the router sends here:** scroll-stoppers, launch teasers that need mystery, anything where the brand's animist/dream/strange pillar is the point, content that should feel like it leaked from somewhere.

**Skill should contain:** a taxonomy of estrangement moves (rule-swap, scale-shift, animacy-shift, time-shift, perspective-from-the-object), consistency checks, and a "one true thing" gate so weirdness stays meaningful. Tonal guardrails per loop pulled from substrate (the Verdant Relic strange is not the Deck Doctors strange).

---

## 4. Engine B — Rubin (creative)

**Status: exists.** `/mnt/skills/user/rubin/SKILL.md`

**Job:** make content carried by voice, feeling, and taste — the pieces that have to *move* someone. Rubin is already built as a **creative-process conductor**: it diagnoses where a piece is in its making and routes to the right tactic rather than applying one formula.

**Its native structure (use as-is):**
- Four phases: **Seed → Experiment → Craft → Complete** (non-linear; moves back and forth).
- Six reference domains it routes between: **awareness** (perception, gathering raw material), **seeds** (ideation, lowering stakes, following excitement), **craft** (building, breaking sameness, temporary rules), **judgment** (taste, ruthless edit, the ecstatic as compass, essence), **voice** (point of view, sincerity, the mountaintop test), **collaboration** (Choice C, feedback on the work not the person).

**How the execution engine uses it:** for a creative-mode brief, invoke Rubin as the generator with the loop's substrate as the voice/taste context. Practically, lean on its **seeds** domain for divergence (collect without judging, follow excitement, A/B the survivors) and its **judgment** domain as a pre-QA taste pass (essence test, the ecstatic as compass) before candidates hit the formal QA filter. Rubin's judgment domain and the OS's `strategy-taste` check are complementary — Rubin for "does this have life," strategy-taste for "is this sharp and ownable."

**When the router sends here:** manifestos, founder notes, voice-forward captions, emotional beats, anything where the writing itself is the product.

**No build needed** — wire the existing skill in. The only addition is making it substrate-aware per loop (it currently runs brand-agnostic).

---

## 5. Engine C — Alexander (designed)

**Status: to build.** `/mnt/skills/user/alexander/SKILL.md` (proposed path)

**Job:** produce composed, structured content where form carries meaning — carousels, multi-panel sequences, layouts, systematic visual sets. Built on **Christopher Alexander's** theory of structure: wholeness, centers, and structure-preserving transformation. This is the rigorous opposite of Alien Worlds — where that engine estranges, this one *organizes*.

**Core method (decomposition into centers, then unfolding):**
1. **Find the centers.** Decompose the piece into its centers — the elements that focus attention and feel like *something* (the cover, the turn, the payoff panel, the CTA). A design is a field of centers that strengthen each other.
2. **Strengthen each center, and make centers help centers.** Alexander's fifteen properties are the toolkit (levels of scale, strong centers, boundaries, alternating repetition, positive space, good shape, local symmetries, deep interlock, contrast, gradients, roughness, echoes, the void, simplicity, not-separateness). Apply the few that fit; don't checklist all fifteen.
3. **Unfold, don't assemble.** Build the piece through **structure-preserving transformations** — each step intensifies the wholeness that's already there rather than bolting on parts. A carousel grows panel-by-panel from a seed, each panel making the whole feel more inevitable, not just longer.
4. **Test for life.** Alexander's actual criterion: which version has more life / feels more whole? (His "mirror of the self" test — which one is a truer picture of you.) That's the selection gate.

**When the router sends here:** carousels, explainer sequences, spec/mechanism content, anything where panel-to-panel structure and visual hierarchy do the work. Pairs naturally with the Nano Banana 2 image node and Magnific finishing — Alexander decides the composition; those render and finish it.

**Skill should contain:** the centers-decomposition procedure, a working subset of the fifteen properties with content-specific examples (what "levels of scale" means in a carousel, what "the void" means in a single image), the structure-preserving transformation loop, and the life/wholeness selection test. Visual-grammar constraints pulled from the loop substrate (the 1-bit mask form-grammar is itself an Alexandrian pattern language — it should live here).

---

## 6. How the engines feed the rest of the OS

```
ROUTER → engine(s) → N candidates (gen_method tagged)
   → QA FILTER (brand-fit, taste, safety, perf-prediction)
   → APPROVAL (human; edit_diff + reject_tags captured)
   → ... rest of pipeline (see content-os-plan.md §6)
```

Two feedback connections make the engine smart over time:

**1. `gen_method` → router tuning.** Performance and edit signal are partitioned by engine, so the loop learns the right routing per loop (§2). The router stops guessing and starts knowing.

**2. Reject tags → engine selection, not just substrate.** Some tags implicate the *engine choice*, not the brand memory:

| Reject tag | May mean (engine reading) |
|------------|---------------------------|
| `too_literal` | should have routed *weird* (Alien Worlds), not designed/creative |
| `cliche` | the creative engine needs fresher seeds, or route weird for novelty |
| `off_brand_visual` | Alexander decomposition failed — weak centers / wrong properties |
| `wrong_format` | router mis-classified mode; fix routing heuristic |
| `off_voice` | substrate issue, not engine — route stays, voice rules tighten |

So the tag taxonomy from the plan doc does double duty: it tunes the substrate *and* the router/engine selection.

---

## 7. Build status & order

| Engine | Status | Work |
|--------|--------|------|
| **Rubin** (creative) | ✅ exists | wire in; make substrate-aware per loop |
| **Alien Worlds** (weird) | ⬜ to build | estrangement taxonomy + consistency + "one true thing" gate |
| **Alexander** (designed) | ⬜ to build | centers decomposition + 15-properties subset + unfolding loop + life test |
| **Router** | ⬜ to build | heuristic v1 (§2 table); becomes loop-tuned over time |

**Suggested order:**
1. **Router v1** with the heuristic table — even dumb routing beats no routing, and it starts logging `gen_method` immediately so the loop can begin learning.
2. **Wire Rubin** (lowest effort, already built) so the creative path works end-to-end first.
3. **Build Alexander** next — designed content (carousels) is likely your highest-volume format, so it banks the most edit signal fastest.
4. **Build Alien Worlds** last — highest-variance, most fun, but you want the loop already running to tell you whether weird actually outperforms in each loop before over-investing.
