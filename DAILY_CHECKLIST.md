# OreSight — Daily Checklist
## Quick Reference for Both Team Members

---

## 🎯 Your Mission

**Goal:** Build MVP in 10 days covering all 3 SIH requirements
**Strategy:** You (Backend/ML) + Friend (Frontend/UI) work in parallel
**Handshake:** APIs are the contract between you

---

## 📋 Person A (Backend/ML) — Daily Tasks

### ☀️ Morning Routine (5 min)
```bash
□ Pull latest: git checkout develop && git pull
□ Check friend's progress (read their commit messages)
□ Post standup update in chat (what I'm doing today)
□ Start work on your branch
```

---

### 📅 Day 1: Satellite Data Download
**Branch:** `feature/prospectivity-ml`

```bash
□ Set up Earth Engine or Sentinel Hub account
□ Create scripts/fetch_satellite_data.py
□ Download Sentinel-2 for Balaghat (Bands: B2,B3,B4,B8,B11,B12)
□ Download DEM (SRTM or Cartosat)
□ Download GSI geology from NGDR
□ Save to data/satellite/ and data/geology/
□ Document sources in DATA_SOURCES.md
□ HANDOFF: Share moil_mines.geojson with friend
```

**EOD Commit:**
```bash
git add data/ scripts/fetch_satellite_data.py DATA_SOURCES.md
git commit -m "feat(data): Add satellite data collection pipeline"
git push origin feature/prospectivity-ml
```

**Evening Check:** Friend can see mine locations on map? ✓

---

### 📅 Day 2: Feature Engineering
**Branch:** `feature/prospectivity-ml`

```bash
□ Create ml/prism/features.py
□ Calculate: NDVI, iron_oxide_ratio, SWIR_ratio, clay_index
□ Extract DEM derivatives: slope, aspect, curvature
□ Calculate distance features (to mines, to lineaments)
□ Create training labels (positive/negative samples)
□ Save: data/processed/prospectivity_features.parquet
□ Test: parquet file loads, has ~20 columns, no NaN
```

**EOD Commit:**
```bash
git commit -m "feat(ml): Add prospectivity feature engineering"
git push origin feature/prospectivity-ml
```

---

### 📅 Day 3: Train Prospectivity Model
**Branch:** `feature/prospectivity-ml`

```bash
□ Create ml/prism/prospectivity.py
□ Implement spatial cross-validation (GroupKFold)
□ Train Random Forest (n_estimators=200, class_weight='balanced')
□ Generate probability map (TIF raster)
□ Rank top 10 targets (cluster nearby cells)
□ Save: models/prospectivity_rf.pkl
□ Save: data/processed/top_10_targets.geojson
□ Save: reports/prospectivity_metrics.json (AUC, precision)
□ Test: AUC-ROC > 0.70 (acceptable) or > 0.75 (good)
□ HANDOFF: Share top_10_targets.geojson with friend (they need it Day 4)
```

**EOD Commit:**
```bash
git commit -m "feat(ml): Train prospectivity model (AUC: 0.78)"
git push origin feature/prospectivity-ml
```

---

### 📅 Day 4: EO Constraints Pipeline
**Branch:** `feature/eo-constraints`

```bash
□ Create ml/earth_observation/constraints.py
□ Implement get_soil_moisture() - SMAP or Sentinel-1
□ Implement get_land_surface_temperature() - MODIS LST
□ Implement get_ndvi() - Sentinel-2
□ Download for Balaghat, 2018-2024
□ Save: data/eo_constraints/balaghat_constraints.csv
□ Columns: date, rainfall_mm, soil_moisture, temperature_max, ndvi
□ Test: ~2000 rows, no NaN values
```

**EOD Commit:**
```bash
git commit -m "feat(eo): Add multi-source satellite constraint pipeline"
git push origin feature/eo-constraints
```

---

### 📅 Day 5: Enhanced Forecast Model
**Branch:** `feature/eo-constraints`

```bash
□ Modify ml/pulse/forecast.py
□ Merge constraints CSV into forecast dataframe
□ Add lag features: lag_7_soil_moisture, lag_7_temperature
□ Add rolling features: rolling_30_ndvi
□ Retrain LightGBM with expanded features
□ Update SHAP driver calculation
□ Save: reports/forecast_metrics_v2.json
□ Test: MAE same or better, SHAP includes new features
□ HANDOFF: Tell friend API schema updated (4 drivers now)
```

**EOD Commit:**
```bash
git commit -m "feat(forecast): Add soil moisture, LST, NDVI features"
git push origin feature/eo-constraints
```

---

### 📅 Day 6: EAR Calculator (Part 1)
**Branch:** `feature/dynamic-ear`

