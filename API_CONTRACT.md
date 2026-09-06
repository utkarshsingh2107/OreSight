# OreSight — API Contract
## Backend ↔ Frontend Interface Agreement

**Purpose:** Clear agreement between Person A (Backend) and Person B (Frontend) on exact API shapes.

**Rule:** Person A defines and implements these. Person B consumes them exactly as specified.

---

## Existing APIs (Already Working)

### ✅ GET /api/mines
```json
Response: Array<{
  id: number,
  name: string,
  state: string,
  latitude: number,
  longitude: number,
  mine_type: "underground" | "opencast",
  monthly_target_tonnes: number
}>

Example:
[{
  "id": 1,
  "name": "Balaghat",
  "state": "Madhya Pradesh",
  "latitude": 21.8075,
  "longitude": 80.1889,
  "mine_type": "underground",
  "monthly_target_tonnes": 25000
}]
```

### ✅ GET /api/mines/{id}/kpi
```json
Response: {
  latest_tonnes: number,
  mtd_tonnes: number,
  monthly_target_tonnes: number,
  shortfall_probability: number  // 0-1
}
```

### ✅ POST /api/forecast
```json
Request: {
  mine_id: number,
  horizon_days: number,  // typically 30
  rainfall_override_mm?: number  // optional for what-if
}

Response: {
  mine_id: number,
  horizon_days: number,
  p10: number[],  // daily forecast, length = horizon_days
  p50: number[],
  p90: number[],
  shortfall_probability: number,
  drivers: Array<{
    name: string,
    contribution: number  // SHAP value
  }>,
  fan_chart: Array<{
    date: string,
    p10: number,
    p50: number,
    p90: number
  }>
}
```

---

## NEW APIs (Person A to Build)

### 🆕 GET /api/prospectivity/targets
**Person A:** Implement Day 8
**Person B:** Use Day 4-5

```json
Response: {
  targets: Array<{
    rank: number,        // 1-10
    id: string,          // unique identifier
    lat: number,
    lon: number,
    probability: number, // 0-1 (e.g., 0.87 = 87%)
    confidence: "low" | "medium" | "high",
    evidence: {
      iron_oxide_index: number,     // 0-1
      ndvi_anomaly: number,          // -1 to 1
      swir_ratio: number,            // 0-1
      distance_to_known_mine_km: number,
      slope_degrees: number
    }
  }>
}

Example:
{
  "targets": [{
    "rank": 1,
    "id": "target_001",
    "lat": 21.789,
    "lon": 80.234,
    "probability": 0.87,
    "confidence": "high",
    "evidence": {
      "iron_oxide_index": 0.92,
      "ndvi_anomaly": 0.15,
      "swir_ratio": 0.78,
      "distance_to_known_mine_km": 2.3,
      "slope_degrees": 12.5
    }
  }]
}
```

---

### 🆕 GET /api/prospectivity/map
**Person A:** Implement Day 8
**Person B:** Use Day 3-4 (initially with mock)

**Option 1 (Simpler):** GeoJSON
```json
Response: {
  type: "FeatureCollection",
  features: Array<{
    type: "Feature",
    geometry: {
      type: "Point",
      coordinates: [lon, lat]
    },
    properties: {
      probability: number  // 0-1
    }
  }>
}
```

**Option 2 (Better for large data):** Raster Tiles (TMS/XYZ format)
```
URL Template: /api/prospectivity/tiles/{z}/{x}/{y}.png
Returns: PNG tile with heatmap rendering
```

**Person A chooses:** Use Option 1 for MVP (simpler), Option 2 if time permits.

---

### 🆕 GET /api/prospectivity/features/{target_id}
**Person A:** Implement Day 8
**Person B:** Use Day 5 (for feature importance chart)

```json
Response: {
  target_id: string,
  feature_importance: Array<{
    feature_name: string,
    importance: number,  // 0-1, normalized
    display_name: string  // human-readable
  }>
}

Example:
{
  "target_id": "target_001",
  "feature_importance": [
    {
      "feature_name": "iron_oxide_index",
      "importance": 0.32,
      "display_name": "Iron Oxide Detection (Sentinel-2)"
    },
    {
      "feature_name": "distance_to_known_mine_km",
      "importance": 0.28,
      "display_name": "Distance to Known Mines"
    },
    {
      "feature_name": "ndvi_anomaly",
      "importance": 0.21,
      "display_name": "Vegetation Stress (NDVI)"
    }
  ]
}
```

