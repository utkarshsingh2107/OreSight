# OreSight — खनिज दृष्टि
### A Reserve-to-Rake Digital Twin for MOIL's Manganese Operations
**Smart India Hackathon — Complete Technical & Product Blueprint**

*Problem Statement: "Using AI/ML and Space Technology to Identify Manganese Reserves and Overcome Production Shortfalls" (Ministry of Steel / MOIL Limited)*

---

## How to read this document

| Marker | Meaning |
|---|---|
| ✅ **VERIFIED** | Fact confirmed from a cited public source |
| 🔶 **ASSUMPTION** | Reasonable inference — must be validated with MOIL if you reach later rounds |
| 🔷 **RECOMMENDATION** | My engineering/product judgement, not a fact |
| ⚠️ **REALITY CHECK** | Something most SIH teams will get wrong. Read these twice. |

---

# PART A — UNDERSTANDING & RESEARCH

## 1. Understand the Problem

### 1.1 The problem in plain language

MOIL is India's largest manganese ore producer. Every year it must answer two questions:

1. **"How much manganese do we actually have, and where exactly is it?"** (the *stock* question)
2. **"How much can we actually dig out and dispatch this month/quarter/year?"** (the *flow* question)

Today MOIL answers Q1 with manual geological surveys, borehole drilling and expert interpretation, and Q2 with spreadsheets built on last year's production records. Both answers are slow to produce, updated infrequently (often annually), and — crucially — **they are not connected to each other**. The result is a recurring mismatch: the plan says 1.65 lakh tonnes this month, the mine delivers 1.42 lakh tonnes, and the reasons are only understood in the *post-mortem* meeting, not in advance.

### 1.2 What is the organisation actually asking for?

Read the statement carefully. It asks for **three capabilities in one dashboard**:

| # | Capability | Nature | Time horizon |
|---|---|---|---|
| A | **Identify and map reserves** more accurately using surface + sub-surface indicators | *Descriptive / geological* | Years |
| B | **Predict production shortfalls** from equipment downtime, weather, blasting delays | *Predictive / operational* | Days–Quarters |
| C | **Suggest corrective actions** — reschedule, re-optimise blasting, redeploy equipment | *Prescriptive / decision* | Hours–Weeks |

⚠️ **REALITY CHECK #1 — the single most important insight in this document.**
A and B are on completely different time scales and use completely different data. Most SIH teams will build a pretty prospectivity map (A) and a separate LSTM forecast (B), bolt them into one React app, and call it a solution. Judges from the Ministry of Steel will immediately see that these are two disconnected demos in one browser tab.

**The winning move is to make A and B mathematically dependent on each other.** The bridge is this: *a reserve is not production until it is physically accessible.* A block of ore that is (i) below the current development level, (ii) behind an un-driven cross-cut, (iii) in a pit sector that floods for 90 days a year, or (iv) reachable only by an LHD that is 82% likely to fail this quarter — is a *geological* reserve but not a *plannable* one.

That bridge is our core product concept: **Effective Accessible Reserve (EAR)** — see §4.5. Build that, and you have a single coherent product instead of two demos.

### 1.3 Users and stakeholders

| Stakeholder | Role | What they need from the system | Frequency of use |
|---|---|---|---|
| **Mine Manager** (per mine, 11 mines) | Statutory head of the mine under Mines Act 1952 | Daily/weekly: which faces to work, which equipment is at risk, will I hit my monthly target | Daily |
| **Mine Planning Engineer / Surveyor** | Builds stope plans, level plans, monthly schedules | Block model, accessible reserve per level, revised schedule proposals | Weekly |
| **Chief Geologist / Exploration Head** | Reserve declaration, drill programme design | Prospectivity maps, drill-hole prioritisation, UNFC classification, resource-to-reserve conversion | Monthly/Quarterly |
| **GM (Production) / Regional Head** | Owns the regional production target | Cross-mine shortfall risk, where to redeploy assets between mines | Weekly |
| **Director (Production) / CMD, HQ Nagpur** | Owns annual corporate target and board commitments | One-screen national view, P10/P50/P90 annual outlook, "reserve at risk" | Monthly |
| **Maintenance / Excavation Engineer** | Equipment availability & utilisation | Failure risk ranking, service scheduling, spares pre-positioning | Daily |
| **Marketing / Dispatch** | Grade-wise commitments to ferro-alloy & steel customers | Grade-blend feasibility, dispatch forecast by grade | Weekly |
| **Regulator — IBM / DGMS / State DGM** | Statutory oversight, MCDR returns, safety | Auditable reserve statements, statutory returns, mine-plan compliance | Annual/On-demand |
| **Ministry of Steel / Ministry of Mines** | Policy, import substitution, critical minerals | National supply outlook, import-dependence risk | Quarterly |

🔷 **RECOMMENDATION:** In your SIH presentation, name **five** of these explicitly with a persona card each. Teams that say "users = MOIL" lose points against teams that say "the Mine Manager at Balaghat opens this at 6:45 AM before the first shift briefing."

### 1.4 The current process (as practised in Indian underground/opencast metal mining)

🔶 **ASSUMPTION** (based on standard Indian mining practice under MCDR 2017 and MEMC Rules 2015; validate with MOIL if possible):

**Reserve estimation chain:**
```
Regional geological mapping (GSI / in-house)
  → Surface trenching, pitting, geophysical survey
  → Exploratory boreholes (core drilling), core logging
  → Lab assay (Mn%, Fe%, SiO2, Al2O3, P, moisture)
  → Manual/CAD sectional interpretation (level plans, cross-sections)
  → Volume × bulk density × recovery factor = tonnage
  → Classification per UNFC (G1–G4 confidence, feasibility & economic axes)
  → Annual Return to Indian Bureau of Mines under MCDR
```

**Production planning chain:**
```
Annual corporate target (top-down, from MoU with Ministry)
  → Break-up per mine (based on last year's actuals + capacity)
  → Monthly targets per mine (flat or seasonally adjusted by thumb-rule)
  → Weekly stope/face allocation by Mine Manager (experience-driven)
  → Daily shift plan on paper / whiteboard
  → Daily production report (DPR) — often a spreadsheet emailed up the chain
  → Monthly review meeting: explain the variance
```

### 1.5 Why the current process is insufficient

| Weakness | Consequence |
|---|---|
| **Drilling is slow and expensive.** A single deep borehole in the Sausar belt can take weeks and lakhs of rupees. Coverage is therefore sparse. | Reserve confidence is patchy. Grade surprises at the face. |
| **Interpretation is expert-dependent and non-reproducible.** Two geologists draw two different ore-body outlines from the same sections. | No uncertainty quantification. A single deterministic tonnage number that nobody can attach a confidence interval to. |
| **Reserve figures are updated annually, plans are made monthly, mining happens per shift.** | The plan is built on a picture of the ore body that is up to 12 months stale. |
| **Production planning uses averages, not distributions.** "Balaghat does 22,000 t/month" ignores that monsoon months do 14,000 t. | Systematic over-promising in Q2 (Jul–Sep) and scrambling in Q4. |
| **Constraint data lives in silos** — equipment logs with maintenance, blasting records with the mining engineer, rainfall in nobody's system, manpower with HR. | No single model can see that the shortfall was caused by *rain → haul road condition → dumper cycle time*, not by the face crew. |
| **Variance analysis is retrospective.** | By the time you know you missed, the month is over. Correction costs 3× more. |
| **No feedback loop from actual mined grade back to the block model** (reconciliation). | Model bias compounds year on year. |

### 1.6 Root causes (not symptoms)

1. **Sparse, expensive sub-surface information.** Physics problem — you cannot see through rock cheaply.
2. **Deterministic thinking in a stochastic system.** Single-number reserves, single-number targets, in a domain where everything is a distribution.
3. **Data fragmentation.** No unified, time-stamped, geo-referenced operational data layer.
4. **Decoupling of the geological model from the operational plan.** The two live in different software, different departments, different time bases.
5. **Absence of an explicit constraint model.** Nobody has written down, as equations, what actually limits tonnage at each mine.
6. **Human bandwidth.** 11 mines × ~30 working faces × daily decisions is beyond a spreadsheet.

⚠️ **REALITY CHECK #2:** Note that only root cause #1 is a "find more ore with AI" problem. Root causes #2–#6 are *systems and decision-science* problems. The SIH statement's own "Expected Solution" line asks for a **dashboard showing predicted reserves, production trends, risks of shortfall** — i.e. the organisation is itself telling you that the deliverable is a **decision system**, not a magic ore-finder. Weight your effort accordingly: **~30% reserve mapping, ~40% shortfall prediction, ~30% prescriptive action.**

### 1.7 Ambiguities in the problem statement (state these explicitly in your presentation — it shows maturity)

| Ambiguity | Why it matters | How we resolve it |
|---|---|---|
| **"Satellite inputs such as rainfall, soil moisture, vegetation index, land temperature"** are listed under the *reserve identification* objective. | ⚠️ These four variables are **surface climate/vegetation variables. They do not see manganese ore at depth.** Rainfall does not correlate with a gondite ore body 200 m below ground. | We split satellite usage honestly into two roles: **(a) geological remote sensing** — ASTER/Sentinel-2 SWIR band ratios, iron-oxide and clay indices, DEM/structural lineaments, and *geobotanical stress* (metal-tolerant vegetation anomalies over mineralised gondite outcrops) — for reserve *targeting*; and **(b) climate/operational variables** — IMERG rainfall, SMAP/Sentinel-1 soil moisture, MODIS LST, NDVI — as **production-constraint drivers**, which is where they genuinely add value. Saying this out loud will differentiate you. |
| "Identify reserves" — new greenfield discovery, or better delineation of known ore bodies? | Completely different models, data and value. | We do **both, at two scales**: regional prospectivity (brownfield lease-scale extension targets) *and* mine-scale 3D block modelling. §6.2. |
| "Production shortfall" — vs monthly target? vs annual MoU? vs geological potential? | Determines the loss function. | We define it against **the approved monthly/quarterly plan**, with rollups to annual. Configurable. |
| No data is supplied with the statement. | You cannot train on real MOIL borehole assays or DPRs — they are commercially sensitive. | We build a **physically-calibrated synthetic data generator** for the demo, plus real ingestion adapters for open data (GSI/NGDR, Sentinel, IMERG). We label synthetic data as synthetic *in the UI*. §13.3. |
| "Optimizing blasting" — safety-critical. | An AI that prescribes blast parameters is a regulatory and safety minefield (DGMS, Explosives Rules 2008). | We **do not** auto-generate blast designs. We optimise *blast scheduling and sequencing* and flag delay risk. §6.7 explains where we deliberately refuse to use AI. |

### 1.8 The problem, defined precisely (this is your problem statement slide)

> **MOIL's production plans are built on a geological model that is annually-updated, deterministic and disconnected from the operational constraints that actually govern tonnage. Consequently, reserve figures overstate what is plannable, and shortfalls are diagnosed after they occur rather than prevented.**
>
> We will build a system that (i) maintains a continuously-updated, *probabilistic* 3D reserve model fused from boreholes, geophysics and Earth-observation evidence; (ii) converts that into an **Effective Accessible Reserve** by applying a learned operational constraint model; (iii) forecasts production as a *distribution*, attributing shortfall risk to named, actionable causes; and (iv) prescribes and simulates corrective actions before the shortfall happens.

---

## 2. Existing Solutions & Market Research

### 2.1 Category 1 — Commercial mine planning & resource modelling software

| Product | What it does | How it works | Strengths | Limitations | Why it doesn't solve this PS |
|---|---|---|---|---|---|
| **Datamine Studio RM / MineSched** (Datamine, UK) | Industry-standard geological modelling, block modelling, resource estimation, scheduling | Desktop CAD + geostatistics (kriging, SGS); rule-based scheduler | Deep geostatistics, auditable, JORC/UNFC-ready | Very expensive licences; desktop-bound; expert-only; **no ML, no weather, no live equipment data**; scheduling is deterministic | Produces a static reserve number. Has no concept of shortfall probability or EO data. |
| **Seequent Leapfrog Geo + Edge** | Implicit 3D geological modelling from drill-holes | Radial basis function implicit surfaces | Extremely fast, beautiful 3D geology, industry trusted | Modelling only; no production forecasting; no operations; cost | Solves ~25% of objective A, 0% of B and C |
| **Micromine / Maptek Vulcan / Deswik** | Equivalent full-stack mine planning suites | Block models + interactive scheduling + haulage sim | Mature, well-supported in India | Same as above — geology & plan, not risk & prediction. Deswik adds good scheduling but requires a planner to drive it | No probabilistic shortfall forecasting, no EO integration, no prescriptive AI |
| **Micromine Nexus / Datamine Discover** | Data management layers | Central repositories | Governance | Still not predictive | — |

**What we learn:** don't try to rebuild a block-modelling engine — it's a decade of work. Instead **consume** block-model outputs and add the layer these tools structurally lack: probabilistic operational coupling. Also: adopt their *data schemas* (collar/survey/assay/lithology drill-hole tables) so our system is interoperable, not a silo. That interoperability point is a strong SIH answer to "how would MOIL actually adopt this?"

### 2.2 Category 2 — Fleet management & mine operations systems

| Product | What it does | Strengths | Limitations | Gap for this PS |
|---|---|---|---|---|
| **Modular Mining DISPATCH**, **Wenco**, **Hexagon MineOperate** | Real-time truck/shovel dispatch optimisation in large opencast mines | Proven tonnage gains (5–15% on haulage) | Built for **large opencast** fleets; heavy hardware retrofit; very costly; **8 of MOIL's 11 mines are underground** where GPS does not work | Doesn't address reserves at all; underground applicability limited |
| **Sandvik OptiMine**, **Epiroc Mobilaris, Newtrax** | Underground fleet tracking, equipment health, positioning | Genuinely solves UG telemetry | Requires OEM equipment + underground network (Wi-Fi/LTE/leaky feeder) — big capex | Telemetry only; no reserve model, no planning intelligence |
| **SAP PM / Maximo** | Maintenance management | Enterprise-grade | Reactive/scheduled maintenance, not predictive by default | Feeds our system; doesn't replace it |

**What we learn:** these are our **data sources**, not our competitors. Design explicit adapters (SAP PM, DPR spreadsheets, OEM CSV exports). Also learn: MOIL's underground-heavy mine mix means "IoT everywhere" is an unrealistic assumption for a hackathon — see §13.

### 2.3 Category 3 — Indian government & PSU digital initiatives

