# Massachusetts Building-Permit Data — Landscape & Ingestion Strategy

> Companion to `backend-architecture-plan.md`. Answers "where are permits for MA, and how do we make the pipeline robust." Prices/counts are vendor- or third-party-reported and marked approximate — verify before committing budget.

## 1. The landscape (the load-bearing facts)

**There is no usable statewide source of individual building permits in Massachusetts.** Permits are issued municipally by each of ~351 city/town building departments under the statewide building code (780 CMR, set by the Board of Building Regulations and Standards / BBRS). BBRS sets the code and licenses supervisors; it does **not** aggregate permit records. The state e-permitting portals (`elicensing21.mass.gov`, `eplace.eea.mass.gov`) are Accela installs for *occupational licenses* and *environmental* permits — **not** municipal building permits.

Statewide, only **aggregate counts** exist (US Census Building Permits Survey; MAPC DataCommon "Building Permits by Type and Year") — useful for market sizing, useless for leads. Boston Indicators' "The Surprising Lack of Good Permitting Data" confirms MA permit data is fragmented and inconsistently formatted.

**The beachhead insight:** **all Berkshire County towns share ONE PermitEyes instance** (`permiteyes.com/Berkshire/` · `permiteyes.us/berkshire/`) — Adams, Pittsfield, Great Barrington, Lee, etc. all feed it. So Berkshire County is **one integration, not dozens**. Statewide scale-up then reduces to "integrate the handful of dominant vendors," since a few platforms cover most towns.

## 2. Sources & systems

### A. Municipal permitting vendors (scrape/integration targets)
| System | Rough MA coverage | Access | API? | Notes |
|---|---|---|---|---|
| **OpenGov (ex-ViewPoint Cloud)** | ~110 MA communities (largest single vendor) | Public portal per town; some Socrata publishing | Internal APIs; no clean bulk public API | Highest-priority statewide integration |
| **PermitEyes (Full Circle Tech)** | Dozens of towns; **all of Berkshire on one instance** | Public search/login portal | No public API — scrape | **Your Berkshire beachhead** (+ Bedford, Falmouth, Chelmsford, Taunton…) |
| **CitizenServe** | Many towns; powers Somerville ISD | Per-town portals (`…installationID=N`) | Somerville re-publishes as open data | Predictable URL pattern by installationID |
| **Accela** | MA *state* level + some large municipalities | Accela Citizen Access | Construct/Civic API, per-jurisdiction | State portals ≠ building permits |
| **Tyler EnerGov** | Some municipalities (count uncertain) | Per-town portal | API exists, jurisdiction-gated | Confirm town-by-town |
| **Cloudpermit** | MA count not confirmed | Per-town portal | Limited | Mark uncertain |
| **In-house / none** | Many small towns (paper/PDF) | Manual / FOIA | No | Long tail; low ROI |

### B. Free open-data datasets (big MA cities) — build these, they're trivial & fresh
| City | Dataset | Platform | Access | Standard |
|---|---|---|---|---|
| **Boston** | Approved Building Permits (2009–now, ~monthly) | Analyze Boston (CKAN/Socrata) | Free CSV + API | Also a **BLDS** version |
| **Cambridge** | Building Permits (New Construction; Addition/Alteration; Electrical/Mechanical/Solar) | Socrata `data.cambridgema.gov` | Free SODA API + CSV | From ViewPoint |
| **Somerville** | Applications for Permits & Licenses (88k+, daily) | Socrata `data.somervillema.gov` | Free SODA API + CSV | From CitizenServe |
| **Framingham** | BLDS draft-stage adopter (verify) | — | — | BLDS |

### C. Commercial aggregators (buy-instead-of-scrape)
| Provider | MA coverage | API? | Rough price (uncertain) | Model |
|---|---|---|---|---|
| **Shovels.ai** | Nationwide 1,800+ juris, ~85% US pop; **verify Berkshire/W-MA depth on their map** | **Yes, modern REST** | ~$599/mo start | Best API-first fit |
| **ATTOM** | Nationwide, 158M+ properties | Yes (API/Bulk/Cloud) | Enterprise, quote-only | Property-data heavy |
| **BuildZoom** | ~90% US, 350M+ permits | Data plans | ~$500–2,000+/mo, annual | Marketplace-oriented |
| **Construction Monitor** | Selected metros | **No API** (PDF/CSV email) | Per-metro | Poor software fit |
| **PermitStack / PermitGrab / Permit Ledger** | Newer API-first | Yes | Not verified | Get quotes for price pressure |

## 3. Recommended ingestion strategy (tiered, hybrid — buy breadth, build the rest)

