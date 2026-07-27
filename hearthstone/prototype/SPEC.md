# PARRY — Rules Specification v1.0

A two-player digital CCG prototype. The one thing it exists to prove: **the defender can
affect the attacker's turn, at a moment the defender chooses, without a priority stack.**

Everything else in this document is scaffolding built to be as small as possible around
that claim.

## 0. What the measured findings force

| Finding | Consequence enforced in this spec |
|---|---|
| Stats-per-mana flat over 42 sets (2.04 → 2.07); text length +42% (50.8 → 71.9 chars, r=0.93) | Card text budget: **hard cap 60 characters, target average under 35**. Current set: avg **24.2**, max **50**. Depth lives in the Response layer, not in card text. |
| Gini 0.736 at peak, Dr. Boom in 50% of decks | **There is no neutral card pool.** Every card is faction-locked. A card cannot become a universal auto-include if it is legal in one of two decks. |
| Rotation cut ≥25%-inclusion cards from 9 to 2 | Set boundaries are a first-class field (`faction`), and the prototype ships two disjoint pools so format hygiene is structural, not a patch. |
| Secrets = 118 cards, 1.6% of pool, all ≤3 mana, zero power nerfs in 12 years | The Response layer is **7 of 38 cards (18.4%)**, present in both decks, and it is the deck-defining axis rather than a flavour layer. |
| You cannot act on the opponent's turn | Sections 5–7. |

Keyword count: **5**. Effect verbs: **16**. Both are budgets, not counts to grow.

---

## 1. Match setup

| Item | Value |
|---|---|
| Hero starting Health | 25 |
| Hero starting Armor | 0 |
| Deck size | exactly 30 |
| Copies per card | max 2 |
| Deck legality | all cards share one `faction` |
| Board width | 6 units per side |
| Hand cap | 10 (excess draws are burned, not held) |
| Mana cap | 10 |
| Guard cap | 3 |
| Hard draw limit | turn 40 → draw |

Setup order, all randomness through the seeded PRNG (§10):

1. Shuffle both decks (Fisher–Yates, §10).
2. Coin flip on the PRNG picks the first player.
3. First player draws 3. Second player draws 4 **and starts with 1 Guard.**
   (This replaces a Coin-style catch-up card. It is deliberately paid in the new currency
   so the second player's compensation is *reactive*, which is the weaker half of the
   game and therefore the safer place to put a free resource.)
4. Mulligan: each player may return any subset of their opening hand. Returned cards go
   into the deck, the deck is reshuffled, and the same number is drawn. One mulligan only,
   both simultaneous, resolved first-player-first for PRNG determinism.
5. First player begins turn 1 with Mana Max 1.

---

## 2. Core loop

A turn belongs to exactly one player, the **active player**. The other is the **defender**.

### 2.1 Start Step (no response windows open here)

In this exact order:

1. `turn_number += 1`
2. Active player's `mana_max = min(10, mana_max + 1)`; `mana = mana_max`
3. Defender's `response_used_this_turn = false`
4. Resolve the active player's **Fuse queue** in FIFO order. Each queued effect resolves
   fully, including deaths, before the next begins. Fuse effects open no response window.
5. For each of the active player's units: `attacks_used = 0`, `summoning_sick = false`
6. Active player draws 1 card (fatigue rules, §9)

### 2.2 Main Step

The active player may take any number of the following actions in any order:

| Action | Cost | Opens window |
|---|---|---|
| `PLAY_UNIT` | mana | **DEPLOY** (unless the card has Sealed) |
| `PLAY_SPELL` | mana | **CAST** (unless the card has Sealed) |
| `ARM_RESPONSE` | Guard | none, ever |
| `ATTACK` | free (1 per unit per turn) | **STRIKE** |
| `END_TURN` | — | ends Main Step |

`ARM_RESPONSE` deliberately opens no window. Arming is not a threat; letting the defender
interrupt it would spend a Response on nothing.

### 2.3 End Step

In this exact order:

1. Resolve `TURN_END>` triggers on the active player's units, left to right by board index.
2. Open the **END window** (§6). This is the defender's guaranteed last chance.
3. Convert leftover mana to Guard: `guard = min(3, guard + floor(mana / 2))`. Excess is lost.
4. For each of the active player's units with `stun > 0`: `stun -= 1`.
5. Discard down to hand cap 10 (rightmost first).
6. Pass turn.

---

## 3. Resources

