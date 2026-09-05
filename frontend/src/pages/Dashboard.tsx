import { useEffect, useState, useCallback } from "react";
import {
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
import MapView from "../components/MapView";
import KpiCards from "../components/KpiCards";
import ProductionChart from "../components/ProductionChart";
import ForecastPanel from "../components/ForecastPanel";
import ActionsPanel from "../components/ActionsPanel";

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

  const baselineRainfall =
    production.length > 0
      ? production
          .slice(-90)
          .reduce((sum, p) => sum + (p.rainfall_mm ?? 0), 0) / Math.min(90, production.length)
      : 5;

  return (
    <div className="min-h-screen bg-[#0b0f14] p-6 text-gray-100">
      <header className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">OreSight — खनिज दृष्टि</h1>
          <p className="text-sm text-gray-400">
            {mine ? `${mine.name}, ${mine.state}` : "Loading mine…"}
          </p>
        </div>
        <DataHonestyBadge />
      </header>

      {error && (
        <div className="mb-4 rounded border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      <div className="mb-4">
        <KpiCards kpi={kpi} />
      </div>

      <div className="mb-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <MapView mine={mine} />
        <ProductionChart data={production} />
      </div>

      <div className="mb-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
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
    </div>
  );
}
