# GitHub-sourced Hearthstone decklist datasets — provenance, coverage, biases

Assembled 2026-07-26. Everything below labelled **MEASURED** was computed by parsing the
actual files in this repo checkout, not copied from a README. Claims labelled
**RECOLLECTION / UNVERIFIED** are flagged as such.

Normalized output lives beside this file as `decks_<owner>-<repo>.ndjson`
(newline-delimited JSON, one deck per line).

## Common record schema

```json
{
  "name":      "deck title, or null if the source has none",
  "class":     "Priest | Warrior | ... (source's own casing preserved)",
  "archetype": "source archetype label, or null",
  "cards":     ["Card Name", "Card Name", ...],
  "date":      "YYYY-MM-DD or YYYY-MM-DD HH:MM:SS, or null",
  "source":    "origin site (via github repo)",
  "upvotes":   0,
  "format":    "Standard | Wild | null",
  "extra":     { "source-specific fields kept verbatim" }
}
```

`cards[]` is **expanded**: a 2-of appears twice, so `len(cards)` is the deck size.
Card names come from `dbfId` lookups against the local `HearthSim/hsdata` clone at
patch **36.0.3.247416** (35,320 entities mapped, MEASURED). That means names are the
**current** in-game names, not necessarily the era-correct ones — see the rename caveat
under dataset 2.

---

## 1. `decks_NJacobsohn-Hearthstone-Data-Analysis.ndjson`

* Repo: `github.com/NJacobsohn/Hearthstone-Data-Analysis` (master @ `b94041a`), 112 MB clone.
* Underlying source file: `data/hearthstone_decks.csv` (80.7 MB).
* Ultimate origin: **HearthPwn.com** user-submitted deck listings. The scraper appears to be
  Scrapy-based; a sibling repo `rmnvncnt/pystone` contains a HearthPwn spider with the exact
  same field names (`deck_type`, `deck_archetype`, `rating`) — plausible common ancestry,
  **UNVERIFIED** as the literal provenance.

### MEASURED counts

| metric | value |
|---|---|
| decks emitted | **346,232** |
| distinct `deck_id` | 346,232 (zero duplicates) |
| card slots seen / resolved to a real card | 10,386,960 / 10,386,960 (**100 %**) |
| deck size distribution | every single deck is exactly 30 cards |
| date range | **2013-05-23 → 2017-03-19** |
| distinct archetype labels | 76 (incl. the sentinel `"Unknown"`) |
| decks with a real archetype label | **103,608** (29.9 %); the other 242,624 were `"Unknown"` |
| output file size | 322 MB (stream it; do not `json.load` it) |

The `"Unknown"` sentinel is normalized to `archetype: null`; the raw string is preserved in
`extra.archetype_raw` so you can tell "author left it blank" apart from "field absent".

Decks by year (MEASURED): 2013 → 16,610 · 2014 → 53,175 · 2015 → 103,715 ·
2016 → 152,165 · 2017 → 20,567.

`deck_type` (MEASURED, kept in `extra.deck_type`):

| deck_type | decks |
|---|---|
| Ranked Deck | 202,375 |
| None (untagged) | 91,058 |
| Theorycraft | 19,688 |
| Arena | 14,095 |
| PvE Adventure | 9,059 |
| Tavern Brawl | 6,360 |
| Tournament | 3,597 |

**For ranked-ladder work, filter `extra.deck_type == "Ranked Deck"`.** Arena / Tavern Brawl /
PvE / Theorycraft rows are out of scope per the brief and must be dropped, not averaged in.

Class balance is remarkably flat (MEASURED): Mage 45,306 · Priest 44,307 · Paladin 42,266 ·
Warlock 38,022 · Druid 37,891 · Shaman 36,457 · Warrior 35,944 · Rogue 34,794 · Hunter 31,245.
That flatness is itself evidence this measures *posting behaviour*, not ladder representation —
real ladder class shares over 2013-2017 were never within 1.4x of each other for long.

