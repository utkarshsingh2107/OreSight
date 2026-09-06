"""
Feature Engineering for Prospectivity Analysis

Extracts features from satellite imagery and DEM for ML-based mineral prospectivity mapping.

Features extracted:
1. Spectral indices (NDVI, iron oxide ratio, clay index, SWIR ratio)
2. Topographic features (slope, aspect, curvature)
3. Distance features (to known mines, to lineaments)
4. Texture features (spatial variability)

Author: Person A (Backend/ML)
Date: 2024
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from scipy import ndimage
from scipy.spatial.distance import cdist
from sklearn.preprocessing import StandardScaler
import json
import warnings
warnings.filterwarnings('ignore')


class ProspectivityFeatureExtractor:
    """Extract features from satellite and geological data for prospectivity modeling"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize feature extractor"""
        self.data_dir = Path(data_dir)
        self.satellite_dir = self.data_dir / "satellite"
        self.geology_dir = self.data_dir / "geology"
        self.processed_dir = self.data_dir / "processed"
        
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Loaded rasters
        self.rasters = {}
        self.transform = None
        self.crs = None
        
        print("✅ Initialized ProspectivityFeatureExtractor")
        print(f"   Data directory: {self.data_dir.absolute()}")
    
    def load_rasters(self) -> Dict[str, np.ndarray]:
        """Load all satellite rasters into memory"""
        
        print("\n📂 Loading raster data...")
        
        raster_files = {
            'dem': 'dem_balaghat.tif',
            'ndvi': 'ndvi_balaghat.tif',
            'iron_oxide': 'iron_oxide_ratio_balaghat.tif',
            'clay': 'clay_index_balaghat.tif',
            'swir': 'swir_ratio_balaghat.tif'
        }
        
        for name, filename in raster_files.items():
            filepath = self.satellite_dir / filename
            
            if not filepath.exists():
                print(f"⚠️  {filepath} not found, skipping")
                continue
            
            with rasterio.open(filepath) as src:
                data = src.read(1)  # Read first band
                self.rasters[name] = data
                
                # Store transform and CRS from first raster
                if self.transform is None:
                    self.transform = src.transform
                    self.crs = src.crs
                
                print(f"   ✓ Loaded {name}: {data.shape}, range=[{data.min():.2f}, {data.max():.2f}]")
        
        print(f"✅ Loaded {len(self.rasters)} rasters")
        return self.rasters
    
    def calculate_slope_aspect(self, dem: np.ndarray, resolution: float = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate slope and aspect from DEM
        
        Args:
            dem: Digital elevation model array
            resolution: Cell size in meters
        
        Returns:
            slope (degrees), aspect (degrees from north)
        """
        
        print("\n🗻 Calculating topographic features...")
        
        # Calculate gradients
        dy, dx = np.gradient(dem, resolution)
        
        # Slope in degrees
        slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))
        
        # Aspect in degrees from north (0-360)
        aspect = np.degrees(np.arctan2(-dx, dy))
        aspect = (aspect + 360) % 360  # Normalize to 0-360
        
        print(f"   ✓ Slope: min={slope.min():.2f}°, max={slope.max():.2f}°, mean={slope.mean():.2f}°")
        print(f"   ✓ Aspect: range=[0°, 360°]")
        
        return slope, aspect
    
    def calculate_curvature(self, dem: np.ndarray, resolution: float = 100) -> np.ndarray:
        """
        Calculate profile curvature from DEM
        
        Curvature indicates convex (positive) vs concave (negative) terrain
        """
        
        # Second derivatives
        d2y = ndimage.laplace(dem)
        
        # Normalize by resolution
        curvature = d2y / (resolution ** 2)
        
        print(f"   ✓ Curvature: min={curvature.min():.6f}, max={curvature.max():.6f}")
        
        return curvature
    
    def detect_lineaments(self, dem: np.ndarray, threshold: float = 50) -> np.ndarray:
        """
        Detect lineaments (linear features) using edge detection on DEM
        
        Lineaments often indicate faults/fractures that control mineralization
        """
        
        print("\n🔍 Detecting lineaments...")
        
        # Canny edge detection
        from scipy import ndimage
        
        # Calculate magnitude of gradient
        dy, dx = np.gradient(dem)
        magnitude = np.sqrt(dx**2 + dy**2)
        
        # Threshold to get edges
        edges = magnitude > np.percentile(magnitude, 90)
        
        print(f"   ✓ Detected lineaments: {edges.sum()} pixels ({edges.sum() / edges.size * 100:.1f}%)")
        
        return edges.astype(float)
    
    def calculate_distance_to_mines(self, shape: Tuple[int, int]) -> np.ndarray:
        """Calculate distance from each pixel to nearest known mine"""
        
        print("\n📍 Calculating distance to known mines...")
        
        # Load mine locations
        mines_file = self.geology_dir / "moil_mines.geojson"
        
        if not mines_file.exists():
            print(f"⚠️  {mines_file} not found, returning zeros")
            return np.zeros(shape)
        
        gdf = gpd.read_file(mines_file)
        
        # Create grid of coordinates
        rows, cols = shape
        row_coords, col_coords = np.mgrid[0:rows, 0:cols]
        
        # Convert pixel coordinates to geographic
        from rasterio.transform import xy
        lons, lats = [], []
        for r in range(0, rows, 10):  # Sample every 10th pixel for speed
            for c in range(0, cols, 10):
                lon, lat = xy(self.transform, r, c)
                lons.append(lon)
                lats.append(lat)
        
        grid_coords = np.column_stack([lats, lons])
        mine_coords = np.column_stack([gdf.geometry.y, gdf.geometry.x])
        
        # Calculate distances (degrees, approximate)
        distances = cdist(grid_coords, mine_coords, metric='euclidean')
        min_distances = distances.min(axis=1)
        
        # Interpolate to full grid
        from scipy.interpolate import griddata
        sample_points = [(r, c) for r in range(0, rows, 10) for c in range(0, cols, 10)]
        full_points = [(r, c) for r in range(rows) for c in range(cols)]
        
        distance_grid = griddata(
            sample_points, min_distances, full_points, 
            method='linear', fill_value=min_distances.max()
        ).reshape(shape)
        
        # Convert degrees to km (approximate)
        distance_grid_km = distance_grid * 111  # 1 degree ≈ 111 km
        
        print(f"   ✓ Distance range: {distance_grid_km.min():.2f} - {distance_grid_km.max():.2f} km")
        print(f"   ✓ Using {len(gdf)} mine locations")
        
        return distance_grid_km
    
    def calculate_texture_features(self, raster: np.ndarray, window_size: int = 3) -> Dict[str, np.ndarray]:
        """
        Calculate texture features (spatial variability) using moving window
        
        Args:
            raster: Input raster
            window_size: Size of moving window (default 3x3)
        
        Returns:
            Dictionary with std, range, mean texture features
        """
        
        print(f"\n🎨 Calculating texture features (window={window_size}x{window_size})...")
        
        # Standard deviation
        std = ndimage.generic_filter(raster, np.std, size=window_size)
        
        # Range (max - min)
        def range_filter(values):
            return values.max() - values.min()
        
        range_texture = ndimage.generic_filter(raster, range_filter, size=window_size)
        
        print(f"   ✓ Std texture: range=[{std.min():.3f}, {std.max():.3f}]")
        print(f"   ✓ Range texture: range=[{range_texture.min():.3f}, {range_texture.max():.3f}]")
        
        return {
            'std': std,
            'range': range_texture
        }
    
    def extract_features_at_points(self, points_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
        """
        Extract all features at given point locations
        
        Args:
            points_gdf: GeoDataFrame with point geometries
        
        Returns:
            DataFrame with features for each point
        """
        
        print(f"\n🎯 Extracting features at {len(points_gdf)} points...")
        
        features = []
        
        for idx, point in points_gdf.iterrows():
            lon, lat = point.geometry.x, point.geometry.y
            
            # Convert geographic coords to pixel coords
            row, col = rasterio.transform.rowcol(self.transform, lon, lat)
            
            # Extract features from each raster
            feature_dict = {
                'lat': lat,
                'lon': lon,
            }
            
            # Add label if present
            if 'label' in point:
                feature_dict['label'] = point['label']
            
            # Spectral indices
            for name in ['ndvi', 'iron_oxide', 'clay', 'swir']:
                if name in self.rasters:
                    try:
                        feature_dict[name] = self.rasters[name][row, col]
                    except IndexError:
                        feature_dict[name] = np.nan
            
            # Topographic features
            if 'dem' in self.rasters:
                try:
                    feature_dict['elevation'] = self.rasters['dem'][row, col]
                except IndexError:
                    feature_dict['elevation'] = np.nan
            
            if 'slope' in self.rasters:
                try:
                    feature_dict['slope'] = self.rasters['slope'][row, col]
                except IndexError:
                    feature_dict['slope'] = np.nan
            
            if 'aspect' in self.rasters:
                try:
                    feature_dict['aspect'] = self.rasters['aspect'][row, col]
                except IndexError:
                    feature_dict['aspect'] = np.nan
            
            if 'curvature' in self.rasters:
                try:
                    feature_dict['curvature'] = self.rasters['curvature'][row, col]
                except IndexError:
                    feature_dict['curvature'] = np.nan
            
            # Distance features
            if 'distance_to_mines' in self.rasters:
                try:
                    feature_dict['distance_to_mines_km'] = self.rasters['distance_to_mines'][row, col]
                except IndexError:
                    feature_dict['distance_to_mines_km'] = np.nan
            
            if 'distance_to_lineaments' in self.rasters:
                try:
                    feature_dict['distance_to_lineaments'] = self.rasters['distance_to_lineaments'][row, col]
                except IndexError:
                    feature_dict['distance_to_lineaments'] = np.nan
            
            # Texture features
            for texture_type in ['ndvi_std', 'iron_oxide_std']:
                if texture_type in self.rasters:
                    try:
                        feature_dict[texture_type] = self.rasters[texture_type][row, col]
                    except IndexError:
                        feature_dict[texture_type] = np.nan
            
            features.append(feature_dict)
        
        df = pd.DataFrame(features)
        
        # Remove rows with too many NaNs
        nan_threshold = 0.3  # Remove if >30% features are NaN
        nan_ratio = df.isna().sum(axis=1) / len(df.columns)
        df = df[nan_ratio < nan_threshold]
        
        print(f"   ✓ Extracted {len(df.columns) - 2} features")  # -2 for lat/lon
        print(f"   ✓ Valid samples: {len(df)} (removed {len(features) - len(df)} with too many NaNs)")
        
        return df
    
    def run_pipeline(self) -> pd.DataFrame:
        """Run complete feature extraction pipeline"""
        
        print("="*70)
        print("🚀 Prospectivity Feature Extraction Pipeline")
        print("="*70)
        
        # Step 1: Load rasters
        self.load_rasters()
        
        if len(self.rasters) == 0:
            raise ValueError("No rasters loaded! Run fetch_satellite_data.py first.")
        
        # Step 2: Calculate derived features
        if 'dem' in self.rasters:
            slope, aspect = self.calculate_slope_aspect(self.rasters['dem'])
            self.rasters['slope'] = slope
            self.rasters['aspect'] = aspect
            
            curvature = self.calculate_curvature(self.rasters['dem'])
            self.rasters['curvature'] = curvature
            
            lineaments = self.detect_lineaments(self.rasters['dem'])
            
            # Calculate distance to lineaments
            from scipy.ndimage import distance_transform_edt
            distance_to_lineaments = distance_transform_edt(~lineaments.astype(bool))
            self.rasters['distance_to_lineaments'] = distance_to_lineaments
        
        # Step 3: Distance to mines
        shape = self.rasters['dem'].shape
        distance_to_mines = self.calculate_distance_to_mines(shape)
        self.rasters['distance_to_mines'] = distance_to_mines
        
        # Step 4: Texture features (OPTIONAL - skip for speed)
        # if 'ndvi' in self.rasters:
        #     ndvi_texture = self.calculate_texture_features(self.rasters['ndvi'])
        #     self.rasters['ndvi_std'] = ndvi_texture['std']
        # 
        # if 'iron_oxide' in self.rasters:
        #     iron_texture = self.calculate_texture_features(self.rasters['iron_oxide'])
        #     self.rasters['iron_oxide_std'] = iron_texture['std']
        
        print("\n⏩ Skipping texture features for speed (optional features)")
        print("   Using 12 core features: 4 spectral + 4 topographic + 2 distance + lat/lon")
        
        # Step 5: Load training labels
        labels_file = self.geology_dir / "training_labels.geojson"
        
        if not labels_file.exists():
            raise FileNotFoundError(f"{labels_file} not found! Run fetch_satellite_data.py first.")
        
        labels_gdf = gpd.read_file(labels_file)
        print(f"\n📋 Loaded {len(labels_gdf)} training samples")
        
        # Step 6: Extract features at label points
        features_df = self.extract_features_at_points(labels_gdf)
        
        # Step 7: Save to parquet
        output_path = self.processed_dir / "prospectivity_features.parquet"
        features_df.to_parquet(output_path, index=False)
        
        print(f"\n✅ Saved features to {output_path}")
        print(f"   Shape: {features_df.shape}")
        print(f"   Features: {[c for c in features_df.columns if c not in ['lat', 'lon', 'label']]}")
        
        # Step 8: Summary statistics
        self._print_summary(features_df)
        
        return features_df
    
    def _print_summary(self, df: pd.DataFrame):
        """Print summary statistics"""
        
        print("\n" + "="*70)
        print("📊 Feature Summary")
        print("="*70)
        
        if 'label' in df.columns:
            print(f"\nClass distribution:")
            print(f"   Positive (near mines): {(df['label'] == 1).sum()}")
            print(f"   Negative (far from mines): {(df['label'] == 0).sum()}")
            print(f"   Class balance: {(df['label'] == 1).sum() / len(df) * 100:.1f}% positive")
        
        print(f"\nFeature statistics:")
        feature_cols = [c for c in df.columns if c not in ['lat', 'lon', 'label']]
        
        for col in feature_cols:
            if col in df.columns:
                print(f"   {col}: mean={df[col].mean():.3f}, std={df[col].std():.3f}, "
                      f"range=[{df[col].min():.3f}, {df[col].max():.3f}]")
        
        print("\n📋 Next steps:")
        print("   1. Review feature distributions")
        print("   2. Proceed to Day 3: Train prospectivity ML model")
        print("   3. Use ml/prism/prospectivity.py for model training")


def main():
    """Main entry point"""
    
    print("OreSight Prospectivity Feature Extractor v1.0")
    print("Person A (Backend/ML)\n")
    
    # Run feature extraction
    extractor = ProspectivityFeatureExtractor(data_dir="data")
    features_df = extractor.run_pipeline()
    
    print("\n🎉 Feature extraction complete!")
    print(f"   Output: data/processed/prospectivity_features.parquet")
    print(f"   Samples: {len(features_df)}")
    print(f"   Features: {len([c for c in features_df.columns if c not in ['lat', 'lon', 'label']])}")


if __name__ == "__main__":
    main()
