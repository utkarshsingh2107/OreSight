import { useEffect, useState, useCallback } from "react";
import { getLiveWeather, type LiveWeather } from "../api/client";

const REFRESH_MS = 15 * 60 * 1000; // 15 minutes

function Stat({
  icon,
  label,
  value,
  unit,
  accent,
}: {
  icon: string;
  label: string;
  value: string | number;
  unit: string;
  accent?: string;
}) {
  return (
    <div className="flex flex-col items-center rounded-lg border border-white/10 bg-black/20 px-3 py-2.5 text-center">
      <span className="text-lg">{icon}</span>
      <div className={`mt-0.5 text-base font-bold ${accent ?? "text-white"}`}>
        {value}
        <span className="ml-0.5 text-xs font-normal text-slate-400">{unit}</span>
      </div>
      <div className="text-[10px] text-slate-500">{label}</div>
    </div>
  );
}

export default function LiveWeatherWidget({ mineId }: { mineId: number }) {
  const [data, setData] = useState<LiveWeather | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    getLiveWeather(mineId)
      .then((d) => {
        setData(d);
        setLastUpdated(new Date());
        setError(false);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [mineId]);

  useEffect(() => {
    load();
    const interval = setInterval(load, REFRESH_MS);
    return () => clearInterval(interval);
  }, [load]);

  return (
    <div className="rounded-xl border border-white/10 bg-slate-800/60 p-4 backdrop-blur">
      {/* Header */}
      <div className="mb-3 flex items-center gap-2">
        <span className="text-base">🛰️</span>
        <span className="text-sm font-semibold text-slate-200">Live Weather</span>
        {!loading && !error && (
          <span className="flex items-center gap-1 rounded-full border border-emerald-700/40 bg-emerald-900/30 px-2 py-0.5 text-[10px] font-semibold text-emerald-400">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
            LIVE
          </span>
        )}
        {loading && (
          <span className="ml-auto text-xs text-slate-500">Fetching…</span>
        )}
        {!loading && lastUpdated && (
          <span className="ml-auto text-[10px] text-slate-600">
            Updated {lastUpdated.toLocaleTimeString()}
          </span>
        )}
        <button
          onClick={load}
          disabled={loading}
          className="ml-1 rounded p-1 text-slate-500 hover:text-slate-300 disabled:opacity-40"
          title="Refresh"
        >
          🔄
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-amber-700/40 bg-amber-900/20 px-3 py-2 text-xs text-amber-300">
          ⚠️ Could not fetch live weather. Check internet connection.
        </div>
      )}

      {data && (
        <>
          <div className="mb-2 grid grid-cols-2 gap-2 sm:grid-cols-4">
            <Stat
              icon="🌧️"
              label="Rainfall today"
              value={data.rainfall_mm}
              unit="mm"
              accent={data.rainfall_mm > 20 ? "text-red-400" : data.rainfall_mm > 5 ? "text-sky-300" : "text-slate-200"}
            />
            <Stat
              icon="🌡️"
              label="Max temperature"
              value={data.temperature_max_c}
              unit="°C"
              accent={data.temperature_max_c > 40 ? "text-red-400" : "text-orange-300"}
            />
            <Stat
              icon="💧"
              label="Soil moisture"
              value={data.soil_moisture_m3m3}
              unit="m³/m³"
              accent="text-blue-300"
            />
            <Stat
              icon="💨"
              label="Wind speed"
              value={data.wind_speed_kmh}
              unit="km/h"
              accent="text-slate-200"
            />
          </div>

          {/* 7-day averages row */}
          <div className="flex gap-3 text-xs text-slate-500">
            <span>7-day avg rainfall: <span className="text-slate-300">{data.rainfall_7d_avg_mm} mm/day</span></span>
            <span>·</span>
            <span>7-day avg temp: <span className="text-slate-300">{data.temperature_7d_avg_c}°C</span></span>
          </div>

          <div className="mt-2 text-[10px] text-slate-600">
            Source: {data.source} · {data.date}
          </div>
        </>
      )}

      {!data && !loading && !error && (
        <div className="text-xs text-slate-500">No weather data available.</div>
      )}
    </div>
  );
}
