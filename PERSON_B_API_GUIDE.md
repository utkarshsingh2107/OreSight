# Person B API Integration Guide

**🎉 All APIs Ready for Integration!**

Person A has completed all backend implementation. This guide provides everything Person B needs to integrate the OreSight APIs into the frontend.

---

## 📦 What's Ready

### ✅ Completed Deliverables

| Day | Deliverable | Status | Files |
|-----|-------------|--------|-------|
| 1-3 | Satellite Data + Prospectivity ML | ✅ Complete | `moil_mines.geojson`, `top_10_targets.geojson` |
| 4-5 | EO Constraints + Enhanced Forecast | ✅ Complete | EO data pipeline, 17-feature forecast model |
| 6-7 | Dynamic EAR Calculator + APIs | ✅ Complete | `/ear/breakdown`, `/ear/what-if` endpoints |
| 8-9 | Prospectivity APIs | ✅ Complete | `/prospectivity/targets`, `/prospectivity/features` |
| 10 | Integration + Documentation | ✅ Complete | All routers registered, this guide |

---

## 🚀 Quick Start

### 1. Start the Backend Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Server will be available at: `http://localhost:8000`

### 2. View API Documentation

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get all mines
curl http://localhost:8000/api/mines

# Get prospectivity targets
curl http://localhost:8000/api/prospectivity/targets

# Get EAR breakdown
curl http://localhost:8000/api/mines/1/ear/breakdown
```

---

## 📡 API Endpoints Reference

### Existing APIs (Already Working)

#### **GET /api/mines**
Returns list of all mines with basic info.

```typescript
Response: Array<{
  id: number
  name: string
  state: string
  latitude: number
  longitude: number
  mine_type: "underground" | "opencast"
  monthly_target_tonnes: number
}>
```

**Use Case**: Populate mine selector, display mines on map

---

#### **GET /api/mines/{id}/kpi**
Returns KPI metrics for dashboard cards.

```typescript
Response: {
  mine_name: string
  latest_date: string
  latest_tonnes: number
  mtd_actual_tonnes: number
  monthly_target_tonnes: number
  shortfall_probability: number  // 0-1
}
```

**Use Case**: Display KPI cards (Today's Production, MTD Progress, Shortfall Risk)

---

#### **POST /api/forecast**
Returns production forecast with uncertainty and drivers.

```typescript
Request: {
  mine_id: number
  horizon_days: number  // typically 30
  rainfall_override_mm?: number  // optional for what-if
}

Response: {
  mine_id: number
  horizon_days: number
  p10: number  // optimistic forecast
  p50: number  // median forecast
  p90: number  // pessimistic forecast
  shortfall_probability: number  // 0-1
  drivers: Array<{
    name: string
    impact: number  // 0-1, normalized
    direction: "increases risk" | "decreases risk"
    category: "weather" | "equipment" | "operational"  // NEW in Day 5
  }>
  fan_chart: Array<{
    day: number
    p10: number
    p50: number
    p90: number
  }>
}
```

**Use Case**: 
- Display forecast fan chart
- Show top drivers with categories (group by weather/equipment/operational)
- Enable rainfall what-if slider

**Enhanced in Day 5**: Added `category` field to drivers for UI grouping

---

### NEW APIs (Days 6-9)

#### **GET /api/mines/{id}/ear/breakdown**
Returns Economically Accessible Reserve calculation with factor breakdown.

```typescript
Response: {
  geological_reserve_tonnes: number
  factors: {
    depth_factor: number        // 0-1
    equipment_factor: number    // 0-1
    climate_factor: number      // 0-1
    infra_factor: number        // 0-1
  }
  intermediate_values: {
    after_depth: number
    after_equipment: number
    after_climate: number
    after_infra: number  // = EAR
  }
  effective_accessible_reserve_tonnes: number
  accessibility_percentage: number  // 0-100
}
```

**Use Case**:
- Display waterfall chart showing cascading reductions
- Show baseline EAR calculation
- Display accessibility percentage in reserve panel

**Example Response**:
```json
{
  "geological_reserve_tonnes": 22000000,
  "factors": {
    "depth_factor": 0.731,
    "equipment_factor": 1.0,
    "climate_factor": 0.75,
    "infra_factor": 0.988
  },
  "intermediate_values": {
    "after_depth": 16083289,
    "after_equipment": 16083289,
    "after_climate": 12062467,
    "after_infra": 11911686
  },
  "effective_accessible_reserve_tonnes": 11911686,
  "accessibility_percentage": 54.1
}
```

---

#### **POST /api/mines/{id}/ear/what-if**
Calculate EAR for a what-if scenario with sliders.

```typescript
Request: {
  equipment?: {
    LHD?: number        // number of Load-Haul-Dump vehicles (default: 3)
    dumper?: number     // number of dumpers (default: 5)
  }
  weather?: {
    monsoon_days?: number  // expected monsoon days (default: 90)
  }
  infrastructure?: {
    haul_road_distance_km?: number  // distance to plant (default: 2.5)
  }
}

