# OreSight — Technical Implementation Tasks
## Detailed Task Breakdown for SIH Improvement

---

## Phase 1: Reserve Identification Module (Priority 1 — Days 1-7)

### Task 1.1: Satellite Data Collection Pipeline
**File:** `scripts/fetch_satellite_data.py`
**Time:** 1 day
**Dependencies:** None (start immediately)

```python
# Subtasks:
- [ ] Set up Google Earth Engine Python API or sentinelhub-py
- [ ] Define bounding box for Nagpur-Balaghat manganese belt
- [ ] Download Sentinel-2 imagery (last 2 years, cloud-filtered)
      → Bands: B2,B3,B4,B8 (visible/NIR), B11,B12 (SWIR)
- [ ] Calculate spectral indices:
      → NDVI = (NIR - Red) / (NIR + Red)
      → Iron oxide ratio = B4/B2
      → SWIR ratio = B11/B8
      → Clay index = B11/B12
- [ ] Download DEM (SRTM 30m or Cartosat)
- [ ] Export as GeoTIFF rasters aligned to common grid
- [ ] Save metadata (acquisition dates, cloud cover %)
```

**Output:** `data/satellite/balaghat_belt/` folder with:
- `sentinel2_composite.tif` (multi-band)
- `ndvi.tif`
- `iron_oxide_index.tif`
- `dem.tif`
- `metadata.json`

---

### Task 1.2: Geological Data Integration
**File:** `scripts/fetch_geological_data.py`
**Time:** 0.5 days
**Dependencies:** None

```python
# Subtasks:
- [ ] Download GSI geological map from NGDR/Bhukosh
      → URL: https://bhukosh.gsi.gov.in/
- [ ] Extract known MOIL mine locations (11 mines) as point shapefile
- [ ] Download GSI manganese occurrence database (if available)
- [ ] Convert to GeoJSON for web display
- [ ] Create training labels:
      → Positive class: Known mine locations + 1km buffer
      → Negative class: Random points >5km from any mine
```

**Output:** `data/geology/`
- `moil_mines.geojson` (11 points)
- `gsi_manganese_occurrences.geojson`
- `training_labels.geojson` (positive/negative samples)
- `lithology.geojson` (rock types)

---

### Task 1.3: Feature Engineering for Prospectivity
**File:** `ml/prism/features.py`
**Time:** 1 day
**Dependencies:** Task 1.1, 1.2

```python
# Subtasks:
- [ ] Load all rasters into xarray Dataset
- [ ] Extract features at each grid cell (100m resolution):
      → Spectral indices (NDVI, iron oxide, clay, SWIR)
      → DEM derivatives (slope, aspect, curvature)
      → Distance to known mines
      → Distance to geological contacts (gondite boundaries)
      → Distance to lineaments (Canny edge detection on DEM)
- [ ] Create training dataframe:
      → Each row = one grid cell
      → Columns = 15-20 features + label (0/1)
- [ ] Handle NaN values (interpolation or masking)
- [ ] Standardize features (z-score normalization)
```

**Output:** `data/processed/prospectivity_features.parquet`
- ~1M rows × 20 columns
- Ready for ML training

---

### Task 1.4: Prospectivity ML Model
**File:** `ml/prism/prospectivity.py`
**Time:** 1 day
**Dependencies:** Task 1.3

```python
# Subtasks:
- [ ] Split data with spatial cross-validation (sklearn GroupKFold by lat/lon bins)
- [ ] Train Random Forest classifier:
      → n_estimators=200
      → max_depth=15
      → class_weight='balanced' (handle imbalance)
- [ ] Evaluate on test set:
      → AUC-ROC, precision-recall curve
      → Feature importance plot
- [ ] Generate probability map for entire region
- [ ] Rank top 50 prospect cells, cluster into targets
- [ ] Save model as pickle
```

**Output:**
- `models/prospectivity_rf_model.pkl`
- `data/processed/prospectivity_map.tif` (probability raster)
- `data/processed/top_targets.geojson` (top 10 prospects)
- `reports/model_metrics.json` (AUC, precision, recall)

---

