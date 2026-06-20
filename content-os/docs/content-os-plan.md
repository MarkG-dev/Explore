# AI Content OS — Consolidated Plan

*An operating system for AI-generated social content, designed around the learning loop as the spine rather than generation volume.*

---

## 1. Core Thesis

Raw generation is commoditized — anyone can pipe a prompt into a model. The defensible layer is everything *around* generation: brand memory, the judgment filter, orchestration, and above all the **feedback/learning loop**.

The design is built backwards from one question:

> *How does this produce on-brand content a human would have approved, without the human in the loop every time?*

The system's job is **not** to maximize engagement. It is to **compound judgment** — to make the brand memory and the QA filter smarter over time, using engagement as one noisy input among several.

**Design center (locked):**
- Hardest part to nail: **the feedback/learning loop**
- v1 autonomy: **human approves batches** (not full autonomy, not per-item gating forever)
- Scope: **open-ended / exploring** — could become an internal Spacecadet tool or a product for other brands later

---

## 2. Architecture Overview

Six layers. Build budget goes almost entirely into #1 (substrate) and #4 (judgment) — the rest is glue or commodity.

1. **Substrate (brand + voice memory)** — versioned, composable blocks, not one monolithic prompt. Voice/tone rules, visual grammar (1-bit mask form-grammar, Verdant Relic aesthetics), banned moves, sacred cows, reference exemplars, platform-specific adaptations. Generation pulls only the relevant slice. **Namespaced per loop** (see §11) — each brand/product has its own substrate; loops can seed each other.
2. **Ideation + execution engine** — briefs → candidate concepts via a router that dispatches each brief to one of three creative engines by content mode (weird / creative / designed). Fed by the content calendar, the maker-trend "hot objects" demand feed, and recycled high-performers. Specced separately in `execution-engine.md`.
3. **Generation layer** — modality-routed model calls behind a thin abstraction so providers can be swapped as the frontier moves. (See tool stack below.)
4. **Judgment / QA filter (the moat)** — brand-fit scoring, factual/safety checks, taste check, performance prediction. This is what eventually removes the human from the loop. Most systems skip it and stay forever human-gated.
5. **Orchestration + scheduling + distribution** — calendar, multi-platform formatting, posting, A/B variants. Integrate existing infra; do not rebuild.
6. **Feedback loop** — engagement and (more importantly) human-edit signal flow back into the substrate and ideation engine. Without this it's a fancy generator, not an OS.

---

## 3. The Design Center: The Learning Loop

### Why the loop is the hard part (and why most systems fake it)

1. **Attribution is corrupted.** Engagement = content × timing × algorithm × audience state × luck. Reward outcomes naively and you train on noise — you learn the algorithm's transient preferences, not durable taste.
2. **The measurable metric isn't the target.** Likes/reach are cheap and available; brand affinity / movement toward the product is what matters and is nearly unmeasurable per-post. Optimizing the proxy degrades the target (Goodhart). This is the failure mode that turns brand accounts into engagement-bait sludge over six months.
3. **Feedback is sparse and slow.** A handful of strong signals per week, each delayed days. Terrible training signal for anything resembling RL — you cannot brute-force a learned model with this little data.

### Four nested loops (different clocks)

| Loop | Clock | Human? | What it captures / does |
|------|-------|--------|--------------------------|
| **0 — Approval** | minutes | yes | The **edit diff** — the richest signal in the system (see Crown Jewel). Captures (candidate → your edit → one-tap reason). |
| **1 — Performance** | days | semi | Post-publish engagement, *gated through skepticism*: normalize vs. slot baseline, require a hypothesis not a verdict, run a control holdout. |
| **2 — Substrate update** | weeks | gated | Aggregated signal *proposes* changes to brand memory. Human approves. The substrate is sacred; it changes deliberately. |
| **3 — Model/prompt** | months | — | Accumulated edit corpus drives fine-tuning, few-shot exemplar banks, or prompt rewrites. |