- **Tier 0 — Berkshire beachhead (build now, in-house):** one scraper against the shared Berkshire PermitEyes instance covers the entire launch county. This is the MVP; validate before spending on data licensing.
- **Tier 1 — Buy a national API baseline:** evaluate **Shovels.ai** first (only API-first vendor with a modern API + public-ish pricing). **Run a coverage test for Berkshire + your next 5 counties before signing** — "85% of population" skews urban, rural Western MA may be thin. Parallel-quote ATTOM + PermitStack for price pressure.
- **Tier 2 — Free open data for big cities (build, trivial):** ingest Boston, Cambridge, Somerville directly from their free Socrata/CKAN APIs — fresher and richer than any aggregator, and free. Prefer **BLDS** feeds where available.
- **Tier 3 — Vendor-templated scrapers for the long tail:** don't build 351 scrapers — build **one per platform** (OpenGov/ViewPoint → ~110 towns; CitizenServe → dozens via `installationID`; EnerGov; more PermitEyes). ~5 integrations gets most remaining coverage. Skip paper-only micro-towns until a customer needs one.

**Decision rule:** *buy* metro/high-density coverage (aggregator + free open data); *build* vendor-platform scrapers where aggregators are thin and a per-vendor template repeats — especially **PermitEyes (your moat)** and **OpenGov (the statewide majority)**.

## 4. Robustness principles

- **Normalize to BLDS.** Adopt the BLDS field schema as the internal canonical model so every source (Socrata, aggregator, scraper) maps into one shape.
- **Template by vendor, not by town.** Portal structure is shared within a vendor, so one parser + a config table of town endpoints scales far better than bespoke scrapers. *(Our `scrape/` registry + config-driven selectors already do this.)*
- **Incremental / dedup:** key on `(jurisdiction, permit_number)` + a content hash to catch amendments. Poll open-data APIs with `updated_at`; crawl scraped portals by issue-date windows with overlap. Store raw payloads for reprocessing. *(Our `stable_id` upserts already give idempotency.)*
- **Change detection:** portals break silently — add per-source row-count + schema-drift alerts ("Town X returned 0 rows for 3 days").
- **Politeness:** throttle, backoff, cache, off-peak, honor robots.txt; get a **Socrata app token** to lift free-API rate limits.
- **Legality (not legal advice):** *hiQ v. LinkedIn* (9th Cir., reaffirmed post-*Van Buren*) — scraping **publicly accessible** data (no login/auth bypass) is generally not a CFAA violation, but courts preserved **breach-of-ToS, copyright, trespass-to-chattels** theories. Prefer official open-data APIs and licensed feeds; reserve scraping for public, no-auth portals; keep it low-impact; have counsel review each portal's ToS before commercializing.

## 5. Direct URLs (free open-data)
- Boston – Approved Building Permits: `https://data.boston.gov/dataset/approved-building-permits` (CSV id `6ddcd912-32a0-43df-9908-63574f8c7e77`)
- Boston – BLDS version: `https://permits.partner.socrata.com/dataset/City-of-Boston-Building-Permits-BLDS/ga54-wzas`
- Cambridge – New Construction: `https://data.cambridgema.gov/resource/9qm7-wbdc.json`
- Cambridge – Addition/Alteration: `https://data.cambridgema.gov/Inspectional-Services/Building-Permits-Addition-Alteration/qu2z-8suj`
- Somerville – Permits & Licenses: `https://data.somervillema.gov/`
- MAPC DataCommon (aggregate counts): `https://datacommon.mapc.org/browser/datasets/384`
- Berkshire PermitEyes: `https://permiteyes.com/Berkshire/user_logins.asp` · `https://permiteyes.us/berkshire/loginuser.php`

Socrata access pattern: `https://<domain>/resource/<id>.json` (or `.csv`), e.g. `https://data.cambridgema.gov/resource/9qm7-wbdc.json`.

## 6. Verify before spending
1. **Shovels.ai actual Berkshire/Western-MA depth** — check their coverage map; "85% of US population" may under-cover rural MA.
2. **OpenGov's exact current MA town count** and whether any expose a bulk/API export.
3. **EnerGov + Cloudpermit MA counts.**
4. **All aggregator prices** (Shovels ~$599/mo, BuildZoom ~$500–2,000/mo, ATTOM quote-only are reported, not confirmed quotes).

*Sources: Mass.gov BBRS · MAPC DataCommon · Boston Indicators "bad permit data" · Analyze Boston · Boston BLDS (Socrata) · Cambridge/Somerville Open Data · permitdata.org (BLDS) · Shovels coverage/API · ATTOM · BuildZoom · OpenGov · Full Circle/PermitEyes · White & Case + EFF on hiQ/Van Buren scraping law.*