### Task 1.5: Prospectivity API Endpoints
**File:** `backend/app/routers/prospectivity.py`
**Time:** 0.5 days
**Dependencies:** Task 1.4

```python
# Endpoints to implement:

@router.get("/api/prospectivity/map")
def get_prospectivity_map():
    """
    Return probability map as GeoJSON or PNG tiles (TMS/XYZ format)
    """

@router.get("/api/prospectivity/targets")
def get_top_targets(limit: int = 10):
    """
    Return top N prospect targets ranked by probability
    Response: [
        {
            "rank": 1,
            "lat": 21.234,
            "lon": 80.567,
            "probability": 0.87,
            "confidence": "high",
            "evidence": {
                "iron_oxide_index": 0.92,
                "distance_to_known_mine_km": 2.3,
                ...
            }
        }
    ]
    """

@router.get("/api/prospectivity/features")
def get_feature_importance():
    """
    Return model feature importance for explainability
    """

@router.post("/api/prospectivity/evaluate")
def evaluate_location(lat: float, lon: float):
    """
    Evaluate prospectivity at a custom location
    """
```

---

### Task 1.6: Prospectivity Frontend
**Files:** 
- `frontend/src/components/ProspectivityMap.tsx`
- `frontend/src/components/ProspectivityPanel.tsx`
**Time:** 2 days
**Dependencies:** Task 1.5

```typescript
// Components to build:

// 1. ProspectivityMap.tsx
- [ ] Add raster layer overlay (prospectivity heatmap)
- [ ] Add markers for top 10 targets
- [ ] Add click handler to show target details
- [ ] Layer controls (toggle geology, satellite, targets)
- [ ] Legend showing probability scale

// 2. ProspectivityPanel.tsx
- [ ] Table of top 10 targets with columns:
      → Rank, Coordinates, Probability, Distance to nearest mine
- [ ] Click to zoom to target on map
- [ ] "Export drill plan" button (download as KML)
- [ ] Evidence breakdown (bar chart of feature contributions)

// 3. FeatureImportanceChart.tsx
- [ ] Horizontal bar chart showing feature importance
- [ ] Tooltip explaining each feature
```

**Output:** New tab/section in dashboard showing prospectivity view

---

## Phase 2: Enhanced Space Technology Integration (Days 8-11)

### Task 2.1: Multi-Source Satellite Constraint Data
**File:** `ml/earth_observation/constraints.py`
**Time:** 1.5 days
**Dependencies:** None

```python
# Subtasks:

# 2.1.1: Soil Moisture (Sentinel-1 or SMAP)
- [ ] Download Sentinel-1 VV/VH backscatter time series
- [ ] Convert to soil moisture proxy (regression or lookup table)
- [ ] Alternative: Use SMAP L4 soil moisture product
- [ ] Aggregate to mine-level daily time series

# 2.1.2: Land Surface Temperature (Landsat 8/MODIS)
- [ ] Download Landsat 8 thermal band (Band 10)
- [ ] Convert DN to temperature (Kelvin → Celsius)
- [ ] Alternative: MODIS LST daily product (faster)
- [ ] Extract mine-level daily max temperature

# 2.1.3: Enhanced Vegetation Index
- [ ] Already have NDVI from Task 1.1
- [ ] Create seasonal baseline (Jan-Jun average)
- [ ] Calculate anomaly: current - baseline
- [ ] High anomaly = vegetation stress = potential access issues

# 2.1.4: Unified Constraint Calculator
def get_operational_constraints(mine_id, start_date, end_date):
    """
    Returns daily constraint scores (0-1) for:
    - rainfall_constraint
    - soil_moisture_constraint  [NEW]
    - temperature_constraint    [NEW]
    - vegetation_constraint     [NEW]
    """
```

**Output:**
- `data/eo_constraints/balaghat_constraints.csv`
- Daily time series with 4 constraint columns
- API-ready format

---

### Task 2.2: Enhance Forecast Model with EO Constraints
**File:** `ml/pulse/forecast.py` (modify existing)
**Time:** 1 day
**Dependencies:** Task 2.1

