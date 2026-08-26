# Gates — Consistency, One True Thing, Danger Zones

*Three gates a candidate must clear before it ships. They are the difference between uncanny and embarrassing. Run them in order; a failure at any gate sends the candidate back, not forward. These are pre-QA gates internal to the engine — they fire before the candidate ever reaches the OS's formal QA filter or the human approval step.*

---

## Gate 1 — The Consistency Check

**Question: Does every detail obey the one altered law of the world?**

Consistency is what separates the uncanny from the random. A world earns belief by never breaking its own physics. Walk the candidate detail by detail:

- Name the one rule (from `novel-frames.md`). Then check each image, line, and claim against it: *does this follow from the rule, or did it sneak in from default reality?*
- **Any detail that doesn't obey the rule is a leak.** One leak tells the audience the world is fake and the spell collapses. Fix the leak or cut the detail.
- Watch for the second-law smuggle: a secondary estrangement move that introduces a *rival* physics. Allowed only if it lives *inside* the primary rule (see `novel-frames.md` → Combining moves). Two competing laws = no footing = fail.
- Watch for lore contradiction across a series: a post that breaks established world-facts fails this gate even if internally clean.

**Pass condition:** you could hand the world's rule to a stranger and they could predict every detail in the piece.

---

## Gate 2 — The One True Thing

**Question: Does the weirdness land a real feeling or insight about the *actual* subject?**

The alien world is a lens on the real one. Strangeness that reveals nothing true is empty spectacle — the single most common way good-looking weird content fails. Test:

- Finish the sentence: *"Through this world, the audience understands or feels that the real subject is ______."* The blank must contain something **true and slightly uncomfortable** about the actual product/idea — not a restatement of the gimmick.
- If the blank fills only with description of the world ("…that dreams are currency"), you have spectacle. The true thing must be about the *subject*, not the conceit.
- The true thing should be *felt*, not explained. If the piece has to spell out its own insight, the world failed to carry it — re-report from inside.
- One true thing, not five. A dispatch that tries to land several insights lands none. Pick the sharpest.

**Pass condition:** a viewer who never saw the brief would come away feeling something accurate about the real subject — and couldn't have gotten that feeling from a straight description.

---

## Gate 3 — The Danger Zone Check (per dialect)

**Question: Has the chosen dialect tipped into its specific failure mode?**

Every dialect dies a particular death. Check the candidate against the danger zone of *its* dialect (full table in `dialects.md`):

| Dialect | Dies as |
|---|---|
| Sage | wandering into vagueness or spiritual fluff |
| Ruler | startup-ese, over-corporate opacity |
| Rebel | empty edginess, generic contrarian tropes |
| Lover | faux-poetic DTC speak, Instagram cringe |
| Jester | meme-for-meme's-sake, tonal incoherence |
| Magician | woo-woo spiritualism, unfocused abstraction |
| Explorer | vagueness mistaken for insight, flatness disguised as curiosity |
| Guardian | boring rationality, fake warmth |
| Creator | ADHD tone, decorative without depth |
| Caregiver | patronizing voice, emotional manipulation |
| Every-Person | bland platitudes, social-media-therapy voice |
| Outlaw | try-hard goth, cliché rule-breaking |
| Hero | TED-talk inspiration junkie, empty motivation |

- If the candidate reads like its danger zone, the dialect's *ceiling* wasn't reached — it collapsed to the floor or below. Push toward the ceiling description, or switch dialect.
- The universal danger zone across all dialects: **it sounds like it could appear on a bland startup's homepage hero.** If so, rewrite or kill it.

**Pass condition:** the candidate sits at or near the dialect's ceiling, nowhere near its danger zone, and avoids generic startup tone entirely.

---

## How the gates connect to the loop's reject tags

The OS's reject taxonomy maps back onto these gates, which makes failures diagnosable rather than vague:

- `too_literal` → usually a **Gate 1** failure: the rule wasn't held, or the report toured the world instead of dropping the reader inside. Re-estrange and commit harder.
- `cliche` → a **Gate 3** failure (dialect collapsed to a stock move) *or* a stale estrangement axis. Switch the move's axis or push the dialect to its ceiling.
- `off_brand_visual` → the world's visual physics drifted from the loop's substrate grammar. Re-anchor the world's look to the substrate.
- `off_voice` → the dialect contradicts the loop's house voice. This is a substrate/dialect mismatch, not a world problem — change dialect, keep the world.

Frequent failures at a given gate are a signal worth carrying into the weekly substrate review: if this loop's weird candidates keep failing Gate 2, the loop may not actually want weird — which is exactly the kind of thing the conductor should learn.
