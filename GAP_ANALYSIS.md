# OreSight — Gap Analysis & Priority Matrix
## What You Have vs What SIH Needs

---

## Problem Statement Requirements Breakdown

The SIH Problem Statement #26009 asks for **THREE distinct capabilities**:

### Requirement A: Identify and Map Manganese Reserves
> "identify and map manganese reserves more accurately using surface and sub-surface indicators"

**What This Means:**
- Find NEW manganese deposits (prospectivity mapping)
- Use satellite/space technology for surface indicators
- Integrate with sub-surface data (drilling, geophysics)
- Output: Where should MOIL drill next?

### Requirement B: Predict Production Shortfalls
> "Predict shortfalls in production by analyzing constraints like equipment downtime, weather conditions, or blasting delays"

**What This Means:**
- Forecast production as a probability distribution (not a single number)
- Attribute shortfall risk to specific causes
- Use satellite data for weather/climate constraints
- Output: What's the probability we miss target this month, and why?

### Requirement C: Suggest Corrective Actions
> "Suggest corrective actions such as adjusting mine schedules, optimizing blasting, or re-deploying equipment"

**What This Means:**
- Prescriptive analytics (not just descriptive/predictive)
- Actionable recommendations with estimated impact
- Consider constraints (budget, equipment availability, safety)
- Output: Do X, Y, Z to recover the shortfall

---

## Current App Scorecard

| Requirement | Weight | Your Score | Max Score | Gap |
|-------------|--------|------------|-----------|-----|
| **A: Reserve Identification** | 30% | 3/10 | 10 | ❌ **CRITICAL GAP** |
| **B: Shortfall Prediction** | 40% | 7/10 | 10 | ⚠️ Good, needs enhancement |
| **C: Corrective Actions** | 30% | 5/10 | 10 | ⚠️ Weak, needs data-driven approach |
| **Overall** | 100% | **49%** | 100% | **51% gap** |

---

## Detailed Gap Analysis

### Requirement A: Reserve Identification (3/10 ❌)

#### What You Have:
✅ Static 3D block model image (synthetic)
✅ Grade-tonnage curve display
✅ EAR number display

#### What's Missing (Critical):
❌ **No actual reserve identification** — you show existing reserves, not new ones
❌ **No satellite-based prospectivity mapping** — the PS explicitly asks for this
❌ **No "identify reserves" workflow** — where should MOIL explore next?
❌ Limited use of "surface indicators" from space technology
❌ No integration of geological maps or structural features

#### Why This Is Critical:
- This is **30% of the problem statement**
- Judges will ask: "How does this identify NEW reserves?"
- Other teams will likely have prospectivity heatmaps (you need this to compete)
- The "space technology" theme is underutilized

#### Fix Priority: **P0 (CRITICAL)**
Must build prospectivity module to be competitive.

---

### Requirement B: Shortfall Prediction (7/10 ⚠️)

#### What You Have:
✅ LightGBM quantile forecast (P10/P50/P90)
✅ Shortfall probability calculation
✅ SHAP driver attribution
✅ Rainfall integration (real data)
✅ What-if slider (interactive)
✅ Equipment downtime simulation

#### What's Missing:
⚠️ **Limited satellite data usage** — only rainfall, PS mentions 4 indicators:
  - Rainfall ✅ (you have this)
  - Soil moisture ❌ (missing)
  - Vegetation index ❌ (missing)
  - Land temperature ❌ (missing)
⚠️ No equipment failure risk model (you simulate it randomly)
⚠️ No blast delay modeling
⚠️ No manpower constraint modeling

#### Why This Matters:
- You have the foundation, but judges will ask about the other 3 satellite inputs
- "Space Technology" is the theme — need to show multi-source integration
- Current model is good but not comprehensive

#### Fix Priority: **P1 (High)**
Enhance existing model with additional satellite constraints.

---

### Requirement C: Corrective Actions (5/10 ⚠️)

#### What You Have:
✅ Action suggestion endpoint
✅ Action ranking (greedy heuristic)
✅ Apply action workflow
✅ Audit log tracking
✅ PDF report generation

#### What's Missing:
⚠️ **Actions are hand-coded heuristics** — Δtonnes values are assumptions
⚠️ No learning from historical action outcomes
⚠️ No optimization (just greedy ranking)
⚠️ No constraint checking (budget, equipment availability)
⚠️ No "optimizing blasting" as mentioned in PS