```python
# Modifications:
- [ ] Add new features to feature engineering pipeline:
      → lag_7_soil_moisture
      → lag_7_temperature
      → rolling_30_ndvi_anomaly
- [ ] Retrain LightGBM model with expanded feature set
- [ ] Update SHAP driver calculation to include new features
- [ ] Add feature importance comparison (before/after)
```

**Output:** Updated forecast model with better accuracy

---

### Task 2.3: EO Constraints Dashboard Panel
**File:** `frontend/src/components/EOConstraintsPanel.tsx`
**Time:** 1 day
**Dependencies:** Task 2.2

```typescript
// Component features:
- [ ] 4 mini gauges showing current constraint levels:
      → Rainfall (existing)
      → Soil Moisture [NEW]
      → Temperature [NEW]
      → Vegetation Access [NEW]
- [ ] 7-day forecast for each constraint
- [ ] Historical constraint correlation chart
      → Show: "When soil moisture > 0.4, production drops 18%"
- [ ] Satellite image thumbnail with last acquisition date
```

---

## Phase 3: Data-Driven Corrective Actions (Days 12-13)

### Task 3.1: Action Library Database
**File:** `backend/app/models.py` (add tables)
**Time:** 0.5 days

```python
# New SQLAlchemy models:

class ActionLibrary(Base):
    __tablename__ = "action_library"
    id: int
    action_type: str  # e.g., 'extra_shift', 'equipment_redeploy'
    description: str
    base_delta_tonnes: float
    cost_inr: float
    lead_time_days: int
    constraints: JSON  # {"min_equipment": 3, "weather": "no_heavy_rain"}

class ActionOutcome(Base):
    __tablename__ = "action_outcomes"
    id: int
    action_id: int  # FK to ActionLibrary
    mine_id: int
    applied_date: date
    predicted_delta_tonnes: float
    actual_delta_tonnes: float  # Reconciled 30 days later
    success: bool
```

**Output:** Migration script, seeded action library

---

### Task 3.2: Action Effectiveness Model
**File:** `ml/pulse/actions.py`
**Time:** 1 day
**Dependencies:** Task 3.1

```python
# Subtasks:
- [ ] Feature engineering for action effectiveness:
      → action_type (one-hot encoded)
      → current_equipment_count
      → weather_forecast_7d (rainfall, temperature)
      → historical_success_rate
      → season (monsoon vs non-monsoon)
- [ ] Train regression model: context → actual Δtonnes
      → Use LightGBM or Linear Regression
- [ ] Update action suggestion endpoint to use learned effectiveness
```

---

### Task 3.3: Optional — MILP Optimizer
**File:** `ml/pulse/optimizer.py`
**Time:** 1 day (optional, high impact)
**Dependencies:** Task 3.2

```python
# Using Google OR-Tools or PuLP:
- [ ] Define decision variables: x_i ∈ {0,1} for each action
- [ ] Objective: maximize Σ(x_i × Δtonnes_i) - λ × Σ(x_i × cost_i)
- [ ] Constraints:
      → Budget: Σ(x_i × cost_i) ≤ budget
      → Equipment: Σ(x_i requiring equipment E) ≤ available_E
      → Time windows: no overlapping actions
- [ ] Solve and return optimal action bundle
```

**Output:** Enhanced `/api/actions/optimize` endpoint

---

## Phase 4: Dynamic EAR Calculator (Days 14-15)

### Task 4.1: EAR Computation Engine
**File:** `ml/prism/ear.py`
**Time:** 1 day

```python
# Subtasks:
- [ ] Load block model (from existing blockmodel.py)
- [ ] Apply accessibility factors:
      1. Depth factor: f_depth = exp(-depth / 500)
      2. Equipment factor: f_equip = available_LHDs / required_LHDs
      3. Climate factor: f_climate = (1 - flood_risk_probability)
      4. Infra factor: f_infra = 1 / (1 + distance_to_haul_road / 1000)
- [ ] Compute block-level EAR: EAR_block = tonnage × f_depth × f_equip × f_climate × f_infra
- [ ] Sum over all blocks: total_EAR = Σ EAR_block
- [ ] Return factor breakdown for explainability
```

