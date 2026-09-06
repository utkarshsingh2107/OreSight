# OreSight — SIH 2026 Improvement Plan
## Transforming Current App into a Complete Solution

---

## Executive Summary

**Current State:** You have a solid technical foundation showing production forecasting with rainfall correlation. However, it only addresses ~40% of the problem statement.

**Gap Analysis:** The SIH problem statement requires **THREE distinct capabilities**:
1. ✅ **Predict production shortfalls** — You have this (LightGBM + SHAP)
2. ⚠️ **Identify and map manganese reserves** — You have only EAR display, not actual reserve identification
3. ⚠️ **Suggest corrective actions** — You have greedy heuristics, but they're not data-driven

**Critical Missing Elements:**
- No actual reserve identification/prospectivity mapping using space technology
- No integration of satellite indicators (vegetation index, soil moisture, land temperature) as mentioned in PS
- No connection between reserve estimation and production capability
- Limited use of "space technology" (only rainfall currently)

---

## The Winning Strategy: Dual-Scale Approach

### Scale 1: Regional Prospectivity (NEW — High Priority)
**What:** Identify new potential manganese reserves using ML + satellite data
**Why:** Directly addresses "identify and map manganese reserves" requirement
**How:** Mineral prospectivity mapping using multi-source data

### Scale 2: Mine-Level Production Optimization (CURRENT — Enhance)
**What:** Forecast shortfalls and optimize operations at active mines
**Why:** You already have this foundation — strengthen it
**How:** Enhance existing forecast + actions system

---

## Priority 1: Add Reserve Identification Module (Critical Gap)

### 1.1 Prospectivity Mapping System
**Timeframe:** 3-4 days
**Impact:** HIGH — Addresses the biggest gap

#### Components to Build:

**A. Multi-Source Data Integration**
```
Data Sources to Integrate:
├── Geological Data
│   ├── GSI geological maps (from NGDR/Bhukosh)
│   ├── Known mine locations (MOIL's 11 mines as training points)
│   └── Rock type boundaries (gondite, metamorphic rocks)
│
├── Satellite/Space Technology (CRITICAL)
│   ├── Sentinel-2 Optical (existing)
│   │   ├── SWIR band ratios (iron oxide detection)
│   │   ├── NDVI (vegetation stress over mineralization)
│   │   └── Clay mineral indices
│   ├── Sentinel-1 SAR (NEW)
│   │   ├── Texture analysis
│   │   └── Structural lineament detection
│   ├── ASTER/Landsat (NEW)
│   │   ├── Band ratio composites
│   │   └── Thermal anomalies (Land Surface Temperature)
│   └── DEM/Topography (NEW)
│       ├── Structural lineaments
│       ├── Slope analysis
│       └── Drainage patterns
│
└── Geophysical (if available)
    ├── Magnetic data
    └── Gravity data
```

**B. Prospectivity ML Model**
- **Algorithm:** Random Forest or XGBoost for mineral prospectivity
- **Training Data:** 
  - Positive: Known MOIL mine locations + GSI manganese occurrences
  - Negative/Unlabelled: Random background points (with buffer zones)
- **Features:** 
  - Spectral indices from Sentinel-2
  - Texture from Sentinel-1
  - Distance to lineaments
  - Lithology (from GSI)
  - Elevation derivatives
  - NDVI (vegetation anomalies)
  - Land Surface Temperature
- **Output:** Probability heatmap of manganese prospectivity

**C. Interactive Prospectivity Dashboard**
```
New Components:
├── ProspectivityMap.tsx
│   ├── Heatmap overlay on base map
│   ├── Known mine markers
│   ├── Drill hole recommendations
│   └── Layer controls (geology, satellite, lineaments)
│
├── ProspectivityPanel.tsx
│   ├── Top 10 prospect targets ranked
│   ├── Evidence layers contribution
│   ├── Confidence scores
│   └── Download drill plan (shapefile/KML)
│
└── FeatureImportanceChart.tsx
    └── Which satellite/geological features drive each target
```

#### Implementation Steps:

1. **Data Collection Script** (`scripts/fetch_satellite_data.py`)
   - Download Sentinel-2 imagery for Nagpur-Balaghat belt
   - Extract band ratios (SWIR, iron oxide, clay indices)
   - Calculate NDVI, LST from available bands
   - Download DEM for lineament extraction

