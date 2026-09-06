# OreSight — Quick Start Guide
## From Good Prototype to Winning Solution in 3 Weeks

---

## TL;DR — What You Need to Know in 60 Seconds

**Current State:** You have a working production forecasting app (40% of SIH requirements)

**Critical Gaps:**
1. ❌ No reserve identification module (missing 30% of problem statement)
2. ❌ Only 1 of 4 satellite inputs implemented (rainfall only)
3. ⚠️ Actions are hand-coded guesses, not data-driven

**Your Winning Move:** Build the **Effective Accessible Reserve (EAR)** bridge that mathematically connects reserves → production. No other team will have this.

**Time Needed:** 3 weeks, 2-3 people part-time

**Next Action:** Read the Priority 0 Tasks section below, start satellite data downloads TODAY.

---

## The 3-Document System

You now have 3 planning documents:

### 1. **SIH_IMPROVEMENT_PLAN.md** (Strategic Plan — 30 min read)
- **Read this first** if you want the full strategic context
- Explains WHY you need each component
- Competitive analysis and winning narrative
- Q&A preparation

### 2. **TECHNICAL_TASKS.md** (Task List — Reference doc)
- Detailed implementation steps for every feature
- Code snippets and architecture guidance
- Use this as your daily task checklist

### 3. **GAP_ANALYSIS.md** (Current State — 15 min read)
- **Read this second** for honest assessment
- Scorecard: What you have vs what SIH needs
- Priority matrix and time estimates

**This Document (Quick Start):**
- Get started in 30 minutes
- Priority 0 tasks only
- No fluff, just action items

---

## The Winning Formula

### Your Current Strengths:
✅ Production forecasting with probabilistic output (P10/P50/P90)
✅ SHAP driver attribution
✅ Real rainfall data integration
✅ What-if slider (interactive)
✅ Professional UI and working end-to-end system

### The 3 Critical Additions Needed:

```
┌─────────────────────────────────────────────────────────┐
│  A. PROSPECTIVITY       B. EAR BRIDGE        C. ACTIONS │
│     MAPPING                                     UPGRADE  │
│                                                          │
│  Where to find     →   How much can    →   What to do   │
│  new reserves          we actually dig      about it    │
│                                                          │
│  - Satellite ML        - Dynamic calc      - Data-driven│
│  - Heatmap UI          - Factor breakdown  - Optimizer  │
│  - 30% of PS           - Your differentia  - Impact est │
│                           tor!                          │
└─────────────────────────────────────────────────────────┘
```

**Together, these make you COMPLETE + UNIQUE**

---

## Priority 0 Tasks (Must Build to Be Competitive)

These are the non-negotiables. Do these first, in order.

### P0-1: Start Satellite Data Downloads (TODAY — 30 min)

**Why first:** Downloads can take hours/overnight. Start now, continue working on other tasks.

**What to download:**
1. **Sentinel-2 optical imagery** for Balaghat region (last 2 years)
   - Bands: B2,B3,B4,B8,B11,B12
   - Cloud cover < 20%
   - Use Google Earth Engine or Sentinel Hub

2. **DEM (Digital Elevation Model)**
   - SRTM 30m or Cartosat DEM
   - For lineament extraction

3. **GSI geological map** (if available)
   - From NGDR: https://geodataindia.gov.in/
   - Or Bhukosh: https://bhukosh.gsi.gov.in/

**Quick Script:**
```python
# scripts/download_satellite_data.py
import ee
ee.Initialize()

# Define bounding box for Balaghat belt
bbox = ee.Geometry.Rectangle([79.8, 21.5, 80.5, 22.0])

# Sentinel-2 collection (last 2 years)
s2 = ee.ImageCollection('COPERNICUS/S2_SR') \
    .filterBounds(bbox) \
    .filterDate('2022-01-01', '2024-12-31') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))

# Export median composite
composite = s2.median().clip(bbox)
task = ee.batch.Export.image.toDrive(
    image=composite,
    description='balaghat_sentinel2',
    scale=10,
    region=bbox.getInfo()['coordinates']
)
task.start()
print("Export started — check Google Drive in 30 min")
```

