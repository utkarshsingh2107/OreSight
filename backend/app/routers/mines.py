from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter()


@router.get("/mines", response_model=list[schemas.MineOut])
def list_mines(db: Session = Depends(get_db)):
    return db.query(models.Mine).all()


@router.get("/mines/{mine_id}", response_model=schemas.MineOut)
def get_mine(mine_id: int, db: Session = Depends(get_db)):
    mine = db.query(models.Mine).filter(models.Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")
    return mine


@router.get("/mines/{mine_id}/kpi", response_model=schemas.KpiOut)
def get_kpi(mine_id: int, db: Session = Depends(get_db)):
    mine = db.query(models.Mine).filter(models.Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")

    latest = (
        db.query(models.ProductionDaily)
        .filter(models.ProductionDaily.mine_id == mine_id)
        .order_by(models.ProductionDaily.date.desc())
        .first()
    )
    if not latest:
        raise HTTPException(status_code=404, detail="No production data yet")

    month_start = latest.date.replace(day=1)
    mtd_rows = (
        db.query(models.ProductionDaily)
        .filter(
            models.ProductionDaily.mine_id == mine_id,
            models.ProductionDaily.date >= month_start,
            models.ProductionDaily.date <= latest.date,
        )
        .all()
    )
    mtd_actual = sum(r.tonnes for r in mtd_rows)

    return schemas.KpiOut(
        mine_name=mine.name,
        latest_date=latest.date,
        latest_tonnes=latest.tonnes,
        mtd_actual_tonnes=mtd_actual,
        monthly_target_tonnes=mine.monthly_target_tonnes,
        shortfall_probability=None,
    )
