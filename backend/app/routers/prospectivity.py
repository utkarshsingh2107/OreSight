"""
Prospectivity API Router

Endpoints for mineral prospectivity mapping and exploration targets:
- GET /prospectivity/targets - Return top exploration targets
- GET /prospectivity/features/{target_id} - Feature importance for a target

Author: Person A (Backend/ML)
Date: 2024
"""

import json
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas import (
    ProspectivityTargetsResponse,
    ProspectivityTargetOut,
    EvidenceOut,
    FeatureImportanceResponse,
    FeatureImportanceOut
)

router = APIRouter()

# Data file paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
TARGETS_PATH = PROJECT_ROOT / "data" / "processed" / "top_10_targets.geojson"
METRICS_PATH = PROJECT_ROOT / "reports" / "prospectivity_metrics.json"

# Feature display names for UI
FEATURE_DISPLAY_NAMES = {
    "distance_to_mines_km": "Distance to Known Mines",
    "iron_oxide": "Iron Oxide Detection (Sentinel-2)",
    "swir": "SWIR Alteration Index",
    "aspect": "Terrain Aspect",
    "slope": "Terrain Slope",
    "curvature": "Topographic Curvature",
    "clay": "Clay Mineral Detection",
    "ndvi": "Vegetation Stress (NDVI)",
    "elevation": "Elevation (DEM)",
    "distance_to_lineaments": "Distance to Geological Lineaments"
}


@router.get("/prospectivity/targets", response_model=ProspectivityTargetsResponse)
def get_prospectivity_targets(
    limit: int = Query(default=10, ge=1, le=50, description="Number of targets to return")
):
    """
    Get top exploration targets from prospectivity model
    
    Returns ranked list of potential mineralization sites based on:
    - Iron oxide spectral signature (Sentinel-2)
    - Vegetation stress (NDVI anomaly)
    - Proximity to known mines
    - Topographic features
    
    Targets are pre-computed by ml/prism/prospectivity.py
    and saved to data/processed/top_10_targets.geojson
    
    Args:
        limit: Maximum number of targets to return (1-50, default 10)
    
    Returns:
        ProspectivityTargetsResponse with ranked targets
    """
    
    # Check if targets file exists
    if not TARGETS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Prospectivity targets not generated yet. Run ml/prism/prospectivity.py first."
        )
    
    # Load GeoJSON file
    with open(TARGETS_PATH, 'r') as f:
        geojson = json.load(f)
    
    # Parse features and convert to API format
    targets = []
    
    for feature in geojson['features'][:limit]:
        props = feature['properties']
        geom = feature['geometry']
        
        # Generate unique ID from rank
        target_id = f"target_{props['rank']:03d}"
        
        # Parse evidence
        evidence = EvidenceOut(
            iron_oxide_index=props['evidence']['iron_oxide_index'],
            ndvi_anomaly=props['evidence']['ndvi_anomaly'],
            distance_to_known_mine_km=props['evidence']['distance_to_known_mine_km']
        )
        
        # Create target
        target = ProspectivityTargetOut(
            rank=props['rank'],
            id=target_id,
            lat=props['lat'],
            lon=props['lon'],
            probability=props['probability'],
            confidence=props['confidence'],
            nearest_mine=props.get('nearest_mine'),
            distance_to_mine_km=props.get('distance_to_mine_km'),
            evidence=evidence
        )
        
        targets.append(target)
    
    return ProspectivityTargetsResponse(targets=targets)


@router.get("/prospectivity/features/{target_id}", response_model=FeatureImportanceResponse)
def get_target_features(target_id: str):
    """
    Get feature importance for a specific target
    
    For MVP: Returns global model feature importance (same for all targets).
    For Production: Could return SHAP values specific to each prediction.
    
    Args:
        target_id: Target identifier (e.g., "target_001")
    
    Returns:
        FeatureImportanceResponse with ranked features
    """
    
    # Validate target_id format
    if not target_id.startswith("target_"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target_id format. Expected 'target_XXX', got '{target_id}'"
        )
    
    # Check if metrics file exists
    if not METRICS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Prospectivity metrics not found. Run ml/prism/prospectivity.py first."
        )
    
    # Load model metrics
    with open(METRICS_PATH, 'r') as f:
        metrics = json.load(f)
    
    # Get feature importance from trained model
    feature_importance = metrics['feature_importance']
    
    # Convert to API format
    features = []
    for feat in feature_importance:
        feature_name = feat['feature']
        display_name = FEATURE_DISPLAY_NAMES.get(feature_name, feature_name)
        
        features.append(FeatureImportanceOut(
            feature_name=feature_name,
            importance=feat['importance'],
            display_name=display_name
        ))
    
    return FeatureImportanceResponse(
        target_id=target_id,
        feature_importance=features
    )


@router.get("/prospectivity/features", response_model=FeatureImportanceResponse)
def get_global_features():
    """
    Get global model feature importance
    
    Returns feature importance from the trained Random Forest model.
    Shows which features contribute most to prospectivity predictions.
    
    Returns:
        FeatureImportanceResponse with ranked features
    """
    
    # Check if metrics file exists
    if not METRICS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Prospectivity metrics not found. Run ml/prism/prospectivity.py first."
        )
    
    # Load model metrics
    with open(METRICS_PATH, 'r') as f:
        metrics = json.load(f)
    
    # Get feature importance from trained model
    feature_importance = metrics['feature_importance']
    
    # Convert to API format
    features = []
    for feat in feature_importance:
        feature_name = feat['feature']
        display_name = FEATURE_DISPLAY_NAMES.get(feature_name, feature_name)
        
        features.append(FeatureImportanceOut(
            feature_name=feature_name,
            importance=feat['importance'],
            display_name=display_name
        ))
    
    return FeatureImportanceResponse(
        target_id=None,  # Global importance (not target-specific)
        feature_importance=features
    )
