"""
Live Weather Router
GET /api/mines/{mine_id}/live-weather

Fetches real-time weather data from Open-Meteo (free, no API key) for the
mine's exact coordinates. Returns rainfall, temperature, soil moisture, and
wind speed — the 4 satellite/space-tech inputs mentioned in the SIH PS.

Data source: Open-Meteo API (ERA5 reanalysis + ECMWF forecast)
Latency: ~300ms first call, then cached for 60 minutes.
"""

import json
import time
import urllib.request
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends

from backend.app.database import SessionLocal
from backend.app import models

router = APIRouter()

# Simple in-process cache: {mine_id: (timestamp, data)}
_cache: dict[int, tuple[float, dict]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class LiveWeatherResponse(BaseModel):
    mine_id: int
    mine_name: str
    latitude: float
    longitude: float
    date: str
    rainfall_mm: float
    temperature_max_c: float
    soil_moisture_m3m3: float
    wind_speed_kmh: float
    # 7-day trailing averages
    rainfall_7d_avg_mm: float
    temperature_7d_avg_c: float
    source: str
    cached: bool
    fetched_at: str


def fetch_open_meteo(lat: float, lon: float) -> dict:
    """Call Open-Meteo ERA5 API for last 7 days of weather at given coordinates."""
    today = date.today().isoformat()
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=precipitation_sum,temperature_2m_max,soil_moisture_0_to_10cm_mean,wind_speed_10m_max"
        f"&past_days=7"
        f"&forecast_days=1"
        f"&timezone=Asia%2FKolkata"
    )
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Open-Meteo unavailable: {e}")


@router.get("/mines/{mine_id}/live-weather", response_model=LiveWeatherResponse)
def get_live_weather(mine_id: int, db: Session = Depends(get_db)):
    """
    Get live weather conditions at a mine's coordinates from Open-Meteo.

    Uses ERA5 reanalysis for rainfall, temperature, soil moisture, and wind speed.
    Data is cached for 1 hour to avoid rate limiting.
    """
    # Check cache
    now = time.time()
    if mine_id in _cache:
        ts, cached_data = _cache[mine_id]
        if now - ts < CACHE_TTL_SECONDS:
            cached_data["cached"] = True
            return LiveWeatherResponse(**cached_data)

    # Get mine metadata
    mine = db.query(models.Mine).filter(models.Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")

    # Fetch from Open-Meteo
    raw = fetch_open_meteo(mine.latitude, mine.longitude)

    daily = raw.get("daily", {})
    times = daily.get("time", [])
    rain_vals = [v or 0.0 for v in daily.get("precipitation_sum", [])]
    temp_vals = [v or 25.0 for v in daily.get("temperature_2m_max", [])]
    soil_vals = [v or 0.3 for v in daily.get("soil_moisture_0_to_10cm_mean", [])]
    wind_vals = [v or 10.0 for v in daily.get("wind_speed_10m_max", [])]

    # Latest available day
    latest_idx = len(times) - 1 if times else 0
    latest_date = times[latest_idx] if times else date.today().isoformat()

    rain_today = rain_vals[latest_idx] if rain_vals else 0.0
    temp_today = temp_vals[latest_idx] if temp_vals else 25.0
    soil_today = soil_vals[latest_idx] if soil_vals else 0.3
    wind_today = wind_vals[latest_idx] if wind_vals else 10.0

    # 7-day trailing averages (excluding today)
    rain_7d = sum(rain_vals[:-1]) / max(len(rain_vals) - 1, 1) if len(rain_vals) > 1 else rain_today
    temp_7d = sum(temp_vals[:-1]) / max(len(temp_vals) - 1, 1) if len(temp_vals) > 1 else temp_today

    from datetime import datetime
    fetched_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    result = {
        "mine_id": mine_id,
        "mine_name": mine.name,
        "latitude": mine.latitude,
        "longitude": mine.longitude,
        "date": latest_date,
        "rainfall_mm": round(rain_today, 1),
        "temperature_max_c": round(temp_today, 1),
        "soil_moisture_m3m3": round(soil_today, 3),
        "wind_speed_kmh": round(wind_today, 1),
        "rainfall_7d_avg_mm": round(rain_7d, 1),
        "temperature_7d_avg_c": round(temp_7d, 1),
        "source": "Open-Meteo ERA5 reanalysis (api.open-meteo.com)",
        "cached": False,
        "fetched_at": fetched_at,
    }

    # Store in cache
    _cache[mine_id] = (now, result.copy())

    return LiveWeatherResponse(**result)
