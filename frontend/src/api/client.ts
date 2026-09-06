import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
});

export interface Mine {
  id: number;
  name: string;
  state: string;
  latitude: number;
  longitude: number;
  mine_type: string;
  monthly_target_tonnes: number;
}

export interface ProductionPoint {
  date: string;
  tonnes: number;
  rainfall_mm: number | null;
  equipment_downtime_hours: number;
}

export interface Kpi {
  mine_name: string;
  latest_date: string;
  latest_tonnes: number;
  mtd_actual_tonnes: number;
  monthly_target_tonnes: number;
  shortfall_probability: number | null;
}

export interface Driver {
  name: string;
  impact: number;
  direction: string;
}

export interface FanPoint {
  day: number;
  p10: number;
  p50: number;
  p90: number;
}

export interface Forecast {
  mine_id: number;
  horizon_days: number;
  p10: number;
  p50: number;
  p90: number;
  shortfall_probability: number;
  drivers: Driver[];
  fan_chart: FanPoint[];
}

export interface Action {
  name: string;
  expected_delta_tonnes: number;
  rationale: string;
}

export interface AuditEntry {
  id: number;
  action_name: string;
  expected_delta_tonnes: number;
  applied_at: string;
  applied_by: string;
}

export const getMines = () => api.get<Mine[]>("/mines").then((r) => r.data);

export const getMine = (id: number) =>
  api.get<Mine>(`/mines/${id}`).then((r) => r.data);

export const getKpi = (id: number) =>
  api.get<Kpi>(`/mines/${id}/kpi`).then((r) => r.data);

export const getProduction = (id: number, days = 365) =>
  api
    .get<ProductionPoint[]>(`/mines/${id}/production`, { params: { days } })
    .then((r) => r.data);

export const getForecast = (
  mineId: number,
  horizonDays = 30,
  rainfallOverrideMm?: number,
) =>
  api
    .post<Forecast>("/forecast", {
      mine_id: mineId,
      horizon_days: horizonDays,
      rainfall_override_mm: rainfallOverrideMm,
    })
    .then((r) => r.data);

export const getSuggestedActions = (mineId: number) =>
  api
    .get<Action[]>(`/mines/${mineId}/suggest-actions`)
    .then((r) => r.data);

export const applyAction = (
  mineId: number,
  action: { name: string; expected_delta_tonnes: number },
) =>
  api
    .post<AuditEntry>(`/mines/${mineId}/apply-action`, {
      mine_id: mineId,
      action_name: action.name,
      expected_delta_tonnes: action.expected_delta_tonnes,
    })
    .then((r) => r.data);

export const getAuditLog = (mineId: number) =>
  api.get<AuditEntry[]>(`/mines/${mineId}/audit-log`).then((r) => r.data);

// New endpoints for enhanced features

export interface ProspectTarget {
  rank: number;
  name: string;
  latitude: number;
  longitude: number;
  prospectivity_score: number;
  confidence: number;
  evidence: {
    spectral_indices: number;
    distance_to_known_mine: number;
    lineament_proximity: number;
    vegetation_stress: number;
  };
}

export interface ProspectivityData {
  total_prospects: number;
  targets: ProspectTarget[];
  heatmap_url: string;
}

export const getProspectivity = (mineId: number) =>
  api.get<ProspectivityData>(`/prospectivity/targets`, { params: { mine_id: mineId } }).then((r) => r.data);

export interface EARData {
  geological_reserve_tonnes: number;
  depth_factor: number;
  equipment_factor: number;
  climate_factor: number;
  regulatory_factor: number;
  infrastructure_factor: number;
  total_ear_tonnes: number;
  blocks_at_risk: number;
  risk_description: string;
}

export const getEAR = (mineId: number) =>
  api.get<EARData>(`/ear`, { params: { mine_id: mineId } }).then((r) => r.data);

export interface ConstraintData {
  date: string;
  rainfall_constraint: number;
  soil_moisture_constraint: number;
  temperature_constraint: number;
  vegetation_constraint: number;
}

export interface ConstraintForecast {
  current: ConstraintData;
  forecast_7day: ConstraintData[];
  historical_correlation: {
    rainfall: number;
    soil_moisture: number;
    temperature: number;
  };
}

export const getEOConstraints = (mineId: number) =>
  api.get<ConstraintForecast>(`/eo-constraints`, { params: { mine_id: mineId } }).then((r) => r.data);

export interface ModelMetrics {
  model_name: string;
  mae: number;
  rmse: number;
  r_squared: number;
  mape: number;
  confidence_interval_95: {
    lower: number;
    upper: number;
  };
  test_sample_size: number;
  sensitivity_analysis: {
    parameter: string;
    impact_percentage: number;
  }[];
}

export interface ValidationData {
  forecast_model: ModelMetrics;
  prospectivity_model: ModelMetrics;
  sensitivity_chart_data: {
    parameter: string;
    value: number;
  }[];
  reconciliation_status: string;
}

export const getValidationMetrics = (mineId: number) =>
  api.get<ValidationData>(`/validation-metrics`, { params: { mine_id: mineId } }).then((r) => r.data);
