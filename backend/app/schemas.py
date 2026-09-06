from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class MineOut(BaseModel):
    id: int
    name: str
    state: str
    latitude: float
    longitude: float
    mine_type: str
    monthly_target_tonnes: float

    class Config:
        from_attributes = True


class ProductionPoint(BaseModel):
    date: date
    tonnes: float
    rainfall_mm: Optional[float] = None
    equipment_downtime_hours: float = 0.0

    class Config:
        from_attributes = True


class KpiOut(BaseModel):
    mine_name: str
    latest_date: date
    latest_tonnes: float
    mtd_actual_tonnes: float
    monthly_target_tonnes: float
    shortfall_probability: Optional[float] = None


class ForecastRequest(BaseModel):
    mine_id: int
    horizon_days: int = 30
    rainfall_override_mm: Optional[float] = None


class DriverOut(BaseModel):
    name: str
    impact: float
    direction: str  # "increases risk" / "decreases risk"


class ForecastOut(BaseModel):
    mine_id: int
    horizon_days: int
    p10: float
    p50: float
    p90: float
    shortfall_probability: float
    drivers: list[DriverOut]
    fan_chart: list[dict]


class ActionOut(BaseModel):
    name: str
    expected_delta_tonnes: float
    rationale: str


class ApplyActionRequest(BaseModel):
    mine_id: int
    action_name: str
    expected_delta_tonnes: float


class AuditLogOut(BaseModel):
    id: int
    action_name: str
    expected_delta_tonnes: float
    applied_at: datetime
    applied_by: str

    class Config:
        from_attributes = True


# ============================================================================
# Prospectivity Schemas
# ============================================================================

class EvidenceOut(BaseModel):
    """Evidence supporting a prospectivity target"""
    iron_oxide_index: float
    ndvi_anomaly: float
    distance_to_known_mine_km: float


class ProspectivityTargetOut(BaseModel):
    """Exploration target from prospectivity model"""
    rank: int
    id: str
    lat: float
    lon: float
    probability: float
    confidence: str  # "low" | "medium" | "high"
    nearest_mine: Optional[str] = None
    distance_to_mine_km: Optional[float] = None
    evidence: EvidenceOut


class ProspectivityTargetsResponse(BaseModel):
    """Response with list of exploration targets"""
    targets: list[ProspectivityTargetOut]


class FeatureImportanceOut(BaseModel):
    """Feature importance for target or global model"""
    feature_name: str
    importance: float
    display_name: str


class FeatureImportanceResponse(BaseModel):
    """Response with feature importance list"""
    target_id: Optional[str] = None
    feature_importance: list[FeatureImportanceOut]