Response: {
  // Same structure as GET /ear/breakdown
  // Recalculated with new scenario parameters
}
```

**Use Case**:
- Connect to interactive sliders in reserve panel
- Debounce slider changes (500ms) before calling API
- Show real-time impact on EAR

**Example Request**:
```json
{
  "equipment": {
    "LHD": 4  // Add one more LHD
  },
  "weather": {
    "monsoon_days": 100  // Heavier monsoon
  }
}
```

**Performance**: < 1 second response time, suitable for real-time sliders

---

#### **GET /api/prospectivity/targets?limit=10**
Returns ranked list of exploration targets.

```typescript
Response: {
  targets: Array<{
    rank: number           // 1-10
    id: string            // e.g., "target_001"
    lat: number
    lon: number
    probability: number   // 0-1 (mineralization probability)
    confidence: "low" | "medium" | "high"
    nearest_mine: string | null
    distance_to_mine_km: number | null
    evidence: {
      iron_oxide_index: number        // 0-1
      ndvi_anomaly: number            // -1 to 1
      distance_to_known_mine_km: number
    }
  }>
}
```

**Use Case**:
- Display exploration targets on map as markers/pins
- Show target details in sidebar/panel
- Color code by probability or confidence level

**Example Response**:
```json
{
  "targets": [
    {
      "rank": 1,
      "id": "target_001",
      "lat": 21.2063,
      "lon": 79.1983,
      "probability": 0.621,
      "confidence": "low",
      "nearest_mine": "Kandri Mine",
      "distance_to_mine_km": 3.47,
      "evidence": {
        "iron_oxide_index": 0.906,
        "ndvi_anomaly": -0.084,
        "distance_to_known_mine_km": 3.47
      }
    }
  ]
}
```

---

#### **GET /api/prospectivity/features/{target_id}**
Returns feature importance for a specific target (or global).

```typescript
Response: {
  target_id: string | null  // null for global importance
  feature_importance: Array<{
    feature_name: string
    importance: number  // 0-1, normalized
    display_name: string  // human-readable name
  }>
}
```

**Use Case**:
- Display feature importance bar chart
- Show which factors drive target predictions
- Educational/interpretability view

**Example Response**:
```json
{
  "target_id": "target_001",
  "feature_importance": [
    {
      "feature_name": "distance_to_mines_km",
      "importance": 0.783,
      "display_name": "Distance to Known Mines"
    },
    {
      "feature_name": "iron_oxide",
      "importance": 0.057,
      "display_name": "Iron Oxide Detection (Sentinel-2)"
    },
    {
      "feature_name": "swir",
      "importance": 0.028,
      "display_name": "SWIR Alteration Index"
    }
  ]
}
```

**Note**: For MVP, all targets return the same global feature importance. For production, could use SHAP values for target-specific interpretation.

---

#### **GET /api/prospectivity/features**
Global model feature importance (same data, no target_id required).

---

## 📂 Static Data Files

These files are ready in the `data/` directory for direct use:

### **moil_mines.geojson**
Location: `data/geology/moil_mines.geojson`

Contains 11 MOIL mine locations with properties:
- Name, type, coordinates
- Use for map markers

### **top_10_targets.geojson**
Location: `data/processed/top_10_targets.geojson`

Contains 10 exploration targets with full evidence.
- Use as fallback if API unavailable
- Or load directly for faster initial render

### **block-model-balaghat.png**
Location: `frontend/public/block-model-balaghat.png`

3D visualization of Balaghat block model.
- Use in reserve panel for visual context

---

## 🎨 UI Integration Checklist

### Dashboard Page

- [ ] **KPI Cards**
  - Call `/api/mines/1/kpi`
  - Display: Today's Production, MTD Actual, Monthly Target, Shortfall Risk
  - Update interval: Every 30 seconds

- [ ] **Production Chart**
  - Call `/api/mines/1/production` (existing endpoint)
  - Display historical production line chart

- [ ] **Map View**
  - Load `moil_mines.geojson` for mine markers
  - Load `top_10_targets.geojson` for exploration target markers
  - Or call `/api/prospectivity/targets` for live data

### Forecast Panel

- [ ] **Fan Chart**
  - Call `POST /api/forecast` with `mine_id=1, horizon_days=30`
  - Display P10/P50/P90 curves
  - Show uncertainty bands

- [ ] **Top Drivers**
  - Display `drivers` array from forecast response
  - Group by `category` (weather, equipment, operational)
  - Show impact bars and direction

- [ ] **What-If Rainfall Slider**
  - Call `POST /api/forecast` with `rainfall_override_mm` value
  - Debounce to 500ms before API call
  - Show impact on P50 forecast

### Reserve Panel

- [ ] **EAR Waterfall Chart**
  - Call `GET /api/mines/1/ear/breakdown`
  - Display cascading reduction bars:
    - Geological Reserve → After Depth → After Equipment → After Climate → After Infrastructure (EAR)
  - Show accessibility percentage

- [ ] **What-If Sliders**
  - Equipment: LHD count (1-6), Dumper count (3-8)
  - Weather: Monsoon days (60-120)
  - Infrastructure: Haul road distance (0.5-5.0 km)
  - Call `POST /api/mines/1/ear/what-if` with updated values
  - Debounce to 500ms
  - Update waterfall chart with new values

- [ ] **Block Model Image**
  - Display `/block-model-balaghat.png` from public folder

### Prospectivity Panel (Optional/Advanced)

- [ ] **Exploration Targets List**
  - Call `GET /api/prospectivity/targets?limit=10`
  - Display ranked list with probability
  - Click to zoom map to target location

- [ ] **Feature Importance Chart**
  - Call `GET /api/prospectivity/features/{target_id}`
  - Display horizontal bar chart
  - Show top 5 features

---

## 🔧 TypeScript Type Definitions

Add these to `frontend/src/api/types.ts`:

```typescript
// EAR Types
export interface AccessibilityFactors {
  depth_factor: number
  equipment_factor: number
  climate_factor: number
  infra_factor: number
}