---

### Task 4.2: EAR Explainer UI
**File:** `frontend/src/components/EARExplainer.tsx`
**Time:** 1 day
**Dependencies:** Task 4.1

```typescript
// Interactive component:
- [ ] Funnel chart showing:
      Geological Reserve (100%)
        ↓ depth factor (-15%)
      Depth-Adjusted (85%)
        ↓ equipment factor (-10%)
      Equipment-Adjusted (75%)
        ↓ climate factor (-20% in monsoon)
      Climate-Adjusted (55%)
        ↓ infra factor (-5%)
      **Effective Accessible Reserve (50%)**

- [ ] Sliders for what-if:
      → "Add 1 LHD" → f_equip increases → EAR increases
      → "20% heavier monsoon" → f_climate decreases → EAR decreases
- [ ] Real-time recalculation (< 2 sec)
- [ ] "Blocks at risk" table (blocks with lowest accessibility)
```

---

## Phase 5: Polish & Validation (Days 16-21)

### Task 5.1: Validation Metrics Dashboard
**File:** `frontend/src/components/ValidationMetrics.tsx`
**Time:** 1 day

```typescript
// Display:
- [ ] Forecast model performance:
      → MAE (Mean Absolute Error)
      → RMSE
      → R² on test set
      → P50 calibration plot (predicted vs actual)
- [ ] Prospectivity model performance:
      → AUC-ROC curve
      → Precision-Recall curve
      → Confusion matrix
- [ ] Action effectiveness:
      → Predicted vs actual Δtonnes scatter plot
      → Success rate by action type
```

---

### Task 5.2: Methodology Modal
**File:** `frontend/src/components/MethodologyModal.tsx`
**Time:** 0.5 days

```typescript
// Modal with tabs:
- [ ] Tab 1: Reserve Identification
      → Explain prospectivity model
      → List features used
      → Show validation approach
- [ ] Tab 2: Production Forecasting
      → Explain LightGBM + quantile regression
      → List features
      → Explain SHAP
- [ ] Tab 3: EAR Calculation
      → Formula breakdown
      → Explain each factor
- [ ] Tab 4: Data Sources
      → Table with dataset, source, license, date
```

---

### Task 5.3: Multi-Mine Support (Optional)
**Time:** 1 day

```python
# Backend:
- [ ] Ensure all endpoints accept mine_id parameter
- [ ] Seed database with basic info for all 11 MOIL mines
- [ ] Create aggregate KPI endpoint: /api/national-dashboard

# Frontend:
- [ ] Add mine selector dropdown in header
- [ ] Create NationalDashboard.tsx page showing:
      → Total EAR across all mines
      → Aggregate shortfall risk
      → Mine-wise comparison table
```

---

### Task 5.4: Mobile Responsiveness
**Time:** 1 day

```css
/* Ensure all components work on mobile:
- [ ] Map: touch-friendly zoom/pan
- [ ] Charts: horizontal scroll if needed
- [ ] Tables: collapse to cards on small screens
- [ ] Sliders: large enough touch targets
- [ ] Test on real mobile device (not just Chrome dev tools)
*/
```

---

### Task 5.5: Documentation & Demo Prep
**Time:** 2 days

```markdown
# Documentation to write:
- [ ] ARCHITECTURE.md (system design, data flow diagrams)
- [ ] DATA_SOURCES.md (every dataset with citation)
- [ ] API.md (comprehensive API reference)
- [ ] DEPLOYMENT.md (how to deploy on cloud)
- [ ] Update README.md with new features

# Demo prep:
- [ ] Record 5-min screen capture demo (backup video)
- [ ] Create 8-slide presentation:
      1. Team intro + problem statement
      2. Gap analysis
      3. Our solution (3 pillars: A, B, C)
      4. Architecture diagram
      5. Demo walkthrough (live or video)
      6. Validation & results
      7. Impact & ROI
      8. Roadmap & thank you
- [ ] Rehearse 3 times (full pitch + Q&A)
- [ ] Prepare answers to top 10 expected questions
```

---

## Testing Checklist

