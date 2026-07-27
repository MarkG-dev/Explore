# Switching to local — exactly what you need

## The short version

```bash
git clone -b claude/hearthstone-meta-study-av4kmh <your-Explore-remote> Explore
cd Explore
python3 hearthstone/serve.py          # -> http://127.0.0.1:8000/hearthstone
```

That is the whole switch. The data is committed, so the site works immediately with
no build step and no rebuild.

**Do not open `index.html` directly.** `file://` looks like it should work and does
not: browsers block `fetch()` from an opaque origin, so every dataset comes back
empty and the page renders with dashes. The paths are correct — the browser refuses
the read. You need HTTP, which is all `serve.py` is for.

**Do not use `python3 -m http.server` either.** It 301-redirects `/hearthstone` to
`/hearthstone/`; Vercel's rewrite does not redirect. That difference hid a real bug
(relative data paths resolved against `/` in production and 404'd, which is why the
deployed site showed no data). `serve.py` reads the rewrite table straight out of
`vercel.json` and applies it without redirecting, so local matches production exactly.

## Requirements

| Need | Version | Why |
|---|---|---|
| Python | 3.9+ (3.11 tested) | scripts + server; standard library only for serving |
| `pip install hearthstone` | any | card enums, CardXML parser, deckstring decoding |
| git | any | cloning, and the 320-build history walk |
| Disk | ~1.5 GB | 726 MB hsdata clone + ~370 MB working data |
| Node | 18+ | only if you want to run the prototype's tests |

Nothing else. No npm install for the site, no framework, no database server —
`cards.sqlite` is a file.

## What actually changes by going local

Only one thing, and it is the important one: **network access**. Every source that
knows what top-legend players play blocks datacenter IPs, so from the cloud they are
all unreachable. From your connection they are all fine.

| | Cloud | Local |
|---|---|---|
| Card data (HearthSim/hsdata via GitHub) | works | works |
| Rebuild the whole database | works | works |
| The site | works | works |
| hsreplay.net (every subdomain) | **403 at CONNECT** | works |
| vicioussyndicate.com | **Cloudflare 403** | works |
| hsguru / metastats / hearthstone-decks / hearthstonetopdecks | **blocked** | works |
| icy-veins.com | **Cloudflare 403** | works |
| reddit.com | **disallowed to the agent** | works |

So: nothing about the *build* needs to change. Going local exists purely to open the
meta-data sources.

## Run the ingest kit (the reason to be local)

```bash
cd hearthstone/ingest
# 1. put a real contact address in the UA string in common.py
pip install hearthstone

python3 fetch_reddit_competitivehs.py --limit 200 --with-comments
python3 fetch_legend_decks.py --list-sources
python3 fetch_legend_decks.py --source hearthstone-decks --pages 10 --dump
python3 fetch_legend_decks.py --all --pages 5
python3 normalize_legend.py
```

Output goes to `data/ingested/legend_decks.json`. Reload the site and a Top-Legend
section appears; until then the site says why it is absent rather than showing an
empty panel.

**Expect the first run to need fixing.** These scripts have never made a successful
request — every target host is unreachable from where they were written. Start with
`--source hearthstone-decks --pages 2 --dump` so you can see what is matching, and
check `ingest/.cache/` for what actually came back. The design should limit the
damage: it regexes Blizzard **deckstrings** (`AAEB...`) out of the page rather than
parsing anyone's DOM, so a site redesign breaks the scraped titles but not the
decklists. That decode path is verified — a real deckstring resolves to 30 exact card
names against `cards.sqlite`.

## Optional: rebuild the dataset from nothing

The data is committed, so you only need this to verify reproducibility or to refresh
after a new patch.

```bash
git clone https://github.com/HearthSim/hsdata.git ~/hsdata      # 726 MB, full history
cd Explore/hearthstone

python3 scripts/build_history.py --repo ~/hsdata --out data     # ~25 min, 3 workers
python3 scripts/extract_cards.py --carddefs ~/hsdata/CardDefs.xml --out data
python3 scripts/deep_analysis.py
python3 scripts/aggregate_decks.py                              # needs the deck archive
```

`build_history.py` is the only slow step — it walks all 320 dated client builds.
Everything downstream runs in seconds. Adjust `--workers` to your core count; the
cloud box had 4 and used 3.

### Restore the 307 MB deck archive

Committed as four gzip shards so nothing was lost:

```bash
python3 scripts/shard_decks.py --verify     # proves SHA-256 match, byte for byte
python3 scripts/shard_decks.py --restore data/research/decks_hearthpwn.ndjson
```

## Refreshing after a Hearthstone patch

```bash
cd ~/hsdata && git pull                                          # new build tags
cd Explore/hearthstone
python3 scripts/build_history.py --repo ~/hsdata --out data      # picks up new builds
python3 scripts/extract_cards.py --carddefs ~/hsdata/CardDefs.xml --out data
python3 scripts/deep_analysis.py
```

New cards, new balance changes and the updated analysis all flow from those three
commands. The site needs no changes.

## Troubleshooting

**Site loads but every number is a dash.** You opened it over `file://`, or the data
files are missing. Use `serve.py`; it warns on startup if `cards_lite.json` is absent.

**404s for `sets_spine.json`, `mechanics.json`, `issues.json`, `pro_scene.json`,
`legend_decks.json`.** Expected and harmless. Those are research outputs that land as
the agent fleets finish; the site treats them as optional and renders "still being
assembled" panels in their place.

**`hearthstone.cardxml.load()` raises `ModuleNotFoundError: hearthstone_data`.** A bug
in python-hearthstone: it imports that package even when handed an explicit path. Both
scripts drive `ElementTree.iterparse` + `CardXML.from_xml` directly to avoid it. If
you write new code against that library, do the same.

**Vercel build fails on a `functions` pattern.** A `functions` entry in `vercel.json`
matching zero files is a hard build error. That is what broke this branch's deploy —
`api/scrape-cosmos.js` and `api/magnific.js` were deleted but left in the config. If
you delete an API route, delete its entry too.