### 3.1 Mana

Standard escalating pool. `mana_max` grows by 1 each of your Start Steps to a cap of 10;
`mana` refills to `mana_max` every Start Step. Unspent mana does **not** carry over as mana.

### 3.2 Guard — the public reaction resource

| Property | Rule |
|---|---|
| Visibility | **Fully public.** Both players always see both Guard totals, rendered as pips. |
| Accrual | End Step only: `floor(unspent_mana / 2)`, added to your own pool. |
| Cap | 3. Overflow is destroyed, not banked. |
| Carryover | Yes, indefinitely, until spent. |
| Spendable on | **Arming Responses. Nothing else. Ever.** |
| Other sources | Card effects (`GAIN_GUARD:n`), all faction-locked to SENTINEL. |

**Why Guard cannot be spent on anything else.** If Guard could pay for proactive cards it
becomes a second mana bar, and the whole readability win of a public pool is lost — the
opponent no longer knows what the pips *mean*. Keeping it single-purpose means the pip
count is a direct statement: *"I can arm a Response costing up to N."*

**The dominant-strategy attack, and the five things that stop it.** The red team will
argue that holding Guard open every turn is free value. It is not:

1. **The 2:1 conversion is lossy.** Two unspent mana buy one Guard. You are paying a 2-mana
   card's worth of development for one point of a currency that cannot damage, cannot
   develop, and cannot win.
2. **The cap is 3 and there is no overflow.** A player already at 3 who ends a turn with
   spare mana simply threw it away.
3. **There is exactly one Response slot (§5).** Guard beyond the cost of the single card
   you intend to arm is inert. There is no combo to save up for.
4. **Guard buys timing, not value — this is the balance invariant.** Every Response mode in
   the set is costed at or below what the same effect would cost as a mana spell. A 2-Guard
   Response does roughly what a 2-mana spell does. Since 2 Guard cost you 4 unspent mana,
   the Response layer is a *worse* rate than proactive play. You pay the premium purely for
   the right to choose the moment.
5. **A deck with no Responses is not taxed.** It spends all its mana every turn and
   generates zero Guard, which costs it nothing, because Guard was never going to do
   anything for it. The Option-5 "balance cliff" failure mode is answered by making Guard
   accrual *opt-in through play patterns* rather than automatic.

The residual risk is stated honestly in §12.

---

## 4. The card types

`cost` means **mana** for UNIT and SPELL, and **Guard** for RESPONSE. The engine switches
on `type`. There is no card that costs both.

| Type | Cost paid in | Where it goes | Text budget |
|---|---|---|---|
| UNIT | mana | the board | ≤60 chars |
| SPELL | mana | discard after resolving | ≤60 chars |
| RESPONSE | Guard | face-down in your Response slot | ≤60 chars |

---

## 5. ARMING a Response

**When.** During your own Main Step only. Never during the opponent's turn. Never during
a Start or End Step. Arming and firing can therefore never happen on the same turn.

**Cost.** The card's `cost` in Guard, paid immediately and irreversibly at the moment of
arming. This is the pre-payment. It is why no hidden resource math exists at fire time,
and therefore why there is no hesitation tell.

**Slot.** Each player has exactly **one** Response slot.

> **What if two are armed?** It cannot happen. `ARM_RESPONSE` is illegal while your slot is
> occupied. The engine rejects it in `legalActions`. This is the whole answer — no priority
> ordering rules, no "which fires first", no simultaneous-Response resolution.

**Persistence.** An armed Response **persists indefinitely** until it is fired. It does not
expire at end of turn, at end of your next turn, or ever. Rationale: use-it-or-lose-it
would force reflex-firing, which is exactly the low-skill behaviour the design is trying to
avoid; permanent arming instead makes *holding* a real strategic option, and the single
slot ensures holding has an opportunity cost (you cannot arm anything better).

**Destruction.** Nothing in the current set destroys or reveals an armed Response. If a
future card does, it must be faction-locked.

### 5.1 What is public

| Fact | Public? |
|---|---|
| Both players' Guard totals, at all times | **Yes** |
| That a Response is armed | **Yes** — a face-down card is rendered in the slot |
| The armed Response's **Guard cost** | **Yes** — printed on the card back |
| The armed Response's **identity** | **No** |
| Its available modes | **No** |
| Whether any mode is legal in the current window | **No** — see below |

