# Backend Implementation Guide - Enable Frontend Features

This guide specifies the exact API endpoints and response formats needed to activate the 6 new frontend components built by Person B.

---

## 📋 Summary

Frontend has built:
- ✅ ProspectivityPanel (waiting for `/api/prospectivity/targets`)
- ✅ EARExplainer (waiting for `/api/ear`)
- ✅ EOConstraintsPanel (waiting for `/api/eo-constraints`)
- ✅ ValidationMetrics (waiting for `/api/validation-metrics`)

These components currently show "No data available" or loading states. Implementing these 4 endpoints will activate all Priority 1, 2, 4 features.

---

## 1. Prospectivity Targets Endpoint

### Route
```python
@router.get("/prospectivity/targets")
def get_prospectivity_targets(mine_id: int):
    """Get top 10 prospectivity drill targets for a mine."""
```

### Query Parameters
| Parameter | Type | Required | Example |
|-----------|------|----------|---------|
| `mine_id` | int | Yes | `1` |

### Response Format
```json
{
  "total_prospects": 10,
  "targets": [
    {
      "rank": 1,
      "name": "Target Cluster A",
      "latitude": 21.8245,
      "longitude": 79.8523,
      "prospectivity_score": 0.92,
      "confidence": 0.87,
      "evidence": {
        "spectral_indices": 0.89,
        "distance_to_known_mine": 0.95,
        "lineament_proximity": 0.88,
        "vegetation_stress": 0.81
      }
    },
    {
      "rank": 2,
      "name": "Target Cluster B",
      "latitude": 21.8156,
      "longitude": 79.8634,
      "prospectivity_score": 0.88,
      "confidence": 0.84,
      "evidence": {
        "spectral_indices": 0.85,
        "distance_to_known_mine": 0.92,
        "lineament_proximity": 0.86,
        "vegetation_stress": 0.78
      }
    },
    // ... up to 10 targets
  ],
  "heatmap_url": "/api/prospectivity/heatmap?mine_id=1"
}
```

### Response Details
- **rank**: 1-10, unique per response
- **name**: Descriptive cluster name (e.g., "Zone NE-3", "Basement High A")
- **latitude/longitude**: WGS84 coordinates
- **prospectivity_score**: 0-1 (1 = most likely to have manganese)
- **confidence**: 0-1 (model confidence in prediction)
- **evidence**: 0-1 scores for 4 evidence layers
- **heatmap_url**: URL to raster image or `/dev/null` if not available

### Implementation Notes
- Use `ml/prism/prospectivity.py` to generate scores
- Sort by `prospectivity_score` descending
- Use leave-one-mine-out validation to avoid overfitting
- Cache results for 24 hours (heavy computation)

### Example Implementation
```python
from ml.prism.prospectivity import compute_prospects

@router.get("/prospectivity/targets")
def get_prospectivity_targets(mine_id: int):
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")
    
    targets = compute_prospects(mine, top_n=10)
    
    return {
        "total_prospects": len(targets),
        "targets": targets,
        "heatmap_url": f"/api/prospectivity/heatmap?mine_id={mine_id}"
    }
```

---

## 2. EAR (Effective Accessible Reserve) Endpoint

### Route
```python
@router.get("/ear")
def get_ear(mine_id: int):
    """Get Effective Accessible Reserve with accessibility factors."""
```

### Query Parameters
| Parameter | Type | Required | Example |
|-----------|------|----------|---------|
| `mine_id` | int | Yes | `1` |

### Response Format
```json
{
  "geological_reserve_tonnes": 50000,
  "depth_factor": 0.85,
  "equipment_factor": 0.90,
  "climate_factor": 0.80,
  "regulatory_factor": 0.95,
  "infrastructure_factor": 0.88,
  "total_ear_tonnes": 28584,
  "blocks_at_risk": 12,
  "risk_description": "12 blocks in flood-prone zone during monsoon; 5 blocks below active development level"
}
```

### Factor Calculations

#### depth_factor (0.5-1.0)
```python
# Blocks below current mining elevation get discount
# Formula: 1 - (deepness_ratio ^ 1.5) where deepness_ratio = (block_depth - current_depth) / max_depth_accessible
# Range: 0.5 (very deep) to 1.0 (accessible)
```

#### equipment_factor (0.7-1.0)
```python
# Based on current equipment availability & predicted failures
# Equipment_factor = (available_equipment / total_equipment) * (1 - failure_probability)
# Default: 1.0 if no equipment downtime predicted
```

