import { useEffect, useState } from "react";
import { api } from "../api/client";
import ReactECharts from "echarts-for-react";

export interface ModelMetrics {
  model_name: string;
  mae: number; // Mean Absolute Error
  rmse: number; // Root Mean Squared Error
  r_squared: number; // R² score
  mape: number; // Mean Absolute Percentage Error
  confidence_interval_95: {
    lower: number;
    upper: number;
  };
  test_sample_size: number;
  sensitivity_analysis: {
    parameter: string;
    impact_percentage: number;
  }[];
}

export interface ValidationData {
  forecast_model: ModelMetrics;
  prospectivity_model: ModelMetrics;
  sensitivity_chart_data: {
    parameter: string;
    value: number;
  }[];
  reconciliation_status: string;
}

interface ValidationMetricsProps {
  mineId: number;
}

export default function ValidationMetrics({ mineId }: ValidationMetricsProps) {
  const [data, setData] = useState<ValidationData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"forecast" | "prospectivity">("forecast");

  useEffect(() => {
    setLoading(true);
    api
      .get<ValidationData>(`/validation-metrics`, { params: { mine_id: mineId } })
      .then((res) => {
        setData(res.data);
        setError(null);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || "Failed to load validation metrics");
      })
      .finally(() => setLoading(false));
  }, [mineId]);

  if (loading) {
    return (
      <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
        <div className="h-96 animate-pulse rounded bg-gray-700/50" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
        <p className="text-sm text-gray-400">No validation data available</p>
      </div>
    );
  }

  const activeMetrics = activeTab === "forecast" ? data.forecast_model : data.prospectivity_model;

  // Sensitivity chart
  const sensitivityChartOption = {
    xAxis: {
      type: "category",
      data: activeMetrics.sensitivity_analysis.map((s) => s.parameter),
      axisLabel: {
        interval: 0,
        rotate: 45,
      },
    },
    yAxis: {
      type: "value",
      name: "Impact (%)",
    },
    tooltip: {
      trigger: "axis",
      formatter: "{b}: {c}%",
    },
    grid: {
      left: 60,
      right: 20,
      top: 30,
      bottom: 80,
    },
    series: [
      {
        type: "bar",
        data: activeMetrics.sensitivity_analysis.map((s) => s.impact_percentage),
        itemStyle: {
          color: new (window as any).echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#3b82f6" },
            { offset: 1, color: "#1e40af" },
          ]),
        },
      },
    ],
  };

  const getMetricColor = (value: number, maxValue: number = 1) => {
    const percentage = value / maxValue;
    if (percentage > 0.85) return "text-green-400";
    if (percentage > 0.7) return "text-yellow-400";
    return "text-orange-400";
  };

  return (
    <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-white">Model Validation & Uncertainty</h2>
        <p className="text-xs text-gray-400">
          Performance metrics and sensitivity analysis
        </p>
      </div>

      {error && (
        <div className="mb-4 rounded border border-yellow-600/40 bg-yellow-600/10 p-2 text-xs text-yellow-300">
          {error}
        </div>
      )}

      {/* Reconciliation Status */}
      {data.reconciliation_status && (
        <div className="mb-4 rounded border border-blue-600/40 bg-blue-600/10 p-3">
          <p className="text-xs font-medium text-blue-300 mb-1">📊 Reconciliation Status</p>
          <p className="text-xs text-blue-200">{data.reconciliation_status}</p>
        </div>
      )}

      {/* Tab Selector */}
      <div className="mb-4 flex gap-2 border-b border-gray-600/50">
        <button
          onClick={() => setActiveTab("forecast")}
          className={`px-3 py-2 text-xs font-medium border-b-2 transition-colors ${
            activeTab === "forecast"
              ? "border-blue-500 text-blue-400"
              : "border-transparent text-gray-400 hover:text-gray-300"
          }`}
        >
          Forecast Model
        </button>
        <button
          onClick={() => setActiveTab("prospectivity")}
          className={`px-3 py-2 text-xs font-medium border-b-2 transition-colors ${
            activeTab === "prospectivity"
              ? "border-blue-500 text-blue-400"
              : "border-transparent text-gray-400 hover:text-gray-300"
          }`}
        >
          Prospectivity Model
        </button>
      </div>

      {/* Metrics Grid */}
      <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-3">
        <div className="rounded-lg border border-gray-600/50 bg-gray-900/30 p-3">
          <p className="text-xs text-gray-400 mb-1">MAE (Mean Absolute Error)</p>
          <p className="text-xl font-bold text-white">{activeMetrics.mae.toFixed(2)}</p>
          <p className="text-xs text-gray-500 mt-1">Lower is better</p>
        </div>

        <div className="rounded-lg border border-gray-600/50 bg-gray-900/30 p-3">
          <p className="text-xs text-gray-400 mb-1">RMSE</p>
          <p className="text-xl font-bold text-white">{activeMetrics.rmse.toFixed(2)}</p>
          <p className="text-xs text-gray-500 mt-1">Penalizes outliers</p>
        </div>

        <div className="rounded-lg border border-gray-600/50 bg-gray-900/30 p-3">
          <p className="text-xs text-gray-400 mb-1">R² (Coefficient)</p>
          <p className={`text-xl font-bold ${getMetricColor(activeMetrics.r_squared, 1)}`}>
            {(activeMetrics.r_squared * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">Variance explained</p>
        </div>

        <div className="rounded-lg border border-gray-600/50 bg-gray-900/30 p-3">
          <p className="text-xs text-gray-400 mb-1">MAPE</p>
          <p className={`text-xl font-bold ${getMetricColor(1 - activeMetrics.mape / 100, 1)}`}>
            {(activeMetrics.mape).toFixed(1)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">Mean % error</p>
        </div>

        <div className="rounded-lg border border-gray-600/50 bg-gray-900/30 p-3">
          <p className="text-xs text-gray-400 mb-1">95% Confidence Interval</p>
          <p className="text-sm font-mono text-blue-400">
            [{activeMetrics.confidence_interval_95.lower.toFixed(0)},
            <br />
            {activeMetrics.confidence_interval_95.upper.toFixed(0)}]
          </p>
          <p className="text-xs text-gray-500 mt-1">Range for 95% certainty</p>
        </div>

        <div className="rounded-lg border border-gray-600/50 bg-gray-900/30 p-3">
          <p className="text-xs text-gray-400 mb-1">Test Sample Size</p>
          <p className="text-xl font-bold text-white">{activeMetrics.test_sample_size}</p>
          <p className="text-xs text-gray-500 mt-1">Data points</p>
        </div>
      </div>

      {/* Sensitivity Analysis Chart */}
      <div className="mb-6 rounded-lg border border-gray-600/50 bg-gray-900/30 p-4">
        <p className="text-sm font-medium text-gray-300 mb-3">Sensitivity Analysis</p>
        <p className="text-xs text-gray-400 mb-3">
          How much each input parameter impacts the {activeTab === "forecast" ? "forecast" : "prospectivity"} result
        </p>
        <ReactECharts
          option={sensitivityChartOption}
          style={{ height: "300px", width: "100%" }}
          opts={{ renderer: "svg" }}
        />
      </div>

      {/* Key Insights */}
      <div className="rounded-lg border border-gray-600/50 bg-gray-900/30 p-4">
        <p className="text-sm font-medium text-gray-300 mb-3">Key Insights</p>
        <ul className="space-y-2 text-xs text-gray-300">
          <li className="flex gap-2">
            <span className="text-blue-400">•</span>
            <span>
              Model explains <strong>{(activeMetrics.r_squared * 100).toFixed(0)}%</strong> of variance in{" "}
              {activeTab === "forecast" ? "production shortfalls" : "manganese prospectivity"}
            </span>
          </li>
          <li className="flex gap-2">
            <span className="text-blue-400">•</span>
            <span>
              Average prediction error: <strong>{activeMetrics.mae.toFixed(1)}</strong> (±
              {activeMetrics.mape.toFixed(1)}%)
            </span>
          </li>
          <li className="flex gap-2">
            <span className="text-blue-400">•</span>
            <span>
              Tested on <strong>{activeMetrics.test_sample_size}</strong> independent data points using k-fold validation
            </span>
          </li>
          <li className="flex gap-2">
            <span className="text-blue-400">•</span>
            <span>
              Most sensitive to: <strong>{activeMetrics.sensitivity_analysis[0]?.parameter}</strong> (
              {activeMetrics.sensitivity_analysis[0]?.impact_percentage.toFixed(1)}% impact)
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
}