---

### 🆕 GET /api/mines/{id}/ear/breakdown
**Person A:** Implement Day 7
**Person B:** Use Day 8-9

```json
Response: {
  geological_reserve_tonnes: number,
  factors: {
    depth_factor: number,      // 0-1
    equipment_factor: number,  // 0-1
    climate_factor: number,    // 0-1
    infra_factor: number       // 0-1
  },
  intermediate_values: {
    after_depth: number,     // tonnes
    after_equipment: number, // tonnes
    after_climate: number,   // tonnes
    after_infra: number      // tonnes (= EAR)
  },
  effective_accessible_reserve_tonnes: number,
  accessibility_percentage: number  // EAR / geological * 100
}

Example:
{
  "geological_reserve_tonnes": 850000,
  "factors": {
    "depth_factor": 0.85,
    "equipment_factor": 0.90,
    "climate_factor": 0.75,
    "infra_factor": 0.95
  },
  "intermediate_values": {
    "after_depth": 722500,
    "after_equipment": 650250,
    "after_climate": 487688,
    "after_infra": 463303
  },
  "effective_accessible_reserve_tonnes": 463303,
  "accessibility_percentage": 54.5
}
```

---

### 🆕 POST /api/mines/{id}/ear/what-if
**Person A:** Implement Day 7
**Person B:** Use Day 9 (for interactive sliders)

```json
Request: {
  equipment?: {
    LHD?: number,     // number of Load-Haul-Dump vehicles
    dumper?: number   // number of dumpers
  },
  weather?: {
    monsoon_days?: number  // expected monsoon days (60-120)
  },
  infrastructure?: {
    haul_road_distance_km?: number  // 0.5-5
  }
}

Response: {
  // Same as GET /ear/breakdown
  // Recalculated with new scenario parameters
}

Example Request:
{
  "equipment": {
    "LHD": 4  // Add one more LHD (was 3)
  },
  "weather": {
    "monsoon_days": 100  // Heavier monsoon (was 90)
  }
}

Example Response:
{
  "geological_reserve_tonnes": 850000,
  "factors": {
    "depth_factor": 0.85,
    "equipment_factor": 0.95,  // Increased due to more LHDs
    "climate_factor": 0.70,    // Decreased due to heavier monsoon
    "infra_factor": 0.95
  },
  "effective_accessible_reserve_tonnes": 478912,
  "accessibility_percentage": 56.3
}
```

**Important for Person B:** Debounce slider changes (500ms) before calling this API.

---

### 🆕 GET /api/eo-constraints/{mine_id}
**Person A:** Implement Day 5
**Person B:** Use Day 6-7

```json
Response: {
  mine_id: number,
  date_range: {
    start: string,  // ISO date
    end: string
  },
  constraints: Array<{
    date: string,  // ISO date
    rainfall_mm: number,
    soil_moisture: number,     // 0-1
    temperature_max_c: number,
    ndvi: number               // -1 to 1
  }>,
  current: {
    // Latest values for gauges
    rainfall_mm: number,
    soil_moisture: number,
    temperature_max_c: number,
    ndvi: number
  },
  forecast_7d: {
    // 7-day forecast for each constraint
    dates: string[],  // 7 dates
    rainfall_mm: number[],
    soil_moisture: number[],
    temperature_max_c: number[],
    ndvi: number[]
  }
}

Example:
{
  "mine_id": 1,
  "date_range": {
    "start": "2023-01-01",
    "end": "2024-12-31"
  },
  "constraints": [
    {
      "date": "2024-01-15",
      "rainfall_mm": 2.3,
      "soil_moisture": 0.35,
      "temperature_max_c": 28.5,
      "ndvi": 0.42
    }
    // ... ~700 more daily records
  ],
  "current": {
    "rainfall_mm": 5.2,
    "soil_moisture": 0.41,
    "temperature_max_c": 32.1,
    "ndvi": 0.38
  },
  "forecast_7d": {
    "dates": ["2024-12-20", "2024-12-21", ...],
    "rainfall_mm": [2.0, 0.5, 0.0, 1.2, 3.5, 2.8, 1.0],
    "soil_moisture": [0.39, 0.38, 0.37, 0.38, 0.41, 0.42, 0.40],
    "temperature_max_c": [31.0, 32.5, 33.0, 31.5, 30.0, 29.5, 30.5],
    "ndvi": [0.38, 0.38, 0.38, 0.37, 0.37, 0.37, 0.36]
  }
}
```

