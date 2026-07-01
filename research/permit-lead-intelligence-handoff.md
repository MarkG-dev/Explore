# Permit-Lead Intelligence for Contractors — Research Handoff

> **Purpose:** Self-contained brief so a fresh chat (or a new teammate) can pick up this business idea cold, without re-doing the research. Everything below was validated through iterative web research + two rounds of adversarial grading.
>
> **Status:** `GO-WITH-CHANGES`. Graded **B− (business) / B (launch plan)**. The analysis phase is done. The next action is **not more research** — it's a **4-week double-blind lead-quality test** (see §9).
>
> **Sourcing caveat:** Reddit and many vendor/review pages were blocked (HTTP 403) during research; a lot of pricing/coverage figures are from search-engine snippets of vendor pages, not always direct fetches. Treat load-bearing numbers (§10) as "verify before betting the company," not gospel.

---

## 1. One-paragraph summary

When someone builds or renovates, the law requires a **building permit** — a **public record** announcing that a specific, funded project is about to happen at a specific address. That's a high-intent signal for contractors. The business: **aggregate permits, score them by trade + adjacent-trade opportunity (roof permit → solar/gutter lead), enrich the owner contact, and sell the scored leads to small specialty contractors** as a better alternative to Angi/Thumbtack's hated shared-lead model. The permit data itself is a **commodity** (public, and largely already aggregated by Shovels.ai) — so the data is **not** the moat. The moat is **execution + distribution + a usage-generated data loop (won/lost outcomes) + eventual workflow stickiness**, aimed at a **low-tech, under-served, high-willingness-to-pay** market.

---

## 2. The lens we judged this with (reusable)

Every idea in the parent research effort was scored on a **6-criteria scorecard** + a **"moat paradox"** test:

**Scorecard:** (1) budget-adjacent WTP · (2) proprietary data moat (NOT public/commodity) · (3) proactive purchase habit already exists · (4) big-enough TAM · (5) low platform-dependency · (6) painkiller not vitamin. Plus: buildable by a small team.

**Moat paradox:** *Where data is public/easy → it's a commodity (an incumbent aggregates it, sells the API, price-cuts/bundles). Where data is a real moat → it's proprietary/gated (which is exactly why the incumbent charges $$$$).* Pure "aggregate public data and resell" businesses keep failing this test.

**How permit-leads scores:**

| Criterion | As a *data play* | As a *contractor-OS-via-leads* play |
|---|---|---|
| Budget-adjacent WTP | 🟡 | 🟢 (contractors spend $1.5–10k/mo on leads today) |
| Proprietary data moat | 🔴 (public) | 🔴 data — **neutralized**; moat = workflow lock-in + won/lost loop 🟢 |
| Proactive purchase habit | 🟡 | 🟢 (they actively buy leads now) |
| TAM | 🔴 (if niche/local) | 🟢 (contractor software is large) |
| Platform-dependency | 🟢 | 🟢 (you own pipeline + customer) |
| Painkiller | 🟡 | 🟢 (leads + save ~5 hrs/wk) |

**Key insight:** the idea only works when reframed off "sell aggregated data" and onto "**win a low-tech market on execution; the data was never the moat.**"

---

## 3. The industry / how permit data works

- **The signal:** a building permit = a confirmed, funded, specific project (roof, solar, pool, addition, HVAC, septic, remodel) at a known address, with the owner named. Far higher intent than an Angi form-fill.
- **The fan-out (the value):** one permit creates leads for *multiple adjacent trades*:
  - Roof replacement → solar, gutters, skylights, insulation
  - Pool → fencing (often code-required), landscaping, decking, solar/heating
  - Kitchen/addition remodel → flooring, countertops, HVAC, electrical, paint
  - New construction → landscaping, security, window treatments, pest, moving
  - Permit with **no contractor listed** (owner/DIY pull) → the homeowner may need a pro = direct lead