2. **Feature Engineering** (`ml/prism/features.py`)
   - Compute spectral indices
   - Extract lineaments using edge detection
   - Create distance-to-features rasters
   - Stack all features into training dataset

3. **Prospectivity Model** (`ml/prism/prospectivity.py`)
   - Train Random Forest on MOIL mine locations
   - Generate probability map
   - Rank top prospects with confidence intervals
   - Export drill-target recommendations

4. **API Endpoints** (`backend/app/routers/prospectivity.py`)
   ```python
   GET /api/prospectivity/map          # Heatmap tiles
   GET /api/prospectivity/targets      # Top 10 prospects
   GET /api/prospectivity/features     # Feature importance
   POST /api/prospectivity/evaluate    # Evaluate custom location
   ```

5. **Frontend Components**
   - Map layer switcher for geology/satellite/prospects
   - Target ranking panel
   - Feature attribution display

---

## Priority 2: Enhance Space Technology Integration

### 2.1 Expand Satellite Data Usage (Critical for "Space Technology" Theme)

**Current:** Only rainfall (Good, but insufficient)

**Add These Satellite-Derived Constraints:**

#### A. Soil Moisture (Sentinel-1 / SMAP)
**Use Case:** Predict haul road trafficability and pit water accumulation
**Data Source:** Sentinel-1 VV/VH or SMAP L4
**Integration Point:** Add as feature to production forecast model
**Story:** "Heavy rainfall + high soil moisture = 3-day haul road closure"

#### B. Vegetation Index (NDVI - Sentinel-2/Landsat)
**Use Case 1:** Geobotanical prospecting (stressed vegetation over mineralization)
**Use Case 2:** Seasonal work constraint (forest regulations in protected areas)
**Integration:** 
- Prospectivity model (high weight)
- Production constraint (monsoon greenness = access issues)

#### C. Land Surface Temperature (Landsat 8/9 Thermal, MODIS)
**Use Case:** Equipment performance derating + worker safety constraints
**Data Source:** Landsat thermal bands, MODIS LST daily
**Integration Point:** Temperature > 42°C = shift productivity penalty factor
**Story:** "Heat stress reduces equipment efficiency by 15-20% in summer"

#### D. Coherence / InSAR (Sentinel-1, if time permits)
**Use Case:** Ground deformation monitoring, slope stability
**Data Source:** Sentinel-1 time series interferometry
**Integration:** Flag high-deformation areas as "reserve at risk"

### 2.2 Implementation

**New Module:** `ml/earth_observation/constraints.py`
```python
def get_operational_constraints(mine_location, date_range):
    """
    Fetch multi-source EO data and return operational constraint scores.
    
    Returns:
        - rainfall_constraint: 0-1 (1 = no rain, 0 = flooding)
        - soil_moisture_constraint: 0-1
        - temperature_constraint: 0-1
        - vegetation_access_constraint: 0-1
    """
```

**Updated Forecast Model:**
- Add soil moisture, LST, NDVI as features alongside rainfall
- Retrain LightGBM model
- Update SHAP drivers to show all EO constraints

**New Dashboard Panel:** `EOConstraintsPanel.tsx`
- Live satellite data display
- 7-day constraint forecast
- Historical constraint correlation with production dips

---

## Priority 3: Strengthen Corrective Actions (Make Them Real)

### 3.1 Current Problem
Your actions are hand-coded heuristics with assumed Δtonnes. Judges will ask: "How did you calculate these numbers?"

### 3.2 Solution: Data-Driven Action Modeling

**A. Action Database** (expand current stub)
```sql
CREATE TABLE action_library (
    action_id INT PRIMARY KEY,
    action_type VARCHAR (e.g., 'extra_shift', 'equipment_redeploy', 'blast_schedule_advance'),
    base_delta_tonnes INT,
    cost_inr INT,
    lead_time_days INT,
    applicable_constraints JSON  -- e.g., {"min_equipment_available": 3}
);

CREATE TABLE action_outcomes (
    -- Track historical outcomes when actions were applied
    action_id INT,
    applied_date DATE,
    predicted_delta_tonnes INT,
    actual_delta_tonnes INT,  -- Reconcile 30 days later
    success BOOLEAN
);
```

