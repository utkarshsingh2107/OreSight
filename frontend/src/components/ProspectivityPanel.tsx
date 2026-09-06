import React, { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";
import {
  getProspectivityTargets,
  getFeatureImportance,
  type ProspectivityTarget,
  type FeatureImportance,
} from "../api/client";

const CONFIDENCE_STYLES: Record<string, string> = {
  high: "bg-amber-500/25 text-amber-300 border-amber-600/40",
  medium: "bg-orange-500/25 text-orange-300 border-orange-600/40",
  low: "bg-slate-500/20 text-slate-400 border-slate-600/40",
};

export default function ProspectivityPanel() {
  const [targets, setTargets] = useState<ProspectivityTarget[]>([]);
  const [features, setFeatures] = useState<FeatureImportance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<number | null>(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([getProspectivityTargets(10), getFeatureImportance()])
      .then(([t, f]) => {
        setTargets(t.targets);
        setFeatures(f.feature_importance);
      })
      .catch(() => setError("Could not load prospectivity data."))
      .finally(() => setLoading(false));
  }, []);

  const featureChartOption = features.length > 0
    ? {
        backgroundColor: "transparent",
        grid: { left: 160, right: 20, top: 12, bottom: 12 },
        xAxis: {
          type: "value",
          axisLabel: { color: "#64748b", fontSize: 10, formatter: (v: number) => `${(v * 100).toFixed(0)}%` },
          splitLine: { lineStyle: { color: "#1e293b" } },
        },
        yAxis: {
          type: "category",
          data: [...features].reverse().map((f) => f.display_name),
          axisLabel: { color: "#94a3b8", fontSize: 10 },
          axisLine: { show: false },
          axisTick: { show: false },
        },
        tooltip: {
          backgroundColor: "#0f172a",
          borderColor: "#334155",
          textStyle: { color: "#e2e8f0", fontSize: 12 },
          formatter: (p: { name: string; value: number }) =>
            `${p.name}: ${(p.value * 100).toFixed(1)}%`,
        },
        series: [
          {
            type: "bar",
            data: [...features].reverse().map((f) => ({
              value: f.importance,
              itemStyle: {
                color:
                  f.importance > 0.5
                    ? "#f59e0b"
                    : f.importance > 0.1
                      ? "#38bdf8"
                      : "#64748b",
                borderRadius: [0, 4, 4, 0],
              },
            })),
            barMaxWidth: 18,
            label: {
              show: true,
              position: "right",
              color: "#64748b",
              fontSize: 10,
              formatter: (p: { value: number }) => `${(p.value * 100).toFixed(1)}%`,
            },
          },
        ],
      }
    : null;

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center text-slate-500">
        <svg className="mr-2 h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
        Loading prospectivity model…
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-800/40 bg-red-900/20 p-4 text-sm text-red-300">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Model stats header */}
      <div className="rounded-xl border border-white/10 bg-slate-800/60 p-4 backdrop-blur">
        <div className="mb-3 flex items-center gap-2">
          <span className="text-base">🛰️</span>
          <span className="text-sm font-semibold text-slate-200">Mineral Prospectivity Mapping</span>
          <span className="ml-auto rounded-full bg-emerald-900/40 border border-emerald-700/40 px-2 py-0.5 text-xs text-emerald-300">
            AUC-ROC 0.936
          </span>
        </div>

        {/* Model badges */}
        <div className="mb-4 flex flex-wrap gap-2 text-xs">
          {[
            { label: "Random Forest", icon: "🌲", color: "bg-emerald-900/40 border-emerald-700/40 text-emerald-300" },
            { label: "660 training samples", icon: "📊", color: "bg-sky-900/40 border-sky-700/40 text-sky-300" },
            { label: "5-fold spatial CV", icon: "🔄", color: "bg-violet-900/40 border-violet-700/40 text-violet-300" },
            { label: "Sentinel-2 + DEM", icon: "🛰️", color: "bg-amber-900/40 border-amber-700/40 text-amber-300" },
            { label: "10 spectral features", icon: "📡", color: "bg-slate-700/60 border-slate-600/40 text-slate-300" },
          ].map((b) => (
            <span
              key={b.label}
              className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 font-medium ${b.color}`}
            >
              {b.icon} {b.label}
            </span>
          ))}
        </div>

        {/* Feature importance chart */}
        {featureChartOption && (
          <div>
            <div className="mb-1 text-xs font-medium uppercase tracking-wider text-slate-400">
              Feature Importance
            </div>
            <ReactECharts option={featureChartOption} style={{ height: 220 }} />
          </div>
        )}
      </div>

      {/* Top 10 Targets */}
      <div className="rounded-xl border border-white/10 bg-slate-800/60 p-4 backdrop-blur">
        <div className="mb-3 flex items-center gap-2">
          <span className="text-base">📍</span>
          <span className="text-sm font-semibold text-slate-200">Top 10 Exploration Targets</span>
          <span className="ml-auto text-xs text-slate-500">Click row to expand</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-white/10 text-left text-[10px] uppercase tracking-wider text-slate-500">
                <th className="pb-2 pr-3">Rank</th>
                <th className="pb-2 pr-3">Confidence</th>
                <th className="pb-2 pr-3">Probability</th>
                <th className="pb-2 pr-3">Lat / Lon</th>
                <th className="pb-2 pr-3">Nearest Mine</th>
                <th className="pb-2">Distance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {targets.map((t) => (
                <React.Fragment key={t.id}>
                  <tr
                    key={t.id}
                    onClick={() => setSelected(selected === t.rank ? null : t.rank)}
                    className="cursor-pointer transition hover:bg-white/5"
                  >
                    <td className="py-2 pr-3 font-bold text-white">
                      {t.rank <= 3 ? (
                        <span className="rounded bg-amber-500/20 px-1.5 text-amber-300">#{t.rank}</span>
                      ) : (
                        `#${t.rank}`
                      )}
                    </td>
                    <td className="py-2 pr-3">
                      <span
                        className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold capitalize ${CONFIDENCE_STYLES[t.confidence] ?? ""}`}
                      >
                        {t.confidence}
                      </span>
                    </td>
                    <td className="py-2 pr-3">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-20 overflow-hidden rounded-full bg-slate-700">
                          <div
                            className="h-1.5 rounded-full bg-amber-400"
                            style={{ width: `${t.probability * 100}%` }}
                          />
                        </div>
                        <span className="text-slate-300">{Math.round(t.probability * 100)}%</span>
                      </div>
                    </td>
                    <td className="py-2 pr-3 font-mono text-slate-400">
                      {t.lat.toFixed(4)}, {t.lon.toFixed(4)}
                    </td>
                    <td className="py-2 pr-3 text-slate-300">{t.nearest_mine ?? "—"}</td>
                    <td className="py-2 text-slate-400">
                      {t.distance_to_mine_km != null ? `${t.distance_to_mine_km.toFixed(1)} km` : "—"}
                    </td>
                  </tr>
                  {selected === t.rank && (
                    <tr key={`${t.id}-detail`} className="bg-slate-700/30">
                      <td colSpan={6} className="px-3 py-3">
                        <div className="grid grid-cols-3 gap-3 text-xs">
                          <div className="rounded-lg bg-black/20 border border-white/5 p-2">
                            <div className="text-slate-500">Iron Oxide Index (Sentinel-2)</div>
                            <div className="mt-1 text-base font-bold text-amber-400">
                              {t.evidence.iron_oxide_index.toFixed(3)}
                            </div>
                          </div>
                          <div className="rounded-lg bg-black/20 border border-white/5 p-2">
                            <div className="text-slate-500">NDVI Anomaly</div>
                            <div className={`mt-1 text-base font-bold ${t.evidence.ndvi_anomaly < 0 ? "text-red-400" : "text-emerald-400"}`}>
                              {t.evidence.ndvi_anomaly > 0 ? "+" : ""}{t.evidence.ndvi_anomaly.toFixed(3)}
                            </div>
                          </div>
                          <div className="rounded-lg bg-black/20 border border-white/5 p-2">
                            <div className="text-slate-500">Dist. to Known Mine</div>
                            <div className="mt-1 text-base font-bold text-sky-400">
                              {t.evidence.distance_to_known_mine_km.toFixed(1)} km
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