`extra.deck_set` is a patch/era tag with 32 values (MEASURED), the largest being
Explorers 57,307 · Old Gods 49,895 · Blackrock Launch 38,900 · Gadgetzan 31,329 ·
Naxx Launch 22,283 · Yogg Nerf 22,175 · Karazhan 22,034 · TGT Launch 21,516.
This is a usable patch-era join key and is more trustworthy than `format`.

### Known biases and traps

1. **`upvotes` measures popularity of the HearthPwn *post*, not ladder winrate.**
   A deck by a known streamer (e.g. the dataset contains a `Kolento` row) accumulates
   rating from author fame and from being posted early in a patch cycle. There is no
   games-played, no winrate, and no rank information anywhere in this dataset.
2. **`format` is unreliable as a historical fact.** MEASURED: 56,224 decks whose `date`
   predates the Standard/Wild split (2016-04-26) are nonetheless labelled `Standard`.
   Standard did not exist then. The field looks like legality re-evaluated at scrape time,
   i.e. "this decklist happens to contain only cards Standard-legal as of the scrape",
   not "this deck was played in Standard". Use `extra.deck_set` + `date` for era, not `format`.
3. **Archetype labels are sparse and human-entered.** MEASURED: only 103,608 of 346,232 decks
   (29.9 %) carry any archetype at all; restricted to the 202,375 `Ranked Deck` rows it is
   **86,494 (42.7 %)**. So the majority of the corpus is unlabelled. The label is a
   HearthPwn author-selected tag, so it is noisy and its vocabulary drifts with the site's
   taxonomy (e.g. `Aggroadin`, `Renolock`, `N'Zoth Rogue` sit alongside generic `Ramp Druid`).
4. **Survivorship / recency**: HearthPwn deck pages that were deleted before the scrape are
   simply absent. The dataset also stops dead at 2017-03-19 — nothing from Un'Goro onward.
5. **Self-selection**: uploading a deck to HearthPwn requires effort, so budget/meme/theorycraft
   decks are over-represented relative to how often they were actually queued on ladder.

---

## 2. `decks_Eochs-HS-Data-Analysis.ndjson`

* Repo: `github.com/Eochs/HS-Data-Analysis` (master @ `cfeb2bb`), 5.8 MB clone.
* Underlying source file: `decks.csv` (5.5 MB), wide one-hot: 566 card-name columns
  each holding a 0/1/2 count. Normalizer melts these into `cards[]`.
* Origin: **HearthPwn.com**, restricted at scrape time to constructed decks with >= 2 upvotes.

### MEASURED counts

| metric | value |
|---|---|
| decks emitted | **2,369** (matches the README claim, verified) |
| card-name columns | 566 |
| `Updated` timestamp range | **2015-01-29 13:19:25 → 2015-04-26 12:19:14** |
| `Rating` min / median / max | 2 / 2 / 1,357 |
| decks with exactly 30 cards | 2,353 |
| malformed decks (<30 cards) | 16 — sizes 0 (x2), 1, 2, 8, 16, 18, 28 (x3), 29 (x6) |

Archetype label (`Deck Type` column, MEASURED): Control 577 · None 479 · Midrange 334 ·
Aggro 328 · Combo 283 · Tempo 135 · Theorycraft 127 · Tournament 106.
Note this vocabulary mixes an *archetype axis* (Control/Aggro/Midrange/Combo/Tempo) with a
*context axis* (Theorycraft/Tournament) in one column — 233 rows are therefore unlabelled
on the archetype axis even though they aren't "None".

Classes (MEASURED): Mage 368 · Druid 363 · Warlock 270 · Paladin 245 · Rogue 234 ·
Priest 224 · Shaman 223 · Hunter 221 · Warrior 221.

### Known biases and traps