---

## Enhanced Existing API: POST /api/forecast (Updated Day 5)

**Person A:** Modify Day 5 to return 4 drivers instead of 2
**Person B:** Update Day 7 to display all 4

```json
Response: {
  // ... existing fields ...
  drivers: Array<{
    name: string,
    contribution: number,  // SHAP value
    category: "weather" | "equipment" | "operational"  // NEW
  }>
}

Example:
{
  "drivers": [
    {
      "name": "Soil Moisture",
      "contribution": 0.32,
      "category": "weather"
    },
    {
      "name": "Temperature (LST)",
      "contribution": 0.28,
      "category": "weather"
    },
    {
      "name": "Equipment Downtime",
      "contribution": 0.24,
      "category": "equipment"
    },
    {
      "name": "Rainfall",
      "contribution": 0.16,
      "category": "weather"
    }
  ]
}
```

---

## TypeScript Type Definitions (Person B to Create)

**File:** `frontend/src/api/client.ts`

```typescript
// Prospectivity Types
export interface ProspectivityTarget {
  rank: number;
  id: string;
  lat: number;
  lon: number;
  probability: number;
  confidence: "low" | "medium" | "high";
  evidence: {
    iron_oxide_index: number;
    ndvi_anomaly: number;
    swir_ratio: number;
    distance_to_known_mine_km: number;
    slope_degrees: number;
  };
}

export interface ProspectivityTargetsResponse {
  targets: ProspectivityTarget[];
}

export interface FeatureImportance {
  feature_name: string;
  importance: number;
  display_name: string;
}

export interface FeatureImportanceResponse {
  target_id: string;
  feature_importance: FeatureImportance[];
}

// EAR Types
export interface EARBreakdown {
  geological_reserve_tonnes: number;
  factors: {
    depth_factor: number;
    equipment_factor: number;
    climate_factor: number;
    infra_factor: number;
  };
  intermediate_values: {
    after_depth: number;
    after_equipment: number;
    after_climate: number;
    after_infra: number;
  };
  effective_accessible_reserve_tonnes: number;
  accessibility_percentage: number;
}

export interface EARWhatIfRequest {
  equipment?: {
    LHD?: number;
    dumper?: number;
  };
  weather?: {
    monsoon_days?: number;
  };
  infrastructure?: {
    haul_road_distance_km?: number;
  };
}

// EO Constraints Types
export interface EOConstraint {
  date: string;
  rainfall_mm: number;
  soil_moisture: number;
  temperature_max_c: number;
  ndvi: number;
}

export interface EOConstraintsResponse {
  mine_id: number;
  date_range: {
    start: string;
    end: string;
  };
  constraints: EOConstraint[];
  current: Omit<EOConstraint, 'date'>;
  forecast_7d: {
    dates: string[];
    rainfall_mm: number[];
    soil_moisture: number[];
    temperature_max_c: number[];
    ndvi: number[];
  };
}

// Enhanced Forecast (update existing)
export interface Driver {
  name: string;
  contribution: number;
  category: "weather" | "equipment" | "operational";
}

export interface Forecast {
  mine_id: number;
  horizon_days: number;
  p10: number[];
  p50: number[];
  p90: number[];
  shortfall_probability: number;
  drivers: Driver[];  // Enhanced
  fan_chart: Array<{
    date: string;
    p10: number;
    p50: number;
    p90: number;
  }>;
}
```

---

## API Client Functions (Person B to Implement)

**File:** `frontend/src/api/client.ts`