export interface IntermediateValues {
  after_depth: number
  after_equipment: number
  after_climate: number
  after_infra: number
}

export interface EARBreakdown {
  geological_reserve_tonnes: number
  factors: AccessibilityFactors
  intermediate_values: IntermediateValues
  effective_accessible_reserve_tonnes: number
  accessibility_percentage: number
}

export interface EARWhatIfRequest {
  equipment?: {
    LHD?: number
    dumper?: number
  }
  weather?: {
    monsoon_days?: number
  }
  infrastructure?: {
    haul_road_distance_km?: number
  }
}

// Prospectivity Types
export interface Evidence {
  iron_oxide_index: number
  ndvi_anomaly: number
  distance_to_known_mine_km: number
}

export interface ProspectivityTarget {
  rank: number
  id: string
  lat: number
  lon: number
  probability: number
  confidence: "low" | "medium" | "high"
  nearest_mine: string | null
  distance_to_mine_km: number | null
  evidence: Evidence
}

export interface ProspectivityTargetsResponse {
  targets: ProspectivityTarget[]
}

export interface FeatureImportance {
  feature_name: string
  importance: number
  display_name: string
}

export interface FeatureImportanceResponse {
  target_id: string | null
  feature_importance: FeatureImportance[]
}

// Enhanced Forecast (updated)
export interface Driver {
  name: string
  impact: number
  direction: "increases risk" | "decreases risk"
  category: "weather" | "equipment" | "operational"  // NEW
}
```

---

## 🛠️ API Client Functions

Add these to `frontend/src/api/client.ts`:

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// EAR APIs
export async function getEARBreakdown(mineId: number): Promise<EARBreakdown> {
  const res = await api.get(`/mines/${mineId}/ear/breakdown`)
  return res.data
}

export async function calculateEARWhatIf(
  mineId: number,
  scenario: EARWhatIfRequest
): Promise<EARBreakdown> {
  const res = await api.post(`/mines/${mineId}/ear/what-if`, scenario)
  return res.data
}

// Prospectivity APIs
export async function getProspectivityTargets(
  limit: number = 10
): Promise<ProspectivityTargetsResponse> {
  const res = await api.get(`/prospectivity/targets?limit=${limit}`)
  return res.data
}

export async function getTargetFeatures(
  targetId: string
): Promise<FeatureImportanceResponse> {
  const res = await api.get(`/prospectivity/features/${targetId}`)
  return res.data
}

export async function getGlobalFeatures(): Promise<FeatureImportanceResponse> {
  const res = await api.get(`/prospectivity/features`)
  return res.data
}
```

