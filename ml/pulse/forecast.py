"""
PULSE — production shortfall forecasting for a single mine.

Approach (deliberately simple for a 36h solo build, but real):
  - Build a training set by sliding a window over history: for each valid
    "as-of" day t, features are computed from data available up to and
    including t, and the target is the SUM of tonnes over the next
    `horizon_days` days (t+1 .. t+horizon_days).
  - Train three independent LightGBM quantile regressors (alpha = 0.1, 0.5,
    0.9) on that dataset -> a real P10/P50/P90 for the horizon total.
  - SHAP TreeExplainer on the P50 model gives real driver attribution for
    the current (latest) inference row.
  - Shortfall probability is estimated by fitting a Normal distribution to
    the P10/P50/P90 (P10/P90 ~= mean +/- 1.2816*sigma) and evaluating the
    CDF at the monthly (scaled) target. This is an approximation, not a
    full Monte Carlo — documented as such.
  - Models are cached in-process per mine so what-if slider moves (which
    change one feature and re-run inference only) respond in well under a
    second, not by retraining.

This intentionally trades some statistical sophistication (see blueprint
§6.3 for the full hierarchical-reconciliation design) for something a solo
build can finish, verify, and explain confidently in a demo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import lightgbm as lgb
import shap

FEATURE_COLUMNS = [
    "day_of_week",
    "month",
    "is_holiday",
    "rainfall_today",
    "rainfall_7d_sum",
    "rainfall_30d_sum",
    "equipment_downtime_hours",
    "downtime_7d_sum",
    "lag_1_tonnes",
    "lag_7_tonnes",
    "rolling_7_mean_tonnes",
    "rolling_30_mean_tonnes",
]

FRIENDLY_NAMES = {
    "day_of_week": "Day of week",
    "month": "Seasonal / fiscal cycle",
    "is_holiday": "Weekly rest day",
    "rainfall_today": "Rainfall (today)",
    "rainfall_7d_sum": "Rainfall (7-day trailing)",
    "rainfall_30d_sum": "Rainfall (30-day trailing)",
    "equipment_downtime_hours": "Equipment downtime (today)",
    "downtime_7d_sum": "Equipment downtime (7-day trailing)",
    "lag_1_tonnes": "Yesterday's output",
    "lag_7_tonnes": "Output one week ago",
    "rolling_7_mean_tonnes": "Recent production trend (7-day)",
    "rolling_30_mean_tonnes": "Recent production trend (30-day)",
}


@dataclass
class TrainedForecastModel:
    models: dict  # alpha -> lgb.Booster
    explainer: object
    feature_df: pd.DataFrame  # full engineered history (for building inference rows)
    horizon_days: int
    cache: dict = field(default_factory=dict)


_MODEL_CACHE: dict[tuple[int, int], TrainedForecastModel] = {}


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """df must be sorted by date ascending with columns: date, tonnes,
    rainfall_mm, equipment_downtime_hours, is_holiday."""
    out = df.copy().reset_index(drop=True)
    out["date"] = pd.to_datetime(out["date"])
    out["day_of_week"] = out["date"].dt.dayofweek
    out["month"] = out["date"].dt.month
    out["rainfall_today"] = out["rainfall_mm"]
    out["rainfall_7d_sum"] = out["rainfall_mm"].rolling(7, min_periods=1).sum()
    out["rainfall_30d_sum"] = out["rainfall_mm"].rolling(30, min_periods=1).sum()
    out["downtime_7d_sum"] = out["equipment_downtime_hours"].rolling(7, min_periods=1).sum()
    out["lag_1_tonnes"] = out["tonnes"].shift(1)
    out["lag_7_tonnes"] = out["tonnes"].shift(7)
    out["rolling_7_mean_tonnes"] = out["tonnes"].shift(1).rolling(7, min_periods=1).mean()
    out["rolling_30_mean_tonnes"] = out["tonnes"].shift(1).rolling(30, min_periods=1).mean()
    return out


def _build_training_set(feat_df: pd.DataFrame, horizon_days: int) -> tuple[pd.DataFrame, pd.Series]:
    n = len(feat_df)
    rows = []
    targets = []
    # need enough history for lag_30 features and enough future for the horizon target
    start_idx = 30
    end_idx = n - horizon_days
    tonnes = feat_df["tonnes"].values
    for t in range(start_idx, end_idx):
        target_sum = tonnes[t + 1 : t + 1 + horizon_days].sum()
        rows.append(feat_df.loc[t, FEATURE_COLUMNS])
        targets.append(target_sum)
    X = pd.DataFrame(rows).reset_index(drop=True)
    y = pd.Series(targets)
    return X, y


def _train_quantile_model(X: pd.DataFrame, y: pd.Series, alpha: float) -> lgb.Booster:
    train_data = lgb.Dataset(X, label=y)
    params = {
        "objective": "quantile",
        "alpha": alpha,
        "metric": "quantile",
        "learning_rate": 0.08,
        "num_leaves": 15,
        "min_data_in_leaf": 10,
        "verbose": -1,
    }
    return lgb.train(params, train_data, num_boost_round=150)


def get_or_train(mine_id: int, horizon_days: int, history_df: pd.DataFrame) -> TrainedForecastModel:
    key = (mine_id, horizon_days)
    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key]

    feat_df = _engineer_features(history_df)
    X, y = _build_training_set(feat_df, horizon_days)

    models = {
        0.1: _train_quantile_model(X, y, 0.1),
        0.5: _train_quantile_model(X, y, 0.5),
        0.9: _train_quantile_model(X, y, 0.9),
    }
    explainer = shap.TreeExplainer(models[0.5])

    trained = TrainedForecastModel(
        models=models, explainer=explainer, feature_df=feat_df, horizon_days=horizon_days
    )
    _MODEL_CACHE[key] = trained
    return trained


def _latest_inference_row(trained: TrainedForecastModel, rainfall_override_mm: float | None) -> pd.DataFrame:
    latest = trained.feature_df.iloc[[-1]][FEATURE_COLUMNS].copy()
    if rainfall_override_mm is not None:
        # Interpret the slider as a trailing-daily-average rainfall scenario.
        latest["rainfall_today"] = rainfall_override_mm
        latest["rainfall_7d_sum"] = rainfall_override_mm * 7
        latest["rainfall_30d_sum"] = rainfall_override_mm * 30
    return latest


def predict(
    mine_id: int,
    horizon_days: int,
    history_df: pd.DataFrame,
    monthly_target_tonnes: float,
    rainfall_override_mm: float | None = None,
) -> dict:
    trained = get_or_train(mine_id, horizon_days, history_df)
    row = _latest_inference_row(trained, rainfall_override_mm)

    p10 = float(trained.models[0.1].predict(row)[0])
    p50 = float(trained.models[0.5].predict(row)[0])
    p90 = float(trained.models[0.9].predict(row)[0])
    # Guard against quantile crossing on small data
    p10, p50, p90 = sorted([p10, p50, p90])

    sigma = max(1e-6, (p90 - p10) / (2 * 1.2816))
    target = monthly_target_tonnes * (horizon_days / 30.0)
    z = (target - p50) / sigma
    shortfall_probability = 0.5 * (1 + math.erf(z / math.sqrt(2)))
    shortfall_probability = min(1.0, max(0.0, shortfall_probability))

    shap_values = trained.explainer.shap_values(row)
    shap_row = shap_values[0] if shap_values.ndim == 2 else shap_values
    driver_impacts = list(zip(FEATURE_COLUMNS, shap_row))
    driver_impacts.sort(key=lambda x: abs(x[1]), reverse=True)
    max_abs = max(abs(v) for _, v in driver_impacts) or 1.0

    drivers = []
    for name, val in driver_impacts[:5]:
        drivers.append(
            {
                "name": FRIENDLY_NAMES.get(name, name),
                "impact": round(abs(val) / max_abs, 3),
                "direction": "increases risk" if val < 0 else "decreases risk",
            }
        )

    # Simple day-by-day fan chart: distribute the cumulative quantile curve
    # using the historical average daily share (smooth, not perfectly
    # calibrated per-day, but monotonic and visually honest).
    fan_chart = []
    for day in range(1, horizon_days + 1):
        frac = day / horizon_days
        fan_chart.append(
            {
                "day": day,
                "p10": round(p10 * frac, 1),
                "p50": round(p50 * frac, 1),
                "p90": round(p90 * frac, 1),
            }
        )

    return {
        "p10": p10,
        "p50": p50,
        "p90": p90,
        "shortfall_probability": shortfall_probability,
        "drivers": drivers,
        "fan_chart": fan_chart,
    }