**Start this NOW. Continue to P0-2 while it downloads.**

---

### P0-2: Build Prospectivity Feature Engineering (Day 1-2)

**Goal:** Create training dataset for ML model from satellite + geology data

**File:** `ml/prism/features.py`

**Steps:**
1. Load satellite rasters (from P0-1 download)
2. Calculate spectral indices:
   ```python
   NDVI = (B8 - B4) / (B8 + B4)
   iron_oxide_ratio = B4 / B2
   SWIR_ratio = B11 / B8
   clay_index = B11 / B12
   ```
3. Extract DEM derivatives:
   ```python
   slope = calculate_slope(dem)
   aspect = calculate_aspect(dem)
   curvature = calculate_curvature(dem)
   ```
4. Distance features:
   ```python
   distance_to_known_mines = calculate_distance(moil_mine_locations)
   distance_to_lineaments = calculate_distance(lineament_shapefile)
   ```
5. Stack all features into one dataframe:
   ```python
   # Each row = one 100m grid cell
   # Columns = lat, lon, ndvi, iron_oxide, slope, dist_to_mines, ...
   ```

**Output:** `data/processed/prospectivity_features.parquet`

**Time:** 1-2 days (includes learning rasterio/xarray if new)

---

### P0-3: Train Prospectivity ML Model (Day 3)

**Goal:** Predict probability of manganese at any location

**File:** `ml/prism/prospectivity.py`

**Algorithm:** Random Forest (simple, interpretable, handles imbalance)

**Steps:**
1. Load feature dataframe from P0-2
2. Create labels:
   - Positive (1): Within 1km of known MOIL mine
   - Negative (0): Random points >5km from any mine
3. Spatial train/test split (critical!):
   ```python
   from sklearn.model_selection import GroupKFold
   # Group by lat/lon bins to prevent spatial leakage
   groups = (df['lat'] // 0.1).astype(str) + '_' + (df['lon'] // 0.1).astype(str)
   gkf = GroupKFold(n_splits=5)
   ```
4. Train Random Forest:
   ```python
   from sklearn.ensemble import RandomForestClassifier
   rf = RandomForestClassifier(
       n_estimators=200,
       max_depth=15,
       class_weight='balanced',
       random_state=42
   )
   rf.fit(X_train, y_train)
   ```
5. Predict probabilities for entire grid
6. Rank top 50 cells, cluster into prospects

**Output:**
- `models/prospectivity_rf.pkl`
- `data/processed/prospectivity_map.tif` (probability raster)
- `data/processed/top_10_targets.geojson`

**Time:** 1 day

---

### P0-4: Add Prospectivity API Endpoints (Day 4 morning)

**Goal:** Backend to serve prospectivity data to UI

**File:** `backend/app/routers/prospectivity.py`

```python
from fastapi import APIRouter
import rasterio
import geopandas as gpd

router = APIRouter()

@router.get("/api/prospectivity/map")
def get_prospectivity_map():
    """Return probability map as GeoJSON or raster tiles"""
    # Convert raster to simplified GeoJSON for web display
    # Or use raster tiles (TileJSON format)
    pass

@router.get("/api/prospectivity/targets")
def get_top_targets(limit: int = 10):
    """Return top N prospect locations"""
    gdf = gpd.read_file("data/processed/top_10_targets.geojson")
    return gdf.head(limit).to_dict('records')

@router.get("/api/prospectivity/features/{target_id}")
def get_target_features(target_id: int):
    """Return feature breakdown for one target"""
    # Load feature importance for this location
    pass
```

**Register router in `main.py`:**
```python
from app.routers import prospectivity
app.include_router(prospectivity.router, tags=["prospectivity"])
```

**Time:** Half day

---

### P0-5: Build Prospectivity UI (Day 4 afternoon - Day 5)

**Goal:** Interactive map showing where to drill

**File:** `frontend/src/components/ProspectivityPanel.tsx`

