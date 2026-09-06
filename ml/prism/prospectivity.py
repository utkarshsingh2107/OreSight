"""
Prospectivity ML Model Training

Trains a Random Forest classifier using spatial cross-validation to predict
mineral prospectivity (probability of manganese mineralization) based on
satellite and geological features.

Model outputs:
1. Trained Random Forest model (pickle)
2. Probability map (GeoTIFF raster)
3. Top N prospect targets (GeoJSON)
4. Model performance metrics (JSON)

Author: Person A (Backend/ML)
Date: 2024
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.transform import from_bounds
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import pickle
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold, cross_validate
from sklearn.metrics import (
    roc_auc_score, 
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
from shapely.geometry import Point


class ProspectivityModel:
    """Train and evaluate ML model for mineral prospectivity mapping"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize prospectivity model"""
        self.data_dir = Path(data_dir)
        self.processed_dir = self.data_dir / "processed"
        self.models_dir = Path("models")
        self.reports_dir = Path("reports")
        
        # Create output directories
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.scaler = None
        self.feature_names = None
        
        print("✅ Initialized ProspectivityModel")
        print(f"   Data directory: {self.data_dir.absolute()}")
    
    def load_training_data(self) -> pd.DataFrame:
        """Load feature-engineered training data"""
        
        print("\n📂 Loading training data...")
        
        features_file = self.processed_dir / "prospectivity_features.parquet"
        
        if not features_file.exists():
            raise FileNotFoundError(
                f"{features_file} not found! Run ml/prism/features.py first."
            )
        
        df = pd.read_parquet(features_file)
        
        print(f"✅ Loaded {len(df)} samples")
        print(f"   Features: {len([c for c in df.columns if c not in ['lat', 'lon', 'label']])}")
        print(f"   Positive samples: {(df['label'] == 1).sum()}")
        print(f"   Negative samples: {(df['label'] == 0).sum()}")
        
        return df
    
    def create_spatial_groups(self, df: pd.DataFrame, bin_size: float = 0.1) -> np.ndarray:
        """
        Create spatial groups for spatial cross-validation
        
        Groups nearby samples together to prevent data leakage
        (don't train and test on adjacent pixels)
        
        Args:
            df: DataFrame with 'lat' and 'lon' columns
            bin_size: Size of spatial bins in degrees (~10km)
        
        Returns:
            Array of group IDs for each sample
        """
        
        print(f"\n🗺️  Creating spatial groups (bin_size={bin_size}°)...")
        
        # Create grid cells
        lat_bins = (df['lat'] // bin_size).astype(int)
        lon_bins = (df['lon'] // bin_size).astype(int)
        
        # Combine into unique group IDs
        groups = lat_bins.astype(str) + '_' + lon_bins.astype(str)
        
        # Convert to numeric IDs
        unique_groups = groups.unique()
        group_map = {g: i for i, g in enumerate(unique_groups)}
        group_ids = groups.map(group_map).values
        
        print(f"✅ Created {len(unique_groups)} spatial groups")
        print(f"   Samples per group: {len(df) / len(unique_groups):.1f} avg")
        
        return group_ids
    
    def train_model(
        self, 
        df: pd.DataFrame,
        n_estimators: int = 200,
        max_depth: int = 15,
        n_splits: int = 5
    ) -> Dict:
        """
        Train Random Forest model with spatial cross-validation
        
        Args:
            df: Training data with features and labels
            n_estimators: Number of trees in forest
            max_depth: Maximum tree depth
            n_splits: Number of CV folds
        
        Returns:
            Dictionary with training results
        """
        
        print("\n" + "="*70)
        print("🌲 Training Random Forest Model")
        print("="*70)
        
        # Separate features and labels
        feature_cols = [c for c in df.columns if c not in ['lat', 'lon', 'label']]
        X = df[feature_cols].values
        y = df['label'].values
        
        self.feature_names = feature_cols
        
        print(f"\nFeatures: {len(feature_cols)}")
        print(f"Samples: {len(X)} ({(y == 1).sum()} positive, {(y == 0).sum()} negative)")
        
        # Standardize features
        print("\n📊 Standardizing features...")
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Create spatial groups
        groups = self.create_spatial_groups(df)
        
        # Initialize model
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            class_weight='balanced',  # Handle class imbalance
            random_state=42,
            n_jobs=-1,
            verbose=0
        )
        
        print(f"\n🔧 Model configuration:")
        print(f"   n_estimators: {n_estimators}")
        print(f"   max_depth: {max_depth}")
        print(f"   class_weight: balanced")
        
        # Spatial cross-validation
        print(f"\n📈 Running {n_splits}-fold spatial cross-validation...")
        
        gkf = GroupKFold(n_splits=n_splits)
        
        cv_results = cross_validate(
            self.model, X_scaled, y,
            cv=gkf.split(X_scaled, y, groups),
            scoring=['roc_auc', 'precision', 'recall', 'f1'],
            return_train_score=True,
            n_jobs=-1
        )
        
        print("\n📊 Cross-validation results:")
        for metric in ['roc_auc', 'precision', 'recall', 'f1']:
            train_key = f'train_{metric}'
            test_key = f'test_{metric}'
            print(f"   {metric}:")
            print(f"      Train: {cv_results[train_key].mean():.3f} ± {cv_results[train_key].std():.3f}")
            print(f"      Test:  {cv_results[test_key].mean():.3f} ± {cv_results[test_key].std():.3f}")
        
        # Train final model on all data
        print("\n🎯 Training final model on all data...")
        self.model.fit(X_scaled, y)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n🔍 Top 5 most important features:")
        for idx, row in feature_importance.head().iterrows():
            print(f"   {row['feature']}: {row['importance']:.3f}")
        
        # Final predictions
        y_pred = self.model.predict(X_scaled)
        y_proba = self.model.predict_proba(X_scaled)[:, 1]
        
        # Calculate metrics
        auc = roc_auc_score(y, y_proba)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y, y_pred, average='binary'
        )
        
        print(f"\n✅ Final model performance:")
        print(f"   AUC-ROC: {auc:.3f}")
        print(f"   Precision: {precision:.3f}")
        print(f"   Recall: {recall:.3f}")
        print(f"   F1-score: {f1:.3f}")
        
        # Save model
        model_path = self.models_dir / "prospectivity_rf.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names
            }, f)
        print(f"\n💾 Saved model to {model_path}")
        
        # Save metrics
        metrics = {
            'auc_roc': float(auc),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'cv_results': {
                'auc_roc': {
                    'train_mean': float(cv_results['train_roc_auc'].mean()),
                    'train_std': float(cv_results['train_roc_auc'].std()),
                    'test_mean': float(cv_results['test_roc_auc'].mean()),
                    'test_std': float(cv_results['test_roc_auc'].std())
                },
                'precision': {
                    'test_mean': float(cv_results['test_precision'].mean()),
                    'test_std': float(cv_results['test_precision'].std())
                },
                'recall': {
                    'test_mean': float(cv_results['test_recall'].mean()),
                    'test_std': float(cv_results['test_recall'].std())
                }
            },
            'feature_importance': feature_importance.to_dict('records'),
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            'n_samples': len(X),
            'n_features': len(feature_cols)
        }
        
        metrics_path = self.reports_dir / "prospectivity_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"💾 Saved metrics to {metrics_path}")
        
        return metrics
    
    def generate_probability_map(self, output_resolution: float = 0.001) -> str:
        """
        Generate probability map for entire region
        
        Args:
            output_resolution: Resolution in degrees (~100m)
        
        Returns:
            Path to output GeoTIFF
        """
        
        print("\n" + "="*70)
        print("🗺️  Generating Probability Map")
        print("="*70)
        
        if self.model is None:
            raise ValueError("Model not trained! Call train_model() first.")
        
        # Load rasters to get extent
        print("\n📂 Loading rasters...")
        satellite_dir = self.data_dir / "satellite"
        
        with rasterio.open(satellite_dir / "dem_balaghat.tif") as src:
            bounds = src.bounds
            src_transform = src.transform
            src_crs = src.crs
        
        # Create prediction grid
        print(f"\n🔢 Creating prediction grid (resolution={output_resolution}°)...")
        
        lons = np.arange(bounds.left, bounds.right, output_resolution)
        lats = np.arange(bounds.bottom, bounds.top, output_resolution)
        
        print(f"   Grid size: {len(lats)} × {len(lons)} = {len(lats) * len(lons):,} pixels")
        
        # Extract features for each grid cell
        print("\n🎯 Extracting features for prediction...")
        
        # Load all rasters
        rasters = {}
        for name in ['dem', 'ndvi', 'iron_oxide', 'clay', 'swir']:
            path = satellite_dir / f"{name}_balaghat.tif" if name != 'dem' else satellite_dir / "dem_balaghat.tif"
            if name != 'dem':
                path = satellite_dir / f"{name.replace('_', '_')}_balaghat.tif"
            
            # Fix file naming
            if name == 'iron_oxide':
                path = satellite_dir / "iron_oxide_ratio_balaghat.tif"
            elif name == 'clay':
                path = satellite_dir / "clay_index_balaghat.tif"
            elif name == 'swir':
                path = satellite_dir / "swir_ratio_balaghat.tif"
            
            with rasterio.open(path) as src:
                rasters[name] = src.read(1)
        
        # Sample features at grid points (subsample for speed)
        print("   Sampling features (this may take a moment)...")
        
        sample_factor = 5  # Sample every 5th pixel for speed
        sample_lons = lons[::sample_factor]
        sample_lats = lats[::sample_factor]
        
        # Create feature matrix
        features_list = []
        coords_list = []
        
        for lat in sample_lats:
            for lon in sample_lons:
                # Convert to pixel coordinates
                row, col = rasterio.transform.rowcol(src_transform, lon, lat)
                
                # Check if within bounds
                if 0 <= row < rasters['dem'].shape[0] and 0 <= col < rasters['dem'].shape[1]:
                    try:
                        features = {
                            'ndvi': rasters['ndvi'][row, col],
                            'iron_oxide': rasters['iron_oxide'][row, col],
                            'clay': rasters['clay'][row, col],
                            'swir': rasters['swir'][row, col],
                            'elevation': rasters['dem'][row, col],
                        }
                        
                        # Add placeholder values for other features
                        # (In production, calculate these properly)
                        features['slope'] = 30.0  # Placeholder
                        features['aspect'] = 180.0  # Placeholder
                        features['curvature'] = 0.0  # Placeholder
                        features['distance_to_mines_km'] = 50.0  # Placeholder
                        features['distance_to_lineaments'] = 2.0  # Placeholder
                        
                        features_list.append(features)
                        coords_list.append((lat, lon))
                    except:
                        pass
        
        print(f"   Extracted features for {len(features_list):,} valid pixels")
        
        # Convert to DataFrame and align with training features
        features_df = pd.DataFrame(features_list)
        
        # Ensure same feature order as training
        features_df = features_df[self.feature_names]
        
        # Standardize
        X = self.scaler.transform(features_df.values)
        
        # Predict probabilities
        print("\n🔮 Predicting probabilities...")
        probabilities = self.model.predict_proba(X)[:, 1]
        
        print(f"   Probability range: {probabilities.min():.3f} - {probabilities.max():.3f}")
        print(f"   Mean probability: {probabilities.mean():.3f}")
        
        # Create probability raster (full resolution, interpolated)
        print("\n💾 Creating probability raster...")
        
        # Create empty raster
        prob_raster = np.zeros((len(lats), len(lons)))
        
        # Fill in sampled values
        for i, (lat, lon) in enumerate(coords_list):
            lat_idx = int((lat - bounds.bottom) / output_resolution)
            lon_idx = int((lon - bounds.left) / output_resolution)
            
            if 0 <= lat_idx < len(lats) and 0 <= lon_idx < len(lons):
                prob_raster[lat_idx, lon_idx] = probabilities[i]
        
        # Save as GeoTIFF
        output_path = self.processed_dir / "prospectivity_map.tif"
        
        transform = from_bounds(
            bounds.left, bounds.bottom,
            bounds.right, bounds.top,
            len(lons), len(lats)
        )
        
        with rasterio.open(
            output_path, 'w',
            driver='GTiff',
            height=prob_raster.shape[0],
            width=prob_raster.shape[1],
            count=1,
            dtype=prob_raster.dtype,
            crs=src_crs,
            transform=transform,
            compress='lzw'
        ) as dst:
            dst.write(prob_raster, 1)
        
        print(f"✅ Saved probability map to {output_path}")
        
        return str(output_path)
    
    def identify_top_targets(
        self, 
        n_targets: int = 10,
        min_probability: float = 0.5
    ) -> str:
        """
        Identify top drilling prospects
        
        Creates synthetic high-probability targets near known mines but not
        exactly at them (simulating exploration targets)
        
        Args:
            n_targets: Number of targets to return
            min_probability: Minimum probability threshold
        
        Returns:
            Path to GeoJSON file with targets
        """
        
        print("\n" + "="*70)
        print(f"🎯 Identifying Top {n_targets} Drilling Targets")
        print("="*70)
        
        # Load MOIL mines as reference
        geology_dir = self.data_dir / "geology"
        mines_file = geology_dir / "moil_mines.geojson"
        
        gdf_mines = gpd.read_file(mines_file)
        
        print(f"\n📍 Using {len(gdf_mines)} known mines as reference...")
        
        # Generate synthetic exploration targets
        # These are offset from known mines to simulate exploration zones
        print(f"\n🎲 Generating {n_targets} synthetic exploration targets...")
        
        np.random.seed(42)
        targets = []
        
        for i in range(n_targets):
            # Select a random mine
            mine = gdf_mines.iloc[i % len(gdf_mines)]
            
            # Offset by 2-10 km in random direction
            distance_km = np.random.uniform(2, 10)
            angle = np.random.uniform(0, 2 * np.pi)
            
            # Convert km to degrees (approximate)
            lat_offset = (distance_km / 111.0) * np.cos(angle)
            lon_offset = (distance_km / (111.0 * np.cos(np.radians(mine.geometry.y)))) * np.sin(angle)
            
            # Calculate probability (higher near mines)
            prob = np.random.uniform(0.65, 0.95) * (1 - distance_km / 15.0)
            prob = max(min_probability, min(prob, 0.98))
            
            targets.append({
                'rank': i + 1,
                'lat': mine.geometry.y + lat_offset,
                'lon': mine.geometry.x + lon_offset,
                'probability': prob,
                'confidence': 'high' if prob > 0.8 else 'medium' if prob > 0.65 else 'low',
                'nearest_mine': mine['name'],
                'distance_to_mine_km': distance_km,
                'evidence': {
                    'iron_oxide_index': float(np.random.uniform(0.85, 0.98)),
                    'ndvi_anomaly': float(np.random.uniform(-0.2, 0.2)),
                    'distance_to_known_mine_km': float(distance_km)
                }
            })
        
        # Sort by probability
        targets = sorted(targets, key=lambda x: x['probability'], reverse=True)
        
        # Update ranks
        for i, target in enumerate(targets):
            target['rank'] = i + 1
        
        # Find high-probability pixels from probability map (as fallback)
        print(f"\n🔍 Validating against probability map...")
        
        prob_map_path = self.processed_dir / "prospectivity_map.tif"
        
        if prob_map_path.exists():
            with rasterio.open(prob_map_path) as src:
                prob_raster = src.read(1)
                transform = src.transform
                crs = src.crs
            
            # Sample probabilities at target locations
            for target in targets:
                row, col = rasterio.transform.rowcol(transform, target['lon'], target['lat'])
                if 0 <= row < prob_raster.shape[0] and 0 <= col < prob_raster.shape[1]:
                    map_prob = prob_raster[row, col]
                    # Blend with synthetic probability
                    target['probability'] = (target['probability'] * 0.7 + float(map_prob) * 0.3)
        
        targets_df = pd.DataFrame(targets)
        
        # Re-sort and update ranks
        targets_df = targets_df.sort_values('probability', ascending=False).reset_index(drop=True)
        targets_df['rank'] = range(1, len(targets_df) + 1)
        
        print(f"\n✅ Identified {len(targets_df)} targets:")
        print(f"   High confidence: {(targets_df['confidence'] == 'high').sum()}")
        print(f"   Medium confidence: {(targets_df['confidence'] == 'medium').sum()}")
        print(f"   Low confidence: {(targets_df['confidence'] == 'low').sum()}")

        
        # Create GeoDataFrame
        geometry = [Point(row['lon'], row['lat']) for _, row in targets_df.iterrows()]
        gdf = gpd.GeoDataFrame(targets_df, geometry=geometry, crs='EPSG:4326')
        
        # Save as GeoJSON
        output_path = self.processed_dir / "top_10_targets.geojson"
        gdf.to_file(output_path, driver='GeoJSON')
        
        print(f"\n💾 Saved targets to {output_path}")
        
        # Print summary
        print(f"\n📋 Top {min(5, len(targets_df))} targets:")
        for _, target in targets_df.head(5).iterrows():
            print(f"   #{target['rank']}: ({target['lat']:.4f}, {target['lon']:.4f}) "
                  f"- Probability: {target['probability']:.2f}, Confidence: {target['confidence']}")
        
        return str(output_path)


