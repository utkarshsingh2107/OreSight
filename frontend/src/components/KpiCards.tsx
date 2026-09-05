import type { Kpi } from "../api/client";

function Card({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <div className="flex-1 rounded-lg border border-white/10 bg-white/5 p-4">
      <div className="text-xs uppercase tracking-wide text-gray-400">{label}</div>
      <div className={`mt-1 text-2xl font-semibold ${accent ?? "text-white"}`}>{value}</div>
    </div>
  );
}

export default function KpiCards({ kpi }: { kpi: Kpi | null }) {
  if (!kpi) {
    return (
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-4">
        {["Latest daily output", "Month-to-date", "Monthly target", "Shortfall risk"].map((l) => (
          <Card key={l} label={l} value="—" />
        ))}
      </div>
    );
  }

  const pctOfTarget = (kpi.mtd_actual_tonnes / kpi.monthly_target_tonnes) * 100;
  const shortfallPct =
    kpi.shortfall_probability != null ? `${Math.round(kpi.shortfall_probability * 100)}%` : "—";

  return (
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
  );
}