```bash
□ Create ml/prism/ear.py
□ Implement compute_dynamic_ear() function
□ Calculate accessibility factors:
  - f_depth = exp(-(depth - current) / 500)
  - f_equip = available / required
  - f_climate = 1 - (0.3 * monsoon_risk)
  - f_infra = 1 / (1 + distance / 5)
□ Compute EAR = tonnage × f_depth × f_equip × f_climate × f_infra
□ Return factor breakdown dict
□ Write unit tests for each factor
```

**EOD Commit:**
```bash
git commit -m "feat(ear): Implement EAR calculation with factors"
git push origin feature/dynamic-ear
```

---

### 📅 Day 7: EAR API Endpoints
**Branch:** `feature/dynamic-ear`

```bash
□ Create/modify backend/app/routers/reserve.py
□ Add GET /api/mines/{id}/ear/breakdown
□ Add POST /api/mines/{id}/ear/what-if
□ Create Pydantic schemas for request/response
□ Test with curl/Postman
□ Document in OpenAPI (/docs)
□ HANDOFF: Share API docs + example JSON with friend
```

**EOD Commit:**
```bash
git commit -m "feat(api): Add EAR endpoints with what-if scenarios"
git push origin feature/dynamic-ear
```

---

### 📅 Day 8: Prospectivity APIs
**Branch:** `feature/api-endpoints`

```bash
□ Create backend/app/routers/prospectivity.py
□ Add GET /api/prospectivity/map (return GeoJSON)
□ Add GET /api/prospectivity/targets
□ Add GET /api/prospectivity/features/{id}
□ Convert raster to web format (GeoJSON or COG)
□ Add response caching
□ Test all endpoints with curl
```

**EOD Commit:**
```bash
git commit -m "feat(api): Add prospectivity endpoints"
git push origin feature/api-endpoints
```

---

### 📅 Day 9: Final API Integration
**Branch:** `feature/api-endpoints`

```bash
□ Register all routers in main.py
□ Update schemas.py with all new types
□ Generate OpenAPI docs (verify /docs complete)
□ Write integration tests
□ Update requirements.txt
□ HANDOFF: Full API documentation to friend
```

**EOD Commit:**
```bash
git commit -m "feat(api): Register all new routers and update docs"
git push origin feature/api-endpoints
```

---

### 📅 Day 10: Integration & Testing
**Branch:** Merge to `develop`

```bash
□ Merge all feature branches to develop
□ Resolve conflicts (coordinate with friend)
□ Run backend test suite (pytest)
□ Test all APIs with curl (all return 200)
□ Update backend/README.md
□ Seed database with all new data
□ Ready for friend's frontend integration
```

**EOD:** Backend complete, APIs stable ✓

---

## 🎨 Person B (Frontend/UI) — Daily Tasks

### ☀️ Morning Routine (5 min)
```bash
□ Pull latest: git checkout develop && git pull
□ Check friend's progress (any API changes?)
□ Post standup update in chat
□ Start work on your branch
```

---

### 📅 Day 1-2: Mock Data Setup
**Branch:** `feature/base-ui-improvements`

```bash
□ Create frontend/src/mocks/prospectivity.mock.ts
□ Create mockProspectivityTargets (10 targets)
□ Create mockEARBreakdown (factor structure)
□ Update api/client.ts with mock toggle
□ Set VITE_USE_MOCKS=true in .env
□ Enhance dashboard layout (tabs or sections)
□ Polish existing components (loading states, errors)
□ Test mobile responsiveness
```

**EOD Commit Day 2:**
```bash
git commit -m "feat(ui): Add mock data for parallel development"
git push origin feature/base-ui-improvements
```

---

### 📅 Day 3-4: Prospectivity Map UI
**Branch:** `feature/prospectivity-ui`

**Day 3:**
```bash
□ Create components/ProspectivityMap.tsx
□ Add heatmap layer to existing MapView
□ Add layer toggle controls
□ Add probability legend
□ Use mock GeoJSON initially
```

**Day 4:**
```bash
□ Create components/ProspectivityPanel.tsx
□ Build target list (cards with rank, coords, probability)
□ Add click → zoom to target on map
□ Add target markers with popups
□ Style with Tailwind
□ WAIT for friend's top_10_targets.geojson (EOD Day 3)
□ Switch from mock to real data
```

**EOD Commit Day 4:**
```bash
git commit -m "feat(ui): Add prospectivity map and target list"
git push origin feature/prospectivity-ui
```

---

### 📅 Day 5: Prospectivity Polish
**Branch:** `feature/prospectivity-ui`

```bash
□ Replace all mocks with real API calls
□ Create FeatureImportanceChart.tsx (horizontal bars)
□ Add loading states and error handling
□ Add "Export KML" button
□ Test with real data from friend
□ Polish animations
```

**EOD Commit:**
```bash
git commit -m "feat(ui): Integrate real prospectivity data"
git push origin feature/prospectivity-ui
```

---

