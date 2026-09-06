import { useEffect, useState } from "react";
import { api } from "../api/client";
import ReactECharts from "echarts-for-react";

export interface ConstraintData {
  date: string;
  rainfall_constraint: number;
  soil_moisture_constraint: number;
  temperature_constraint: number;
  vegetation_constraint: number;
}

export interface ConstraintForecast {
  current: ConstraintData;
  forecast_7day: ConstraintData[];
  historical_correlation: {
    rainfall: number;
    soil_moisture: number;
    temperature: number;
  };
}

interface EOConstraintsPanelProps {
  mineId: number;
}

export default function EOConstraintsPanel({ mineId }: EOConstraintsPanelProps) {
  const [data, setData] = useState<ConstraintForecast | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api
      .get<ConstraintForecast>(`/eo-constraints`, { params: { mine_id: mineId } })
      .then((res) => {
        setData(res.data);
        setError(null);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || "Failed to load constraint data");
      })
      .finally(() => setLoading(false));
  }, [mineId]);

  if (loading) {
    return (
      <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
        <div className="h-80 animate-pulse rounded bg-gray-700/50" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
        <p className="text-sm text-gray-400">No constraint data available</p>
      </div>
    );
  }

  // Prepare chart data for 7-day forecast
  const chartData = {
    xAxis: {
      type: "category",
      data: data.forecast_7day.map((_, i) => `Day ${i + 1}`),
      boundaryGap: false,
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 1,
    },
    tooltip: {
      trigger: "axis",
    },
    legend: {
      data: ["Rainfall", "Soil Moisture", "Temperature", "Vegetation"],
    },
    series: [
      {
        name: "Rainfall",
        type: "line",
        data: data.forecast_7day.map((d) => d.rainfall_constraint),
        smooth: true,
        itemStyle: { color: "#3b82f6" },
        areaStyle: { color: "rgba(59, 130, 246, 0.2)" },
      },
      {
        name: "Soil Moisture",
        type: "line",
        data: data.forecast_7day.map((d) => d.soil_moisture_constraint),
        smooth: true,
        itemStyle: { color: "#8b5cf6" },
        areaStyle: { color: "rgba(139, 92, 246, 0.2)" },
      },
      {
        name: "Temperature",
        type: "line",
        data: data.forecast_7day.map((d) => d.temperature_constraint),
        smooth: true,
        itemStyle: { color: "#ec4899" },
        areaStyle: { color: "rgba(236, 72, 153, 0.2)" },
      },
      {
        name: "Vegetation",
        type: "line",
        data: data.forecast_7day.map((d) => d.vegetation_constraint),
        smooth: true,
        itemStyle: { color: "#10b981" },
        areaStyle: { color: "rgba(16, 185, 129, 0.2)" },
      },
    ],
  };

  // Get constraint status and color
  const getConstraintStatus = (value: number) => {
    if (value > 0.8) return { label: "Good", color: "text-green-400", bgColor: "bg-green-600/20" };
    if (value > 0.6) return { label: "Moderate", color: "text-yellow-400", bgColor: "bg-yellow-600/20" };
    if (value > 0.4) return { label: "Caution", color: "text-orange-400", bgColor: "bg-orange-600/20" };
    return { label: "Poor", color: "text-red-400", bgColor: "bg-red-600/20" };
  };

  const rainfallStatus = getConstraintStatus(data.current.rainfall_constraint);
  const soilStatus = getConstraintStatus(data.current.soil_moisture_constraint);
  const tempStatus = getConstraintStatus(data.current.temperature_constraint);
  const vegStatus = getConstraintStatus(data.current.vegetation_constraint);

  return (
    <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-white">Operational Constraints</h2>
        <p className="text-xs text-gray-400">
          Multi-source satellite data showing production constraints
        </p>
      </div>

      {error && (
        <div className="mb-4 rounded border border-yellow-600/40 bg-yellow-600/10 p-2 text-xs text-yellow-300">
          {error}
        </div>
      )}

      {/* Current Constraints */}
      <div className="mb-6 grid grid-cols-2 gap-2 md:grid-cols-4">
        <div
          className={`rounded-lg border border-gray-600/50 ${rainfallStatus.bgColor} p-3`}
        >
          <p className="text-xs text-gray-400 mb-1">🌧️ Rainfall</p>
          <p className={`text-lg font-bold ${rainfallStatus.color}`}>
            {(data.current.rainfall_constraint * 100).toFixed(0)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">{rainfallStatus.label}</p>
        </div>

        <div
          className={`rounded-lg border border-gray-600/50 ${soilStatus.bgColor} p-3`}
        >
          <p className="text-xs text-gray-400 mb-1">💧 Soil Moisture</p>
          <p className={`text-lg font-bold ${soilStatus.color}`}>
            {(data.current.soil_moisture_constraint * 100).toFixed(0)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">{soilStatus.label}</p>
        </div>

        <div
          className={`rounded-lg border border-gray-600/50 ${tempStatus.bgColor} p-3`}
        >
          <p className="text-xs text-gray-400 mb-1">🌡️ Temperature</p>
          <p className={`text-lg font-bold ${tempStatus.color}`}>
            {(data.current.temperature_constraint * 100).toFixed(0)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">{tempStatus.label}</p>
        </div>

        <div
          className={`rounded-lg border border-gray-600/50 ${vegStatus.bgColor} p-3`}
        >
          <p className="text-xs text-gray-400 mb-1">🌱 Vegetation (NDVI)</p>
          <p className={`text-lg font-bold ${vegStatus.color}`}>
            {(data.current.vegetation_constraint * 100).toFixed(0)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">{vegStatus.label}</p>
        </div>
      </div>

      {/* 7-Day Forecast Chart */}
      <div className="mb-6 rounded-lg border border-gray-600/50 bg-gray-900/30 p-4">
        <p className="text-sm font-medium text-gray-300 mb-3">7-Day Constraint Forecast</p>
        <ReactECharts
          option={chartData}
          style={{ height: "250px", width: "100%" }}
          opts={{ renderer: "svg" }}
        />
      </div>

      {/* Historical Correlation */}
      <div className="rounded-lg border border-gray-600/50 bg-gray-900/30 p-4">
        <p className="text-sm font-medium text-gray-300 mb-3">Historical Production Correlation</p>
        <div className="space-y-2">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-400">Rainfall Impact on Production</span>
              <span className="text-xs font-mono text-blue-400">
                {(data.historical_correlation.rainfall * 100).toFixed(1)}%
              </span>
            </div>
            <div className="h-2 rounded-full bg-gray-700 overflow-hidden">
              <div
                className="h-full bg-blue-500"
                style={{ width: `${data.historical_correlation.rainfall * 100}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-400">Soil Moisture Impact</span>
              <span className="text-xs font-mono text-purple-400">
                {(data.historical_correlation.soil_moisture * 100).toFixed(1)}%
              </span>
            </div>
            <div className="h-2 rounded-full bg-gray-700 overflow-hidden">
              <div
                className="h-full bg-purple-500"
                style={{ width: `${data.historical_correlation.soil_moisture * 100}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-400">Temperature Impact</span>
              <span className="text-xs font-mono text-pink-400">
                {(data.historical_correlation.temperature * 100).toFixed(1)}%
              </span>
            </div>
            <div className="h-2 rounded-full bg-gray-700 overflow-hidden">
              <div
                className="h-full bg-pink-500"
                style={{ width: `${data.historical_correlation.temperature * 100}%` }}
              />
            </div>
          </div>
        </div>

        <p className="text-xs text-gray-500 mt-3 leading-relaxed">
          These correlations show how each satellite-derived constraint historically impacted actual production.
          Higher values indicate stronger predictive power.
        </p>
      </div>
    </div>
  );
}