1. **Era is a single ~3-month window: Naxx/GvG into Blackrock Mountain, early 2015.**
   The README says the filter was "updated after the Undertaker nerf, or after the Blackrock
   Mountain release"; the MEASURED `Updated` timestamps top out at 2015-04-26, so the scrape
   happened in late April 2015 and BRM decks are only ~3 weeks represented. Do not treat this
   as a BRM-meta dataset.
2. **`Updated` is a last-edited timestamp at scrape time, not a creation or play date.**
   A deck first posted in 2014 that its author touched in April 2015 carries an April 2015 date.
3. **`upvotes` (>= 2 by construction) again measures post popularity, not winrate.**
   The median is 2 — i.e. half the corpus sits exactly at the inclusion threshold, so the
   rating column has almost no discriminating power in the lower half.
4. **`format` is null for every row, deliberately.** Standard/Wild did not exist in April 2015.
5. **Two column names no longer exist in the game and were left as-is** (VERIFIED against the
   local CardDefs): `Succubus` was renamed **Felstalker** (`EX1_306`, dbf 592) and
   `Mistress of Pain` was renamed **Queen of Pain** (`GVG_018`, dbf 2172). If you join this
   dataset's `cards[]` against modern card names, those two will miss. Every other one of the
   566 columns matched a collectible card exactly (MEASURED).
6. **No deck titles and no author** — `name` is null throughout; the source CSV never had them.

---

## 3. `decks_Alfxjx-hsguru-data-spider.ndjson`

* Repo: `github.com/Alfxjx/hsguru-data-spider` (main @ `5bd6be6`), 2.2 MB clone.
* Underlying source file: `data/2024-07-01-hsguru.json` — `{title, code}` pairs, where `code`
  is a real Blizzard deckstring.
* Origin: **hsguru.com** meta/deck listings, scraped once.

### MEASURED counts

| metric | value |
|---|---|
| decks emitted | **39** |
| deckstring decode failures | 0 |
| deck size distribution | all 39 decks are exactly 30 cards |
| distinct archetype titles | 20 |
| format (from the deckstring itself) | Standard 38 · Wild 1 |
| snapshot dates available | exactly one: **2024-07-01** |

Git history checked (full clone, MEASURED): the repo has a **single commit** and has only ever
contained that one snapshot file. It is not a time series despite the date-stamped filename.

Archetype titles present (MEASURED, all 20): BFU Rainbow Excavate DK, Drilling Rogue,
Elemental Mage, Even Shaman, Even Warlock, Handbuff Paladin, Highlander Druid,
Highlander Priest, Highlander Warrior, Insanity Warlock, Mech Rogue, Odyn Warrior,
Overheal Priest, Rainbow Mage, Secret Hunter, Shopper DH, Sludge Warlock, Spell Mage,
Taunt Warrior, Tempo Druid. Class spread (from hero dbfId): Druid 10 · Warlock 8 ·
Warrior 5 · DK 3 · Rogue 3 · Mage 3 · Priest 2 · Paladin 2 · Hunter 1 · DH 1 · Shaman 1.

### Known biases and traps

1. **n = 39. This is an anecdote, not a sample.** It cannot support any percentage claim about
   the July 2024 meta. Use it as a source of *concrete, era-correct decklists with archetype
   names attached* — which the two HearthPwn datasets cannot provide for the modern era — and
   nothing more.
2. **No winrate, no games-played, no popularity field.** `upvotes` is null throughout.
   Whatever ranking hsguru applied when listing these decks was not captured by the scraper.
3. **Selection is hsguru's editorial/statistical cut**, i.e. these are decks hsguru surfaced
   as notable. `Tempo Druid` appearing 9 times and `Even Warlock` 4 times reflects how many
   variant lists were listed, which is a weak popularity proxy at best.
4. The one `Wild` deck should be excluded from Standard-only analysis; the format flag here is
   trustworthy because it is decoded from the deckstring's own format byte, not from a scraper.

---

## Repos tried and rejected (no decklist data on disk)

