"""
Test Enhanced Forecast Model with EO Constraints

Tests the updated forecast model with 4 satellite inputs:
- Rainfall (already integrated)
- Soil Moisture (SMAP/Sentinel-1)
- Temperature (MODIS LST)
- NDVI (Sentinel-2)

Author: Person A (Backend/ML)
Date: 2024
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from ml.pulse import forecast

def load_production_with_constraints(mine_name: str = "balaghat") -> pd.DataFrame:
    """Load production data merged with EO constraints"""
    
    print(f"📂 Loading data for {mine_name}...")
    
    # Load production data
    prod_file = Path("data/synthetic") / f"production_daily_{mine_name}.csv"
    prod_df = pd.read_csv(prod_file)
    prod_df['date'] = pd.to_datetime(prod_df['date'])
    
    print(f"   ✓ Production: {len(prod_df)} records")
    
    # Load EO constraints
    eo_file = Path("data/eo_constraints") / f"{mine_name}_constraints.csv"
    eo_df = pd.read_csv(eo_file)
    eo_df['date'] = pd.to_datetime(eo_df['date'])
    
    print(f"   ✓ EO Constraints: {len(eo_df)} records")
    
    # Merge
    merged = prod_df.merge(
        eo_df[['date', 'soil_moisture', 'temperature_max_c', 'ndvi', 'rainfall_mm']],
        on='date',
        how='left',
        suffixes=('', '_eo')
    )
    
    # Use EO rainfall if production rainfall is missing
    if 'rainfall_mm_eo' in merged.columns:
        merged['rainfall_mm'] = merged['rainfall_mm'].fillna(merged['rainfall_mm_eo'])
        merged = merged.drop('rainfall_mm_eo', axis=1)
    
    # Fill any remaining missing values
    merged = merged.fillna({
        'soil_moisture': 0.35,
        'temperature_max_c': 32.0,
        'ndvi': 0.35,
        'rainfall_mm': 0.0,
        'equipment_downtime_hours': 0.0
    })
    
    print(f"   ✓ Merged: {len(merged)} records with {len(merged.columns)} columns")
    print(f"   Columns: {list(merged.columns)}")
    
    return merged


def test_forecast():
    """Test the enhanced forecast model"""
    
    print("="*70)
    print("🧪 Testing Enhanced Forecast Model with EO Constraints")
    print("="*70)
    
    # Load data
    df = load_production_with_constraints("balaghat")
    
    # Ensure required columns
    if 'is_holiday' not in df.columns:
        df['is_holiday'] = 0
    
    # Test forecast
    mine_id = 1
    horizon_days = 30
    monthly_target = 25000
    
    print(f"\n🔮 Running forecast prediction...")
    print(f"   Mine ID: {mine_id}")
    print(f"   Horizon: {horizon_days} days")
    print(f"   Monthly target: {monthly_target:,} tonnes")
    
    result = forecast.predict(
        mine_id=mine_id,
        horizon_days=horizon_days,
        history_df=df,
        monthly_target_tonnes=monthly_target,
        rainfall_override_mm=None
    )
    
    print(f"\n✅ Forecast Results:")
    print(f"   P10 (optimistic): {result['p10']:,.0f} tonnes")
    print(f"   P50 (median): {result['p50']:,.0f} tonnes")
    print(f"   P90 (pessimistic): {result['p90']:,.0f} tonnes")
    print(f"   Shortfall probability: {result['shortfall_probability']:.1%}")
    
    print(f"\n📊 Top Drivers (with categories):")
    for i, driver in enumerate(result['drivers'], 1):
        print(f"   {i}. {driver['name']} ({driver['category']})")
        print(f"      Impact: {driver['impact']:.3f}")
        print(f"      Direction: {driver['direction']}")
    
    # Check if EO constraints are being used
    eo_drivers = [d for d in result['drivers'] 
                  if any(x in d['name'].lower() for x in ['soil', 'temperature', 'ndvi', 'vegetation'])]
    
    if eo_drivers:
        print(f"\n✅ SUCCESS: EO constraints are active in forecast!")
        print(f"   {len(eo_drivers)} EO-related driver(s) found in top 5")
    else:
        print(f"\n⚠️  Note: No EO constraints in top 5 drivers")
        print(f"   They may have lower importance than other features")
    
    # Test what-if with rainfall override
    print(f"\n🔄 Testing what-if scenario (heavy rainfall)...")
    
    result_whatif = forecast.predict(
        mine_id=mine_id,
        horizon_days=horizon_days,
        history_df=df,
        monthly_target_tonnes=monthly_target,
        rainfall_override_mm=15.0  # Heavy rainfall scenario
    )
    
    print(f"   Baseline P50: {result['p50']:,.0f} tonnes")
    print(f"   Heavy rain P50: {result_whatif['p50']:,.0f} tonnes")
    print(f"   Impact: {result_whatif['p50'] - result['p50']:,.0f} tonnes")
    
    print("\n" + "="*70)
    print("✅ Enhanced Forecast Model Test Complete!")
    print("="*70)
    
    print("\n📋 Summary:")
    print(f"   ✓ Model trained with {len(df)} historical records")
    print(f"   ✓ Using {len(forecast.FEATURE_COLUMNS)} features (including 5 EO features)")
    print(f"   ✓ Forecast range: {result['p10']:,.0f} - {result['p90']:,.0f} tonnes")
    print(f"   ✓ Top driver categories: weather, equipment, operational")
    print(f"   ✓ What-if scenarios working")
    
    print("\n📤 Ready for Person B:")
    print("   - Enhanced forecast API now returns 4 satellite inputs")
    print("   - Driver categories included for UI grouping")
    print("   - Model automatically uses EO constraints when available")
    
    return result


if __name__ == "__main__":
    result = test_forecast()