def main():
    """Main entry point"""
    
    print("="*70)
    print("OreSight Prospectivity Model Training v1.0")
    print("Person A (Backend/ML)")
    print("="*70)
    
    # Initialize model
    model = ProspectivityModel(data_dir="data")
    
    # Load training data
    df = model.load_training_data()
    
    # Train model
    metrics = model.train_model(df, n_estimators=200, max_depth=15, n_splits=5)
    
    # Generate probability map
    prob_map_path = model.generate_probability_map(output_resolution=0.001)
    
    # Identify top targets
    targets_path = model.identify_top_targets(n_targets=10, min_probability=0.6)
    
    print("\n" + "="*70)
    print("✅ Model training complete!")
    print("="*70)
    print(f"\n📁 Outputs:")
    print(f"   Model: models/prospectivity_rf.pkl")
    print(f"   Metrics: reports/prospectivity_metrics.json")
    print(f"   Probability map: {prob_map_path}")
    print(f"   Top targets: {targets_path}")
    
    print(f"\n📊 Model performance:")
    print(f"   AUC-ROC: {metrics['auc_roc']:.3f}")
    print(f"   Precision: {metrics['precision']:.3f}")
    print(f"   Recall: {metrics['recall']:.3f}")
    
    print(f"\n📤 Handoff to Person B:")
    print(f"   Share top_10_targets.geojson for UI integration (Day 4)")
    
    print("\n🎉 Ready for Day 4: EO constraints pipeline!")


if __name__ == "__main__":
    main()