| repo | clone size | what is actually inside (MEASURED) | verdict |
|---|---|---|---|
| `fergunet/HSDataset` | 200 KB | **`README.md` only.** The archetype-research dataset from Mora et al., *Entertainment Computing* 43:100498 (2022) is not in git — the README points to `zenodo.org/records/10198504`. | **Unusable here.** Zenodo egress is blocked in this environment (verified: `CONNECT tunnel failed, response 403`). Worth re-fetching on a network that allows Zenodo. |
| `yawgmoth/HSPrediction` | 280 KB | 4 Python files (`learn_archetypes.py`, `analyze_log.py`, `check_replay.py`) + README. Zero data files. | Unusable. It is *code* that consumes HSReplay XML replays plus a private archetype ground-truth JSON the author never published. |
| `Zero-to-Heroes/HearthstoneJSON` | not cloned | Datamining/API scripts for **card** data. | Skipped — no decklists, and we already have the authoritative `HearthSim/hsdata` clone for cards. |
| `djdookie/Advisor` | 732 KB | C# HDT plugin source. No `.json`/`.csv`/`.xml` data payload at HEAD. Its archetype decks are fetched from hsreplay.net at runtime. | Unusable offline. |
| `fatheroctopus/hdt-deck-predictor` | 1.8 MB | C# plugin source only. No bundled meta data files. | Unusable. |
| `andburn/hdt-plugin-endgame` | 712 KB | C# plugin source; only data-ish file is a 76-byte `FodyWeavers.xml`. | Unusable. |
| `waymanglover/hearthstats` | 76 KB | HearthPwn scraper scripts + a 23-byte `requirements.txt`. No SQLite DB committed. | Unusable. |
| `aleenprd/hearthstone-topdecks-scraper` | 21 MB | `data/hstd_all_cards_merged.csv` (10.7 MB) is **per-card** data scraped from hearthstonetopdecks.com — columns `title, summary, text, type, cost, rarity, class, set, mechanics, rating, num_comments, comments, attack, health, school, durability`. Not decks. | Not a decklist set. *Potentially interesting separately*: it carries community star `rating` and raw `comments` per card, i.e. pre-release community expectation vs. actual outcome. |

`HearthSim/hsarchetypes` was attempted and does not resolve (clone prompted for
credentials → repo is private or does not exist). Not pursued further.

---

## Coverage gap you should be aware of

Stitching the three together, MEASURED era coverage is:

* **2013-05 → 2017-03** — dense (346k HearthPwn decks), but archetype-labelled on only
  29.9 % overall / 42.7 % of ranked rows.
* **2015-01 → 2015-04** — a second, independent, upvote-filtered HearthPwn slice (2,369 decks).
* **2024-07-01** — 39 decks, one day.
* **Everything else — 2017-04 (Un'Goro) through 2024-06, and 2024-07 through 2026-07 — has zero decks here.**

That is roughly **nine of Hearthstone's thirteen years with no decklist coverage at all** from
GitHub-reachable sources. Any longitudinal claim across that span cannot be grounded in these
files. The blocked-but-real candidates for closing part of the gap are the Zenodo HSDataset
(Mora et al. 2022) and the HSReplay/vS APIs, neither reachable from this environment.

## Reproduction

Scripts used (kept in the session scratchpad, not committed here):

* `build_cardmap.py` — drives `xml.etree.ElementTree.iterparse` over
  `hsdata-full/CardDefs.xml` and `hearthstone.cardxml.CardXML.from_xml` to emit a
  `dbfId -> {name, card_id, class, set, type, cost, collectible}` map.
  (`hearthstone.cardxml.load()` is broken in this environment — it imports a missing
  `hearthstone_data` package — so iterparse is driven manually.)
* `normalize_decks.py` — writes the three NDJSON files and `measured_stats.json`.

Deckstrings are decoded with `hearthstone.deckstrings.Deck.from_deckstring`.