#### Why This Matters:
- Judges will ask: "How did you calculate these numbers?"
- Hand-waved estimates hurt credibility
- No data-driven justification for recommendations

#### Fix Priority: **P1 (High)**
Make actions data-driven and add optimization layer.

---

## Space Technology Usage Gap

### Problem Statement Explicitly Mentions:
> "satellite/space technology inputs (such as rainfall, soil moisture, vegetation index, and land temperature)"

### Your Current Usage:

| Space Tech Input | Status | Usage |
|------------------|--------|-------|
| **Rainfall** | ✅ Fully implemented | Real IMERG/ERA5 data, forecast feature, what-if slider |
| **Soil Moisture** | ❌ Not implemented | Missing — easy to add from Sentinel-1 or SMAP |
| **Vegetation Index (NDVI)** | ❌ Not implemented | Missing — critical for prospectivity |
| **Land Temperature** | ❌ Not implemented | Missing — use Landsat thermal or MODIS LST |

**Coverage: 25% (1 out of 4 mentioned inputs)**

### Why This is a Problem:
- The theme is literally "Space Technology"
- You're only using 25% of the suggested inputs
- Easy for judges to ask: "What about soil moisture / vegetation / temperature?"
- Other teams will likely use all 4

### Fix Priority: **P0 (CRITICAL)**
Must add remaining 3 satellite inputs.

---

## Competitive Positioning

### What Other Teams Will Likely Do:

#### Team Archetype 1: "Pretty Map, No Substance"
- Builds beautiful prospectivity heatmap
- No production forecasting
- No prescriptive actions
- **Your advantage:** You have B & C, they only have A

#### Team Archetype 2: "Time Series Dashboard"
- Builds production forecast with LSTM
- Shows historical trends, maybe anomaly detection
- No reserve identification
- No prescriptive layer
- **Your advantage:** You have A & C (if you build A), they only have B

#### Team Archetype 3: "LLM Chatbot"
- RAG over mining documents
- "Ask me about production"
- No rigorous ML models
- **Your advantage:** You have real quantitative models

#### Team Archetype 4: "Complete But Shallow"
- Has all 3 components (A, B, C)
- But each is superficial (basic heatmap, simple forecast, generic actions)
- **Your risk:** This is your current state — you're complete but shallow on A & C

### How to Win:
Build **complete AND deep**:
- **A (Prospectivity):** Multi-source features, validated ML model, explainable
- **B (Forecast):** Multi-satellite constraints, uncertainty quantification, SHAP attribution
- **C (Actions):** Data-driven Δtonnes, optimization, constraint checking

**The Differentiator:** The EAR (Effective Accessible Reserve) concept — the bridge from reserves (A) to production (B). No other team will have this.

---

## The Winning Narrative: EAR as the Bridge

### Current Problem with Most Solutions:
- Reserves and production are **disconnected**
- Geological reserves are a number in a report
- Production plans are based on last year's actuals
- No mathematical connection between them

### Your Unique Insight:
**Not all reserves are equally produceable.**

A block of manganese ore at depth 450m, behind an undriven crosscut, in a zone that floods for 90 days a year, reachable only by an LHD that has 30% failure risk this quarter — is a **geological reserve** but not a **plannable reserve**.

### The EAR Formula:
```
Effective Accessible Reserve (EAR) = 
    Geological Reserve × Accessibility Factor

Where Accessibility Factor = 
    f(depth, equipment, weather, infrastructure, regulations)
```

### Why This Wins:
1. **Mathematically connects A → B** (reserves → production)
2. **Incorporates space technology** (weather factor from satellites)
3. **Actionable** (improve EAR by adding equipment, improving haul roads)
4. **Unique** (no other team will think of this)
5. **Explainable** (funnel diagram showing factor breakdown)

### Implementation Status:
- Concept: ✅ Documented in blueprint
- Static display: ✅ You show one EAR number
- Dynamic calculation: ❌ **MISSING** — not interactive, not explained
- Factor breakdown: ❌ **MISSING**
- What-if scenarios: ❌ **MISSING**

**Fix Priority: P0 (CRITICAL) — This is your demo's "wow moment"**

---

## Priority Matrix (Effort vs Impact)

