import ReactECharts from "echarts-for-react";
import type { ProductionPoint } from "../api/client";

function rollingAvg(data: number[], window: number): number[] {
  return data.map((_, i) => {
    const start = Math.max(0, i - window + 1);
    const slice = data.slice(start, i + 1);
    return slice.reduce((a, b) => a + b, 0) / slice.length;
  });
}

export default function ProductionChart({ data }: { data: ProductionPoint[] }) {
  const recent = data.slice(-180); // last 6 months
  const avg30 = rollingAvg(recent.map((d) => d.tonnes), 30);

  const option = {
    backgroundColor: "transparent",
    grid: { left: 60, right: 60, top: 28, bottom: 36 },
    legend: {
      top: 4,
      right: 8,
      textStyle: { color: "#94a3b8", fontSize: 11 },
      itemWidth: 12,
      itemHeight: 4,
    },
    xAxis: {
      type: "category",
      data: recent.map((d) => d.date),
      axisLabel: {
        color: "#64748b",
        interval: Math.floor(recent.length / 6),
        formatter: (v: string) => v.slice(5), // MM-DD
      },
      axisLine: { lineStyle: { color: "#1e293b" } },
    },
    yAxis: [
      {
        type: "value",
        name: "tonnes/day",
        nameTextStyle: { color: "#64748b", fontSize: 10 },
        axisLabel: { color: "#64748b", fontSize: 10 },
        splitLine: { lineStyle: { color: "#1e293b" } },
      },
      {
        type: "value",
        name: "rainfall mm",
        nameTextStyle: { color: "#64748b", fontSize: 10 },
        axisLabel: { color: "#64748b", fontSize: 10, formatter: (v: number) => `${v}` },
        splitLine: { show: false },
      },
    ],
    tooltip: {
      trigger: "axis",
      backgroundColor: "#0f172a",
      borderColor: "#334155",
      textStyle: { color: "#e2e8f0", fontSize: 12 },
      axisPointer: { type: "cross", lineStyle: { color: "#334155" } },
    },
    series: [
      {
        name: "Rainfall",
        type: "bar",
        yAxisIndex: 1,
        data: recent.map((d) => d.rainfall_mm ?? 0),
        itemStyle: { color: "rgba(99,179,237,0.25)", borderRadius: [2, 2, 0, 0] },
        barMaxWidth: 4,
        z: 1,
      },
      {
        name: "Production",
        type: "line",
        data: recent.map((d) => d.tonnes),
        smooth: true,
        showSymbol: false,
        lineStyle: { color: "#38bdf8", width: 2 },
        areaStyle: {
          color: {
            type: "linear",
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(56,189,248,0.25)" },
              { offset: 1, color: "rgba(56,189,248,0.02)" },
            ],
          },
        },
        z: 3,
      },
      {
        name: "30-day avg",
        type: "line",
        data: avg30,
        smooth: true,
        showSymbol: false,
        lineStyle: { color: "#f59e0b", width: 1.5, type: "dashed" },
        z: 2,
      },
    ],
  };

  return (
    <div className="rounded-xl border border-white/10 bg-slate-800/60 p-4 backdrop-blur">
      <div className="mb-1 flex items-center gap-2">
        <span className="text-base">📈</span>
        <span className="text-sm font-semibold text-slate-200">Production History</span>
        <span className="ml-auto rounded-full bg-slate-700 px-2 py-0.5 text-xs text-slate-400">
          Last 180 days
        </span>
      </div>
      {data.length === 0 ? (
        <div className="flex h-64 items-center justify-center text-sm text-slate-500">
          No production data — run the data generator.
        </div>
      ) : (
        <ReactECharts option={option} style={{ height: 280 }} />
      )}
    </div>
  );
}
