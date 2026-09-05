"""
Seeds backend/oresight.db with:
  - Balaghat mine metadata (real coordinates, real facts — see sources below)
  - The synthetic-but-calibrated production_daily series
  - The synthetic equipment_events series

Run this after generate_synthetic.py. Safe to re-run: it wipes and reloads
Balaghat's data only (idempotent for demo-reset purposes).

Sources for real Balaghat metadata:
  - Coordinates (21°50'N, 80°14'E) and depth/century-old operation:
    MOIL Balaghat Mine Subsidence Report (forestsclearance.nic.in)
  - "Largest and deepest underground manganese mine in Asia", underground
    method: moil.nic.in "About MOIL" and Wikipedia "MOIL"
"""
import csv
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.database import Base, engine, SessionLocal  # noqa: E402
from app import models  # noqa: E402

PRODUCTION_CSV = os.path.join(BASE_DIR, "data", "synthetic", "production_daily_balaghat.csv")
EQUIPMENT_CSV = os.path.join(BASE_DIR, "data", "synthetic", "equipment_events_balaghat.csv")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Wipe existing Balaghat data for idempotent re-seeding (demo-reset)
        existing = db.query(models.Mine).filter(models.Mine.name == "Balaghat").first()
        if existing:
            db.query(models.ProductionDaily).filter(models.ProductionDaily.mine_id == existing.id).delete()
            db.query(models.EquipmentEvent).filter(models.EquipmentEvent.mine_id == existing.id).delete()
            db.query(models.ActionLog).filter(models.ActionLog.mine_id == existing.id).delete()
            db.delete(existing)
            db.commit()

        mine = models.Mine(
            name="Balaghat",
            state="Madhya Pradesh",
            latitude=21.83,
            longitude=80.23,
            mine_type="underground",
            monthly_target_tonnes=19500.0,
        )
        db.add(mine)
        db.commit()
        db.refresh(mine)

        with open(PRODUCTION_CSV, "r") as f:
            reader = csv.DictReader(f)
            batch = []
            for row in reader:
                batch.append(
                    models.ProductionDaily(
                        mine_id=mine.id,
                        date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
                        tonnes=float(row["tonnes"]),
                        rainfall_mm=float(row["rainfall_mm"]),
                        equipment_downtime_hours=float(row["equipment_downtime_hours"]),
                        is_holiday=int(row["is_holiday"]),
                    )
                )
            db.bulk_save_objects(batch)
            db.commit()
            print(f"Seeded {len(batch)} production_daily rows for Balaghat")

        with open(EQUIPMENT_CSV, "r") as f:
            reader = csv.DictReader(f)
            batch = []
            for row in reader:
                batch.append(
                    models.EquipmentEvent(
                        mine_id=mine.id,
                        asset_name=row["asset_name"],
                        event_type=row["event_type"],
                        event_date=datetime.strptime(row["event_date"], "%Y-%m-%d").date(),
                        downtime_hours=float(row["downtime_hours"]),
                    )
                )
            db.bulk_save_objects(batch)
            db.commit()
            print(f"Seeded {len(batch)} equipment_events rows for Balaghat")

        print(f"Mine seeded: id={mine.id}, name={mine.name}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