#### climate_factor (0.6-1.0)
```python
# Seasonal rainfall impact & flood zones
# During monsoon: 0.6 (heavy restrictions)
# Non-monsoon: 0.95 (minor impact)
# Permanent flood zones: 0.6 (year-round discount)
```

#### regulatory_factor (0.6-1.0)
```python
# DGMS compliance & protected areas
# Blocks in protected forest: 0.6
# Blocks near DGMS safety limit: 0.7
# Normal areas: 0.95
```

#### infrastructure_factor (0.7-1.0)
```python
# Distance to haul roads & processing plant
# < 500m: 1.0
# 500-1000m: 0.95
# 1000-2000m: 0.85
# > 2000m: 0.70
```

### Response Details
- **geological_reserve_tonnes**: From block model (static baseline)
- **[5 factors]**: Multipliers (0-1 range)
- **total_ear_tonnes**: `geological_reserve_tonnes * product(factors)`
- **blocks_at_risk**: Count of blocks with factor < 1.0
- **risk_description**: Human-readable risk summary

### Implementation Notes
- Factors are computed from:
  - Block model (depth, location)
  - Equipment CMMS logs (downtime)
  - Weather data (rainfall season)
  - GSI geology (protected areas)
  - Mine infrastructure (haul roads)
- EAR should be recalculated daily
- Cache for 24 hours

### Example Implementation
```python
from ml.prism.ear import compute_dynamic_ear

@router.get("/ear")
def get_ear(mine_id: int):
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")
    
    ear_data = compute_dynamic_ear(
        mine_id=mine_id,
        block_model=fetch_block_model(mine_id),
        equipment_logs=fetch_equipment_logs(mine_id),
        weather_forecast=fetch_weather_forecast(mine),
        geology=fetch_geology(mine)
    )
    
    return ear_data
```

---

## 3. EO Constraints Endpoint

### Route
```python
@router.get("/eo-constraints")
def get_eo_constraints(mine_id: int):
    """Get multi-source satellite operational constraints + 7-day forecast."""
```

### Query Parameters
| Parameter | Type | Required | Example |
|-----------|------|----------|---------|
| `mine_id` | int | Yes | `1` |

### Response Format
```json
{
  "current": {
    "date": "2026-09-06",
    "rainfall_constraint": 0.95,
    "soil_moisture_constraint": 0.88,
    "temperature_constraint": 0.75,
    "vegetation_constraint": 0.92
  },
  "forecast_7day": [
    {
      "date": "2026-09-07",
      "rainfall_constraint": 0.90,
      "soil_moisture_constraint": 0.85,
      "temperature_constraint": 0.78,
      "vegetation_constraint": 0.91
    },
    {
      "date": "2026-09-08",
      "rainfall_constraint": 0.85,
      "soil_moisture_constraint": 0.80,
      "temperature_constraint": 0.80,
      "vegetation_constraint": 0.90
    },
    // ... 7 days total
  ],
  "historical_correlation": {
    "rainfall": 0.68,
    "soil_moisture": 0.45,
    "temperature": 0.32
  }
}
```

### Constraint Calculations (each 0-1, higher = better)

#### rainfall_constraint
```python
# 1.0 = no rain (ideal)
# Based on Sentinel-1 VV/VH ratio or IMD rainfall forecast
# Formula: 1 - (rainfall_mm / critical_threshold)
# Critical threshold for manganese mine: ~150mm cumulative over 30 days
```

#### soil_moisture_constraint
```python
# 1.0 = dry (haul roads passable)
# Based on Sentinel-1 SAR backscatter or SMAP soil moisture
# Formula: 1 - (soil_moisture_index / saturation_threshold)
# > 80% saturation = haul roads unusable
```

#### temperature_constraint
```python
# 1.0 = cool (< 30°C)
# Based on Landsat 8 thermal bands or MODIS LST
# Formula: 1 - ((temp - 25) / 50)
# > 42°C = 15-20% equipment efficiency loss
```

#### vegetation_constraint
```python
# 1.0 = low vegetation stress (NDVI < 0.3, no geobotanical anomaly)
# Based on Sentinel-2 NDVI
# Formula: 1 - (NDVI / 0.5)
# Low NDVI = geobotanical indicator of mineralization (prospectivity)
```

### Response Details
- **current**: Latest daily values from satellite
- **forecast_7day**: 7-day outlook (7 records)
- **historical_correlation**: Pearson correlation with actual production (last 90 days)
  - Example: rainfall_correlation = 0.68 means 68% of production variance explained by rainfall

