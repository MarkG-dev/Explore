# Hearthstone Meta Study

A longitudinal study of Hearthstone's ranked Constructed metas (2013–2026), plus a
downloadable database of every card in the game.

Live at `/hearthstone`.

## Why the dating method matters

A card's `CARD_SET` tag does **not** tell you when the card came out. Blizzard
re-buckets cards over time: the original Classic cards now report `LEGACY`, and the
Core set is re-curated every year. Fireball reports `LEGACY`, not a 2014 set. Sorting
a card database by its current set therefore mis-dates thousands of cards.

So instead of trusting the tag, this project walks **320 dated snapshots** of the
game's card definitions in chronological order and records the first build each card
ever appeared in. That is empirical, and the same pass yields the balance changelog:
every cost / attack / health / durability / armor / rules-text edit any card ever
received, with the build it happened in.

**Caveat, stated plainly:** these are the dates card data *shipped to the client*,
which runs days to weeks ahead of public release (Goblins vs Gnomes data appears
2014-12-04 for a 2014-12-08 launch). The field is named `data_first_seen` rather than
`release_date` for that reason. Researched public release dates, where available, are
carried separately as `set_release_date` / in `sets_spine.json`.

## Pipeline

Run in this order. Steps 1–2 need a local clone of
[HearthSim/hsdata](https://github.com/HearthSim/hsdata) (~726 MB with full history):

```bash
git clone https://github.com/HearthSim/hsdata.git /path/to/hsdata
pip install hearthstone            # python-hearthstone, for the enums + CardXML parser

# 1. Walk every dated build -> per-card first-appearance + full change history
python3 scripts/build_history.py --repo /path/to/hsdata --out data

# 2. Build the card database (json / csv / sqlite+FTS5 / lite index / changelog)
python3 scripts/extract_cards.py \
    --carddefs /path/to/hsdata/CardDefs.xml --out data

# 3. Optional: aggregate the HearthPwn deck archive (see data/research/.gitignore)
python3 scripts/aggregate_decks.py

# 4. Optional: power-creep measurement over the built database
python3 scripts/powercreep.py
```

Note: `hearthstone.cardxml.load()` in python-hearthstone is broken — it imports a
missing `hearthstone_data` package even when given an explicit path. Both scripts
drive `ElementTree.iterparse` + `CardXML.from_xml` directly instead.

## Scope

Collectible Constructed cards for ranked ladder. Battlegrounds (`BACON_*`) and
Mercenaries (`LETTUCE_*`) content is entirely non-collectible and so is removed by the
collectible filter; the only set excluded by name is `HERO_SKINS` (740 cosmetic hero
portraits).

Two buckets that look excludable but are kept, because they are real playable cards:

- `PLACEHOLDER_202204` — 654 Core-set reprints (`CORE_AT_003`, `CORE_AV_226`, …)
- `DEMON_HUNTER_INITIATE` — the 20 Demon Hunter launch cards

**Reprints:** the same card exists under several IDs (Fireball is `CS2_029` in Legacy,
plus `CORE_CS2_029` and `VAN_CS2_029`). Every printing is kept as its own row;
`is_reprint = 0` selects the unique cards. Current counts: **7,367 printings /
5,963 unique cards**, and **2,695 balance-change events**.

## Data files

| File | What it is |
|---|---|
| `data/cards.json` | Full records incl. per-card balance history |
| `data/cards.csv` | Flat table; list columns pipe-delimited |
| `data/cards.sqlite` | Indexed SQLite + FTS5. Tables: `cards`, `card_mechanics`, `balance_changes`, `cards_fts` |
| `data/cards_lite.json` | Columnar index the website loads |
| `data/changelog.json` | Every balance change, flat and date-ordered |
| `data/card_history.json` | Raw per-card first/last build + change list, incl. non-collectible entities |
| `data/sets_first_seen.json` | Each set → first dated client build |
| `data/build_index.json` | Every build walked, with dates and entity counts |
| `data/mechanics_index.json` | Keyword → count, first appearance, card IDs |
| `data/deck_aggregate.json` | 202,375 ranked HearthPwn decks aggregated per patch era |
| `data/manifest.json` | Provenance, counts, exclusion report |
| `data/meta/era_*.json` | Per-era meta dossiers (researched) |
| `data/research/` | Normalised decklist archives + provenance notes |

### Deck data honesty

`deck_aggregate.json` measures **deck-posting behaviour on HearthPwn**, not ladder
playrate and not winrate — the source has no games-played, rank, or winrate field. It
covers 2013-05 → 2017-03 only. Roughly nine of Hearthstone's thirteen years have no
decklist coverage from any source reachable here; `data/research/decksets_README.md`
documents that gap rather than papering over it.

## Attribution

Card data is datamined from the Hearthstone client via
[HearthSim/hsdata](https://github.com/HearthSim/hsdata). Not affiliated with or
endorsed by Blizzard Entertainment. Hearthstone is a trademark of Blizzard
Entertainment, Inc.

## Getting the rest of the data in (local ingest)

The meta half of this study is limited by network access, not by effort. Every source
that knows what top-legend players actually play — HSReplay, Vicious Syndicate, HSGuru,
hearthstone-decks.net, metastats.net, Icy Veins, Reddit — blocks datacenter IP ranges,
so none of them are reachable from a cloud environment. They work fine from an ordinary
home connection.

`ingest/` is a runnable kit for exactly that gap:

```bash
cd hearthstone/ingest
pip install hearthstone
python3 fetch_reddit_competitivehs.py --limit 200 --with-comments
python3 fetch_legend_decks.py --all --pages 5 --dump
python3 normalize_legend.py
```

Output lands in `data/ingested/legend_decks.json`, which the website picks up
automatically and renders as a Top-Legend section. Until then the site says so
explicitly rather than showing an empty panel.

Two things worth knowing before running it. **These scripts have never made a
successful request** — every target host is unreachable from where they were written,
so expect to adjust selectors on the first run; `--dump` shows what is matching. And
they parse **deckstrings, not HTML**: every deck site publishes Blizzard's `AAEB...`
codes, which decode to exact card lists against `cards.sqlite`, so a site redesign
breaks the scraped titles but not the decks.

`ingest/README.md` covers etiquette (robots.txt is honoured, one request per host every
2s, everything cached), why there is deliberately no HSReplay aggregate scraper, and
what the resulting data can and cannot support.