- **The fragmentation (why it's a business, not a weekend project):** there are **~10,000–20,000 permit-issuing jurisdictions (AHJs)** in the US (Shovels counts 10,000+; Census defines ~20,100 places). Each has its own software, format, and update cadence. ~10,000 are **fully offline** (paper/phone/in-person). No single faucet.
- **Dominant permit software:** Tyler Technologies (EnerGov), Accela (Civic Platform), OpenGov (fast-growing), CentralSquare/CityView, CitizenServe, plus regional systems (e.g., **PermitEyes** in New England). BLDS is an emerging open-data standard adopted by ~13 major cities.

---

## 4. Coverage reality (researched)

- Largest aggregators cover only ~**1,800–2,400** jurisdictions each:
  - **Shovels.ai:** ~1,800–2,000 jurisdictions = **~85% of US population**, 180M+ permits.
  - BuildZoom ~2,400 (metro-biased); Construction Monitor ~2,200; ATTOM ~2,000; PermitStack 514 (API).
- **~8,000–13,000 jurisdictions (80–90% by count) are uncovered** — BUT that long tail is only **~1% of permit activity** (tiny towns, <6 permits/yr).
- **Shovels is actively racing to close the gap** ("Project Storm": 350+ offline jurisdictions in 3 months, ~$430–860/jurisdiction).

**Conclusion:** ⚠️ **Coverage is NOT a moat.** Winning the uncovered tail is a low-value land-race against a funded incumbent. Do not build the thesis on "we cover more towns."

---

## 5. Competitive landscape (3 layers)

**Layer 1 — Raw permit data (sell data/API):**
- **Shovels.ai** — $7.64M raised, ~39 ppl, API-first for developers/proptech/climate-tech. Pricing ~$599/mo+. **Not contractor-facing.** Owns the data-breadth position. *Biggest structural threat if it ever ships a contractor product.*
- BuildZoom (marketplace + data license), Construction Monitor (supplier-focused), ATTOM, PermitStack ($19/mo+ API).
- **BuildFax** — owned by **Verisk** (acq. 2019); sells to **insurers/lenders**, not contractors. Orthogonal.

**Layer 2 — Commercial project leads / permit workflow (enterprise):**
- **Dodge Construction Network** (~$6–12k/yr/seat) & **ConstructConnect** (~$4.8–8.4k/yr; project intel from ~$129/mo) — **commercial** bidding/plans. Won't move down-market (unit economics, innovator's dilemma).
- **PermitFlow** — **$91M raised (Accel), ~124 ppl, ~$500M implied val.** AI permit **workflow automation** for **big builders** (Amazon, Lennar, Toll Brothers). **Different market** today — but **most likely to move down-market** into small-contractor space eventually. Watch closely.

**Layer 3 — Homeowner-form lead gen (the incumbent to displace):**
- **Angi / HomeAdvisor / Thumbtack** — shared-lead resale: one homeowner form sold to **2–5 contractors**, $20–150/lead, ~3–5% conversion. **FTC fined HomeAdvisor $7.2M (2023)** for misrepresenting lead quality/source and selling out-of-area/out-of-trade leads. Contractors hate it (pay to lose, junk leads, no exclusivity). This validates the pain.

**The direct competitors (small-contractor permit leads) — all THIN:**

| Player | Size/funding | Coverage | Price | Product | Weakness |
|---|---|---|---|---|---|
| **PermitGrab** | 1–3 ppl, bootstrap, no reviews | ~770–1,061 cities, ~34–48 states | **$149/mo flat** | Daily email digest + phone/license verification | Raw list; no scoring/CRM/workflow |
| **PermitVector** | 1–3 ppl, bootstrap | Texas (~6–10 metros) | $199–399/mo | Adjacent-trade daily brief (clever) | Texas-only; no workflow |
| **Permits.llc** | 1–2 ppl, pre-PMF | Massachusetts (90+ towns) | $0.01–0.10/record | Exclusive-per-county-per-niche lock | Single-state; unproven |

**Verdict:** the small-contractor-lead lane has **no entrenched, well-funded, well-reviewed player.** The lead players are thin bootstrap ops with raw-list products (no intent-scoring, no CRM, no workflow). **Beatable on execution.**

---

## 6. Why the market is winnable ("tech for a market that doesn't use it")

Sourced evidence the customer is severely under-served by software:
- **70% of contractors have no formal technology roadmap.**
- **78% of construction firms have <20 employees**; 82% of HVAC firms have <20 techs.
- Permit leads convert **12–15% (exclusive)** vs **4–5% (Angi shared)** — *(⚠️ these are generic benchmarks; must be verified for the launch market — see §8/§9)*.
- Contractors already spend **$1,500–$10,000/mo** on leads.
- The trades won by **ServiceTitan (~$9B), Jobber (~$150M+ ARR est.), Housecall Pro** — none on a data moat; all on **product + distribution + workflow lock-in** into a low-tech base. **None started with permit leads.** None of the permit-lead players have attempted workflow expansion. That's the gap.

---

## 7. The thesis & moat stack (what we're actually building)

**Thesis:** *Land with **intent-scored** permit leads (the wedge into a low-tech, high-WTP, unclaimed market), then monetize the relationship — via workflow stickiness and/or B2B — rather than competing as a raw-data reseller.*

