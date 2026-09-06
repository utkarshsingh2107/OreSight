import os
import sys
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd

from ..database import get_db
from .. import models, schemas

SIH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if SIH_ROOT not in sys.path:
    sys.path.insert(0, SIH_ROOT)

from ml.pulse import forecast as pulse_forecast  # noqa: E402

logger = logging.getLogger(__name__)
router = APIRouter()

# ---------------------------------------------------------------------------
# EO constraints CSV path (relative to the repository root)
# ---------------------------------------------------------------------------
_EO_CONSTRAINTS_DIR = Path(SIH_ROOT) / "data" / "eo_constraints"

# Mine-ID → EO constraints CSV filename mapping.
# Extend this dict when more mines are added.
_EO_CSV_MAP: dict[int, str] = {
    1: "balaghat_constraints.csv",
}


def _load_eo_constraints(mine_id: int) -> pd.DataFrame | None:
    """
    Load the Earth-Observation constraints CSV for a given mine and return it
    as a DataFrame indexed on 'date' (datetime).

    Columns expected by pulse_forecast._engineer_features():
        soil_moisture, soil_moisture_7d_avg, temperature_max_c,
        temperature_7d_avg, ndvi

    The CSV on disk contains:
        date, soil_moisture, temperature_max_c, ndvi, rainfall_mm

    This function derives the rolling averages so that the forecast feature
    engineering has real values instead of the neutral fall-back defaults.

    Returns None (with a warning) if the file is missing or cannot be parsed,
    so the router degrades gracefully to the existing behaviour.
    """
    fname = _EO_CSV_MAP.get(mine_id)
    if fname is None:
        return None

    csv_path = _EO_CONSTRAINTS_DIR / fname
    if not csv_path.exists():
        logger.warning(
            "EO constraints file not found for mine %d: %s", mine_id, csv_path
        )
        return None

    try:
        eo = pd.read_csv(csv_path, parse_dates=["date"])
        eo = eo.sort_values("date").reset_index(drop=True)

        # Derive 7-day rolling averages that the forecast feature engineering uses
        eo["soil_moisture_7d_avg"] = (
            eo["soil_moisture"].rolling(7, min_periods=1).mean()
        )
        eo["temperature_7d_avg"] = (
            eo["temperature_max_c"].rolling(7, min_periods=1).mean()
        )

        eo = eo.set_index("date")
        return eo

    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to load EO constraints for mine %d: %s", mine_id, exc)
        return None


def _merge_eo_into_history(
    history_df: pd.DataFrame,
    eo_df: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Left-join the EO constraint columns onto history_df on the 'date' column.

    Only the columns that the forecast feature engineering actually uses are
    joined.  Any dates in history_df that are absent from eo_df are left as
    NaN; pulse_forecast._engineer_features() already has neutral fall-backs
    for missing EO columns so no further action is needed here.
    """
    if eo_df is None:
        return history_df

    eo_cols = [
        "soil_moisture",
        "soil_moisture_7d_avg",
        "temperature_max_c",
        "temperature_7d_avg",
        "ndvi",
    ]
    # Only keep EO columns that exist in the loaded CSV
    eo_cols = [c for c in eo_cols if c in eo_df.columns]

    if not eo_cols:
        return history_df

    eo_subset = eo_df[eo_cols].reset_index()  # brings 'date' back as a column

    # Normalise types before merging
    history_df = history_df.copy()
    history_df["date"] = pd.to_datetime(history_df["date"])
    eo_subset["date"]  = pd.to_datetime(eo_subset["date"])

    merged = history_df.merge(eo_subset, on="date", how="left")
    return merged


# ---------------------------------------------------------------------------
# Forecast endpoint
# ---------------------------------------------------------------------------

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

    # Build the core production history DataFrame
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

    # Join EO constraint columns (soil_moisture, temperature_max_c, ndvi, …)
    # so that pulse_forecast._engineer_features() uses real satellite-derived
    # values instead of the neutral fall-back defaults it applies when those
    # columns are absent from history_df.
    eo_df = _load_eo_constraints(req.mine_id)
    df    = _merge_eo_into_history(df, eo_df)

    if eo_df is not None:
        eo_cols_present = [
            c for c in ("soil_moisture", "temperature_max_c", "ndvi")
            if c in df.columns and df[c].notna().any()
        ]
        logger.info(
            "EO constraints joined for mine %d: %s", req.mine_id, eo_cols_present
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
