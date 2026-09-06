import type { Action, AuditEntry } from "../api/client";

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function ImpactBadge({ delta }: { delta: number }) {
  const label = delta > 1500 ? "High" : delta > 800 ? "Medium" : "Low";
  const color =
    delta > 1500
      ? "bg-emerald-500/25 text-emerald-300 border-emerald-700/40"
      : delta > 800
        ? "bg-amber-500/25 text-amber-300 border-amber-700/40"
        : "bg-slate-500/25 text-slate-300 border-slate-600/40";
  return (
    <span className={`rounded border px-2 py-0.5 text-[10px] font-semibold ${color}`}>
      {label}
    </span>
  );
}

export default function ActionsPanel({
  actions,
  auditLog,
  onSuggest,
  onApply,
  loading,
}: {
  actions: Action[];
  auditLog: AuditEntry[];
  onSuggest: () => void;
  onApply: (action: Action) => void;
  loading: boolean;
}) {
  const maxDelta = actions.length > 0 ? Math.max(...actions.map((a) => a.expected_delta_tonnes)) : 1;

  return (
    <div className="rounded-xl border border-white/10 bg-slate-800/60 p-4 backdrop-blur">
      {/* Header */}
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-base">⚡</span>
          <span className="text-sm font-semibold text-slate-200">Prescriptive Actions</span>
        </div>
        <button
          onClick={onSuggest}
          disabled={loading}
          className="flex items-center gap-1.5 rounded-lg bg-sky-500/20 px-3 py-1.5 text-xs font-semibold text-sky-300 transition hover:bg-sky-500/30 disabled:opacity-50 border border-sky-700/40"
        >
          {loading ? (
            <>
              <svg className="h-3 w-3 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Ranking…
            </>
          ) : (
            <>✨ Suggest Actions</>
          )}
        </button>
      </div>

      {/* Actions list */}
      {actions.length === 0 ? (
        <div className="flex h-24 items-center justify-center rounded-lg border border-dashed border-slate-700 text-sm text-slate-500">
          Click "Suggest Actions" to get ML-ranked corrective options
        </div>
      ) : (
        <div className="space-y-2">
          {actions.map((a) => (
            <div
              key={a.name}
              className="rounded-lg border border-white/10 bg-black/20 p-3 transition hover:border-white/20"
            >
              <div className="mb-1.5 flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-white">{a.name}</span>
                    <ImpactBadge delta={a.expected_delta_tonnes} />
                  </div>
                  <div className="mt-0.5 text-xs text-slate-400">{a.rationale}</div>
                </div>
                <div className="flex shrink-0 flex-col items-end gap-1.5">
                  <span className="text-base font-bold text-emerald-400">
                    +{a.expected_delta_tonnes.toFixed(0)} t
                  </span>
                  <button
                    onClick={() => onApply(a)}
                    className="rounded-lg bg-emerald-500/20 px-3 py-1 text-xs font-semibold text-emerald-300 transition hover:bg-emerald-500/30 border border-emerald-700/40"
                  >
                    Apply
                  </button>
                </div>
              </div>
              {/* Impact bar */}
              <div className="mt-1.5 h-1 w-full overflow-hidden rounded-full bg-slate-700">
                <div
                  className="h-1 rounded-full bg-emerald-400 transition-all duration-500"
                  style={{ width: `${(a.expected_delta_tonnes / maxDelta) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Audit log */}
      <div className="mt-4">
        <div className="mb-2 text-xs font-medium uppercase tracking-wider text-slate-400">
          📋 Audit Log
        </div>
        {auditLog.length === 0 ? (
          <div className="text-xs text-slate-600">No actions applied yet.</div>
        ) : (
          <div className="space-y-1.5">
            {auditLog.slice(0, 5).map((entry) => (
              <div
                key={entry.id}
                className="flex items-center justify-between rounded border border-white/5 bg-black/20 px-2.5 py-1.5 text-xs"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />
                  <span className="truncate text-slate-300">{entry.action_name}</span>
                  <span className="text-slate-500">by {entry.applied_by}</span>
                </div>
                <span className="shrink-0 text-slate-500">{timeAgo(entry.applied_at)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