### Unit Tests
```bash
# Backend tests to write:
- [ ] test_prospectivity.py (model predictions)
- [ ] test_forecast.py (existing, update for new features)
- [ ] test_ear.py (factor calculations)
- [ ] test_constraints.py (EO data parsing)

# Run: pytest backend/tests/
```

### Integration Tests
```bash
# API tests:
- [ ] test_api_prospectivity.py (all endpoints return 200)
- [ ] test_api_forecast.py (existing, update)
- [ ] test_api_actions.py (optimize endpoint)

# Run: pytest backend/tests/integration/
```

### End-to-End Test
```bash
# Manual checklist:
- [ ] Fresh install on clean machine (follow README)
- [ ] All dashboards load without errors
- [ ] All sliders work and update in < 3 sec
- [ ] PDF report generates successfully
- [ ] Mobile view works
- [ ] Offline mode works (no internet during demo)
```

---

## Git Workflow

### Branch Strategy
```bash
# Main branches:
- main (stable, demo-ready at all times)
- develop (integration branch)

# Feature branches (create from develop):
- feature/prospectivity
- feature/eo-constraints
- feature/dynamic-ear
- feature/action-optimization
- feature/ui-polish

# Merge flow:
feature/* → develop (PR + review) → main (after testing)
```

### Commit Conventions
```
feat: Add prospectivity mapping module
fix: Correct EAR calculation for depth factor
docs: Update API documentation with new endpoints
test: Add unit tests for constraints module
refactor: Optimize satellite data loading
chore: Update dependencies
```

---

## Dependencies to Add

### Backend (`requirements.txt` additions)
```
# Already have: fastapi, sqlalchemy, pandas, lightgbm, shap, scikit-learn

# Add for prospectivity:
xarray>=2023.0.0
rasterio>=1.3.0
rioxarray>=0.13.0
geopandas>=0.12.0
shapely>=2.0.0
pyproj>=3.4.0

# Add for satellite data:
earthengine-api>=0.1.350  # Google Earth Engine
sentinelhub>=3.9.0        # Sentinel Hub (alternative)
pystac-client>=0.7.0      # STAC catalog search
odc-stac>=0.3.0           # Load from STAC

# Add for optimization (optional):
ortools>=9.6.0            # Google OR-Tools for MILP
pulp>=2.7.0               # Alternative MILP solver

# Add for spatial analysis:
geopy>=2.3.0              # Distance calculations
```

### Frontend (`package.json` additions)
```json
{
  "dependencies": {
    // Already have: react, react-dom, recharts, maplibre-gl

    // Add for raster display:
    "georaster": "^1.6.0",
    "georaster-layer-for-maplibre": "^1.0.0",

    // Add for advanced charts:
    "d3": "^7.8.5",
    "@nivo/bar": "^0.83.0",  // For fancy funnel chart

    // Add for PDF export (optional):
    "jspdf": "^2.5.1",
    "html2canvas": "^1.4.1"
  }
}
```

---

## Time Estimates by Priority

| Priority | Description | Time | Can Skip? |
|----------|-------------|------|-----------|
| **P0 (Critical)** | Prospectivity module (Tasks 1.1-1.6) | 6 days | ❌ No |
| **P0 (Critical)** | EO constraints (Tasks 2.1-2.3) | 3 days | ❌ No |
| **P1 (High)** | Dynamic EAR (Tasks 4.1-4.2) | 2 days | ⚠️ Partial OK |
| **P1 (High)** | Data-driven actions (Tasks 3.1-3.2) | 1.5 days | ⚠️ Partial OK |
| **P2 (Medium)** | MILP optimizer (Task 3.3) | 1 day | ✅ Yes |
| **P2 (Medium)** | Validation UI (Task 5.1-5.2) | 1.5 days | ✅ Yes |
| **P3 (Nice-to-have)** | Multi-mine support (Task 5.3) | 1 day | ✅ Yes |
| **P3 (Nice-to-have)** | Mobile polish (Task 5.4) | 1 day | ⚠️ Basic only |
| **P0 (Critical)** | Documentation & demo (Task 5.5) | 2 days | ❌ No |