### Implementation Notes
- Pull Sentinel-1/2 data via Google Earth Engine or Copernicus Hub
- Update daily at 00:00 UTC
- Forecast from weather model (ECMWF or GFS)
- Historical correlation from regression analysis on production vs constraint data

### Example Implementation
```python
from ml.earth_observation.constraints import get_operational_constraints

@router.get("/eo-constraints")
def get_eo_constraints(mine_id: int):
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")
    
    constraints = get_operational_constraints(
        mine_location=(mine.latitude, mine.longitude),
        date_range=(date.today() - timedelta(days=1), date.today() + timedelta(days=7))
    )
    
    # Calculate historical correlation
    historical = calculate_historical_correlation(mine_id, lookback_days=90)
    
    return {
        "current": constraints["current"],
        "forecast_7day": constraints["forecast"],
        "historical_correlation": historical
    }
```

---

## 4. Validation Metrics Endpoint

### Route
```python
@router.get("/validation-metrics")
def get_validation_metrics(mine_id: int):
    """Get model performance metrics and sensitivity analysis."""
```

### Query Parameters
| Parameter | Type | Required | Example |
|-----------|------|----------|---------|
| `mine_id` | int | Yes | `1` |

### Response Format
```json
{
  "forecast_model": {
    "model_name": "LightGBM Production Forecast",
    "mae": 234.5,
    "rmse": 312.8,
    "r_squared": 0.82,
    "mape": 8.5,
    "confidence_interval_95": {
      "lower": 2750,
      "upper": 3250
    },
    "test_sample_size": 180,
    "sensitivity_analysis": [
      {"parameter": "rainfall_mm", "impact_percentage": 35.2},
      {"parameter": "equipment_downtime_hours", "impact_percentage": 28.1},
      {"parameter": "seasonal_factor", "impact_percentage": 18.5},
      {"parameter": "lagged_production_3d", "impact_percentage": 12.3},
      {"parameter": "soil_moisture", "impact_percentage": 5.8}
    ]
  },
  "prospectivity_model": {
    "model_name": "Random Forest Reserve Identification",
    "mae": 0.08,
    "rmse": 0.12,
    "r_squared": 0.78,
    "mape": 12.3,
    "confidence_interval_95": {
      "lower": 0.68,
      "upper": 0.92
    },
    "test_sample_size": 45,
    "sensitivity_analysis": [
      {"parameter": "swir_band_ratio", "impact_percentage": 31.2},
      {"parameter": "ndvi_vegetation", "impact_percentage": 22.8},
      {"parameter": "distance_to_lineament", "impact_percentage": 20.5},
      {"parameter": "distance_to_known_mine", "impact_percentage": 15.3},
      {"parameter": "sar_texture", "impact_percentage": 10.2}
    ]
  },
  "sensitivity_chart_data": [
    {"parameter": "rainfall_mm", "value": 35.2},
    {"parameter": "equipment_downtime_hours", "value": 28.1},
    {"parameter": "seasonal_factor", "value": 18.5},
    {"parameter": "lagged_production_3d", "value": 12.3},
    {"parameter": "soil_moisture", "value": 5.8}
  ],
  "reconciliation_status": "Reconciliation complete: Predicted 2,845 tonnes vs Actual 2,876 tonnes (1.1% error) for August 2026"
}
```

### Metrics Definitions

| Metric | Formula | Interpretation |
|--------|---------|-----------------|
| **MAE** | Σ\|y_actual - y_pred\| / N | Average error in same units as y |
| **RMSE** | √(Σ(y_actual - y_pred)²/N) | Penalizes larger errors more |
| **R²** | 1 - (SS_res / SS_tot) | Fraction of variance explained (0-1) |
| **MAPE** | Σ(\|y_actual - y_pred\| / y_actual) / N × 100 | Percentage error |
| **95% CI** | y_pred ± 1.96 × SE | 95% confidence interval for predictions |

### Sensitivity Analysis
- Use SHAP (SHapley Additive exPlanations) values for feature importance
- Alternative: Permutation importance (drop each feature, measure model performance drop)
- Sum of all sensitivity scores ≈ 100%
- Sorts by impact percentage descending

### Response Details
- **forecast_model**: LightGBM production model metrics
- **prospectivity_model**: Random Forest prospectivity model metrics
- **sensitivity_chart_data**: Flattened for frontend bar chart
- **reconciliation_status**: Human-readable summary of recent accuracy

