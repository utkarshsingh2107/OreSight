import type { Action, AuditEntry } from "../api/client";

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
  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-4">
      <div className="mb-2 flex items-center justify-between">
        <div className="text-sm font-medium text-gray-300">Prescriptive actions</div>
        <button
          onClick={onSuggest}
          disabled={loading}
          className="rounded bg-sky-500/20 px-3 py-1 text-xs font-medium text-sky-300 hover:bg-sky-500/30 disabled:opacity-50"
        >
          {loading ? "Ranking…" : "Suggest actions"}
        </button>
      </div>

      {actions.length === 0 ? (
        <div className="flex h-24 items-center justify-center text-sm text-gray-500">
          Click "Suggest actions" to rank corrective options.
        </div>
      ) : (
        <div className="space-y-2">
          {actions.map((a) => (
            <div
              key={a.name}
              className="flex items-center justify-between rounded border border-white/10 bg-black/20 p-3"
            >
              <div>
                <div className="text-sm font-medium text-white">{a.name}</div>
                <div className="text-xs text-gray-400">{a.rationale}</div>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-sm font-semibold text-emerald-400">
                  +{a.expected_delta_tonnes.toFixed(0)} t
                </div>
                <button
                  onClick={() => onApply(a)}
                  className="rounded bg-emerald-500/20 px-3 py-1 text-xs font-medium text-emerald-300 hover:bg-emerald-500/30"
                >
                  Apply
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-4">
        <div className="mb-1 text-xs uppercase tracking-wide text-gray-400">Audit log</div>
        {auditLog.length === 0 ? (
          <div className="text-xs text-gray-500">No actions applied yet.</div>
        ) : (
          <div className="space-y-1">
            {auditLog.map((entry) => (
              <div key={entry.id} className="flex justify-between text-xs text-gray-400">
                <span>
                  {entry.action_name} ({entry.applied_by})
                </span>
                <span>{new Date(entry.applied_at).toLocaleString()}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
