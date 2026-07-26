# Handoff — running this locally, and where it should live long term

## 1. Fastest way to get it local

Everything is committed and pushed, so the quickest path is not the zip:

```bash
git clone -b claude/hearthstone-meta-study-av4kmh <your-Explore-remote> Explore
cd Explore/hearthstone
```

The zip exists for convenience, but `git pull` keeps you in sync as the research
agents keep landing files. Use the zip if you want a frozen snapshot.

### Rebuild the whole dataset from nothing

Two scripts and one clone reproduce every byte of the card database:

```bash
pip install hearthstone
git clone https://github.com/HearthSim/hsdata.git ~/hsdata     # ~726 MB, full history

cd Explore/hearthstone
python3 scripts/build_history.py --repo ~/hsdata --out data    # ~25 min, 3 workers
python3 scripts/extract_cards.py --carddefs ~/hsdata/CardDefs.xml --out data
python3 scripts/deep_analysis.py
```

`build_history.py` is the slow one — it walks all 320 dated client builds. Everything
else runs in seconds off its output.

### Restore the full deck archive

The 307 MB archive ships as four verified gzip shards, so nothing was lost:

```bash
python3 scripts/shard_decks.py --verify    # proves SHA-256 match, byte for byte
python3 scripts/shard_decks.py --restore data/research/decks_hearthpwn.ndjson
python3 scripts/aggregate_decks.py --src data/research/decks_hearthpwn.ndjson
```

### View the site

```bash
python3 -m http.server 8000        # from the Explore root
open http://localhost:8000/hearthstone/
```

It is a static page reading JSON from `data/`. No build step, no server code.

---

## 2. The thing only you can do: get the meta data in

This is the real bottleneck, and it is a network problem, not an effort problem.
Every source that knows what top-legend players actually play blocks datacenter IPs:

| Source | From the cloud env | From your home connection |
|---|---|---|
| hsreplay.net (all subdomains) | 403 at CONNECT | works |
| vicioussyndicate.com | Cloudflare 403 | works |
| hsguru.com, metastats.net | blocked | works |
| hearthstone-decks.net | blocked | works |
| hearthstonetopdecks.com | blocked | works |
| icy-veins.com | Cloudflare 403 | works |
| reddit.com | disallowed to the agent | works |

I retried HSReplay across every host — `hsreplay.net`, `www.`, `api.`, `eu.api.`,
`static.`, and `hearthsim.net` — and all six get a 403 to CONNECT from the egress
gateway. That is an organisation network policy, not something to route around.

```bash
cd hearthstone/ingest
# put a real contact address in the UA string in common.py first
pip install hearthstone
python3 fetch_reddit_competitivehs.py --limit 200 --with-comments
python3 fetch_legend_decks.py --all --pages 5 --dump
python3 normalize_legend.py
```

Output lands in `data/ingested/legend_decks.json` and the site renders a Top-Legend
section automatically. Until then it says so rather than showing an empty panel.

**These scripts have never made a successful request** — every target host is
unreachable from where they were written. They are built defensively (deckstring
regex rather than DOM parsing, on-disk caching, `--dump` to show matches), and the
decode path is verified end to end, but expect to adjust the `SOURCES` list on the
first run.

### On HSReplay specifically

There is deliberately no HSReplay scraper in the kit. Their API docs state plainly:

> "There is no public API for global or aggregated statistics."

Scraping their internal analytics endpoints would be going around a stated position,
and it is how a project gets IP-banned. Supported routes instead, best first:

1. **vS Data Reaper** — ~350 weekly reports since May 2016 with archetype playrate and
   matchup winrate tables. The closest thing to a public longitudinal ladder record.
2. **HSReplay in a browser** — the tier list pages render the numbers; a few manual
   snapshots per patch goes a long way.
3. **Run a deck tracker** (HDT / Firestone) — logs *your own* games locally. Real
   rank-tagged data you own outright.

Drop any manual export into `data/ingested/` as JSON or CSV and it can be wired in.

---

## 3. Where this should live long term

