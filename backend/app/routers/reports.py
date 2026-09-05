from fastapi import APIRouter, HTTPException

router = APIRouter()

# NOTE (H0-1 placeholder): built out in the H23-26 block (ReportLab PDF).


@router.get("/mines/{mine_id}/report.pdf")
def get_report(mine_id: int):
    raise HTTPException(status_code=501, detail="Report generation not implemented yet (see H23-26 block)")
