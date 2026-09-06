# OreSight Data Sources Documentation

**Last Updated:** 2026-09-06 19:10
**Created by:** Person A (Backend/ML)

---

## Overview

This document lists all data sources used in the OreSight prospectivity analysis.

---

## Geological Data

### MOIL Mine Locations
- **File:** `data\geology\moil_mines.geojson`
- **Source:** MOIL (Manganese Ore India Limited) public records
- **Type:** Point vector (GeoJSON)
- **Count:** 11 mines
- **Coverage:** Nagpur-Balaghat manganese belt
- **CRS:** EPSG:4326 (WGS84)
- **License:** Public domain
- **Notes:** Includes both underground and opencast mines

### Training Labels
- **File:** `data\geology\training_labels.geojson`
- **Source:** Generated from MOIL mine locations
- **Type:** Point vector with binary labels
- **Positive samples:** 1km buffer around known mines
- **Negative samples:** >5km from any mine
- **Use:** ML model training and validation

---

## Satellite Data

### Digital Elevation Model (DEM)
- **File:** `data\satellite\dem_balaghat.tif`
- **Source:** SRTM 30m (Shuttle Radar Topography Mission)
- **Resolution:** 30m (1 arc-second)
- **Coverage:** Balaghat belt (79.50°E - 81.50°E, 21.00°N - 22.50°N)
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

s2 = ee.ImageCollection('COPERNICUS/S2_SR') \
    .filterBounds(region) \
    .filterDate('2022-01-01', '2024-01-01') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
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
Last verified: 2026-09-06