### The Crown Jewel — the edit diff

Every time a human fixes a candidate **before it posts** — changes a word, cuts a line, swaps the image — that fix is the single most valuable datum in the system.

It's a clean, pre-publish, causal judgment: the *before* (what the AI made) and the *after* (what it should have been) form a perfect arrow — *you were here, you should've been there* — with the noise stripped out. Likes can't teach that; they're full of timing and luck. The edit is your taste, isolated.

**The whole OS is a machine for collecting those arrows.** Bank enough and the generator learns to make your move on the first try — which is the entire point: eventually the human stops having to fix it, and it runs without drifting off-taste. Most systems throw the edit away and keep only the like. This system keeps the one signal that's actually yours.

> Implication: **edit-capture UX is make-or-break.** If logging a reason takes more than one tap, it won't happen and the gold evaporates. This is a product/UX problem disguised as an ML problem.

### The control / holdout stream

- ~**15%** of published items get `is_control: true`.
- Controls are generated from the *current substrate but deliberately ignoring the last N learning-loop adjustments* — i.e., what the system would have made *before* it "learned" recent lessons.
- Compare normalized performance of control vs. optimized weekly. **If optimized doesn't beat control with significance, the loop is adding variance not value — pause substrate changes.**
- This is the single guardrail against laundering a few weeks of algorithmic noise into permanent brand drift. Cost: 15% of "optimized" output as the price of knowing whether the loop works. Cheap insurance.

---

## 4. The Lineage Data Model

The schema **is** the OS — the loop, the QA filter, and every "what did we learn" query read and write here. Principle: **one immutable record per content item that accretes a lineage as it moves through the pipeline.** Nothing overwritten; each stage appends.

```yaml
content_item:
  id: ci_2026_0619_a3f             # stable, sortable
  loop_id: loop_dreamcatcher       # WHICH LOOP — partitions everything below
  status: draft | approved | rejected | scheduled | live | archived

  # ── STAGE 1: BRIEF ──────────────────────────────
  brief:
    intent: "tease Dreamcatcher waitlist"
    angle_id: ang_curiosity_07              # which ideation angle
    pillar: "calm tech / animism"           # maps to this loop's substrate
    platform: ig | x | tiktok | li
    format: carousel | single | reel | thread
    content_mode: weird | creative | designed   # which execution engine ran
    substrate_version: sub_dreamcatcher_v14     # loop-scoped, versioned
    trend_signal_ref: hotobj_0612_3         # if triggered by maker-trend feed
    created_at: ...

  # ── STAGE 2: GENERATION (the candidate set) ─────
  candidates:                               # store ALL, not just the winner
    - cand_id: c1
      modality: text | image | video
      gen_method: alien_worlds | rubin | alexander   # which engine produced it
      model: "nano-banana-2 / veo-3.1 / sonnet-4.6"
      raw_prompt: "..."
      output_ref: supabase://.../c1.png
      gen_params: {seed, creativity, ...}
      internal_score: 0.72                  # from QA filter, pre-human
      score_breakdown: {brand_fit: .8, taste: .7, safety: 1.0, perf_pred: .6}
    - cand_id: c2
      ...
  selected_candidate: c1

  # ── STAGE 3: FINISHING ──────────────────────────
  finishing:
    - step: magnific_creative               # upscale + creative detail
      input_ref: c1.png
      output_ref: c1_4k.png
      params: {scale: 4, creativity: 3, prompt: "..."}
      cost_usd: 0.16

  # ── STAGE 4: HUMAN JUDGMENT (the gold signal) ───
  approval:
    decision: approved | rejected | edited
    edit_diff:                              # THE crown jewel
      before: "..."
      after: "..."
      delta_type: [voice, format, length, factual]
    reject_tags: [off_voice, too_literal, cliche, wrong_format, off_brand_visual]
    reviewer: mark
    reviewed_at: ...
    time_to_decide_sec: 8                   # friction metric — watch it

  # ── STAGE 5: PUBLICATION ────────────────────────
  publication:
    platform_post_id: "..."
    posted_at: ...
    slot: "tue_0900"                        # for baseline normalization
    is_control: false                       # holdout stream flag
    variant_group: vg_07                    # if A/B'd

  # ── STAGE 6: PERFORMANCE (accretes over time) ───
  performance:
    raw: {impressions, likes, saves, shares, comments, ...}
    normalized:
      vs_slot_baseline: 2.1x
      percentile: 0.88
    snapshots: [{t: +1h}, {t: +24h}, {t: +7d}]   # capture the curve, not one number

  # ── STAGE 7: RETROSPECTIVE (the hypothesis) ─────
  retrospective:
    hypothesis: "short declarative hook drove saves"
    confidence: low | med | high
    feeds_substrate_proposal: prop_v15_03
```