**B. Action Effectiveness Model**
- Train a regression model: `action + context → actual Δtonnes`
- Context: current equipment availability, weather forecast, manpower
- Update action suggestions with learned effectiveness, not assumptions

**C. Multi-Objective Optimization** (Optional, high impact if time allows)
- Use Google OR-Tools CP-SAT or PuLP
- Objective: Maximize Σ(Δtonnes) - Σ(cost)
- Constraints: Budget, equipment limits, time windows
- Output: Optimal action bundle, not just ranked list

### 3.3 Implementation

**New Module:** `ml/pulse/actions.py`
```python
def optimize_action_bundle(
    shortfall_tonnes: float,
    budget_inr: float,
    available_equipment: dict,
    weather_forecast: list
) -> list[ActionRecommendation]:
    """
    MILP optimization to select best action bundle.
    """
```

**Enhanced API:**
```python
POST /api/actions/optimize
{
    "mine_id": 1,
    "shortfall_tonnes": 3500,
    "budget_inr": 500000,
    "constraints": {...}
}
```

---

## Priority 4: Build the "Digital Twin" Narrative

### 4.1 The Missing Link: Effective Accessible Reserve (EAR)

**Current:** You show a static EAR number with no explanation
**Fix:** Make EAR dynamic and transparent

**Concept:** EAR = Geological Reserve × Accessibility Factor

**Accessibility Factors (each 0-1 multiplier):**
1. **Depth Factor:** Blocks below current development level get discount
2. **Equipment Factor:** If key equipment (LHD, dumper) is predicted to fail → discount
3. **Climate Factor:** Blocks in flood-prone areas → seasonal discount
4. **Regulatory Factor:** Blocks near protected forest → discount
5. **Infrastructure Factor:** Blocks far from current haul roads → discount

**New Component:** `EARExplainer.tsx`
- Visual breakdown showing: Geological → Depth → Equipment → Climate → EAR
- Slider: "What if we add one more LHD?" → EAR increases dynamically
- Slider: "What if monsoon is 20% heavier?" → EAR decreases

**Why This Wins:** This is the **"aha moment"** that connects reserves to production. No other team will have this.

### 4.2 Implementation

**Backend:** `ml/prism/ear.py`
```python
def compute_dynamic_ear(
    block_model: BlockModel,
    current_equipment: list,
    weather_forecast: dict,
    depth_constraints: dict
) -> dict:
    """
    Compute EAR with factor breakdown.
    Returns:
        - total_ear_tonnes
        - geological_reserve
        - accessibility_factors (dict of multipliers)
        - blocks_at_risk (list)
    """
```

**Frontend:** Add sliders and real-time recalculation

---

## Priority 5: Professional Polish & Credibility Boosters

### 5.1 Data Honesty (You Already Have — Strengthen It)
- ✅ Keep the badge
- Add: Data sources panel with clickable citations
- Add: "Methodology" modal explaining each model

### 5.2 Validation & Uncertainty Quantification
- Show model performance metrics (MAE, RMSE, R² on test set)
- Add confidence intervals on EAR estimates
- Add sensitivity analysis: "How sensitive is shortfall to rainfall forecast error?"

### 5.3 Regulatory Compliance
- Add UNFC classification indicator on reserve panel
- Add MCDR-compatible export (CSV/Excel for statutory returns)
- Add "Auditable trail" showing all assumptions

### 5.4 Multi-Mine View (If Time Permits)
- Currently: Single mine (Balaghat)
- Enhancement: Add dropdown for all 11 MOIL mines
- National dashboard: Total EAR, aggregate shortfall risk
- **Why:** Shows scalability

### 5.5 Mobile-Responsive
- Mine Manager uses this at 6:45 AM on phone
- Ensure all panels work on mobile viewport

---

## Implementation Roadmap (Time-Based)

### Week 1: Critical Gaps
**Days 1-2:** Prospectivity data collection & feature engineering
**Days 3-4:** Prospectivity ML model + API endpoints
**Days 5-6:** Prospectivity frontend (map + targets panel)
**Day 7:** Integration testing & documentation

### Week 2: Enhancement & Polish
**Days 8-9:** Add soil moisture, LST, NDVI to forecast model
**Days 10-11:** Rebuild action optimization with data-driven approach
**Days 12-13:** Dynamic EAR calculator with breakdown
**Day 14:** Full system integration test