This is the exact line the option study asks for. The attacker knows a response exists and
roughly how big it is, which is what makes "play around it" a real decision. What remains
hidden is *which* card, which is the bluffing surface that replaces Magic's untapped lands.

**No information leak, by construction.** A window is offered whenever a Response is armed
and unspent this turn — the offer does **not** depend on whether any mode is legal. If the
defender's armed card has no legal mode for this window, the prompt still appears and the
only enabled button is Pass. This is the fix for MTG Arena's auto-pass bug: the appearance
of a prompt carries zero information the attacker did not already have, because the armed
card was public the whole time.

---

## 6. FIRING a Response — the window model

Firing happens at **defined trigger points only**. There are four, and no others.

| Window | Opens exactly when | `TRIGGER` refers to | Pending action |
|---|---|---|---|
| `CAST` | opponent's SPELL is declared, cost paid, targets chosen — **before** any effect applies | the spell's target, if it has one | the spell |
| `DEPLOY` | opponent's UNIT is placed on the board — **after** placement, **before** its `ARRIVAL>` trigger and before it may act | the arriving unit | the arrival trigger |
| `STRIKE` | opponent declares an attack, attacker and defender chosen — **before** damage is dealt either way | the **attacking unit** | the combat damage |
| `END` | opponent's End Step, after `TURN_END>` triggers, before Guard conversion | nothing — `TRIGGER` is null | none |

Sealed cards open no `CAST` or `DEPLOY` window. Fuse resolutions and Start Step events open
no window. Effects that summon units (`SUMMON:`) open no `DEPLOY` window — only a card
played from hand does.

### 6.1 Window procedure

```
openWindow(kind, pending):
  d = defender
  if d.response_slot == null:            resolve(pending); return
  if d.response_used_this_turn == true:  resolve(pending); return
  state.awaiting = { player: d, kind: 'RESPONSE', window: kind, pending }
  # engine halts here and returns; UI submits PASS or FIRE
```

On `PASS`:
- The window closes. The pending action resolves.
- The Response **stays armed**. `response_used_this_turn` is **not** set.
- The defender may therefore be offered every subsequent window in the same turn.

On `FIRE(modeIndex, targets)`:
- Legality check: the chosen mode's `windows` must contain the current window kind or `ANY`.
  Illegal mode → the action is rejected by `legalActions` and never reaches the resolver.
- Resolve the mode's effect **immediately and completely**, including any deaths it causes.
- **Nothing may respond to a Response.** There is no stack. This is the LoR Burst
  restriction, adopted deliberately (§12 records what it costs).
- Move the Response card from the slot to its owner's discard.
- Set `response_used_this_turn = true`. No further windows open this turn.
- Then resolve the pending action, **unless** the mode contained `COUNTER` or
  `CANCEL_ATTACK`.

### 6.2 Exactly one per opponent turn

`response_used_this_turn` is reset in the *active* player's Start Step (§2.1 step 3), so
each player gets exactly one firing per opponent turn cycle. Passing does not consume it.
Firing does.

### 6.3 Interaction between COUNTER / CANCEL_ATTACK and the pending action

| Verb | Legal window | Effect on pending |
|---|---|---|
| `COUNTER` | `CAST` only | Spell is countered. Its mana stays spent. It goes to its owner's discard. No effect resolves. |
| `CANCEL_ATTACK` | `STRIKE` only | No damage in either direction. The attacker's `attacks_used` is still incremented — the attack was spent. |

`RETURN:TRIGGER` at a `DEPLOY` window returns the unit to its owner's hand before its
`ARRIVAL>` trigger fires; the trigger never happens. The mana stays spent.

`DEAL:n:TRIGGER` at a `STRIKE` window is applied **before** combat damage. If the attacker
dies to it, the attack deals no damage, but `attacks_used` is still incremented.

### 6.4 Simultaneous triggers

There is no such thing as two Responses firing at once — one slot, one firing, and only the
defender ever fires. Everything else resolves in a defined deterministic order:

- Fuse queue: FIFO, per player, resolved in the owner's Start Step.
- `TURN_END>` triggers: left to right by board index.
- `FALL>` triggers: after the current effect has fully resolved, deaths are collected and
  their `FALL>` triggers fire left to right by the board index the unit occupied. Deaths
  caused by a `FALL>` trigger are collected into a second pass, and so on, to a hard depth
  limit of 16 passes.
- Simultaneous hero deaths: **draw**.

