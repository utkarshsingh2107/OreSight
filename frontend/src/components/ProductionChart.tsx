import ReactECharts from "echarts-for-react";
import type { ProductionPoint } from "../api/client";

export default function ProductionChart({ data }: { data: ProductionPoint[] }) {
  const option = {
    backgroundColor: "transparent",
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: "category",
      data: data.map((d) => d.date),
      axisLabel: { color: "#9ca3af" },
    },
    yAxis: {
      type: "value",
      name: "tonnes/day",
      axisLabel: { color: "#9ca3af" },
      splitLine: { lineStyle: { color: "#1f2937" } },
    },
    tooltip: { trigger: "axis" },
    series: [
      {
        name: "Production",
        type: "line",
        data: data.map((d) => d.tonnes),
        smooth: true,
        showSymbol: false,
        lineStyle: { color: "#38bdf8" },
        areaStyle: { color: "rgba(56, 189, 248, 0.1)" },
      },
    ],
  };

  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-4">
      <div className="mb-2 text-sm font-medium text-gray-300">Daily production history</div>
      {data.length === 0 ? (
        <div className="flex h-64 items-center justify-center text-sm text-gray-500">
          No production data yet — run the synthetic data generator.
        </div>
      ) : (
        <ReactECharts option={option} style={{ height: 260 }} />
      )}
    </div>
  );
}
