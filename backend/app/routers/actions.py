from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter()

# NOTE (H0-1 placeholder): static candidate actions with hand-estimated
# Δtonnes. Replaced by a proper greedy-ranking function in the H15-17 block.
CANDIDATE_ACTIONS = [
    {
        "name": "Add an extra evening shift at Face 3",
        "expected_delta_tonnes": 180.0,
        "rationale": "Face 3 has spare accessible reserve and idle crew capacity in the evening slot.",
    },
    {
        "name": "Redeploy LHD-2 from Face 5 to Face 1",
        "expected_delta_tonnes": 120.0,
        "rationale": "Face 1 is currently haulage-constrained, not face-constrained.",
    },
    {
        "name": "Pre-position spares for the haul truck fleet",
        "expected_delta_tonnes": 90.0,
        "rationale": "Reduces expected downtime from the highest-risk asset this month.",
    },
]


@router.get("/mines/{mine_id}/suggest-actions", response_model=list[schemas.ActionOut])
def suggest_actions(mine_id: int):
    ranked = sorted(CANDIDATE_ACTIONS, key=lambda a: a["expected_delta_tonnes"], reverse=True)
    return [schemas.ActionOut(**a) for a in ranked]


@router.post("/mines/{mine_id}/apply-action", response_model=schemas.AuditLogOut)
def apply_action(mine_id: int, req: schemas.ApplyActionRequest, db: Session = Depends(get_db)):
    entry = models.ActionLog(
        mine_id=mine_id,
        action_name=req.action_name,
        expected_delta_tonnes=req.expected_delta_tonnes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/mines/{mine_id}/audit-log", response_model=list[schemas.AuditLogOut])
def audit_log(mine_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.ActionLog)
        .filter(models.ActionLog.mine_id == mine_id)
        .order_by(models.ActionLog.applied_at.desc())
        .all()
    )
