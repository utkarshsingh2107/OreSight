import json
import os
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

# Add project root to path for ml imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from ml.reserves.ear_calculator import EARCalculator, MineConfiguration
from backend.app.schemas import EARBreakdownOut, EARWhatIfRequest

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


@router.get("/mines/{mine_id}/ear/breakdown", response_model=EARBreakdownOut)
def get_ear_breakdown(mine_id: int):
    """
    Get Economically Accessible Reserve breakdown for a mine
    
    Returns baseline EAR calculation with all accessibility factors.
    Shows how geological reserve is reduced through:
    - Depth constraints
    - Equipment capacity
    - Climate impacts (monsoon)
    - Infrastructure limitations
    
    For MVP: Only mine_id=1 (Balaghat) is supported.
    """
    # Validate mine exists
    if mine_id != 1:
        raise HTTPException(
            status_code=404,
            detail=f"Mine {mine_id} not found. Only mine_id=1 (Balaghat) is supported in MVP."
        )
    
    # Load geological reserve
    if not os.path.exists(SUMMARY_PATH):
        raise HTTPException(
            status_code=404,
            detail="Reserve summary not found. Run ml/prism/blockmodel.py first."
        )
    
    with open(SUMMARY_PATH) as f:
        summary = json.load(f)
    
    geological_reserve = summary["total_geological_tonnage"]
    
    # Initialize EAR calculator
    calc = EARCalculator(geological_reserve_tonnes=geological_reserve)
    
    # Use baseline configuration
    baseline_config = MineConfiguration(
        lhd_count=3,
        dumper_count=5,
        monsoon_days_baseline=90,
        haul_road_distance_km=2.5,
        average_depth_m=150,
        max_economical_depth_m=300
    )
    
    # Calculate EAR
    result = calc.calculate(config=baseline_config)
    
    # Return API response
    return result.to_dict()


@router.post("/mines/{mine_id}/ear/what-if", response_model=EARBreakdownOut)
def calculate_ear_whatif(mine_id: int, scenario: EARWhatIfRequest):
    """
    Calculate EAR for a what-if scenario
    
    Allows Person B to test how changes to:
    - Equipment fleet (add/remove LHDs, dumpers)
    - Weather conditions (monsoon duration)
    - Infrastructure (haul road distance)
    
    ...affect the Economically Accessible Reserve.
    
    Use this for interactive sliders in UI.
    """
    # Validate mine exists
    if mine_id != 1:
        raise HTTPException(
            status_code=404,
            detail=f"Mine {mine_id} not found. Only mine_id=1 (Balaghat) is supported in MVP."
        )
    
    # Load geological reserve
    if not os.path.exists(SUMMARY_PATH):
        raise HTTPException(
            status_code=404,
            detail="Reserve summary not found. Run ml/prism/blockmodel.py first."
        )
    
    with open(SUMMARY_PATH) as f:
        summary = json.load(f)
    
    geological_reserve = summary["total_geological_tonnage"]
    
    # Initialize EAR calculator
    calc = EARCalculator(geological_reserve_tonnes=geological_reserve)
    
    # Baseline configuration
    baseline_config = MineConfiguration(
        lhd_count=3,
        dumper_count=5,
        monsoon_days_baseline=90,
        haul_road_distance_km=2.5,
        average_depth_m=150,
        max_economical_depth_m=300
    )
    
    # Convert Pydantic models to dict for what-if overrides
    whatif_overrides = {}
    
    if scenario.equipment:
        whatif_overrides["equipment"] = scenario.equipment.model_dump(exclude_none=True)
    
    if scenario.weather:
        whatif_overrides["weather"] = scenario.weather.model_dump(exclude_none=True)
    
    if scenario.infrastructure:
        whatif_overrides["infrastructure"] = scenario.infrastructure.model_dump(exclude_none=True)
    
    # Calculate EAR with what-if scenario
    result = calc.calculate(
        config=baseline_config,
        whatif_overrides=whatif_overrides
    )
    
    # Return API response
    return result.to_dict()