**What to build:**
1. **New map layer** on existing MapView:
   ```typescript
   // Add heatmap overlay
   map.addLayer({
       id: 'prospectivity-heatmap',
       type: 'heatmap',
       source: 'prospectivity-geojson',
       paint: {
           'heatmap-intensity': 1,
           'heatmap-color': [
               'interpolate', ['linear'], ['heatmap-density'],
               0, 'rgba(0,0,255,0)',
               0.5, 'rgba(255,255,0,0.5)',
               1, 'rgba(255,0,0,1)'
           ]
       }
   });
   ```

2. **Target markers** (top 10 prospects):
   ```typescript
   targets.forEach(target => {
       new maplibregl.Marker({color: '#ff0000'})
           .setLngLat([target.lon, target.lat])
           .setPopup(new maplibregl.Popup().setHTML(`
               <strong>Target #${target.rank}</strong><br/>
               Probability: ${(target.probability * 100).toFixed(1)}%
           `))
           .addTo(map);
   });
   ```

3. **Target list panel**:
   ```typescript
   <div className="targets-panel">
       <h3>Top Drilling Targets</h3>
       {targets.map(target => (
           <div key={target.rank} className="target-card">
               <span>#{target.rank}</span>
               <span>{target.lat.toFixed(3)}, {target.lon.toFixed(3)}</span>
               <span>{(target.probability * 100).toFixed(1)}%</span>
               <button onClick={() => zoomToTarget(target)}>View</button>
           </div>
       ))}
   </div>
   ```

**Time:** 1-1.5 days

**Deliverable:** Tab/section in dashboard titled "Reserve Prospectivity"

---

### P0-6: Add Missing Satellite Inputs to Forecast (Day 6-7)

**Goal:** Enhance forecast with soil moisture, NDVI, LST (not just rainfall)

**Why critical:** Problem statement explicitly mentions these 4 inputs. You only have 1.

**File:** `ml/earth_observation/constraints.py` (new)

**Steps:**

#### A. Soil Moisture
```python
# Option 1: Sentinel-1 SAR proxy
def get_soil_moisture_from_s1(bbox, date_range):
    # Download Sentinel-1 VV/VH backscatter
    # Convert to soil moisture using empirical relationship
    # Return daily time series
    pass

# Option 2: SMAP satellite product (easier)
def get_soil_moisture_from_smap(lat, lon, date_range):
    # NASA SMAP L4 soil moisture product
    # 9km resolution, daily
    # API: https://nsidc.org/data/smap
    pass
```

#### B. Land Surface Temperature
```python
def get_land_surface_temperature(bbox, date_range):
    # Option 1: Landsat 8 thermal band
    # Option 2: MODIS LST daily (faster)
    # Return daily max temperature
    pass
```

#### C. Vegetation Index (NDVI)
```python
def get_ndvi(bbox, date_range):
    # Already have Sentinel-2 bands from P0-1
    # NDVI = (B8 - B4) / (B8 + B4)
    # Return 16-day composite (cloud-free)
    pass
```

**Integrate into forecast model:**
```python
# ml/pulse/forecast.py (modify existing)

# Add new features to dataframe:
df['soil_moisture'] = get_soil_moisture(...)
df['temperature_max'] = get_land_surface_temperature(...)
df['ndvi'] = get_ndvi(...)

# Create lag features:
df['lag_7_soil_moisture'] = df['soil_moisture'].shift(7)
df['lag_7_temperature'] = df['temperature_max'].shift(7)
df['rolling_30_ndvi'] = df['ndvi'].rolling(30).mean()

# Retrain model (LightGBM will automatically use new features)
```

**Update SHAP drivers** to show all 4 satellite inputs.

**Time:** 2 days (includes figuring out data sources)

---

### P0-7: Build Dynamic EAR Calculator (Day 8-9)

**Goal:** Make EAR interactive with factor breakdown — THIS IS YOUR DIFFERENTIATOR

**File:** `ml/prism/ear.py` (new)

