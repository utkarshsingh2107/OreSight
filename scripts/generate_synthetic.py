"""
Generates a physically-calibrated synthetic daily production series for
MOIL's Balaghat mine, 2018 -> latest available rainfall date.

REAL inputs:
  - Daily rainfall at the Balaghat mine site (21.83N, 80.23E), from
    data/processed/rainfall_balaghat.csv (Open-Meteo / ERA5 reanalysis).

ASSUMED/SYNTHETIC calibration (explicitly disclosed, see docs/domain-glossary.md
and the blueprint's own illustrative figures in section 1.5):
  - Non-monsoon baseline ~22,000 tonnes/month
  - Monsoon-suppressed actual ~14,000 tonnes/month
  - No official per-mine breakdown of MOIL's published company-level totals
    is publicly available, so the mine-level absolute numbers here are a
    calibrated assumption, not a real MOIL disclosure. Company-level FY
    totals (FY24-25: 18.02 lakh t, FY25-26: 19.07 lakh t) ARE real and are
    documented in docs/domain-glossary.md.

Output: data/synthetic/production_daily_balaghat.csv,
        data/synthetic/equipment_events_balaghat.csv

Deterministic: fixed random seed for reproducibility.
"""
import csv
import os
import random
from datetime import date, datetime, timedelta

random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAINFALL_CSV = os.path.join(BASE_DIR, "data", "processed", "rainfall_balaghat.csv")
OUT_PRODUCTION = os.path.join(BASE_DIR, "data", "synthetic", "production_daily_balaghat.csv")
OUT_EQUIPMENT = os.path.join(BASE_DIR, "data", "synthetic", "equipment_events_balaghat.csv")

BASELINE_MONTHLY_TONNES = 22000.0
BASELINE_DAILY_TONNES = BASELINE_MONTHLY_TONNES / 30.0  # ~733 t/day

# Assets modelled for equipment downtime (named, so they can be cited as
# shortfall drivers later in the SHAP panel).
ASSETS = ["LHD-1", "LHD-2", "Haul Truck-3", "Winder-1", "Drill Rig-2"]


def load_rainfall():
    rows = []
    with open(RAINFALL_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = datetime.strptime(row["date"], "%Y-%m-%d").date()
            rows.append((d, float(row["rainfall_mm"])))
    return rows


def rolling_rainfall_stress(rainfall_by_date, idx, window=7):
    """7-day trailing rainfall sum — proxy for haul-road/flooding persistence."""
    start = max(0, idx - window + 1)
    window_vals = [r for _, r in rainfall_by_date[start : idx + 1]]
    return sum(window_vals)


def simulate_equipment_downtime(current_date, active_failures):
    """
    Poisson-ish random failures per asset with log-normal repair durations.
    Returns today's total downtime hours and updates active_failures in place.
    """
    total_downtime = 0.0
    events = []

    # Resolve ongoing repairs
    still_active = []
    for asset, end_date in active_failures:
        if current_date < end_date:
            still_active.append((asset, end_date))
            total_downtime += 8.0  # a day mid-repair costs a full shift-equivalent
        else:
            events.append((asset, "repair_complete", current_date, 0.0))
    active_failures[:] = still_active

    # New failures: small daily probability per asset (~ MTBF of a few months)
    for asset in ASSETS:
        if not any(a == asset for a, _ in active_failures):
            if random.random() < 0.006:  # roughly one failure per ~5-6 months per asset
                repair_days = max(1, round(random.lognormvariate(1.0, 0.6)))
                end_date = current_date + timedelta(days=repair_days)
                active_failures.append((asset, end_date))
                events.append((asset, "failure", current_date, 8.0))
                total_downtime += 8.0

    return total_downtime, events


def main():
    rainfall_by_date = load_rainfall()

    production_rows = []
    equipment_rows = []
    active_failures = []  # list of (asset, repair_end_date)

    for idx, (d, rain_mm) in enumerate(rainfall_by_date):
        # --- Weekday effect ---
        is_sunday = d.weekday() == 6  # Monday=0 ... Sunday=6
        weekday_factor = 0.55 if is_sunday else 1.0

        # --- Monsoon suppression via real rainfall (7-day trailing stress) ---
        stress = rolling_rainfall_stress(rainfall_by_date, idx, window=7)
        # Calibrated so ~150mm/week trailing rain suppresses output toward the
        # ~14,000 t/month monsoon baseline (a ~36% cut from the 22,000 baseline).
        rain_factor = max(0.55, 1 - 0.0024 * stress)

        # --- Fiscal Q4 push (Jan-Mar): mild positive pressure toward year-end targets ---
        fiscal_push = 1.05 if d.month in (1, 2, 3) else 1.0

        # --- Equipment downtime ---
        downtime_hours, events = simulate_equipment_downtime(d, active_failures)
        for asset, event_type, event_date, dt_hours in events:
            equipment_rows.append(
                {
                    "asset_name": asset,
                    "event_type": event_type,
                    "event_date": event_date.isoformat(),
                    "downtime_hours": dt_hours,
                }
            )
        downtime_factor = max(0.5, 1 - downtime_hours / 24.0)

        # --- Random day-to-day noise ---
        noise = random.gauss(1.0, 0.06)

        tonnes = (
            BASELINE_DAILY_TONNES
            * weekday_factor
            * rain_factor
            * fiscal_push
            * downtime_factor
            * noise
        )
        tonnes = max(0.0, round(tonnes, 1))

        production_rows.append(
            {
                "date": d.isoformat(),
                "tonnes": tonnes,
                "rainfall_mm": rain_mm,
                "equipment_downtime_hours": round(downtime_hours, 1),
                "is_holiday": 1 if is_sunday else 0,
            }
        )

    os.makedirs(os.path.dirname(OUT_PRODUCTION), exist_ok=True)
    with open(OUT_PRODUCTION, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["date", "tonnes", "rainfall_mm", "equipment_downtime_hours", "is_holiday"]
        )
        writer.writeheader()
        writer.writerows(production_rows)

    with open(OUT_EQUIPMENT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["asset_name", "event_type", "event_date", "downtime_hours"])
        writer.writeheader()
        writer.writerows(equipment_rows)

    total_tonnes = sum(r["tonnes"] for r in production_rows)
    years = (rainfall_by_date[-1][0] - rainfall_by_date[0][0]).days / 365.25
    print(f"Generated {len(production_rows)} days of production -> {OUT_PRODUCTION}")
    print(f"Generated {len(equipment_rows)} equipment events -> {OUT_EQUIPMENT}")
    print(f"Average annual tonnage over the series: {total_tonnes / years:,.0f} t/year")


if __name__ == "__main__":
    main()