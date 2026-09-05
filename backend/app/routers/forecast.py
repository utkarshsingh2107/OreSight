import os
import sys

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd

from ..database import get_db
from .. import models, schemas

SIH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if SIH_ROOT not in sys.path:
    sys.path.insert(0, SIH_ROOT)

from ml.pulse import forecast as pulse_forecast  # noqa: E402

router = APIRouter()


@router.post("/forecast", response_model=schemas.ForecastOut)
def forecast(req: schemas.ForecastRequest, db: Session = Depends(get_db)):
    mine = db.query(models.Mine).filter(models.Mine.id == req.mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")

    rows = (
        db.query(models.ProductionDaily)
        .filter(models.ProductionDaily.mine_id == req.mine_id)
        .order_by(models.ProductionDaily.date.asc())
        .all()
    )
    if len(rows) < 60:
        raise HTTPException(status_code=400, detail="Not enough production history yet")

    df = pd.DataFrame(
        [
            {
                "date": r.date,
                "tonnes": r.tonnes,
                "rainfall_mm": r.rainfall_mm or 0.0,
                "equipment_downtime_hours": r.equipment_downtime_hours or 0.0,
                "is_holiday": r.is_holiday or 0,
            }
            for r in rows
        ]
    )

    result = pulse_forecast.predict(
        mine_id=req.mine_id,
        horizon_days=req.horizon_days,
        history_df=df,
        monthly_target_tonnes=mine.monthly_target_tonnes,
        rainfall_override_mm=req.rainfall_override_mm,
    )

    return schemas.ForecastOut(
        mine_id=req.mine_id,
        horizon_days=req.horizon_days,
        p10=result["p10"],
        p50=result["p50"],
        p90=result["p90"],
        shortfall_probability=result["shortfall_probability"],
        drivers=[schemas.DriverOut(**d) for d in result["drivers"]],
        fan_chart=result["fan_chart"],
    )
