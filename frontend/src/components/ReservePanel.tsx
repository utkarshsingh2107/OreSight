import { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";
import { api } from "../api/client";

interface GradeTonnagePoint {
  cutoff_grade: number;
  tonnage: number;
  avg_grade: number;
}

interface ReserveData {
  total_geological_tonnage: number;
  effective_accessible_reserve_tonnage: number;
  accessibility_discount_pct: number;
  tonnage_by_confidence: Record<string, number>;
  grade_tonnage_curve: GradeTonnagePoint[];
  block_model_image_url: string;
  note: string;
}

export default function ReservePanel({ mineId }: { mineId: number }) {
  const [data, setData] = useState<ReserveData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<ReserveData>(`/mines/${mineId}/reserve`)
      .then((r) => setData(r.data))
      .catch(() => setError("Reserve model not generated yet."));
  }, [mineId]);

  const option = data
    ? {
        backgroundColor: "transparent",
        grid: { left: 60, right: 20, top: 20, bottom: 40 },
        xAxis: {
          type: "value",
          name: "cutoff grade (% Mn)",
          nameLocation: "middle",
          nameGap: 25,
          axisLabel: { color: "#9ca3af" },
        },
        yAxis: {
          type: "value",
          name: "tonnage above cutoff",
          axisLabel: { color: "#9ca3af", formatter: (v: number) => `${(v / 1e6).toFixed(1)}M` },
          splitLine: { lineStyle: { color: "#1f2937" } },
        },
        tooltip: { trigger: "axis" },
        series: [
          {
            name: "Tonnage",
            type: "line",
            data: data.grade_tonnage_curve.map((p) => [p.cutoff_grade, p.tonnage]),
            smooth: true,
            showSymbol: false,
            lineStyle: { color: "#a78bfa" },
            areaStyle: { color: "rgba(167, 139, 250, 0.12)" },
          },
        ],
      }
    : null;

  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-4">
      <div className="mb-2 text-sm font-medium text-gray-300">
        Reserve — 3D block model &amp; grade-tonnage curve
      </div>

      {error && <div className="text-sm text-gray-500">{error}</div>}

      {data && (
        <>
          <div className="mb-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
            <div className="rounded border border-white/10 bg-black/20 p-3">
              <div className="text-xs text-gray-400">Total geological reserve</div>
              <div className="text-lg font-semibold text-white">
                {(data.total_geological_tonnage / 1e6).toFixed(1)}M t
              </div>
            </div>
            <div className="rounded border border-emerald-500/30 bg-emerald-500/10 p-3">
              <div className="text-xs text-gray-400">Effective Accessible Reserve (EAR)</div>
              <div className="text-lg font-semibold text-emerald-400">
                {(data.effective_accessible_reserve_tonnage / 1e6).toFixed(1)}M t
              </div>
            </div>
            <div className="rounded border border-white/10 bg-black/20 p-3">
              <div className="text-xs text-gray-400">Accessibility discount</div>
              <div className="text-lg font-semibold text-amber-400">
                {data.accessibility_discount_pct}%
              </div>
            </div>
          </div>

          <img
            src={data.block_model_image_url}
            alt="Balaghat synthetic 3D block model, colored by Mn grade"
            className="mb-3 w-full rounded border border-white/10"
          />

          {option && <ReactECharts option={option} style={{ height: 220 }} />}

          <div className="mt-2 text-xs text-gray-500">{data.note}</div>
        </>
      )}
    </div>
  );
}
