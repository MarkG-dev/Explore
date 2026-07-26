# Local ingest kit — getting the rest of the data in

## Why this exists

The card half of this study is complete and needs nothing from you: it is datamined
from the game client via GitHub, which the cloud environment can reach.

The **meta** half is the problem. Every source that knows what top-legend players
actually play blocks datacenter IP ranges:

| Source | From the cloud env | From your home connection |
|---|---|---|
| hsreplay.net | blocked at CONNECT | works in a browser |
| vicioussyndicate.com | Cloudflare 403 | works |
| hsguru.com | blocked | works |
| hearthstone-decks.net | blocked | works |
| metastats.net | blocked | works |
| hearthstonetopdecks.com | blocked | works |
| icy-veins.com | Cloudflare 403 | works |
| reddit.com | disallowed to the agent | works |
| web.archive.org | disallowed to the agent | works |

They are not blocking *you*. Run these scripts from a normal connection and the data
comes in. That is the whole reason to go local.

## Honest status of these scripts

**I could not test them.** Every target host is unreachable from where they were
written, so they have never made a successful request. They are written defensively —
deckstring-first parsing, on-disk caching, verbose logging — but assume the first run
needs adjustment, and use `--dump` to see what is actually matching.

The design choice that should make them durable: `fetch_legend_decks.py` does not
parse anyone's HTML structure. It regexes out Blizzard **deckstrings** (`AAEB...`) and
decodes them against the local card database. A site redesign breaks the scraped
titles; it does not break the decklists.

## Setup

```bash
cd hearthstone/ingest
pip install hearthstone          # deckstring decoding + card enums
# put a real contact address in the UA string in common.py — see "Etiquette"
```

## Run

```bash
# 1. r/CompetitiveHS — the best written record of *why* top players chose a deck
python3 fetch_reddit_competitivehs.py --limit 200 --with-comments

# 2. Top-legend decklists from the public deck sites
python3 fetch_legend_decks.py --list-sources
python3 fetch_legend_decks.py --source hearthstone-decks --pages 10 --dump
python3 fetch_legend_decks.py --all --pages 5

# 3. Fold everything into the site's data directory
python3 normalize_legend.py
```

Output lands in `hearthstone/data/ingested/`. The website reads
`data/ingested/legend_decks.json` automatically and shows a Top-Legend section when
it is present; nothing else needs changing.

## HSReplay specifically

HSReplay is the single best source of ladder statistics and there is **no legitimate
bulk export**. Their own API documentation is explicit:

> "There is no public API for global or aggregated statistics."

Their published API covers *your own* account — your replays, your collection — via
OAuth, and `fetch_hsreplay_account.py` is a stub for that if you want your own match
history in the dataset. The site's aggregate numbers are not offered as a feed, so I
have deliberately **not** written something that scrapes their internal analytics
endpoints. That would be going around a stated position, and it is the kind of thing
that gets a project blocked outright.

The supported routes, in order of how much I would rely on them:

1. **Vicious Syndicate Data Reaper** — ~350 weekly reports since May 2016, with
   archetype playrate and matchup winrate tables. The closest thing to a public
   longitudinal record of the ladder that exists. Reading and citing it is fine;
   check their terms before bulk-archiving it.
2. **HSReplay in your browser** — the tier list and archetype pages render the numbers
   you want. Manual, but legitimate, and a few snapshots go a long way.
3. **Run a deck tracker** — HDT or Firestone logs *your own* games locally, which is
   real rank-tagged data you own outright.

If you export anything by hand, drop it in `hearthstone/data/ingested/` as JSON or CSV
and tell me the shape; wiring it into the site and the analysis is quick.

## Etiquette

`common.py` enforces the following, and you should leave it that way:

- **robots.txt is read and honoured** per host; disallowed paths are skipped.
- **One request at a time per host, 2s apart.** Slow is fine — this is a few thousand
  pages once, not a live service.
- **Every response is cached** to `.cache/`, so re-running a normaliser costs zero
  requests. Delete the directory to refresh.
- **An identifying User-Agent with a contact address.** Put your real address in it.
  A scraper that identifies itself and is reachable gets tolerated; an anonymous one
  gets banned.

These sites are run by small volunteer teams and are the reason a study like this is
possible at all. Do not hammer them.

## What the data can and cannot support

Even with everything above, be careful what you claim:

- Deck sites publish what their editors chose to feature. That is a **curated sample**,
  not a random sample of the ladder.
- A `#12 Legend` tag proves one player hit that rank with that list. It says nothing
  about the deck's winrate in anyone else's hands.
- Reddit writeups are the highest-quality *reasoning* available and the lowest-quality
  *statistics*. Treat them as expert testimony, not measurement.
- Only vS and HSReplay have real sampled winrates, and neither offers a bulk feed.

The study already labels every quantitative claim with a confidence level. Anything
ingested here should keep doing that.