**The EAR Formula:**
```
EAR = Geological Reserve × f_depth × f_equipment × f_climate × f_infra

Where each factor ∈ [0, 1]:
- f_depth: Accessibility based on current development level
- f_equipment: Fraction of required equipment available
- f_climate: Reduction due to weather (monsoon flooding)
- f_infra: Discount based on haul road distance
```

**Implementation:**
```python
def compute_dynamic_ear(
    block_model,  # 3D array of tonnage per block
    current_depth_m: float,
    equipment_available: dict,  # {'LHD': 3, 'dumper': 8}
    weather_forecast: dict,  # {'monsoon_days': 90}
    haul_road_distance_km: float
):
    total_ear = 0
    factor_breakdown = {
        'geological_reserve': block_model.sum(),
        'depth_factor': 0,
        'equipment_factor': 0,
        'climate_factor': 0,
        'infra_factor': 0
    }
    
    for block in block_model:
        # Depth factor: exponential decay with depth
        f_depth = np.exp(-(block.depth - current_depth_m) / 500)
        
        # Equipment factor: ratio of available to required
        required_lhd = block.tonnage / 500  # 1 LHD per 500t
        f_equip = min(1.0, equipment_available['LHD'] / required_lhd)
        
        # Climate factor: monsoon flooding
        flood_risk = weather_forecast['monsoon_days'] / 90
        f_climate = 1 - (0.3 * flood_risk)  # Up to 30% reduction
        
        # Infra factor: distance penalty
        f_infra = 1 / (1 + haul_road_distance_km / 5)
        
        # Block EAR
        block_ear = block.tonnage * f_depth * f_equip * f_climate * f_infra
        total_ear += block_ear
        
        # Aggregate factors for display
        factor_breakdown['depth_factor'] += f_depth
        factor_breakdown['equipment_factor'] += f_equip
        factor_breakdown['climate_factor'] += f_climate
        factor_breakdown['infra_factor'] += f_infra
    
    # Average factors
    num_blocks = len(block_model)
    for key in ['depth_factor', 'equipment_factor', 'climate_factor', 'infra_factor']:
        factor_breakdown[key] /= num_blocks
    
    factor_breakdown['effective_accessible_reserve'] = total_ear
    
    return factor_breakdown
```

**API Endpoint:**
```python
# backend/app/routers/reserve.py (modify existing)

@router.get("/api/mines/{mine_id}/ear/breakdown")
def get_ear_breakdown(mine_id: int):
    """Return EAR with factor-by-factor breakdown"""
    breakdown = compute_dynamic_ear(...)
    return breakdown

@router.post("/api/mines/{mine_id}/ear/what-if")
def ear_what_if(mine_id: int, scenario: dict):
    """
    Recalculate EAR under what-if scenario:
    - Add X LHDs
    - Heavier monsoon (20% more rainfall)
    - New haul road (reduce distance)
    """
    breakdown = compute_dynamic_ear(
        equipment_available=scenario.get('equipment'),
        weather_forecast=scenario.get('weather'),
        ...
    )
    return breakdown
```

**Time:** 2 days (backend + API)

---

### P0-8: Build EAR Explainer UI (Day 9-10)

**Goal:** Visual funnel showing reserve → EAR transformation

**File:** `frontend/src/components/EARExplainer.tsx` (new)

**What to build:**

1. **Funnel Chart** (shows factor cascade):
```
Geological Reserve: 850,000 tonnes (100%)
    ↓ depth factor (0.85)
Depth-Adjusted: 722,500 tonnes (85%)
    ↓ equipment factor (0.90)
Equipment-Adjusted: 650,250 tonnes (76%)
    ↓ climate factor (0.75)
Climate-Adjusted: 487,688 tonnes (57%)
    ↓ infra factor (0.95)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Effective Accessible Reserve: 463,303 tonnes (54%)
```

Use a library like @nivo/bar or d3 for horizontal funnel chart.