### Week 3: Polish & Presentation Prep
**Days 15-16:** UI/UX refinement, mobile responsiveness
**Days 17-18:** Add validation metrics, uncertainty quantification
**Days 19-20:** Documentation, video demo, rehearsal
**Day 21:** Final testing, backup video recording

---

## Risk Mitigation

### Risk 1: Satellite Data Download is Slow
**Mitigation:** 
- Start downloads immediately (can run overnight)
- Use pre-processed datasets from Google Earth Engine (faster)
- Have cached synthetic data as fallback

### Risk 2: Prospectivity Model Doesn't Converge
**Mitigation:**
- Start with simpler distance-to-known-mines baseline
- Use Random Forest (more forgiving than deep learning)
- Pre-train on publicly available manganese occurrence database

### Risk 3: Time Runs Out
**Mitigation:**
- Follow priority order strictly
- Each priority is independently demoable
- Always have working system (never break main branch)

---

## Success Metrics

### Technical Validation
- [ ] Prospectivity model AUC-ROC > 0.75
- [ ] Forecast MAE < 15% of monthly target
- [ ] Action recommendations improve simulated output by >10%
- [ ] EAR calculation time < 2 seconds

### Demo Quality
- [ ] Can explain every number on screen
- [ ] Judges can interact with sliders and see immediate results
- [ ] Mobile-friendly
- [ ] Runs offline (no internet dependency during demo)
- [ ] Backup video recorded

### Story Quality
- [ ] Clear problem statement (30 sec)
- [ ] Differentiator from other teams identified (15 sec)
- [ ] Live demo hits all three PS requirements (3 min)
- [ ] Q&A prep covers top 10 technical questions

---

## New Components Summary

### Backend (Python/FastAPI)
```
New Routers:
├── routers/prospectivity.py      # Reserve identification endpoints
├── routers/eo_constraints.py     # Multi-satellite constraint data
└── routers/ear.py                # Dynamic EAR calculation

New ML Modules:
├── ml/prism/prospectivity.py     # Mineral prospectivity mapping
├── ml/prism/features.py          # Feature engineering for MPM
├── ml/prism/ear.py               # Dynamic EAR computation
├── ml/earth_observation/
│   ├── sentinel2.py              # Optical indices (NDVI, band ratios)
│   ├── sentinel1.py              # SAR processing
│   ├── landsat.py                # Thermal LST
│   └── constraints.py            # Unified constraint calculator

New Scripts:
├── scripts/fetch_satellite_data.py
└── scripts/train_prospectivity_model.py
```

### Frontend (React/TypeScript)
```
New Components:
├── components/ProspectivityMap.tsx
├── components/ProspectivityPanel.tsx
├── components/EOConstraintsPanel.tsx
├── components/EARExplainer.tsx
├── components/ActionOptimizer.tsx
├── components/ValidationMetrics.tsx
└── components/MethodologyModal.tsx

New Pages:
├── pages/ProspectivityView.tsx
└── pages/MultiMineDashboard.tsx (optional)
```

---

## Judging Criteria Alignment

| SIH Criterion | How We Address It | Evidence in Demo |
|---|---|---|
| **Innovation** | Dual-scale approach (prospectivity + production), EAR concept | EAR explainer, live slider interactions |
| **Feasibility** | Uses proven ML (RF, LightGBM), open data (Sentinel, GSI) | Data sources panel, working prototype |
| **Scalability** | Designed for all 11 MOIL mines, open-source stack | Multi-mine dropdown, cloud-ready architecture |
| **Impact** | Directly reduces shortfalls, finds new reserves | ROI calculation in PDF report |
| **Use of Space Tech** | Multi-source satellite integration (S1, S2, Landsat, MODIS) | EO constraints panel, prospectivity feature importance |
| **Completeness** | Addresses all 3 PS objectives | Checklist slide: A✓ B✓ C✓ |
| **Presentation** | Clear problem → gap → solution → demo → impact story | Rehearsed 7-minute pitch |
| **Technical Depth** | Can explain every model, every assumption | Q&A prep doc (see below) |

---

## Top 10 Q&A to Prepare

1. **"How did you validate your prospectivity model without drilling new holes?"**
   - Answer: K-fold spatial cross-validation, leave-one-mine-out, comparison to GSI known occurrences

2. **"What if the satellite data is cloudy?"**
   - Answer: Time-series compositing (median of last 90 days), SAR works through clouds, model handles missing data