```typescript
// Prospectivity
export async function getProspectivityTargets(limit: number = 10): Promise<ProspectivityTargetsResponse> {
  const res = await api.get(`/api/prospectivity/targets?limit=${limit}`);
  return res.data;
}

export async function getTargetFeatures(targetId: string): Promise<FeatureImportanceResponse> {
  const res = await api.get(`/api/prospectivity/features/${targetId}`);
  return res.data;
}

// EAR
export async function getEARBreakdown(mineId: number): Promise<EARBreakdown> {
  const res = await api.get(`/api/mines/${mineId}/ear/breakdown`);
  return res.data;
}

export async function calculateEARWhatIf(
  mineId: number,
  scenario: EARWhatIfRequest
): Promise<EARBreakdown> {
  const res = await api.post(`/api/mines/${mineId}/ear/what-if`, scenario);
  return res.data;
}

// EO Constraints
export async function getEOConstraints(mineId: number): Promise<EOConstraintsResponse> {
  const res = await api.get(`/api/eo-constraints/${mineId}`);
  return res.data;
}
```

---

## Error Responses (Standard for All APIs)

```json
// 404 Not Found
{
  "detail": "Mine not found"
}

// 400 Bad Request
{
  "detail": "Invalid mine_id"
}

// 500 Internal Server Error
{
  "detail": "Forecast model training failed"
}
```

**Person A:** Always return structured JSON errors, never raw exceptions.
**Person B:** Handle errors gracefully with user-friendly messages.

---

## API Versioning (Future-Proofing)

All APIs use `/api/` prefix. No version number for MVP.

If breaking changes needed later:
- Add `/api/v2/` endpoints
- Keep `/api/` (v1) working for backward compatibility

---

## Performance Requirements

**Person A must ensure:**
- GET requests return in < 1 second
- POST /forecast returns in < 3 seconds (first call may train model)
- POST /ear/what-if returns in < 2 seconds
- All responses cached where appropriate

**Person B must ensure:**
- Show loading states for all API calls
- Debounce slider changes (500ms) before API calls
- Cache responses in React state when possible

---

## Testing Contract

### Person A's Responsibility:
```bash
# Provide curl examples for each endpoint
curl http://localhost:8000/api/prospectivity/targets

# Provide Postman collection (optional)

# Document in OpenAPI (/docs)
```

### Person B's Responsibility:
```typescript
// Test with mock data first
const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true';

if (USE_MOCKS) {
  return mockData;
}

// Switch to real API once Person A confirms endpoint is ready
```

---

## Handoff Schedule

| Day | Person A Delivers | Person B Receives |
|-----|-------------------|-------------------|
| 3   | `/api/prospectivity/targets` | top_10_targets.geojson for map |
| 5   | Updated `/api/forecast` with 4 drivers | Enhanced forecast response |
| 7   | `/api/mines/{id}/ear/breakdown` + `/what-if` | EAR API contract + examples |
| 9   | All APIs stable, OpenAPI docs complete | Full API documentation |

**Communication:** Person A messages Person B immediately when an API is ready for integration.

---

## Conflict Resolution

**If API shape disagrees with this contract:**
1. Person A and Person B discuss via call (5 min)
2. Agree on change
3. Update this document
4. Both commit to changed contract

**Don't:** Person A silently changes API, breaking Person B's code.
**Don't:** Person B requests arbitrary changes to APIs.

**Do:** Respect the contract. Changes require mutual agreement.

---

## Final Notes

**Person A:** Your APIs are the foundation. Make them:
- Fast (< 2 sec)
- Stable (don't change without notice)
- Well-documented (OpenAPI /docs)

**Person B:** Your UI brings APIs to life. Make it:
- Responsive (loading states, errors)
- Efficient (debounce, cache)
- Beautiful (this is what judges see)

**Both:** This contract is your agreement. Respect it, and you'll avoid 90% of integration bugs.

---

## Quick Reference Checklist

### Person A (Backend) Checklist:
```
□ Implement endpoint exactly as specified
□ Test with curl, verify JSON matches contract
□ Add to OpenAPI docs (/docs)
□ Message Person B when ready
□ Provide example request/response
```

### Person B (Frontend) Checklist:
```
□ Create TypeScript types matching contract
□ Implement API client function
□ Test with mock data first
□ Switch to real API once Person A confirms
□ Add error handling and loading states
```

---

**This contract is your north star. Follow it, and integration will be smooth. 🚀**