```
High Impact
│
│   P0: Prospectivity        P0: EAR Dynamic
│       Module                   Calculator
│   (A: Reserve ID)          (A→B Bridge)
│   
│   P1: Add Soil Moisture,   P1: Data-Driven
│       NDVI, LST                Actions
│   (B: Enhanced Forecast)   (C: Prescriptive)
│
├─────────────────────────────────────────
│   P3: Multi-Mine            P2: MILP
│       Dashboard                Optimizer
│   (Nice-to-have)           (C: Advanced)
│
Low Impact
    Low Effort              High Effort
```

### Priority Definitions:

**P0 (Critical — Must Build):**
1. Prospectivity mapping module (Requirement A)
2. Dynamic EAR calculator with factor breakdown (A→B bridge)
3. Add soil moisture, vegetation, temperature to forecast (Space tech theme)

**P1 (High Priority — Should Build):**
1. Data-driven action effectiveness model (Requirement C)
2. Enhanced SHAP with all satellite features (Requirement B)
3. Validation metrics display (Credibility)

**P2 (Medium — Good to Have):**
1. MILP optimizer for action bundles (Requirement C)
2. Reconciliation loop (predicted vs actual)
3. Equipment failure risk model

**P3 (Low — Nice to Have):**
1. Multi-mine support
2. Mobile responsiveness
3. Advanced 3D viewer

---

## Time Investment Required

### Minimum to Be Competitive (Must Do):
| Task | Time | Priority |
|------|------|----------|
| Prospectivity mapping | 5 days | P0 |
| Add 3 missing satellite inputs | 2 days | P0 |
| Dynamic EAR calculator | 2 days | P0 |
| **Total Minimum** | **9 days** | - |

### To Be Strong (Should Do):
| Task | Time | Priority |
|------|------|----------|
| Data-driven actions | 2 days | P1 |
| Validation metrics UI | 1 day | P1 |
| Polish & documentation | 2 days | P1 |
| **Total Strong** | **5 days** | - |

### To Win (Stretch Goals):
| Task | Time | Priority |
|------|------|----------|
| MILP optimizer | 1 day | P2 |
| Multi-mine support | 1 day | P3 |
| **Total Winning** | **2 days** | - |

**Total Time Budget: 16 days of focused work**
**Recommended Team: 2-3 people, 3 weeks part-time**

---

## What You Do Well (Keep Doing This)

✅ **Honest about synthetic data** — Data honesty badge is excellent
✅ **Real satellite data** — Rainfall from actual sources (ERA5/IMERG)
✅ **Solid ML foundation** — LightGBM with quantile regression is correct approach
✅ **Explainability** — SHAP drivers are crucial for PSU trust
✅ **Interactive** — What-if slider is engaging
✅ **End-to-end** — You have working system, not just notebooks
✅ **Professional** — Code is clean, documented, deployable

**Do NOT throw this away. Build on it.**

---

## What Needs Immediate Attention

### Critical (Do This Week):
1. **Build prospectivity module** — This is 30% of the problem you're currently not addressing
2. **Add soil moisture, NDVI, LST** — Cover all 4 mentioned satellite inputs
3. **Make EAR dynamic and explainable** — This is your unique differentiator

### High Priority (Do Next Week):
1. **Make actions data-driven** — Replace assumptions with learned models
2. **Add validation metrics** — Show you tested rigorously
3. **Polish the narrative** — Practice explaining EAR concept

### Optional (If Time Permits):
1. MILP optimizer
2. Multi-mine view
3. Mobile responsive design

---

## Red Flags to Avoid (Common SIH Mistakes)

### ❌ Don't Do These:
1. **Don't skip requirement A** — "We focused on B & C" = automatic point deduction
2. **Don't claim 99% accuracy** — Instant credibility loss with technical judges
3. **Don't hide synthetic data** — Transparency = credibility (you're doing this right)
4. **Don't use deep learning for everything** — Simpler models often win in competitions
5. **Don't present without rehearsing** — Stumbling during demo loses massive points
6. **Don't overengineer** — Working prototype > perfect architecture
7. **Don't forget the backup video** — Laptop failures are common