3. **"How do you handle underground mines where satellites can't see production?"**
   - Answer: Satellites see constraints (rain, temp, vegetation access), not ore itself. Also use surface stockpile detection.

4. **"Your EAR concept is new — how do you know it's accurate?"**
   - Answer: Reconciliation loop (compare predicted EAR to actual mined tonnes), confidence intervals, sensitivity analysis

5. **"Can MOIL actually afford to implement this?"**
   - Answer: Open-source stack, runs on single server, satellite data is free, ROI calculation shows payback in 3 months

6. **"What about safety and DGMS compliance?"**
   - Answer: We don't auto-generate blast designs (safety-critical). All recommendations are decision-support, final approval is human.

7. **"How is this different from Datamine/Vulcan?"**
   - Answer: Those are static geological models. We connect geology → operations → real-time forecasting. Complementary, not competitive.

8. **"Your synthetic data looks too good. What about real data?"**
   - Answer: (Point to badge) We're transparent. Model architecture is the product. Real data integration is Phase 2. Here's the adapter design.

9. **"What if equipment logs aren't digitized?"**
   - Answer: Fallback to manual entry form, OCR of paper logs, or simple average-based model. Design is data-agnostic.

10. **"Can this work for other minerals beyond manganese?"**
    - Answer: Yes. Prospectivity model retrains on any labeled mineral occurrences. Production model is commodity-agnostic.

---

## Final Checklist Before Submission

### Code & System
- [ ] All endpoints return valid responses (no 500 errors)
- [ ] Frontend handles loading/error states gracefully
- [ ] Works offline (seeded database, no external API calls during demo)
- [ ] Runs on fresh install (test on clean VM)
- [ ] Git repo is clean (no secrets, no huge files)

### Demo
- [ ] Screen recording backup (full 5-min walkthrough)
- [ ] Laptop fully charged, external mouse/clicker ready
- [ ] Fallback: phone with demo video if laptop fails
- [ ] Team knows who presents what (clear role division)

### Documentation
- [ ] README.md explains how to run in 3 steps
- [ ] ARCHITECTURE.md explains system design
- [ ] DATA_SOURCES.md lists every dataset with citations
- [ ] API documentation (auto-generated Swagger)

### Presentation
- [ ] Slides: 8-10 slides max (problem, gap, solution, demo, impact, next)
- [ ] Rehearsed 3 times (full 7-min pitch + 3-min Q&A)
- [ ] Timer set (don't overrun)
- [ ] Intro: Who we are, problem statement ID, what we built (30 sec)

---

## What NOT to Do (Common SIH Mistakes)

❌ **Don't** build a chatbot and call it AI
❌ **Don't** show only a prospectivity heatmap (1/3 of problem)
❌ **Don't** show only a production dashboard (1/3 of problem)
❌ **Don't** use deep learning if simpler models work (judges will ask about overfitting)
❌ **Don't** hide your synthetic data (transparency = credibility)
❌ **Don't** claim 99% accuracy (instant red flag)
❌ **Don't** skip error handling (demo gods are cruel)
❌ **Don't** present without rehearsing (nervous rambling loses points)

✅ **Do** connect reserves to production (the EAR bridge)
✅ **Do** show uncertainty quantification (P10/P50/P90)
✅ **Do** use multiple satellite sources (claim the "space tech" theme)
✅ **Do** make it interactive (sliders, filters, real-time updates)
✅ **Do** explain every assumption proactively
✅ **Do** show you understand MOIL's real constraints (DGMS, MCDR, underground vs opencast)

---

## Conclusion

**Your Current App:** Strong technical foundation, but addresses only 40% of problem statement.

**After This Plan:** Complete solution addressing all three objectives (identify reserves, predict shortfalls, suggest actions) with genuine multi-source space technology integration and a unique "digital twin" narrative no other team will have.

**The Differentiator:** The Effective Accessible Reserve (EAR) concept — the mathematical bridge connecting geological reserves to achievable production. This is your "aha moment."

**Timeline:** Realistically 3 weeks of focused work. Doable for 2-3 people working part-time.

**Outcome:** A prototype that looks like a real product, not a hackathon demo. Professional, explainable, scalable, and directly aligned with Ministry of Steel priorities.

Good luck! 🚀
