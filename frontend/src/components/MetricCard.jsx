export function MetricCard({ label, value, trend }) {
  const positive = trend?.startsWith('+');

  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <em className={positive ? 'trend-positive' : 'trend-negative'}>{trend}</em>
    </article>
  );
}