**Schema decisions that matter:**

- **Store every candidate, not just the winner.** The losers are training data — they tell you what the selection step rejects, which is half the taste signal. Cheap to store, irreplaceable later.
- **`substrate_version` on every item is non-negotiable.** Without it, a substrate change and an algorithm change are indistinguishable in the data, and the whole loop becomes uninterpretable.
- **`edit_diff` is the crown jewel** — clean, pre-publish, causal. Six months of these = the fine-tuning corpus.
- **`is_control`** enables the holdout guard.
- **Snapshots, not single numbers.** A 1-hour spike that dies ≠ a slow-burn saver. The *shape* carries the signal — especially saves/shares (intent) vs. likes (reflex).

---

## 5. Reject / Edit Tag Taxonomy (the one-tap UX)

Tiny and exhaustive-enough, or it won't get used. Each tag is an **address** — it routes automatically to the substrate component it implicates.

| Tag | Maps to substrate component | Loop action if frequent |
|-----|------------------------------|--------------------------|
| `off_voice` | voice/tone rules | propose voice-rule tightening |
| `cliche` | banned-moves list | propose adding pattern to banned moves |
| `too_literal` | brand-belief / depth | propose exemplar reweighting |
| `wrong_format` | platform-format specs | fix format template (mechanical) |
| `off_brand_visual` | visual grammar | propose visual-rule clarification |
| `factual` | safety / QA | hard QA gate (not a taste signal) |

A tag isn't a label, it's a routing instruction. `cliche` on 40% of one angle's candidates → auto-proposed banned-moves entry in the next substrate-update review.

---

## 6. The Pipeline

```
┌─────────────┐
│ TREND/BRIEF │  maker-trend "hot objects" feed + content calendar
│   intake    │  → creates brief record (Stage 1)
└──────┬──────┘
       ▼
┌─────────────┐
│  IDEATION   │  ROUTER classifies brief by content_mode →
│ + EXECUTION │  dispatches to one of three engines:
│   ENGINE    │    weird    → Alien Worlds
│             │    creative → Rubin
│             │    designed → Alexander
│             │  → N candidates (gen_method tagged) → briefs
│             │  (specced in execution-engine.md)
└──────┬──────┘
       ▼
┌─────────────┐
│ GENERATION  │  text:  Claude / Sonnet (API)
│ (multimodal)│  image: Nano Banana 2     ← base generation
│             │  video: Veo 3.1
│             │  → N candidates per brief (Stage 2)
└──────┬──────┘
       ▼
┌─────────────┐
│  FINISHING  │  Magnific: upscale + creative detail
│             │  ONLY on selected image candidates (Stage 3)
│             │  gate to winners to control cost
└──────┬──────┘
       ▼
┌─────────────┐
│  QA FILTER  │  brand-fit + taste + safety + perf-prediction
│ (automated) │  → internal_score, surfaces top candidate
└──────┬──────┘
       ▼
┌─────────────┐
│  APPROVAL   │  ← HUMAN. Batch review. One-tap tags. Edits captured.
│ (batch)     │  THE GOLD SIGNAL (Stage 4)
└──────┬──────┘
       ▼
┌─────────────┐
│  SCHEDULE   │  Blotato: multi-platform format + queue + post
│  + POST     │  set is_control, slot, variant_group (Stage 5)
└──────┬──────┘
       ▼
┌─────────────┐
│ PERFORMANCE │  pull engagement at +1h / +24h / +7d, normalize vs slot
│  HARVEST    │  (Stage 6)
└──────┬──────┘
       ▼
┌─────────────┐
│ RETROSPECT  │  generate hypothesis → link to substrate proposal
│ + LOOP BACK │  (Stage 7) → weekly substrate review → HUMAN
└─────────────┘
```

