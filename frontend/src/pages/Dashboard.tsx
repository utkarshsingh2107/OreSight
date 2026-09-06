import { useEffect, useState, useCallback } from "react";
import {
  api,
  getMines,
  getKpi,
  getProduction,
  getForecast,
  getSuggestedActions,
  applyAction,
  getAuditLog,
  getProspectivityTargets,
  type Mine,
  type Kpi,
  type ProductionPoint,
  type Forecast,
  type Action,
  type AuditEntry,
  type ProspectivityTarget,
} from "../api/client";
import MapView from "../components/MapView";
import KpiCards from "../components/KpiCards";
import ProductionChart from "../components/ProductionChart";
import ForecastPanel from "../components/ForecastPanel";
import ActionsPanel from "../components/ActionsPanel";
import ReservePanel from "../components/ReservePanel";
import ProspectivityPanel from "../components/ProspectivityPanel";
import LiveWeatherWidget from "../components/LiveWeatherWidget";

type Tab = "overview" | "reserves" | "forecast" | "prospectivity" | "actions";

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: "overview", label: "Overview", icon: "📊" },
  { id: "reserves", label: "Reserves & EAR", icon: "🪨" },
  { id: "forecast", label: "Forecast", icon: "🔮" },
  { id: "prospectivity", label: "Prospectivity", icon: "🛰️" },
  { id: "actions", label: "Actions", icon: "⚡" },
];

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<Tab>("overview");
  const [mines, setMines] = useState<Mine[]>([]);
  const [mine, setMine] = useState<Mine | null>(null);
  const [kpi, setKpi] = useState<Kpi | null>(null);
  const [production, setProduction] = useState<ProductionPoint[]>([]);
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [actions, setActions] = useState<Action[]>([]);
  const [actionsLoading, setActionsLoading] = useState(false);
  const [auditLog, setAuditLog] = useState<AuditEntry[]>([]);
  const [prospectivityTargets, setProspectivityTargets] = useState<ProspectivityTarget[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [resetting, setResetting] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    getMines()
      .then((ms) => {
        if (ms.length === 0) {
          setError("No mines seeded — run scripts/seed_all_mines.py.");
          return;
        }
        setMines(ms);
        setMine(ms[0]);
      })
      .catch(() => setError("Cannot reach API — is the backend running?"));
  }, []);

  useEffect(() => {
    if (!mine) return;
    getKpi(mine.id).then(setKpi).catch(() => {});
    getProduction(mine.id).then(setProduction).catch(() => {});
    getAuditLog(mine.id).then(setAuditLog).catch(() => {});
    loadForecast(mine.id);
    // Load prospectivity targets for map
    getProspectivityTargets(10)
      .then((r) => setProspectivityTargets(r.targets))
      .catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mine]);

  const loadForecast = useCallback((mineId: number, rainfallMm?: number) => {
    setForecastLoading(true);
    getForecast(mineId, 30, rainfallMm)
      .then(setForecast)
      .catch(() => {})
      .finally(() => setForecastLoading(false));
  }, []);

  const handleSuggest = () => {
    if (!mine) return;
    setActionsLoading(true);
    getSuggestedActions(mine.id)
      .then(setActions)
      .finally(() => setActionsLoading(false));
  };

  const handleApply = (action: Action) => {
    if (!mine) return;
    applyAction(mine.id, action).then(() => getAuditLog(mine.id).then(setAuditLog));
  };

  const handleResetDemo = () => {
    setResetting(true);
    api
      .post("/admin/reset-demo")
      .then(() => window.location.reload())
      .catch(() => setResetting(false));
  };

  const baselineRainfall =
    production.length > 0
      ? production
          .slice(-90)
          .reduce((sum, p) => sum + (p.rainfall_mm ?? 0), 0) / Math.min(90, production.length)
      : 5;

  const shortfallPct =
    kpi?.shortfall_probability != null ? Math.round(kpi.shortfall_probability * 100) : null;

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      {/* Sidebar */}
      <aside
        className={`flex flex-col border-r border-white/10 bg-slate-900/80 backdrop-blur transition-all duration-300 ${
          sidebarOpen ? "w-52" : "w-14"
        }`}
      >
        {/* Brand */}
        <div className="flex items-center gap-3 border-b border-white/10 px-3 py-4">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-amber-500/20 text-lg">
            ⛏️
          </div>
          {sidebarOpen && (
            <div className="min-w-0">
              <div className="truncate text-sm font-bold text-white">OreSight</div>
              <div className="truncate text-[10px] text-slate-500">खनिज दृष्टि</div>
            </div>
          )}
          <button
            onClick={() => setSidebarOpen((v) => !v)}
            className="ml-auto shrink-0 rounded p-1 text-slate-500 hover:bg-white/5 hover:text-slate-300"
          >
            {sidebarOpen ? "◀" : "▶"}
          </button>
        </div>

        {/* Mine selector */}
        {sidebarOpen && mines.length > 0 && (
          <div className="mx-3 mt-3">
            <div className="mb-1 text-[10px] uppercase tracking-wider text-slate-500">Active Mine</div>
            <select
              value={mine?.id ?? ""}
              onChange={(e) => {
                const selected = mines.find((m) => m.id === parseInt(e.target.value));
                if (selected) setMine(selected);
              }}
              className="w-full rounded-lg border border-white/10 bg-slate-700/60 px-2.5 py-1.5 text-xs font-semibold text-sky-300 focus:outline-none focus:ring-1 focus:ring-sky-500"
            >
              {mines.map((m) => (
                <option key={m.id} value={m.id} className="bg-slate-800 text-white">
                  {m.name} ({m.mine_type})
                </option>
              ))}
            </select>
            {mine && (
              <div className="mt-1 text-[10px] text-slate-500">
                {mine.state} · Target: {mine.monthly_target_tonnes.toLocaleString()} t/mo
              </div>
            )}
          </div>
        )}

        {/* Shortfall indicator */}
        {sidebarOpen && shortfallPct !== null && (
          <div className={`mx-3 mt-2 rounded-lg border px-2.5 py-1.5 text-xs ${
            shortfallPct > 60
              ? "border-red-700/40 bg-red-900/20 text-red-300"
              : shortfallPct > 35
                ? "border-amber-700/40 bg-amber-900/20 text-amber-300"
                : "border-emerald-700/40 bg-emerald-900/20 text-emerald-300"
          }`}>
            <div className="text-[10px] uppercase tracking-wider opacity-70">Shortfall Risk</div>
            <div className="text-sm font-bold">{shortfallPct}%</div>
          </div>
        )}

        {/* Nav items */}
        <nav className="mt-4 flex-1 space-y-0.5 px-2">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex w-full items-center gap-3 rounded-lg px-2.5 py-2.5 text-left text-sm transition ${
                activeTab === tab.id
                  ? "bg-sky-500/20 text-sky-300 font-semibold"
                  : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
              }`}
            >
              <span className="shrink-0 text-base">{tab.icon}</span>
              {sidebarOpen && <span className="truncate">{tab.label}</span>}
              {activeTab === tab.id && sidebarOpen && (
                <span className="ml-auto h-1.5 w-1.5 rounded-full bg-sky-400" />
              )}
            </button>
          ))}
        </nav>

        {/* Bottom actions */}
        <div className="border-t border-white/10 p-2 space-y-1">
          {mine && (
            <a
              href={`/api/mines/${mine.id}/report.pdf`}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 rounded-lg px-2.5 py-2 text-xs text-slate-400 hover:bg-white/5 hover:text-slate-200 transition"
            >
              <span className="text-base">📄</span>
              {sidebarOpen && "Download PDF"}
            </a>
          )}
          <button
            onClick={handleResetDemo}
            disabled={resetting}
            className="flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-xs text-slate-500 hover:bg-white/5 hover:text-slate-300 disabled:opacity-40 transition"
          >
            <span className="text-base">🔄</span>
            {sidebarOpen && (resetting ? "Resetting…" : "Reset demo")}
          </button>
        </div>

        {/* Data honesty badge */}
        {sidebarOpen && (
          <div className="border-t border-white/10 px-3 py-2">
            <div className="rounded border border-amber-700/40 bg-amber-900/20 px-2 py-1.5 text-[10px] text-amber-400">
              ⚠️ Synthetic geometry · Real rainfall & satellite data
            </div>
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className="flex flex-1 flex-col min-w-0">
        {/* Top bar */}
        <header className="sticky top-0 z-10 flex items-center justify-between border-b border-white/10 bg-slate-900/80 px-6 py-3 backdrop-blur">
          <div>
            <h1 className="text-base font-bold text-white">
              {TABS.find((t) => t.id === activeTab)?.icon}{" "}
              {TABS.find((t) => t.id === activeTab)?.label}
            </h1>
            {mine && (
              <p className="text-xs text-slate-500">
                {mine.name}, {mine.state} · MOIL Limited
              </p>
            )}
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_6px_#34d399]" />
            Live
          </div>
        </header>

        {/* Error banner */}
        {error && (
          <div className="mx-6 mt-4 rounded-xl border border-red-700/40 bg-red-900/20 px-4 py-3 text-sm text-red-300">
            ⚠️ {error}
          </div>
        )}

        {/* Tab content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* ── OVERVIEW ── */}
          {activeTab === "overview" && (
            <div className="space-y-4">
              <KpiCards kpi={kpi} />
              {mine && <LiveWeatherWidget mineId={mine.id} />}
              <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
                <MapView
                  mine={mine}
                  allMines={mines}
                  onSelectMine={setMine}
                  prospectivityTargets={prospectivityTargets}
                />
                <ProductionChart data={production} />
              </div>
            </div>
          )}

          {/* ── RESERVES ── */}
          {activeTab === "reserves" && mine && (
            <ReservePanel mineId={mine.id} />
          )}

          {/* ── FORECAST ── */}
          {activeTab === "forecast" && (
            <div className="max-w-3xl">
              <ForecastPanel
                forecast={forecast}
                baselineRainfall={baselineRainfall}
                loading={forecastLoading}
                onRainfallChange={(mm) => mine && loadForecast(mine.id, mm)}
              />
            </div>
          )}

          {/* ── PROSPECTIVITY ── */}
          {activeTab === "prospectivity" && (
            <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
              <ProspectivityPanel />
              <MapView
                mine={mine}
                allMines={mines}
                onSelectMine={setMine}
                prospectivityTargets={prospectivityTargets}
              />
            </div>
          )}

          {/* ── ACTIONS ── */}
          {activeTab === "actions" && (
            <div className="max-w-2xl">
              <ActionsPanel
                actions={actions}
                auditLog={auditLog}
                loading={actionsLoading}
                onSuggest={handleSuggest}
                onApply={handleApply}
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
