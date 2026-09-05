import { useState } from "react";
import ReactECharts from "echarts-for-react";
import type { Forecast } from "../api/client";

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

  const option = forecast
    ? {
        backgroundColor: "transparent",
        grid: { left: 50, right: 20, top: 20, bottom: 30 },
        xAxis: {
          type: "category",
          data: forecast.fan_chart.map((f) => `Day ${f.day}`),
          axisLabel: { color: "#9ca3af", interval: 4 },
        },
        yAxis: {
          type: "value",
          name: "cumulative tonnes",
          axisLabel: { color: "#9ca3af" },
          splitLine: { lineStyle: { color: "#1f2937" } },
        },
        tooltip: { trigger: "axis" },
        series: [
          {
            name: "P90",
            type: "line",
            data: forecast.fan_chart.map((f) => f.p90),
            lineStyle: { opacity: 0 },
            stack: "band",
            areaStyle: { color: "rgba(56, 189, 248, 0.15)" },
            showSymbol: false,
          },
          {
            name: "P10",
            type: "line",
            data: forecast.fan_chart.map((f) => f.p10),
            lineStyle: { opacity: 0 },
            showSymbol: false,
          },
          {
            name: "P50",
            type: "line",
            data: forecast.fan_chart.map((f) => f.p50),
            lineStyle: { color: "#38bdf8", width: 2 },
            showSymbol: false,
          },
        ],
      }
    : null;

  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-4">
      <div className="mb-2 flex items-center justify-between">
        <div className="text-sm font-medium text-gray-300">Production forecast (P10 / P50 / P90)</div>
        {forecast && (
          <div
            className={`rounded px-2 py-1 text-xs font-semibold ${
              forecast.shortfall_probability > 0.4
                ? "bg-red-500/20 text-red-300"
                : "bg-emerald-500/20 text-emerald-300"
            }`}
          >
            Shortfall probability: {Math.round(forecast.shortfall_probability * 100)}%
          </div>
        )}
      </div>

      {option ? (
        <ReactECharts option={option} style={{ height: 240 }} />
      ) : (
        <div className="flex h-60 items-center justify-center text-sm text-gray-500">
          {loading ? "Computing forecast…" : "No forecast yet."}
        </div>
      )}

      <div className="mt-4">
        <label className="mb-1 flex justify-between text-xs text-gray-400">
          <span>What-if: rainfall scenario (mm, trailing 90-day avg)</span>
          <span>{rainfall.toFixed(1)} mm</span>
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
      </div>

      {forecast && (
        <div className="mt-4">
          <div className="mb-1 text-xs uppercase tracking-wide text-gray-400">
            Top drivers (why)
          </div>
          <div className="space-y-1">
            {forecast.drivers.map((d) => (
              <div key={d.name} className="flex items-center gap-2 text-sm">
                <div className="w-40 shrink-0 truncate text-gray-300">{d.name}</div>
                <div className="h-2 flex-1 rounded bg-white/10">
                  <div
                    className={`h-2 rounded ${
                      d.direction === "increases risk" ? "bg-red-400" : "bg-emerald-400"
                    }`}
                    style={{ width: `${Math.round(d.impact * 100)}%` }}
                  />
                </div>
                <div className="w-28 shrink-0 text-xs text-gray-500">{d.direction}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