| System | What it does | Strengths | Limitations | Relevance |
|---|---|---|---|---|
| **Mining Surveillance System (MSS)** — IBM + BISAG + MoM, launched 2016 | Satellite-based detection of illegal mining outside lease boundaries; raises "triggers" to state authorities ✅ **VERIFIED** ([Ministry of Mines / press coverage](https://geospatialworld.net/news/india-use-surveillance-satellite-system-monitor-illegal-mining/)) | Proves EO-based mine monitoring works at national scale in India, institutionally accepted | **Regulator-facing and compliance-only**; detects unauthorised *area* change, not production volume, grade or shortfall; reported to have low follow-through on alerts | Strongest precedent to cite. Our system is the *producer-facing* counterpart: same satellite backbone, opposite user and purpose. |
| **National Geoscience Data Repository (NGDR) — geodataindia.gov.in** & **GSI Bhukosh** | Open national geoscience data portal: geology, geophysics, geochemistry, borehole data ✅ **VERIFIED** | **This is your primary free real dataset.** Real Indian geoscience layers, downloadable | Coverage/format heterogeneity; not mine-operations data | Use it. Demoing on *real Indian geoscience data* rather than toy data is a major credibility win. |
| **IndiaAI × GSI Hackathon on AI-Driven Mineral Targeting (2025)** — 39,000 km² in Karnataka & Andhra Pradesh, targets included **manganese**; ₹10L first prize ✅ **VERIFIED** ([PIB](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2112453)) | Government-run AI mineral prospectivity challenge | Confirms the Ministry of Mines actively wants ML prospectivity | It covers **targeting only** — not production | ⚠️ Cite this to show the reserve-mapping half is *government-validated as a direction*, then argue your differentiation is the production-coupling half. |
| **Khanij Bazaar / MSTC e-auction, Mining Tenement System (MTS)** | Mineral block auctions, tenement lifecycle | Transactional backbone | Administrative, not analytical | Integration story for Phase 2 |
| **Bhuvan / Bhoonidhi (NRSC), MOSDAC (SAC)** | ISRO geoportals and EO data ordering; Bhuvan exposes some APIs and IMD weather products ✅ **VERIFIED** ([Bhuvan API](https://bhuvan-app1.nrsc.gov.in/api/), [Bhoonidhi](https://bhoonidhi.nrsc.gov.in/)) | Indian sovereign EO — politically important for an SIH pitch | Bhoonidhi ordering is not a low-latency programmatic pipeline; API coverage is limited | 🔷 Use **Sentinel/Copernicus + GPM IMERG for the working pipeline** and **Bhuvan/Bhoonidhi/Cartosat as the sovereign-data story + high-res DEM**. Say clearly you designed for both. |
| **Coal India OITDS / CMPDI systems** | Operator-independent truck dispatch, coal | Domestic precedent for PSU adoption | Coal-specific, opencast, dispatch-only | Adoption-pathway evidence |

### 2.4 Category 4 — AI-first mineral exploration companies

| Company | What it does | How | Strengths | Limitations / Why not sufficient |
|---|---|---|---|---|
| **KoBold Metals** (US; Gates/Bezos-backed, raised ~$491M) ✅ **VERIFIED** ([coverage](https://www.deeplearning.ai/the-batch/how-kobold-metals-uses-ai-to-find-rare-earth-minerals/)) | ML over integrated geoscience datasets ("TerraShed"/"Machine Prospector") to find copper, Ni, Li deposits; reports significant copper discoveries | Bayesian + ML models over geophysics, geochem, historical drilling; buys/leases ground and drills | Proves ML prospectivity works commercially at scale | **Closed, proprietary, exploration-only.** They *own and explore* ground; they do not solve a producing PSU's monthly shortfall. Not licensable to MOIL. |
| **Earth AI** (Australia) | ML targeting + owns its own drilling rigs to close the loop fast | End-to-end target→drill | Fast validation loop | Exploration only; greenfield; proprietary |
| **VerAI Discoveries, Minerva Intelligence, GoldSpot Discoveries** | AI prospectivity / geological reasoning | Various ML + knowledge-graph approaches | Some explainability work (Minerva) | Exploration only, Western asset focus |
| **Fleet Space (ExoSphere)** | Ambient noise seismic tomography + satellite backhaul for rapid sub-surface imaging | Genuine "space technology" for exploration | Hardware service, expensive; not software MOIL can deploy | Great to *cite* as the state of the art in the "space tech" framing |
| **IBM Watson / Microsoft AI for Earth mining pilots** | Generic ML platforms applied to mining | Cloud scale | Not a product; integration heavy | — |

### 2.5 Category 5 — Open-source projects & libraries you should actually use

| Project | What it gives you | Use in our build |
|---|---|---|
| **GemPy** | Open-source implicit 3D structural geological modelling (Python) | Build 3D geology surfaces from synthetic/real drill-holes for the demo |
| **PyKrige / GSTools / SciKit-GStat** | Ordinary/Universal Kriging, variogram fitting, Gaussian random fields | The *baseline* resource estimator and uncertainty simulation |
| **GeostatsPy / SGeMS concepts** | Sequential Gaussian Simulation | P10/P50/P90 tonnage realisations |
| **PySAL, verstack, `sklearn` GroupKFold** | Spatial cross-validation (spatial block CV) | ⚠️ Critical: prevents the #1 error in prospectivity ML — spatial autocorrelation leakage inflating accuracy to a fake 98% |
| **Google Earth Engine (Python API) / `sentinelhub-py` / `pystac-client` + `odc-stac`** | Free, planetary-scale access to Sentinel-1/2, Landsat, ASTER, MODIS, GPM IMERG, SMAP | The entire EO ingestion layer |
| **`rasterio`, `rioxarray`, `xarray`, `geopandas`, `shapely`, `pyproj`** | Raster/vector geoprocessing | Feature engineering |
| **`statsmodels`, `LightGBM`, `sktime`, `Nixtla StatsForecast/MLForecast`, `HierarchicalForecast`** | Time-series forecasting + **hierarchical reconciliation (MinT)** | The shortfall engine |
| **`SHAP`** | Model explanation | The "why" panel — decisive for PSU trust |
| **Google OR-Tools / PuLP + CBC / HiGHS** | MILP optimisation | The prescriptive scheduler |
| **`lifelines` / `scikit-survival`** | Weibull & Cox survival models | Equipment failure risk |
| **MapLibre GL JS + deck.gl + TiTiler/`rio-tiler`** | Web maps + COG raster tiles, no licence cost | The dashboard map |
| **Three.js / react-three-fiber** | 3D block model in the browser | The visual "wow" |
| **OpenDroneMap / WebODM** | Drone photogrammetry → DSM → stockpile volumes | Phase 2 volume reconciliation |

### 2.6 Category 6 — Research literature (cite 4–6 of these in your deck)

- **Ore-grade estimation, ML vs kriging.** Comparative studies on iron ore show ML (RF/GBM/SVR) can match or beat Ordinary Kriging on point accuracy but frequently **under-represent spatial continuity and variance**. Practical conclusion: use kriging/SGS for the resource statement, ML for fast re-estimation, domaining and confidence classification. ([Minerals, MDPI, iron ore grade study](https://doi.org/10.3390/min15020131); [Minerals 10(10):847, combined ML algorithms](https://doi.org/10.3390/min10100847))
- **Mineral prospectivity mapping (MPM) with ML.** Established literature on RF/SVM/CNN and **positive–unlabelled learning** for MPM; the recurring methodological warning is class imbalance + spatial leakage.
- **InSAR/Sentinel-1 for open-pit monitoring & slope stability.** Time-series InSAR is a demonstrated technique for mine deformation monitoring; coherence loss is a usable *mining-activity* proxy. ([ISPRS Archives XLVIII-1/W2-2023, 945](https://isprs-archives.copernicus.org/articles/XLVIII-1-W2-2023/945/2023/); Remote Sensing, InSAR coherence in open-pit coal mines)
- **Multi-sensor EO for open-pit mine monitoring** — recent review confirming combined optical + SAR + thermal workflows. ([ScienceDirect, JAG 2025](https://sciencedirect.com/science/article/pii/S1569843225004819))
- **Indian Minerals Yearbook — Manganese Ore chapters (IBM)** — authoritative national reserve/resource figures and grade classifications, useful to calibrate your synthetic data realistically. ([IBM IMYB 2020 Manganese](https://ibm.gov.in/writereaddata/files/04272022163406Manganese_2020.pdf))

### 2.7 Master comparison table

| Solution | Reserve mapping | 3D block model | EO/satellite | Production forecast | Shortfall *probability* | Equipment risk | Prescriptive actions | Cost | Underground-capable | India-ready |
|---|---|---|---|---|---|---|---|---|---|---|
| Datamine / Vulcan / Micromine | ✅ Strong | ✅ Strong | ❌ | ⚠️ Deterministic schedule | ❌ | ❌ | ❌ | 💰💰💰 | ✅ | ⚠️ Licence cost |
| Leapfrog Geo | ⚠️ Modelling only | ✅ Strong | ❌ | ❌ | ❌ | ❌ | ❌ | 💰💰💰 | ✅ | ⚠️ |
| Modular DISPATCH / Wenco | ❌ | ❌ | ❌ | ⚠️ Real-time only | ❌ | ⚠️ | ✅ Dispatch-level | 💰💰💰 | ❌ Mostly OC | ⚠️ |
| Sandvik OptiMine / Newtrax | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ⚠️ | 💰💰 | ✅ | ⚠️ Capex |
| MSS (IBM/BISAG) | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | Govt | n/a | ✅ |
| NGDR / Bhukosh | ⚠️ Data only | ❌ | ⚠️ Data | ❌ | ❌ | ❌ | ❌ | Free | n/a | ✅ |
| KoBold / Earth AI | ✅ Strong | ⚠️ | ✅ | ❌ | ❌ | ❌ | ❌ | Not licensable | n/a | ❌ |
| Excel + tribal knowledge (**the real incumbent**) | ⚠️ | ❌ | ❌ | ⚠️ Averages | ❌ | ❌ | ⚠️ Human | Free | ✅ | ✅ |
| **OreSight (ours)** | ✅ | ✅ (light) | ✅ Dual-purpose | ✅ Probabilistic | ✅ **Unique** | ✅ | ✅ **Unique** | Low/OSS | ✅ | ✅ |

⚠️ **REALITY CHECK #3:** Your true competitor is not Datamine. It is **the incumbent spreadsheet plus a 30-year veteran Mine Manager's intuition** — and that veteran is often right. Your pitch must be "we make his intuition explicit, auditable, and available to the other 10 mines," not "AI replaces him." PSU judges respond very strongly to this framing.

---

## 3. Identify the Gap

### 3.1 What is missing in existing solutions

1. **No product couples the geological model to the operational constraint model.** Reserves live in Datamine; constraints live in SAP/Excel; nobody computes *accessible* reserve.
2. **No probabilistic production forecasting in Indian metal mining.** Everyone forecasts a number; nobody forecasts a distribution with a shortfall probability.
3. **Earth observation is used for policing, not for planning.** MSS watches the *boundary*. Nobody uses rainfall/soil-moisture/LST to *derate* a mine's planned capacity in advance.
4. **No causal attribution of shortfall.** Post-mortems say "due to heavy rain"; nobody quantifies "63 mm of rain over 3 days historically costs Dongri Buzurg 1,850 ± 400 t over the following 6 days."
5. **No prescriptive layer.** Even the best fleet systems optimise *within today*; nobody re-optimises the *month* under uncertainty.
6. **Nothing is regulator-shaped.** UNFC/MCDR-aligned outputs are produced manually. An auto-drafted, auditable reserve statement is a huge unglamorous win.
7. **UX is built for specialists.** Every serious tool needs a trained geologist. Nothing exists for the Mine Manager at 6:45 AM on a phone with 2 bars of signal.

### 3.2 The single biggest gap (your one-sentence gap slide)

> **There is no system that tells a mine manager, *before* the month begins, how much of the declared reserve he can actually realise, what will stop him, with what probability, and what he should do about it.**

### 3.3 Five candidate approaches, honestly ranked

| # | Approach | Description |
|---|---|---|
| **A1** | **Pure AI prospectivity mapper** | ML over GSI/NGDR + EO layers → manganese prospectivity heatmap for the Nagpur–Bhandara–Balaghat belt. Drill-target ranking. |
| **A2** | **Pure production forecasting & anomaly dashboard** | Time-series ML on DPRs + weather + equipment logs → shortfall alerts and driver attribution. |
| **A3** | **Satellite mine-activity monitoring platform** | Sentinel-1/2 change detection, pit/dump footprint growth, stockpile proxies, InSAR deformation → compare against declared production. |
| **A4** | **⭐ Reserve-to-Production Digital Twin (OreSight)** | Probabilistic 3D block model → **Effective Accessible Reserve** via a learned constraint model → probabilistic production forecast with attribution → MILP prescriptive re-scheduling → single dashboard. EO feeds both halves. |
| **A5** | **LLM "mining copilot"** | RAG over mine plans, DGMS circulars, DPRs, geological reports; natural-language Q&A and report generation. |

**Scoring (1–10, 10 = best):**

| Criterion | A1 | A2 | A3 | **A4** | A5 |
|---|---|---|---|---|---|
| Innovation | 6 | 5 | 6 | **9** | 4 |
| Feasibility in 36h | 8 | 9 | 6 | **6** | 8 |
| Real-world impact for MOIL | 5 | 7 | 4 | **10** | 4 |
| Fit to *all three* PS objectives | 3 | 4 | 3 | **10** | 2 |
| Dev time | 8 | 9 | 5 | **5** | 8 |
| Cost | 9 | 9 | 7 | **8** | 5 |
| Scalability | 7 | 8 | 8 | **9** | 7 |
| Technical depth judges can probe | 7 | 6 | 7 | **10** | 3 |
| Demo "wow" | 6 | 4 | 8 | **9** | 6 |
| Differentiation from other SIH teams | 4 | 3 | 6 | **10** | 2 |
| **Weighted total** | 63 | 64 | 60 | **86** | 49 |

**Why not the others:**

- **A1 alone** ignores two-thirds of the problem statement and competes directly with the government's own IndiaAI-GSI hackathon output. You will look derivative.
- **A2 alone** is a generic time-series dashboard. Every third SIH team builds one. No moat.
- **A3 alone** is beautiful but MOIL's mines are mostly underground — satellites see almost nothing of the actual production. It is a supporting act, not the show.
- **A5 alone** is a chatbot on documents. Judges are saturated with these in 2026 and it does not "identify reserves" or "predict shortfalls" in any rigorous sense. ⚠️ Keep an LLM only as a *narration layer* on top of real numbers (§6.6), never as the core.

### 3.4 🔷 RECOMMENDED APPROACH: **A4 — OreSight, the Reserve-to-Production Digital Twin**

with **A5 downgraded to a thin, grounded reporting assistant** and **A3 folded in** as (i) an EO constraint feed and (ii) an opencast reconciliation check.

---

# PART B — THE SOLUTION

## 4. Proposed Solution

### 4.1 Product

**Name:** **OreSight** (खनिज दृष्टि — *"vision into the mineral"*)
**Tagline:** *From reserve to rake — see the ore, and see what stands between you and it.*

**One-line pitch:**
> OreSight is a reserve-to-production digital twin that fuses borehole, geophysical and satellite data into a probabilistic 3D manganese reserve model, then continuously computes how much of that reserve is actually **producible** under real equipment, weather and development constraints — forecasting shortfalls weeks in advance and prescribing the corrective schedule.

**Core value proposition (say this to judges in 15 seconds):**
> *"Every mining company knows how much ore it has. Almost none know how much it can actually get out next month, or why not. OreSight closes that gap — and it turns 'the monsoon hurt us' from a post-mortem excuse into a number you can plan against 30 days early."*

### 4.2 Target users (primary → secondary)

1. **Mine Manager & Mine Planning Engineer** — daily/weekly operator (primary)
2. **GM Production / Regional Head** — cross-mine reallocation (primary)
3. **Chief Geologist / Exploration** — reserve confidence & drill targeting (primary)
4. **Maintenance Engineer** — equipment risk (secondary)
5. **HQ Director / Ministry dashboard** — portfolio view (secondary)
6. **IBM/DGMS auditor** — read-only, auditable reserve statement (tertiary)

### 4.3 Main use cases

| ID | Use case | Actor | Trigger |
|---|---|---|---|
| UC-1 | View probabilistic reserve (P10/P50/P90) by mine, level and block | Geologist | Monthly |
| UC-2 | Rank next drill-hole locations by expected information gain | Geologist | Exploration planning |
| UC-3 | See regional prospectivity heatmap for lease-extension targets | Exploration Head | Quarterly |
| UC-4 | Get 30/60/90-day production forecast with shortfall probability | Mine Manager, GM | Weekly + on demand |
| UC-5 | Understand *why* a shortfall is predicted (ranked drivers, SHAP) | Mine Manager | On alert |
| UC-6 | Receive ranked corrective actions with expected tonnage recovery | Mine Manager | On alert |
| UC-7 | Run "what-if": heavier monsoon / LHD-3 fails / extra shift | Planning Engineer | Ad hoc |
| UC-8 | Re-optimise the month's face/equipment schedule | Planning Engineer | Monthly + on alert |
| UC-9 | Reconcile planned vs mined vs dispatched tonnage & grade; update the model | Surveyor | Monthly |
| UC-10 | Verify opencast activity/footprint against declared output using EO | HQ/Audit | Monthly |
| UC-11 | Auto-draft MCDR/UNFC reserve statement | Geologist | Annual |
| UC-12 | Grade-blend feasibility for customer commitments | Marketing | Weekly |

### 4.4 User journey (the Mine Manager, Balaghat, a Tuesday in July)

```
06:45  Opens OreSight on phone. Home card:
       "BALAGHAT — Month-to-date 9,140 t of 22,000 t target.
        P(shortfall > 5%) = 0.71  ▲ up from 0.44 last week"
06:46  Taps the risk card. Driver panel:
       1. Rainfall 128 mm forecast next 7 days → haulage derating −18%   (SHAP +1,340 t risk)
       2. LHD-04 failure probability 0.63 in 14 days (2,180 running hrs) (SHAP +780 t risk)
       3. Level 6 SE cross-cut development 9 days behind → Stope 6-3 not ready (SHAP +610 t risk)
06:48  Taps "Suggest actions". Three ranked, simulated options:
       A. Shift 2 crews from Level 6 SE to Level 5 NW (ready, Mn 42.1%)  → +1,450 t, P(shortfall) 0.71→0.42
       B. Pull LHD-04 service forward to 8 Jul (planned 24 Jul)          → +520 t,  P → 0.61
       C. Advance the Stope 5-2 blast round from 14 Jul to 9 Jul         → +380 t,  P → 0.66
       A+B+C combined → P(shortfall) = 0.19
06:52  Selects A + B. Clicks "Apply to plan".
       System writes a revised weekly schedule, notifies the maintenance
       engineer and the two shift in-charges, and logs the decision
       with its full model justification to the audit trail.
07:00  Shift briefing — he has a printed one-pager with the reasoning.
[T+30d] Reconciliation: actual 21,380 t vs 22,000 t. Without intervention the
        model's counterfactual said 19,600 t. Recovery logged: +1,780 t.
        Model retrains on the new data point.
```

⚠️ That last line — **the counterfactual and the retraining loop** — is what makes this a system rather than a dashboard. Put it on a slide.

### 4.5 The core concept: **Effective Accessible Reserve (EAR)**

This is your claimable innovation. Define it precisely:

For every block *b* in the 3D block model, at time *t*, over horizon *H*:

```
EAR(t, H) = Σ_b  T_b · G_b · A_b(t,H) · R_b · C_b

where
  T_b  = tonnage of block b            (volume × bulk density)
  G_b  = grade-qualification indicator (Mn% within saleable spec, or blendable)
  A_b  = ACCESSIBILITY  ∈ [0,1]  — probability the block can be physically
         reached and mined within horizon H, given:
           • development status of the connecting drive/cross-cut/ramp
           • required lead time (development metres remaining ÷ advance rate)
           • ventilation / ground-support readiness (UG)
           • stripping ratio & bench readiness (OC)
  R_b  = EXTRACTION & RECOVERY factor — stope recovery, dilution, ore loss
  C_b  = CONSTRAINT AVAILABILITY ∈ [0,1] — expected capacity factor from the
         operational model:
           C_b = f(equipment availability, weather derating, manpower,
                   blasting cadence, haulage & dispatch capacity)
```

- Standard reserve statements give you `Σ T_b · G_b · R_b`.
- **OreSight gives you that, times `A_b · C_b`, with a full probability distribution over both.**
- The difference — **"Reserve at Risk"** — is the headline number no existing product produces.

🔷 **Present EAR as a funnel graphic:** *Total Resource → Proved+Probable Reserve → Accessible Reserve (A) → Effective Accessible Reserve (A×C) → Committed Plan.* Judges will remember this one visual more than anything else in your deck.

### 4.6 Feature breakdown

#### ✅ MVP — must be built and working for the SIH prototype

| # | Feature | Why it's MVP |
|---|---|---|
| M1 | **Multi-mine map view** (MapLibre) — 11 MOIL mines with lease polygons, status, live KPI chips | Orientation, credibility, 10 min of work |
| M2 | **3D block model viewer** — rotate/slice/filter blocks by grade & confidence; level plans | The visual anchor of "reserve" |
| M3 | **Probabilistic resource estimation** — Ordinary Kriging + Sequential Gaussian Simulation → P10/P50/P90 tonnage & grade per level | The rigorous core of objective A |
| M4 | **Regional prospectivity map** — PU-learning/XGBoost over stacked EO + geophysics layers, with spatial block CV and an honest uncertainty layer | Objective A, second scale; uses real GSI/NGDR data |
| M5 | **EO ingestion pipeline** — Sentinel-2 indices, GPM IMERG rainfall, MODIS LST, Sentinel-1 soil-moisture proxy, per mine, as a time series | The "space technology" requirement, done for real |
| M6 | **Probabilistic production forecast** — LightGBM quantile regression, 30/60/90 days, per mine, hierarchically reconciled to corporate total | Objective B core |
| M7 | **Shortfall probability + driver attribution** — P(output < target) and SHAP-ranked causes | The differentiator. **Do not skip.** |
| M8 | **Equipment failure risk** — Weibull/GBM survival model per major asset | A named, actionable driver |
| M9 | **Weather derating curves** — learned distributed-lag response of output to rainfall, per mine | Genuinely novel + explainable |
| M10 | **Prescriptive engine** — MILP re-allocation of faces/crews/equipment, with expected tonnage recovery per action | Objective C. The "wow". |
| M11 | **What-if simulator** — sliders for rainfall, equipment status, crew count; recompute in < 3 s | Best live-demo device you have |
| M12 | **EAR / Reserve-at-Risk funnel** | Your signature metric |
| M13 | **Role-based auth + audit log** | Government-grade seriousness |
| M14 | **Alerts** (in-app + email/webhook) | Closes the loop |

#### 🔶 Phase 2 (3–9 months, post-hackathon)

- P1. **Drone photogrammetry ingestion** (WebODM) → true stockpile & pit volume, monthly reconciliation
- P2. **Sentinel-1 InSAR time-series** for dump/pit-wall deformation and slope-stability early warning
- P3. **Grade-blend optimiser** across mines to meet customer specs (ferro-grade / SMn / battery-grade feedstock)
- P4. **Live IoT/telemetry adapters** — OEM CAN-bus, winder SCADA, weighbridge, underground LTE
- P5. **Drill-hole planning by expected information gain** (Bayesian optimisation over the kriging variance field)
- P6. **Auto-drafted MCDR annual return & UNFC classification report**
- P7. **Mobile-first offline PWA** for underground/low-connectivity shift reporting
- P8. **Hindi / Marathi UI** (Bhashini API) and voice-based DPR entry
- P9. **Dispatch & rake-planning integration** (railway rake availability as a constraint)
- P10. **Safety module** — DGMS incident correlation with production pressure

#### 🔵 Future / long-term

- F1. **Federated national platform** — the same engine for NMDC (iron), HCL (copper), state DGMs; a "Mineral Production Assurance Grid"
- F2. **Critical-minerals extension** — apply the prospectivity engine to REE, Ni-PGE, Li under the National Critical Mineral Mission
- F3. **Physics-informed neural networks / geological priors** in the interpolation (structure-aware, honouring fold geometry of the Sausar Group)
- F4. **Ambient-noise passive seismic** (Fleet Space–style) or airborne EM as new evidence layers
- F5. **Carbon & water accounting** per tonne, ESG reporting
- F6. **Digital twin with real-time simulation** of ore flow from face to rake
- F7. **Automated reserve-to-market price optimisation** with Khanij Bazaar / e-auction integration

### 4.7 What makes this genuinely innovative (no buzzwords)

1. **EAR as a computed, probabilistic quantity** — a reserve number conditioned on operations. Not in any commercial product we found.
2. **Hierarchical probabilistic forecasting with reconciliation** (face → mine → region → company), so the CMD's number and the Mine Manager's number are guaranteed consistent. Solves a real organisational pain, not just a modelling one.
3. **Learned weather-derating curves from satellite rainfall** — works at mines with no rain gauge, quantifies monsoon impact per mine instead of a company-wide fudge factor.
4. **Causal-style attribution + counterfactual accounting** — every alert carries its drivers; every applied action is scored against a counterfactual. This creates the evidence base that makes a PSU keep using the tool in year two.
5. **Optimisation under uncertainty**, not point-estimate optimisation — MILP over quantile scenarios (a light stochastic programme).
6. **Regulator-shaped outputs** — UNFC/MCDR alignment makes it adoptable, not just impressive.

### 4.8 Direct mapping: PS requirement → OreSight feature

| PS says | OreSight delivers |
|---|---|
| "Identify and map manganese reserves more accurately using surface and sub-surface indicators" | M3 (sub-surface: boreholes → kriging/SGS 3D block model) + M4 (surface: ASTER/Sentinel-2 spectral indices, geophysics, lineaments → prospectivity) |
| "using geological data, historical production, equipment performance, and satellite inputs" | All four are first-class data sources: `boreholes`, `production_daily`, `equipment_events`, `eo_timeseries` |
| "rainfall, soil moisture, vegetation index, land temperature" | M5 + M9 — ingested as features and turned into per-mine derating curves |
| "Predict shortfalls … equipment downtime, weather, blasting delays" | M6, M7, M8 — each of the three named causes is an explicit modelled driver |
| "Suggest corrective actions — adjusting mine schedules, optimizing blasting, re-deploying equipment" | M10 — MILP produces exactly these three action classes |
| "user-friendly dashboard showing predicted reserves, production trends, risks of shortfall" | M1, M2, M12 + the risk/driver/action panels |

---

## 5. Detailed System Architecture

### 5.1 Architecture diagram (text)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                  USERS                                        │
│  Mine Manager (mobile/PWA) · Planning Engineer · Geologist · GM · HQ · Auditor │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │  HTTPS / TLS 1.3
┌───────────────────────────────────▼──────────────────────────────────────────┐
│  PRESENTATION LAYER                                                           │
│  React 18 + TypeScript + Vite  |  TailwindCSS + shadcn/ui                     │
│  MapLibre GL JS (2D map) · deck.gl (large geo layers) ·                       │
│  react-three-fiber/Three.js (3D block model) · ECharts/Recharts (charts)      │
│  TanStack Query (server state) · Zustand (UI state) · PWA + service worker    │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │  REST + WebSocket (live alerts)
┌───────────────────────────────────▼──────────────────────────────────────────┐
│  API GATEWAY / EDGE                                                           │
│  Nginx (TLS termination, gzip/brotli, static)                                 │
│  → rate limiting, request ID injection, CORS, WAF rules                       │
└───────────────────────────────────┬──────────────────────────────────────────┘
┌───────────────────────────────────▼──────────────────────────────────────────┐
│  APPLICATION LAYER — FastAPI (Python 3.11), Pydantic v2, async                │
│  ┌──────────────┬───────────────┬──────────────┬──────────────┬────────────┐ │
│  │ auth_svc     │ geo_svc       │ ops_svc      │ forecast_svc │ optim_svc  │ │
│  │ JWT, RBAC,   │ mines, blocks,│ production,  │ predictions, │ scenarios, │ │
│  │ audit        │ boreholes,    │ equipment,   │ drivers,     │ actions,   │ │
│  │              │ prospectivity │ blasts, EO   │ alerts       │ schedules  │ │
│  └──────────────┴───────────────┴──────────────┴──────────────┴────────────┘ │
│  report_svc (PDF/XLSX exports)   ·  notify_svc (email/webhook/WS)             │
└───────┬───────────────────────────────────────────────────┬──────────────────┘
        │                                                   │
        │ (sync, <300ms)                                    │ (async jobs)
        │                                          ┌────────▼─────────────────┐
        │                                          │ Redis (broker + cache)   │
        │                                          │ Celery workers           │
        │                                          │  · eo_ingest             │
        │                                          │  · nightly_retrain       │
        │                                          │  · kriging/SGS runs      │
        │                                          │  · MILP solve            │
        │                                          │  Celery Beat (schedules) │
        │                                          └────────┬─────────────────┘
        │                                                   │
┌───────▼───────────────────────────────────────────────────▼──────────────────┐
│  AI/ML ENGINE  (Python library + model registry, callable sync or async)      │
│  ┌───────────────────────┬───────────────────────┬─────────────────────────┐ │
│  │ PRISM                 │ PULSE                 │ NUDGE                   │ │
│  │ Reserve intelligence  │ Production risk       │ Prescriptive optimiser  │ │
│  │ • Variogram + OK      │ • LightGBM quantile   │ • MILP (OR-Tools/HiGHS) │ │
│  │ • Seq. Gaussian Sim   │   forecast (P10/50/90)│ • Scenario evaluation   │ │
│  │ • XGBoost/PU-learning │ • MinT hierarchical   │ • Counterfactual scoring│ │
│  │   prospectivity       │   reconciliation      │ • Greedy fallback       │ │
│  │ • Spatial block CV    │ • Weibull/GBM         │                         │ │
│  │ • Confidence → UNFC   │   equipment survival  │                         │ │
│  │                       │ • Distributed-lag     │                         │ │
│  │                       │   weather derating    │                         │ │
│  │                       │ • SHAP attribution    │                         │ │
│  └───────────────────────┴───────────────────────┴─────────────────────────┘ │
│  MLflow — experiment tracking, model registry, versioned artefacts            │
└───────┬──────────────────────────────────────────────────────────────────────┘
        │
┌───────▼──────────────────────────────────────────────────────────────────────┐
│  DATA LAYER                                                                   │
│  PostgreSQL 16                                                                │
│    + PostGIS      → mines, leases, boreholes, blocks, geometries              │
│    + TimescaleDB  → production_daily, equipment_events, eo_timeseries         │
│                     (hypertables + continuous aggregates)                     │
│  MinIO / S3       → COG rasters, block-model binaries, drone imagery,         │
│                     model artefacts, generated PDFs                           │
│  Redis            → cache (forecast responses, tile metadata), job broker     │
│  TiTiler          → dynamic COG → XYZ tiles for the web map                   │
└───────┬──────────────────────────────────────────────────────────────────────┘
        │
┌───────▼──────────────────────────────────────────────────────────────────────┐
│  INGESTION / EXTERNAL DATA                                                    │
│  Copernicus Data Space / Sentinel Hub → Sentinel-1 (SAR), Sentinel-2 (optical)│
│  NASA GES DISC / GPM IMERG           → rainfall (0.1°, half-hourly)           │
│  NASA SMAP / Sentinel-1 derived      → soil moisture                          │
│  MODIS / Landsat (LST, NDVI)         → land surface temperature, vegetation   │
│  ASTER (SWIR)                        → mineral/alteration band ratios         │
│  GSI Bhukosh / NGDR (geodataindia)   → geology, geophysics, geochem, boreholes│
│  ISRO Bhuvan / Bhoonidhi             → Cartosat DEM, Indian EO (sovereign)    │
│  IMD                                 → station rainfall & forecasts           │
│  MOIL internal (adapters):                                                    │
│     DPR spreadsheets (XLSX/CSV) · SAP PM export · lab assay CSV ·             │
│     survey/CAD (DXF) · Datamine/Micromine block-model export                  │
└───────┬──────────────────────────────────────────────────────────────────────┘
┌───────▼──────────────────────────────────────────────────────────────────────┐
│  PLATFORM / OPS                                                               │
│  Docker + Docker Compose (hackathon) → Kubernetes (production)                │
│  GitHub Actions CI/CD  ·  Prometheus + Grafana  ·  Loki (logs)                │
│  Sentry (errors)  ·  pgBackRest (DB backup)  ·  Vault/Doppler (secrets)       │
│  Deployment target: NIC MeghRaj / MeitY-empanelled cloud, or on-prem MOIL DC   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Component-by-component justification

**Frontend — React + TypeScript + Vite.** TypeScript matters here because the domain objects (block, borehole, forecast quantile) are complex and a 6-person team will otherwise lose hours to shape mismatches. Vite for sub-second HMR during a 36-hour build.

**MapLibre GL JS (not Google Maps / Mapbox).** Free, open-source, no API key, no billing surprise during a demo, and works with self-hosted tiles — which matters because a mining PSU may run this air-gapped. 🔷 *Say this in the deck: "no proprietary map dependency, deployable inside MOIL's own network."*

**deck.gl** for anything over ~10k features (block model points, prospectivity grid) — canvas/WebGL rendering instead of DOM.

**react-three-fiber / Three.js** for the 3D block model. Render blocks as an `InstancedMesh` — 200,000 blocks at 60 fps. ⚠️ Do **not** render 200k individual meshes; that will kill your demo laptop.

**FastAPI (Python).** Chosen over Node because the entire ML/geoscience stack (`scikit-learn`, `LightGBM`, `PyKrige`, `rasterio`, `geopandas`, `SHAP`, `OR-Tools`) is Python. One language across backend and ML removes an entire integration surface — a serious advantage with 36 hours. Async support handles concurrent map/tile requests; automatic OpenAPI docs saves the frontend dev hours.

**PostgreSQL + PostGIS + TimescaleDB.** One database instead of three:

- *PostGIS* gives real spatial types, spatial indexes (GiST), `ST_3DDistance`, `ST_Within` for lease-boundary checks — essential and free.
- *TimescaleDB* gives hypertables + continuous aggregates for the production and EO time series; a "monthly tonnage by mine" query that would take seconds becomes milliseconds.
- Relational integrity matters because this is auditable government data.
🔷 A NoSQL store is *not* recommended: the domain is highly relational (mine→level→stope→block→assay) and you need transactional consistency for audit.

**MinIO / S3.** Rasters and model artefacts do not belong in Postgres. Store Cloud-Optimised GeoTIFFs (COGs) in object storage and serve tiles with **TiTiler** — this is the modern, cheap, correct pattern for web-delivered EO.

**Redis + Celery.** Kriging over a 200k-block grid, an SGS run with 100 realisations, an EO download, or a MILP solve can take 30 s – 10 min. These must never block an HTTP request. Celery Beat schedules the nightly EO pull and weekly retrain.

**MLflow.** Model registry + experiment tracking. In the demo this lets you say "here are the 14 experiments we ran and the metric that made us pick this model" — which is a *very* strong answer when a technical judge asks "how do you know your model is good?"

**Keycloak (production) / FastAPI-JWT (hackathon).** RBAC with the roles in §11. For the hackathon a simple JWT + role claim is sufficient and honest; state Keycloak/SSO as the production path.

**Prometheus + Grafana + Loki + Sentry.** Uptime, latency, model-drift metrics (PSI on input features, rolling MAE on forecasts). 🔷 Mention **model drift monitoring** explicitly — very few SIH teams do, and it signals production thinking.

**Docker Compose → Kubernetes.** One `docker compose up` must bring the entire stack alive on a judge's machine. That is a demo insurance policy as much as an architecture choice.

### 5.3 Data flow, end to end

```
[Nightly 02:00 IST]
 Celery Beat → eo_ingest task
   → query Copernicus/GEE for new Sentinel-2 & Sentinel-1 scenes over 11 lease AOIs
   → cloud-mask (s2cloudless), compute NDVI, NDMI, iron-oxide & clay ratios,
     Sentinel-1 VV/VH backscatter (soil-moisture proxy)
   → pull GPM IMERG rainfall & MODIS LST for each AOI centroid
   → write COGs to MinIO, aggregated values to TimescaleDB (eo_timeseries)

[Daily 06:00 IST]
 forecast_refresh task
   → assemble features: 28-day production lags, rolling means, calendar,
     equipment availability, EO variables (with 0–14 day lags),
     blast counts, development metres, manpower
   → LightGBM quantile models (α = 0.1/0.5/0.9) predict D+1 … D+90 per mine
   → HierarchicalForecast MinT reconciliation across face→mine→region→company
   → compute P(cumulative < target) by Monte-Carlo over quantile-fitted dists
   → SHAP values per mine for the top drivers
   → write to `forecasts`, `forecast_drivers`; raise `alerts` above threshold
   → WebSocket push + email digest

[On demand — user clicks "Suggest actions" or moves a what-if slider]
 optim_svc → build MILP from current EAR, equipment availability distribution,
             derating curves, development schedule
   → solve with HiGHS/CBC (target < 3 s; warm start + time limit)
   → return ranked actions each with Δtonnage and Δ P(shortfall)
   → user applies → writes `schedule_versions` + `audit_log`

[Monthly]
 reconciliation task
   → compare planned vs mined vs weighbridge-dispatched tonnage & grade
   → compute model bias per mine/level; feed correction factors back to PRISM
   → EO check for opencast: pit-footprint change vs declared volume → flag anomalies
```

---

## 6. AI/ML — Detailed Design

⚠️ **REALITY CHECK #4:** The fastest way to lose a technical judge is to say "we used a deep learning model." The fastest way to win one is to say "we used ordinary kriging because with 340 boreholes a neural network overfits, and here is the spatial cross-validation that proves it." **Justify every model choice against a simpler baseline.**

### 6.1 Where AI genuinely helps — and where it must not be used

| Task | Use AI? | Why |
|---|---|---|
| Spatial interpolation of grade between boreholes | ✅ Geostatistics (kriging/SGS) — *the* right tool, with ML as a comparator | Sparse, spatially autocorrelated data with a known covariance structure |
| Regional prospectivity from multi-layer evidence | ✅ ML (PU-learning + gradient boosting) | High-dimensional, non-linear, no closed-form model |
| Production time-series forecasting | ✅ ML (gradient boosting with quantile loss) | Many interacting drivers, non-linear, seasonal |
| Equipment failure risk | ✅ Survival analysis / GBM | Censored time-to-event data — classic |
| Weather → capacity response | ✅ Statistical (distributed-lag regression) | Interpretable, small-data-friendly. Deep learning here would be indefensible. |
| Attribution of shortfall causes | ✅ SHAP over the forecast model | Trust and adoption |
| Schedule re-optimisation | ❌ **Not ML — use MILP.** | It's a constrained combinatorial problem with hard feasibility rules. RL would be unexplainable, data-hungry and unsafe. 🔷 *Say this explicitly — refusing to use AI where it doesn't belong is a maturity signal.* |
| **Blast design (burden, spacing, charge, delay)** | ❌ **NEVER** | Safety-critical, DGMS-regulated under the Mines Act 1952 and Explosives Rules 2008. We optimise blast *timing/sequencing within an approved design*, and flag delays. Do not let your team put "AI-optimised blasting parameters" on a slide. |
| Statutory reserve classification (final sign-off) | ❌ AI proposes, **Recognised Qualified Person signs** | MEMC Rules require a competent person. Our system produces a draft with evidence; a human certifies. |
| Ground-control / slope stability decisions | ⚠️ Advisory only (Phase 2 InSAR) | Life safety; always human-in-the-loop |
| Report narration | ✅ LLM, tightly grounded (§6.6) | Convenience, never inference |

### 6.2 PRISM — Reserve intelligence

#### 6.2.1 Scale A — Regional prospectivity (targeting new/extension areas)

**Study area (demo):** the Sausar Group manganese belt — Nagpur & Bhandara districts (Maharashtra) and Balaghat district (Madhya Pradesh). ✅ MOIL's 11 mines lie in this belt.

**Grid:** 30 m × 30 m cells over the AOI.

**Evidence layers (features):**

| Layer | Source | Rationale |
|---|---|---|
| ASTER SWIR band ratios (e.g. B5/B6, B7/B6 — clay/alteration), B4/B3 iron oxide | ASTER L2 | Detects alteration & Fe/Mn-oxide surface expression of gondite/gossan |
| Sentinel-2 indices: Iron Oxide (B4/B2), Clay (B11/B12), NDVI, NDMI, bare-soil index | Copernicus | Surface mineralogy proxy + vegetation screening |
| **Geobotanical stress anomaly** — NDVI residual after removing terrain/soil/rainfall effects | Sentinel-2 + covariates | Metal-tolerant/stressed vegetation over mineralised outcrops. Uses NDVI *honestly*, as a weak surface indicator, not as a Mn detector |
| Landsat/MODIS LST anomaly | MODIS LST | Thermal inertia contrast of ore-bearing vs host lithology on bare ground |
| DEM derivatives: slope, curvature, TPI, drainage density | Cartosat-1 DEM (Bhuvan) / SRTM | Structural & geomorphic control |
| **Lineament density & distance-to-lineament** | Auto-extracted from DEM hillshade + Sentinel-1 | Structural control on Sausar mineralisation |
| Aeromagnetic / gravity (Bouguer) residual & derivatives | GSI Bhukosh / NGDR | Sub-surface density/susceptibility contrast — real sub-surface signal |
| Geochemistry (stream sediment Mn, Fe ppm) | NGDR/GSI | Direct pathfinder |
| Lithology one-hot (Sausar Group formations: Mansar, Lohangi, Chorbaoli) | GSI 1:50k geology | Domain prior |
| Distance to known Mn occurrence / historic working | GSI + MOIL | Strongest single predictor — ⚠️ and a leakage hazard; see below |

**Labels:** known manganese occurrences (positives). There are **no reliable negatives** — an unexplored cell is not a "no ore" cell.

**Model — this is the technically defensible choice:**

1. **Positive–Unlabelled (PU) learning** via bagged one-class / Elkan-Noto style estimation, *or* a one-class SVM / Isolation-Forest anomaly baseline.
2. Main model: **XGBoost / LightGBM** on positives vs *randomly sampled unlabelled negatives*, bagged over many negative draws (this is the standard MPM workaround).
3. **Spatial block cross-validation** (`GroupKFold` on 10 km × 10 km spatial blocks). ⚠️ **This is the single most important methodological detail in your entire prospectivity pipeline.** Random k-fold on spatially autocorrelated grids will report AUC ≈ 0.98 and mean nothing. Reporting a lower, honest spatial-CV AUC (realistically **0.78–0.88**) with an explanation beats reporting 0.98 with a shrug — technical judges know this trap.
4. Calibrate outputs (Platt/isotonic) so the "prospectivity score" is a usable probability.
5. Output: prospectivity raster + **uncertainty raster** (bagging variance) + top-N ranked target polygons with the feature contributions that generated each.

**Metrics:** spatial-CV AUC, **success-rate / prediction-rate curve** (the standard MPM metric — what fraction of known deposits fall in the top X% of predicted area), Cohen's κ, and the *capture efficiency* at 5% and 10% of area.

⚠️ Drop "distance to known occurrence" from the final model or handle it with extreme care — it trivially leaks the label and produces a map that just draws circles around existing mines. Run the model both with and without it and **show both**. That comparison slide is a genuine credibility moment.

#### 6.2.2 Scale B — Mine-scale 3D block model (the reserve number)

**Input:** drill-hole tables in the industry-standard four-table form —
`collar (hole_id, x, y, z)`, `survey (hole_id, depth, azimuth, dip)`, `assay (hole_id, from, to, Mn%, Fe%, SiO2, Al2O3, P)`, `lithology (hole_id, from, to, rock_code)`.

**Pipeline:**
```
1. Desurvey holes (minimum-curvature) → 3D sample points
2. Composite assays to fixed length (1.0 m or 1.5 m) — length-weighted
3. Domain the deposit: separate ore lens vs host (Mn cut-off, e.g. ≥ 10% Mn),
   optionally an unfolding / structural coordinate transform so interpolation
   follows the folded stratabound geometry of the Sausar gondite bands
   (⚠️ this is what a real geologist will ask about — interpolating a tightly
    folded ore band in plain Cartesian space smears grade across barren rock)
4. Declustering + outlier capping (top-cut at 99.5th percentile)
5. Experimental variogram → fit (spherical/exponential), with anisotropy
   along strike / down dip / across the band
6. Build a regular block model (5 m × 5 m × 5 m; sub-blocked at contacts)
7. ESTIMATE:
     a. Ordinary Kriging  → grade estimate + kriging variance   [primary]
     b. Sequential Gaussian Simulation, 100 realisations         [uncertainty]
     c. ML comparator: LightGBM / RF on (x,y,z, structural coords, lithology,
        distance-to-nearest-hole, local sample stats) — report against OK
8. Tonnage = volume × bulk density (Mn ore ≈ 3.2–4.0 t/m³, grade-dependent —
   fit a density–grade regression rather than using a single constant)
9. CONFIDENCE CLASSIFICATION → UNFC-aligned:
     drill spacing + kriging variance + number of informing samples + slope of
     regression → Measured / Indicated / Inferred → UNFC codes (e.g. 111, 121,
     122, 331). Rule-based + a small classifier; always human-certifiable.
10. Grade–tonnage curves at multiple cut-offs; P10/P50/P90 from the 100 SGS
    realisations.
```

**Metrics:** leave-one-out cross-validation on holes (MAE, RMSE, R² on Mn%), variogram model fit, **slope of regression of true-on-estimated** (conditional bias check — the metric real resource geologists use), and calibration of the P10–P90 interval (do ~80% of held-out samples fall inside it?).

🔷 **Honest positioning for your deck:** *"We do not claim ML beats 60 years of geostatistics. We use kriging for the estimate, simulation for the uncertainty, and ML for three things geostatistics is bad at: fusing heterogeneous surface evidence, classifying confidence at scale, and re-estimating in seconds when a new hole lands."* This sentence will impress a mining-domain judge more than any accuracy number.

#### 6.2.3 Accessibility model (the `A_b` term in EAR)

Not ML — a deterministic reachability graph, and it's better for being simple:

- Build a graph of the mine: shafts → levels → drives → cross-cuts → stopes → blocks (opencast: benches → ramps → haul roads).
- Each edge has a `status` (existing / under development / planned) and `metres_remaining`.
- `lead_time(b) = Σ metres_remaining along the path / historical advance_rate(mine, heading_type)`
- `A_b(H) = P(lead_time(b) ≤ H)` using the **distribution** of historical advance rates (not the mean).
- Add binary gates: ventilation ready, ground support done, statutory permission in place.

⚠️ This component requires zero ML and delivers half the product's value. Build it early.

### 6.3 PULSE — Production shortfall prediction

#### 6.3.1 Target and framing

Predict daily tonnage `y(m, d)` per mine `m`, horizon 1–90 days. Then:
```
Shortfall probability for period P with target T:
  S = P( Σ_{d ∈ P} y(m,d)  <  (1 - τ) · T )      τ = tolerance, default 5%
```
Computed by Monte Carlo: fit a distribution per day from the predicted quantiles (or use direct quantile sampling with a copula for day-to-day correlation — ⚠️ *ignoring correlation between days will badly understate the tail; mention this, it's a sophisticated point*), then sum 10,000 sampled paths.

#### 6.3.2 Feature set

| Group | Features |
|---|---|
| **Autoregressive** | lags 1–14, 21, 28, 364; rolling mean/std/min/max over 7/14/28/90 d; month-to-date cumulative vs pro-rata target |
| **Calendar** | day of week, month, festival/holiday flags, shift pattern, statutory holidays, financial-quarter position (captures the real Q4 push) |
| **Weather (EO)** | IMERG rainfall d, and lags 1–14; 3/7/14-day cumulative rainfall; consecutive wet days; SMAP/S1 soil moisture; MODIS LST; NDVI (haul-road/vegetation context); **forecast** rainfall for the horizon (IMD/GFS/open-meteo) |
| **Equipment** | count & capacity-weighted availability of LHDs, drill jumbos, dumpers, shovels, winders; mean time since last service; open work orders; **predicted failure probability from §6.4** |
| **Mining** | blasts fired last 7/14 d; development metres advanced; number of active faces; average face grade; stope readiness count; ore-pass/skip availability |
| **Manpower** | attendance %, contractor strength, absenteeism trend |
| **Geological** | average Mn% of active faces from the block model; hardness/RQD proxy; dilution rate |
| **Logistics** | stock at pit-head, weighbridge dispatch, rake availability (Phase 2) |

#### 6.3.3 Models (with baselines — always show the ladder)

| Tier | Model | Purpose |
|---|---|---|
| B0 | Last-year-same-month average | The incumbent. **Beat this and quantify by how much.** |
| B1 | Seasonal naive + ETS/ARIMA | Statistical baseline |
| B2 | **LightGBM with quantile objective** (α = 0.1, 0.5, 0.9) | 🔷 **Primary model.** Handles non-linearity, missing values, mixed feature types; trains in seconds; gives native quantiles |
| B3 | **HierarchicalForecast MinT reconciliation** | Forces face → mine → region → company consistency |
| B4 | (Optional, only if time) Temporal Fusion Transformer / N-BEATS | ⚠️ Almost certainly *not* worth it in 36 h with ~5 years × 11 mines of daily data. Mention as future work, don't build it. |

**Metrics:** MAE, RMSE, **MAPE/WAPE per mine**, **pinball loss** for the quantiles, **PICP** (prediction-interval coverage probability — does the 80% interval actually contain 80% of outcomes?), and for the shortfall classifier: **Brier score**, ROC-AUC, PR-AUC, and a **reliability/calibration curve**.

🔷 **Accuracy targets to state (realistic, defensible):** monthly-total WAPE **8–12%** per mine (vs ~18–25% for the naive baseline 🔶 assumed); 80% prediction intervals with PICP within **0.75–0.85**; shortfall classifier Brier score < 0.15. Do **not** promise 95% accuracy — a domain judge will know you're bluffing.

#### 6.3.4 Weather derating curves (a genuinely novel, presentable artefact)

For each mine, fit a **distributed-lag model**:
```
Δoutput(d) = β₀ + Σ_{k=0}^{14} β_k · rainfall(d−k) + γ · soil_moisture(d) + controls + ε
```
with a smoothness penalty on `β_k` (a polynomial-distributed-lag / Almon lag or a penalised spline). Plot `β_k` vs lag as the mine's **rain response curve**.

Result you can put on a slide: *"At Dongri Buzurg (opencast), 50 mm of rain costs 9.2% of capacity on the same day and 14.1% cumulatively over the following 6 days. At Balaghat (underground, 383 m deep — the deepest of MOIL's 11 mines ✅), the same rainfall costs only 3.1%, and it arrives with a 2-day lag through haulage and dispatch, not extraction."*

⚠️ That single comparison — underground vs opencast rain sensitivity, learned from satellite rainfall — is worth more in the judging room than an extra model. It shows you understand *mining*, not just ML.

### 6.4 Equipment failure risk

- **Data:** per-asset event log — commissioning date, cumulative running hours, breakdown events (start/end), work orders, fault codes if available.
- **Model A (primary): Weibull Accelerated Failure Time / Cox PH** (`lifelines`) on time-to-next-failure, censored at "still running." Gives an interpretable hazard and a survival curve per asset.
- **Model B: gradient boosting survival / binary GBM** on "fails within next 14 days?" with features: hours since service, hours since last failure, rolling breakdown frequency, asset age, utilisation intensity, ambient temperature (MODIS LST as a proxy!), and monsoon flag.
- **Output:** `P(failure ≤ 14 d)` per asset → feeds PULSE as a feature *and* NUDGE as a constraint.
- **Metrics:** concordance index (C-index) for survival; PR-AUC + Brier for the binary form.

🔶 **ASSUMPTION & honesty note:** without vibration/oil/CAN-bus telemetry this is *statistical* reliability modelling, not condition-based predictive maintenance. **Say so.** Then say: "with OEM telemetry in Phase 2, the same architecture accepts sensor features and the C-index should rise materially." Judges reward calibrated claims.

### 6.5 NUDGE — Prescriptive optimisation

**Formulation (MILP — write this on a slide; almost no SIH team shows a real formulation):**

*Decision variables*

- `x[f,t] ≥ 0` — tonnes mined from face/stope `f` in period `t` (t = week, over a 4–13 week horizon)
- `z[f,t] ∈ {0,1}` — face `f` is active in period `t`
- `e[k,f,t] ∈ {0,1}` — equipment unit `k` assigned to face `f` in period `t`
- `s[j,t] ∈ {0,1}` — maintenance job `j` scheduled in period `t`
- `d[t] ≥ 0` — shortfall against target in period `t` (soft variable)

*Objective*
```
maximise   Σ_t [ w₁ · Σ_f x[f,t]                (tonnage)
                − w₂ · d[t]                      (penalised shortfall)
                − w₃ · Σ_f grade_deviation[f,t]  (blend compliance)
                − w₄ · redeployment_cost         (churn penalty — real, and
                                                   crews hate being moved) ]
```

*Constraints*
```
C1  Σ_f x[f,t] + d[t]  ≥  target[t]                            (target with slack)
C2  x[f,t] ≤ capacity(f) · z[f,t] · derate_weather(t)
      · availability_equipment(t)                              (physical capacity)
C3  Σ_t x[f,t] ≤ EAR(f)                                        (can't mine what isn't there)
C4  z[f,t] ≤ ready(f,t)                                        (development / A_b gate)
C5  Σ_f e[k,f,t] ≤ 1  ∀k,t                                     (one unit, one face)
C6  Σ_k e[k,f,t] ≥ min_fleet(f) · z[f,t]                       (a face needs its fleet)
C7  E[available(k,t)] ≥ threshold  unless  s[j,t]=1            (failure-risk-aware)
C8  |Σ_f x[f,t]·grade(f) / Σ_f x[f,t]  −  target_grade|  ≤ ε   (grade blending)
C9  blasts_per_week(t) ≤ B_max ;  min gap between blasts       (statutory + practical)
C10 Σ_f x[f,t] ≤ hoisting/haulage/crusher capacity(t)          (bottleneck)
C11 manpower(t) constraints; C12 stock & dispatch limits
```

*Solve:* OR-Tools CP-SAT or HiGHS/CBC via PuLP. For a MOIL-scale instance (≈30 faces × 13 weeks × ~25 equipment units) this solves in **well under a second to a few seconds**. Set a time limit of 5 s and accept the incumbent solution — 🔷 always ship a **greedy heuristic fallback** (sort faces by grade × readiness × equipment-availability, fill target) so the demo can never hang on an infeasible solve.

*Robustness:* solve for the P10, P50 and P90 weather/equipment scenarios and report the action set that performs best across all three (a light **scenario-based stochastic programme**). Say "we optimise for the plan that is robust across rainfall scenarios, not the plan that is optimal if nothing goes wrong."

*Presentation:* never dump the raw schedule. Convert the diff between current plan and optimised plan into **3–5 natural-language actions**, each with Δtonnage and Δ P(shortfall). That translation layer is the product.

### 6.6 Where (and how) an LLM is allowed in

**Allowed:**

- Turning the numeric action list into a briefing paragraph and a shift-briefing one-pager.
- Drafting the monthly variance-explanation narrative from computed drivers.
- Natural-language query → structured filter ("show me stopes above 40% Mn on level 5 that are ready this month") via **function calling into your own API**, never free SQL.

**Hard rules to prevent hallucination:**

1. **The LLM never computes a number.** Every figure it prints is passed in from a computed payload. Template-constrain the output.
2. **Structured output only** (JSON schema / Pydantic-validated), then rendered — not raw prose into the UI.
3. **Post-generation numeric validation:** regex-extract every number in the LLM output and assert it exists in the source payload; reject and fall back to a deterministic template on mismatch. 🔷 *Mention this guardrail explicitly — it is the correct answer to "how do you handle hallucination?"*
4. Every generated narrative is stamped "AI-generated summary — figures computed by OreSight models" with a link to the underlying computation.
5. Nothing safety-related, statutory, or blast-related is ever LLM-generated.

**Model choice:** a small open model (Llama 3.1 8B / Mistral 7B via Ollama) run locally is sufficient and keeps MOIL's operational data inside its own network — an important argument for a PSU. 🔷 Do **not** make an external LLM API a hard dependency of your demo; network failure at the venue is a real risk.

### 6.7 Cost considerations

| Item | Hackathon | Production (annual, order of magnitude 🔶) |
|---|---|---|
| EO data (Sentinel, IMERG, MODIS, Landsat) | ₹0 — all free & open | ₹0 |
| Google Earth Engine | Free for research/non-commercial; ⚠️ commercial/government use needs a paid plan — plan for a self-hosted `pystac` + Copernicus pipeline as the production path | Modest, or ₹0 self-hosted |
| Compute (training) | Laptop / Colab | 1 GPU node occasionally + CPU cluster |
| Inference | CPU-only — all our models are CPU-friendly (that is a deliberate choice) | Low |
| Cloud hosting | Free tier / laptop | ₹8–20 L/yr on MeghRaj/empanelled cloud, or on-prem |
| LLM | Local Ollama, ₹0 | Local inference; no per-token cost |
| Commercial mining software licences | ₹0 (we replace/complement) | Avoided cost — a *savings* line in your business case |

🔷 **Design principle worth stating:** *every model in OreSight runs on CPU.* No GPU dependency means it can be deployed on a modest on-premise server inside a mine's IT room. That is a real, practical differentiator versus deep-learning-heavy proposals.

---

## 7. Technology Stack

### 7.1 Recommended stack (with honest alternatives)

| Layer | Primary choice | Alternatives | Why the primary |
|---|---|---|---|
| **Frontend framework** | React 18 + TypeScript + Vite | Next.js, Vue 3, SvelteKit | Largest talent pool in a student team; Vite is fastest to iterate; Next.js SSR adds complexity you don't need for an authenticated internal dashboard |
| **UI library** | TailwindCSS + **shadcn/ui** | MUI, Ant Design, Mantine | shadcn gives professional-looking components you own and can restyle in minutes — critical for looking polished in 36 h |
| **Charts** | Apache ECharts (+ Recharts for simple ones) | Plotly.js, Chart.js, visx | ECharts handles large series, candlestick-style uncertainty bands and is free |
| **Maps** | **MapLibre GL JS** + deck.gl | Leaflet (simpler, less capable), Mapbox GL (licence), OpenLayers | No API key, no billing, offline/self-host capable |
| **3D** | Three.js via **react-three-fiber** + `drei` | Babylon.js, CesiumJS (if you want a globe/terrain) | Declarative React integration; `InstancedMesh` for 200k blocks |
| **Backend** | **FastAPI** (Python 3.11), Pydantic v2, Uvicorn/Gunicorn | Django REST (heavier, but great admin), Node/NestJS (loses the ML ecosystem), Go (fast, no ML libs) | Same language as ML; auto OpenAPI; async; minimal boilerplate |
| **Task queue** | Celery + Redis | RQ (simpler), Dramatiq, APScheduler | Mature, good monitoring (Flower), Beat scheduler included |
| **Database** | **PostgreSQL 16 + PostGIS 3.4 + TimescaleDB** | MySQL (weak GIS), MongoDB (wrong shape), InfluxDB (adds a second DB) | One engine, real spatial + real time-series, ACID, free |
| **ORM / migrations** | SQLAlchemy 2.0 + Alembic + GeoAlchemy2 | Tortoise, SQLModel, raw SQL | Mature; GeoAlchemy2 for PostGIS types |
| **Object storage** | MinIO (S3 API) | AWS S3, local filesystem for the hackathon | Self-hostable — matters for an air-gapped PSU deployment |
| **Raster tiles** | **TiTiler** (`rio-tiler`) serving COGs | GeoServer (heavier, Java), MapTiler | Lightweight, Python, dynamic tiling from COGs |
| **Geospatial processing** | `rasterio`, `rioxarray`, `xarray`, `geopandas`, `shapely`, `pyproj`, `GDAL` | — | The standard stack |
| **EO access** | `pystac-client` + `odc-stac` on **Copernicus Data Space**; `earthengine-api` for prototyping; `sentinelhub-py` | Direct Bhoonidhi ordering (manual), AWS Open Data | STAC gives reproducible, scriptable access |
| **Geostatistics** | `PyKrige`, `GSTools`, `scikit-gstat`, `GeostatsPy` | SGeMS, GSLIB (Fortran), `gstat` (R) | Pure Python, integrates with the rest |
| **3D geology** | **GemPy** | Leapfrog (commercial), implicit RBF by hand | Open-source implicit modelling; good for the demo surfaces |
| **ML** | scikit-learn, **LightGBM**, XGBoost, `SHAP`, `lifelines`/`scikit-survival` | CatBoost, PyTorch (unnecessary here) | Fast, CPU-friendly, interpretable, quantile-native |
| **Forecasting** | Nixtla `StatsForecast` + `MLForecast` + **`HierarchicalForecast`** | `sktime`, Prophet, Darts | HierarchicalForecast gives MinT reconciliation out of the box — hard to hand-roll |
| **Optimisation** | **Google OR-Tools** (CP-SAT) and/or PuLP + HiGHS | Gurobi/CPLEX (licence), pyomo | Free, fast, well-documented |
| **ML lifecycle** | MLflow | Weights & Biases, DVC | Self-hostable, free, model registry included |
| **Auth** | FastAPI JWT + RBAC (hackathon) → **Keycloak** (prod) | Auth0 (cost), Firebase Auth (data residency ⚠️) | Keycloak is open-source, self-hosted, supports SSO/LDAP which a PSU will demand |
| **Notifications** | WebSockets (in-app) + SMTP + webhook | FCM push, SMS via MSG91/Gupshup for field staff | Free & simple; SMS matters at remote mines |
| **LLM** | Ollama + Llama 3.1 8B / Mistral 7B, local | OpenAI/Anthropic API (data residency ⚠️, network dependency) | Runs offline, keeps operational data in-network |
| **Containerisation** | Docker + Docker Compose → Kubernetes | Podman, bare metal | One-command demo bring-up |
| **CI/CD** | GitHub Actions (lint, test, build, push image) | GitLab CI, Jenkins | Free for public repos, zero setup |
| **Monitoring** | Prometheus + Grafana + Loki + Sentry | ELK, Datadog (cost) | Free, self-hosted |
| **Testing** | pytest + `httpx` (API), Vitest + Testing Library (FE), Playwright (E2E) | Jest, Cypress | Fast |
| **File/report generation** | WeasyPrint or ReportLab (PDF), `openpyxl`/`xlsxwriter` (XLSX) | pandoc + LaTeX | Native Python, no external binary needed |
| **OCR (if legacy paper logs)** | PaddleOCR / Tesseract + `pdfplumber` | Google Vision (cost, residency) | 🔷 Only Phase 2 — MOIL's core data is digital enough; don't waste hackathon hours here |
| **i18n** | `react-i18next`; Bhashini API for Hindi/Marathi | — | Phase 2 |

### 7.2 Selection principles applied

- **Free / open-source everywhere.** Total software licence cost of the stack: **₹0.** State this — it is a decisive argument for government procurement.
- **CPU-only inference.** No GPU in the deployment budget.
- **Self-hostable end to end.** MOIL can run this inside its own data centre with no internet egress (except EO ingestion, which can be a scheduled one-way pull). Air-gap-friendly architecture is a serious PSU requirement.
- **One language (Python) across backend + ML**, one language (TS) on the frontend. Two languages total for a 6-person team.
- **Boring where it doesn't matter, sharp where it does.** Postgres and FastAPI are boring on purpose so that your innovation budget goes into PRISM/PULSE/NUDGE.

---

## 8. Database Design

### 8.1 Entities

**Organisational:** `users`, `roles`, `user_roles`, `regions`, `mines`, `audit_log`
**Geological:** `leases`, `boreholes`, `borehole_survey`, `assays`, `lithology`, `geo_domains`, `block_models`, `blocks`, `block_realisations`, `prospectivity_runs`, `prospectivity_cells`
**Mine layout:** `levels`, `workings` (drives/cross-cuts/ramps/benches), `faces` (stopes/benches), `development_progress`
**Operational (time-series):** `production_daily`, `production_shift`, `blast_events`, `equipment`, `equipment_events`, `manpower_daily`, `dispatch_daily`, `stock_daily`
**Environmental:** `eo_scenes`, `eo_timeseries`, `weather_forecast`
**Analytics:** `targets`, `forecasts`, `forecast_drivers`, `alerts`, `equipment_risk`, `derating_curves`, `scenarios`, `optimisation_runs`, `recommended_actions`, `schedule_versions`, `reconciliation`
**ML ops:** `model_registry`, `model_runs`, `feature_snapshots`

### 8.2 Key tables and important fields

```sql
-- ============ ORGANISATION ============
mines (
  mine_id           SERIAL PK,
  code              TEXT UNIQUE,          -- 'BLG', 'DGB', 'KND'
  name              TEXT,                 -- 'Balaghat'
  region_id         INT FK → regions,
  state             TEXT, district        TEXT,
  mine_type         TEXT CHECK (IN ('underground','opencast','mixed')),
  lease_geom        GEOMETRY(POLYGON, 4326),   -- PostGIS, GiST index
  centroid          GEOMETRY(POINT, 4326),
  max_depth_m       NUMERIC,
  rated_capacity_tpa NUMERIC,
  commissioned_on   DATE,
  is_active         BOOLEAN
)

-- ============ GEOLOGY ============
boreholes (
  hole_id     TEXT PK,  mine_id INT FK,
  collar_geom GEOMETRY(POINTZ, 32644),   -- UTM 44N, metres — do NOT store
  collar_rl_m NUMERIC,                   --   mine geometry in degrees
  total_depth_m NUMERIC, drill_date DATE,
  purpose     TEXT,   -- exploration | grade-control | geotechnical
  data_source TEXT,   -- 'MOIL' | 'GSI-NGDR' | 'SYNTHETIC'
  is_synthetic BOOLEAN DEFAULT FALSE      -- ⚠️ demo honesty flag
)

borehole_survey (survey_id PK, hole_id FK, depth_m, azimuth_deg, dip_deg)

assays (
  assay_id BIGSERIAL PK, hole_id FK,
  from_m NUMERIC, to_m NUMERIC,
  mn_pct NUMERIC, fe_pct NUMERIC, sio2_pct NUMERIC, al2o3_pct NUMERIC,
  p_pct NUMERIC, moisture_pct NUMERIC,
  bulk_density NUMERIC, sample_geom GEOMETRY(POINTZ,32644),
  lab_ref TEXT, qaqc_flag TEXT,          -- pass | duplicate | standard | fail
  UNIQUE (hole_id, from_m, to_m)
)

lithology (lith_id PK, hole_id FK, from_m, to_m, rock_code, formation, rqd_pct)

block_models (
  model_id SERIAL PK, mine_id FK, version TEXT, created_at TIMESTAMPTZ,
  block_size_x/y/z NUMERIC, origin_x/y/z NUMERIC, nx, ny, nz INT,
  method TEXT,               -- 'OK' | 'SGS' | 'ML-GBM' | 'IDW'
  variogram_params JSONB, run_stats JSONB, certified_by INT FK → users
)

blocks (
  block_id BIGSERIAL PK, model_id FK, mine_id FK, level_id FK NULL,
  ix INT, iy INT, iz INT,
  centroid GEOMETRY(POINTZ, 32644),
  mn_pct_est NUMERIC, kriging_variance NUMERIC,
  mn_p10 NUMERIC, mn_p50 NUMERIC, mn_p90 NUMERIC,
  tonnage NUMERIC, bulk_density NUMERIC,
  domain_code TEXT,                          -- ore lens id / waste
  confidence_class TEXT,                     -- measured|indicated|inferred
  unfc_code TEXT,                            -- '111','121','122','331'
  n_informing_samples INT, nearest_hole_m NUMERIC,
  accessibility NUMERIC,     -- A_b  ∈ [0,1]
  recovery_factor NUMERIC,   -- R_b
  ear_tonnes NUMERIC,        -- computed Effective Accessible Reserve
  status TEXT                -- in-situ | scheduled | mined | sterilised
)
-- Indexes: (model_id, iz), GIST(centroid), (mine_id, confidence_class)

block_realisations (block_id FK, realisation_no INT, mn_pct NUMERIC)
  -- 100 SGS realisations; partitioned / or stored as a Parquet file in MinIO
  -- ⚠️ 200k blocks × 100 realisations = 20M rows. For the hackathon, store
  --    realisations as Parquet in MinIO and keep only P10/P50/P90 in Postgres.

prospectivity_cells (
  cell_id BIGSERIAL PK, run_id FK, geom GEOMETRY(POLYGON,4326),
  score NUMERIC, uncertainty NUMERIC, rank INT, top_features JSONB
)

-- ============ MINE LAYOUT & ACCESSIBILITY ============
levels  (level_id PK, mine_id FK, level_name, rl_m NUMERIC, status)
workings(working_id PK, mine_id FK, level_id FK, type, geom GEOMETRY(LINESTRINGZ),
         status, metres_total, metres_done, advance_rate_m_per_day NUMERIC)
faces   (face_id PK, mine_id FK, level_id FK, code, type,     -- stope|bench
         geom GEOMETRY(POLYGONZ), avg_mn_pct, ear_tonnes,
         ready_from DATE, min_fleet JSONB, capacity_tpd NUMERIC, status)
face_blocks (face_id FK, block_id FK)                          -- M:N

-- ============ OPERATIONS (TimescaleDB hypertables) ============
production_daily (
  ts DATE, mine_id INT, face_id INT NULL,
  ore_tonnes NUMERIC, waste_tonnes NUMERIC, avg_mn_pct NUMERIC,
  shifts_worked INT, is_holiday BOOLEAN,
  source TEXT,                                -- 'DPR' | 'weighbridge' | 'SYNTHETIC'
  PRIMARY KEY (ts, mine_id, face_id)
)  -- hypertable on ts; continuous aggregate: monthly_production_by_mine

equipment (
  equip_id PK, mine_id FK, asset_no TEXT, type TEXT,   -- LHD|jumbo|dumper|shovel|winder
  make_model TEXT, capacity NUMERIC, commissioned_on DATE,
  cumulative_hours NUMERIC, last_service_on DATE, status TEXT
)
equipment_events (
  ts TIMESTAMPTZ, equip_id INT, event_type TEXT,  -- breakdown|repair|service|idle|running
  duration_hours NUMERIC, fault_code TEXT, downtime_category TEXT, remarks TEXT
)  -- hypertable

blast_events (
  ts TIMESTAMPTZ, mine_id, face_id, planned_ts TIMESTAMPTZ,
  delay_hours NUMERIC, delay_reason TEXT,
  holes INT, explosive_kg NUMERIC, tonnes_broken NUMERIC,
  fragmentation_index NUMERIC, misfire BOOLEAN
)

manpower_daily (ts DATE, mine_id, planned_strength, present_strength, contractor_strength)
dispatch_daily (ts DATE, mine_id, tonnes_dispatched, grade, mode, rake_no)

-- ============ EARTH OBSERVATION ============
eo_scenes (scene_id PK, mine_id, sensor, acquired_at, cloud_pct,
           cog_uri TEXT, bands JSONB, footprint GEOMETRY(POLYGON,4326))
eo_timeseries (
  ts DATE, mine_id INT,
  rainfall_mm NUMERIC,           -- GPM IMERG
  rainfall_3d NUMERIC, rainfall_7d NUMERIC, rainfall_14d NUMERIC,
  soil_moisture NUMERIC,         -- SMAP / Sentinel-1 derived
  ndvi NUMERIC, ndmi NUMERIC, lst_c NUMERIC,
  s1_vv_db NUMERIC, s1_coherence NUMERIC,
  pit_area_m2 NUMERIC, dump_area_m2 NUMERIC,   -- opencast change detection
  PRIMARY KEY (ts, mine_id)
)  -- hypertable
weather_forecast (issued_at, valid_date, mine_id, rain_mm_p50, rain_mm_p90, source)

-- ============ ANALYTICS ============
targets (target_id PK, mine_id FK, period_type, period_start, period_end,
         target_tonnes NUMERIC, target_grade NUMERIC, approved_by, approved_on)

forecasts (
  forecast_id BIGSERIAL PK, run_id UUID, mine_id FK, model_version TEXT,
  generated_at TIMESTAMPTZ, target_date DATE, horizon_days INT,
  p10 NUMERIC, p50 NUMERIC, p90 NUMERIC,
  shortfall_prob NUMERIC, expected_shortfall_tonnes NUMERIC
)
forecast_drivers (forecast_id FK, driver_name TEXT, shap_value NUMERIC,
                  direction TEXT, tonnes_impact NUMERIC, rank INT)

alerts (alert_id PK, mine_id, severity, type, title, body, shortfall_prob,
        raised_at, acknowledged_by, acknowledged_at, resolved_at, status)

equipment_risk (ts DATE, equip_id, p_failure_14d NUMERIC, p_failure_30d NUMERIC,
                expected_downtime_hours NUMERIC, model_version TEXT)

derating_curves (mine_id FK, driver TEXT, lag_days INT, coefficient NUMERIC,
                 ci_low NUMERIC, ci_high NUMERIC, fitted_at TIMESTAMPTZ, r2 NUMERIC)

scenarios (scenario_id PK, created_by FK, name, mine_ids INT[], params JSONB,
           created_at, base_forecast_run UUID)

optimisation_runs (opt_id PK, scenario_id FK, mine_id, horizon_weeks,
                   objective_value NUMERIC, solver TEXT, solve_ms INT,
                   status TEXT, solution JSONB)

recommended_actions (
  action_id PK, opt_id FK, mine_id, rank INT,
  action_type TEXT,     -- reschedule_face | redeploy_equipment | advance_blast
                        -- | pull_forward_maintenance | add_shift | defer_development
  title TEXT, description TEXT, payload JSONB,
  delta_tonnes NUMERIC, delta_shortfall_prob NUMERIC,
  cost_estimate NUMERIC, feasibility_notes TEXT,
  status TEXT,          -- proposed | accepted | rejected | applied
  decided_by FK, decided_at, rejection_reason TEXT
)

schedule_versions (version_id PK, mine_id, effective_from, created_by,
                   parent_version_id, schedule JSONB, applied_actions INT[])

reconciliation (period, mine_id, planned_t, model_predicted_t, actual_mined_t,
                dispatched_t, planned_grade, actual_grade,
                counterfactual_t,        -- what we predicted WITHOUT the action
                actions_applied INT[], recovery_tonnes NUMERIC, bias_factor NUMERIC)

audit_log (log_id BIGSERIAL PK, ts TIMESTAMPTZ, user_id, role, action, entity,
           entity_id, before JSONB, after JSONB, ip INET, request_id UUID)
```

### 8.3 ER diagram (text)

```
regions 1──∞ mines
mines   1──∞ leases            mines 1──∞ levels 1──∞ workings
mines   1──∞ boreholes 1──∞ assays
                       1──∞ borehole_survey
                       1──∞ lithology
mines   1──∞ block_models 1──∞ blocks 1──∞ block_realisations
                                    │
                        faces ∞──∞ blocks   (via face_blocks)
                          │
levels 1──∞ faces 1──∞ production_daily
mines  1──∞ production_daily
mines  1──∞ equipment 1──∞ equipment_events
                      1──∞ equipment_risk
mines  1──∞ blast_events
mines  1──∞ eo_timeseries        mines 1──∞ eo_scenes
mines  1──∞ weather_forecast
mines  1──∞ targets
mines  1──∞ forecasts 1──∞ forecast_drivers
mines  1──∞ alerts
mines  1──∞ derating_curves
users  1──∞ scenarios 1──∞ optimisation_runs 1──∞ recommended_actions
                                                        │
                                          schedule_versions ──┘
mines  1──∞ reconciliation
users  ∞──∞ roles (user_roles)      users 1──∞ audit_log
model_registry 1──∞ model_runs → referenced by forecasts.model_version
```

### 8.4 Design notes worth defending

- **Two coordinate systems on purpose.** Lease boundaries and EO products in EPSG:4326 (lat/lon); mine geometry, boreholes and blocks in **EPSG:32644 (UTM 44N, metres)** — because kriging distances, block volumes and drive lengths are meaningless in degrees. ⚠️ This is a real trap; teams that store `POINTZ` in 4326 and then compute a variogram get garbage.
- **Realisations off-row.** 100 SGS realisations × 200k blocks would bloat Postgres. Keep P10/P50/P90 in the table, full realisations as Parquet in MinIO.
- **`is_synthetic` / `source` flags everywhere.** So the UI can honestly badge demo data. Judges notice and respect this.
- **`counterfactual_t` in reconciliation.** This is how you prove value in year one. Most teams forget to design for measuring their own impact.
- **Immutable `audit_log` with before/after JSONB.** Required for a government system; also your defence when someone asks "who changed the plan?"

---

## 9. API Design

Base: `/api/v1`. All responses JSON. Auth: `Authorization: Bearer <JWT>`. Every mutating call writes to `audit_log`.

### 9.1 Auth & users

| Method | Endpoint | Purpose | Request | Response | Auth |
|---|---|---|---|---|---|
| POST | `/auth/login` | Obtain tokens | `{username, password, otp?}` | `{access_token, refresh_token, expires_in, user{id,name,role,mines[]}}` | ❌ |
| POST | `/auth/refresh` | Rotate access token | `{refresh_token}` | `{access_token}` | ❌ |
| POST | `/auth/logout` | Revoke | — | `204` | ✅ |
| GET | `/users/me` | Profile + permissions | — | `{id,name,email,roles[],mine_scope[]}` | ✅ |
| GET | `/users` | List (admin) | `?role=&mine_id=` | `[user]` | ✅ Admin |

### 9.2 Mines & geology

| Method | Endpoint | Purpose | Response (abridged) | Auth |
|---|---|---|---|---|
| GET | `/mines` | All mines + current KPI chips | `[{mine_id, code, name, type, centroid, mtd_tonnes, target, shortfall_prob, status}]` | ✅ |
| GET | `/mines/{id}` | Mine detail | `{...mine, levels[], active_faces, equipment_summary, lease_geojson}` | ✅ |
| GET | `/mines/{id}/reserve/summary` | Reserve funnel (EAR) | `{resource_t, reserve_t, accessible_t, ear_t, at_risk_t, by_confidence:{measured,indicated,inferred}, p10,p50,p90}` | ✅ |
| GET | `/mines/{id}/blocks` | Block model for 3D viewer | `?level=&min_mn=&max_mn=&confidence=&format=json|binary` → `{count, blocks:[{ix,iy,iz,x,y,z,mn,conf,ear,status}]}` ⚠️ *return binary/typed arrays above 50k blocks* | ✅ |
| GET | `/mines/{id}/blocks/grade-tonnage` | Grade–tonnage curve | `[{cutoff_mn, tonnes, avg_grade}]` | ✅ |
| GET | `/mines/{id}/boreholes` | Drill-holes with traces | `[{hole_id, collar, trace_geojson, depth, assays_summary, is_synthetic}]` | ✅ |
| POST | `/mines/{id}/boreholes/import` | Upload collar/survey/assay CSVs | multipart | `202 {job_id}` | ✅ Geologist |
| POST | `/mines/{id}/block-model/run` | Trigger re-estimation | `{method:'OK'|'SGS'|'ML', block_size, variogram?, n_realisations?}` | `202 {job_id}` | ✅ Geologist |
| GET | `/jobs/{job_id}` | Async job status | `{status, progress, result_ref, error}` | ✅ |
| GET | `/prospectivity/runs` | List prospectivity runs | `[{run_id, aoi, model, spatial_cv_auc, created_at}]` | ✅ |
| GET | `/prospectivity/{run_id}/tiles/{z}/{x}/{y}.png` | Raster tiles (TiTiler) | PNG | ✅ |
| GET | `/prospectivity/{run_id}/targets` | Ranked target polygons | `[{rank, geom, score, uncertainty, area_km2, top_features:[{name,contribution}]}]` | ✅ |

### 9.3 Operations & Earth observation

| Method | Endpoint | Purpose | Response | Auth |
|---|---|---|---|---|
| GET | `/production` | Production time series | `?mine_id=&from=&to=&granularity=day|week|month` → `[{ts, mine_id, ore_tonnes, avg_mn_pct}]` | ✅ |
| POST | `/production` | Submit DPR (or bulk upload) | `{ts, mine_id, face_id, ore_tonnes, avg_mn_pct, shifts}` | `201` | ✅ Mine staff |
| GET | `/equipment` | Fleet with health | `?mine_id=` → `[{equip_id, asset_no, type, status, availability_30d, p_failure_14d}]` | ✅ |
| POST | `/equipment/{id}/events` | Log breakdown/service | `{event_type, ts, duration_hours, fault_code}` | `201` | ✅ Maintenance |
| GET | `/blasts` | Blast history & delays | `?mine_id=&from=&to=` | ✅ |
| GET | `/eo/timeseries` | EO variables per mine | `?mine_id=&from=&to=&vars=rainfall,ndvi,lst,soil_moisture` | ✅ |
| GET | `/eo/scenes` | Available imagery | `?mine_id=&sensor=&max_cloud=` → `[{scene_id, acquired_at, cog_uri, thumbnail}]` | ✅ |
| GET | `/eo/tiles/{scene_id}/{z}/{x}/{y}.png` | Imagery tiles | PNG | ✅ |
| GET | `/eo/change-detection` | OC footprint change | `?mine_id=&from=&to=` → `{pit_area_delta_m2, dump_area_delta_m2, geojson, implied_volume_note}` | ✅ |
| POST | `/eo/ingest` | Force EO refresh | `{mine_ids[], from, to}` | `202 {job_id}` | ✅ Admin |

### 9.4 Forecasting, risk & prescription (the core APIs)

| Method | Endpoint | Purpose | Request / Query | Response | Auth |
|---|---|---|---|---|---|
| GET | `/forecast` | Probabilistic production forecast | `?mine_id=&horizon=90` | `{mine_id, model_version, generated_at, series:[{date, p10, p50, p90}], period_summary:{target_t, p50_t, shortfall_prob, expected_shortfall_t}}` | ✅ |
| GET | `/forecast/drivers` | Ranked shortfall causes | `?mine_id=&period=2026-09` | `[{rank, driver, shap_value, direction, tonnes_impact, evidence:{...}, category:'weather'|'equipment'|'development'|'manpower'}]` | ✅ |
| GET | `/risk/summary` | Portfolio risk board | `?region_id=` | `[{mine_id, name, target, p50, shortfall_prob, top_driver, trend}]` | ✅ |
| GET | `/risk/derating-curve` | Learned rain response | `?mine_id=&driver=rainfall` | `{lags:[{lag_days, coefficient, ci_low, ci_high}], r2, interpretation}` | ✅ |
| GET | `/equipment/risk` | Failure risk ranking | `?mine_id=&horizon=14` | `[{equip_id, asset_no, p_failure, expected_downtime_h, drivers[]}]` | ✅ |
| POST | `/scenarios` | Create a what-if | `{name, mine_ids[], overrides:{rainfall_multiplier, equipment_status:{id:'down'}, extra_shifts, manpower_pct, target_override}}` | `201 {scenario_id}` | ✅ Planner |
| POST | `/scenarios/{id}/simulate` | Run the scenario | — | `{baseline:{p50, shortfall_prob}, scenario:{p50, shortfall_prob}, delta_t, series[]}` (target < 3 s) | ✅ |
| POST | `/optimise` | Get corrective actions | `{mine_id, horizon_weeks, objective_weights?, scenario_id?, constraints?}` | `{opt_id, solve_ms, actions:[{rank, action_type, title, description, delta_tonnes, delta_shortfall_prob, cost_estimate, payload}], combined:{delta_tonnes, shortfall_prob_after}}` | ✅ Planner |
| POST | `/actions/{id}/decide` | Accept/reject an action | `{decision:'accept'|'reject', reason?}` | `{status, schedule_version_id?}` | ✅ Mine Manager |
| POST | `/schedule/apply` | Commit revised schedule | `{opt_id, action_ids[], effective_from}` | `201 {version_id, notified_users[]}` | ✅ Mine Manager |
| GET | `/schedule/{mine_id}` | Current schedule | `?version=` | `{version_id, weeks:[{week, faces:[{face_id, tonnes, equipment[]}]}]}` | ✅ |
| GET | `/alerts` | Active alerts | `?mine_id=&severity=&status=` | `[alert]` | ✅ |
| POST | `/alerts/{id}/ack` | Acknowledge | `{note?}` | `200` | ✅ |
| WS | `/ws/alerts` | Live alert stream | — | server-push alert events | ✅ |
| GET | `/reconciliation` | Plan vs actual vs counterfactual | `?mine_id=&period=` | `{planned_t, predicted_t, actual_t, counterfactual_t, recovery_t, bias_factor, grade_variance}` | ✅ |
| GET | `/reports/{type}` | Generate PDF/XLSX | `?mine_id=&period=&format=pdf|xlsx` (`type` ∈ `monthly-review`, `reserve-statement`, `shift-briefing`) | file stream | ✅ |
| GET | `/models` | Model registry & metrics | — | `[{name, version, trained_at, metrics{}, features[], status}]` | ✅ |
| GET | `/health`, `/metrics` | Liveness, Prometheus | — | — | ❌ / internal |

### 9.5 API conventions to implement (small effort, big professionalism)

- **Pagination:** `?limit=&cursor=` on every list endpoint.
- **Idempotency:** `Idempotency-Key` header on POSTs that mutate schedules.
- **Errors:** RFC 7807 problem+json — `{type, title, status, detail, instance, request_id}`.
- **Versioning:** `/api/v1` in the path; deprecation via `Sunset` header.
- **Every ML response carries `model_version` and `generated_at`.** 🔷 When a judge asks "how do you know which model produced this number?", you point at the field.
- **Rate limits:** 100 req/min per user; 10/min on `/optimise` and `/scenarios/*/simulate`.

---

# PART C — EXECUTION

## 10. Complete User Flows

### 10.1 Flow A — Mine Manager (daily/weekly, the primary loop)

```
1.  Opens PWA on phone/desktop → JWT auth (SSO in prod) → role = MINE_MANAGER,
    mine_scope = [BLG]
2.  Home: single mine card — MTD tonnes vs pro-rata target, 30-day forecast
    fan chart (P10/P50/P90), shortfall probability gauge, active alerts count
3.  Backend: GET /forecast?mine_id=BLG&horizon=30  (served from Redis cache,
    refreshed 06:00 daily; < 200 ms)
4.  Taps the risk gauge → GET /forecast/drivers → ranked driver cards, each with
    category icon (weather / equipment / development / manpower), SHAP-derived
    tonnage impact, and the underlying evidence (rainfall chart, asset history)
5.  Taps "What can I do?" → POST /optimise {mine_id, horizon_weeks: 4}
    → Celery/inline MILP solve (< 3 s) → 3–5 ranked actions
6.  Reviews each action: expected +tonnes, new shortfall probability, cost,
    feasibility notes. Can toggle actions on/off and see the combined effect
    recomputed live.
7.  Accepts two actions → POST /schedule/apply
    → new schedule_version written; maintenance engineer and shift in-charges
      notified (WebSocket + email + SMS); audit_log entry created
8.  Downloads the shift-briefing one-pager → GET /reports/shift-briefing (PDF)
9.  [Through the month] Enters or uploads the DPR → POST /production
10. [Month end] Reconciliation screen: planned vs predicted vs actual vs
    counterfactual → recovery attributed to his decisions
```

### 10.2 Flow B — Chief Geologist (monthly/quarterly)

```
1.  Login (role = GEOLOGIST, scope = all mines)
2.  Reserve workspace → selects Balaghat → 3D block model loads
    (GET /mines/BLG/blocks?level=all&format=binary)
3.  Slices by level, filters Mn ≥ 35%, colours by confidence class
    → sees exactly where "Inferred" material dominates the plan
4.  Reserve funnel: Resource → Reserve → Accessible → EAR → Plan,
    with P10/P50/P90 bands and a "Reserve at Risk" figure
5.  Uploads new assay results from three completed holes
    → POST /mines/BLG/boreholes/import (CSV) → validation report
6.  Triggers re-estimation → POST /mines/BLG/block-model/run
    {method:'OK', then 'SGS', n_realisations:100}
    → Celery job (2–8 min) → progress via GET /jobs/{id}
7.  Compares model v12 vs v13: grade–tonnage curves overlaid, tonnage delta by
    confidence class, LOO cross-validation metrics, conditional-bias check
8.  Opens the regional prospectivity map, inspects the top 10 targets,
    reviews feature contributions and the uncertainty layer
9.  Marks 3 targets for the next drilling programme → exports GeoJSON + PDF
10. Generates the draft reserve statement → GET /reports/reserve-statement
    → reviews and digitally certifies (RQP sign-off recorded in audit_log)
```

### 10.3 Flow C — GM (Production) / Regional Head (weekly)

```
1.  Login (role = REGIONAL_HEAD, scope = region)
2.  Portfolio board: all mines in the region as rows —
    target, P50 forecast, shortfall probability, top driver, 7-day trend arrow
3.  Sorts by shortfall probability → two mines in red
4.  Opens cross-mine reallocation view: which equipment is idle/under-utilised
    at a low-risk mine and transferable to a high-risk one (with transit time)
5.  Creates a regional scenario → POST /scenarios
    {mine_ids:[...], overrides:{equipment_transfer:[{equip_id, from, to}]}}
    → POST /scenarios/{id}/simulate
6.  Sees regional aggregate improve; confirms that MinT reconciliation keeps
    mine-level and regional numbers consistent
7.  Issues the reallocation; system notifies both mine managers
8.  Exports the weekly review pack (PDF) for the Monday meeting
```

### 10.4 Flow D — Maintenance Engineer (daily)

```
1.  Login (role = MAINTENANCE)
2.  Fleet health board sorted by P(failure ≤ 14 d) descending
3.  For each high-risk asset: survival curve, hours since service, breakdown
    history, contributing factors, and — crucially — the *production* impact
    if it fails (linked from PULSE: "LHD-04 failure ⇒ −780 t this month")
4.  Pulls a service forward → POST /equipment/{id}/events {event_type:'planned_service'}
    → PULSE recomputes; shortfall probability updates
5.  Spares pre-positioning list generated for the top-5 risk assets
```

### 10.5 Flow E — HQ / Ministry (monthly, read-heavy)

```
1.  Login (role = EXECUTIVE) → national map, 11 mines, colour = shortfall risk
2.  Company annual outlook: cumulative actual + forecast fan vs the MoU target
3.  "Reserve at Risk" national figure with drill-down by mine
4.  Import-substitution view: forecast domestic supply vs demand (Phase 2)
5.  Exports the board pack
```

### 10.6 Flow F — Auditor / IBM (on demand, read-only)

```
1.  Login (role = AUDITOR, read-only, no scenario/optimise access)
2.  Reserve statement with full lineage: every block traces to its informing
    boreholes, assay lab refs, QA/QC flags, model version, variogram parameters,
    and the certifying RQP
3.  Audit log query: who changed which schedule, when, on what model evidence
4.  Export signed PDF
```

### 10.7 System (unattended) flows

```
NIGHTLY 02:00  eo_ingest  → new Sentinel scenes, IMERG, MODIS → COGs + timeseries
NIGHTLY 03:00  feature_build → assemble the feature store snapshot
DAILY   06:00  forecast_refresh → quantile forecasts, reconciliation, SHAP,
                                   alerts, WebSocket push, 06:15 email digest
WEEKLY  Sun    retrain → LightGBM + survival models; MLflow logs metrics;
                         auto-promote only if held-out pinball loss improves
                         ⚠️ never auto-promote on training loss
MONTHLY 1st    reconciliation → bias factors back into PRISM; drift report
                                (PSI on features, rolling MAE) → alert if drift
```

---

## 11. Security & Privacy

### 11.1 Threat model (state this — it shows you thought, not just listed)

| Asset | Threat | Impact |
|---|---|---|
| Reserve & grade data | Exfiltration by a competitor or for insider trading (**MOIL is a listed company** — reserve revisions are price-sensitive) | ⚠️ **This is the highest-severity risk in the whole system and most teams miss it.** Material non-public information. |
| Production forecasts | Leak ahead of quarterly results announcement | SEBI/insider-trading exposure |
| Mine layout & blast schedules | Misuse; explosives-related security | Safety/security |
| Employee attendance data | Personal data under DPDP Act 2023 | Privacy/compliance |
| The models themselves | Poisoning via forged DPR entries | Corrupted decisions |

### 11.2 Controls

**Authentication**

- JWT (short-lived access 15 min + rotating refresh) for the hackathon; **Keycloak with SSO/LDAP integration to MOIL's directory** in production.
- **MFA/OTP mandatory** for roles that can change plans or certify reserves.
- Password policy per CERT-In/NIC guidance; account lockout; no shared accounts.

**Authorisation — RBAC with mine-level scoping**

| Role | Read reserves | Edit geology | Read production | Enter production | Run scenarios | Apply schedule | Certify reserve | Admin |
|---|---|---|---|---|---|---|---|---|
| `MINE_STAFF` | own mine | ❌ | own mine | ✅ | ❌ | ❌ | ❌ | ❌ |
| `MINE_MANAGER` | own mine | ❌ | own mine | ✅ | ✅ | ✅ own mine | ❌ | ❌ |
| `PLANNER` | own mine | ❌ | own mine | ❌ | ✅ | propose only | ❌ | ❌ |
| `MAINTENANCE` | ❌ | ❌ | own mine | equipment only | ✅ | ❌ | ❌ | ❌ |
| `GEOLOGIST` | all | ✅ | all | ❌ | ✅ | ❌ | ⚠️ if RQP | ❌ |
| `REGIONAL_HEAD` | region | ❌ | region | ❌ | ✅ | ✅ region | ❌ | ❌ |
| `EXECUTIVE` | all | ❌ | all | ❌ | ✅ | ❌ | ❌ | ❌ |
| `AUDITOR` | all (RO) | ❌ | all (RO) | ❌ | ❌ | ❌ | ❌ | ❌ |
| `ADMIN` | ❌ by default | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

🔷 Note the deliberate choice: `ADMIN` manages users and infrastructure but has **no default data access** — separation of duties. Enforce authorisation at the **query level** (every ORM query filtered by `mine_scope`), not just in the UI.

**Encryption**

- TLS 1.3 in transit; HSTS; modern cipher suites only.
- AES-256 at rest: PostgreSQL TDE or encrypted volumes; MinIO server-side encryption.
- Column-level encryption (`pgcrypto`) for the most sensitive fields (assay results pre-publication, personal identifiers).
- Secrets in HashiCorp Vault / Doppler — **never** in `.env` committed to git. ⚠️ *Add a `gitleaks` pre-commit hook on day 1; a leaked key in your public SIH repo is an avoidable disaster.*

**API security**

- Input validation via Pydantic on every endpoint; strict types; max payload sizes.
- Parameterised queries only (SQLAlchemy) — no string-built SQL.
- Rate limiting + per-user quotas; CORS allow-list; CSRF protection on cookie flows.
- Security headers: CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy.
- File uploads: extension + MIME + magic-byte validation, size cap, virus scan (ClamAV), stored outside the web root in MinIO with signed short-lived URLs.

**Audit & retention**

- Append-only `audit_log`; every read of reserve data by an executive is logged too.
- Retention: operational time series 10 years (mining records have statutory retention); personal data minimised and retained only as long as needed (DPDP purpose limitation); logs 1 year hot, 5 years cold.
- Right to erasure handled for personal data (attendance) — **not** for statutory mining records, which are exempt as legally required retention.

**AI-specific security**

- Model artefacts versioned, hashed and access-controlled (a tampered model is a supply-chain attack).
- **Input sanity gates** on DPR entry: a single-day tonnage outside 5σ of the mine's history is quarantined for review, not silently ingested → defends against poisoning and fat-finger errors.
- LLM: prompt-injection defence — user text is never concatenated into system prompts; strict JSON-schema outputs; numeric validation (§6.6); no tool access beyond read-only whitelisted endpoints.
- Model cards published for each model: intended use, training data, metrics, known limitations. 🔷 A "Model Card" tab in the UI is a genuinely impressive, low-effort feature.

**Abuse prevention**

- Anomaly detection on user behaviour (bulk export of block data, off-hours access).
- Bulk export requires a second approver for `EXECUTIVE`/`AUDITOR` roles.
- Watermarked PDF exports with the requesting user's identity embedded.

### 11.3 Indian regulatory alignment (name these in the deck)

| Regulation / standard | Relevance | How we comply |
|---|---|---|
| **Digital Personal Data Protection Act, 2023** | Employee attendance, contractor data | Purpose limitation, data minimisation, consent notices, breach reporting, defined Data Fiduciary responsibilities |
| **CERT-In Directions, April 2022** | 6-hour incident reporting; 180-day log retention within India | Centralised logging in-country, documented IR runbook, NTP sync to NIC/NPL |
| **MeitY / GIGW 3.0** | Government website & app guidelines, accessibility | WCAG 2.1 AA, GIGW-compliant UI patterns |
| **MeghRaj (GI Cloud) policy** | Government cloud deployment | Deploy on NIC MeghRaj or a MeitY-empanelled CSP; data resident in India |
| **MCDR 2017 & MEMC Rules 2015** | Reserve reporting, mine plans, RQP certification | UNFC-aligned outputs; human certification workflow; auditable lineage |
| **Mines Act 1952 + DGMS circulars** | Safety, statutory roles, records | No AI in safety-critical decisions; statutory registers preserved |
| **SEBI (PIT) Regulations, 2015** | MOIL is listed; reserve/production data is price-sensitive | UPSI handling: access logging, need-to-know RBAC, trading-window awareness for report generation |
| **National Geospatial Policy 2022 / Guidelines 2021** | Liberalised geospatial data; restrictions on certain fine-resolution data for foreign entities | Use compliant data sources; keep high-resolution data in-country |
| **ISO/IEC 27001**, **ISO 27701** | Security & privacy management | Target certification path for production |

---

## 12. Scalability

⚠️ **REALITY CHECK #5 — answer the question honestly, because the honest answer is better.**
This is an **internal enterprise system**, not a consumer app. MOIL has ~5,000–6,000 employees total; realistic concurrent users are **50–300**, peaking maybe at 500 during a monthly review. If you claim "our architecture scales to 1 crore users," an experienced judge will conclude you don't understand your own product.

**Say instead:** *"The user axis scales trivially — the interesting scaling axes here are **data volume, spatial resolution, model count and mine count**. And the real 1-crore-scale story is a different product: extending this platform to every mining lease in India."* That answer will land far better.

### 12.1 The scaling ladder we actually care about

| Stage | Scope | Users | Data scale | Architecture |
|---|---|---|---|---|
| **S0 — Prototype** | 1–2 mines, synthetic + open data | 10 | ~10⁵ blocks, 5 yr daily ops | Docker Compose on one VM/laptop. Monolithic FastAPI. SQLite→Postgres. |
| **S1 — MOIL pilot** | 2 mines, real data | 50 | 10⁶ blocks, 10 yr ops, daily EO | Single VM (8 vCPU/32 GB) + managed Postgres. Redis cache. Celery 2 workers. |
| **S2 — MOIL-wide** | 11 mines | 300 concurrent | 10⁷ blocks, 100+ assets, 11 AOIs daily EO (~50 GB/yr COGs) | 3-node Kubernetes. Postgres primary + read replica. TimescaleDB compression + continuous aggregates. MinIO cluster. Celery 6–10 workers, separate queues (`eo`, `ml`, `optim`). CDN/Nginx cache for tiles. |
| **S3 — Multi-PSU (NMDC, HCL, state DGMs)** | ~200 mines | 5,000 | 10⁸+ blocks, multi-commodity | Multi-tenant with schema-per-tenant or RLS. Horizontal API pods behind an LB. Postgres partitioning by `mine_id` + time. Object storage for all rasters/realisations. Model registry serving per-tenant models. Kafka replaces Redis for ingestion if event volume demands. |
| **S4 — National platform** | All ~1,500 working mineral leases + public/citizen transparency portal | 10⁵–10⁷ (public read) | Petabyte EO archive | Split read path: a fully static, CDN-cached **public portal** (pre-rendered tiles + cached JSON) in front of the private analytical core. This is how you legitimately reach crore-scale — by separating public reads from the analytical workload, not by scaling Postgres to a crore of writers. |

### 12.2 Specific techniques and when to apply them

**Database**

- *Now:* correct indexes (GiST on geometries, BRIN on hypertable time columns, composite on `(mine_id, ts)`), `EXPLAIN ANALYZE` on the five hot queries.
- *S2:* TimescaleDB **continuous aggregates** for daily→weekly→monthly rollups (the dashboards then never touch raw rows); **compression policy** on data older than 90 days (typically 10–20× on time series); read replicas for dashboards.
- *S3:* declarative partitioning of `blocks` by `mine_id`, of hypertables by time; connection pooling with PgBouncer (⚠️ FastAPI + async can exhaust connections fast); move `block_realisations` entirely to Parquet/DuckDB.

**Caching**

- Redis for forecast payloads (TTL to the next 06:00 refresh), reserve summaries, tile metadata.
- HTTP `ETag` + `Cache-Control` on tiles and block payloads; browser + Nginx layers.
- Precompute, don't compute-on-request: the daily job writes results; the API reads them. 🔷 *This is why the dashboard feels instant in the demo.*

**Load balancing & compute**

- Stateless API pods → any LB works. Sticky sessions only for WebSockets (or move to Redis pub/sub fan-out).
- Separate Celery queues by workload class so a 10-minute SGS run never starves a 3-second MILP solve. ⚠️ This one decision prevents the most common "why did the demo hang" failure.

**Queues & streaming**

- Redis/Celery is sufficient to S2. Move to Kafka only at S3+ when you have real telemetry streams (IoT sensors at 1 Hz across 200 assets).

**Monolith vs microservices**

- 🔷 **Start as a modular monolith.** One FastAPI app, clean internal module boundaries (`geo`, `ops`, `forecast`, `optim`), separate routers. Extract to services only when a module needs independent scaling — realistically only the ML/optimisation workers and the tile server, which are *already* separate processes.
- ⚠️ Do not build microservices for the hackathon. Teams that do spend Day 2 debugging service discovery instead of building the demo.

**AI inference scaling**

- All models are CPU-friendly and **batch**, not real-time: forecasts are precomputed nightly for all mines in one job (seconds of compute).
- Only `/optimise` and `/scenarios/simulate` are on-demand — bound them with solver time limits, cache by parameter hash, and queue beyond a concurrency limit.
- Kriging/SGS is the heavy job: run as a Celery task, chunk by level, parallelise with `joblib`/Dask, cache the block model, and only re-run on new data.
- Model serving: no TorchServe/Triton needed. Load LightGBM/sklearn artefacts into the worker at startup.

---

## 13. Feasibility for SIH

### 13.1 The honest triage

| Component | 24–48 h feasible? | Verdict |
|---|---|---|
| Multi-mine map + KPI dashboard | ✅ Easy | **Build for real** |
| 3D block model viewer | ✅ Moderate (r3f `InstancedMesh`) | **Build for real** — biggest visual payoff per hour |
| Ordinary Kriging + variogram on synthetic holes | ✅ `PyKrige` makes this hours, not days | **Build for real** |
| SGS with 100 realisations | ⚠️ Doable but slow — **precompute offline**, ship the results | **Precompute, serve from DB** |
| Prospectivity ML on real GSI/NGDR + Sentinel layers | ⚠️ Data wrangling is the risk, not the model | **Build for real, but prepare the raster stack BEFORE the hackathon** |
| EO ingestion pipeline (live download during demo) | ❌ Venue Wi-Fi will betray you | **Build the pipeline, run it beforehand, cache all rasters and time series locally.** Show the code + a "refresh" that hits cache. |
| LightGBM quantile forecasting + SHAP | ✅ Hours | **Build for real** |
| Hierarchical reconciliation (MinT) | ✅ `HierarchicalForecast` — ~1 hour | **Build for real** — high impressiveness-to-effort ratio |
| Weibull equipment survival | ✅ `lifelines`, ~2 hours | **Build for real** |
| Weather derating curves | ✅ statsmodels OLS with lags, ~2 hours | **Build for real** — great slide |
| MILP prescriptive engine | ⚠️ 6–10 hours including debugging infeasibility | **Build for real, with a greedy fallback** |
| What-if simulator | ✅ Reuses the forecast + optimiser | **Build for real** — your demo centrepiece |
| Live IoT / SCADA integration | ❌ | **Mock.** Show the adapter interface and a sample payload. |
| Real MOIL data | ❌ Not public | **Synthetic, clearly labelled** (§13.3) |
| InSAR deformation processing | ❌ Hours of SAR processing | **Pre-render 2–3 example outputs as images; present as Phase 2** |
| Drone photogrammetry | ❌ | **Phase 2 slide only** |
| Keycloak SSO | ❌ Over-engineering | **JWT + roles is enough; state Keycloak as the prod path** |
| Kubernetes | ❌ | **Docker Compose. Say "K8s manifests are the production path."** |
| LLM narration | ✅ Local Ollama, 2 hours | **Optional — build only if ahead of schedule** |
| Auto-drafted MCDR return | ⚠️ | **One example PDF, generated for real, from one template** |

### 13.2 What must actually work in the demo (non-negotiable)

1. Map → mine selection → live KPIs
2. 3D block model with grade & confidence filtering, and the **EAR funnel**
3. Forecast fan chart with a real shortfall probability
4. Driver attribution panel with real SHAP values
5. **What-if slider → recompute in < 3 s → shortfall probability visibly moves**
6. "Suggest actions" → ranked actions from a real MILP solve
7. Apply action → schedule updates → audit log entry appears
8. One generated PDF

### 13.3 The data strategy — read this carefully, it decides your credibility

You will not get MOIL's borehole assays or DPRs. Handle it like a professional:

**Layer 1 — REAL open data (use as much as you can; this is your credibility)**

- GSI **Bhukosh / NGDR** geology, geophysics, geochemistry for the Nagpur–Bhandara–Balaghat belt ✅ real
- **Sentinel-2 / Sentinel-1 / MODIS / Landsat** over the actual MOIL lease areas ✅ real
- **GPM IMERG rainfall & IMD data** for those districts, 2015–2026 ✅ real — *your weather derating curves can be fitted on genuinely real rainfall*
- **Cartosat/SRTM DEM** ✅ real
- **IBM Indian Minerals Yearbook** manganese chapters — real national/state reserve figures and grade distributions to calibrate against ✅ real
- **MOIL public disclosures** — annual reports, monthly production press releases, investor presentations. ✅ **Real production time series at company level.** MOIL reported record production of **19.07 lakh tonnes in FY 2025-26**, up ~5.8% from 18.02 lakh tonnes in FY 2024-25 ✅ ([PSU Connect](https://www.psuconnect.in/psu-news/moil-limited-achieves-record-manganese-ore-production-in-fy-2025-26)), and has publicly targeted **3.5 million tonnes by FY30** ✅ ([Ferro-Alloys.com](https://www.ferro-alloys.com/en/News/Details/332496)). Monthly production figures appear in MOIL's monthly exchange filings — **scrape/compile these into a real monthly series.** 🔷 *Anchoring your synthetic mine-level data so that it sums to the real published company total is a superb move — it makes your demo verifiable.*

**Layer 2 — SYNTHETIC but physically calibrated (for what you cannot get)**
Write a generator (`scripts/generate_synthetic.py`) that produces:

- **Boreholes & assays:** simulate a folded, stratabound gondite ore band using a Gaussian random field with realistic anisotropy (long range along strike, short across the band), grade distribution calibrated to published Indian manganese grades (broadly ~10–54% Mn across ore types), plus realistic Fe/SiO₂/Al₂O₃ correlations and a density–grade relationship.
- **Daily production per mine (2018–2026):** base capacity per mine scaled so the 11 mines sum to MOIL's *published* annual totals; add weekday/holiday effects, a monsoon suppression term driven by **real IMERG rainfall**, equipment-downtime shocks, blast cadence, and a fiscal-Q4 push.
- **Equipment events:** Weibull-distributed times to failure per asset class with realistic MTBF; repair durations log-normal.
- **Blast records** with realistic delay causes and durations.

⚠️ **Then be transparent about it.** Put a small badge in the UI header: *"Demo data: real EO/geoscience + synthetic operational data calibrated to MOIL's published production."* Have one slide titled "Our data honesty." **Judges trust teams that disclose more than teams that claim.** And if a judge asks "is this real MOIL data?", the team that already answered it wins; the team that fumbles loses the round.

**Layer 3 — Ingestion adapters (built, demonstrated on a sample file)**

- DPR Excel template → validated import
- Datamine/Micromine block-model CSV export → import
- SAP PM equipment event CSV → import
Demonstrating "here's how your real data walks in on day one" answers the adoption question before it's asked.

### 13.4 What impresses judges (ranked by return on effort)

| Rank | Feature | Why it lands |
|---|---|---|
| 1 | **The what-if slider that moves the shortfall probability live** | Visceral, interactive, obviously not a static mockup |
| 2 | **Driver attribution ("*why*")** | Judges are tired of black boxes; this is the trust story |
| 3 | **The EAR / Reserve-at-Risk funnel** | A concept no other team will have. Original thinking. |
| 4 | **3D block model rotating with confidence colouring** | Pure visual impact; also proves you understand geology |
| 5 | **Prescriptive actions with quantified tonnage recovery** | Answers "so what?" |
| 6 | **Spatial cross-validation & honest metrics** | Domain-expert judges will specifically probe for this |
| 7 | **Underground vs opencast rain-response comparison** | Proves genuine mining domain understanding |
| 8 | **Data-honesty badge + model cards** | Rare, memorable, disarming |
| 9 | **`docker compose up` reproducibility** | Signals engineering discipline |
| 10 | **Regulator-shaped outputs (UNFC/MCDR draft)** | Adoption realism |

### 13.5 What to cut ruthlessly

❌ Blockchain (there is no distributed-trust problem here) · ❌ AR/VR mine walkthrough · ❌ A generic chatbot · ❌ Real-time IoT · ❌ Kubernetes · ❌ Microservices · ❌ Custom deep-learning architectures · ❌ Mobile native apps (PWA is enough) · ❌ Social/gamification features · ❌ Multi-language UI (Phase 2) · ❌ Rebuilding a CAD/mine-design tool

### 13.6 Minimum Working Demo (if everything goes wrong, ship this)

```
A single-mine (Balaghat) view with:
  • Real IMERG rainfall time series
  • Synthetic-but-calibrated daily production, 2018–2026
  • A LightGBM quantile forecast with a P10/P50/P90 fan and shortfall probability
  • A SHAP driver panel
  • A rainfall what-if slider
  • Three greedy-heuristic corrective actions with Δtonnes
  • A static pre-rendered 3D block model image + grade-tonnage curve
That is buildable by two people in 12 hours and still tells the whole story.
Everything else is upside. Build the MWD first, then expand. ⚠️ Do not build
outward-in; build this core, get it working end-to-end, then add.
```

---

## 14. Development Roadmap

### 14.1 Pre-hackathon (the 2–3 weeks that actually decide the outcome)

⚠️ **REALITY CHECK #6:** SIH grand finales are won in the *preparation*, not the 36 hours. Everything below is legitimate preparation.

| Week | Work | Owner | Output |
|---|---|---|---|
| **W−3** | Domain immersion: read MOIL annual report + investor deck, IBM Indian Minerals Yearbook manganese chapter, GSI Sausar Group literature, MCDR/UNFC basics. Talk to any mining-engineering faculty/student you can find. | Everyone (2 h each) | Shared glossary + 20 domain facts you can quote |
| **W−3** | Data acquisition: register on NGDR/Bhukosh, Copernicus Data Space, NASA Earthdata; download and clip all EO/geoscience layers for the AOI; compile MOIL's monthly published production into a CSV | AI/ML + DevOps | `data/raw/` fully populated **offline** |
| **W−2** | Build & tune the synthetic data generator against real published totals | AI/ML | `data/processed/` + a reproducible seed |
| **W−2** | Repo skeleton, Docker Compose, DB schema + Alembic migrations, seed script, CI | Backend + DevOps | `docker compose up` gives a running empty app |
| **W−2** | Design system: Figma wireframes for all 6 screens, colour tokens, component inventory | UI/UX | Clickable prototype |
| **W−1** | Train and freeze the heavy models offline: SGS realisations, prospectivity raster, variogram fits. Commit artefacts. | AI/ML | `models/` + `artifacts/` |
| **W−1** | Full dry-run build of the MWD (§13.6); rehearse the demo twice; record a backup video | Everyone | Working baseline + fallback video |

🔷 **The backup video is not optional.** Record a 4-minute screen capture of the working demo. If the venue network, your laptop, or a last-minute merge breaks the live demo, you present the video and keep your composure. Teams lose finals to laptop failures every year.

### 14.2 The 36-hour hackathon plan

**HOUR 0–4 — Foundation (everyone)**

- Clone the prepared skeleton, `docker compose up`, verify green
- Load seed data (synthetic + prepared EO)
- Freeze the API contract (OpenAPI schema agreed and committed) ⚠️ *Do this in hour 2, not hour 20. The single biggest time sink in hackathons is frontend and backend disagreeing on shapes.*
- Frontend: layout shell, routing, auth stub, design tokens
- **Output:** app boots, login works, empty screens routed

**HOUR 4–10 — Core data + reserve half**

- Backend: `/mines`, `/production`, `/eo/timeseries`, `/mines/{id}/blocks`
- AI/ML: kriging block model on synthetic holes → load blocks into DB; grade–tonnage curves; confidence classification
- Frontend: map view with 11 mines + KPI cards; production charts
- **Output:** map and reserve data visible end-to-end

**HOUR 10–16 — 3D + forecasting**

- Frontend: r3f 3D block viewer with level slicing, grade/confidence colouring, `InstancedMesh`
- AI/ML: LightGBM quantile forecast + MinT reconciliation + SHAP; write to `forecasts` / `forecast_drivers`
- Backend: `/forecast`, `/forecast/drivers`, `/risk/summary`
- **Output:** 3D model rotates; forecast fan chart renders with real numbers

**HOUR 16–20 — SLEEP (in shifts). ⚠️ Yes, this is in the plan.**
Rotate: 3 sleep 16–20, 3 sleep 20–24. Teams that skip sleep entirely present badly at hour 34, and presentation is 40% of the score.

**HOUR 20–26 — Risk + prescription**

- AI/ML: Weibull equipment risk; weather derating curves; shortfall Monte Carlo
- Backend: MILP in `optim_svc` + greedy fallback; `/optimise`, `/scenarios`, `/scenarios/{id}/simulate`
- Frontend: driver panel, equipment risk board, EAR funnel
- **Output:** "Suggest actions" returns real ranked actions

**HOUR 26–30 — Integration & the demo path**

- Wire the what-if sliders end-to-end; alerts + WebSocket; `/schedule/apply` + audit log
- PDF report generation (one template, done well)
- Prospectivity map layer on the map view
- **Output:** the full §16 demo script runs start to finish

**HOUR 30–34 — Polish, harden, rehearse**

- Loading skeletons, empty states, error boundaries, mobile responsiveness
- Seed the demo to a known-good state; add a **"Reset demo"** button ⚠️ *(essential — you will demo more than once)*
- Performance: cache warm-up so every demo click is < 1 s
- Rehearse the 5-minute script three times, with the Q&A drill
- **Output:** demo is boring to run because it always works

**HOUR 34–36 — Freeze**

- Code freeze. No new features. ⚠️ **Enforce this.** The classic finale disaster is a feature merged at hour 35 that breaks the demo.
- Final deck, README, architecture diagram, backup video verified, laptops charged, offline mode tested

### 14.3 If you have 4 weeks instead (internal hackathon / pre-finale build)

| Week | Focus | Output |
|---|---|---|
| **W1** | Data & domain: acquire all EO/geoscience layers, build & validate the synthetic generator, DB schema, ingestion adapters, repo + CI | Reproducible dataset; schema migrated; adapters tested |
| **W2** | PRISM: variogram → OK → SGS → block model → confidence classification → prospectivity model with spatial CV; MLflow experiments | Block model + prospectivity raster + a metrics report you can defend |
| **W3** | PULSE + NUDGE: forecasting, reconciliation, SHAP, survival models, derating curves, MILP + fallback; all APIs | `/forecast`, `/optimise` working with real metrics |
| **W4** | Frontend build-out, integration, security (RBAC/audit), reports, performance, documentation, demo rehearsal, backup video | Shipped product + rehearsed demo |

---

## 15. Team Division (6 members)

🔷 **Principle:** every member owns a *vertical slice they can demo*, not just a horizontal layer. That way, if one person is blocked, the others still have demonstrable output — and every member can answer judges' questions about a piece of the product.

### Member 1 — Frontend Lead (dashboard & visualisation)
**Builds:** app shell, routing, auth flow, design system integration; map view (MapLibre + deck.gl) with lease polygons and KPI chips; all charts (forecast fan, grade–tonnage, derating curve, driver bars); alerts UI; responsive/PWA behaviour; loading/empty/error states.
**Owns the demo of:** screens 1, 3, 4.
**Depends on:** frozen API contract (hour 2), design tokens from M5.
**Deliverable:** a fast, professional-looking dashboard that never shows a raw JSON error.

### Member 2 — Frontend/3D & Interaction Specialist
**Builds:** the 3D block-model viewer (react-three-fiber, `InstancedMesh`, level slicing, clipping planes, grade/confidence colour ramps, hover tooltips, borehole traces); the EAR funnel visualisation; the **what-if scenario panel** with live recompute; the action-selection UI with combined-effect recomputation.
**Owns the demo of:** the two "wow" moments (3D model, what-if slider).
**Depends on:** `/mines/{id}/blocks` and `/scenarios/*/simulate`.
**Deliverable:** 200k blocks at 60 fps and sub-3-second scenario response.
🔷 *This role exists as a separate person deliberately — the 3D viewer is where hackathon teams either shine or sink hours.*

### Member 3 — Backend Lead
**Builds:** FastAPI application, module structure, SQLAlchemy models + Alembic migrations, all CRUD and query endpoints, JWT auth + RBAC + `mine_scope` enforcement, audit logging, Celery wiring, WebSocket alerts, report generation (PDF/XLSX), ingestion adapters, OpenAPI contract ownership, pytest suite.
**Owns the demo of:** the API docs page (`/docs`) — 🔷 *showing a clean, complete OpenAPI spec to a technical judge is a strong, under-used move*, plus the audit log and RBAC story.
**Depends on:** DB schema from M4.
**Deliverable:** every endpoint in §9 working, documented and tested.

### Member 4 — AI/ML Engineer: PRISM (reserves & geospatial)
**Builds:** synthetic borehole generator; desurvey + compositing; variogram fitting; Ordinary Kriging; SGS realisations; block model + confidence/UNFC classification; grade–tonnage curves; the accessibility (`A_b`) reachability model; the prospectivity pipeline (raster stack, PU-learning/XGBoost, **spatial block CV**, calibration, uncertainty, target ranking); EO ingestion pipeline (Sentinel/IMERG/MODIS → COGs + time series).
**Owns the demo of:** the reserve half + the honest-metrics slide.
**Deliverable:** block model in the DB, prospectivity COG in MinIO, a defensible metrics report.

### Member 5 — AI/ML Engineer: PULSE & NUDGE (forecasting & optimisation)
**Builds:** feature engineering pipeline; baselines (B0/B1) *and* the LightGBM quantile models; MinT hierarchical reconciliation; shortfall Monte Carlo; SHAP attribution; Weibull/GBM equipment survival; distributed-lag weather derating curves; the MILP formulation in OR-Tools + greedy fallback; scenario simulation; MLflow tracking.
**Owns the demo of:** the forecast, driver attribution and prescriptive-action story — *the core of the pitch*.
**Deliverable:** `/forecast` and `/optimise` backed by real, metric-validated models.

### Member 6 — Data/DevOps + Integration & Presentation Lead
**Builds:** Docker Compose stack (Postgres+PostGIS+Timescale, Redis, MinIO, TiTiler, MLflow, API, worker, frontend); seed and **demo-reset** scripts; GitHub Actions CI; monitoring; deployment; data acquisition and licensing/attribution notes; the ingestion adapter templates.
**Also owns:** the pitch deck, the architecture diagram, the demo script, the Q&A preparation drill, the backup video, and the README.
**Owns the demo of:** the opening framing and the closing business/adoption case.
🔷 *This is the highest-leverage role in an SIH team and the one most often under-resourced. The best technical solution presented badly loses to a good solution presented brilliantly.*

### Member 5b/UX note
If your team has a dedicated designer instead of a second frontend developer, swap M2's non-3D work to them: Figma wireframes for all screens in W−2, colour/typography tokens, iconography, the persona cards, and the user-journey slide. Then M1 absorbs the 3D viewer. 🔷 Do the wireframes **before** the hackathon regardless of who does them.

### Coordination rules (worth writing on the wall)

1. **API contract frozen at hour 2.** Any change requires both leads to agree and update the OpenAPI file.
2. **Trunk-based development**, small PRs, `main` always demo-able. Feature flags for anything half-built.
3. **Stand-up every 4 hours, 5 minutes, standing.** State: done / doing / blocked.
4. **Integration checkpoints at hours 10, 20, 26, 30.** At each, the full demo path must run end-to-end, even if with stub data.
5. **Code freeze at hour 34. No exceptions.**
6. **Anyone blocked for more than 45 minutes escalates.** Sunk-cost debugging kills hackathon teams.

---

# PART D — PITCH

## 16. Prototype / Demo Design

### 16.1 The first screen (you get 8 seconds)

**Do NOT open on a login page.** Have a pre-authenticated session ready.

Open on the **National Command View**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ OreSight  खनिज दृष्टि          [Demo data: real EO + calibrated synthetic]  │
├──────────────┬──────────────┬──────────────┬──────────────┬─────────────────┤
│ FY26 TARGET  │ ACHIEVED MTD │ FORECAST FY  │ RESERVE AT   │ MINES AT RISK   │
│  20.10 LT    │  8.42 LT     │ 19.4 LT      │ RISK         │   3 of 11       │
│              │  ▲ 4.1% YoY  │ (P50)        │  2.8 LT      │   ● ● ●         │
│              │              │ P10 18.1 ─   │  of 14.2 LT  │                 │
│              │              │ P90 20.3     │  accessible  │                 │
├──────────────┴──────────────┴──────────────┴──────────────┴─────────────────┤
│                                                                              │
│    [ MAP: Maharashtra + MP, 11 MOIL mines as graduated circles ]             │
│      ● Balaghat   RED    P(shortfall) 0.71                                   │
│      ● Dongri Bz  AMBER  P(shortfall) 0.48                                   │
│      ● Gumgaon    AMBER  P(shortfall) 0.44                                   │
│      ● Kandri, Munsar, Beldongri, Chikla, Ukwa, Sitapatore, Tirodi  GREEN    │
│                                                                              │
│    Layers: [Mines] [Leases] [Prospectivity] [Rainfall 7d] [NDVI] [Sentinel-2]│
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ ⚠ 3 ACTIVE ALERTS      Balaghat: shortfall risk ↑ 0.44 → 0.71 (rain + LHD-04)│
└─────────────────────────────────────────────────────────────────────────────┘
```

Everything a judge needs to understand the product is on this one screen: scale (11 mines), the number nobody else has (**Reserve at Risk**), probabilistic thinking (P10/P50/P90), and live risk.

### 16.2 The 5-minute demo script (rehearse this verbatim)

**[0:00–0:35] The hook — problem, in numbers**
> "MOIL produced a record **19.07 lakh tonnes of manganese ore in FY 2025-26** and is targeting **3.5 million tonnes by 2030**. That's a 45-plus percent increase. Right now, reserve estimation is manual and annual, and production planning runs on spreadsheets and experience. The gap between those two is where shortfalls are born — and today they're explained in the monthly review, not prevented. We built OreSight to close that gap."

**[0:35–1:20] Reserve — "the ore we have"**

- Click Balaghat → 3D block model loads and rotates.
- Slice by level; colour by grade; then switch to colour-by-confidence.
> "This is a 3D block model built from borehole assays using ordinary kriging, with 100 sequential Gaussian simulations for uncertainty. Blue is Measured, amber Indicated, grey Inferred — and notice how much of what the plan depends on next quarter is *amber*. Alongside it, this heat map is our regional prospectivity model over the Sausar belt — trained on real GSI geophysics and Sentinel-2 and ASTER imagery, validated with **spatial** block cross-validation, not random k-fold, because spatial autocorrelation would have inflated our AUC to a meaningless 0.98."

**[1:20–2:00] The EAR funnel — the original idea**

- Show the funnel: Resource → Reserve → Accessible → EAR → Plan.
> "Here is where we're different from every mine-planning package. A reserve isn't production. This block" *(click one)* "is high-grade — but it sits behind a cross-cut that's nine days behind schedule, and its haulage route floods. So its **accessibility** is 0.35 and its **constraint availability** is 0.72. Multiply through, across every block, and MOIL's 14.2 lakh tonnes of accessible reserve becomes **11.4 lakh tonnes of Effective Accessible Reserve**. That 2.8 lakh tonne gap is the Reserve at Risk — and no existing product computes it."

**[2:00–3:00] Shortfall — "will we get it out?"**

- Open Balaghat's forecast: the fan chart, target line, shortfall gauge at 0.71.
- Open the driver panel.
> "This is a probabilistic forecast, not a point estimate — P10, P50, P90, reconciled so the mine's number and the company's number are mathematically consistent. Balaghat has a 71% probability of missing this month's target. And here's *why*, ranked by SHAP contribution: 128 mm of forecast rain, LHD-04 with a 63% chance of failing in 14 days, and Level 6 SE development nine days behind."
- Click the rainfall driver → the derating curve appears.
> "This curve is learned from ten years of **real** GPM satellite rainfall against production. At Dongri Buzurg — opencast — 50 mm of rain costs 9% of capacity the same day. At Balaghat — underground, 383 metres deep — it costs 3%, and it arrives two days later, through haulage, not extraction. No rain gauge required. That distinction is invisible in a spreadsheet."

**[3:00–4:00] ⭐ THE WOW MOMENT — what-if and prescription**

- Drag the rainfall slider from *Normal* to *+40%*.
> "Watch the whole portfolio respond."
- *(All 11 mines recolour; the national forecast fan widens; Reserve at Risk jumps; three mines flip to red. Under 3 seconds.)*
- Click **"Suggest corrective actions."**
> "Now the system doesn't just warn — it prescribes. This is a mixed-integer optimisation over faces, crews and equipment, subject to development readiness, grade-blend commitments, hoisting capacity and blasting cadence — solved in 1.4 seconds."
- Three actions appear with Δtonnes and Δ probability. Toggle them on.
> "Move two crews to Level 5 North-West — plus 1,450 tonnes. Pull LHD-04's service forward — plus 520. Advance the Stope 5-2 blast round — plus 380. Together, shortfall probability falls from 0.71 to 0.19."
- Click **Apply**.
> "One click writes a new schedule version, notifies the maintenance engineer and both shift in-charges, and logs the decision with its full model justification to an immutable audit trail — because this is a listed PSU and every plan change has to be defensible."

**[4:00–4:40] Credibility & honesty**
> "Two things we want to be explicit about. First, our data: the geoscience layers, satellite imagery and rainfall are **real**; MOIL's borehole assays and daily production reports are commercially confidential, so our operational data is synthetic — but calibrated so that it sums to MOIL's actual published annual production. It's badged as such in the interface. Second, our metrics: our monthly forecast WAPE is *X*%, our 80% prediction intervals achieve *Y*% coverage, and our prospectivity AUC under spatial cross-validation is *Z* — not the inflated number random splitting would give. Every model is registered in MLflow with its metrics and a model card. And every model runs on CPU — this deploys on a server inside a mine's own IT room, with no GPU and no internet dependency."

**[4:40–5:00] Close**
> "Every component is open-source: zero licence cost, deployable on MeghRaj or on-premise, DPDP- and CERT-In-aligned, with UNFC-shaped outputs so a geologist can certify them directly into the MCDR return. And the same engine works for NMDC's iron ore or HCL's copper tomorrow — MOIL is where it starts, not where it ends."

### 16.3 Q&A preparation — the questions you will be asked

| Likely question | Your answer |
|---|---|
| "Is this real MOIL data?" | Answered proactively at 4:00. Real EO + geoscience; synthetic operational data calibrated to published totals; badged in the UI. |
| "Rainfall doesn't find manganese. Why is it in the problem statement?" | ⭐ "It doesn't, and we say so. We split satellite use into geological remote sensing — ASTER/Sentinel SWIR indices, lineaments, geophysics — for targeting, and climate variables for production constraints. Conflating the two is the trap in this statement." *(This answer alone can win you the round.)* |
| "How accurate is your model?" | Give numbers with baselines and intervals, plus coverage. Never say "95% accurate." |
| "How do you handle sparse boreholes?" | Kriging with a fitted variogram; simulation for uncertainty; confidence classes so the user *sees* where the model is guessing; and expected-information-gain drill targeting as Phase 2. |
| "What if the model is wrong?" | Three defences: probabilistic outputs (we express uncertainty, not certainty), human-in-the-loop (nothing auto-applies), and monthly reconciliation with counterfactual accounting that measures our own error and corrects bias. |
| "Why not just use Datamine?" | "We complement it — we import its block models. Datamine has no probabilistic production forecasting, no EO integration and no prescriptive optimisation. We add the operational half it structurally lacks." |
| "Can MOIL actually deploy this?" | Open-source stack, ₹0 licences, CPU-only, air-gap-capable, Docker/K8s, MeghRaj-deployable, ingestion adapters for their existing DPR/SAP/block-model formats. |
| "What about safety and blasting?" | "We deliberately do not generate blast designs — that's DGMS-regulated and safety-critical. We optimise blast *scheduling* within approved designs and predict delay risk." |
| "Isn't this just a dashboard?" | "A dashboard shows you what happened. This computes a quantity that doesn't otherwise exist — Effective Accessible Reserve — forecasts a distribution, attributes causes, and solves an optimisation to prescribe action. The dashboard is the surface." |
| "How do you prove value?" | The counterfactual reconciliation loop: every applied action is scored against what the model predicted would have happened without it. |

### 16.4 Physical demo hygiene

- Two laptops, both with the full stack running locally. Screen mirror tested.
- Offline mode verified: **assume the venue Wi-Fi fails.**
- "Reset demo" button; run it before every presentation.
- Backup video (4 min) on both laptops and a pen drive.
- One printed A3 architecture diagram — judges walking the floor engage with paper.
- One-page leave-behind: problem, EAR concept, architecture, metrics, adoption path.

---

## 17. Innovation — What You Can Honestly Claim

| Type | Innovation | Why it's real, not a buzzword |
|---|---|---|
| **Conceptual / Technical** | **Effective Accessible Reserve (EAR)** — reserve as a probabilistic quantity conditioned on the operational constraint model | We searched the commercial and academic landscape: resource estimation and mine scheduling are separate disciplines with separate software. Formalising `EAR = Σ T·G·A·R·C` with distributions over `A` and `C`, and surfacing "Reserve at Risk," is a genuinely new operational metric. It is also *simple enough to be adopted* — that's what makes it valuable rather than merely clever. |
| **Technical** | **Hierarchically-reconciled probabilistic production forecasting** (face → mine → region → company, MinT) | Solves a real organisational failure: today the mine's forecast and HQ's forecast are two different numbers produced by two different methods. Reconciliation makes them provably consistent *and* improves accuracy. |
| **Technical (EO)** | **Learned per-mine weather derating curves from satellite rainfall** | Converts "the monsoon hurt us" into a quantified, lagged, per-mine response function — fitted on real GPM/IMERG data, so it works at mines with no rain gauge, and distinguishes underground from opencast sensitivity. |
| **AI** | **Attribution-first design + counterfactual value accounting** | Every alert carries SHAP-ranked, human-readable drivers; every applied action is scored against a counterfactual. This is what converts a pilot into a system that survives year two in a PSU. |
| **AI (methodological honesty)** | **Spatial block cross-validation and PU-learning in prospectivity; kriging retained where it beats ML** | Choosing the *right* method and proving it with the *right* validation is more innovative in practice than stacking a transformer on sparse data. We can show the comparison. |
| **Process** | **UNFC/MCDR-shaped, human-certified outputs with full lineage** | Turns a demo into something a Recognised Qualified Person can actually sign. Adoption innovation, which is where most govt-tech dies. |
| **Process** | **Data-honesty badging and published model cards in the product itself** | Rare in government AI. It builds institutional trust and makes the system auditable by design. |
| **UX** | **Decision-shaped interface**: risk → *why* → *what to do* → simulate → apply, in four taps, on a phone at 6:45 AM | Existing mining software is built for specialists at a desktop workstation. This is built for the person who actually makes the call, in the environment they make it in. |
| **UX** | **The what-if slider on a portfolio of mines** | Makes uncertainty tangible for non-technical decision-makers. Converts a statistical concept into a physical control. |
| **Scalability / Deployment** | **CPU-only, air-gap-capable, ₹0-licence, multi-commodity architecture** | Not a marketing claim — it's an explicit engineering constraint we designed to, and it is precisely what makes replication to NMDC/HCL/state DGMs plausible rather than aspirational. |

⚠️ **Do NOT claim:** "world's first AI mining platform" (false), "99% accurate" (false and unprovable), "blockchain-secured" (irrelevant), "digital twin" without qualification (we have a *decision* twin, not a physics twin — say so precisely). Overclaiming is the fastest way to lose a technically literate judge.

---

## 18. Business & Deployment Model

### 18.1 Who pays?

| Payer | Rationale | Vehicle |
|---|---|---|
| **MOIL Limited** (primary) | Direct beneficiary; it is a profitable, cash-generating Miniratna PSU with an explicit growth target | Capex from its own IT/R&D budget; standard PSU tendering (GeM / open tender) |
| **NMET** (National Mineral Exploration Trust) | Funds exploration activity nationally; the prospectivity half fits its mandate squarely | Project proposal under NMET's exploration-technology window |
| **Ministry of Mines / Ministry of Steel** | Import substitution, National Critical Mineral Mission alignment | Scheme funding for a replicable national platform |
| **State DGMs (MP, Maharashtra, Odisha, Karnataka)** | Revenue assurance and lease monitoring | State mineral fund / DMF |
| **Other mining PSUs** (NMDC, HCL, KIOCL) | Same problem, different commodity | Licence or shared-services model |

### 18.2 Deployment model (recommended: **open-core with a government services wrapper**)

- **Core platform: open-source (Apache 2.0).** Publishes on the government's open-source repository; other PSUs and states can adopt freely. This is politically attractive (aligns with MeitY's open-source policy) and it maximises adoption.
- **Revenue/sustainability: services, not licences** — deployment, data onboarding, model calibration per mine, training, AMC, and custom integrations.
- **Hosting options:** (a) MOIL on-premise data centre (most likely, given price-sensitive reserve data); (b) NIC MeghRaj; (c) a MeitY-empanelled CSP in an Indian region. Architecture supports all three unchanged.

### 18.3 Adoption pathway (be concrete — judges ask)

```
Phase 0 (0–3 mo)   Pilot MoU with MOIL for 2 mines (1 UG + 1 OC, e.g. Balaghat +
                   Dongri Buzurg). Load 5 years of historical DPR + assay data.
                   Success metric: forecast WAPE vs their current planning error.
Phase 1 (3–9 mo)   Extend to all 11 mines. Integrate SAP PM and the survey/CAD
                   pipeline. Train ~40 users. Run in "shadow mode" — the system
                   forecasts, the humans plan as usual, and we compare monthly.
                   ⚠️ Shadow mode is the single most important adoption tactic:
                   it builds evidence without asking anyone to trust it yet.
Phase 2 (9–18 mo)  Go live as the planning system of record. Add drone
                   photogrammetry reconciliation and InSAR monitoring.
                   Auto-drafted MCDR returns.
Phase 3 (18–36 mo) Replicate to NMDC / HCL / state DGMs as a multi-tenant
                   "Mineral Production Assurance" platform under Ministry of
                   Mines sponsorship.
```

### 18.4 Cost model (order of magnitude 🔶 — label these as estimates)

| Item | Year 1 | Steady state (annual) |
|---|---|---|
| Software licences | ₹0 | ₹0 |
| Infrastructure (on-prem server or MeghRaj) | ₹15–25 L | ₹8–15 L |
| Development & customisation (team of 5–6) | ₹60–90 L | — |
| Data onboarding & model calibration (11 mines) | ₹15–20 L | ₹3–5 L |
| Training & change management | ₹5–8 L | ₹2–3 L |
| Maintenance & support (AMC ~18% of build) | — | ₹12–18 L |
| **Total** | **₹95 L – 1.4 Cr** | **₹25–40 L** |

**Value case:** MOIL produced 19.07 lakh tonnes in FY26 ✅. A **1% improvement in realised production** ≈ **19,000 tonnes**. 🔶 At an assumed realisation in the ₹8,000–12,000/tonne range for saleable manganese ore grades (validate against MOIL's published price notifications), that is **≈ ₹15–23 crore of additional annual revenue** — i.e. the system pays for itself many times over on a fraction of a percent of improvement. 🔷 Present it exactly this way: *"we don't need to be right about everything; we need to be right about one percent."* That framing is far more persuasive than a claimed 15% improvement.

### 18.5 Long-term sustainability

- **Institutional home:** hand the codebase to MOIL's IT department or an academic partner (IIT/NIT Nagpur or a CSIR lab) with a maintenance MoU. Government software dies when it has no owner.
- **Open-source community:** the geoscience-ML community actively contributes to tools like GemPy and PyKrige; an Indian mining-analytics open-source project would attract contributors.
- **Capability transfer:** train MOIL geologists and planners to retrain models themselves — the MLflow + notebook workflow is designed for this. A system only the vendor can operate is a system that gets abandoned.

---

## 19. Risks & Failure Cases

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **R1** | **Real borehole/production data never becomes available** | High | High | Synthetic-but-calibrated data (§13.3) + real open data everywhere possible; build ingestion adapters so real data plugs in on day one; be transparent in the UI |
| **R2** | Historical data is too short/sparse for reliable forecasting (e.g. 2 years only) | Medium | High | Hierarchical models borrow strength across mines; strong priors; start with statistical baselines that need less data; report honest uncertainty rather than fabricating precision |
| **R3** | **Model overfits / spurious spatial accuracy** in prospectivity | High if careless | High (credibility) | Spatial block CV, PU-learning, uncertainty layer, ablation with/without leaky features, publish honest metrics |
| **R4** | Forecast confidently wrong during a regime change (new mine, new equipment, policy shift) | Medium | Medium | Drift monitoring (PSI, rolling MAE), auto-widen intervals under drift, alert the operator that the model is out of distribution, human override always available |
| **R5** | Optimiser returns an infeasible or operationally absurd plan | Medium | High (trust) | Soft constraints with penalties instead of hard infeasibility; greedy fallback; feasibility explanation ("this action is blocked because …"); mandatory human approval; a churn penalty so it doesn't reshuffle crews weekly |
| **R6** | **Users don't adopt it** — the veteran manager keeps using his spreadsheet | **High — the biggest real risk** | Fatal | Shadow-mode pilot; explainability first; the system *proposes*, the human *decides*; make the first version save him work (auto-generated DPR rollups and review packs) before asking him to trust its forecasts; recruit one enthusiastic mine manager as a champion |
| **R7** | Data-entry quality is poor (DPRs filled at month end from memory) | High | High | Input validation and 5σ quarantine; mobile-first shift entry that takes 30 seconds; weighbridge cross-checks; EO cross-checks for opencast; surface data-quality scores per mine so it becomes visible and improvable |
| **R8** | Cloud/EO API changes or GEE licensing shifts | Medium | Medium | Abstract EO access behind an interface; primary path is STAC + Copernicus (open, stable); cache all rasters locally; Bhoonidhi/Bhuvan as sovereign fallback |
| **R9** | **Security breach exposes price-sensitive reserve data** | Low | Severe (SEBI/regulatory) | §11 controls; on-prem deployment; strict RBAC + full read auditing; UPSI handling procedure; bulk-export dual approval |
| **R10** | AI-generated narrative states a wrong number | Medium if unguarded | High | LLM never computes; JSON-schema outputs; numeric validation against the source payload with deterministic fallback; AI-generated content clearly labelled |
| **R11** | Team can't finish in 36 hours | Medium | Fatal for SIH | MWD-first strategy (§13.6); pre-hackathon preparation; code freeze at h34; backup video; feature flags |
| **R12** | Demo fails live (network, laptop, merge) | Medium | Fatal for SIH | Fully local stack, two laptops, reset script, offline mode, backup video, printed diagram |
| **R13** | Judges see it as "just another dashboard" | Medium | High | Lead with EAR and the what-if moment, not with the map; explicitly compare against Datamine/Leapfrog/DISPATCH; show the MILP formulation |
| **R14** | Scope creep into a full mine-planning suite | High | Medium | Written non-goals: *we do not do CAD mine design, ventilation simulation, blast design, financial modelling, or geotechnical analysis* |
| **R15** | Safety-critical misuse (someone treats an advisory as an instruction) | Low | Severe | Explicit scope statements in the UI; no safety-critical outputs; statutory decisions remain with statutory role-holders; disclaimers on generated documents |
| **R16** | Model bias systematically favours easy-to-mine, low-grade material | Medium | Medium | Grade-blend constraints in the MILP; monitor realised grade vs plan in reconciliation; multi-objective weighting exposed to the planner |

---

## 20. Final Solution Blueprint

```
════════════════════════════════════════════════════════════════════════════════
PROBLEM
  MOIL's production plans rest on an annually-updated, deterministic geological
  model that is disconnected from the operational constraints actually governing
  tonnage. Reserves therefore overstate what is plannable, and shortfalls are
  diagnosed after they occur instead of being prevented.

TARGET USERS
  Mine Manager · Mine Planning Engineer · Chief Geologist · Maintenance Engineer
  · GM (Production)/Regional Head · HQ Executive · IBM/DGMS Auditor

SOLUTION
  OreSight (खनिज दृष्टि) — a reserve-to-production digital twin.
  Three engines behind one decision-shaped dashboard:
    PRISM  reserve intelligence   (where is the ore, and how sure are we?)
    PULSE  production risk         (will we get it out, and what will stop us?)
    NUDGE  prescriptive optimiser  (what should we do about it?)

CORE FEATURES (MVP)
  Multi-mine command view · 3D probabilistic block model (OK + SGS, P10/50/90)
  · regional prospectivity map (PU-learning + XGBoost, spatial block CV)
  · EO ingestion (Sentinel-1/2, GPM IMERG, MODIS LST, NDVI/NDMI)
  · Effective Accessible Reserve & Reserve-at-Risk funnel
  · probabilistic 30/60/90-day forecast with hierarchical MinT reconciliation
  · shortfall probability + SHAP driver attribution
  · Weibull equipment failure risk · learned per-mine weather derating curves
  · MILP prescriptive actions with Δtonnage and Δrisk · what-if simulator
  · RBAC + immutable audit log · generated reports

KEY INNOVATION
  Effective Accessible Reserve — reserves expressed as a probability
  distribution conditioned on the operational constraint model, producing a
  "Reserve at Risk" figure no existing product computes. Supported by
  hierarchically-reconciled probabilistic forecasting, satellite-derived
  per-mine weather derating curves, and counterfactual value accounting.

TECH STACK
  React 18 + TypeScript + Vite + Tailwind/shadcn + MapLibre + deck.gl +
  react-three-fiber + ECharts
  FastAPI (Python 3.11) + Celery + Redis
  PostgreSQL 16 + PostGIS + TimescaleDB · MinIO (COGs) · TiTiler
  scikit-learn · LightGBM · PyKrige/GSTools · GemPy · HierarchicalForecast ·
  SHAP · lifelines · OR-Tools · MLflow
  Docker Compose → Kubernetes · GitHub Actions · Prometheus/Grafana/Loki
  100% open-source. ₹0 licence cost. CPU-only inference. Air-gap capable.

ARCHITECTURE
  Users → React PWA → Nginx/API gateway → FastAPI modular monolith
        → (sync) PostGIS/Timescale + Redis cache
        → (async) Celery workers → PRISM / PULSE / NUDGE → MLflow registry
        → MinIO object store (COGs, realisations, reports) → TiTiler tiles
        ← EO ingestion (Copernicus, NASA GES DISC, MODIS, GSI/NGDR, Bhuvan)
        ← MOIL adapters (DPR XLSX, SAP PM, lab assays, block-model exports)

AI/ML
  Kriging + Sequential Gaussian Simulation for the reserve estimate & its
  uncertainty; XGBoost/PU-learning for prospectivity with spatial block CV;
  LightGBM quantile regression + MinT for production; Weibull/GBM survival for
  equipment; distributed-lag regression for weather response; SHAP for
  attribution; MILP (OR-Tools) — NOT ML — for prescription; a locally-hosted,
  numerically-validated LLM for narration only.
  Metrics: spatial-CV AUC & capture efficiency · LOO RMSE and slope-of-regression
  · WAPE, pinball loss, PICP · Brier score · C-index.

DATABASE
  PostgreSQL 16 + PostGIS (mines, leases, boreholes, blocks in EPSG:32644)
  + TimescaleDB hypertables (production_daily, equipment_events, eo_timeseries)
  + MinIO/Parquet for SGS realisations and rasters. Immutable audit_log.
  Provenance flags (`source`, `is_synthetic`) on every data-bearing table.

APIs
  /mines · /mines/{id}/reserve/summary · /mines/{id}/blocks · /prospectivity/*
  /production · /equipment · /eo/timeseries · /eo/change-detection
  /forecast · /forecast/drivers · /risk/summary · /risk/derating-curve
  /scenarios · /scenarios/{id}/simulate · /optimise · /actions/{id}/decide
  /schedule/apply · /alerts · /reconciliation · /reports/{type} · /models
  JWT + RBAC with mine-level scoping; every ML response carries model_version.

MVP (36 hours)
  M1 map · M2 3D blocks · M3 kriging+SGS · M4 prospectivity · M5 EO pipeline ·
  M6 quantile forecast · M7 shortfall + SHAP · M8 equipment risk ·
  M9 derating curves · M10 MILP actions · M11 what-if · M12 EAR funnel ·
  M13 RBAC+audit · M14 alerts

DEMO
  National view → Balaghat 3D reserve → EAR funnel → forecast + drivers →
  rainfall derating curve → ⭐ what-if slider recolours all 11 mines in <3 s →
  MILP suggests 3 actions → shortfall 0.71 → 0.19 → apply → audit trail →
  data-honesty and metrics slide → open-source, CPU-only, deployable close.

SCALABILITY
  Modular monolith → K8s; Timescale continuous aggregates + compression;
  partitioning by mine_id/time; precomputed nightly analytics served from cache;
  separate Celery queues per workload class; public read path via CDN for a
  future national transparency portal.

FUTURE SCOPE
  Drone photogrammetry volume reconciliation · Sentinel-1 InSAR slope stability ·
  cross-mine grade-blend optimisation · live OEM telemetry · expected-information-
  gain drill targeting · auto-drafted MCDR/UNFC returns · Hindi/Marathi voice DPR ·
  multi-commodity, multi-PSU national platform under the National Critical
  Mineral Mission.
════════════════════════════════════════════════════════════════════════════════
```

---

## 21. "If I were participating in SIH with this problem statement, this is exactly what I would build."

### Step 1 — I would reframe the problem before writing a line of code.
I would decide, in the first team meeting, that this is **not** an ore-finding problem. It is a **decision-assurance problem**: MOIL knows roughly where its manganese is; what it cannot do is tell you, on the 1st of the month, how much of it will actually reach a rake by the 30th, and what to change if the answer is "not enough." I would write that sentence on a whiteboard and refuse to build anything that doesn't serve it. Every other team in that room will build a prospectivity map plus a forecast chart. The reframe is my whole competitive advantage, and it costs nothing.

### Step 2 — I would build the product around one original idea: Effective Accessible Reserve.
One idea, stated crisply, is worth more than ten features. `EAR = Σ T·G·A·R·C`, with `A` (accessibility, from a development-reachability graph) and `C` (constraint availability, from the operational model) as *distributions*. The output is a single number MOIL has never seen: **Reserve at Risk**. I'd make the funnel visualisation the centrepiece of the deck and the second thing the judges see.

### Step 3 — I would spend three weeks on preparation, not on the hackathon.

- Download and clip every EO and geoscience layer for the Nagpur–Bhandara–Balaghat belt **offline**, before the event.
- Compile MOIL's published monthly production into a real time series from its exchange filings.
- Write a synthetic data generator whose mine-level output **sums to MOIL's real published annual totals** — so my numbers are checkable.
- Pre-train the slow models (SGS realisations, prospectivity raster) and commit the artefacts.
- Wireframe all six screens in Figma and have the design tokens ready.
- Build the Minimum Working Demo (§13.6) once, completely, as a dry run. Record a backup video of it.

### Step 4 — In the 36 hours, I would build in this order, strictly.
Core forecast loop first (data → LightGBM quantile → shortfall probability → SHAP → UI). Then the 3D block model. Then the MILP. Then the what-if slider. Then polish. **Never outward-in.** I would freeze the API contract at hour 2 and freeze all code at hour 34, and I would put two people to sleep at hour 16 whatever the state of the build.

### Step 5 — I would make three deliberate, defensible engineering choices and lead with them.

1. **Ordinary Kriging over deep learning** for grade estimation, with the cross-validation to prove it. Refusing to over-use AI is itself a differentiator.
2. **MILP over reinforcement learning** for prescription, because the constraints are hard, the decisions are audited, and explainability is non-negotiable in a PSU.
3. **CPU-only, open-source, air-gappable** as a hard architectural constraint, because a system that needs a GPU cluster and an internet connection will never run inside a mine's IT room.

### Step 6 — I would be aggressively honest about data and metrics.
A visible badge in the UI saying which data is real and which is synthetic. Model cards in the product. Spatial cross-validation results reported instead of inflated random-split AUCs. Realistic accuracy claims with prediction-interval coverage. I would proactively raise the "rainfall doesn't find manganese at 200 metres depth" point *myself*, in the demo — because it is the sharpest observation available about this problem statement, and the team that makes it first owns the room.

### Step 7 — I would design the demo as a story with one physical moment.
Everything builds to the rainfall slider: drag it, and eleven mines change colour, the forecast fan widens, Reserve at Risk jumps, three mines go red — in under three seconds. Then one click produces three concrete actions and the risk falls from 0.71 to 0.19. That is a *felt* moment, not an explained one, and it is what a judge will describe to the other judges afterwards.

### Step 8 — I would close on adoption, not on technology.
Zero licence cost. Deploys on MeghRaj or on-premise. Ingests their existing DPR spreadsheets, SAP exports and Datamine block models on day one. Outputs shaped for UNFC and MCDR so a Recognised Qualified Person can certify them. A shadow-mode pilot on two mines that proves value before anyone is asked to trust it. And the same engine works for NMDC's iron ore and HCL's copper tomorrow.

**In one sentence:** *I would build a probabilistic decision system that tells MOIL how much of its declared reserve it can actually realise this quarter, what will stop it, and what to do about it — and I would win the room by being the only team that admitted what satellites can and cannot see.*

---

## Appendix A — Reading list for the team (do this in week −3)

1. MOIL Limited — latest Annual Report, Investor Presentation and monthly production filings (real production data, mine list, capex plans)
2. IBM — *Indian Minerals Yearbook*, Manganese Ore chapter (national reserves, grades, UNFC classification in practice)
3. GSI — literature on the **Sausar Group** and gondite-hosted manganese mineralisation (deposit geometry drives your interpolation design)
4. MCDR 2017 & MEMC Rules 2015 — what a reserve statement legally is
5. Nixtla `HierarchicalForecast` docs — MinT reconciliation
6. `PyKrige` / `GSTools` tutorials — variograms and kriging in an afternoon
7. Google OR-Tools CP-SAT primer — MILP modelling patterns
8. A mineral-prospectivity-mapping review paper — for the spatial-CV and PU-learning conventions
9. Copernicus Data Space + STAC quickstart; NASA GES DISC GPM IMERG access guide
10. SHAP documentation — TreeExplainer

## Appendix B — Repository structure

```
oresight/
├── docker-compose.yml            # one command brings up the whole stack
├── .github/workflows/ci.yml
├── docs/
│   ├── architecture.md  demo-script.md  model-cards/  data-provenance.md
├── data/
│   ├── raw/          # EO + GSI downloads (git-ignored, documented in DVC)
│   ├── processed/    # clipped rasters, feature stacks
│   └── synthetic/    # generated boreholes, production, equipment events
├── ml/
│   ├── prism/   variogram.py  kriging.py  sgs.py  blockmodel.py
│   │            prospectivity.py  spatial_cv.py  accessibility.py
│   ├── pulse/   features.py  forecast.py  reconcile.py  shortfall.py
│   │            survival.py  derating.py  explain.py
│   ├── nudge/   milp.py  greedy.py  scenarios.py
│   ├── eo/      ingest.py  indices.py  change_detection.py
│   └── notebooks/     # experiments, kept out of the runtime path
├── backend/
│   ├── app/  main.py  api/v1/{geo,ops,forecast,optim,reports,auth}.py
│   │         models/  schemas/  services/  tasks/  core/{security,config}.py
│   ├── alembic/       tests/
├── frontend/
│   ├── src/  pages/  components/{map,blocks3d,charts,panels}/
│   │         hooks/  api/  store/  styles/
├── scripts/  seed.py  generate_synthetic.py  reset_demo.py  prepare_eo.py
└── README.md
```

## Appendix C — Sources

- [MOIL Limited achieves record manganese ore production in FY 2025-26 — PSU Connect](https://www.psuconnect.in/psu-news/moil-limited-achieves-record-manganese-ore-production-in-fy-2025-26)
- [MOIL targets 3.5 million tonnes manganese ore production capacity by 2030 — Ferro-Alloys.com](https://www.ferro-alloys.com/en/News/Details/332496)
- [MOIL achieves record production of 1.60 lakh tonnes in Oct'25 — Business Standard](https://www.business-standard.com/amp/markets/capital-market-news/moil-achieves-record-production-of-1-60-lakh-tonnes-in-oct-25-125110401524_1.html)
- [MOIL — company profile, mine list and depths (Wikipedia)](https://en.wikipedia.org/wiki/MOIL)
- [Indian Minerals Yearbook 2020 — Manganese Ore chapter, Indian Bureau of Mines](https://ibm.gov.in/writereaddata/files/04272022163406Manganese_2020.pdf)
- [Indian Minerals Yearbook 2019 — Manganese Ore chapter, IBM](https://ibm.gov.in/writereaddata/files/01072021154458Manganeseore_2019.pdf)
- [IndiaAI and GSI launch Hackathon on AI-driven Mineral Targeting — PIB, Ministry of Mines](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2112453)
- [National Geoscience Data Repository (NGDR) — geodataindia.gov.in](https://geodataindia.gov.in/register)
- [GSI Hackathon portal](https://hackathon.gsi.gov.in/login)
- [India to use surveillance satellite system to monitor illegal mining (Mining Surveillance System) — Geospatial World](https://geospatialworld.net/news/india-use-surveillance-satellite-system-monitor-illegal-mining/)
- [Mining Surveillance System (MSS) overview](https://www.chronicleindia.in/year-book/chronicle-year-book-2022/mining-surveillance-system-mss)
- [A System to Identify Illegal Mining Raises Hundreds of Alerts — The Wire (on MSS follow-through)](https://m.thewire.in/article/business/a-system-to-identify-illegal-mining-raises-hundreds-of-alerts-governments-sleep-on-half-of-them)
- [Bhuvan API — ISRO/NRSC geoportal](https://bhuvan-app1.nrsc.gov.in/api/)
- [Bhoonidhi — NRSC data ordering portal](https://bhoonidhi.nrsc.gov.in/)
- [How KoBold Metals uses AI to find minerals — DeepLearning.AI, The Batch](https://www.deeplearning.ai/the-batch/how-kobold-metals-uses-ai-to-find-rare-earth-minerals/)
- [AI-powered mineral exploration: KoBold Metals raises $491M — CarbonCredits.com](https://carboncredits.com/ai-powered-mineral-exploration-billionaires-backed-kobold-metals-raised-491-million/)
- [Positive disruption: using AI to discover critical minerals — Mining Review](https://www.miningreview.com/magazine-article/positive-disruption-using-ai-to-discover-critical-minerals/)
- [Advancing iron ore grade estimation: machine learning vs ordinary kriging — Minerals (MDPI)](https://doi.org/10.3390/min15020131)
- [A new ore grade estimation using combined machine learning algorithms — Minerals 10(10):847](https://doi.org/10.3390/min10100847)
- [Time-series InSAR analysis for slope stability monitoring using Sentinel-1 in open-pit mining — ISPRS Archives](https://isprs-archives.copernicus.org/articles/XLVIII-1-W2-2023/945/2023/)
- [Utilization of multi-sensor remote sensing technologies for open-pit mine monitoring — Int. J. Applied Earth Observation](https://sciencedirect.com/science/article/pii/S1569843225004819)
- [Minecraft 2.0: AI-driven exploration reshaping India's hunt for rare earths — Business Standard](https://www.business-standard.com/industry/news/minecraft-2-0-ai-driven-exploration-reshaping-india-s-hunt-for-rare-earths-125112501135_1.html)

---

*Prepared as a technical and product blueprint for Smart India Hackathon. Figures marked ✅ are sourced; figures marked 🔶 are estimates that must be validated before being presented as fact.*
