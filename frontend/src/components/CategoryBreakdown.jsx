const COLORS = [
  '#2c8c7c', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
];

const BAR_H = 28;
const GAP = 6;

export default function CategoryBreakdown({ data }) {
  if (!data || data.length === 0) {
    return <div className="chart-empty">No findings data available yet</div>;
  }

  const top = data.slice(0, 10);
  const maxCount = Math.max(...top.map((d) => d.count));
  const totalH = top.length * (BAR_H + GAP);

  return (
    <div className="category-chart">
      <svg viewBox={`0 0 500 ${totalH}`} className="chart-svg" style={{ height: totalH }}>
        {top.map((d, i) => {
          const y = i * (BAR_H + GAP);
          const barW = (d.count / maxCount) * 320;
          return (
            <g key={d.category}>
              <text x="0" y={y + BAR_H / 2 + 5} className="cat-label">{d.category}</text>
              <rect x="130" y={y + 2} width={barW} height={BAR_H - 4} rx="4" fill={COLORS[i % COLORS.length]} opacity="0.85" />
              <text x={130 + barW + 8} y={y + BAR_H / 2 + 5} className="cat-count">{d.count}</text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
