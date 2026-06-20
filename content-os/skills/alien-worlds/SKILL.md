---
name: alien-worlds
description: Weird-mode creative engine for the Content OS. Generates genuine, coherent strangeness — not random noise — by taking a familiar subject, building it a world with one rule changed, and reporting back from inside that world. Use for scroll-stoppers, launch teasers that need mystery, pattern-breaks, meme-adjacent work, and anything where the brand's animist / dream / strange pillar is the point. Triggers on "make it weird," "stop the scroll," "this feels too safe," "too on-the-nose," "defamiliarize this," "needs an edge," "make it feel like it leaked from somewhere," or any brief the router classifies content_mode = weird. The failure mode it exists to prevent is arbitrary weird (quirk with no logic, which reads as try-hard).
---

# Alien Worlds — Weird-Mode Engine (defamiliarization via worldbuilding)

## Philosophy

**Alien is not a tone. It's a perspective. A posture. A guiding principle.** It's the lens we look through before we begin, and the interference pattern we introduce when things feel too clean, too obvious, or too familiar. Alien is how we remember to disrupt the expected. We don't follow trends — we foresee trajectories. The voice doesn't just stay distinct; it *destabilizes*. It interrupts. It is the foreign body in the category.

**Worldbuilding is not a tone either. It's a technique. A dimensional upgrade.** Where storytelling is about *what* a brand says, worldbuilding is about *where* the story takes place — and *who gets to live there*. It turns messaging into myth, products into artifacts, customers into inhabitants. The goal isn't to speak clearly; it's to create a place people want to move into, reference, remix, or revere.

> If **Alien** is the interference pattern — disrupting what's expected — **Worldbuilding** is the gravity field — pulling people deeper.

The job of this engine is to produce **internally-consistent estrangement**: take the familiar subject, build it a world with its own rules, hold those rules without flinching, and report from inside. The strangeness is *load-bearing* and *self-consistent* — that is what makes it feel uncanny rather than gimmicky.

## The One Law

**Arbitrary weird is the enemy.** Quirk with no logic reads as try-hard. Every move in this engine is in service of strangeness that *obeys a rule* and *lands a real feeling about the actual subject*. If the weirdness isn't doing both, it's empty spectacle — cut it.

## The Core Method

Four steps. This is the spine; everything in the reference files serves it.

1. **Estrange the premise.** Take the brief's subject and ask: *what if this object/idea were native to a world with one rule changed?* (Dreams are currency. Stones remember. The device is alive and slightly bored.) Pick **one** alteration, not five — see `references/estrangement.md` for the taxonomy of moves.
2. **Hold the rule consistently.** Every detail obeys the altered law. Consistency is the entire difference between *uncanny* and *random*. The world earns belief by never breaking its own physics.
3. **Report from inside.** Write/visualize as a *dispatch from* that world, not a *description of* it. Drop the reader in; don't tour them around. No explaining, no winking, no "imagine if."
4. **Return one true thing.** The weirdness has to land a real feeling or insight about the *actual* subject, or it's empty. The alien world is a lens on the real one. This is a gate, not a suggestion — see `references/gates.md`.

## How This Skill Works

When invoked, diagnose the brief and run the method:

1. **What is the real subject?** Name the actual product/idea/feeling under the brief, plainly, before estranging anything. You can't return a true thing about a subject you haven't named.
2. **Which estrangement move fits?** Pick the rule-change that *illuminates* the subject, not just the flashiest one. Load `references/estrangement.md`.
3. **What world does the rule build?** Establish the world's physics so they can be held consistently. Load `references/worldbuilding.md` for reality-design depth (lore, ritual, artifacts, inhabitants).
4. **In what dialect does this world speak?** The 13 tonal archetypes in `references/dialects.md` are *how* the strangeness is voiced — pull the strain that fits the loop's substrate (the Verdant Relic strange is not the Deck Doctors strange).
5. **Does it pass the gates?** Run consistency check + the one-true-thing gate + danger-zone check before producing candidates. Load `references/gates.md`.

Generate **N candidates**, each tagged `gen_method = alien_worlds`. Vary the *estrangement move* and the *dialect* across candidates — that is where the real range lives, not in surface wording.

## The Four Reference Domains

### 1. `references/estrangement.md` — The Taxonomy of Moves
**Load when:** choosing *how* to make the subject strange. The five core moves — **rule-swap, scale-shift, animacy-shift, time-shift, perspective-from-the-object** — plus how to pick the one that illuminates rather than decorates, and how to combine moves without losing consistency.

### 2. `references/worldbuilding.md` — Reality Design
**Load when:** the rule is chosen and the world needs depth so it can be held. Storytelling → worldbuilding shift, the gravity-field principle, lore / ritual / mythology / symbolic artifacts, turning customers into inhabitants. How a world stays coherent across many posts (the world is an asset that compounds, like the substrate).

### 3. `references/dialects.md` — The 13 Tonal Archetypes
**Load when:** deciding the *voice* the dispatch is written in. The full tone table (purpose, mood, language, floor, ceiling, danger zone) for Sage, Ruler, Rebel, Lover, Jester, Magician, Explorer, Guardian, Creator, Caregiver, Every-Person, Outlaw, Hero — plus per-archetype copy instructions for setup lines, manifestos, and language exploration. Dialects are reference, not rule: pull what serves, ignore what doesn't, hybridize freely.

### 4. `references/gates.md` — Consistency, One True Thing, Danger Zones
**Load when:** before candidates ship. The consistency check (does every detail obey the one rule?), the one-true-thing gate (does the weirdness reveal something real about the subject?), and the per-dialect danger zones (the specific way each tone fails — try-hard goth, woo-woo spiritualism, meme-for-meme's-sake, etc.).

## Routing Logic

The execution-engine router sends weird-mode briefs here. Once inside:

- **Brief is vague / subject unclear** → name the real subject first (step 1); refuse to estrange a blur.
- **"Make it weird" with no direction** → default to the estrangement move that *inverts the category's most boring assumption* (`references/estrangement.md`), voiced in the loop's house dialect.
- **Needs mystery / "leaked from somewhere"** → Magician or Explorer dialect + report-from-inside discipline; withhold, don't explain.
- **Launch teaser / pattern-break** → rule-swap or animacy-shift, tight; one true thing about *why the thing matters*, never the spec.
- **It came back `too_literal`** → the rule wasn't held, or the report toured instead of dropping in. Re-estrange harder, commit further.
- **It came back as `cliche`** → the move is a stock move; switch estrangement axis (if you scaled, try animacy; if you anthropomorphized, try perspective-from-the-object).

> Mode × substrate = candidates. This engine supplies the *mode* (weird). The loop's substrate supplies the *taste* (which dialect, which sacred cows, which banned moves). The same brief run in two loops uses the same method and comes out unmistakably each brand's own.

## Tone

Speak from inside the world, with calm conviction in its rules. Don't pitch the strangeness — inhabit it. Treat the altered law as obviously true and let the reader feel the vertigo of a place that runs on different physics but never contradicts itself. When the work feels too clean, break it. When it feels too familiar, mutate it. **Start from the strain that doesn't quite fit — but somehow lands.**
