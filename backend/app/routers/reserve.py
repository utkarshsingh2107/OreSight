import json
import os

from fastapi import APIRouter, HTTPException

router = APIRouter()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "processed"))

# Solo/36h scope: single mine (Balaghat, mine_id=1). Files are precomputed by
# ml/prism/blockmodel.py rather than computed on request (see blueprint §13.1
# — heavy geostatistics should be precomputed, not run live in a demo).
CURVE_PATH = os.path.join(BASE_DIR, "grade_tonnage_balaghat.json")
SUMMARY_PATH = os.path.join(BASE_DIR, "reserve_summary_balaghat.json")


@router.get("/mines/{mine_id}/reserve")
def get_reserve(mine_id: int):
    if not os.path.exists(SUMMARY_PATH) or not os.path.exists(CURVE_PATH):
        raise HTTPException(
            status_code=404,
            detail="Reserve model not generated yet — run ml/prism/blockmodel.py",
        )
    with open(SUMMARY_PATH) as f:
        summary = json.load(f)
    with open(CURVE_PATH) as f:
        curve = json.load(f)

    return {
        **summary,
        "grade_tonnage_curve": curve,
        "block_model_image_url": "/block-model-balaghat.png",
    }
