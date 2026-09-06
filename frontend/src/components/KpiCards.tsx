import { useEffect, useState } from "react";
import type { Kpi, EARData } from "../api/client";
import { api } from "../api/client";

function Card({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <div className="flex-1 rounded-lg border border-gray-700 bg-gray-800/50 p-4">
      <div className="text-xs uppercase tracking-wide text-gray-400">{label}</div>
      <div className={`mt-1 text-2xl font-semibold ${accent ?? "text-white"}`}>{value}</div>
    </div>
  );
}

interface KpiCardsProps {
  kpi: Kpi | null;
  mineId?: number;
}

export default function KpiCards({ kpi, mineId }: KpiCardsProps) {
  const [earData, setEarData] = useState<EARData | null>(null);
  const [showEarBreakdown, setShowEarBreakdown] = useState(false);

  useEffect(() => {
    if (!mineId) return;
    api
      .get<EARData>(`/ear`, { params: { mine_id: mineId } })
      .then((res) => setEarData(res.data))
      .catch(() => {});
  }, [mineId]);

  if (!kpi) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-4">
          {["Latest daily output", "Month-to-date", "Monthly target", "Shortfall risk"].map((l) => (
            <Card key={l} label={l} value="—" />
          ))}
        </div>
      </div>
    );
  }

  const pctOfTarget = (kpi.mtd_actual_tonnes / kpi.monthly_target_tonnes) * 100;
  const shortfallPct =
    kpi.shortfall_probability != null ? `${Math.round(kpi.shortfall_probability * 100)}%` : "—";

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-4">
        <Card label="Latest daily output" value={`${kpi.latest_tonnes.toLocaleString()} t`} />
        <Card
          label="Month-to-date"
          value={`${kpi.mtd_actual_tonnes.toLocaleString()} t (${pctOfTarget.toFixed(0)}%)`}
        />
        <Card label="Monthly target" value={`${kpi.monthly_target_tonnes.toLocaleString()} t`} />
        <Card
          label="Shortfall risk"
          value={shortfallPct}
          accent={
            kpi.shortfall_probability != null && kpi.shortfall_probability > 0.4
              ? "text-red-400"
              : "text-emerald-400"
          }
        />
      </div>

      {/* EAR Breakdown Section */}
      {earData && (
        <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
          <button
            onClick={() => setShowEarBreakdown(!showEarBreakdown)}
            className="w-full flex items-center justify-between cursor-pointer hover:opacity-80 transition-opacity"
          >
            <div>
              <h3 className="text-sm font-semibold text-white">Effective Accessible Reserve (EAR)</h3>
              <p className="text-xs text-gray-400">Geological reserve × accessibility factors</p>
            </div>
            <span className={`text-2xl transition-transform ${showEarBreakdown ? "rotate-180" : ""}`}>
              ▼
            </span>
          </button>

          {showEarBreakdown && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Left: Main EAR Flow */}
              <div className="space-y-3">
                <div className="rounded-lg bg-gradient-to-r from-blue-600/20 to-blue-600/10 border border-blue-600/40 p-3">
                  <p className="text-xs text-gray-400 mb-1">Geological Reserve</p>
                  <p className="text-2xl font-bold text-blue-300">
                    {(earData.geological_reserve_tonnes / 1000).toFixed(1)}k t
                  </p>
                </div>

                <div className="text-center text-gray-400 text-xs">↓</div>

                <div className="text-xs text-gray-400 space-y-1 bg-gray-900/50 rounded p-2">
                  <p>Accessibility Multipliers:</p>
                  <div className="grid grid-cols-2 gap-1 text-xs">
                    <span>Depth: {(earData.depth_factor * 100).toFixed(0)}%</span>
                    <span>Equipment: {(earData.equipment_factor * 100).toFixed(0)}%</span>
                    <span>Climate: {(earData.climate_factor * 100).toFixed(0)}%</span>
                    <span>Regulatory: {(earData.regulatory_factor * 100).toFixed(0)}%</span>
                    <span>Infrastructure: {(earData.infrastructure_factor * 100).toFixed(0)}%</span>
                  </div>
                </div>

                <div className="text-center text-gray-400 text-xs">↓</div>

                <div className="rounded-lg bg-gradient-to-r from-green-600/20 to-green-600/10 border border-green-600/40 p-3">
                  <p className="text-xs text-gray-400 mb-1">Effective Accessible Reserve</p>
                  <p className="text-2xl font-bold text-green-300">
                    {(earData.total_ear_tonnes / 1000).toFixed(1)}k t
                  </p>
                </div>
              </div>

              {/* Right: Factor Breakdown Bars */}
              <div className="space-y-2">
                <p className="text-xs font-medium text-gray-300">Factor Breakdown</p>
                {[
                  { label: "Depth", value: earData.depth_factor, color: "from-blue-500 to-cyan-500" },
                  { label: "Equipment", value: earData.equipment_factor, color: "from-purple-500 to-pink-500" },
                  { label: "Climate", value: earData.climate_factor, color: "from-orange-500 to-red-500" },
                  { label: "Regulatory", value: earData.regulatory_factor, color: "from-yellow-500 to-orange-500" },
                  { label: "Infrastructure", value: earData.infrastructure_factor, color: "from-green-500 to-emerald-500" },
                ].map((factor) => (
                  <div key={factor.label}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-gray-400">{factor.label}</span>
                      <span className="text-xs font-mono text-gray-300">
                        {(factor.value * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="h-2 rounded-full bg-gray-700 overflow-hidden">
                      <div
                        className={`h-full bg-gradient-to-r ${factor.color}`}
                        style={{ width: `${factor.value * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {earData.blocks_at_risk > 0 && (
            <div className="mt-3 rounded border border-orange-600/40 bg-orange-600/10 p-2">
              <p className="text-xs text-orange-300">
                ⚠️ {earData.blocks_at_risk} blocks at risk. {earData.risk_description}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