### 📅 Day 6-7: EO Constraints Panel
**Branch:** `feature/eo-constraints-ui`

**Day 6:**
```bash
□ Create components/EOConstraintsPanel.tsx
□ Build 4 circular gauges:
  - Rainfall
  - Soil Moisture
  - Temperature
  - Vegetation (NDVI)
□ Add 7-day forecast mini-chart for each
□ Use mock data initially
```

**Day 7:**
```bash
□ Create correlation chart
  ("When soil moisture > 0.4, production drops 18%")
□ Add satellite image thumbnail
□ Integrate with enhanced forecast API
□ Update ForecastPanel.tsx to show all 4 drivers
□ Test with real data from friend
```

**EOD Commit Day 7:**
```bash
git commit -m "feat(ui): Add EO constraints dashboard panel"
git push origin feature/eo-constraints-ui
```

---

### 📅 Day 8-9: EAR Explainer (THE STAR)
**Branch:** `feature/ear-explainer`

**Day 8:**
```bash
□ Create components/EARExplainer.tsx
□ Build funnel visualization:
  Geological (100%) → Depth (85%) → Equipment (76%) → 
  Climate (57%) → Infra (54%) → EAR
□ Use @nivo/bar or custom CSS funnel
□ Add tooltips explaining each factor
```

**Day 9:**
```bash
□ Add what-if sliders:
  - Number of LHDs (1-10)
  - Monsoon severity (60-120 days)
  - Haul road distance (0.5-5 km)
□ Implement debounced API call (500ms)
□ Real-time EAR recalculation on slider change
□ Add "Blocks at Risk" table
□ Polish animations (funnel cascade effect)
□ Test with real API from friend
```

**EOD Commit Day 9:**
```bash
git commit -m "feat(ui): Add interactive EAR explainer"
git push origin feature/ear-explainer
```

**This component MUST be stunning. This wins the demo.**

---

### 📅 Day 10: Integration & Polish
**Branch:** `feature/integration-polish`

```bash
□ Merge all feature branches to develop
□ Resolve conflicts with friend
□ Test full app end-to-end
□ Create new dashboard layout with tabs:
  - Overview (existing KPIs, map, chart)
  - Reserve Prospectivity (map + targets)
  - Production Forecast (EO + forecast + actions)
  - EAR Analysis (reserve + explainer)
□ Polish UI consistency
□ Add loading skeletons everywhere
□ Test mobile portrait mode
□ Update frontend/README.md
```

**EOD:** Frontend complete, all features working ✓

---

## 🤝 Daily Coordination (Both)

### Every Morning (5 min):
```
Person A posts:
✅ Yesterday: [what I finished]
🚀 Today: [what I'm building]
📤 Handoff: [what friend will receive, when]
⚠️ Blockers: [anything blocking me]

Person B posts:
✅ Yesterday: [what I finished]
🚀 Today: [what I'm building]
📥 Waiting: [what I need from friend]
⚠️ Blockers: [anything blocking me]
```

### API Changes (Person A → Person B):
```
If you change an API response:
1. Update frontend/src/api/client.ts types
2. Comment in commit: "⚠️ API CHANGE: [description]"
3. Message friend immediately
```

### Handoffs (Critical Sync Points):
```
Day 3 EOD: Person A → top_10_targets.geojson → Person B
Day 5 EOD: Person A → Updated forecast schema → Person B
Day 7 EOD: Person A → EAR API docs + examples → Person B
Day 9 EOD: Person A → All APIs stable → Person B
```

---

## 🔄 Git Workflow (Both)

### Daily:
```bash
# Morning
git checkout develop
git pull origin develop
git checkout -b feature/your-feature  # Or your existing branch
git rebase develop  # Bring in latest changes

# Evening
git add .
git commit -m "feat: descriptive message"
git push origin feature/your-feature
```

### Day 10 Merge:
```bash
# Person A first (backend stable = foundation)
git checkout develop
git pull origin develop
git merge feature/api-endpoints
# Test thoroughly
git push origin develop

# Person B second (after Person A pushed)
git checkout develop
git pull origin develop  # Get Person A's changes
git merge feature/integration-polish
# Resolve any conflicts
git push origin develop
```

---

## ✅ Daily Success Criteria

### Person A (Backend/ML):
```
Day 1: ✓ Data downloaded, documented
Day 2: ✓ Features extracted, parquet file verified
Day 3: ✓ Model trained, AUC > 0.70, GeoJSON shared
Day 4: ✓ EO constraints CSV generated, no NaN
Day 5: ✓ Forecast enhanced, SHAP shows new features
Day 6: ✓ EAR calculator working, unit tests pass
Day 7: ✓ EAR APIs implemented, tested with curl
Day 8: ✓ Prospectivity APIs working, cached responses
Day 9: ✓ All routers registered, OpenAPI docs complete
Day 10: ✓ All APIs return 200, backend tests pass
```