### Implementation Notes
- Calculate from 20% hold-out test set
- Update weekly with recent production data
- Use k-fold cross-validation (k=5) for robustness
- Reconciliation: Compare 30-day-ago predictions vs actual results

### Example Implementation
```python
from ml.pulse.forecast import get_forecast_metrics
from ml.prism.prospectivity import get_prospectivity_metrics

@router.get("/validation-metrics")
def get_validation_metrics(mine_id: int):
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")
    
    forecast_metrics = get_forecast_metrics(mine_id)
    prospectivity_metrics = get_prospectivity_metrics(mine_id)
    
    reconciliation = compute_reconciliation(mine_id, days_ago=30)
    
    return {
        "forecast_model": forecast_metrics,
        "prospectivity_model": prospectivity_metrics,
        "sensitivity_chart_data": forecast_metrics["sensitivity_analysis"],
        "reconciliation_status": reconciliation
    }
```

---

## Integration Checklist

- [ ] Create 4 new router files in `backend/app/routers/`
- [ ] Implement data fetching from:
  - [ ] Block model database
  - [ ] Equipment CMMS logs
  - [ ] Weather data (Sentinel/IMD/ECMWF)
  - [ ] GSI geology layers
  - [ ] Production history
- [ ] Wire into `backend/app/main.py`:
  ```python
  from app.routers import prospectivity, ear, eo_constraints, validation
  
  app.include_router(prospectivity.router, prefix="/api")
  app.include_router(ear.router, prefix="/api")
  app.include_router(eo_constraints.router, prefix="/api")
  app.include_router(validation.router, prefix="/api")
  ```
- [ ] Add mock data for demo (if real data not available)
- [ ] Test all endpoints with Swagger UI: `http://localhost:8000/docs`
- [ ] Verify response formats match TypeScript interfaces
- [ ] Add error handling (404, 500, timeout)
- [ ] Add caching (Redis, 24h TTL for heavy endpoints)

---

## Testing Endpoints

### Curl Examples
```bash
# Test Prospectivity
curl "http://localhost:8000/api/prospectivity/targets?mine_id=1"

# Test EAR
curl "http://localhost:8000/api/ear?mine_id=1"

# Test EO Constraints
curl "http://localhost:8000/api/eo-constraints?mine_id=1"

# Test Validation
curl "http://localhost:8000/api/validation-metrics?mine_id=1"
```

### Python Test
```python
import requests

BASE_URL = "http://localhost:8000/api"

# All 4 endpoints
endpoints = [
    "/prospectivity/targets?mine_id=1",
    "/ear?mine_id=1",
    "/eo-constraints?mine_id=1",
    "/validation-metrics?mine_id=1"
]

for endpoint in endpoints:
    r = requests.get(f"{BASE_URL}{endpoint}")
    print(f"{endpoint}: {r.status_code}")
    print(r.json()[:200])  # First 200 chars
```

---

## Frontend Impact

Once these endpoints are live:

| Endpoint | Frontend Component | Status Change |
|----------|-------------------|---|
| `/prospectivity/targets` | ProspectivityPanel | "No data" → Shows top 10 targets |
| `/ear` | EARExplainer + KpiCards | "No data" → Shows EAR breakdown + sliders |
| `/eo-constraints` | EOConstraintsPanel | "No data" → Shows 4 constraints + 7-day chart |
| `/validation-metrics` | ValidationMetrics | "No data" → Shows model metrics + sensitivity |

---

## Priority

1. **High Priority**: `/prospectivity/targets` + `/ear` (addresses 60% of missing gaps)
2. **Medium Priority**: `/eo-constraints` (space technology demonstration)
3. **Low Priority**: `/validation-metrics` (bonus credibility feature)

Start with endpoints 1 & 2, then expand to 3 & 4.

---

## Fallback Behavior

If any endpoint is missing or returns 404:
- **ProspectivityPanel**: Shows "No prospects available yet. Run prospectivity analysis."
- **EARExplainer**: Shows "No EAR data available"
- **EOConstraintsPanel**: Shows "No constraint data available"
- **ValidationMetrics**: Shows "No validation data available"

All components include error handling and graceful degradation. **Frontend will not crash.**

---

**Date**: September 6, 2026  
**Status**: Frontend complete, awaiting backend implementation  
**Estimated Backend Effort**: 2-3 days for full implementation
