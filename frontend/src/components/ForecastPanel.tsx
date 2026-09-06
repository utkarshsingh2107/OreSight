import { useState } from "react";
import ReactECharts from "echarts-for-react";
import type { Forecast } from "../api/client";

const SATELLITE_INPUTS = [
  { key: "rainfall", label: "Rainfall", icon: "🌧️", color: "text-sky-400 bg-sky-900/40 border-sky-700/50" },
  { key: "soil_moisture", label: "Soil Moisture", icon: "💧", color: "text-blue-400 bg-blue-900/40 border-blue-700/50" },
  { key: "ndvi", label: "NDVI", icon: "🌿", color: "text-emerald-400 bg-emerald-900/40 border-emerald-700/50" },
  { key: "temperature", label: "Land Temp", icon: "🌡️", color: "text-orange-400 bg-orange-900/40 border-orange-700/50" },
];

const CATEGORY_COLORS: Record<string, string> = {
  weather: "bg-sky-500",
  equipment: "bg-violet-500",
  operational: "bg-amber-500",
};

export default function ForecastPanel({
  forecast,
  baselineRainfall,
  onRainfallChange,
  loading,
}: {
  forecast: Forecast | null;
  baselineRainfall: number;
  onRainfallChange: (mm: number) => void;
  loading: boolean;
}) {
  const [rainfall, setRainfall] = useState(baselineRainfall);

  const sp = forecast ? Math.round(forecast.shortfall_probability * 100) : null;
  const riskColor =
    sp !== null && sp > 60
      ? "bg-red-500/20 text-red-300 border-red-700/50"
      : sp !== null && sp > 35
        ? "bg-amber-500/20 text-amber-300 border-amber-700/50"
        : "bg-emerald-500/20 text-emerald-300 border-emerald-700/50";

  const option = forecast
    ? {
        backgroundColor: "transparent",
        grid: { left: 56, right: 20, top: 24, bottom: 32 },
        xAxis: {
          type: "category",
          data: forecast.fan_chart.map((f) => `Day ${f.day}`),
          axisLabel: { color: "#64748b", interval: 4, fontSize: 10 },
          axisLine: { lineStyle: { color: "#1e293b" } },
        },
        yAxis: {
          type: "value",
          name: "cum. tonnes",
          nameTextStyle: { color: "#64748b", fontSize: 10 },
          axisLabel: { color: "#64748b", fontSize: 10, formatter: (v: number) => `${(v / 1000).toFixed(0)}k` },
          splitLine: { lineStyle: { color: "#1e293b" } },
        },
        tooltip: {
          trigger: "axis",
          backgroundColor: "#0f172a",
          borderColor: "#334155",
          textStyle: { color: "#e2e8f0", fontSize: 12 },
        },
        series: [
          {
            name: "P90 (optimistic)",
            type: "line",
            data: forecast.fan_chart.map((f) => f.p90),
            lineStyle: { opacity: 0 },
            areaStyle: { color: "rgba(56,189,248,0.12)" },
            showSymbol: false,
            stack: "band",
          },
          {
            name: "P10 (pessimistic)",
            type: "line",
            data: forecast.fan_chart.map((f) => f.p10),
            lineStyle: { opacity: 0 },
            showSymbol: false,
          },
          {
            name: "P50 (median)",
            type: "line",
            data: forecast.fan_chart.map((f) => f.p50),
            lineStyle: { color: "#38bdf8", width: 2.5 },
            showSymbol: false,
          },
        ],
      }
    : null;

  return (
    <div className="rounded-xl border border-white/10 bg-slate-800/60 p-4 backdrop-blur">
      {/* Header */}
      <div className="mb-3 flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-base">🔮</span>
            <span className="text-sm font-semibold text-slate-200">30-Day Production Forecast</span>
          </div>
          <p className="mt-0.5 text-xs text-slate-500">LightGBM quantile model · 17 features</p>
        </div>
        {sp !== null && (
          <div className={`rounded-lg border px-3 py-1.5 text-xs font-semibold ${riskColor}`}>
            Shortfall risk: {sp}%
          </div>
        )}
      </div>

      {/* Satellite inputs badges */}
      <div className="mb-3 flex flex-wrap gap-2">
        {SATELLITE_INPUTS.map((s) => (
          <div
            key={s.key}
            className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${s.color}`}
          >
            <span>{s.icon}</span>
            <span>{s.label}</span>
            <span className="ml-0.5 h-1.5 w-1.5 rounded-full bg-current opacity-80" />
          </div>
        ))}
      </div>

      {/* Fan chart */}
      {option ? (
        <ReactECharts option={option} style={{ height: 220 }} />
      ) : (
        <div className="flex h-56 items-center justify-center text-sm text-slate-500">
          {loading ? (
            <span className="flex items-center gap-2">
              <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Computing forecast…
            </span>
          ) : (
            "Loading forecast…"
          )}
        </div>
      )}

      {/* Rainfall what-if slider */}
      <div className="mt-3 rounded-lg border border-white/5 bg-black/20 p-3">
        <label className="mb-2 flex justify-between text-xs text-slate-400">
          <span>🌧️ What-if: Rainfall scenario (90-day trailing avg)</span>
          <span className="font-semibold text-sky-300">{rainfall.toFixed(1)} mm/day</span>
        </label>
        <input
          type="range"
          min={0}
          max={30}
          step={0.5}
          value={rainfall}
          onChange={(e) => setRainfall(parseFloat(e.target.value))}
          onMouseUp={() => onRainfallChange(rainfall)}
          onTouchEnd={() => onRainfallChange(rainfall)}
          className="w-full accent-sky-400"
        />
        <div className="mt-1 flex justify-between text-xs text-slate-600">
          <span>Dry (0mm)</span>
          <span>Normal (~5mm)</span>
          <span>Heavy monsoon (30mm)</span>
        </div>
      </div>

      {/* SHAP drivers */}
      {forecast && forecast.drivers.length > 0 && (
        <div className="mt-3">
          <div className="mb-2 text-xs font-medium uppercase tracking-wider text-slate-400">
            Top forecast drivers (SHAP)
          </div>
          <div className="space-y-1.5">
            {forecast.drivers.slice(0, 6).map((d) => {
              const catColor = CATEGORY_COLORS[d.category ?? "operational"] ?? "bg-slate-500";
              return (
                <div key={d.name} className="flex items-center gap-2.5 text-xs">
                  <div className="w-36 shrink-0 truncate text-slate-300">{d.name}</div>
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-700">
                    <div
                      className={`h-1.5 rounded-full ${d.direction === "increases risk" ? "bg-red-400" : "bg-emerald-400"}`}
                      style={{ width: `${Math.round(d.impact * 100)}%` }}
                    />
                  </div>
                  {d.category && (
                    <div className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] text-white ${catColor}`}>
                      {d.category}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