### Person B (Frontend/UI):
```
Day 2: ✓ Mock data setup, layout prepared
Day 4: ✓ Prospectivity map + targets working with mocks
Day 5: ✓ Real data integrated, no console errors
Day 7: ✓ EO constraints panel complete, all 4 gauges
Day 9: ✓ EAR explainer working, sliders update EAR
Day 10: ✓ All tabs load, no errors, mobile responsive
```

---

## 🚨 Troubleshooting

### "I'm blocked waiting on the other person"
→ **Person A:** Work on tests, documentation, or next feature
→ **Person B:** Use mock data, work on polish/animations

### "Merge conflict!"
→ **Prevention:** Daily rebase from develop
→ **Resolution:** Coordinate via call, resolve together

### "API doesn't match what I expected"
→ **Person A:** Check OpenAPI docs, share curl example
→ **Person B:** Check browser console, share error message

### "Feature taking longer than planned"
→ **Both:** Communicate immediately, adjust scope if needed
→ **Priority:** P0 tasks must finish, drop P1 if needed

---

## 📊 Progress Tracking

### Use This Daily:
```
Day 1:  [▓▓░░░░░░░░] 20%
Day 2:  [▓▓▓░░░░░░░] 30%
Day 3:  [▓▓▓▓░░░░░░] 40%
Day 4:  [▓▓▓▓▓░░░░░] 50%
Day 5:  [▓▓▓▓▓▓░░░░] 60%
Day 6:  [▓▓▓▓▓▓▓░░░] 70%
Day 7:  [▓▓▓▓▓▓▓▓░░] 80%
Day 8:  [▓▓▓▓▓▓▓▓▓░] 90%
Day 9:  [▓▓▓▓▓▓▓▓▓▓] 95%
Day 10: [▓▓▓▓▓▓▓▓▓▓] 100% MVP COMPLETE
```

### Health Check (End of Each Day):
```
□ On track (completed today's tasks)
□ At risk (some tasks incomplete, but recoverable)
□ Blocked (need help or scope adjustment)
```

---

## 🎯 Day 10 Integration Checklist (Both Together)

### Morning (Both):
```bash
□ Pull latest develop
□ Merge your feature branches
□ Resolve conflicts together (call if needed)
□ Start backend server
□ Start frontend server
```

### Testing (Both):
```bash
□ Dashboard loads without errors
□ All tabs accessible
□ Prospectivity: Click target → map zooms ✓
□ EO Constraints: All 4 gauges show data ✓
□ Forecast: SHAP shows all 4 drivers ✓
□ EAR: Sliders update in <2 sec ✓
□ Actions: Suggest → Apply → Audit log ✓
□ PDF report downloads ✓
```

### If Something Breaks:
```
1. Check browser console (frontend error)
2. Check terminal logs (backend error)
3. Check API response in Network tab
4. Fix together, don't blame
```

### When All Tests Pass:
```bash
git checkout main
git merge develop
git tag v1.0.0-mvp
git push origin main --tags
```

**🎉 MVP COMPLETE! Time for demo prep.**

---

## 🎬 Day 11-12: Demo Prep (Both)

### Day 11:
```
Morning:
□ Test on different laptop (fresh install)
□ Fix any bugs found
□ Test offline mode (no internet = no excuses)

Afternoon:
□ Update README.md (both contribute)
□ Write ARCHITECTURE.md (Person A leads)
□ Create DATA_SOURCES.md (Person A)
□ Add FEATURES.md (Person B)
```

### Day 12:
```
Morning:
□ Create 8-slide presentation:
  - Slides 1-2: Problem + Solution (Person A writes)
  - Slides 3-5: Demo walkthrough (Person B scripts)
  - Slides 6-7: Results + Impact (Both)
  - Slide 8: Thank you + Q&A (Both)

Afternoon:
□ Rehearse demo 3 times (switch who drives)
□ Record backup video (Person B drives, Person A narrates)
□ Write answers to top 10 Q&A questions (Both)
□ Test HDMI adapter, charge laptops
```

---

## 🏆 Success = MVP in 10 Days

**You have:**
✓ All 3 SIH requirements covered
✓ Multi-source satellite integration
✓ Unique EAR differentiator
✓ Professional, working prototype

**You are ready to:**
✓ Demo confidently
✓ Answer technical questions
✓ Win or place high

---

## 💪 Final Tips

**Person A:** Your clean APIs are the foundation. Make them fast, stable, documented.

**Person B:** Your UI tells the story. Make the EAR explainer unforgettable.

**Both:** 
- Communicate daily (5 min standup)
- Test often (don't wait for Day 10)
- Trust each other (stay in your lanes)
- Help when blocked (teamwork wins)

**Start NOW. Day 1 begins today.**

**You got this! 🚀**