### Tool stack

| Role | Tool | Notes |
|------|------|-------|
| Text generation | Claude / Sonnet (API) | behind a swap-able abstraction |
| Image generation (base) | **Nano Banana 2** | where images are born |
| Video generation | **Veo 3.1** | |
| Image finishing | **Magnific (Freepik)** | upscale / creative re-detail; a *finishing* node, not a generator — sits after base-gen, before QA. Gate to selected winners (cost control). |
| Posting / distribution | **Blotato** | integrate, don't reimplement |
| Backbone (DB + storage + vectors + compute) | **Supabase** | see §7 |
| Substrate authoring | **Notion** (for now) | see §7 |

---

## 7. Tech Stack & Architecture Decision

**Verdict: Supabase as the backbone + a custom frontend scoped tightly to the approval/learning surface + Notion for substrate authoring (for now) + Blotato for posting.**

### Why Supabase is the spine

It collapses four otherwise-separate components into one platform:

- **Postgres** → the lineage store, as real relational rows you can actually query (e.g. *regress normalized performance on hook-type, controlling for `substrate_version`*).
- **Storage** → every `output_ref` lives alongside the metadata pointing at it. No second blob store to reconcile.
- **pgvector (native)** → the sleeper reason. Brand-fit scoring *and* substrate retrieval are both embedding-similarity problems. With pgvector in the same Postgres, "score this candidate against our exemplars" is one SQL join. The substrate, QA filter, and lineage stop being three systems and become three tables.
- **Edge functions + cron** → performance-harvest webhook sink (Blotato callbacks, the +1h/+24h/+7d snapshots) and loop orchestration. No separate worker infra for v1.

### Why a custom frontend — for exactly one reason

Not for a prettier calendar. For the **edit-capture UX**, which determines whether the whole loop works. A custom approval surface lets you capture the diff at the editor level, make tagging genuinely one tap, route each tag to its substrate component, and drive `time_to_decide_sec` toward zero. Owning that moment = owning the data-generation engine. Everything else custom is optional; this isn't.

### The one component NOT to absorb yet: substrate authoring

The substrate (voice rules, banned moves, exemplars) is human-prose-heavy, low-volume, deliberately changed. Notion earns its keep there: nice editing, free version history, comments. Keep authoring in Notion, **sync into Supabase as versioned rows for retrieval** — humans edit in the comfortable place, the engine reads from Postgres. Collapse it into the custom frontend later, once the system's proven.

> **Supabase = engine + approval app + lineage spine. Notion = substrate editing room (for now). Blotato = posting. Magnific = finishing.**

### Scope guardrail

Do not let "custom frontend" creep into rebuilding the calendar/scheduler/posting UI. The custom surface is narrowly **review + edit-capture + substrate-proposal**. Those are the only screens where bespoke control changes outcomes.

---

## 8. Key Tradeoffs

