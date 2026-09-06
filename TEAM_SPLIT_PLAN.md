# OreSight — 2-Person Team Split Plan
## Parallel Development Strategy for Fast MVP

---

## Team Structure

**Person A (You):** Backend + ML Focus
**Person B (Your Friend):** Frontend + UI Focus

**Strategy:** Clean separation by layer to minimize merge conflicts
**Timeline:** 10 days to MVP (all P0 tasks)
**Branch Strategy:** Feature branches → develop → main

---

## Work Split Philosophy

### Why This Split Works:
✅ **Minimal file overlap** — Backend/ML vs Frontend rarely touch same files
✅ **Clear interface contract** — API endpoints are the handoff point
✅ **Parallel work possible** — Mock data enables frontend work before backend is done
✅ **Natural skill division** — Python/ML vs TypeScript/React

### Merge Conflict Zones (Watch These):
⚠️ `backend/app/main.py` — Router registration (coordinate before merging)
⚠️ `frontend/src/api/client.ts` — API client definitions (Person A defines, Person B uses)
⚠️ README.md — Both will update (Person A owns setup, Person B owns features)

---

## Daily Sync Protocol (5 Minutes)

**Every Morning (Before Starting Work):**
```
1. Pull latest from develop branch
2. Quick standup (async via chat if needed):
   - What I finished yesterday
   - What I'm working on today
   - Any blockers or API changes needed
3. Agree on any shared file changes
```

**Every Evening (Before Committing):**
```
1. Push to your feature branch
2. Update team Trello/GitHub project board
3. Flag if tomorrow's work needs coordination
```

---

## Person A (Backend + ML) — Your Tasks

### Your Mission:
Build the data pipeline, ML models, and APIs. Your friend consumes your APIs via frontend.

### Your Branches:
```
main
├── develop
    ├── feature/prospectivity-ml       (Days 1-3)
    ├── feature/eo-constraints         (Days 4-5)
    ├── feature/dynamic-ear            (Days 6-7)
    └── feature/api-endpoints          (Days 8-10)
```

---

### Day 1: Satellite Data Collection + Setup

**Branch:** `feature/prospectivity-ml`

**Tasks:**
- [ ] Set up Google Earth Engine account or Sentinel Hub API
- [ ] Create `scripts/fetch_satellite_data.py`
- [ ] Download Sentinel-2 imagery for Balaghat belt (last 2 years)
      → Bands: B2, B3, B4, B8, B11, B12
      → Output: `data/satellite/sentinel2_composite.tif`
- [ ] Download DEM (SRTM or Cartosat)
      → Output: `data/satellite/dem.tif`
- [ ] Download GSI geological map from NGDR
      → Output: `data/geology/moil_mines.geojson`

**Deliverable:** Data files in `data/` folder, documented in `DATA_SOURCES.md`

**Evening Commit Message:**
```
feat(data): Add satellite data collection pipeline

- Download Sentinel-2 composite for Balaghat belt
- Fetch DEM and geological maps
- Document data sources and licenses
```

**Handoff to Person B:** Share `moil_mines.geojson` — they'll need it for map markers

---

### Day 2: Prospectivity Feature Engineering

**Branch:** `feature/prospectivity-ml` (continue)

**Tasks:**
- [ ] Create `ml/prism/features.py`
- [ ] Calculate spectral indices:
      ```python
      NDVI = (B8 - B4) / (B8 + B4)
      iron_oxide_ratio = B4 / B2
      SWIR_ratio = B11 / B8
      clay_index = B11 / B12
      ```
- [ ] Extract DEM derivatives (slope, aspect, curvature)
- [ ] Calculate distance features:
      - Distance to known MOIL mines
      - Distance to lineaments (Canny edge detection on DEM)
- [ ] Create training dataset:
      - Positive labels: 1km buffer around MOIL mines
      - Negative labels: Random points >5km from mines
- [ ] Save: `data/processed/prospectivity_features.parquet`

**Testing:** Verify parquet file loads correctly, has ~20 columns

**Evening Commit:**
```
feat(ml): Add prospectivity feature engineering pipeline

- Calculate spectral indices from Sentinel-2
- Extract DEM derivatives and distance features
- Generate training labels from MOIL mine locations
```

---

### Day 3: Prospectivity ML Model Training

