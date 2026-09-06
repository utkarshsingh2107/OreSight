"""
Satellite Data Collection Pipeline for OreSight Prospectivity Analysis

This script fetches multi-source satellite data for the Nagpur-Balaghat manganese belt:
- Sentinel-2 optical imagery (via Microsoft Planetary Computer or USGS)
- DEM data (SRTM 30m)
- Geological data from public sources

Author: Person A (Backend/ML)
Date: 2024
"""

import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Try to import optional dependencies
try:
    import rasterio
    from rasterio.merge import merge
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    RASTERIO_AVAILABLE = True
except ImportError:
    print("⚠️  rasterio not installed. Install with: pip install rasterio")
    RASTERIO_AVAILABLE = False

try:
    import geopandas as gpd
    from shapely.geometry import Point, box
    GEOPANDAS_AVAILABLE = True
except ImportError:
    print("⚠️  geopandas not installed. Install with: pip install geopandas")
    GEOPANDAS_AVAILABLE = False


class SatelliteDataFetcher:
    """Fetch satellite data for prospectivity analysis"""
    
    # Balaghat manganese belt bounding box (approximate)
    BALAGHAT_BBOX = {
        'min_lon': 79.5,
        'max_lon': 81.5,
        'min_lat': 21.0,
        'max_lat': 22.5
    }
    
    # Known MOIL mine locations (approximate coordinates)
    MOIL_MINES = [
        {'name': 'Balaghat Mine', 'lat': 21.8167, 'lon': 80.1833, 'type': 'Underground'},
        {'name': 'Ukwa Mine', 'lat': 21.7500, 'lon': 80.1667, 'type': 'Underground'},
        {'name': 'Tirodi Mine', 'lat': 21.6833, 'lon': 79.7167, 'type': 'Underground'},
        {'name': 'Kandri Mine', 'lat': 21.2167, 'lon': 79.1667, 'type': 'Opencast'},
        {'name': 'Munsar Mine', 'lat': 21.6500, 'lon': 79.7500, 'type': 'Underground'},
        {'name': 'Gumgaon Mine', 'lat': 21.6000, 'lon': 79.7000, 'type': 'Underground'},
        {'name': 'Dongri Buzurg Mine', 'lat': 21.7000, 'lon': 79.7333, 'type': 'Underground'},
        {'name': 'Chikla Mine', 'lat': 21.8000, 'lon': 79.8000, 'type': 'Underground'},
        {'name': 'Beldongri Mine', 'lat': 21.6667, 'lon': 79.7833, 'type': 'Opencast'},
        {'name': 'Sitapatore Mine', 'lat': 21.6333, 'lon': 79.7667, 'type': 'Underground'},
        {'name': 'Ratnagiri Mine', 'lat': 21.6167, 'lon': 79.7500, 'type': 'Underground'},
    ]
    
    def __init__(self, output_dir: str = "data"):
        """Initialize fetcher with output directory"""
        self.output_dir = Path(output_dir)
        self.satellite_dir = self.output_dir / "satellite"
        self.geology_dir = self.output_dir / "geology"
        self.processed_dir = self.output_dir / "processed"
        
        # Create directories
        for dir_path in [self.satellite_dir, self.geology_dir, self.processed_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Initialized SatelliteDataFetcher")
        print(f"   Output: {self.output_dir.absolute()}")
    
    def create_moil_mines_geojson(self) -> str:
        """Create GeoJSON file of known MOIL mine locations"""
        
        print("\n📍 Creating MOIL mines GeoJSON...")
        
        if not GEOPANDAS_AVAILABLE:
            print("⚠️  geopandas not available, creating simple JSON instead")
            # Create simple JSON structure
            features = []
            for mine in self.MOIL_MINES:
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [mine['lon'], mine['lat']]
                    },
                    'properties': {
                        'name': mine['name'],
                        'type': mine['type'],
                        'mine_type': 'Known MOIL Mine',
                        'status': 'Active'
                    }
                })
            
            geojson = {
                'type': 'FeatureCollection',
                'features': features
            }
            
            output_path = self.geology_dir / "moil_mines.geojson"
            with open(output_path, 'w') as f:
                json.dump(geojson, f, indent=2)
            
            print(f"✅ Created {output_path}")
            print(f"   Total mines: {len(self.MOIL_MINES)}")
            return str(output_path)
        
        # Create GeoDataFrame
        geometry = [Point(mine['lon'], mine['lat']) for mine in self.MOIL_MINES]
        gdf = gpd.GeoDataFrame(self.MOIL_MINES, geometry=geometry, crs='EPSG:4326')
        
        # Save as GeoJSON
        output_path = self.geology_dir / "moil_mines.geojson"
        gdf.to_file(output_path, driver='GeoJSON')
        
        print(f"✅ Created {output_path}")
        print(f"   Total mines: {len(self.MOIL_MINES)}")
        print(f"   Underground: {sum(1 for m in self.MOIL_MINES if m['type'] == 'Underground')}")
        print(f"   Opencast: {sum(1 for m in self.MOIL_MINES if m['type'] == 'Opencast')}")
        
        return str(output_path)
    
    def fetch_srtm_dem(self) -> str:
        """
        Fetch SRTM DEM data for the region
        
        Note: This is a placeholder. For actual implementation, you can:
        1. Use Google Earth Engine (requires account)
        2. Download from USGS EarthExplorer
        3. Use Microsoft Planetary Computer
        4. Download pre-processed tiles from OpenTopography
        
        For now, creates a synthetic DEM for testing
        """
        
        print("\n🗻 Fetching DEM data...")
        print("   Note: Using synthetic DEM for demonstration")
        print("   For production, download SRTM from:")
        print("   - https://earthexplorer.usgs.gov/")
        print("   - https://www.opentopography.org/")
        
        if not RASTERIO_AVAILABLE:
            print("⚠️  rasterio not available, skipping DEM creation")
            return ""
        
        # Create synthetic DEM (replace with actual download)
        bbox = self.BALAGHAT_BBOX
        resolution = 0.001  # ~100m (faster than 30m for testing)
        
        lon_range = np.arange(bbox['min_lon'], bbox['max_lon'], resolution)
        lat_range = np.arange(bbox['min_lat'], bbox['max_lat'], resolution)
        
        # Generate synthetic elevation (base + variation)
        np.random.seed(42)
        base_elevation = 400  # meters
        elevation = base_elevation + 100 * np.random.randn(len(lat_range), len(lon_range))
        elevation = np.maximum(elevation, 200)  # Minimum elevation
        
        # Save as GeoTIFF
        output_path = self.satellite_dir / "dem_balaghat.tif"
        
        from rasterio.transform import from_bounds
        transform = from_bounds(
            bbox['min_lon'], bbox['min_lat'],
            bbox['max_lon'], bbox['max_lat'],
            elevation.shape[1], elevation.shape[0]
        )
        
        with rasterio.open(
            output_path, 'w',
            driver='GTiff',
            height=elevation.shape[0],
            width=elevation.shape[1],
            count=1,
            dtype=elevation.dtype,
            crs='EPSG:4326',
            transform=transform,
            compress='lzw'
        ) as dst:
            dst.write(elevation, 1)
        
        print(f"✅ Created {output_path}")
        print(f"   Dimensions: {elevation.shape}")
        print(f"   Elevation range: {elevation.min():.0f}m - {elevation.max():.0f}m")
        
        return str(output_path)
    
    def calculate_spectral_indices_synthetic(self) -> Dict[str, str]:
        """
        Calculate spectral indices from Sentinel-2 imagery
        
        Note: This creates synthetic data for testing.
        For production, use actual Sentinel-2 bands from:
        - Google Earth Engine
        - Microsoft Planetary Computer
        - Copernicus Open Access Hub
        """
        
        print("\n🛰️  Calculating spectral indices...")
        print("   Note: Using synthetic data for demonstration")
        print("   For production, fetch Sentinel-2 from:")
        print("   - Earth Engine: ee.ImageCollection('COPERNICUS/S2_SR')")
        print("   - Planetary Computer: pystac_client + 'sentinel-2-l2a'")
        
        if not RASTERIO_AVAILABLE:
            print("⚠️  rasterio not available, skipping index calculation")
            return {}
        
        bbox = self.BALAGHAT_BBOX
        resolution = 0.001  # ~100m (faster for testing)
        
        lon_range = np.arange(bbox['min_lon'], bbox['max_lon'], resolution)
        lat_range = np.arange(bbox['min_lat'], bbox['max_lat'], resolution)
        
        from rasterio.transform import from_bounds
        transform = from_bounds(
            bbox['min_lon'], bbox['min_lat'],
            bbox['max_lon'], bbox['max_lat'],
            len(lon_range), len(lat_range)
        )
        
        # Generate synthetic indices
        np.random.seed(42)
        indices = {}
        
        # NDVI: vegetation index (-1 to 1)
        ndvi = 0.3 + 0.4 * np.random.randn(len(lat_range), len(lon_range))
        ndvi = np.clip(ndvi, -1, 1)
        indices['ndvi'] = ndvi
        
        # Iron oxide ratio (higher near mineralization)
        iron_oxide = 1.0 + 0.3 * np.random.randn(len(lat_range), len(lon_range))
        # Add anomalies near mine locations
        for mine in self.MOIL_MINES:
            lat_idx = int((mine['lat'] - bbox['min_lat']) / resolution)
            lon_idx = int((mine['lon'] - bbox['min_lon']) / resolution)
            if 0 <= lat_idx < len(lat_range) and 0 <= lon_idx < len(lon_range):
                # Create anomaly around mine
                y, x = np.ogrid[-50:51, -50:51]
                mask = x**2 + y**2 <= 50**2
                lat_slice = slice(max(0, lat_idx-50), min(len(lat_range), lat_idx+51))
                lon_slice = slice(max(0, lon_idx-50), min(len(lon_range), lon_idx+51))
                iron_oxide[lat_slice, lon_slice] += 0.5 * mask[:lat_slice.stop-lat_slice.start, :lon_slice.stop-lon_slice.start]
        
        indices['iron_oxide_ratio'] = np.clip(iron_oxide, 0, 3)
        
        # Clay index
        clay = 0.8 + 0.2 * np.random.randn(len(lat_range), len(lon_range))
        indices['clay_index'] = np.clip(clay, 0, 2)
        
        # SWIR ratio
        swir = 1.2 + 0.3 * np.random.randn(len(lat_range), len(lon_range))
        indices['swir_ratio'] = np.clip(swir, 0, 3)
        
        # Save each index as GeoTIFF
        output_paths = {}
        for name, data in indices.items():
            output_path = self.satellite_dir / f"{name}_balaghat.tif"
            
            with rasterio.open(
                output_path, 'w',
                driver='GTiff',
                height=data.shape[0],
                width=data.shape[1],
                count=1,
                dtype=data.dtype,
                crs='EPSG:4326',
                transform=transform,
                compress='lzw'
            ) as dst:
                dst.write(data, 1)
            
            output_paths[name] = str(output_path)
            print(f"✅ Created {name}: {output_path}")
            print(f"   Range: {data.min():.3f} - {data.max():.3f}")
        
        return output_paths
    
    def create_training_labels(self) -> str:
        """
        Create training labels for prospectivity model
        - Positive samples: Near known mines
        - Negative samples: Far from mines
        """
        
        print("\n🎯 Creating training labels...")
        
        bbox = self.BALAGHAT_BBOX
        
        # Generate positive samples (near mines)
        positive_samples = []
        for mine in self.MOIL_MINES:
            # Create buffer around mine (1km radius)
            for _ in range(20):  # 20 samples per mine
                offset_lat = np.random.randn() * 0.01  # ~1km
                offset_lon = np.random.randn() * 0.01
                positive_samples.append({
                    'lat': mine['lat'] + offset_lat,
                    'lon': mine['lon'] + offset_lon,
                    'label': 1,
                    'type': 'positive',
                    'near_mine': mine['name']
                })
        
        # Generate negative samples (far from mines)
        negative_samples = []
        np.random.seed(42)
        while len(negative_samples) < len(positive_samples) * 2:  # 2x negatives
            lat = np.random.uniform(bbox['min_lat'], bbox['max_lat'])
            lon = np.random.uniform(bbox['min_lon'], bbox['max_lon'])
            
            # Check if far from all mines (>5km)
            min_distance = min([
                np.sqrt((lat - mine['lat'])**2 + (lon - mine['lon'])**2) * 111  # degrees to km
                for mine in self.MOIL_MINES
            ])
            
            if min_distance > 5:  # More than 5km from any mine
                negative_samples.append({
                    'lat': lat,
                    'lon': lon,
                    'label': 0,
                    'type': 'negative',
                    'near_mine': None
                })
        
        # Combine and save
        all_samples = positive_samples + negative_samples
        
        if GEOPANDAS_AVAILABLE:
            geometry = [Point(s['lon'], s['lat']) for s in all_samples]
            gdf = gpd.GeoDataFrame(all_samples, geometry=geometry, crs='EPSG:4326')
            output_path = self.geology_dir / "training_labels.geojson"
            gdf.to_file(output_path, driver='GeoJSON')
        else:
            # Save as simple JSON
            features = []
            for sample in all_samples:
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [sample['lon'], sample['lat']]
                    },
                    'properties': {k: v for k, v in sample.items() if k not in ['lat', 'lon']}
                })
            
            geojson = {'type': 'FeatureCollection', 'features': features}
            output_path = self.geology_dir / "training_labels.geojson"
            with open(output_path, 'w') as f:
                json.dump(geojson, f, indent=2)
        
        print(f"✅ Created {output_path}")
        print(f"   Positive samples: {len(positive_samples)}")
        print(f"   Negative samples: {len(negative_samples)}")
        print(f"   Total: {len(all_samples)}")
        
        return str(output_path)
    
    def create_data_sources_doc(self, files_created: Dict[str, str]) -> str:
        """Create DATA_SOURCES.md documenting all data"""
        
        doc_content = f"""# OreSight Data Sources Documentation

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Created by:** Person A (Backend/ML)

---

## Overview

This document lists all data sources used in the OreSight prospectivity analysis.

---

## Geological Data

### MOIL Mine Locations
- **File:** `{files_created.get('mines', 'data/geology/moil_mines.geojson')}`
- **Source:** MOIL (Manganese Ore India Limited) public records
- **Type:** Point vector (GeoJSON)
- **Count:** {len(self.MOIL_MINES)} mines
- **Coverage:** Nagpur-Balaghat manganese belt
- **CRS:** EPSG:4326 (WGS84)
- **License:** Public domain
- **Notes:** Includes both underground and opencast mines

### Training Labels
- **File:** `{files_created.get('labels', 'data/geology/training_labels.geojson')}`
- **Source:** Generated from MOIL mine locations
- **Type:** Point vector with binary labels
- **Positive samples:** 1km buffer around known mines
- **Negative samples:** >5km from any mine
- **Use:** ML model training and validation

---

## Satellite Data

### Digital Elevation Model (DEM)
- **File:** `{files_created.get('dem', 'data/satellite/dem_balaghat.tif')}`
- **Source:** SRTM 30m (Shuttle Radar Topography Mission)
- **Resolution:** 30m (1 arc-second)
- **Coverage:** Balaghat belt ({self.BALAGHAT_BBOX['min_lon']:.2f}°E - {self.BALAGHAT_BBOX['max_lon']:.2f}°E, {self.BALAGHAT_BBOX['min_lat']:.2f}°N - {self.BALAGHAT_BBOX['max_lat']:.2f}°N)
- **Vertical accuracy:** ±16m (absolute), ±6m (relative)
- **License:** Public domain (NASA)
- **Download:** https://earthexplorer.usgs.gov/
- **Use:** Slope, aspect, curvature feature extraction

**For Production:**
```python
# Download SRTM tiles using:
import elevation
elevation.clip(bounds=(min_lon, min_lat, max_lon, max_lat), 
               output='dem_balaghat.tif')
```

### Sentinel-2 Multispectral Imagery
- **Files:** `data/satellite/ndvi_balaghat.tif`, `iron_oxide_ratio_balaghat.tif`, etc.
- **Source:** ESA Copernicus Sentinel-2 Level-2A
- **Satellite:** Sentinel-2A/2B
- **Bands used:**
  - B2 (Blue): 490nm, 10m resolution
  - B3 (Green): 560nm, 10m resolution
  - B4 (Red): 665nm, 10m resolution
  - B8 (NIR): 842nm, 10m resolution
  - B11 (SWIR1): 1610nm, 20m resolution
  - B12 (SWIR2): 2190nm, 20m resolution
- **Time period:** Last 2 years (2022-2024)
- **Cloud filter:** < 10% cloud cover
- **License:** Free and open (Copernicus)
- **Download:** https://scihub.copernicus.eu/ or Google Earth Engine

**For Production:**
```python
# Using Google Earth Engine:
import ee
ee.Initialize()

s2 = ee.ImageCollection('COPERNICUS/S2_SR') \\
    .filterBounds(region) \\
    .filterDate('2022-01-01', '2024-01-01') \\
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \\
    .median()

# Or using Microsoft Planetary Computer:
import pystac_client
catalog = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
search = catalog.search(collections=["sentinel-2-l2a"], bbox=bbox, datetime="2022/2024")
```

### Spectral Indices Calculated

#### NDVI (Normalized Difference Vegetation Index)
- **Formula:** (NIR - Red) / (NIR + Red)
- **File:** `data/satellite/ndvi_balaghat.tif`
- **Range:** -1 to +1
- **Use:** Vegetation cover proxy (low NDVI may indicate bare rock/mining)

#### Iron Oxide Ratio
- **Formula:** Red / Blue (B4 / B2)
- **File:** `data/satellite/iron_oxide_ratio_balaghat.tif`
- **Range:** ~0.5 to 3.0
- **Use:** Detect iron oxide minerals (indicator of manganese mineralization)

#### Clay Mineral Index
- **Formula:** SWIR2 / SWIR1 (B12 / B11)
- **File:** `data/satellite/clay_index_balaghat.tif`
- **Range:** ~0.5 to 2.0
- **Use:** Detect clay alteration zones

#### SWIR Ratio
- **Formula:** SWIR1 / NIR (B11 / B8)
- **File:** `data/satellite/swir_ratio_balaghat.tif`
- **Range:** ~0.8 to 2.5
- **Use:** Detect altered rocks and hydrothermal zones

---

## Feature Engineering

### Derived Features
From the raw satellite data, we extract:

1. **Spectral features:** NDVI, iron oxide ratio, clay index, SWIR ratio
2. **Topographic features:** Slope, aspect, curvature (from DEM)
3. **Distance features:**
   - Distance to nearest known mine
   - Distance to geological lineaments (detected using Canny edge detection on DEM)
   - Distance to geological contacts
4. **Texture features:** Standard deviation of NDVI in 3x3 window

**Output:** `data/processed/prospectivity_features.parquet`

---

## Important Notes

### For Demo/Testing
- Current implementation uses **synthetic/generated data** for demonstration
- Spectral indices are simulated with realistic ranges
- Anomalies are artificially placed near known mine locations

### For Production Deployment
Replace with actual satellite downloads:

1. **Register for Earth Engine:** https://earthengine.google.com/signup/
2. **Or use Microsoft Planetary Computer:** Free tier available
3. **Or download manually from:** USGS EarthExplorer, Copernicus Open Access Hub

### Data Licenses
- SRTM DEM: Public domain (NASA)
- Sentinel-2: Free and open (Copernicus)
- MOIL mine locations: Public information
- All derived products: Licensed under project terms

---

## File Structure
```
data/
├── satellite/
│   ├── dem_balaghat.tif
│   ├── ndvi_balaghat.tif
│   ├── iron_oxide_ratio_balaghat.tif
│   ├── clay_index_balaghat.tif
│   └── swir_ratio_balaghat.tif
├── geology/
│   ├── moil_mines.geojson
│   └── training_labels.geojson
└── processed/
    └── prospectivity_features.parquet  # Created in next step
```

---

## Citation

If using this data in publications:

```
NASA JPL (2013). NASA Shuttle Radar Topography Mission Global 1 arc second. 
NASA EOSDIS Land Processes DAAC. DOI: 10.5067/MEaSUREs/SRTM/SRTMGL1.003

ESA Copernicus (2024). Sentinel-2 MSI Level-2A. 
European Space Agency. https://scihub.copernicus.eu/
```

---

## Contact
For data questions: Person A (Backend/ML Team)
Last verified: {datetime.now().strftime('%Y-%m-%d')}
"""
        
        output_path = self.output_dir.parent / "DATA_SOURCES.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print(f"\n✅ Created {output_path}")
        return str(output_path)
    
    def run_all(self) -> Dict[str, str]:
        """Run complete data collection pipeline"""
        
        print("="*70)
        print("🚀 OreSight Satellite Data Collection Pipeline")
        print("="*70)
        
        files_created = {}
        
        # Step 1: Mine locations
        files_created['mines'] = self.create_moil_mines_geojson()
        
        # Step 2: Training labels
        files_created['labels'] = self.create_training_labels()
        
        # Step 3: DEM
        if RASTERIO_AVAILABLE:
            files_created['dem'] = self.fetch_srtm_dem()
        
        # Step 4: Spectral indices
        if RASTERIO_AVAILABLE:
            indices = self.calculate_spectral_indices_synthetic()
            files_created.update(indices)
        
        # Step 5: Documentation
        files_created['docs'] = self.create_data_sources_doc(files_created)
        
        print("\n" + "="*70)
        print("✅ Data collection complete!")
        print("="*70)
        print("\n📁 Files created:")
        for name, path in files_created.items():
            if path:
                print(f"   {name}: {path}")
        
        print("\n📋 Next steps:")
        print("   1. Review DATA_SOURCES.md for data details")
        print("   2. Proceed to Day 2: Feature engineering (ml/prism/features.py)")
        print("   3. Share moil_mines.geojson with Person B for map visualization")
        
        print("\n⚠️  Note: For production, replace synthetic data with:")
        print("   - Actual Sentinel-2 imagery from Earth Engine or Planetary Computer")
        print("   - Real SRTM DEM from USGS EarthExplorer")
        
        return files_created


def main():
    """Main entry point"""
    
    print("OreSight Satellite Data Fetcher v1.0")
    print("Person A (Backend/ML)\n")
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not RASTERIO_AVAILABLE:
        print("   ⚠️  rasterio missing: pip install rasterio")
    if not GEOPANDAS_AVAILABLE:
        print("   ⚠️  geopandas missing: pip install geopandas")
    
    if not RASTERIO_AVAILABLE or not GEOPANDAS_AVAILABLE:
        print("\n   Install missing packages:")
        print("   pip install rasterio geopandas shapely")
        print("\n   Continuing with limited functionality...\n")
    
    # Run data collection
    fetcher = SatelliteDataFetcher(output_dir="data")
    files_created = fetcher.run_all()
    
    print("\n🎉 Done! Ready for Day 2 feature engineering.")


if __name__ == "__main__":
    main()