### 6.5 Clocks are not the engine's problem

The option study specifies an 8-second decision clock, default pass, and a 90-second
match-level response bank. **None of that lives in `engine.js`.** The engine is pure and has
no wall clock. Timeouts are implemented in the UI layer, which submits an ordinary `PASS`
action when the clock expires. Same for the accessibility auto-fire ("fire if I would take
lethal") — that is a UI heuristic that submits an ordinary `FIRE` action. This keeps
`seed + action list ⇒ identical game`, which is the precondition for headless self-play.

---

## 7. What the attacker can do about it

This is the skill expression and it must be enumerable, or the mechanic is just variance.

1. **Read the pips.** Guard is public. Zero Guard means no Response can be armed next turn.
2. **Read the cost on the card back.** A 1-cost armed Response is a small effect. A 3-cost
   one is not. Cost is public precisely so this read exists.
3. **Bait it.** Only one Response fires per turn. Lead with a cheap threatening play; if it
   draws the fire, the rest of your turn is safe. This is the core attacker skill and it is
   the reason the mechanic is not "the defender wins".
4. **Play Sealed.** Sealed cards open no window at all. Vanguard buys certainty at a stat
   discount (Vault Breaker is a 3-mana 4/2 where the rate would allow 4/3).
5. **Sequence.** Attack before casting, or cast before attacking, depending on which loss
   you can afford.
6. **Starve the END window.** If you make no plays, the defender only ever sees the END
   window, where narrow modes are illegal and only the weak generic modes work.
7. **Overload it.** Two threats in one turn; only one can be answered.

---

## 8. Board rules

**Placement.** Units enter at the rightmost board index. Board width 6. `PLAY_UNIT` is
illegal on a full board. A `SUMMON:` into a full board is silently skipped.

**Summoning sickness.** A unit cannot attack the turn it arrives unless it has **Swift**.
A Swift unit's arrival-turn attack may not target the enemy hero.

**Attacking.** One attack per unit per turn (`attacks_used`, reset in Start Step; refreshed
by `REFRESH_ATTACKS`). A unit with `attack == 0` cannot attack. A unit with `stun > 0`
cannot attack.

**Combat.** Attacker deals `attack` to the target; if the target is a unit, it deals its
`attack` back to the attacker. Both applications are simultaneous, then deaths are checked.
Heroes have no attack stat and never retaliate. There are no weapons and no hero powers —
both are cut deliberately: they are homogenising, they add text, and they add nothing to
the thesis.

**Bulwark.** If the defending player controls at least one unit with Bulwark, an attack
must target a Bulwark unit. Bulwark does not restrict spells, `DEAL:` effects, or Responses.

**Ward.** The first time a unit with Ward would take damage of 1 or more, the damage is set
to 0 and Ward is removed. Ward does not prevent `DESTROY:` or `RETURN:`.

**Stun.** `STUN:` sets `stun = 2`. The value decrements by 1 at the end of the stunned
unit's controller's End Step. A unit stunned during its controller's own turn therefore
also misses the following turn, which is the intent.

**Damage and health.** Damage is persistent on units until healed. `HEAL:` cannot exceed
printed max health. A unit at `health <= 0` is destroyed. Heroes absorb damage from Armor
first, then Health; Armor has no cap and never decays on its own.

**Buffs.** `BUFF:a/h` is permanent and raises both current and max health by `h`.

---

## 9. Win, loss, draw

| Condition | Result |
|---|---|
| A hero's Health reaches 0 or less | that player loses immediately |
| Both heroes reach 0 in the same resolution | draw |
| Turn 40 completes | draw |

**Fatigue.** Drawing from an empty deck: `fatigue += 1`, then deal `fatigue` damage to your
own hero. No card is drawn. This is what actually terminates control mirrors; the turn-40
cap exists only to bound headless self-play.

**Burn.** Drawing at hand cap 10 removes the card from the deck and puts it in the discard.

---

## 10. Determinism

One PRNG, seeded, threaded through the state. No other source of randomness anywhere.

```js
// mulberry32 — exact, do not substitute
function nextRandom(state) {
  let t = (state.rngState = (state.rngState + 0x6D2B79F5) >>> 0);
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}
function randInt(state, n) { return Math.floor(nextRandom(state) * n); }

// Fisher-Yates, descending, exact
function shuffle(state, arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = randInt(state, i + 1);
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}
```

PRNG call order at setup is fixed: shuffle P1 deck, shuffle P2 deck, coin flip, then
mulligan reshuffles P1 then P2. Any deviation breaks replay.

Only one card in the set consumes randomness at all (`RANDOM_ENEMY_UNIT` is defined in the
vocabulary but currently unused). This is intentional — a prototype whose purpose is to
measure an interaction mechanic should not have its signal buried in variance.

### 10.1 Engine API

`engine.js` is pure. It imports nothing, touches no DOM, and reads no globals.

```js
createGame({ seed, decks: { A: [cardId...], B: [cardId...] }, cards }) -> State
legalActions(state)            -> Action[]        // includes RESPOND actions when awaiting
applyAction(state, action)     -> { state, events }   // returns a NEW state, never mutates
isTerminal(state)              -> null | 'A' | 'B' | 'DRAW'
```

`state.awaiting` is non-null exactly when the engine is halted mid-action waiting for a
Response decision. When it is non-null, `legalActions` returns only that player's
`PASS` / `FIRE` options. The UI renders from `events`; the engine never renders.

Action shapes:

```
{ t:'PLAY_UNIT',  card, index }
{ t:'PLAY_SPELL', card, target? }
{ t:'ARM',        card }
{ t:'ATTACK',     attacker, target }
{ t:'END_TURN' }
{ t:'PASS' }                        // only while awaiting
{ t:'FIRE', mode, target? }         // only while awaiting
```

---

## 11. Effect vocabulary

The whole engine is one `switch`. Sixteen verbs, thirteen selectors, four triggers, five
window tags. Nothing is bespoke per card.

**Statement grammar.** `VERB:arg:arg`, statements joined by `;`, evaluated left to right.

**Trigger prefix.** `ARRIVAL>`, `FALL>`, `TURN_END>`, `FUSE>` — one optional prefix on the
whole effect string. No prefix on a SPELL means "on cast".

**Targeting.** A card or mode that needs a target begins with `TARGET:<selector>;`. Exactly
one target is chosen per resolution, and every later `T` in that string refers to it. If no
legal target exists, the card is illegal to play (spells) or the trigger is skipped (units).

**Response grammar.**
`RESPONSE|<Label>@<W[,W]>><statements>|<Label>@<W[,W]>><statements>`
Exactly two modes per card. Two, not three: menu bloat is the stated failure mode of
Option 3, and two modes fit on a phone as two buttons.

### Verbs

| Verb | Semantics |
|---|---|
| `NONE` | no effect (keyword-only cards) |
| `TARGET:<sel>` | prefix; binds `T` for the rest of the string |
| `DEAL:<n>:<sel>` | n damage |
| `HEAL:<n>:<sel>` | restore up to n, capped at max health |
| `ARMOR:<n>` | your hero gains n Armor |
| `DRAW:<n>` | you draw n (fatigue/burn apply) |
| `SUMMON:<a>/<h>:<Name>[:<KW>,...]` | create a token you control; skipped if board full |
| `BUFF:<a>/<h>:<sel>` | permanent stat increase |
| `GRANT:<KW>:<sel>` | grant a keyword |
| `DESTROY:<sel>` | destroy (ignores Ward) |
| `RETURN:<sel>` | return unit to owner's hand (ignores Ward; lost if hand full) |
| `STUN:<sel>` | set `stun = 2` |
| `GAIN_GUARD:<n>` | gain n Guard, capped at 3 |
| `REFRESH_ATTACKS:<sel>` | set `attacks_used = 0` |
| `COUNTER` | CAST window only; cancel the pending spell |
| `CANCEL_ATTACK` | STRIKE window only; cancel the pending combat |

### Selectors

`T` (bound target) · `TRIGGER` (the card/unit that opened the window) · `SELF` (the source
unit) · `UNIT` · `ALLY_UNIT` · `ENEMY_UNIT` · `ANY` (unit or hero) · `ENEMY_HERO` ·
`SELF_HERO` · `ALL_UNITS` · `ALL_ALLY_UNITS` · `ALL_ENEMY_UNITS` · `RANDOM_ENEMY_UNIT`

"Ally" and "enemy" are always relative to the **controller of the effect**, which for a
Response is the defender.

---

## 12. The two decks

No neutrals. Each deck is 2 copies of 15 cards from its faction pool.

### VANGUARD — proactive

18-card pool. Cheap curve, Swift, Sealed, reach. Its Responses are cheap and offensive:
Vanguard does not want to hold Guard, so its Responses cost 1–2 and both have a mode that
does something useful at the END window.

Identity: **Sealed**. Vanguard's answer to a defender who has armed up is to play cards
that cannot be answered at all, paid for at a small stat discount.

Curve: 1×3, 2×4, 3×2, 4×3, 5×1, plus 2 Responses.

### SENTINEL — reactive

20-card pool. Bulwark bodies, hard removal, Armor, in-faction Guard generation, and the
game's only Fuse board wipe. Five Responses in the pool, three in the starter list.

Identity: **Guard economy**. Watchling, Vigilkeeper, Beacon and Bulwark Rite let Sentinel
buy Guard with stats instead of with wasted mana. Every one of them is deliberately
under-statted (Beacon is a 4-mana 2/4 against a 9-point rate) so the second economy is paid
for in board presence rather than being free.

Curve: 1×1, 2×2, 3×3, 4×3, 5×2, 6×1, plus 3 Responses.

### Measured text discipline

| | Hearthstone 2025 mean | PARRY |
|---|---|---|
| Card text length | 71.9 chars | **24.2 chars** |
| Longest card | — | 50 chars |
| Keywords in game | 90+ | **5** |

---

## 13. Open risks

These are the things a red team should attack first. They are listed because they are real,
not because they are solved.

1. **The one-per-turn haymaker convergence.** The option study names this: designing around
   "one Response per turn" pushes the metagame toward a single unanswerable big play per
   turn rather than many small threats. Fuse and Sealed are the mitigations, but Warlord
   (Sealed, refresh all attacks) is exactly the card shape that exploits it and it should be
   the first card watched in self-play.
2. **Guard hoarding at low Guard-card density.** The five defences in §3.2 argue holding is
   costly, but the 2:1 rate is an untested number. If self-play shows Sentinel routinely
   ending turns at 3 Guard with a Response already armed, the rate should go to 3:1 before
   the cap is touched.
3. **Sentinel's in-faction Guard generation is the balance cliff the study warned about.**
   Watchling/Vigilkeeper/Beacon/Rite give Guard without the tempo tax. They are under-statted
   to compensate, but that compensation is a judgement call, not a measurement.
4. **Permanent arming may produce stale boards.** A Response held for eight turns is a
   threat the attacker plays around forever. If self-play shows long stretches where neither
   player commits, the fix is a soft decay (Guard cost refunded, card returned to hand after
   N turns), not an expiry.
5. **Undercurrent's Sink mode is a 2-Guard hard tempo answer to any unit.** Bouncing before
   `ARRIVAL>` is a full two-for-one against Wardstone Oracle or Warlord. It may need to be
   3 Guard.
6. **The DEPLOY window may be strictly better than the others**, because it is the only one
   where the defender acts with complete information about what is arriving. If firing rates
   in self-play are heavily skewed to DEPLOY, the CAST and STRIKE modes are undercosted.
7. **Sealed is a balance-boundary keyword.** The study's Option 7 note applies exactly:
   designers route around classification boundaries, so anything not Sealed becomes strictly
   worse. Sealed must stay rare and stat-discounted or it eats the format.
8. **The attention tax is unmeasured and unmeasurable in a prototype.** Whether a player
   watching the opponent's turn on a phone is a cost or a feature is a live-product question.
   The prototype cannot answer it.
9. **Second player's 1 Guard may be worse than a Coin** in the aggro mirror, where neither
   player wants Guard. Going-second win rate is the first thing self-play should report.
10. **Two modes may be too few for "never a dead card".** Undercurrent and Cold Front have no
    END-legal mode and can be stranded for a whole turn against a passive opponent. That is
    intended texture, but it is the failure mode the study called out under Option 3.

---

## 14. Deviations from the option study

None substantive. Three specifications where the study left the choice open:

- **The pre-payment is made in Guard, not mana.** The study says cards are "pre-paid on your
  own turn" and separately proposes Guard as the funding pool; it does not say which
  currency the pre-payment uses. Paying in Guard makes the two halves one economy rather
  than two, and it means a Response never competes directly with a unit for the same mana.
- **Two modes per card, not the study's "2-3".** Menu bloat is a stated failure mode and two
  buttons is the mobile answer.
- **Clocks moved out of the engine.** The 8-second window and 90-second bank are UI-layer
  features. The engine cannot have a wall clock and remain deterministic.