Right now it sits in `Explore`, a personal tools hub, alongside a WiFi provisioner and
a brand tool. That is fine for building; it is the wrong long-term home for three
reasons: the data directory is ~60 MB committed and will grow with every rebuild, the
audience for a Hearthstone dataset has nothing to do with the rest of the repo, and
Vercel's build already broke once on unrelated config from a sibling project.

**Recommendation: split the dataset from the site.** They have genuinely different
needs, and keeping them together compromises both.

### The dataset → Hugging Face Datasets

Free, versioned, built for exactly this, no size anxiety, and it has a built-in data
viewer plus a parquet conversion so people can query without downloading. It is also
where people actually look for datasets now.

```bash
pip install huggingface_hub
huggingface-cli login
huggingface-cli repo create hearthstone-card-history --type dataset
git clone https://huggingface.co/datasets/<you>/hearthstone-card-history
# copy data/*.json, cards.csv, cards.sqlite and the shards in; git push
```

The pitch writes itself and is genuinely novel: *every Hearthstone card dated by the
build it actually shipped in, plus 2,695 balance changes recovered by diffing 320
client snapshots, plus 346,232 ranked decklists.* Nobody has published the
balance-change reconstruction.

Kaggle is the alternative if you want a different audience; it has better casual
discovery and worse versioning.

### The site → its own repo, on Cloudflare Pages

Cloudflare Pages over Vercel here specifically because this is a static site shipping
tens of megabytes of JSON: Pages has unlimited free bandwidth, Vercel's free tier has
a 100 GB/month cap and this site serves a 5.5 MB `cards.json` to anyone who clicks
download. No functions are needed — nothing here runs server-side.

```
hearthstone-meta-study/          # its own repo
  index.html
  data/            # or point the fetches at the Hugging Face URLs
  scripts/
  ingest/
```

Keep a link from Explore's landing page. If the data lives on Hugging Face, the site
can fetch from there and the site repo stays under a megabyte.

### If you would rather not split

Least-effort acceptable version: leave it in Explore, but move the large artifacts
(`cards.sqlite`, `card_history.json`, the shards) to a GitHub Release attached to a
tag. Releases do not count against repo size, and the site can link to the release
URLs. You keep one repo and stop growing the git history on every rebuild.

### What I would not do

- **GitHub Pages** — 1 GB repo soft limit and a 100 GB/month bandwidth cap; you would
  hit the same problem later with less warning.
- **Git LFS** — solves size, but the free quota is 1 GB storage / 1 GB bandwidth and
  it makes casual `git clone` worse for everyone.
- **Committing the 307 MB raw NDJSON** — the four shards already reproduce it exactly.

---

## 4. Clear next steps

**Do first (5 minutes each)**

1. `git pull` — the deploy fix is in; the Vercel build was failing on
   `api/scrape-cosmos.js` being referenced in `vercel.json` after the file was deleted.
   Confirm the deployment is green.
2. Open `/hearthstone` and click through the tabs, especially **Deep analysis**.

**Do next (an evening)**

3. Run the ingest kit from home. This is the single highest-value thing left — it is
   the only way top-legend deck data enters the study. Expect to fix selectors.
4. Decide the hosting split above. If you want the dataset published, Hugging Face
   first; the site can follow.

**Ongoing / still running here**

5. Three agent fleets are mid-flight: era-by-era meta research (2 of 13 dossiers in),
   the design brief with a red-team pass, and the playable prototype. They write into
   `data/meta/`, `brief/` and `prototype/`. The site already renders those sections as
   pending and fills them in when the JSON lands, so pulling mid-flight is safe.

**Known limits, so you do not rediscover them**

- Deck coverage is dense for 2013-05 → 2017-03 and empty for roughly nine of the
  thirteen years. Only the ingest kit or manual exports close that.
- `data_first_seen` is when card data shipped to the client, days-to-weeks before
  public release. It is not a release date and is deliberately not named one.
- The archetype-diversity curve (2 → 47) is substantially HearthPwn's tag vocabulary
  growing, not the meta diversifying. Gini and staple count are the trustworthy
  diversity signals.
- Nerf latency is right-censored; only the *floor* (same-week emergency nerfs appear
  from 2018) is a defensible reading.
