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
  category?: string;
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

export interface ProspectivityEvidence {
  iron_oxide_index: number;
  ndvi_anomaly: number;
  distance_to_known_mine_km: number;
}

export interface ProspectivityTarget {
  rank: number;
  id: string;
  lat: number;
  lon: number;
  probability: number;
  confidence: "high" | "medium" | "low";
  nearest_mine: string | null;
  distance_to_mine_km: number | null;
  evidence: ProspectivityEvidence;
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
  target_id: string | null;
  feature_importance: FeatureImportance[];
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

export const getProspectivityTargets = (limit = 10) =>
  api
    .get<ProspectivityTargetsResponse>("/prospectivity/targets", { params: { limit } })
    .then((r) => r.data);

export const getFeatureImportance = () =>
  api
    .get<FeatureImportanceResponse>("/prospectivity/features")
    .then((r) => r.data);

export interface LiveWeather {
  mine_id: number;
  mine_name: string;
  latitude: number;
  longitude: number;
  date: string;
  rainfall_mm: number;
  temperature_max_c: number;
  soil_moisture_m3m3: number;
  wind_speed_kmh: number;
  rainfall_7d_avg_mm: number;
  temperature_7d_avg_c: number;
  source: string;
  cached: boolean;
  fetched_at: string;
}

export const getLiveWeather = (mineId: number) =>
  api.get<LiveWeather>(`/mines/${mineId}/live-weather`).then((r) => r.data);