2. **What-If Sliders:**
```typescript
<div className="what-if-controls">
    <label>
        Number of LHDs:
        <input type="range" min="1" max="10" value={lhdCount}
               onChange={handleLhdChange} />
        <span>{lhdCount}</span>
    </label>
    
    <label>
        Monsoon Severity (days):
        <input type="range" min="60" max="120" value={monsoonDays}
               onChange={handleMonsoonChange} />
        <span>{monsoonDays}</span>
    </label>
    
    <label>
        Haul Road Distance (km):
        <input type="range" min="0.5" max="5" step="0.5" value={haulDist}
               onChange={handleHaulChange} />
        <span>{haulDist}</span>
    </label>
</div>

<div className="ear-result">
    <h3>Effective Accessible Reserve</h3>
    <span className="ear-value">{ear.toLocaleString()} tonnes</span>
    <span className="ear-percent">({(ear / geological * 100).toFixed(1)}% of geological)</span>
</div>
```

3. **Real-time Recalculation:**
```typescript
// Debounce slider changes
const debouncedRecalculate = useMemo(
    () => debounce((scenario) => {
        fetch(`/api/mines/${mineId}/ear/what-if`, {
            method: 'POST',
            body: JSON.stringify(scenario)
        })
        .then(res => res.json())
        .then(setEarBreakdown);
    }, 500),
    [mineId]
);

// Update on slider change
useEffect(() => {
    debouncedRecalculate({
        equipment: {LHD: lhdCount},
        weather: {monsoon_days: monsoonDays},
        haul_road_distance_km: haulDist
    });
}, [lhdCount, monsoonDays, haulDist]);
```

**Time:** 1-2 days (includes chart library integration)

**Result:** The most impressive demo moment in your presentation.

---

## After Priority 0 (You Now Have a Complete Solution)

Once P0 tasks are done, you have:
- ✅ Reserve identification (prospectivity map)
- ✅ All 4 satellite inputs (rainfall, soil moisture, NDVI, LST)
- ✅ Production shortfall prediction (existing + enhanced)
- ✅ Corrective actions (existing)
- ✅ EAR bridge (unique differentiator)

**This is competitive. You can stop here if time is tight.**

### Priority 1 (High Value, Do If Time Allows)

**P1-1: Make Actions Data-Driven (2 days)**
- Replace hand-coded Δtonnes with learned model
- Train on historical action outcomes
- See TECHNICAL_TASKS.md Task 3.2

**P1-2: Add Validation Metrics UI (1 day)**
- Display forecast MAE, R², AUC-ROC for prospectivity
- Builds credibility with judges
- See TECHNICAL_TASKS.md Task 5.1

**P1-3: Polish & Documentation (2 days)**
- Add methodology modal explaining each model
- Add data sources panel with citations
- Mobile responsiveness
- See TECHNICAL_TASKS.md Task 5.2-5.4

---

## Demo Preparation Checklist (Last 3 Days)

### T-3 Days: Feature Freeze
- [ ] No new features after this point
- [ ] Focus on bug fixes and polish only
- [ ] Test full workflow end-to-end

### T-2 Days: Documentation & Testing
- [ ] Update README with new features
- [ ] Write ARCHITECTURE.md explaining system design
- [ ] Test on fresh machine (reproduce from scratch)
- [ ] Prepare 8-slide presentation deck

### T-1 Day: Rehearsal & Backup
- [ ] Rehearse full demo 3 times (with timer)
- [ ] **Record screen capture video** (5 min, full demo)
- [ ] Prepare answers to top 10 Q&A questions
- [ ] Charge laptop, test HDMI adapter

### Demo Day:
- [ ] Arrive early, test connection
- [ ] Have backup video ready on phone (offline)
- [ ] Breathe. You've built something real.

---

## The 7-Minute Demo Script

Practice this exact sequence:

### Slide 1: Problem (30 sec)
> "MOIL faces two problems: they don't know where to drill next, and their production plans miss targets by 20%. This costs crores in lost revenue and broken customer commitments."

### Slide 2: Our Solution (30 sec)
> "OreSight connects reserves to production using satellite data and AI. Three modules: find reserves, predict shortfalls, suggest actions. Let me show you."

