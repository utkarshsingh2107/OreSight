# OreSight — Domain Glossary & Quotable Facts

Compiled for team domain immersion (Execution Plan, Phase 0 / Week −3).
Read this together as a team before splitting into roles. Facts marked ✅ are
sourced (see links); facts marked 🔶 are estimates/assumptions to validate,
per the blueprint's own labeling convention.

## Glossary

| Term | Meaning |
|---|---|
| **MOIL** | Manganese Ore India Limited — India's largest manganese ore producer, a PSU under the Ministry of Steel, headquartered in Nagpur. Operates 11 mines (10 underground/opencast in Maharashtra & Madhya Pradesh, 1 in MP). |
| **Gondite** | The manganese-bearing metamorphic rock type hosting most of India's manganese ore, found in the Sausar Group of rocks (Central India). Stratabound, folded ore bands. |
| **Sausar Group** | A Precambrian metasedimentary belt in the Nagpur–Bhandara–Balaghat region of Central India; the geological setting for MOIL's manganese deposits. |
| **UNFC** | United Nations Framework Classification for Resources — the system India uses (via IBM) to classify mineral reserves by geological confidence (G1–G4) and economic/feasibility axes. |
| **MCDR** | Mineral Conservation and Development Rules, 2017 — the statutory framework under which mines must file Annual Returns on reserves, production, and conservation to the Indian Bureau of Mines (IBM). |
| **MEMC Rules** | Mineral (Evidence of Mineral Contents) Rules, 2015 — governs how exploration evidence must be reported to establish reserves/resources. |
| **DGMS** | Directorate General of Mines Safety — statutory safety regulator for Indian mines; relevant to any AI touching blast design (safety-critical, not to be automated — see blueprint §1.7). |
| **DPR** | Daily Production Report — the paper/spreadsheet record mines currently use to report shift-wise output up the chain. |
| **Kriging** | A geostatistical interpolation method (Ordinary Kriging) used to estimate ore grade/tonnage between sparse borehole samples, producing both an estimate and an uncertainty (variance). |
| **SGS** | Sequential Gaussian Simulation — generates multiple equally-probable realisations of the ore body to quantify uncertainty (used for P10/P50/P90 tonnage bands). |
| **Block model** | A 3D grid of small blocks, each assigned an estimated grade/tonnage/confidence — the standard representation of an ore reserve in mining software. |
| **Grade-tonnage curve** | A curve showing how much tonnage is available above a given ore grade cutoff — a standard mine-planning artefact. |
| **NGDR / Bhukosh** | National Geoscience Data Repository / GSI's Bhukosh portal — open geological, geophysical, and geochemical data for India. |
| **Sentinel-1/2, MODIS, IMERG** | Earth observation sources: Sentinel-1 (radar, soil moisture proxy), Sentinel-2 (optical, vegetation/mineral indices), MODIS (land surface temperature), GPM IMERG (satellite rainfall estimates). |
| **EAR (Effective Accessible Reserve)** | OreSight's core original concept: geological reserve tonnage discounted by operational accessibility (development status, flooding risk, equipment availability) — the bridge between "reserve" and "plannable production." See blueprint §4.5. |

## 20 Quotable Domain Facts

1. ✅ MOIL is India's largest manganese ore producer, operating 11 mines across Maharashtra and Madhya Pradesh.
2. ✅ MOIL reported record production of **19.07 lakh tonnes in FY 2025-26**, up ~5.8% from **18.02 lakh tonnes in FY 2024-25**.
3. ✅ MOIL has publicly targeted **3.5 million tonnes of annual capacity by FY30**.
4. ✅ MOIL achieved a record **1.60 lakh tonnes in October 2025** alone (monthly figure).
5. ✅ Indian manganese ore grades broadly range **~10–54% Mn** across different ore types (per IBM Indian Minerals Yearbook).
6. 🔶 A single deep exploratory borehole in the Sausar belt can take weeks to drill and cost lakhs of rupees — coverage is therefore sparse (industry-standard assumption, validate with MOIL if possible).
7. 🔶 Reserve figures are typically updated **annually**, while production plans are made **monthly** and mining happens **per shift** — a 12-month-stale picture drives daily decisions.
8. Under **MCDR 2017**, mines must file an **Annual Return** to the Indian Bureau of Mines (IBM) with reserve/resource figures classified under **UNFC**.
9. UNFC classifies reserves along **geological confidence (G1–G4)** and **economic/feasibility axes** — not a single number, a matrix.
10. Reserve estimation in Indian practice typically flows: regional mapping → trenching/geophysics → boreholes → lab assay (Mn%, Fe%, SiO₂, Al₂O₃, P, moisture) → manual sectional interpretation → volume × density × recovery factor = tonnage.
11. ⚠️ Rainfall, soil moisture, vegetation index, and land surface temperature (the "satellite inputs" named in the problem statement) are **surface climate variables — they do not see ore at depth**. They are legitimate as **production-constraint drivers** (haul road conditions, dewatering), not as sub-surface reserve indicators.
12. Legitimate satellite-based *reserve* targeting instead uses ASTER/Sentinel-2 SWIR band ratios (iron-oxide/clay indices), DEM/structural lineaments, and geobotanical stress anomalies over mineralised outcrops.
13. **Optimising blast design** is safety-critical and regulated by DGMS under the Explosives Rules 2008 — an AI system should optimise *scheduling/sequencing* and flag delay risk, not auto-generate blast parameters.
14. India's **National Geoscience Data Repository (NGDR)** and GSI's **Bhukosh** portal provide open geological, geophysical, and geochemical data usable for real (non-synthetic) prospectivity modelling.
15. ISRO's **Bhuvan** and **Bhoonidhi** portals provide access to Indian EO data, including Cartosat DEM products.
16. The Ministry of Mines and GSI have run an **"AI-driven Mineral Targeting" hackathon** with IndiaAI — showing government appetite for exactly this kind of ML-for-minerals approach.
17. India already runs a satellite-based **Mining Surveillance System (MSS)** to detect illegal mining — precedent for satellite-based mine monitoring at national scale, though follow-through on alerts has been inconsistent (per reporting).
18. Comparable global players like **KoBold Metals** use AI/ML over multi-source geoscience data for mineral exploration and have raised hundreds of millions in funding — validates the category, though KoBold targets discovery, not production operations.
19. Peer-reviewed literature shows **machine learning approaches (e.g. gradient boosting) can outperform or complement Ordinary Kriging** for ore grade estimation — justifies pairing classical geostatistics with ML rather than picking one.
20. **Sentinel-1 InSAR time series** is an established technique for **slope-stability/deformation monitoring** in open-pit mines — a credible Phase 2 feature (not feasible to build live in a 36h hackathon).

## Sources

See `OreSight_SIH_Blueprint.md`, Appendix C for the full source list (PSU Connect,
Ferro-Alloys.com, Business Standard, IBM Indian Minerals Yearbook, GSI/NGDR,
PIB, Bhuvan/Bhoonidhi, DeepLearning.AI, MDPI Minerals journal, ISPRS Archives).