**Moat stack (in order of what actually defends you):**
1. **Intent-scoring / adjacency classification** — "this roof permit ≈ a $15k solar+gutter job, here's the owner + why." Beats thin competitors' raw lists. *(Short-lived edge — replicable.)*
2. **Proprietary won/lost data loop** — contractors mark leads won/lost → you accumulate **conversion-outcome data** (which permit types → which jobs, by trade/geo) that is **generated by usage, owned by you, un-scrapeable, and compounds.** *(This is the "proprietary data loop" the broader search was hunting — a genuine answer to the moat-paradox, BUT see §8: it's a 2–3 year asymmetry, not an instant moat.)*
3. **Workflow lock-in** — become the contractor's system of record (lead status → follow-up → scheduling → invoicing) → switching cost. *(Real moat — but see the hard correction below.)*
4. **Hyper-local distribution + trade-relationship trust** — the actual near-term edge in a fragmented, relationship-driven market.

### ⚠️ The hard correction (from the adversarial grader — do not skip)
- The **"become the full contractor OS" endgame is ~95% likely to fail.** Workflow is brutally competitive (ServiceTitan/Jobber/Housecall Pro took 8–12 years; you'd be a B/C-tier product for ~3 years with catastrophic churn). Every lead company that tried horizontal workflow (Angi, Thumbtack, TaskRabbit) **gave up and stayed vertical.**
- **The fundable version is NOT "build ServiceTitan."** It's: **land with scored leads → prove they beat raw lists → then monetize via (a) white-labeling your lead-scoring INTO Jobber/ServiceTitan as a B2B product, or (b) staying a focused lead + marketplace vertical.** ~1/10th the engineering, with real exit paths (acquisition by the workflow incumbents).
- Therefore: **calibrate expectations** — this is a **solid bootstrappable / vertical business** if the lead-quality edge is real, **not a guaranteed venture rocket.**

---

## 8. Unsolved problems / open questions (the real risk list)

1. **⭐ Is the lead-quality edge real?** Does a *scored* lead convert meaningfully better than a *raw* list? The whole thesis rests here. → **The §9 double-blind test answers this.**
2. **⭐ Is the conversion rate real?** 12–15% is a generic benchmark. If reality is 6–8%, unit economics wobble ($99/mo ÷ ~0.5 leads/mo → CAC pressure; a $49/mo competitor undercuts). **Measure it.**
3. **Data loop is slow.** Needs ~500+ active users and 2–3 years to be statistically defensible per segment. Early data is noisy (sparse won/lost, class imbalance, permit staleness). A thin competitor could bolt on a free CRM and start their own loop. **The loop buys time to lock in workflow; it is not the moat by itself.**
4. **Contact enrichment quality.** Permits list the *property owner*, not necessarily the *decision-maker/buyer*. Owner ≠ buyer can crater conversion. Email-first.
5. **Compliance.** Outreach → **TCPA / Do-Not-Call** (business numbers mostly exempt, but hybrid numbers aren't); owning contact data → **CCPA data-broker registration** (California, ~$2–5k legal review before taking customers), GDPR if applicable. Budget compliance opex by year 2.
6. **Data-source instability.** Jurisdictions change permit software (e.g., Pittsfield MA migrating PermitEyes → OpenGov mid-2025). Scrapers break; it's an ongoing treadmill.
7. **Freshness.** A stale permit lead is worthless — the adjacent trade must reach the owner *during* the project. Speed matters.
8. **Seasonality.** Renovation/permit volume spikes in summer, dies in winter (acute in second-home markets like the Berkshires). Churn/cash-flow risk.
9. **Margin risk on expansion.** Lead-gen is 70–80% gross margin; workflow is 60–70% + more support/ops/data-liability. A $99/mo price can't fund 3 FTE of eng.
10. **PermitFlow ($91M) moving down-market** would bring brand + distribution + enterprise-grade workflow to your lane.

---

## 9. The validation plan (v3 — costed, the immediate next action)

**Berkshire County, MA is the wedge-validation lab** — NOT geography-arbitrage, NOT the destination. Chosen because it's small enough to reach *every* contractor in person and win trust fast. (~129k people, 32 towns, ~100–120 permit-focused contractors, ~600–900 permits/yr, affluent second-home renovation market. Data lives on the **PermitEyes** public portal (`permiteyes.us/berkshire`) + Pittsfield's portal — web-scrapeable, no API. National players skip these small towns.)

### ⭐ The one experiment that decides everything: 4-week double-blind lead-quality test
- Recruit ~20 local contractors in 2–3 trades (**roofing, solar, HVAC/remodel**).
- Randomly split: **10 get YOUR intent-scored leads**, 10 get a **raw PermitGrab-style list** (same underlying permits, unscored).
- Measure **conversion (lead → booked job)** at week 4.
- **Decision:** **≥2× → real wedge, proceed.** **~1.3× → lifestyle business at best.** **~1× → kill.**
- This is cheap and it is the whole ballgame. **No amount of further research substitutes for it.**

### Full validation sequence & kill gates
- **P1 (wks 1–3):** scrape PermitEyes + Pittsfield → AI classify (trade + adjacency + intent score) → enrich owner (email-first) → daily scored digest **+ simple dashboard**.
- **P2 (wks 3–8):** founder sells in person; free 30-day trial → $99–149/mo. Ship a minimal **"mark lead won/lost"** feature (starts the data loop + tests stickiness).
- **Behavioral gates (not vibes):** >70% of contractors mark ≥50% of leads won/lost by month 2; >80% renewal at month 3.
- **Hard kill gates:** 12 wks → 20 to trial; 20 wks → 5 converted to paid; 28 wks → those 5 still active, churn <5%/mo. Miss a gate → kill.
- **Cost:** ~$100–300/mo infra + enrichment; **~$1–2k total** to validate.

### Grader-mandated changes (bake in)
1. **Kill the in-house OS build** in the plan; commit to B2B-integration / vertical.
2. **Hire for distribution, not engineering** — someone with Berkshires contractor relationships. Edge in a $1k-cost geography is trust, not code.
3. Enforce the behavioral + kill gates above.
4. Run the double-blind test **first**.

---

## 10. Load-bearing facts to re-verify before committing

- Angi/HomeAdvisor FTC settlement: **$7.2M, 2023** (misrepresented lead quality/source). ✅ high confidence.
- BuildFax owned by **Verisk** (2019). ✅
- Shovels.ai: ~$7.64M raised, ~1,800 jurisdictions / ~85% population, 180M+ permits, API-first. ✅ (snippet-sourced)
- PermitFlow: **$91M (Accel Series B, Dec 2025)**, enterprise workflow. ✅ (snippet-sourced)
- PermitGrab $149/mo, PermitVector $199–399/mo (TX), Permits.llc $0.01–0.10/record (MA). ⚠️ snippet-sourced, verify.
- ~10,000–20,000 US AHJs; ~10,000 offline; incumbents cover ~1,800–2,400. ✅
- Conversion **12–15% exclusive vs 4–5% shared** — ⚠️ **generic benchmark, MUST verify for the launch market.** This is the single most important number to re-check.
- Berkshires: PermitEyes public portal + Pittsfield → OpenGov migration. ✅

---

## 11. Where we are & the immediate next step

- **Analysis phase: complete.** The idea survived two rounds of adversarial grading (D+ → B−) and earned a **GO-WITH-CHANGES**.
- **Next step is execution, not research:** build the minimal scrape+score pipeline for the Berkshires and **run the 4-week double-blind lead-quality test** (§9). That single result — does a scored lead convert ~2× a raw one — tells you whether this is a real business or a lifestyle one.
- **If it converts ≥2×:** build the won/lost loop, tighten the vertical, and plan the B2B/white-label monetization path (NOT a horizontal OS build).
- **If it doesn't:** kill it cheaply (~$1–2k, ~4–12 weeks in) and redeploy.

---

## Appendix A — How we got here (context)

This idea emerged from a broad "what business should we build" search that **killed ~8 other ideas** on the scorecard/moat-paradox, including: Etsy shop-suspension defense (proactive-WTP + platform risk), cannabis regulatory monitoring (dying customers, thin moat), AI-search/LLM-visibility monitoring (no moat, funded land-grab), SMB-acquisition deal-flow (capped TAM, contested by DealOrb), gov-contracting intel (commodity SAM.gov data), clinical-trial monitoring (commodity API), lending software (saturated/enterprise), and Faire→Etsy reselling (dual policy violation). Permit-leads was the survivor — and even it only works reframed off the data and onto execution. **The meta-lesson: stop hunting for public data to aggregate; hunt for a workflow to own or a data loop you generate.**

## Appendix B — Competitor URLs (for a fresh chat to re-verify)

- Shovels.ai · https://www.shovels.ai/ (coverage: /permit-database; jurisdictions blog: /blog/list-of-all-building-permit-jurisdictions/)
- PermitGrab · https://permitgrab.com/ (cities: /cities)
- PermitVector · https://permitvector.com/
- Permits.llc · https://permits.llc/
- PermitFlow · https://www.permitflow.com/ (Series B: /blog/permitflow-series-b)
- PermitStack · https://permit-stack.com/
- BuildZoom · https://www.buildzoom.com/ · Construction Monitor · https://www.constructionmonitor.com/ · ATTOM · https://www.attomdata.com/
- BuildFax (Verisk) · insurance vertical
- Angi/HomeAdvisor FTC action · https://www.ftc.gov/news-events/news/press-releases/2023/04/ftc-approves-final-order-against-homeadvisor-inc-deceptively-marketing-its-leads-home-improvement
- Berkshires PermitEyes public portal · https://permiteyes.us/berkshire/publicview.php
- ServiceTitan / Jobber / Housecall Pro — the "land→OS" precedents (and expansion-side competitors)
