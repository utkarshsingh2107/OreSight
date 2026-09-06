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
  type Mine,
  type Kpi,
  type ProductionPoint,
  type Forecast,
  type Action,
  type AuditEntry,
} from "../api/client";
import DataHonestyBadge from "../components/DataHonestyBadge";
import ErrorBoundary from "../components/ErrorBoundary";
import MapView from "../components/MapView";
import KpiCards from "../components/KpiCards";
import ProductionChart from "../components/ProductionChart";
import ForecastPanel from "../components/ForecastPanel";
import ActionsPanel from "../components/ActionsPanel";
import ReservePanel from "../components/ReservePanel";
import ProspectivityPanel from "../components/ProspectivityPanel";
import EARExplainer from "../components/EARExplainer";
import EOConstraintsPanel from "../components/EOConstraintsPanel";
import ValidationMetrics from "../components/ValidationMetrics";
import MethodologyModal from "../components/MethodologyModal";

export default function Dashboard() {
  const [mine, setMine] = useState<Mine | null>(null);
  const [kpi, setKpi] = useState<Kpi | null>(null);
  const [production, setProduction] = useState<ProductionPoint[]>([]);
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [actions, setActions] = useState<Action[]>([]);
  const [actionsLoading, setActionsLoading] = useState(false);
  const [auditLog, setAuditLog] = useState<AuditEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [resetting, setResetting] = useState(false);
  const [showMethodology, setShowMethodology] = useState(false);

  useEffect(() => {
    getMines()
      .then((mines) => {
        if (mines.length === 0) {
          setError("No mines seeded yet — run scripts/seed.py.");
          return;
        }
        setMine(mines[0]);
      })
      .catch(() => setError("Could not reach the API — is the backend running?"));
  }, []);

  useEffect(() => {
    if (!mine) return;
    getKpi(mine.id).then(setKpi).catch(() => {});
    getProduction(mine.id).then(setProduction).catch(() => {});
    getAuditLog(mine.id).then(setAuditLog).catch(() => {});
    loadForecast(mine.id);
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

  return (
    <div className="min-h-screen bg-[#0b0f14] text-gray-100">
      <header className="sticky top-0 z-40 border-b border-gray-700 bg-gray-900/95 backdrop-blur supports-[backdrop-filter]:bg-gray-900/80 p-4 md:p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-lg md:text-xl font-bold text-white">OreSight — खनिज दृष्टि</h1>
            <p className="text-xs md:text-sm text-gray-400">
              {mine ? `${mine.name}, ${mine.state}` : "Loading mine…"}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2 md:gap-3">
            <button
              onClick={() => setShowMethodology(true)}
              className="rounded bg-blue-600/50 hover:bg-blue-600 px-2 md:px-3 py-1.5 md:py-2 text-xs font-medium text-white transition-colors"
              title="View methodology and assumptions"
            >
              ℹ️ Methodology
            </button>
            <button
              onClick={handleResetDemo}
              disabled={resetting}
              className="rounded bg-white/10 hover:bg-white/20 px-2 md:px-3 py-1.5 md:py-2 text-xs font-medium text-gray-200 transition-colors disabled:opacity-50"
            >
              {resetting ? "Resetting…" : "Reset"}
            </button>
            {mine && (
              <a
                href={`/api/mines/${mine.id}/report.pdf`}
                target="_blank"
                rel="noreferrer"
                className="rounded bg-white/10 hover:bg-white/20 px-2 md:px-3 py-1.5 md:py-2 text-xs font-medium text-gray-200 transition-colors"
              >
                📥 PDF
              </a>
            )}
            <DataHonestyBadge />
          </div>
        </div>
      </header>

      <MethodologyModal isOpen={showMethodology} onClose={() => setShowMethodology(false)} />

      <main className="p-4 md:p-6 space-y-4 md:space-y-6">
        {error && (
          <div className="rounded border border-red-500/40 bg-red-500/10 p-3 md:p-4 text-sm text-red-300">
            {error}
          </div>
        )}

        <ErrorBoundary>
          <div className="mb-4 md:mb-6">
            <KpiCards kpi={kpi} mineId={mine?.id} />
          </div>
        </ErrorBoundary>

        <ErrorBoundary>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <MapView mine={mine} />
            <ProductionChart data={production} />
          </div>
        </ErrorBoundary>

        {mine && (
          <ErrorBoundary>
            <div className="mb-4 md:mb-6">
              <ReservePanel mineId={mine.id} />
            </div>
          </ErrorBoundary>
        )}

        <ErrorBoundary>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <ForecastPanel
              forecast={forecast}
              baselineRainfall={baselineRainfall}
              loading={forecastLoading}
              onRainfallChange={(mm) => mine && loadForecast(mine.id, mm)}
            />
            <ActionsPanel
              actions={actions}
              auditLog={auditLog}
              loading={actionsLoading}
              onSuggest={handleSuggest}
              onApply={handleApply}
            />
          </div>
        </ErrorBoundary>

        {/* Priority Features */}
        {mine && (
          <>
            <ErrorBoundary>
              <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <ProspectivityPanel mineId={mine.id} />
                <EARExplainer mineId={mine.id} />
              </div>
            </ErrorBoundary>

            <ErrorBoundary>
              <EOConstraintsPanel mineId={mine.id} />
            </ErrorBoundary>

            <ErrorBoundary>
              <ValidationMetrics mineId={mine.id} />
            </ErrorBoundary>
          </>
        )}
      </main>
    </div>
  );
}