**Total Critical Path:** ~14 days of actual work
**Total with Nice-to-haves:** ~19 days
**Recommended Team Size:** 2-3 people working part-time (evenings/weekends)

---

## Risk Management

### Top Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Satellite data download fails / too slow | High | High | Start downloads NOW. Cache local copies. Have synthetic fallback. |
| Prospectivity model underfits (poor AUC) | Medium | High | Start with simple distance-to-known-mines baseline. Use imbalanced-learn SMOTE. Try XGBoost. |
| Feature engineering takes too long | Medium | Medium | Use pre-computed indices from Earth Engine. Skip complex features. |
| MILP optimizer doesn't converge | Medium | Low | Keep greedy fallback. MILP is optional. |
| Integration bugs in last week | High | High | Merge feature branches early. Test continuously. Never break main branch. |
| Team member drops out | Medium | High | Solo-friendly design. Critical tasks (P0) have primary + backup owner. |
| Demo laptop fails | Low | Critical | Backup video (mandatory). Cloud deployment (optional). Phone with video (last resort). |

---

## Success Criteria

### Minimum Viable Demo (must have all):
- ✅ Prospectivity map showing 10+ targets
- ✅ Forecast with soil moisture + temperature (not just rainfall)
- ✅ EAR funnel showing factor breakdown
- ✅ Actions with learned effectiveness
- ✅ All three PS objectives demonstrably addressed
- ✅ Working on fresh laptop install
- ✅ Backup video recorded

### Stretch Goals (nice to have):
- MILP optimizer for actions
- Multi-mine dashboard
- Mobile-responsive
- Real-time satellite data refresh
- Reconciliation loop (predicted vs actual)

---

## Daily Standup Template

Use this for team sync (5 min daily):

```
Date: [YYYY-MM-DD]
Team Member: [Name]

Yesterday:
- [ ] Task X completed (link to PR)
- [ ] Task Y in progress (80% done)

Today:
- [ ] Task Z (finish by EOD)
- [ ] Code review for Task A

Blockers:
- Waiting on satellite data download
- Need help with raster alignment

Health Check:
- On track / At risk / Blocked
```

---

## Final Pre-Demo Checklist (T-1 Day)

### System
- [ ] Full smoke test on fresh install (different laptop)
- [ ] All endpoints return 200 (no 500 errors)
- [ ] Frontend loads without console errors
- [ ] Offline mode works (seed database, no external API calls)
- [ ] Backup video plays without issues

### Data
- [ ] Database seeded with latest data
- [ ] All GeoJSON files in correct folders
- [ ] Satellite images loading correctly
- [ ] No lorem ipsum or placeholder text visible

### Demo Flow
- [ ] Rehearsed 3 times (with timer)
- [ ] Backup video queued and ready
- [ ] Slides finalized (no "TODO" slides)
- [ ] Q&A answers written down

### Hardware
- [ ] Laptop fully charged
- [ ] External mouse/clicker (if presenting)
- [ ] HDMI/USB-C adapter tested
- [ ] Phone with backup video (airplane mode to avoid calls)

### Team
- [ ] Everyone knows their speaking part
- [ ] Roles assigned (who drives demo, who answers Q&A)
- [ ] Dress code confirmed
- [ ] Transport to venue arranged

---

## Post-Demo Actions (If You Win)

### Phase 2 Development (3-6 months)
- [ ] Real data integration with MOIL (MOU/NDA)
- [ ] Production deployment (AWS/Azure with ISRO Bhuvan tie-in)
- [ ] Advanced features:
      → Reconciliation loop (actual vs predicted)
      → Multi-commodity support
      → Advanced 3D viewer
      → Equipment survival model
      → Hierarchical forecasting
- [ ] Pilot at 2-3 MOIL mines
- [ ] Publication: paper on EAR methodology

### Commercialization (if pursued)
- [ ] Patent application for EAR calculation method
- [ ] Form company or license to existing mining tech firm
- [ ] Expand to other PSUs (Coal India, NMDC, HZL)
- [ ] International markets (Australia, Canada, South Africa)

---

Good luck! You have a strong foundation — now make it complete. 🚀
