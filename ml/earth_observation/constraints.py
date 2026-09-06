"""
Multi-Source Earth Observation Constraints Pipeline

Fetches and processes satellite data to provide operational constraints
for mining production forecasting:

1. Soil Moisture - affects equipment mobility and pit stability
2. Land Surface Temperature - affects worker safety and equipment
3. NDVI (vegetation) - proxy for monsoon impact and site conditions
4. Rainfall - direct operational constraint (already integrated)

For MVP: Uses synthetic but realistic data based on typical patterns.
For Production: Replace with actual satellite API calls.

Author: Person A (Backend/ML)
Date: 2024
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import warnings
warnings.filterwarnings('ignore')


class EOConstraintsFetcher:
    """Fetch multi-source Earth Observation constraints for mining operations"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize EO constraints fetcher"""
        self.data_dir = Path(data_dir)
        self.eo_dir = self.data_dir / "eo_constraints"
        self.eo_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ Initialized EOConstraintsFetcher")
        print(f"   Output directory: {self.eo_dir.absolute()}")
    
    def fetch_soil_moisture(
        self, 
        latitude: float, 
        longitude: float,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch soil moisture data for location
        
        Data source: SMAP Level-4 (NASA) or Sentinel-1 derived
        Units: Volumetric soil moisture (0-1, where 1 = saturated)
        
        For MVP: Generates synthetic data based on monsoon patterns
        For Production: Use NASA SMAP API or Google Earth Engine
        
        Args:
            latitude: Site latitude
            longitude: Site longitude
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with columns: date, soil_moisture
        """
        
        print(f"\n🌍 Fetching soil moisture data...")
        print(f"   Location: ({latitude:.4f}, {longitude:.4f})")
        print(f"   Period: {start_date} to {end_date}")
        
        # Generate date range
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate synthetic soil moisture with seasonal patterns
        np.random.seed(42)
        
        # Base pattern: higher during monsoon (June-Sept)
        months = dates.month.values
        
        # Monsoon pattern (higher in Jun-Sep)
        monsoon_effect = np.where(
            (months >= 6) & (months <= 9),
            0.5,  # High moisture during monsoon
            0.25  # Lower moisture otherwise
        )
        
        # Add random variation
        noise = np.random.normal(0, 0.05, len(dates))
        
        # Combine with bounds
        soil_moisture = np.clip(monsoon_effect + noise, 0.1, 0.7)
        
        # Add some temporal autocorrelation (smooth changes)
        for i in range(1, len(soil_moisture)):
            soil_moisture[i] = 0.7 * soil_moisture[i] + 0.3 * soil_moisture[i-1]
        
        df = pd.DataFrame({
            'date': dates,
            'soil_moisture': soil_moisture
        })
        
        print(f"✅ Generated {len(df)} daily soil moisture records")
        print(f"   Range: {soil_moisture.min():.3f} - {soil_moisture.max():.3f}")
        
        return df
    
    def fetch_land_surface_temperature(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch land surface temperature data
        
        Data source: MODIS LST or Landsat 8 thermal
        Units: Degrees Celsius (daily maximum)
        
        For MVP: Generates synthetic data based on seasonal patterns
        For Production: Use MODIS or Landsat API
        
        Args:
            latitude: Site latitude
            longitude: Site longitude
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with columns: date, temperature_max_c
        """
        
        print(f"\n🌡️  Fetching land surface temperature data...")
        print(f"   Location: ({latitude:.4f}, {longitude:.4f})")
        print(f"   Period: {start_date} to {end_date}")
        
        # Generate date range
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate synthetic temperature with seasonal patterns
        np.random.seed(43)
        
        # Day of year for seasonal pattern
        day_of_year = dates.dayofyear.values
        
        # Seasonal pattern (hotter in Apr-Jun, cooler in Dec-Jan)
        # Indian summer: Apr-Jun (peak ~42°C)
        # Monsoon: Jul-Sep (cooler ~30°C)
        # Winter: Dec-Jan (mild ~22°C)
        seasonal_temp = 32 + 10 * np.sin((day_of_year - 100) * 2 * np.pi / 365)
        
        # Add random daily variation
        noise = np.random.normal(0, 2, len(dates))
        
        temperature = seasonal_temp + noise
        temperature = np.clip(temperature, 18, 45)  # Realistic bounds
        
        df = pd.DataFrame({
            'date': dates,
            'temperature_max_c': temperature
        })
        
        print(f"✅ Generated {len(df)} daily temperature records")
        print(f"   Range: {temperature.min():.1f}°C - {temperature.max():.1f}°C")
        
        return df
    
    def fetch_ndvi(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch NDVI (vegetation index) data
        
        Data source: Sentinel-2 or Landsat 8
        Units: NDVI (-1 to 1, where higher = more vegetation)
        
        For MVP: Generates synthetic data based on monsoon patterns
        For Production: Use Sentinel-2 from Earth Engine
        
        Args:
            latitude: Site latitude
            longitude: Site longitude
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with columns: date, ndvi
        """
        
        print(f"\n🌱 Fetching NDVI data...")
        print(f"   Location: ({latitude:.4f}, {longitude:.4f})")
        print(f"   Period: {start_date} to {end_date}")
        
        # Generate date range (16-day composite to match Sentinel-2 revisit)
        dates = pd.date_range(start=start_date, end=end_date, freq='16D')
        
        # Generate synthetic NDVI with seasonal patterns
        np.random.seed(44)
        
        months = dates.month.values
        
        # NDVI pattern: higher during/after monsoon (Jul-Nov)
        monsoon_greenness = np.where(
            (months >= 7) & (months <= 11),
            0.45,  # Green during monsoon
            0.25   # Brown/dry in summer
        )
        
        # Add variation
        noise = np.random.normal(0, 0.05, len(dates))
        ndvi = np.clip(monsoon_greenness + noise, 0.1, 0.7)
        
        # Interpolate to daily for consistency
        df_composite = pd.DataFrame({
            'date': dates,
            'ndvi': ndvi
        })
        
        # Create daily dates
        daily_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        df_daily = pd.DataFrame({'date': daily_dates})
        
        # Merge and forward-fill (NDVI changes slowly)
        df = df_daily.merge(df_composite, on='date', how='left')
        df['ndvi'] = df['ndvi'].fillna(method='ffill').fillna(method='bfill')
        
        print(f"✅ Generated {len(df)} daily NDVI records")
        print(f"   Range: {df['ndvi'].min():.3f} - {df['ndvi'].max():.3f}")
        
        return df
    
    def fetch_all_constraints(
        self,
        mine_name: str,
        latitude: float,
        longitude: float,
        start_date: str = "2018-01-01",
        end_date: str = None
    ) -> pd.DataFrame:
        """
        Fetch all EO constraints for a mine location
        
        Args:
            mine_name: Name of the mine
            latitude: Mine latitude
            longitude: Mine longitude
            start_date: Start date
            end_date: End date (default: today)
        
        Returns:
            DataFrame with all constraints
        """
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        print("="*70)
        print(f"🛰️  Fetching EO Constraints for {mine_name}")
        print("="*70)
        
        # Fetch each constraint
        soil_df = self.fetch_soil_moisture(latitude, longitude, start_date, end_date)
        temp_df = self.fetch_land_surface_temperature(latitude, longitude, start_date, end_date)
        ndvi_df = self.fetch_ndvi(latitude, longitude, start_date, end_date)
        
        # Merge all constraints
        print(f"\n🔗 Merging all constraints...")
        
        df = soil_df.copy()
        df = df.merge(temp_df, on='date', how='left')
        df = df.merge(ndvi_df, on='date', how='left')
        
        # Load existing rainfall data if available
        rainfall_file = self.data_dir / "processed" / f"rainfall_{mine_name.lower().replace(' ', '_')}.csv"
        
        if rainfall_file.exists():
            print(f"   Loading existing rainfall data...")
            rainfall_df = pd.read_csv(rainfall_file)
            rainfall_df['date'] = pd.to_datetime(rainfall_df['date'])
            
            df = df.merge(rainfall_df[['date', 'rainfall_mm']], on='date', how='left')
        else:
            print(f"   Generating synthetic rainfall...")
            # Generate synthetic rainfall with monsoon pattern
            np.random.seed(45)
            months = df['date'].dt.month.values
            
            monsoon_rain = np.where(
                (months >= 6) & (months <= 9),
                np.random.exponential(5, len(df)),  # More rain in monsoon
                np.random.exponential(1, len(df))   # Less rain otherwise
            )
            
            df['rainfall_mm'] = np.clip(monsoon_rain, 0, 50)
        
        # Fill any missing values
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        print(f"\n✅ Combined constraints dataset created")
        print(f"   Total records: {len(df)}")
        print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"   Columns: {list(df.columns)}")
        
        # Save to CSV
        output_file = self.eo_dir / f"{mine_name.lower().replace(' ', '_')}_constraints.csv"
        df.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved to {output_file}")
        
        return df
    
    def generate_forecast(
        self,
        df: pd.DataFrame,
        n_days: int = 7
    ) -> Dict:
        """
        Generate simple 7-day forecast for constraints
        
        For MVP: Uses persistence + random walk
        For Production: Use weather API or ML forecasting
        
        Args:
            df: Historical constraints data
            n_days: Number of days to forecast
        
        Returns:
            Dictionary with forecasted values
        """
        
        print(f"\n📈 Generating {n_days}-day forecast...")
        
        # Get latest values
        latest = df.iloc[-1]
        
        # Generate forecast dates
        last_date = pd.to_datetime(latest['date'])
        forecast_dates = [(last_date + timedelta(days=i+1)).strftime('%Y-%m-%d') 
                         for i in range(n_days)]
        
        # Simple persistence with random walk
        np.random.seed(46)
        
        forecasts = {
            'dates': forecast_dates,
            'rainfall_mm': [],
            'soil_moisture': [],
            'temperature_max_c': [],
            'ndvi': []
        }
        
        # Forecast each variable
        current_rain = latest['rainfall_mm']
        current_soil = latest['soil_moisture']
        current_temp = latest['temperature_max_c']
        current_ndvi = latest['ndvi']
        
        for i in range(n_days):
            # Rainfall: random walk with dampening
            current_rain = max(0, current_rain + np.random.normal(0, 2))
            forecasts['rainfall_mm'].append(round(current_rain, 1))
            
            # Soil moisture: slow changes, influenced by rainfall
            current_soil = np.clip(
                current_soil + 0.01 * (current_rain / 10) + np.random.normal(0, 0.02),
                0.1, 0.7
            )
            forecasts['soil_moisture'].append(round(current_soil, 3))
            
            # Temperature: small random walk
            current_temp = np.clip(
                current_temp + np.random.normal(0, 1.5),
                18, 45
            )
            forecasts['temperature_max_c'].append(round(current_temp, 1))
            
            # NDVI: very slow changes
            current_ndvi = np.clip(
                current_ndvi + np.random.normal(0, 0.01),
                0.1, 0.7
            )
            forecasts['ndvi'].append(round(current_ndvi, 3))
        
        print(f"✅ Generated {n_days}-day forecast for all constraints")
        
        return forecasts


def main():
    """Main entry point"""
    
    print("="*70)
    print("OreSight EO Constraints Pipeline v1.0")
    print("Person A (Backend/ML)")
    print("="*70)
    
    # Initialize fetcher
    fetcher = EOConstraintsFetcher(data_dir="data")
    
    # Fetch constraints for Balaghat mine
    mine_name = "Balaghat"
    latitude = 21.8075
    longitude = 80.1889
    
    df = fetcher.fetch_all_constraints(
        mine_name=mine_name,
        latitude=latitude,
        longitude=longitude,
        start_date="2018-01-01",
        end_date="2024-12-31"
    )
    
    # Generate forecast
    forecast = fetcher.generate_forecast(df, n_days=7)
    
    # Save forecast
    forecast_file = Path("data/eo_constraints") / f"{mine_name.lower()}_forecast_7d.json"
    with open(forecast_file, 'w') as f:
        json.dump(forecast, f, indent=2)
    
    print(f"\n💾 Saved 7-day forecast to {forecast_file}")
    
    # Print summary
    print("\n" + "="*70)
    print("📊 Summary Statistics")
    print("="*70)
    
    print(f"\n📅 Date Range: {df['date'].min()} to {df['date'].max()}")
    print(f"📝 Total Records: {len(df)}")
    
    print(f"\n🌧️  Rainfall:")
    print(f"   Mean: {df['rainfall_mm'].mean():.1f} mm/day")
    print(f"   Max: {df['rainfall_mm'].max():.1f} mm/day")
    
    print(f"\n💧 Soil Moisture:")
    print(f"   Mean: {df['soil_moisture'].mean():.3f}")
    print(f"   Range: {df['soil_moisture'].min():.3f} - {df['soil_moisture'].max():.3f}")
    
    print(f"\n🌡️  Temperature:")
    print(f"   Mean: {df['temperature_max_c'].mean():.1f}°C")
    print(f"   Range: {df['temperature_max_c'].min():.1f}°C - {df['temperature_max_c'].max():.1f}°C")
    
    print(f"\n🌱 NDVI:")
    print(f"   Mean: {df['ndvi'].mean():.3f}")
    print(f"   Range: {df['ndvi'].min():.3f} - {df['ndvi'].max():.3f}")
    
    print("\n🎉 EO constraints pipeline complete!")
    print("\n📋 Next steps:")
    print("   1. Review constraints data in data/eo_constraints/")
    print("   2. Proceed to Day 5: Enhance forecast model")
    print("   3. Use ml/pulse/forecast.py to integrate constraints")


if __name__ == "__main__":
    main()
