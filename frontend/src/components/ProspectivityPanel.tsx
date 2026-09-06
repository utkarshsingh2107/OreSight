import { useEffect, useState } from "react";
import { api } from "../api/client";

export interface ProspectTarget {
  rank: number;
  name: string;
  latitude: number;
  longitude: number;
  prospectivity_score: number; // 0-1
  confidence: number; // 0-1
  evidence: {
    spectral_indices: number;
    distance_to_known_mine: number;
    lineament_proximity: number;
    vegetation_stress: number;
  };
}

export interface ProspectivityData {
  total_prospects: number;
  targets: ProspectTarget[];
  heatmap_url: string;
}

interface ProspectivityPanelProps {
  mineId: number;
}

export default function ProspectivityPanel({ mineId }: ProspectivityPanelProps) {
  const [data, setData] = useState<ProspectivityData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [expandedTarget, setExpandedTarget] = useState<number | null>(null);

  useEffect(() => {
    setLoading(true);
    api
      .get<ProspectivityData>(`/prospectivity/targets`, { params: { mine_id: mineId } })
      .then((res) => {
        setData(res.data);
        setError(null);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || "Failed to load prospectivity data");
      })
      .finally(() => setLoading(false));
  }, [mineId]);

  if (loading) {
    return (
      <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
        <div className="h-96 animate-pulse rounded bg-gray-700/50" />
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-3 md:p-4">
      <div className="mb-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h2 className="text-base md:text-lg font-semibold text-white">Reserve Prospectivity</h2>
          <p className="text-xs text-gray-400">
            Identified {data?.total_prospects || 0} potential manganese reserves
          </p>
        </div>
        <button
          onClick={() => setShowHeatmap(!showHeatmap)}
          className={`rounded px-2 md:px-3 py-1.5 md:py-2 text-xs font-medium transition-colors whitespace-nowrap ${
            showHeatmap
              ? "bg-blue-600/80 text-white hover:bg-blue-600"
              : "bg-gray-700/50 text-gray-300 hover:bg-gray-700"
          }`}
        >
          {showHeatmap ? "Hide" : "Show"} Heatmap
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded border border-yellow-600/40 bg-yellow-600/10 p-2 text-xs text-yellow-300">
          {error}
        </div>
      )}

      {showHeatmap && data?.heatmap_url && (
        <div className="mb-4 overflow-hidden rounded border border-gray-600 bg-gray-900">
          <img
            src={data.heatmap_url}
            alt="Prospectivity Heatmap"
            className="w-full"
            onError={() => setError("Could not load heatmap image")}
          />
        </div>
      )}

      <div className="space-y-2">
        <h3 className="text-xs md:text-sm font-medium text-gray-200">Top Drill Targets</h3>
        {data?.targets && data.targets.length > 0 ? (
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {data.targets.map((target) => (
              <div
                key={target.rank}
                onClick={() =>
                  setExpandedTarget(expandedTarget === target.rank ? null : target.rank)
                }
                className="cursor-pointer rounded border border-gray-600/50 bg-gray-700/30 p-2 md:p-3 transition-colors hover:bg-gray-700/50"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="inline-flex h-5 w-5 md:h-6 md:w-6 flex-shrink-0 items-center justify-center rounded-full bg-blue-600/80 text-xs font-bold text-white">
                        {target.rank}
                      </span>
                      <p className="text-xs md:text-sm font-medium text-white truncate">{target.name}</p>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">
                      {target.latitude.toFixed(4)}° N, {target.longitude.toFixed(4)}° E
                    </p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="text-xs md:text-sm font-semibold text-green-400">
                      {(target.prospectivity_score * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-gray-400">
                      {(target.confidence * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>

                {/* Confidence bar */}
                <div className="mt-2 h-1.5 rounded-full bg-gray-600/50 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-green-500 to-blue-500"
                    style={{ width: `${target.prospectivity_score * 100}%` }}
                  />
                </div>

                {/* Expanded details */}
                {expandedTarget === target.rank && (
                  <div className="mt-3 space-y-2 border-t border-gray-600/30 pt-3">
                    <p className="text-xs font-medium text-gray-300">Evidence Layers</p>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="rounded bg-gray-800/50 p-2">
                        <span className="text-gray-400">Spectral:</span>
                        <p className="font-mono text-green-400">
                          {(target.evidence.spectral_indices * 100).toFixed(0)}%
                        </p>
                      </div>
                      <div className="rounded bg-gray-800/50 p-2">
                        <span className="text-gray-400">Lineaments:</span>
                        <p className="font-mono text-green-400">
                          {(target.evidence.lineament_proximity * 100).toFixed(0)}%
                        </p>
                      </div>
                      <div className="rounded bg-gray-800/50 p-2">
                        <span className="text-gray-400">Distance:</span>
                        <p className="font-mono text-green-400">
                          {(target.evidence.distance_to_known_mine * 100).toFixed(0)}%
                        </p>
                      </div>
                      <div className="rounded bg-gray-800/50 p-2">
                        <span className="text-gray-400">Vegetation:</span>
                        <p className="font-mono text-green-400">
                          {(target.evidence.vegetation_stress * 100).toFixed(0)}%
                        </p>
                      </div>
                    </div>
                    <a
                      href={`#map?lat=${target.latitude}&lon=${target.longitude}`}
                      className="inline-block text-xs text-blue-400 hover:text-blue-300 mt-2"
                    >
                      View on map →
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-gray-400">No prospects available yet.</p>
        )}
      </div>
    </div>
  );
}