---

## 📊 Data Summary

### Geological Reserve Data
- **Total Geological Reserve**: 22,000,000 tonnes
- **Baseline EAR**: 11,911,686 tonnes (54.1% accessibility)
- **Factors**: Depth (0.731), Equipment (1.0), Climate (0.75), Infrastructure (0.988)

### Prospectivity Targets
- **Total Targets**: 10 exploration sites
- **Top Target**: Rank 1, 62.1% probability, near Kandri Mine (3.5 km)
- **Probability Range**: 42% - 62.1%
- **Confidence**: Low, Medium levels

### Forecast Model
- **Features**: 17 total (12 original + 5 satellite)
- **Satellite Inputs**: Soil moisture, Temperature (LST), NDVI
- **Top Drivers**: Rainfall (weather), Equipment downtime, Production trends
- **Model Type**: LightGBM quantile regression (P10/P50/P90)

---

## ⚡ Performance Guidelines

### API Response Times
- **GET endpoints**: < 1 second
- **POST /forecast**: < 3 seconds (first call may train model)
- **POST /ear/what-if**: < 1 second (suitable for sliders)

### Frontend Optimization
- **Debounce sliders**: 500ms delay before API calls
- **Cache responses**: Store in React state when possible
- **Loading states**: Always show loading indicators for API calls
- **Error handling**: Display user-friendly messages on failures

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check Python environment
python --version  # Should be 3.10+

# Install dependencies
cd backend
pip install -r requirements.txt

# Run migrations (if needed)
python scripts/seed.py
```

### API Returns 404
- Ensure server is running on port 8000
- Check API prefix: `/api/` is required
- Verify route is registered in `main.py`

### API Returns 500
- Check server logs in terminal
- Ensure data files exist:
  - `data/processed/top_10_targets.geojson`
  - `data/processed/reserve_summary_balaghat.json`
  - `reports/prospectivity_metrics.json`

### CORS Errors
- Backend allows all origins in development
- Check browser console for actual error
- Ensure `CORSMiddleware` is configured in `main.py`

---

## 📞 Communication Template

### When API is Ready
```
Hey Person B! 👋

[API Name] is now ready for integration:
- Endpoint: [URL]
- Method: [GET/POST]
- Purpose: [What it does]
- Test it: curl http://localhost:8000/api/[endpoint]

Let me know if you need any adjustments!
```

### When You Hit a Blocker
```
Hi Person A! 🚧

I'm trying to integrate [API Name] but getting [issue].

Expected: [what you expected]
Actual: [what's happening]
Error: [error message if any]

Can you take a look?
```

---

## 🎉 Final Checklist

### Person A (Backend) - ✅ ALL COMPLETE

- [x] Satellite data pipeline working
- [x] Prospectivity ML model trained (AUC 0.936)
- [x] EO constraints data generated (2557 records)
- [x] Enhanced forecast model (17 features)
- [x] Dynamic EAR calculator implemented
- [x] EAR API endpoints created
- [x] Prospectivity API endpoints created
- [x] All routers registered in `main.py`
- [x] API documentation complete
- [x] Test scripts working
- [x] All feature branches merged to develop

### Person B (Frontend) - TODO

- [ ] Review this API guide
- [ ] Set up API client with TypeScript types
- [ ] Integrate KPI cards with `/api/mines/{id}/kpi`
- [ ] Build forecast panel with fan chart and drivers
- [ ] Build reserve panel with EAR waterfall chart
- [ ] Implement what-if sliders for forecast and EAR
- [ ] Add exploration targets to map
- [ ] (Optional) Feature importance chart
- [ ] Test all integrations end-to-end
- [ ] Prepare for demo day! 🚀

---

## 🚀 You're All Set!

Person A has delivered:
- **4 new API endpoints** (EAR breakdown, EAR what-if, Prospectivity targets, Feature importance)
- **Enhanced forecast API** with 4 satellite inputs and driver categories
- **Complete data pipeline** from satellite imagery to ML predictions
- **Comprehensive documentation** in this guide

**Next Steps**:
1. Start backend: `uvicorn backend.app.main:app --reload`
2. Test endpoints: `curl http://localhost:8000/api/prospectivity/targets`
3. View docs: http://localhost:8000/docs
4. Integrate into React app using API client functions above

**Questions?** Check the API docs at `/docs`, review test scripts in `scripts/`, or refer to `API_CONTRACT.md`.

---

**Good luck with the integration, Person B! 🎨✨**

_From Person A with ❤️_