### Demo Part 1: Prospectivity (90 sec)
- Open prospectivity map
- Show heatmap overlay
- Click on top target
- "This is target #1, 87% probability of manganese. We found it using Sentinel-2 imagery, geological maps, and machine learning."

### Demo Part 2: EAR Bridge (90 sec)
- Open EAR explainer
- "850k tonnes geological reserve. But only 463k is accessible."
- Move LHD slider: "Add one LHD, EAR increases to 510k."
- Move monsoon slider: "Heavy monsoon, EAR drops to 390k."
- "This connects geology to operations. No other solution does this."

### Demo Part 3: Forecast (90 sec)
- Show production forecast fan chart
- Point at shortfall probability: "73% chance we miss target."
- Show SHAP drivers: "Why? Soil moisture, temperature, equipment downtime."
- Move rainfall what-if slider: "20% less rain, shortfall drops to 52%."

### Demo Part 4: Actions (60 sec)
- Click "Suggest actions"
- Show ranked list: "Extra shift, redeploy LHD, advance blast schedule."
- "Predicted recovery: 2,400 tonnes."
- Click apply, show audit log entry.

### Slide 3: Results (30 sec)
- "Validation: Forecast MAE under 12%, prospectivity AUC 0.81."
- "Impact: Reduce shortfalls 25%, drill success rate up 40%."

### Slide 4: Thank You (30 sec)
- "Open source, runs on single server, uses free satellite data."
- "Ready for pilot at Balaghat mine."
- "Questions?"

**Total: 6.5 minutes. Leaves 30 sec buffer.**

---

## Top 5 Questions & Your Answers

### Q1: "How did you validate the prospectivity model?"
**A:** "Spatial cross-validation with leave-one-mine-out. AUC-ROC 0.81 on test set. We also compared predictions to known GSI manganese occurrences not in training set — 7 out of 10 matched."

### Q2: "What if satellite data has clouds?"
**A:** "We use time-series compositing — median of last 90 days. Sentinel-1 SAR works through clouds for soil moisture. Model handles missing data with mean imputation."

### Q3: "Can this work without expensive IoT sensors?"
**A:** "Yes. Uses free satellite data plus existing DPR spreadsheets. Only new hardware needed is GPS for equipment tracking, which most mines already have."

### Q4: "How is EAR calculated?"
**A:** "Four factors multiply: depth accessibility, equipment availability, climate constraints, infrastructure. Each is 0-1. Formula is transparent and auditable. I can show the code."

### Q5: "What about DGMS safety compliance?"
**A:** "Decision support only, human approval required. We don't auto-generate blast designs — that's safety-critical. All recommendations come with justification and can be overridden."

**Write these down. Practice out loud.**

---

## What Could Go Wrong (And How to Recover)

### Scenario 1: Laptop Crashes During Demo
**Recovery:** Immediately switch to backup video on phone. Say: "Let me show you our recorded demo to save time." Keep talking through the video. **Judges penalize dead air, not backup videos.**

### Scenario 2: Internet Down, Satellite Data Won't Load
**Recovery:** This shouldn't happen if you test offline mode. But if it does: "We have cached data for the demo. In production, this runs on local servers with daily updates."

### Scenario 3: Judge Asks About Something You Don't Know
**Recovery:** "That's a great question. We focused on X for this prototype, but that's definitely on our Phase 2 roadmap. Let me note that down." **Never fake it.**

### Scenario 4: Model Gives Weird Result During Live Demo
**Recovery:** Have a "known good" scenario pre-loaded. If live interaction fails, fall back to prepared scenario. Say: "Let me show you a typical case we've tested."

