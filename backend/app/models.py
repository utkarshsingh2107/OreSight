from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from .database import Base


class Mine(Base):
    __tablename__ = "mines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    state = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    mine_type = Column(String)  # underground / opencast
    monthly_target_tonnes = Column(Float)


class ProductionDaily(Base):
    __tablename__ = "production_daily"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), index=True)
    date = Column(Date, index=True)
    tonnes = Column(Float)
    rainfall_mm = Column(Float, nullable=True)
    equipment_downtime_hours = Column(Float, default=0.0)
    is_holiday = Column(Integer, default=0)


class EquipmentEvent(Base):
    __tablename__ = "equipment_events"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), index=True)
    asset_name = Column(String)
    event_type = Column(String)  # failure / repair_complete
    event_date = Column(Date)
    downtime_hours = Column(Float, default=0.0)


class ForecastRun(Base):
    __tablename__ = "forecast_runs"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), index=True)
    created_at = Column(DateTime, server_default=func.now())
    horizon_days = Column(Integer)
    rainfall_scenario_mm = Column(Float, nullable=True)
    p10 = Column(Float)
    p50 = Column(Float)
    p90 = Column(Float)
    shortfall_probability = Column(Float)
    drivers_json = Column(Text)  # JSON-encoded SHAP driver list


class ActionLog(Base):
    __tablename__ = "action_log"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), index=True)
    action_name = Column(String)
    expected_delta_tonnes = Column(Float)
    applied_at = Column(DateTime, server_default=func.now())
    applied_by = Column(String, default="Mine Manager (demo)")
