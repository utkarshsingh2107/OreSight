from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta

from ..database import get_db
from .. import models, schemas

router = APIRouter()


@router.get("/mines/{mine_id}/production", response_model=list[schemas.ProductionPoint])
def get_production(
    mine_id: int,
    days: int = Query(default=365, le=3650),
    db: Session = Depends(get_db),
):
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
        return []

    start = latest.date - timedelta(days=days)
    rows = (
        db.query(models.ProductionDaily)
        .filter(
            models.ProductionDaily.mine_id == mine_id,
            models.ProductionDaily.date >= start,
        )
        .order_by(models.ProductionDaily.date.asc())
        .all()
    )
    return rows
