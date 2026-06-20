# Approval-View Contract (v1)

> The approval view is not a feature — it's the **data-generation engine**. It owns the
> one moment taste gets captured. Everything here is the handshake between the disposable
> UI and the permanent schema. The UI can be rewritten weekly; **these field names and
> routing semantics must not drift**, because every query the loop ever runs reads them.

The view operates at the `approval` stage of a `content_item`. It **reads** the
`candidates` stage and **writes** an approval record (append-only, never overwrites).

---

## 1. What the surface READS — input contract

The view is handed one `content_item` ready for approval:

```jsonc
{
  "loop_id": "loop_homesick",            // partition key — which loop/house
  "content_item_id": "ci_2026_0620_017",
  "substrate_version": "sub_v3.2",       // stamped on EVERYTHING (non-negotiable)
  "brief": {
    "brief_type": "product_drop",        // normalized — the "for which brief-type" axis
    "brief_text": "Tease the linen pillow restock, warm not salesy."
  },
  "candidates": [                        // ALL of them — losers are half the taste signal
    {
      "candidate_id": "cand_a",
      "asset": { "kind": "text", "body": "..." },   // or { kind:"image", url:"..." }
      "internal_score": 0.81,            // model's own pre-rank — shown, not trusted
      "is_control": false,               // 15% holdout stream
      "gen_methods": ["Alexander", "Alien"],        // ORDERED list of lenses — the recipe
      "making_plan": {                   // the plan we regress performance on
        "lenses": ["Alexander", "Alien"],
        "sequence": "Alexander frames → Alien twists the close",
        "hand_offs": ["Alexander→Alien: keep the object, break the expectation"]
      }
    }
    // ... every candidate, winner and losers
  ]
}
```

The view MUST render, per candidate: the **asset**, its **internal_score**, and its
**recipe** (`gen_methods` + `making_plan`). Recipe visibility is the point — the human is
implicitly rating recipes, not just outputs.

---

## 2. What the surface WRITES — output contract (the gold)

One append on `Approve & ship` / `Reject all`:

```jsonc
{
  "content_item_id": "ci_2026_0620_017",
  "loop_id": "loop_homesick",
  "substrate_version": "sub_v3.2",       // stamped through — sub change vs algo change
  "stage": "approval",
  "approval_action": "approve_with_edits", // approve | approve_with_edits | reject_all
  "selected_candidate_id": "cand_a",       // null when reject_all

  // ── CROWN JEWEL ──────────────────────────────────────────────
  "edit_diff": {
    "before": "...",                  // EXACTLY what the AI made — lossless, the source of truth
    "after": "...",                   // EXACTLY what ships (post-inline-edit) — lossless
    "delta_type": "tightened",        // HUMAN-TAPPED at commit. none|tightened|rewrote|reordered|tone|factual
    "delta_hint": "tightened"         // heuristic guess, reference ONLY — never trusted, never queried as truth
  },

  // ── ONE-TAP ROUTING (triple duty: substrate · lens · planner) ─
  "reject_tags": [
    {
      "tag": "too_literal",
      "layer": "planner",             // WHERE the miss lives — a routing instruction
      "target_ref": "cand_b",         // which candidate / lens / substrate doc the tag is about
      "note": null                    // optional, but never required (1 tap or it won't happen)
    }
  ],

  // ── SILENT FRICTION METRIC ───────────────────────────────────
  "time_to_decide_sec": 42,           // captured silently from view-open to commit
  "decided_at": "2026-06-20T14:03:11Z",
  "decided_by": "mark@deckdoctors.xyz"
}
```

`edit_diff` is captured **at the editor level automatically**: `before` is the selected
candidate's untouched body, `after` is whatever is in the editor at commit. The human never
"saves a diff" — they just edit, and the diff falls out.

**`delta_type` is a one-tap human choice at commit, not a guess.** Raw `before`/`after` are
lossless and can never be wrong, so they're the permanent source of truth. The *label* is the
fragile part, so we don't let code write it: when the candidate was edited, the commit button
reveals a one-tap delta picker (the heuristic pre-highlights a `hint`, but the tap is what
ships). An untouched candidate skips the picker and writes `delta_type: "none"`. The heuristic
is preserved as `delta_hint` for reference/auditing only — it is **never** queried as truth.
This keeps the corpus clean from day one without costing more than one tap.

---

## 3. Reject-tag taxonomy — each tag is a routing instruction, not a label

The reframe (a piece is built by a *sequence of lenses* chosen by a *planner* over a
*substrate*) means a miss can live in three different layers. The tag carries the `layer`
so feedback routes to the thing that can actually fix it.

| tag                 | layer     | means                                                        |
|---------------------|-----------|--------------------------------------------------------------|
| `too_literal`       | planner   | plan should have pulled a wilder lens (e.g. Alien)           |
| `too_safe`          | planner   | recipe under-reached for this brief_type                     |
| `wrong_format`      | planner   | plan picked the wrong shape entirely                         |
| `off_brand_visual`  | lens      | a lens failed inside the build (e.g. Alexander)              |
| `off_voice`         | lens      | voice lens didn't land                                       |
| `weak_hook`         | lens      | opening lens underperformed                                  |
| `factual_error`     | substrate | bad fact pulled from substrate                               |
| `stale_reference`   | substrate | substrate content out of date                                |
| `derivative`        | substrate | substrate too thin → generic output                          |

The view renders these as one-tap chips. Tapping a chip on a candidate emits a
`reject_tags` entry with the correct `layer` pre-filled — the human is routing without
knowing they're routing.

---

## 4. Interaction rules (the non-negotiables)

1. **Batch view** — all candidates on one screen, scores + recipes visible.
2. **Inline editing on the selected candidate** — diff captured at editor level, no "save diff" step.
3. **One tap per reason** — if a reject reason costs more than one tap, it won't happen and the gold evaporates.
4. **time_to_decide is silent** — never shown, never asked for; it's a friction metric to watch.
5. **Append-only** — the view never mutates the candidate; it writes a new approval record.

---

## 5. Honest scope of v1

With sparse feedback, **the human is the loop and this view is instrumentation**. It is a
very well-instrumented assistant collecting training data — not a self-improving machine
yet. That is the correct first thing to build. Polish the one-tap UX *while signal already
flows*; never let a week of polishing cost a week of un-banked `edit_diff`.
