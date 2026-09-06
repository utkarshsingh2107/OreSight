"""
Feature Engineering for Prospectivity Analysis

Extracts features from satellite imagery and DEM for ML-based mineral
prospectivity mapping.

Features extracted:
1. Spectral indices (NDVI, iron oxide ratio, clay index, SWIR ratio)
2. Topographic features (slope, aspect, curvature)
3. Distance features (to known mines, to lineaments via Canny edge detection)
4. SAE latent features — 4-dimensional learned representation of all 5 raster
   bands, trained using a Stacked Autoencoder (inspired by:
   Nagar et al. 2024, "Remote sensing framework for geological mapping via
   stacked autoencoders and clustering", Advances in Space Research).

The SAE latent vectors replace the placeholder constants that were previously
used during full-raster inference in prospectivity.py, so the probability map
is now computed from real pixel-level learned representations.

Author: Person A (Backend/ML)
Date: 2024
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from scipy import ndimage
from scipy.ndimage import distance_transform_edt
from scipy.spatial.distance import cdist
from sklearn.preprocessing import minmax_scale, StandardScaler
import json
import warnings
warnings.filterwarnings('ignore')


# ---------------------------------------------------------------------------
# SAE helper
# ---------------------------------------------------------------------------

def _build_stacked_autoencoder(input_dim: int, latent_dim: int = 4):
    """
    Build a 3-stage Stacked Autoencoder following the architecture used in
    Nagar et al. (2024) for multispectral geological mapping.

    Stage 1 : input_dim → 8 → latent_dim/2 → 8 → input_dim
    Stage 2 : (stage1_output + input) → 10 → 5 → 10 → ...
    Stage 3 : (stage2_latent + stage2_input) → 14 → latent_dim → 14 → ...

    The final encoder of stage 3 produces `latent_dim`-dimensional vectors.

    Returns
    -------
    autoencoder_1, encoder_1,
    autoencoder_2, encoder_2,
    autoencoder_3, encoder_3
    """
    try:
        from tensorflow.keras.layers import Input, Dense
        from tensorflow.keras.models import Model
        from tensorflow.keras.regularizers import l1
    except ImportError as exc:
        raise ImportError(
            "TensorFlow is required for SAE features. "
            "Install it with:  pip install tensorflow"
        ) from exc

    lr = 1e-4
    half = max(2, latent_dim // 2)

    # ---- Stage 1 --------------------------------------------------------
    inp1 = Input(shape=(input_dim,), name="sae_s1_input")
    e1 = Dense(8,          activation='selu', activity_regularizer=l1(lr))(inp1)
    code1 = Dense(half,    activation='selu', activity_regularizer=l1(lr))(e1)
    d1 = Dense(8,          activation='selu', activity_regularizer=l1(lr))(code1)
    out1 = Dense(input_dim, activation='sigmoid', activity_regularizer=l1(lr))(d1)

    ae1 = Model(inp1, out1, name="sae_ae1")
    ae1.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
    enc1 = Model(inp1, code1, name="sae_enc1")

    # ---- Stage 2 --------------------------------------------------------
    stage2_dim = input_dim + half       # concatenated input
    inp2 = Input(shape=(stage2_dim,), name="sae_s2_input")
    e2 = Dense(10,         activation='selu', activity_regularizer=l1(lr))(inp2)
    code2 = Dense(5,       activation='selu', activity_regularizer=l1(lr))(e2)
    d2 = Dense(10,         activation='selu', activity_regularizer=l1(lr))(code2)
    out2 = Dense(stage2_dim, activation='sigmoid', activity_regularizer=l1(lr))(d2)

    ae2 = Model(inp2, out2, name="sae_ae2")
    ae2.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
    enc2 = Model(inp2, code2, name="sae_enc2")

    # ---- Stage 3 --------------------------------------------------------
    stage3_dim = stage2_dim + 5         # concatenated input
    inp3 = Input(shape=(stage3_dim,), name="sae_s3_input")
    e3a = Dense(14,        activation='selu', activity_regularizer=l1(lr))(inp3)
    e3b = Dense(10,        activation='selu', activity_regularizer=l1(lr))(e3a)
    code3 = Dense(latent_dim, activation='selu', activity_regularizer=l1(lr))(e3b)
    d3a = Dense(10,        activation='selu', activity_regularizer=l1(lr))(code3)
    d3b = Dense(14,        activation='selu', activity_regularizer=l1(lr))(d3a)
    out3 = Dense(stage3_dim, activation='sigmoid', activity_regularizer=l1(lr))(d3b)

    ae3 = Model(inp3, out3, name="sae_ae3")
    ae3.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
    enc3 = Model(inp3, code3, name="sae_enc3")

    return ae1, enc1, ae2, enc2, ae3, enc3


def compute_sae_latent_features(
    raster_stack: np.ndarray,
    latent_dim: int = 4,
    epochs_s1: int = 20,
    epochs_s2: int = 10,
    epochs_s3: int = 10,
    batch_size: int = 512,
    verbose: int = 0,
) -> np.ndarray:
    """
    Flatten all pixels, minmax-scale the 5-band stack, train a 3-stage Stacked
    Autoencoder, and return the latent representation.

    Parameters
    ----------
    raster_stack : ndarray of shape (n_bands, height, width)
        The 5-band satellite raster stack (dem, ndvi, iron_oxide, clay, swir).
    latent_dim : int
        Size of the final bottleneck (default 4).
    epochs_s1/s2/s3 : int
        Training epochs per stage.
    batch_size : int
        Mini-batch size.
    verbose : int
        Keras verbosity (0 = silent).

    Returns
    -------
    latent : ndarray of shape (height * width, latent_dim)
        Per-pixel latent vectors, same pixel order as raster_stack.flatten().
    """
    n_bands, height, width = raster_stack.shape
    n_pixels = height * width

    # Reshape to (n_pixels, n_bands) and minmax-scale per band
    data = raster_stack.reshape(n_bands, n_pixels).T          # (N, 5)
    data = minmax_scale(data, feature_range=(0, 1), axis=0)   # scale per column

    ae1, enc1, ae2, enc2, ae3, enc3 = _build_stacked_autoencoder(
        input_dim=n_bands, latent_dim=latent_dim
    )

    print(f"   [SAE] Stage 1  ({n_bands}→{max(2, latent_dim//2)}→{n_bands})  …", end=" ")
    ae1.fit(data, data, epochs=epochs_s1, batch_size=batch_size, verbose=verbose)
    stage1_out = ae1.predict(data, verbose=0)
    print("done")

    stage2_in = np.concatenate([stage1_out, data], axis=1)
    print(f"   [SAE] Stage 2  ({stage2_in.shape[1]}→5→{stage2_in.shape[1]})  …", end=" ")
    ae2.fit(stage2_in, stage2_in, epochs=epochs_s2, batch_size=batch_size, verbose=verbose)
    stage2_latent = enc2.predict(stage2_in, verbose=0)
    print("done")

    stage3_in = np.concatenate([stage2_latent, stage2_in], axis=1)
    print(f"   [SAE] Stage 3  ({stage3_in.shape[1]}→{latent_dim}→{stage3_in.shape[1]})  …", end=" ")
    ae3.fit(stage3_in, stage3_in, epochs=epochs_s3, batch_size=batch_size, verbose=verbose)
    latent = enc3.predict(stage3_in, verbose=0)
    print("done")

    print(f"   [SAE] Latent shape: {latent.shape}  "
          f"range=[{latent.min():.3f}, {latent.max():.3f}]")

    return latent          # (N, latent_dim)


# ---------------------------------------------------------------------------
# Main feature extractor
# ---------------------------------------------------------------------------

class ProspectivityFeatureExtractor:
    """Extract features from satellite and geological data for prospectivity modeling"""

    def __init__(self, data_dir: str = "data"):
        """Initialize feature extractor"""
        self.data_dir = Path(data_dir)
        self.satellite_dir = self.data_dir / "satellite"
        self.geology_dir   = self.data_dir / "geology"
        self.processed_dir = self.data_dir / "processed"

        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # Loaded rasters
        self.rasters = {}
        self.transform = None
        self.crs = None

        # SAE latent grid — filled by _compute_sae_latent_grid()
        # shape: (height, width, latent_dim)
        self._sae_latent_grid: Optional[np.ndarray] = None

        print("✅ Initialized ProspectivityFeatureExtractor")
        print(f"   Data directory: {self.data_dir.absolute()}")

    # ------------------------------------------------------------------
    # Raster loading
    # ------------------------------------------------------------------

    def load_rasters(self) -> Dict[str, np.ndarray]:
        """Load all satellite rasters into memory"""

        print("\n📂 Loading raster data...")

        raster_files = {
            'dem':        'dem_balaghat.tif',
            'ndvi':       'ndvi_balaghat.tif',
            'iron_oxide': 'iron_oxide_ratio_balaghat.tif',
            'clay':       'clay_index_balaghat.tif',
            'swir':       'swir_ratio_balaghat.tif',
        }

        for name, filename in raster_files.items():
            filepath = self.satellite_dir / filename

            if not filepath.exists():
                print(f"⚠️  {filepath} not found, skipping")
                continue

            with rasterio.open(filepath) as src:
                data = src.read(1)
                self.rasters[name] = data

                if self.transform is None:
                    self.transform = src.transform
                    self.crs = src.crs

                print(f"   ✓ Loaded {name}: {data.shape}, "
                      f"range=[{data.min():.2f}, {data.max():.2f}]")

        print(f"✅ Loaded {len(self.rasters)} rasters")
        return self.rasters

    # ------------------------------------------------------------------
    # Topographic derivatives
    # ------------------------------------------------------------------

    def calculate_slope_aspect(
        self, dem: np.ndarray, resolution: float = 100
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate slope and aspect from DEM"""

        print("\n🗻 Calculating topographic features...")

        dy, dx = np.gradient(dem, resolution)

        slope  = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))
        aspect = np.degrees(np.arctan2(-dx, dy))
        aspect = (aspect + 360) % 360

        print(f"   ✓ Slope:  min={slope.min():.2f}°, max={slope.max():.2f}°, "
              f"mean={slope.mean():.2f}°")
        print(f"   ✓ Aspect: range=[0°, 360°]")

        return slope, aspect

    def calculate_curvature(
        self, dem: np.ndarray, resolution: float = 100
    ) -> np.ndarray:
        """Calculate profile curvature from DEM"""

        d2y = ndimage.laplace(dem)
        curvature = d2y / (resolution ** 2)

        print(f"   ✓ Curvature: min={curvature.min():.6f}, max={curvature.max():.6f}")

        return curvature

    # ------------------------------------------------------------------
    # Lineament detection  (IMPROVED — Canny edge detection)
    # ------------------------------------------------------------------

    def detect_lineaments(
        self,
        dem: np.ndarray,
        sigma: float = 2.0,
    ) -> np.ndarray:
        """
        Detect lineaments using Canny edge detection on the DEM.

        Canny produces cleaner, single-pixel-wide edges compared to the
        previous gradient-magnitude threshold, which picked up noise.
        Replaced skimage dependency with a pure scipy/numpy implementation
        so no additional install is required.

        Parameters
        ----------
        dem    : 2-D array (DEM values)
        sigma  : Gaussian smoothing sigma before gradient computation

        Returns
        -------
        Binary edge mask (1 = lineament pixel, 0 = background)
        """

        print("\n🔍 Detecting lineaments (Canny-style edge detection)…")

        # 1. Gaussian smoothing
        smoothed = ndimage.gaussian_filter(dem, sigma=sigma)

        # 2. Sobel gradients
        sx = ndimage.sobel(smoothed, axis=1).astype(float)
        sy = ndimage.sobel(smoothed, axis=0).astype(float)
        magnitude = np.hypot(sx, sy)

        # 3. Non-maximum suppression (thin edges to 1-pixel width)
        angle = np.arctan2(sy, sx)          # [-π, π]
        # Quantise direction into 4 bins: 0°, 45°, 90°, 135°
        angle_deg = (np.degrees(angle) % 180)
        q_angle = np.round(angle_deg / 45) * 45
        q_angle[q_angle == 180] = 0

        suppressed = magnitude.copy()
        h, w = magnitude.shape

        def _neighbors(r, c, d):
            """Return the two neighbor magnitudes along direction d."""
            if d == 0:    return magnitude[r, min(c+1, w-1)], magnitude[r, max(c-1, 0)]
            if d == 45:   return magnitude[max(r-1,0), min(c+1,w-1)], magnitude[min(r+1,h-1), max(c-1,0)]
            if d == 90:   return magnitude[max(r-1, 0), c], magnitude[min(r+1, h-1), c]
            # 135
            return magnitude[max(r-1,0), max(c-1,0)], magnitude[min(r+1,h-1), min(c+1,w-1)]

        for r in range(1, h - 1):
            for c in range(1, w - 1):
                n1, n2 = _neighbors(r, c, q_angle[r, c])
                if magnitude[r, c] < n1 or magnitude[r, c] < n2:
                    suppressed[r, c] = 0

        # 4. Double-threshold hysteresis
        high = np.percentile(suppressed[suppressed > 0], 85)
        low  = high * 0.4
        strong = suppressed >= high
        weak   = (suppressed >= low) & (suppressed < high)

        # Connect weak pixels adjacent to strong ones
        struct = ndimage.generate_binary_structure(2, 2)
        strong_dilated = ndimage.binary_dilation(strong, structure=struct)
        edges = strong | (weak & strong_dilated)

        pct = edges.sum() / edges.size * 100
        print(f"   ✓ Detected lineaments: {edges.sum():,} pixels ({pct:.1f}%)")

        return edges.astype(float)

    # ------------------------------------------------------------------
    # Distance to mines
    # ------------------------------------------------------------------

    def calculate_distance_to_mines(self, shape: Tuple[int, int]) -> np.ndarray:
        """Calculate distance from each pixel to nearest known mine"""

        print("\n📍 Calculating distance to known mines...")

        mines_file = self.geology_dir / "moil_mines.geojson"

        if not mines_file.exists():
            print(f"⚠️  {mines_file} not found, returning zeros")
            return np.zeros(shape)

        gdf = gpd.read_file(mines_file)

        rows, cols = shape
        from rasterio.transform import xy as rast_xy

        lons_s, lats_s = [], []
        for r in range(0, rows, 10):
            for c in range(0, cols, 10):
                lon, lat = rast_xy(self.transform, r, c)
                lons_s.append(lon)
                lats_s.append(lat)

        grid_coords = np.column_stack([lats_s, lons_s])
        mine_coords = np.column_stack([gdf.geometry.y, gdf.geometry.x])

        distances     = cdist(grid_coords, mine_coords, metric='euclidean')
        min_distances = distances.min(axis=1)

        from scipy.interpolate import griddata
        sample_pts = [(r, c) for r in range(0, rows, 10) for c in range(0, cols, 10)]
        full_pts   = [(r, c) for r in range(rows) for c in range(cols)]

        distance_grid = griddata(
            sample_pts, min_distances, full_pts,
            method='linear', fill_value=min_distances.max()
        ).reshape(shape)

        distance_grid_km = distance_grid * 111

        print(f"   ✓ Distance range: {distance_grid_km.min():.2f} – "
              f"{distance_grid_km.max():.2f} km")
        print(f"   ✓ Using {len(gdf)} mine locations")

        return distance_grid_km

    # ------------------------------------------------------------------
    # SAE latent grid
    # ------------------------------------------------------------------

    def _compute_sae_latent_grid(
        self,
        latent_dim: int = 4,
        epochs_s1: int = 20,
        epochs_s2: int = 10,
        epochs_s3: int = 10,
        batch_size: int = 512,
    ) -> np.ndarray:
        """
        Train the SAE on the 5-band raster stack and store the latent
        representation as a (height, width, latent_dim) grid.

        Called once during run_pipeline(); the result is cached in
        self._sae_latent_grid so generate_probability_map() can use it
        without placeholder constants.

        Returns
        -------
        ndarray of shape (height, width, latent_dim)
        """

        band_order = ['dem', 'ndvi', 'iron_oxide', 'clay', 'swir']
        missing = [b for b in band_order if b not in self.rasters]
        if missing:
            raise ValueError(f"Missing rasters for SAE: {missing}")

        # Stack into (5, H, W)
        h, w = self.rasters['dem'].shape
        stack = np.stack([self.rasters[b] for b in band_order], axis=0)

        print("\n🤖 Training Stacked Autoencoder on 5-band raster stack…")
        print(f"   Raster size: {h}×{w} = {h*w:,} pixels, {stack.shape[0]} bands")

        latent_flat = compute_sae_latent_features(
            raster_stack=stack,
            latent_dim=latent_dim,
            epochs_s1=epochs_s1,
            epochs_s2=epochs_s2,
            epochs_s3=epochs_s3,
            batch_size=batch_size,
        )  # (H*W, latent_dim)

        self._sae_latent_grid = latent_flat.reshape(h, w, latent_dim)

        print(f"✅ SAE latent grid ready: shape={self._sae_latent_grid.shape}")
        return self._sae_latent_grid

    def get_sae_latent_at_pixel(self, row: int, col: int) -> Optional[np.ndarray]:
        """
        Return the SAE latent vector for a single pixel (row, col).
        Returns None if SAE has not been computed yet.
        """
        if self._sae_latent_grid is None:
            return None
        try:
            return self._sae_latent_grid[row, col, :]
        except IndexError:
            return None

    # ------------------------------------------------------------------
    # Point-level feature extraction
    # ------------------------------------------------------------------

    def extract_features_at_points(self, points_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
        """
        Extract all features at given point locations.

        If the SAE latent grid is available (populated by run_pipeline),
        `sae_0 … sae_{latent_dim-1}` columns are added to each row.
        """

        print(f"\n🎯 Extracting features at {len(points_gdf)} points...")

        features = []

        for idx, point in points_gdf.iterrows():
            lon, lat = point.geometry.x, point.geometry.y
            row, col = rasterio.transform.rowcol(self.transform, lon, lat)

            feature_dict = {'lat': lat, 'lon': lon}

            if 'label' in point:
                feature_dict['label'] = point['label']

            # Spectral
            for name in ['ndvi', 'iron_oxide', 'clay', 'swir']:
                if name in self.rasters:
                    try:    feature_dict[name] = float(self.rasters[name][row, col])
                    except: feature_dict[name] = np.nan

            # Topographic
            for name in ['elevation', 'slope', 'aspect', 'curvature']:
                raster_key = 'dem' if name == 'elevation' else name
                if raster_key in self.rasters:
                    try:    feature_dict[name] = float(self.rasters[raster_key][row, col])
                    except: feature_dict[name] = np.nan

            # Distance
            for feat, key in [('distance_to_mines_km', 'distance_to_mines'),
                               ('distance_to_lineaments', 'distance_to_lineaments')]:
                if key in self.rasters:
                    try:    feature_dict[feat] = float(self.rasters[key][row, col])
                    except: feature_dict[feat] = np.nan

            # SAE latent features
            latent = self.get_sae_latent_at_pixel(row, col)
            if latent is not None:
                for i, v in enumerate(latent):
                    feature_dict[f'sae_{i}'] = float(v)

            features.append(feature_dict)

        df = pd.DataFrame(features)

        # Remove rows with too many NaNs (>30% of columns)
        nan_ratio = df.isna().sum(axis=1) / len(df.columns)
        df = df[nan_ratio < 0.3].reset_index(drop=True)

        n_feat = len([c for c in df.columns if c not in ('lat', 'lon', 'label')])
        print(f"   ✓ Extracted {n_feat} features per point")
        print(f"   ✓ Valid samples: {len(df)} "
              f"(removed {len(features) - len(df)} with too many NaNs)")

        return df

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def run_pipeline(self, train_sae: bool = True, latent_dim: int = 4) -> pd.DataFrame:
        """
        Run complete feature extraction pipeline.

        Parameters
        ----------
        train_sae  : bool
            If True (default), train the SAE and add latent features.
            Set to False to skip SAE (faster, no TensorFlow required).
        latent_dim : int
            SAE bottleneck size (default 4).
        """

        print("=" * 70)
        print("🚀 Prospectivity Feature Extraction Pipeline")
        print("=" * 70)

        # Step 1: Load rasters
        self.load_rasters()

        if len(self.rasters) == 0:
            raise ValueError("No rasters loaded!")

        # Step 2: Topographic derivatives
        if 'dem' in self.rasters:
            slope, aspect = self.calculate_slope_aspect(self.rasters['dem'])
            self.rasters['slope']  = slope
            self.rasters['aspect'] = aspect

            curvature = self.calculate_curvature(self.rasters['dem'])
            self.rasters['curvature'] = curvature

            lineaments = self.detect_lineaments(self.rasters['dem'])
            dist_lin = distance_transform_edt(~lineaments.astype(bool))
            self.rasters['distance_to_lineaments'] = dist_lin

        # Step 3: Distance to mines
        shape = self.rasters['dem'].shape
        self.rasters['distance_to_mines'] = self.calculate_distance_to_mines(shape)

        # Step 4: SAE latent features
        if train_sae:
            try:
                self._compute_sae_latent_grid(latent_dim=latent_dim)
            except ImportError as e:
                print(f"⚠️  {e}")
                print("   Continuing without SAE features. "
                      "Install tensorflow to enable them.")
        else:
            print("\n⏩ Skipping SAE (train_sae=False)")

        print("\n⏩ Skipping texture features for speed (optional)")

        # Step 5: Load training labels
        labels_file = self.geology_dir / "training_labels.geojson"
        if not labels_file.exists():
            raise FileNotFoundError(f"{labels_file} not found!")

        labels_gdf = gpd.read_file(labels_file)
        print(f"\n📋 Loaded {len(labels_gdf)} training samples")

        # Step 6: Extract features at label points
        features_df = self.extract_features_at_points(labels_gdf)

        # Step 7: Save
        output_path = self.processed_dir / "prospectivity_features.parquet"
        features_df.to_parquet(output_path, index=False)

        feat_cols = [c for c in features_df.columns if c not in ('lat', 'lon', 'label')]
        print(f"\n✅ Saved features to {output_path}")
        print(f"   Shape: {features_df.shape}")
        print(f"   Features: {feat_cols}")

        self._print_summary(features_df)
        return features_df

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _print_summary(self, df: pd.DataFrame):
        """Print summary statistics"""

        print("\n" + "=" * 70)
        print("📊 Feature Summary")
        print("=" * 70)

        if 'label' in df.columns:
            pos = (df['label'] == 1).sum()
            neg = (df['label'] == 0).sum()
            print(f"\nClass distribution:")
            print(f"   Positive (near mines):     {pos}")
            print(f"   Negative (far from mines): {neg}")
            print(f"   Class balance: {pos / len(df) * 100:.1f}% positive")

        feature_cols = [c for c in df.columns if c not in ('lat', 'lon', 'label')]
        print(f"\nFeature statistics:")
        for col in feature_cols:
            print(f"   {col}: mean={df[col].mean():.3f}, std={df[col].std():.3f}, "
                  f"range=[{df[col].min():.3f}, {df[col].max():.3f}]")

        print("\n📋 Next steps:")
        print("   1. Review feature distributions")
        print("   2. Proceed to Day 3: Train prospectivity ML model")
        print("   3. Use ml/prism/prospectivity.py for model training")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    """Main entry point"""

    print("OreSight Prospectivity Feature Extractor v2.0")
    print("Improved with SAE latent features + Canny lineament detection\n")

    extractor = ProspectivityFeatureExtractor(data_dir="data")
    features_df = extractor.run_pipeline(train_sae=True, latent_dim=4)

    feat_count = len([c for c in features_df.columns if c not in ('lat', 'lon', 'label')])
    print(f"\n🎉 Feature extraction complete!")
    print(f"   Output:   data/processed/prospectivity_features.parquet")
    print(f"   Samples:  {len(features_df)}")
    print(f"   Features: {feat_count}")


if __name__ == "__main__":
    main()