- **Slow by design.** A judgment-compounding loop is deliberately conservative about changing the substrate. Fast-learning loops are exactly the ones that drift into sludge. You trade adaptation speed for durability.
- **Edit-capture UX is the make-or-break**, not the model quality. The system's intelligence rides on frictionless in-the-moment judgment capture.
- **You need volume to learn anything.** Sparse feedback means the loop is near-useless until you post at real cadence across enough surface area. Early on, the human *is* the loop and the system is just instrumentation collecting training data. v1 is a very well-instrumented assistant, not a self-improving machine — be honest about that (to yourself or to future customers).
- **Cold-start, resolved by the house structure (see §11).** Because you own all the loops, a new loop seeds from a sibling (inherit Gentle Future's exemplars + banned-moves, then diverge). Cross-loop seeding is upside a true multi-tenant SaaS can't replicate — one customer's taste can't legally/usefully seed another's; your own brands can.
- **Generalized vs. opinionated.** A horizontal "works for any brand" tool is a crowded race to the bottom. A vertical, taste-encoded system for a specific aesthetic is defensible but smaller TAM. The opinionated version plays to the brand-strategy + literary-writing + AI-native-building spike.

---

## 9. Build Sequencing — and the trap

**The trap:** the loop only learns from *volume* of judgments. Every week the custom frontend isn't built is a week of `edit_diff` gold not banked. The risk isn't that Supabase is wrong — it's that "build the perfect approval app" starves the loop of early signal.

**Protection:** the schema is the permanent asset; the frontend is replaceable.

Suggested order:
1. **Lock the schema in Supabase first** (§4). This is the durable foundation.
2. **Ship a deliberately ugly approval view** against that schema in days. Start collecting `edit_diff` immediately.
3. **Polish the approval UX** while signal already flows — one-tap tags, clean diff capture, friction metrics.
4. **Wire Blotato** for posting + the performance-harvest webhook/cron.
5. **Stand up the control holdout** (15%) as soon as you're posting at cadence.
6. **Run the weekly substrate-update review** manually at first; automate proposals later.
7. **Only once the edit corpus is large** (months): fine-tune / build exemplar banks / rewrite prompts (Loop 3).

---

## 10. Open Questions / Decisions Pending

- **Custom ideation/execution method** — now specced in `execution-engine.md` (router + Alien Worlds / Rubin / Alexander). Two of the three engines (Alien Worlds, Alexander) still need to be built as skills.
- **How aggressive should the control holdout be?** 15% is a starting point; tune per loop against how fast each accumulates significance.
- **Where does substrate authoring eventually live** — stay in Notion, or fold into the custom frontend once proven?
- **Loop count discipline** — how many loops can run before edit-attention spreads too thin to compound (see §11)?

---

## 11. The Multi-Loop Model

It's not vertical *or* horizontal. It's **one engine running N loops in parallel** — every brand/product is its own loop with its own substrate, edit corpus, normalized baselines, and control holdout. Gentle Future is a loop. Dreamcatcher is a loop. Deck Doctors is a loop. The architecture doesn't care how many there are.

**What this changes:**

- **The schema already supports it.** `loop_id` at the top of `content_item` partitions every query, baseline, proposal, and holdout for free. The lineage store was always multi-tenant; we just named it.
- **The substrate is namespaced, not singular.** Keyed by `loop_id`. A change proposed in the Dreamcatcher loop never touches the Deck Doctors loop. The QA filter and execution engine load the slice for whichever loop the item belongs to.
- **Cold-start becomes a feature, not a tax.** Because *you* own every loop, a new one seeds pre-warmed from a sibling (inherit exemplars + banned-moves from Gentle Future, then diverge as its own edits accumulate). This cross-loop inheritance is the thing a true external multi-tenant SaaS *can't* easily do — within your own house it's pure upside, and it's what makes the "house of brands" structure compound.

**The one real constraint it sharpens (doesn't solve): volume per loop.** N loops split your finite edit-attention N ways. A loop posting twice a month warms up glacially and stays in assisted mode indefinitely. So the discipline is **loop count, not loop capability** — run few enough loops that each clears the volume bar to actually compound, or knowingly accept that low-cadence loops never reach autonomy. This is the real governor on how wide the house can go.

This also folds the earlier "media-incubated product house" framing into the architecture: the OS becomes the content engine *underneath* the house of brands, with each brand a loop and the hot-objects site as shared top-of-funnel demand-sensing across all of them.