### ✅ Do These Instead:
1. **Cover all 3 requirements** with at least basic implementations
2. **Show uncertainty** — P10/P50/P90, confidence intervals (you're doing this)
3. **Cite sources** — Every dataset, every paper (add citations panel)
4. **Make it interactive** — Sliders, filters, real-time updates (you have some)
5. **Explain the EAR bridge** — This is your unique story
6. **Test on fresh machine** — Ensure reproducibility
7. **Record backup video** — Insurance against demo gods

---

## Questions Judges Will Ask (Be Ready)

### Question Set 1: Technical Depth
1. **"How did you validate your prospectivity model?"**
   - Answer: Spatial cross-validation, AUC-ROC on test set, leave-one-mine-out

2. **"Why LightGBM instead of LSTM for forecasting?"**
   - Answer: Tabular data with engineered features, need P10/P50/P90 quantiles, LightGBM faster + more explainable

3. **"How do you handle missing satellite data (clouds)?"**
   - Answer: Time-series compositing (median of last N days), SAR works through clouds

4. **"What's your model's mean absolute error?"**
   - Answer: [You need to calculate and display this — add to validation panel]

### Question Set 2: Practical Implementation
5. **"Can MOIL actually use this without expensive sensors?"**
   - Answer: Yes — uses free satellite data + existing DPR spreadsheets, minimal new hardware

6. **"What about underground mines where satellites can't see?"**
   - Answer: Satellites measure constraints (rain, temperature), not ore itself. EAR uses mine geometry data, not satellite imaging of underground.

7. **"How long to deploy at a real mine?"**
   - Answer: 2-3 months (data integration, model calibration, user training), then operational

### Question Set 3: Safety & Compliance
8. **"Does this comply with DGMS regulations?"**
   - Answer: Yes — decision support only, human approval required. Doesn't auto-generate blast designs (safety-critical).

9. **"What about UNFC classification?"**
   - Answer: Reserve panel shows UNFC-compatible classification, can export MCDR returns

### Question Set 4: Differentiation
10. **"How is this different from Datamine/Vulcan/existing tools?"**
    - Answer: Those are static geological models. We connect geology → operations → probabilistic forecasting → prescriptive actions. Complementary, not competitive.

**Prepare written answers to all 10. Practice out loud.**

---

## Success Metrics

### Technical Metrics (Display These in App):
- [ ] Prospectivity model AUC-ROC > 0.75
- [ ] Forecast MAE < 15% of monthly target
- [ ] Forecast calibration (P50 should be median of actuals)
- [ ] Action effectiveness: predicted Δtonnes within 20% of actual

### Demo Metrics (Judge Evaluation):
- [ ] All 3 PS requirements demonstrably addressed
- [ ] Live interaction (sliders work, map is zoomable)
- [ ] No errors during demo
- [ ] Questions answered confidently
- [ ] Time limit respected (don't overrun)

### Impact Metrics (For Presentation):
- [ ] Potential shortfall reduction: X% (simulate with historical data)
- [ ] Drill targeting efficiency: Y% (compare random vs ML-guided)
- [ ] ROI calculation: payback period Z months

---

## Final Recommendation

### Your Path to Winning:

**Week 1: Close Critical Gaps**
- Build prospectivity module (maps, ML, UI)
- Add soil moisture, NDVI, LST to forecast
- Make EAR dynamic with factor breakdown
- **Output:** All 3 PS requirements covered

**Week 2: Strengthen & Polish**
- Make actions data-driven
- Add validation metrics display
- Write documentation
- **Output:** Credible, explainable system

**Week 3: Demo Prep**
- Rehearse presentation (3x minimum)
- Record backup video
- Test on fresh machine
- Prepare Q&A answers
- **Output:** Demo-ready

**Your Advantage:**
- Strong technical foundation (good ML, real data)
- Honest approach (data transparency)
- Unique insight (EAR concept)
- Working prototype (not vaporware)

**What You Need:**
- 2-3 weeks of focused work
- 2-3 team members
- Discipline to follow priorities (don't get distracted by shiny features)

**Bottom Line:**
You have 49% of a winning solution. The blueprint shows you how to get to 100%. The missing 51% is **doable in 3 weeks** if you focus on P0 priorities first.

---

## Next Steps (Do These Today)

1. **Read this document with your team** (30 min)
2. **Agree on timeline** — can you commit 3 weeks?
3. **Assign roles** — who builds prospectivity? Who does EO integration? Who does frontend?
4. **Start satellite data downloads NOW** — they take hours (see TECHNICAL_TASKS.md)
5. **Create project board** — GitHub Projects or Trello with tasks from TECHNICAL_TASKS.md
6. **Schedule daily standup** — 5 min sync every morning
7. **Commit to code freeze date** — e.g., 3 days before submission

**Don't wait. Every day of delay is 5% less polish in the final demo.**

Good luck! You can win this. 🚀
