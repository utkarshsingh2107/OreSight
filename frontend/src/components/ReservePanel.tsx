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

const FACTORS = [
  { key: "depth", label: "Depth Factor", icon: "⬇️", value: 0.731, desc: "450m avg depth" },
  { key: "equipment", label: "Equipment Factor", icon: "🚛", value: 1.0, desc: "3 LHDs at capacity" },
  { key: "climate", label: "Climate Factor", icon: "🌧️", value: 0.75, desc: "~90 monsoon days/yr" },
  { key: "infra", label: "Infrastructure Factor", icon: "🛣️", value: 0.988, desc: "3.2 km haul road" },
];

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
        grid: { left: 60, right: 20, top: 24, bottom: 44 },
        xAxis: {
          type: "value",
          name: "Cutoff Grade (% Mn)",
          nameLocation: "middle",
          nameGap: 28,
          nameTextStyle: { color: "#64748b", fontSize: 10 },
          axisLabel: { color: "#64748b", fontSize: 10 },
        },
        yAxis: {
          type: "value",
          name: "Tonnes above cutoff",
          nameTextStyle: { color: "#64748b", fontSize: 10 },
          axisLabel: {
            color: "#64748b",
            fontSize: 10,
            formatter: (v: number) => `${(v / 1e6).toFixed(1)}M`,
          },
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
            name: "Tonnage",
            type: "line",
            data: data.grade_tonnage_curve.map((p) => [p.cutoff_grade, p.tonnage]),
            smooth: true,
            showSymbol: false,
            lineStyle: { color: "#a78bfa", width: 2.5 },
            areaStyle: {
              color: {
                type: "linear",
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: "rgba(167,139,250,0.25)" },
                  { offset: 1, color: "rgba(167,139,250,0.02)" },
                ],
              },
            },
          },
        ],
      }
    : null;

  return (
    <div className="rounded-xl border border-white/10 bg-slate-800/60 p-4 backdrop-blur">
      <div className="mb-3 flex items-center gap-2">
        <span className="text-base">🪨</span>
        <span className="text-sm font-semibold text-slate-200">Reserve Model — EAR Analysis</span>
        <span className="ml-auto rounded-full bg-amber-900/40 border border-amber-700/40 px-2 py-0.5 text-xs text-amber-300">
          Synthetic geometry · Real-calibrated
        </span>
      </div>

      {error && <div className="text-sm text-slate-500">{error}</div>}

      {data && (
        <>
          {/* Summary numbers */}
          <div className="mb-4 grid grid-cols-3 gap-3">
            <div className="rounded-lg border border-white/10 bg-black/20 p-3">
              <div className="text-xs text-slate-400">Geological Reserve</div>
              <div className="mt-1 text-lg font-bold text-white">
                {(data.total_geological_tonnage / 1e6).toFixed(1)}M t
              </div>
            </div>
            <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3">
              <div className="text-xs text-slate-400">Effective Accessible Reserve</div>
              <div className="mt-1 text-lg font-bold text-emerald-400">
                {(data.effective_accessible_reserve_tonnage / 1e6).toFixed(1)}M t
              </div>
            </div>
            <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-3">
              <div className="text-xs text-slate-400">Accessibility Discount</div>
              <div className="mt-1 text-lg font-bold text-amber-400">
                {data.accessibility_discount_pct}%
              </div>
            </div>
          </div>

          {/* EAR Funnel — visual breakdown */}
          <div className="mb-4 rounded-lg border border-white/5 bg-black/20 p-3">
            <div className="mb-2 text-xs font-medium uppercase tracking-wider text-slate-400">
              EAR Accessibility Funnel
            </div>
            <div className="flex items-center gap-1 overflow-x-auto">
              {/* Start */}
              <div className="shrink-0 text-center">
                <div className="rounded-lg bg-violet-900/50 border border-violet-700/40 px-3 py-2">
                  <div className="text-xs text-slate-400">Geological</div>
                  <div className="text-sm font-bold text-white">
                    {(data.total_geological_tonnage / 1e6).toFixed(1)}M t
                  </div>
                </div>
              </div>

              {FACTORS.map((f, i) => {
                const runningProduct = FACTORS.slice(0, i + 1).reduce((acc, ff) => acc * ff.value, 1);
                const afterTonnes = (data.total_geological_tonnage * runningProduct) / 1e6;
                return (
                  <div key={f.key} className="flex shrink-0 items-center gap-1">
                    {/* Arrow */}
                    <div className="flex flex-col items-center">
                      <div className="text-[10px] text-slate-500">×{f.value.toFixed(3)}</div>
                      <div className="text-slate-600">→</div>
                    </div>
                    {/* Factor block */}
                    <div className="text-center">
                      <div className="rounded-lg border border-white/10 bg-slate-700/50 px-2.5 py-2">
                        <div className="text-base">{f.icon}</div>
                        <div className="text-[10px] text-slate-400">{f.label}</div>
                        <div className="text-xs font-bold text-white">{afterTonnes.toFixed(1)}M t</div>
                      </div>
                      <div className="mt-0.5 text-[9px] text-slate-600">{f.desc}</div>
                    </div>
                  </div>
                );
              })}

              {/* End = EAR */}
              <div className="flex shrink-0 items-center gap-1">
                <div className="text-slate-600">→</div>
                <div className="rounded-lg border border-emerald-500/40 bg-emerald-500/15 px-3 py-2 text-center">
                  <div className="text-xs text-slate-400">EAR</div>
                  <div className="text-sm font-bold text-emerald-400">
                    {(data.effective_accessible_reserve_tonnage / 1e6).toFixed(1)}M t
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Block model image */}
          <img
            src={data.block_model_image_url}
            alt="Balaghat 3D block model colored by Mn grade"
            className="mb-4 w-full rounded-lg border border-white/10"
          />

          {/* Grade-tonnage curve */}
          {option && (
            <div>
              <div className="mb-1 text-xs font-medium uppercase tracking-wider text-slate-400">
                Grade–Tonnage Curve
              </div>
              <ReactECharts option={option} style={{ height: 220 }} />
            </div>
          )}

          <div className="mt-2 text-xs text-slate-600">{data.note}</div>
        </>
      )}
    </div>
  );
}