**Branch:** `feature/prospectivity-ml` (continue)

**Tasks:**
- [ ] Create `ml/prism/prospectivity.py`
- [ ] Implement spatial cross-validation:
      ```python
      from sklearn.model_selection import GroupKFold
      groups = (df['lat'] // 0.1).astype(str) + '_' + (df['lon'] // 0.1).astype(str)
      gkf = GroupKFold(n_splits=5)
      ```
- [ ] Train Random Forest:
      ```python
      RandomForestClassifier(
          n_estimators=200,
          max_depth=15,
          class_weight='balanced'
      )
      ```
- [ ] Generate probability map for entire region
- [ ] Rank top 50 cells, cluster into top 10 targets
- [ ] Save outputs:
      - `models/prospectivity_rf.pkl`
      - `data/processed/prospectivity_map.tif`
      - `data/processed/top_10_targets.geojson`
      - `reports/prospectivity_metrics.json` (AUC, precision, recall)

**Testing:** 
- AUC-ROC should be > 0.70 (acceptable) or > 0.75 (good)
- Top 10 targets should be near known mines (validation)

**Evening Commit:**
```
feat(ml): Train prospectivity ML model

- Random Forest with spatial CV
- Generate probability map and top 10 targets
- AUC-ROC: 0.78 on test set
```

**Handoff to Person B:** 
- Share `top_10_targets.geojson` 
- Share `prospectivity_metrics.json`
- They'll need these for UI on Day 4

---

### Day 4: EO Constraints Data Pipeline

**Branch:** `feature/eo-constraints`

**Tasks:**
- [ ] Create `ml/earth_observation/constraints.py`
- [ ] Implement soil moisture fetcher:
      ```python
      def get_soil_moisture(lat, lon, start_date, end_date):
          # Option 1: Sentinel-1 VV/VH proxy
          # Option 2: SMAP L4 product (easier)
          # Return daily time series
      ```
- [ ] Implement LST (Land Surface Temperature) fetcher:
      ```python
      def get_land_surface_temperature(bbox, start_date, end_date):
          # Landsat 8 thermal or MODIS LST
          # Return daily max temperature
      ```
- [ ] Implement NDVI fetcher:
      ```python
      def get_ndvi(bbox, start_date, end_date):
          # Use Sentinel-2 from Day 1
          # Return 16-day composite
      ```
- [ ] Download data for Balaghat mine (2018-present)
- [ ] Save: `data/eo_constraints/balaghat_constraints.csv`
      - Columns: date, rainfall_mm, soil_moisture, temperature_max, ndvi

**Testing:** CSV should have ~2000 rows (daily, 2018-2024), no NaN values

**Evening Commit:**
```
feat(eo): Add multi-source satellite constraint pipeline

- Fetch soil moisture from SMAP
- Extract LST from MODIS
- Calculate NDVI from Sentinel-2
- Generate daily constraint time series
```

---

### Day 5: Enhanced Forecast Model

**Branch:** `feature/eo-constraints` (continue)

**Tasks:**
- [ ] Modify `ml/pulse/forecast.py`
- [ ] Add new features to forecast model:
      ```python
      # Load EO constraints
      constraints = pd.read_csv('data/eo_constraints/balaghat_constraints.csv')
      df = df.merge(constraints, on='date')
      
      # Create lag features
      df['lag_7_soil_moisture'] = df['soil_moisture'].shift(7)
      df['lag_7_temperature'] = df['temperature_max'].shift(7)
      df['rolling_30_ndvi'] = df['ndvi'].rolling(30).mean()
      ```
- [ ] Retrain LightGBM model with expanded features
- [ ] Update SHAP driver calculation
- [ ] Generate feature importance comparison (before/after)
- [ ] Save: `reports/forecast_metrics_v2.json`

**Testing:** 
- MAE should improve or stay same (not degrade)
- SHAP drivers should now include soil moisture, temperature, NDVI

**Evening Commit:**
```
feat(forecast): Enhance model with multi-source EO constraints

- Add soil moisture, LST, NDVI features
- Retrain LightGBM with expanded feature set
- Update SHAP attribution to include new drivers
- MAE improved from 1,850t to 1,620t
```