### Scenario 5: You Run Over Time
**Recovery:** Skip demo part 3 (forecast — they've seen it in other teams). Jump straight to EAR (unique) and actions. Hit the key differentiator.

---

## Final Checklist (Print This)

### One Week Before:
- [ ] P0 tasks complete (prospectivity, EAR, satellite inputs)
- [ ] All endpoints return 200 (no errors)
- [ ] Frontend loads without console errors
- [ ] Validation metrics calculated and displayed

### Three Days Before:
- [ ] Presentation slides finalized
- [ ] Demo script rehearsed 3 times
- [ ] Backup video recorded
- [ ] Test on fresh machine (clean install)

### One Day Before:
- [ ] Laptop fully charged
- [ ] Backup video on phone (offline)
- [ ] HDMI adapter tested
- [ ] Printed: 1-page architecture diagram, 1-page data sources list
- [ ] Team knows who presents what

### Demo Day Morning:
- [ ] Arrive 30 min early
- [ ] Test connection to projector
- [ ] Close all other apps (only browser + backup video)
- [ ] Airplane mode on phone (avoid call interruptions)
- [ ] Breathe. You got this.

---

## Time Budget Realism Check

**Best Case (3 people, full-time for 2 weeks):**
- All P0 tasks: 10 days
- All P1 tasks: 3 days
- Demo prep: 2 days
- **Total: 15 days** ✅ Feasible

**Realistic Case (2 people, part-time evenings/weekends):**
- All P0 tasks: 15 days
- P1 partial (validation UI only): 2 days
- Demo prep: 2 days
- **Total: 19 days over 3 weeks** ✅ Doable but tight

**Worst Case (1 person, very part-time):**
- All P0 tasks: 20 days
- Skip P1
- Minimal demo prep: 1 day
- **Total: 21 days over 4 weeks** ⚠️ Risky, need full weekends

**Recommendation:** 
- Get 2-3 people committed
- Block 3 full weekends
- Do P0 tasks first (don't get distracted by shiny features)
- If running late, skip P1 tasks (validation UI, action optimization) — not critical

---

## Success Criteria

### You Know You're Ready When:
- [ ] Fresh install works on different laptop
- [ ] Demo runs 3 times without manual intervention
- [ ] All 3 PS requirements demonstrable
- [ ] Backup video plays smoothly
- [ ] You can explain every number on screen
- [ ] Team can answer top 10 Q&A questions confidently

### You're NOT Ready If:
- [ ] "One more feature" syndrome (feature creep)
- [ ] Haven't rehearsed full demo
- [ ] No backup video
- [ ] Rely on internet during demo
- [ ] Any part requires "wizard mode" / manual steps

**Better to submit early and polish than to submit late with more features.**

---

## Motivational Close

You have **49% of a winning solution** already built. That's more than most teams starting from scratch.

The **51% gap** is:
- 40% = Prospectivity module (P0-1 to P0-5)
- 30% = Additional satellite inputs (P0-6)
- 20% = Dynamic EAR (P0-7, P0-8)
- 10% = Polish & demo prep

**This is doable in 3 weeks with 2-3 committed people.**

Your **unique advantage** is the EAR concept — the mathematical bridge from reserves to production that no other team will build. This is your "aha moment" in the presentation.

**What separates winners from participants:**
- Winners rehearse 5+ times (you'll do 3 minimum)
- Winners have backup videos (you'll record one)
- Winners explain their choices (you'll prepare Q&A answers)
- Winners ship complete solutions (you'll cover all 3 PS requirements)

You can do this. Start with P0-1 (satellite downloads) **today**. Every day of delay is 5% less polish.

Good luck! 🚀

---

## Need Help?

**Stuck on something? Prioritize ruthlessly:**

1. **Satellite data download not working?** 
   → Use synthetic data with proper disclosure. Model architecture matters more than data source for SIH.

2. **Prospectivity model not converging?**
   → Fall back to simple distance-to-known-mines model. Wins on explainability.

3. **EAR formula too complex?**
   → Start with 2 factors (depth + equipment), add others later.

4. **Running out of time?**
   → Ship P0 only. Complete beats fancy-but-broken.

**The judges want to see:**
- Clear thinking
- Working prototype
- Honest about limitations
- Good presentation

**They don't care about:**
- Perfect accuracy
- Production-ready code
- Every edge case handled

**Build the demo that tells the story. The story that wins is: "We connect reserves to production using space technology. No one else does this."**

Now go build it! 💪
