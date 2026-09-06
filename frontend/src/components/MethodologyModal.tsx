import { useState } from "react";

type Tab = "forecast" | "prospectivity" | "ear" | "actions" | "data";

interface MethodologyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function MethodologyModal({ isOpen, onClose }: MethodologyModalProps) {
  const [activeTab, setActiveTab] = useState<Tab>("forecast");

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-lg border border-gray-600 bg-gray-900 p-6">
        {/* Header */}
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white">Methodology & Assumptions</h1>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-200 transition-colors text-2xl"
          >
            ✕
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="mb-6 flex flex-wrap gap-2 border-b border-gray-600/50 pb-4">
          {[
            { id: "forecast", label: "Production Forecast" },
            { id: "prospectivity", label: "Reserve Identification" },
            { id: "ear", label: "Effective Accessible Reserve" },
            { id: "actions", label: "Action Optimization" },
            { id: "data", label: "Data Sources" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as Tab)}
              className={`px-3 py-2 text-xs font-medium rounded transition-colors ${
                activeTab === tab.id
                  ? "bg-blue-600/80 text-white"
                  : "bg-gray-700/50 text-gray-300 hover:bg-gray-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="space-y-4 text-sm text-gray-200">
          {activeTab === "forecast" && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-white">Production Forecast Model</h2>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Algorithm</h3>
                <p className="text-gray-300 mb-2">
                  LightGBM (Light Gradient Boosting Machine) — a fast, distributed gradient boosting framework optimized for production forecasting with irregular time series.
                </p>
                <ul className="space-y-1 text-xs text-gray-400">
                  <li>• <strong>Why LightGBM:</strong> Handles non-linear rainfall-production relationships without overfitting</li>
                  <li>• <strong>Training:</strong> 90-day rolling window of historical production + rainfall data</li>
                  <li>• <strong>Validation:</strong> K-fold cross-validation on 20% hold-out test set</li>
                </ul>
              </div>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Input Features</h3>
                <ul className="space-y-1 text-xs text-gray-400">
                  <li>• <strong>Rainfall (mm):</strong> Preceding 30-day cumulative, extracted from Sentinel-1/2</li>
                  <li>• <strong>Equipment downtime:</strong> DGMS-reported hours of equipment unavailability</li>
                  <li>• <strong>Seasonal factor:</strong> Monsoon indicator (binary: monsoon vs. non-monsoon)</li>
                  <li>• <strong>Lagged production:</strong> Previous 3 days' output (captures operational momentum)</li>
                  <li>• <strong>Soil moisture:</strong> Derived from Sentinel-1 VV/VH ratio</li>
                </ul>
              </div>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Output Interpretation</h3>
                <ul className="space-y-1 text-xs text-gray-400">
                  <li>• <strong>P10/P50/P90:</strong> 10th, 50th, 90th percentile of production forecast</li>
                  <li>• <strong>Shortfall probability:</strong> % chance production will fall below monthly target</li>
                  <li>• <strong>SHAP drivers:</strong> Feature importance ranked by actual prediction contribution</li>
                </ul>
              </div>

              <div className="rounded border border-yellow-600/40 bg-yellow-600/10 p-2">
                <p className="text-xs text-yellow-300">
                  ⚠️ <strong>Limitation:</strong> Model assumes historical patterns persist. Extreme weather, major equipment changes, or policy shifts require manual model retraining.
                </p>
              </div>
            </div>
          )}

          {activeTab === "prospectivity" && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-white">Reserve Prospectivity Mapping</h2>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Objective</h3>
                <p className="text-gray-300">
                  Identify new manganese mineral prospects using Random Forest classification on multi-source satellite and geological data. Objective: AUC-ROC &gt; 0.75 on hold-out test set.
                </p>
              </div>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Training Data</h3>
                <ul className="space-y-1 text-xs text-gray-400">
                  <li>• <strong>Positive samples:</strong> Known MOIL mine locations + GSI manganese occurrences</li>
                  <li>• <strong>Negative samples:</strong> Random background points (50 km buffer to known mines)</li>
                  <li>• <strong>Spatial validation:</strong> Leave-one-mine-out to prevent overfitting</li>
                </ul>
              </div>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Feature Set</h3>
                <ul className="space-y-1 text-xs text-gray-400">
                  <li>• <strong>Spectral indices (Sentinel-2):</strong> SWIR band ratios, iron oxide index, clay index</li>
                  <li>• <strong>NDVI:</strong> Vegetation stress (geobotanical indicator)</li>
                  <li>• <strong>SAR texture (Sentinel-1):</strong> Surface roughness from VV/VH coherence</li>
                  <li>• <strong>Lineaments:</strong> Extracted via Sobel edge detection on DEM; distance-weighted</li>
                  <li>• <strong>Geology:</strong> GSI lithological classes (proxy for host rock)</li>
                  <li>• <strong>Topography:</strong> Slope, elevation, drainage patterns from SRTM DEM</li>
                </ul>
              </div>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Output</h3>
                <ul className="space-y-1 text-xs text-gray-400">
                  <li>• <strong>Prospectivity score (0–1):</strong> Probability of manganese mineralization</li>
                  <li>• <strong>Confidence interval:</strong> Derived from Random Forest prediction variance</li>
                  <li>• <strong>Feature contribution:</strong> Which evidence layer drives each target</li>
                  <li>• <strong>Heatmap:</strong> Spatial prospectivity grid for visualization</li>
                </ul>
              </div>

              <div className="rounded border border-yellow-600/40 bg-yellow-600/10 p-2">
                <p className="text-xs text-yellow-300">
                  ⚠️ <strong>Caveat:</strong> Prospectivity is statistical estimation, not geology. All recommendations must be validated by field investigation and DGMS-approved exploration surveys.
                </p>
              </div>
            </div>
          )}

          {activeTab === "ear" && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-white">Effective Accessible Reserve (EAR)</h2>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Concept</h3>
                <p className="text-gray-300 mb-2">
                  EAR = Geological Reserve × ∏(Accessibility Factors)
                </p>
                <p className="text-gray-300">
                  Bridges geological estimates with operational reality by applying multipliers for depth, equipment, climate, regulatory, and infrastructure constraints.
                </p>
              </div>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Accessibility Factors</h3>
                <ul className="space-y-2 text-xs text-gray-400">
                  <li>
                    <strong>Depth Factor (0.5–1.0):</strong> Blocks below current development level. Discount increases exponentially with depth (mining cost rises).
                  </li>
                  <li>
                    <strong>Equipment Factor (0.7–1.0):</strong> Equipment availability from CMMS logs + forecast failures. Lower when key LHD/dumpers are predicted to fail.
                  </li>
                  <li>
                    <strong>Climate Factor (0.6–1.0):</strong> Seasonal rainfall impact. Monsoon reduces accessibility; flood-prone blocks discounted year-round.
                  </li>
                  <li>
                    <strong>Regulatory Factor (0.6–1.0):</strong> DGMS limits, forest regulations. Blocks in protected areas heavily discounted.
                  </li>
                  <li>
                    <strong>Infrastructure Factor (0.7–1.0):</strong> Distance to haul roads, processing capacity. Blocks far from current haul network carry penalty.
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Usage in Production Planning</h3>
                <ul className="space-y-1 text-xs text-gray-400">
                  <li>• Annual mining plan targets should not exceed monthly EAR average</li>
                  <li>• Equipment investments increase Equipment Factor → EAR increases</li>
                  <li>• Infrastructure (new haul roads) increases Infrastructure Factor</li>
                  <li>• Dynamic EAR sliders allow scenario planning ("What if…")</li>
                </ul>
              </div>

              <div className="rounded border border-yellow-600/40 bg-yellow-600/10 p-2">
                <p className="text-xs text-yellow-300">
                  ⚠️ <strong>Disclosure:</strong> EAR factors are estimated from historical data and satellite indices. Final reserve classification should follow UNFC / MCDR standards for statutory reporting.
                </p>
              </div>
            </div>
          )}

          {activeTab === "actions" && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-white">Corrective Actions</h2>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Optimization Strategy</h3>
                <p className="text-gray-300 mb-2">
                  When a shortfall is forecasted, suggest a bundle of actions that maximizes Δtonnes within budget and equipment constraints.
                </p>
                <ul className="space-y-1 text-xs text-gray-400">
                  <li>• Algorithm: Integer Linear Programming (ILP) via PuLP or Google OR-Tools</li>
                  <li>• Objective: Maximize ∑(Δtonnes) − ∑(cost), subject to budget &amp; equipment limits</li>
                  <li>• Each action has: base effectiveness, cost, lead time, equipment required</li>
                </ul>
              </div>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Sample Actions</h3>
                <ul className="space-y-1 text-xs text-gray-400">
                  <li>• <strong>Extra shift:</strong> +200–300 tonnes, ₹50k cost, 1-day lead time</li>
                  <li>• <strong>Equipment redeploy:</strong> +150–250 tonnes, ₹30k cost, 3-day lead time</li>
                  <li>• <strong>Advance blast schedule:</strong> +100–200 tonnes, ₹15k cost, 2-day lead time</li>
                  <li>• <strong>Third-party contract:</strong> +500–800 tonnes, ₹200k cost, 5-day lead time</li>
                </ul>
              </div>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Effectiveness Multipliers</h3>
                <p className="text-gray-300 text-xs mb-2">
                  Each action's effectiveness is adjusted based on current operational context:
                </p>
                <ul className="space-y-1 text-xs text-gray-400">
                  <li>• Heavy rain? Equipment-dependent actions lose 20% effectiveness</li>
                  <li>• Low equipment availability? Extra shift is ineffective</li>
                  <li>• High soil moisture? Haul road delays reduce action effectiveness</li>
                </ul>
              </div>

              <div className="rounded border border-yellow-600/40 bg-yellow-600/10 p-2">
                <p className="text-xs text-yellow-300">
                  ⚠️ <strong>Important:</strong> Recommendations are decision-support, not prescriptive. Final action approval remains with mine management.
                </p>
              </div>
            </div>
          )}

          {activeTab === "data" && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-white">Data Sources & Attribution</h2>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Satellite Data</h3>
                <ul className="space-y-2 text-xs text-gray-400">
                  <li>
                    <strong>Sentinel-2 (ESA):</strong> 10-20 m multispectral imagery. Public, free. Hosted on AWS/GCP.
                    <br />Source: https://sentinel.esa.int/web/sentinel/missions/sentinel-2
                  </li>
                  <li>
                    <strong>Sentinel-1 (ESA):</strong> C-band SAR, 10 m resolution. All-weather, penetrates clouds.
                    <br />Source: https://sentinel.esa.int/web/sentinel/missions/sentinel-1
                  </li>
                  <li>
                    <strong>Landsat 8/9 (USGS):</strong> Thermal bands for LST calculation.
                    <br />Source: https://www.usgs.gov/landsat
                  </li>
                  <li>
                    <strong>SRTM DEM (NASA):</strong> 30 m digital elevation model for lineament extraction.
                    <br />Source: https://lpdaac.usgs.gov/products/srtmgl1v003/
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Geological Data</h3>
                <ul className="space-y-1 text-xs text-gray-400">
                  <li>• <strong>GSI 1:2.5M Geological Map:</strong> Lithology, structural lineaments (OpenGov). Via Bhukosh portal.</li>
                  <li>• <strong>MOIL Manganese Occurrences:</strong> Known mine locations (public regulatory filings).</li>
                </ul>
              </div>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Operational Data</h3>
                <ul className="space-y-1 text-xs text-gray-400">
                  <li>• <strong>Production logs:</strong> Daily tonnage from mine SCADA / manual records</li>
                  <li>• <strong>Equipment CMMS:</strong> Maintenance logs, downtime hours (site-specific)</li>
                  <li>• <strong>Rainfall:</strong> IMD weather station data + satellite rainfall estimation (IMERG)</li>
                </ul>
              </div>

              <div>
                <h3 className="font-medium text-blue-400 mb-2">Data Integrity</h3>
                <ul className="space-y-1 text-xs text-gray-400">
                  <li>✅ All satellite datasets are orthorectified and time-stamped</li>
                  <li>✅ Outliers checked via IQR method (values outside 1.5×IQR removed)</li>
                  <li>✅ Missing satellite data: 90-day median composite imputation</li>
                  <li>✅ Production data: Validated against DGMS monthly returns</li>
                </ul>
              </div>

              <div className="rounded border border-green-600/40 bg-green-600/10 p-2">
                <p className="text-xs text-green-300">
                  ✓ <strong>Open Source:</strong> All processing scripts are version-controlled and available on GitHub. No proprietary black boxes.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
