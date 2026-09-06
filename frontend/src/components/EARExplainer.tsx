import { useEffect, useState } from "react";
import { api } from "../api/client";

export interface EARData {
  geological_reserve_tonnes: number;
  depth_factor: number;
  equipment_factor: number;
  climate_factor: number;
  regulatory_factor: number;
  infrastructure_factor: number;
  total_ear_tonnes: number;
  blocks_at_risk: number;
  risk_description: string;
}

interface EARExplainerProps {
  mineId: number;
}

export default function EARExplainer({ mineId }: EARExplainerProps) {
  const [data, setData] = useState<EARData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Local state for slider adjustments
  const [depthFactor, setDepthFactor] = useState(1);
  const [equipmentFactor, setEquipmentFactor] = useState(1);
  const [climateFactor, setClimateFactor] = useState(1);
  const [regulatoryFactor, setRegulatoryFactor] = useState(1);
  const [infrastructureFactor, setInfrastructureFactor] = useState(1);

  useEffect(() => {
    setLoading(true);
    api
      .get<EARData>(`/ear`, { params: { mine_id: mineId } })
      .then((res) => {
        setData(res.data);
        // Initialize sliders with actual values
        setDepthFactor(res.data.depth_factor);
        setEquipmentFactor(res.data.equipment_factor);
        setClimateFactor(res.data.climate_factor);
        setRegulatoryFactor(res.data.regulatory_factor);
        setInfrastructureFactor(res.data.infrastructure_factor);
        setError(null);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || "Failed to load EAR data");
      })
      .finally(() => setLoading(false));
  }, [mineId]);

  if (loading) {
    return (
      <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
        <div className="h-64 animate-pulse rounded bg-gray-700/50" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
        <p className="text-sm text-gray-400">No EAR data available</p>
      </div>
    );
  }

  // Calculate dynamic EAR
  const dynamicEAR = 
    data.geological_reserve_tonnes *
    depthFactor *
    equipmentFactor *
    climateFactor *
    regulatoryFactor *
    infrastructureFactor;

  const earChange = dynamicEAR - data.total_ear_tonnes;
  const earChangePercent = (earChange / data.total_ear_tonnes) * 100;

  return (
    <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-3 md:p-4">
      <div className="mb-4">
        <h2 className="text-base md:text-lg font-semibold text-white">Effective Accessible Reserve (EAR)</h2>
        <p className="text-xs text-gray-400">
          Geological reserve × accessibility factors = achievable production
        </p>
      </div>

      {error && (
        <div className="mb-4 rounded border border-yellow-600/40 bg-yellow-600/10 p-2 text-xs text-yellow-300">
          {error}
        </div>
      )}

      {/* Main EAR Display */}
      <div className="mb-6 rounded-lg bg-gradient-to-br from-blue-600/20 to-purple-600/20 border border-blue-600/40 p-3 md:p-4">
        <div className="grid grid-cols-1 gap-3 md:gap-4">
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Geological Reserve</p>
            <p className="text-2xl md:text-3xl font-bold text-white">
              {(data.geological_reserve_tonnes / 1000).toFixed(1)}k
            </p>
            <p className="text-xs text-gray-500 mt-1">tonnes</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Effective Accessible Reserve</p>
            <p className="text-2xl md:text-3xl font-bold text-green-400">
              {(dynamicEAR / 1000).toFixed(1)}k
            </p>
            <p className={`text-xs mt-1 ${earChange >= 0 ? "text-green-400" : "text-red-400"}`}>
              {earChange >= 0 ? "+" : ""}{(earChange / 1000).toFixed(1)}k ({earChangePercent > 0 ? "+" : ""}{earChangePercent.toFixed(1)}%)
            </p>
          </div>
        </div>
      </div>

      {/* Risk Indicator */}
      {data.blocks_at_risk > 0 && (
        <div className="mb-6 rounded-lg border border-orange-600/40 bg-orange-600/10 p-3">
          <p className="text-xs font-medium text-orange-300 mb-1">⚠️ Blocks at Risk</p>
          <p className="text-xs text-orange-200">
            {data.blocks_at_risk} blocks with accessibility constraints
          </p>
          <p className="text-xs text-orange-300 mt-1">{data.risk_description}</p>
        </div>
      )}

      {/* Interactive Sliders - Responsive Grid */}
      <div className="space-y-3 md:space-y-4">
        <p className="text-xs md:text-sm font-medium text-gray-300">Adjust Factors (Move Sliders)</p>

        {/* Depth Factor */}
        <div>
          <div className="flex items-center justify-between mb-1 md:mb-2">
            <label className="text-xs font-medium text-gray-300">Depth Factor</label>
            <span className="text-xs font-mono text-blue-400">{depthFactor.toFixed(2)}x</span>
          </div>
          <input
            type="range"
            min="0.5"
            max="1"
            step="0.05"
            value={depthFactor}
            onChange={(e) => setDepthFactor(parseFloat(e.target.value))}
            className="w-full accent-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">Deep blocks discount</p>
        </div>

        {/* Equipment Factor */}
        <div>
          <div className="flex items-center justify-between mb-1 md:mb-2">
            <label className="text-xs font-medium text-gray-300">Equipment Factor</label>
            <span className="text-xs font-mono text-blue-400">{equipmentFactor.toFixed(2)}x</span>
          </div>
          <input
            type="range"
            min="0.7"
            max="1"
            step="0.05"
            value={equipmentFactor}
            onChange={(e) => setEquipmentFactor(parseFloat(e.target.value))}
            className="w-full accent-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">Equipment availability</p>
        </div>

        {/* Climate Factor */}
        <div>
          <div className="flex items-center justify-between mb-1 md:mb-2">
            <label className="text-xs font-medium text-gray-300">Climate Factor</label>
            <span className="text-xs font-mono text-blue-400">{climateFactor.toFixed(2)}x</span>
          </div>
          <input
            type="range"
            min="0.6"
            max="1"
            step="0.05"
            value={climateFactor}
            onChange={(e) => setClimateFactor(parseFloat(e.target.value))}
            className="w-full accent-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">Rainfall & flooding impact</p>
        </div>

        {/* Regulatory Factor */}
        <div>
          <div className="flex items-center justify-between mb-1 md:mb-2">
            <label className="text-xs font-medium text-gray-300">Regulatory Factor</label>
            <span className="text-xs font-mono text-blue-400">{regulatoryFactor.toFixed(2)}x</span>
          </div>
          <input
            type="range"
            min="0.6"
            max="1"
            step="0.05"
            value={regulatoryFactor}
            onChange={(e) => setRegulatoryFactor(parseFloat(e.target.value))}
            className="w-full accent-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">Protected area discount</p>
        </div>

        {/* Infrastructure Factor */}
        <div>
          <div className="flex items-center justify-between mb-1 md:mb-2">
            <label className="text-xs font-medium text-gray-300">Infrastructure Factor</label>
            <span className="text-xs font-mono text-blue-400">{infrastructureFactor.toFixed(2)}x</span>
          </div>
          <input
            type="range"
            min="0.7"
            max="1"
            step="0.05"
            value={infrastructureFactor}
            onChange={(e) => setInfrastructureFactor(parseFloat(e.target.value))}
            className="w-full accent-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">Haul road distance impact</p>
        </div>
      </div>

      {/* Factor Visualization */}
      <div className="mt-4 md:mt-6 rounded-lg bg-gray-900/50 border border-gray-700/50 p-3 md:p-4">
        <p className="text-xs font-medium text-gray-300 mb-2 md:mb-3">Accessibility Factor Breakdown</p>
        <div className="space-y-2">
          {[
            { label: "Depth", value: depthFactor },
            { label: "Equipment", value: equipmentFactor },
            { label: "Climate", value: climateFactor },
            { label: "Regulatory", value: regulatoryFactor },
            { label: "Infrastructure", value: infrastructureFactor },
          ].map((factor) => (
            <div key={factor.label} className="flex items-center gap-2">
              <span className="w-20 md:w-24 text-xs text-gray-400 truncate">{factor.label}</span>
              <div className="flex-1 h-2 rounded-full bg-gray-700 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-cyan-400"
                  style={{ width: `${factor.value * 100}%` }}
                />
              </div>
              <span className="w-10 text-right text-xs font-mono text-gray-300">
                {(factor.value * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
