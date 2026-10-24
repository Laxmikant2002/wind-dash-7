import type { MetricSummary } from "../api";

export function MetricsCard({ metrics }: { metrics: MetricSummary }) {
  const cards = [
    ["MAE", `${metrics.mae_mw} MW`, "Mean absolute error"],
    ["RMSE", `${metrics.rmse_mw} MW`, "Root mean square error"],
    ["Bias", `${metrics.bias_mw > 0 ? "+" : ""}${metrics.bias_mw} MW`, "Positive means over-forecast"],
    ["WAPE", `${metrics.wape_percent}%`, "Weighted absolute percentage error"],
  ];

  return (
    <div className="metric-grid">
      {cards.map(([label, value, hint]) => (
        <article className="metric-card" key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
          <small>{hint}</small>
        </article>
      ))}
    </div>
  );
}