**Handoff to Person B:** Updated forecast API schema (they'll update client.ts)

---

### Day 6-7: Dynamic EAR Calculator

**Branch:** `feature/dynamic-ear`

**Tasks Day 6:**
- [ ] Create `ml/prism/ear.py`
- [ ] Implement EAR calculation with factors:
      ```python
      def compute_dynamic_ear(
          block_model,
          current_depth_m,
          equipment_available,  # {'LHD': 3, 'dumper': 8}
          weather_forecast,     # {'monsoon_days': 90}
          haul_road_distance_km
      ):
          # Calculate accessibility factors
          f_depth = np.exp(-(block.depth - current_depth_m) / 500)
          f_equip = available / required
          f_climate = 1 - (0.3 * monsoon_risk)
          f_infra = 1 / (1 + distance / 5)
          
          # Compute EAR
          ear = tonnage * f_depth * f_equip * f_climate * f_infra
          
          return {
              'geological_reserve': ...,
              'depth_factor': ...,
              'equipment_factor': ...,
              'climate_factor': ...,
              'infra_factor': ...,
              'effective_accessible_reserve': ...
          }
      ```
- [ ] Write unit tests for each factor
- [ ] Test with current block model

**Tasks Day 7:**
- [ ] Create API endpoint in `backend/app/routers/reserve.py`:
      ```python
      @router.get("/api/mines/{mine_id}/ear/breakdown")
      def get_ear_breakdown(mine_id: int):
          """Return EAR with factor breakdown"""
          
      @router.post("/api/mines/{mine_id}/ear/what-if")
      def ear_what_if(mine_id: int, scenario: dict):
          """Recalculate EAR under what-if scenario"""
      ```
- [ ] Add Pydantic schemas for request/response
- [ ] Test endpoints with curl/Postman
- [ ] Document API in Swagger docs

**Evening Commit Day 7:**
```
feat(ear): Add dynamic EAR calculator with factor breakdown

- Implement accessibility factors (depth, equipment, climate, infra)
- Create API endpoints for EAR breakdown and what-if scenarios
- Add comprehensive tests for factor calculations
```

**Handoff to Person B:** 
- API contract for EAR endpoints
- Example request/response JSON
- They'll build UI on Day 8-9

---

### Day 8-9: Prospectivity API Endpoints

**Branch:** `feature/api-endpoints`

**Tasks Day 8:**
- [ ] Create `backend/app/routers/prospectivity.py`
- [ ] Implement endpoints:
      ```python
      @router.get("/api/prospectivity/map")
      def get_prospectivity_map():
          """Return probability map as GeoJSON or tiles"""
          
      @router.get("/api/prospectivity/targets")
      def get_top_targets(limit: int = 10):
          """Return top N prospect locations"""
          
      @router.get("/api/prospectivity/features/{target_id}")
      def get_target_features(target_id: int):
          """Return feature breakdown for one target"""
      ```
- [ ] Convert raster to web-friendly format (GeoJSON or COG tiles)
- [ ] Add response caching (these don't change often)
- [ ] Test all endpoints

**Tasks Day 9:**
- [ ] Register all new routers in `main.py`:
      ```python
      from app.routers import prospectivity, reserve
      app.include_router(prospectivity.router, tags=["prospectivity"])
      # Update reserve router with new endpoints
      ```
- [ ] Update Pydantic schemas in `schemas.py`
- [ ] Generate OpenAPI docs (verify at /docs)
- [ ] Write integration tests
- [ ] Update `requirements.txt` with new dependencies

**Evening Commit Day 9:**
```
feat(api): Add prospectivity API endpoints

- Implement map, targets, and features endpoints
- Register new routers in main app
- Add comprehensive integration tests
- Update OpenAPI documentation
```

**Handoff to Person B:** 
- Full API documentation
- Example responses for all endpoints
- They'll wire up frontend on Day 9-10

---

### Day 10: Integration & Polish

**Branch:** `feature/api-endpoints` → merge to `develop`

**Tasks:**
- [ ] Merge all your feature branches to `develop`
- [ ] Resolve any conflicts
- [ ] Run full backend test suite
- [ ] Test all APIs with curl/Postman
- [ ] Update `backend/README.md` with:
      - New endpoints documentation
      - New environment variables (if any)
      - Updated setup instructions
- [ ] Coordinate with Person B on final integration

**Deliverables:**
- [ ] All APIs return 200 (no 500 errors)
- [ ] Swagger docs are complete
- [ ] Sample data seeded and working
- [ ] Backend tests pass

**Evening:** Ready for Person B to integrate frontend

---

## Person B (Frontend + UI) — Your Friend's Tasks

### Their Mission:
Build beautiful, interactive UI that consumes Person A's APIs. Enable parallel work with mock data.

### Their Branches:
```
main
├── develop
    ├── feature/prospectivity-ui       (Days 3-5)
    ├── feature/eo-constraints-ui      (Days 6-7)
    ├── feature/ear-explainer          (Days 8-9)
    └── feature/integration-polish     (Day 10)
```

---

### Day 1-2: Mock Data Setup + Existing UI Enhancement

**Branch:** `feature/base-ui-improvements`

**Strategy:** While Person A downloads satellite data, Person B preps the UI foundation

**Tasks Day 1:**
- [ ] Create mock data files for new features:
      ```typescript
      // frontend/src/mocks/prospectivity.mock.ts
      export const mockProspectivityTargets = [
          {
              rank: 1,
              lat: 21.789,
              lon: 80.234,
              probability: 0.87,
              confidence: 'high',
              evidence: {
                  iron_oxide_index: 0.92,
                  ndvi_anomaly: 0.15,
                  distance_to_known_mine_km: 2.3
              }
          },
          // ... 9 more
      ];
      
      export const mockEARBreakdown = {
          geological_reserve: 850000,
          depth_factor: 0.85,
          equipment_factor: 0.90,
          climate_factor: 0.75,
          infra_factor: 0.95,
          effective_accessible_reserve: 463303
      };
      ```
- [ ] Set up API client with mock toggle:
      ```typescript
      // frontend/src/api/client.ts
      const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true';
      
      export async function getProspectivityTargets() {
          if (USE_MOCKS) return mockProspectivityTargets;
          const res = await api.get('/prospectivity/targets');
          return res.data;
      }
      ```

**Tasks Day 2:**
- [ ] Enhance existing dashboard layout for new panels:
      - Add tab navigation or collapsible sections
      - Prepare grid layout for new components
- [ ] Polish existing components:
      - Improve loading states
      - Add skeleton loaders
      - Better error messages
- [ ] Test mobile responsiveness of existing features

**Evening Commit Day 2:**
```
feat(ui): Add mock data and improve layout for new features

- Create mock data for prospectivity and EAR
- Set up mock toggle for parallel development
- Enhance dashboard layout with tab navigation
- Improve loading and error states
```

---

### Day 3-4: Prospectivity Map UI

**Branch:** `feature/prospectivity-ui`

**Tasks Day 3:**
- [ ] Create `frontend/src/components/ProspectivityMap.tsx`
- [ ] Add heatmap layer to existing MapView:
      ```typescript
      // Use mock GeoJSON initially
      useEffect(() => {
          if (!map) return;
          
          map.addSource('prospectivity', {
              type: 'geojson',
              data: mockProspectivityGeoJSON  // Person A will provide real data Day 3
          });
          
          map.addLayer({
              id: 'prospectivity-heatmap',
              type: 'heatmap',
              source: 'prospectivity',
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
      }, [map]);
      ```
- [ ] Add layer toggle controls (show/hide prospectivity)
- [ ] Add legend explaining probability colors

**Tasks Day 4:**
- [ ] Create `frontend/src/components/ProspectivityPanel.tsx`
- [ ] Build target list UI:
      ```typescript
      <div className="targets-panel">
          <h3>Top Drilling Targets</h3>
          <div className="targets-list">
              {targets.map(target => (
                  <div key={target.rank} className="target-card"
                       onClick={() => handleTargetClick(target)}>
                      <div className="target-rank">#{target.rank}</div>
                      <div className="target-coords">
                          {target.lat.toFixed(3)}, {target.lon.toFixed(3)}
                      </div>
                      <div className="target-probability">
                          {(target.probability * 100).toFixed(1)}%
                      </div>
                      <button>View on Map</button>
                  </div>
              ))}
          </div>
      </div>
      ```
- [ ] Add click handler to zoom map to target
- [ ] Add target markers with popups on map
- [ ] Style with Tailwind (match existing UI theme)

**Evening Commit Day 4:**
```
feat(ui): Add prospectivity map and target list

- Implement heatmap overlay on map
- Create interactive target list panel
- Add zoom-to-target functionality
- Style to match existing UI theme
```

**Coordination:** On Day 4 evening, Person A will push `top_10_targets.geojson`. Person B switches from mock to real data.

---

### Day 5: Prospectivity Integration + Polish

**Branch:** `feature/prospectivity-ui` (continue)

**Tasks:**
- [ ] Replace mock data with real API calls:
      ```typescript
      // Update client.ts
      export async function getProspectivityTargets() {
          const res = await api.get('/api/prospectivity/targets');
          return res.data;
      }
      ```
- [ ] Add feature importance chart:
      ```typescript
      // Create FeatureImportanceChart.tsx
      // Show which satellite/geological features contributed most
      // Use recharts BarChart (horizontal)
      ```
- [ ] Add loading states and error handling
- [ ] Add "Export drill plan" button (download KML)
- [ ] Test with real data from Person A
- [ ] Polish animations and transitions

**Testing:** 
- Map loads without errors
- Clicking target zooms to correct location
- All 10 targets display correctly

**Evening Commit:**
```
feat(ui): Integrate real prospectivity data and add feature importance

- Switch from mock to real API data
- Add feature importance visualization
- Implement KML export for drill planning
- Polish loading states and animations
```

---

### Day 6-7: EO Constraints Dashboard Panel

**Branch:** `feature/eo-constraints-ui`

**Tasks Day 6:**
- [ ] Create `frontend/src/components/EOConstraintsPanel.tsx`
- [ ] Build 4 gauge visualizations:
      ```typescript
      <div className="eo-constraints-grid">
          {[
              {name: 'Rainfall', value: rainfall, unit: 'mm'},
              {name: 'Soil Moisture', value: soilMoisture, unit: '%'},
              {name: 'Temperature', value: temp, unit: '°C'},
              {name: 'Vegetation', value: ndvi, unit: 'NDVI'}
          ].map(constraint => (
              <div className="constraint-gauge">
                  <CircularGauge 
                      value={constraint.value}
                      max={getMaxForConstraint(constraint.name)}
                      color={getColorForValue(constraint.value)}
                  />
                  <span>{constraint.name}</span>
                  <span>{constraint.value} {constraint.unit}</span>
              </div>
          ))}
      </div>
      ```
- [ ] Add 7-day forecast mini-chart for each constraint
- [ ] Use mock data initially (Person A delivers real data Day 5)

**Tasks Day 7:**
- [ ] Create correlation chart:
      ```typescript
      // Show: "When soil moisture > 0.4, production drops 18%"
      // Scatter plot or annotated line chart
      ```
- [ ] Add satellite image thumbnail:
      - Last acquisition date
      - Cloud cover percentage
      - Click to view full resolution (optional)
- [ ] Integrate with enhanced forecast API
- [ ] Update ForecastPanel.tsx to show all 4 drivers (not just rainfall)
- [ ] Test with real data

**Evening Commit Day 7:**
```
feat(ui): Add EO constraints dashboard panel

- Create 4-gauge visualization for satellite inputs
- Add 7-day constraint forecast
- Show constraint-production correlation
- Integrate with enhanced forecast model
```

---

### Day 8-9: EAR Explainer Component (THE CENTERPIECE)

**Branch:** `feature/ear-explainer`

**Tasks Day 8:**
- [ ] Create `frontend/src/components/EARExplainer.tsx`
- [ ] Build funnel visualization:
      ```typescript
      // Option 1: Use @nivo/bar for horizontal stacked bar
      // Option 2: Custom SVG funnel with d3
      // Option 3: CSS-based funnel (simplest)
      
      <div className="ear-funnel">
          <div className="funnel-stage" style={{width: '100%'}}>
              <span>Geological Reserve</span>
              <span>850,000 t (100%)</span>
          </div>
          <div className="funnel-arrow">↓ depth factor (0.85)</div>
          <div className="funnel-stage" style={{width: '85%'}}>
              <span>Depth-Adjusted</span>
              <span>722,500 t (85%)</span>
          </div>
          <div className="funnel-arrow">↓ equipment factor (0.90)</div>
          <div className="funnel-stage" style={{width: '76.5%'}}>
              <span>Equipment-Adjusted</span>
              <span>650,250 t (76%)</span>
          </div>
          {/* ... continue for climate and infra factors */}
          <div className="funnel-final">
              <span>Effective Accessible Reserve</span>
              <span className="ear-highlight">463,303 t (54%)</span>
          </div>
      </div>
      ```

**Tasks Day 9:**
- [ ] Add interactive what-if sliders:
      ```typescript
      const [lhdCount, setLhdCount] = useState(3);
      const [monsoonDays, setMonsoonDays] = useState(90);
      const [haulDistance, setHaulDistance] = useState(2.5);
      
      // Debounced API call on slider change
      const debouncedRecalculate = useMemo(
          () => debounce(async (scenario) => {
              const res = await api.post(`/api/mines/${mineId}/ear/what-if`, scenario);
              setEarBreakdown(res.data);
          }, 500),
          [mineId]
      );
      
      useEffect(() => {
          debouncedRecalculate({
              equipment: {LHD: lhdCount},
              weather: {monsoon_days: monsoonDays},
              haul_road_distance_km: haulDistance
          });
      }, [lhdCount, monsoonDays, haulDistance]);
      ```
- [ ] Add "blocks at risk" table (blocks with lowest accessibility)
- [ ] Integrate with real API (Person A delivers Day 7)
- [ ] Polish animations (funnel stages cascade in)
- [ ] Add tooltips explaining each factor

**Evening Commit Day 9:**
```
feat(ui): Add interactive EAR explainer with what-if scenarios

- Create funnel visualization showing factor cascade
- Implement what-if sliders for equipment, weather, infrastructure
- Add real-time EAR recalculation with debouncing
- Polish animations and add explanatory tooltips
```

**This is your demo centerpiece. Make it beautiful.**

---

### Day 10: Integration, Testing, Polish

**Branch:** `feature/integration-polish`

**Tasks Morning:**
- [ ] Merge all feature branches to `develop`
- [ ] Resolve any conflicts with Person A's work
- [ ] Test full app end-to-end:
      - All APIs return real data (not mocks)
      - All new panels load without errors
      - All interactive features work (sliders, clicks, zooms)
- [ ] Fix any integration bugs

**Tasks Afternoon:**
- [ ] Create new dashboard layout integrating all panels:
      ```typescript
      // Update Dashboard.tsx
      <div className="dashboard">
          <Tabs>
              <Tab label="Overview">
                  <KpiCards />
                  <MapView />
                  <ProductionChart />
              </Tab>
              <Tab label="Reserve Prospectivity">
                  <ProspectivityMap />
                  <ProspectivityPanel />
              </Tab>
              <Tab label="Production Forecast">
                  <EOConstraintsPanel />
                  <ForecastPanel />
                  <ActionsPanel />
              </Tab>
              <Tab label="EAR Analysis">
                  <ReservePanel />
                  <EARExplainer />
              </Tab>
          </Tabs>
      </div>
      ```
- [ ] Polish UI:
      - Consistent spacing and colors
      - Loading skeletons everywhere
      - Empty states with helpful messages
      - Mobile responsive (at least portrait phone)
- [ ] Update `frontend/README.md` with new features

**Testing Checklist:**
- [ ] All tabs load without console errors
- [ ] All sliders work and update in < 2 seconds
- [ ] Map layers toggle correctly
- [ ] Data refreshes on page reload
- [ ] Works in Chrome, Firefox, Safari

**Evening:** Feature-complete MVP ready for demo prep

---

## Merge Strategy

### Branch Flow:
```
Day 1-9: Both work on separate feature/* branches
Day 10: Merge all to develop
Day 11: Test develop thoroughly
Day 12: Merge develop → main (tag as v1.0.0-mvp)
```

### How to Avoid Conflicts:

**Person A (Backend) Never Touches:**
- `frontend/` folder (except API type definitions)
- `README.md` "Features" section (Person B owns)

**Person B (Frontend) Never Touches:**
- `backend/` folder (except reading API docs)
- `ml/` folder
- `scripts/` folder
- `data/` folder (except viewing for testing)

**Shared Files (Coordinate Before Editing):**
- `backend/app/main.py` — Person A coordinates router registration
- `frontend/src/api/client.ts` — Person A defines interface, Person B uses it
- `README.md` — Person A: setup, Person B: features
- `.gitignore` — Coordinate if adding new patterns

### Git Workflow:

**Creating Feature Branch:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
# Work, commit, push
git push -u origin feature/your-feature-name
```

**Daily Sync:**
```bash
# Every morning:
git checkout develop
git pull origin develop
git checkout feature/your-feature-name
git rebase develop  # Or merge develop into your branch
# Resolve conflicts if any
```

**Merging to Develop:**
```bash
# Day 10, when feature is done:
git checkout develop
git pull origin develop
git merge feature/your-feature-name
# Test thoroughly
git push origin develop
```

---

## Communication Protocol

### Morning Standup (5 min, via chat):
```
Person A:
✅ Yesterday: Finished prospectivity model training
🚀 Today: Building prospectivity API endpoints
⚠️ Blockers: None
📤 Handoff: Will push top_10_targets.geojson by EOD

Person B:
✅ Yesterday: Built prospectivity map UI with mocks
🚀 Today: Integrating real data from Person A
⚠️ Blockers: Waiting on GeoJSON file (expected today)
📤 Handoff: None
```

### API Contract Changes:
If Person A changes an API response schema, immediately notify Person B via:
1. Update `frontend/src/api/client.ts` type definitions
2. Comment in PR: "⚠️ API CHANGE: Added 'confidence' field to Target type"
3. Quick chat message

### Blockers:
If blocked waiting on other person's work:
1. Don't sit idle — work on polish, tests, or documentation
2. Use mock data to continue parallel work
3. Escalate if blocker > 4 hours

---

## Tools & Setup

### Shared Tools:
- **Git:** Branches, PRs, clear commit messages
- **GitHub/GitLab:** Project board with tasks (or Trello)
- **Chat:** WhatsApp/Telegram for quick coordination
- **Video Call:** Daily 5-min standup (or async via chat if same timezone)

### Person A Setup:
```bash
# Backend environment
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# ML libraries
pip install scikit-learn lightgbm xgboost shap
pip install rasterio geopandas shapely

# Earth observation
pip install earthengine-api sentinelhub pystac-client

# Testing
pip install pytest pytest-asyncio httpx
```

### Person B Setup:
```bash
# Frontend environment
cd frontend
npm install

# Additional UI libraries
npm install @nivo/bar  # For funnel chart
npm install recharts  # Already have, but may need update
npm install maplibre-gl  # Already have

# Testing
npm install --save-dev @testing-library/react vitest
```

---

## Testing Strategy

### Person A (Backend) Tests:
```bash
# Unit tests for ML models
pytest ml/prism/test_prospectivity.py
pytest ml/prism/test_ear.py

# API integration tests
pytest backend/tests/test_api_prospectivity.py
pytest backend/tests/test_api_ear.py

# Run all tests
pytest backend/tests/
```

### Person B (Frontend) Tests:
```bash
# Component tests
npm run test

# Manual testing checklist:
# - All panels load
# - All sliders work
# - Map interactions work
# - Mobile responsive
```

### Integration Testing (Day 10, Both):
```bash
# Start backend
cd backend
python -m uvicorn app.main:app --port 8000

# Start frontend (separate terminal)
cd frontend
npm run dev

# Test full user journey:
# 1. Dashboard loads
# 2. Switch to Prospectivity tab
# 3. Click on target → map zooms
# 4. Switch to EAR tab
# 5. Move sliders → EAR updates
# 6. Download PDF report
```

---

## Deliverables Checklist

### Person A Deliverables (End of Day 10):
- [ ] Prospectivity ML model trained and saved
- [ ] EO constraints data pipeline working
- [ ] Enhanced forecast model with 4 satellite inputs
- [ ] Dynamic EAR calculator implemented
- [ ] All API endpoints implemented and tested
- [ ] OpenAPI docs updated
- [ ] Backend tests passing
- [ ] `DATA_SOURCES.md` documenting all datasets

### Person B Deliverables (End of Day 10):
- [ ] Prospectivity map UI with heatmap and targets
- [ ] EO constraints dashboard panel
- [ ] EAR explainer with interactive sliders
- [ ] Enhanced forecast panel showing all drivers
- [ ] All components responsive and polished
- [ ] Frontend tests passing
- [ ] `FEATURES.md` documenting all UI components

### Joint Deliverables:
- [ ] Full app runs without errors
- [ ] All 3 PS requirements demonstrable
- [ ] Demo script written and rehearsed once
- [ ] README updated with setup and features

---

## Risk Mitigation

### Risk 1: Person A's data download takes too long
**Mitigation:** 
- Start downloads Day 1 morning, let run overnight
- Person B uses mock data Days 1-3 (no blocker)
- If still stuck Day 3, use smaller region or synthetic data

### Risk 2: API schema mismatch causes frontend errors
**Mitigation:**
- Person A defines TypeScript interfaces in `client.ts` immediately
- Use OpenAPI codegen to auto-generate types (optional)
- Person B tests with mock data shaped like real API

### Risk 3: Merge conflicts on Day 10
**Mitigation:**
- Daily rebases from develop
- Clear file ownership (backend vs frontend)
- Coordinate any shared file edits in advance

### Risk 4: One person falls behind schedule
**Mitigation:**
- Daily progress check (evening commit reviews)
- If Person A behind: Person B focuses on polish and animations
- If Person B behind: Person A helps with simple UI tasks or writes tests
- Adjust scope: Drop P1 tasks if needed to hit P0

### Risk 5: Feature doesn't work in integration
**Mitigation:**
- Both test with real data before Day 10
- Person A provides sample curl commands for each endpoint
- Person B tests API responses in browser console before building UI

---

## Day 11-12: Demo Preparation (Both Together)

**Branch:** `main` (feature-complete)

### Day 11 Morning: Test & Fix
- [ ] Full smoke test on fresh machine (different laptops)
- [ ] Fix any integration bugs
- [ ] Test offline mode (no internet during demo)
- [ ] Verify all endpoints return 200

### Day 11 Afternoon: Documentation
- [ ] Update main README.md
- [ ] Create ARCHITECTURE.md (diagram of system)
- [ ] Create DATA_SOURCES.md (citations for all datasets)
- [ ] Update API docs (make sure /docs is complete)

### Day 12: Demo Prep
- [ ] Write 8-slide presentation deck (divide: Person A explains backend, Person B demos UI)
- [ ] Rehearse demo 3 times (full 7 minutes)
- [ ] Record backup video (Person B drives, Person A narrates)
- [ ] Prepare answers to top 10 Q&A questions
- [ ] Test on presentation laptop, check HDMI/adapters

---

## Success Metrics

### Technical (Must Pass):
- [ ] Backend: All API endpoints return 200
- [ ] Backend: All tests pass (`pytest`)
- [ ] Frontend: No console errors on any page
- [ ] Frontend: All interactive features work
- [ ] Integration: Full user journey works end-to-end

### Demo Quality (Must Achieve):
- [ ] All 3 PS requirements demonstrable
- [ ] Interactive elements work smoothly
- [ ] Visual polish (looks professional, not hacky)
- [ ] Backup video plays without issues
- [ ] Can answer "How did you build X?" for every feature

### Timeline (Target):
- [ ] All P0 tasks done by Day 10
- [ ] Demo-ready by Day 12
- [ ] 2-day buffer before submission

---

## Final Advice

### For Person A (Backend/ML):
- **Your bottleneck:** Satellite data download. Start immediately.
- **Your superpower:** Clean API contracts enable Person B to work in parallel.
- **Your focus:** Make APIs fast (<2 sec response) and well-documented.
- **Don't do:** Frontend work (trust Person B).

### For Person B (Frontend/UI):
- **Your bottleneck:** Waiting for Person A's data. Mitigate with mocks.
- **Your superpower:** Beautiful UI sells the project.
- **Your focus:** Make the EAR explainer stunning (this wins demos).
- **Don't do:** Backend work (trust Person A).

### For Both:
- **Communicate daily.** 5 minutes of sync saves 5 hours of rework.
- **Test often.** Don't wait until Day 10 for first integration.
- **Commit frequently.** Small commits > giant merge bombs.
- **Help each other.** If one is blocked, the other assists.
- **Stay focused on P0.** Resist shiny features until MVP is done.

---

## You Got This! 🚀

**Timeline:** 10 days to MVP
**Outcome:** Complete solution addressing all 3 SIH requirements
**Differentiator:** EAR bridge (no other team will have this)
**Advantage:** Parallel work = 2x speed

**Start now. Day 1 begins with satellite downloads and mock data setup.**

Good luck! 💪
