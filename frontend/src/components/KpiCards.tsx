import type { Kpi } from "../api/client";

function RiskGauge({ probability }: { probability: number }) {
  const pct = Math.round(probability * 100);
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (pct / 100) * circumference;
  const color = pct > 60 ? "#f87171" : pct > 35 ? "#fb923c" : "#34d399";

  return (
    <div className="relative flex h-16 w-16 items-center justify-center">
      <svg className="absolute" width="64" height="64" style={{ transform: "rotate(-90deg)" }}>
        <circle cx="32" cy="32" r={radius} stroke="#1e293b" strokeWidth="6" fill="none" />
        <circle
          cx="32"
          cy="32"
          r={radius}
          stroke={color}
          strokeWidth="6"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.6s ease" }}
        />
      </svg>
      <span className="text-sm font-bold" style={{ color }}>{pct}%</span>
    </div>
  );
}

function StatCard({
  label,
  value,
  sub,
  accent,
  icon,
}: {
  label: string;
  value: string;
  sub?: string;
  accent?: string;
  icon: string;
}) {
  return (
    <div className="flex items-center gap-4 rounded-xl border border-white/10 bg-slate-800/60 p-4 backdrop-blur">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-white/5 text-xl">
        {icon}
      </div>
      <div className="min-w-0 flex-1">
        <div className="text-xs uppercase tracking-wider text-slate-400">{label}</div>
        <div className={`mt-0.5 text-xl font-bold ${accent ?? "text-white"}`}>{value}</div>
        {sub && <div className="text-xs text-slate-500">{sub}</div>}
      </div>
    </div>
  );
}

export default function KpiCards({ kpi }: { kpi: Kpi | null }) {
  if (!kpi) {
    return (
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {["Latest Output", "Month-to-date", "Monthly Target", "Shortfall Risk"].map((l) => (
          <div key={l} className="rounded-xl border border-white/10 bg-slate-800/60 p-4 backdrop-blur">
            <div className="text-xs uppercase tracking-wider text-slate-400">{l}</div>
            <div className="mt-2 h-6 w-24 animate-pulse rounded bg-slate-700" />
          </div>
        ))}
      </div>
    );
  }

  const pctOfTarget = Math.min(
    (kpi.mtd_actual_tonnes / kpi.monthly_target_tonnes) * 100,
    100,
  );
  const shortfallPct =
    kpi.shortfall_probability != null
      ? Math.round(kpi.shortfall_probability * 100)
      : null;

  const barColor =
    pctOfTarget >= 80 ? "bg-emerald-400" : pctOfTarget >= 50 ? "bg-amber-400" : "bg-red-400";

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {/* Latest output */}
      <StatCard
        icon="⛏️"
        label="Latest Daily Output"
        value={`${kpi.latest_tonnes.toLocaleString()} t`}
        accent="text-sky-300"
      />

      {/* MTD with progress bar */}
      <div className="rounded-xl border border-white/10 bg-slate-800/60 p-4 backdrop-blur">
        <div className="mb-2 flex items-center gap-2">
          <span className="text-xl">📦</span>
          <span className="text-xs uppercase tracking-wider text-slate-400">Month-to-date</span>
        </div>
        <div className="text-xl font-bold text-white">
          {kpi.mtd_actual_tonnes.toLocaleString()} t
        </div>
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-700">
          <div
            className={`h-2 rounded-full transition-all duration-700 ${barColor}`}
            style={{ width: `${pctOfTarget}%` }}
          />
        </div>
        <div className="mt-1 text-xs text-slate-500">{pctOfTarget.toFixed(0)}% of target</div>
      </div>

      {/* Target */}
      <StatCard
        icon="🎯"
        label="Monthly Target"
        value={`${kpi.monthly_target_tonnes.toLocaleString()} t`}
        accent="text-slate-200"
      />

      {/* Shortfall risk with gauge */}
      <div className="flex items-center gap-4 rounded-xl border border-white/10 bg-slate-800/60 p-4 backdrop-blur">
        {shortfallPct !== null && <RiskGauge probability={kpi.shortfall_probability!} />}
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-400">Shortfall Risk</div>
          <div
            className={`mt-0.5 text-xl font-bold ${
              shortfallPct !== null && shortfallPct > 60
                ? "text-red-400"
                : shortfallPct !== null && shortfallPct > 35
                  ? "text-amber-400"
                  : "text-emerald-400"
            }`}
          >
            {shortfallPct !== null ? `${shortfallPct}%` : "—"}
          </div>
          <div className="text-xs text-slate-500">
            {shortfallPct !== null && shortfallPct > 60
              ? "High — action needed"
              : shortfallPct !== null && shortfallPct > 35
                ? "Moderate — monitor"
                : "Low — on track"}
          </div>
        </div>
      </div>
    </div>
  );
}
