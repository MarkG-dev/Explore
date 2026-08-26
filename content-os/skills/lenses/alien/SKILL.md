---
name: alien
description: The novel-frames lens of the Content OS ideation engine. Its job is novelty — finding the frame nobody else would, the angle that makes a familiar subject newly visible. Its primary technique is estrangement via worldbuilding (take the subject, change one rule, build it a small world, report from inside), backed by a 13-dialect voice palette. The conductor pulls this lens when a piece needs to surprise, stop the scroll, defamiliarize, break pattern, carry a distinct voice, or feel like it leaked from somewhere. Triggers on "make it weird/novel," "stop the scroll," "this feels too safe," "too on-the-nose," "find a fresher angle," "needs an edge," "give it a voice." The failure mode it exists to prevent is arbitrary weird — novelty with no logic, which reads as try-hard.
---

# Alien — The Novel-Frames Lens

## What this lens is for

**Novel frames.** Given a subject, Alien's job is to find the *frame* nobody else would use — the angle, container, or vantage that makes the familiar subject newly visible and impossible to scroll past. Not strangeness for its own sake; *novelty that reveals.*

A **frame** is the conceptual container you present the subject through. Most content reuses the category's default frame ("here's our product, here's why it's good") and disappears into sameness. Alien's whole function is to swap that default for a frame so fresh the subject is seen again.

> Alien is the conductor's instrument for **novelty and voice**. The conductor (`../../ideation-engine/SKILL.md`) pulls it during the build stage when a piece needs to surprise or to speak in a distinct register. It runs as a discrete pass — it finds and inhabits the frame, then hands off.

## Philosophy

**Alien is not a tone. It's a perspective. A posture. A guiding principle** — the lens we look through before we begin, and the interference pattern we introduce when things feel too clean, too obvious, or too familiar. We don't follow trends; we foresee trajectories. The voice doesn't just stay distinct — it *destabilizes*. It is the foreign body in the category.

**Worldbuilding is the depth mechanism.** Where storytelling is about *what* a brand says, worldbuilding is about *where* the story takes place and *who gets to live there.* A novel frame becomes a *place* — and a place has gravity.

> If novelty is the **interference pattern** that stops the scroll, worldbuilding is the **gravity field** that keeps people there.

## The One Law

**Arbitrary novelty is the enemy.** A fresh-looking frame with no logic reads as try-hard. Every move in this lens serves novelty that *obeys a rule* and *lands a real feeling about the actual subject*. If the frame isn't doing both, it's empty spectacle — cut it.

## The Core Method

Estrangement via worldbuilding is the primary engine for producing novel frames. Four steps:

1. **Find the novel frame.** Take the subject and ask: *what if this were native to a world with one rule changed?* (Dreams are currency. Stones remember. The device is alive and slightly bored.) Pick **one** alteration — the frame — not five. The taxonomy of frame-shift moves is in `references/novel-frames.md`.
2. **Hold the frame consistently.** Every detail obeys the altered rule. Consistency is the entire difference between *novel* and *random*. The frame earns belief by never breaking its own logic.
3. **Report from inside.** Write/visualize as a *dispatch from* that world, not a *description of* it. Drop the reader in; don't tour them around. No explaining, no winking.
4. **Return one true thing.** The frame has to land a real feeling or insight about the *actual* subject, or it's empty. The novel frame is a lens on the real one — a gate, not a suggestion (`references/gates.md`).

## How This Lens Works

When the conductor invokes Alien on a brief (with the loop's substrate as context):

1. **Name the real subject** in one plain sentence first. You can't return a true thing about a subject you never named, and you can't tell whether a frame *illuminates* or merely decorates.
2. **Choose the frame-shift move** that illuminates rather than decorates → `references/novel-frames.md` (rule-swap, scale-shift, animacy-shift, time-shift, perspective-from-the-object).
3. **Build the world** the frame implies, deep enough to hold consistently → `references/worldbuilding.md`.
4. **Pick the dialect** the dispatch speaks in → `references/dialects.md` (the loop's substrate decides which dialects are house vs. banned).
5. **Clear the gates** before producing candidates → `references/gates.md` (consistency · one true thing · per-dialect danger zones).

Produce **N candidates**. Vary the *frame-shift move* and the *dialect* across them — that is where real range lives, not in surface wording. Each candidate is recorded under the engine's recipe (`gen_methods` includes `alien`).

## The Four Reference Domains

### 1. `references/novel-frames.md` — The Frame-Shift Moves
**Load when:** choosing *how* to make the subject novel. The five moves — rule-swap, scale-shift, animacy-shift, time-shift, perspective-from-the-object — plus the tests for picking the one that *illuminates*, and how to combine moves without losing consistency.

### 2. `references/worldbuilding.md` — Reality Design
**Load when:** the frame is chosen and the world needs depth to be held. Storytelling → worldbuilding, the gravity-field principle, lore / ritual / artifacts / inhabitants, and how a world compounds across many posts.

### 3. `references/dialects.md` — The 13 Tonal Archetypes
**Load when:** deciding the *voice* the dispatch is written in. The full tone table (purpose, mood, language, floor, ceiling, danger zone) for all 13 archetypes, plus per-archetype copy instructions. Dialects are reference, not rule: pull what serves, hybridize freely, defer to the substrate.

### 4. `references/gates.md` — Consistency, One True Thing, Danger Zones
**Load when:** before candidates ship. The consistency check, the one-true-thing gate, and the per-dialect danger zones (try-hard goth, woo-woo spiritualism, meme-for-meme's-sake, etc.).

## How Alien composes with the other lens

Alien runs as a discrete pass and hands off — never blended into one averaged prompt with another lens. Common compositions the conductor sets up:

- **Alexander → Alien (cover):** Alexander builds the carousel's structure; Alien generates the novel cover frame + house dialect; the cover is fused back in as a citizen of Alexander's structure.
- **Alien → Rubin (gate):** Alien finds the novel frame; Rubin's judgment checks it has life and lands its one true thing before QA.
- **Rubin → Alien (voice):** Rubin seeds a voice-forward piece; Alien lends a dialect to sharpen its register.

When a piece comes back `too_literal`, the conductor usually didn't pull Alien (or pulled it and the frame wasn't held). When it comes back `cliche`, the frame was stale — switch the frame-shift axis.

## Tone

Speak from inside the frame, with calm conviction in its rules. Don't pitch the novelty — inhabit it. Treat the altered law as obviously true and let the reader feel the vertigo of a place that runs on different logic but never contradicts itself. When the work feels too clean, break it. When it feels too familiar, mutate it. **Start from the frame that doesn't quite fit — but somehow lands.**
