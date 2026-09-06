import { useState } from 'react';

const CHART_W = 600;
const CHART_H = 200;
const PAD = { top: 20, right: 20, bottom: 40, left: 45 };

export default function ScoreTrendChart({ data }) {
  const [hovered, setHovered] = useState(null);

  if (!data || data.length === 0) {
    return <div className="chart-empty">No score data available yet</div>;
  }

  const w = CHART_W - PAD.left - PAD.right;
  const h = CHART_H - PAD.top - PAD.bottom;
  const maxScore = 10;
  const minScore = 0;

  const xScale = (i) => PAD.left + (i / Math.max(data.length - 1, 1)) * w;
  const yScale = (v) => PAD.top + h - ((v - minScore) / (maxScore - minScore)) * h;

  const points = data.map((d, i) => ({ x: xScale(i), y: yScale(d.avg_score), ...d }));
  const linePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ');
  const areaPath = `${linePath} L${points[points.length - 1].x},${PAD.top + h} L${points[0].x},${PAD.top + h} Z`;

  const yTicks = [0, 2.5, 5, 7.5, 10];

  return (
    <div className="chart-container">
      <svg viewBox={`0 0 ${CHART_W} ${CHART_H}`} className="chart-svg">
        {yTicks.map((t) => (
          <g key={t}>
            <line x1={PAD.left} y1={yScale(t)} x2={CHART_W - PAD.right} y2={yScale(t)} className="chart-grid" />
            <text x={PAD.left - 8} y={yScale(t) + 4} className="chart-label-y">{t}</text>
          </g>
        ))}

        <path d={areaPath} className="chart-area" />
        <path d={linePath} className="chart-line" />

        {points.map((p, i) => (
          <g key={i}>
            <circle
              cx={p.x} cy={p.y} r={hovered === i ? 5 : 3}
              className="chart-dot"
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
            />
            {i % Math.max(1, Math.floor(data.length / 6)) === 0 && (
              <text x={p.x} y={PAD.top + h + 16} className="chart-label-x">
                {p.date.slice(5)}
              </text>
            )}
          </g>
        ))}

        {hovered !== null && (
          <g>
            <rect
              x={points[hovered].x - 50} y={points[hovered].y - 38}
              width="100" height="28" rx="4"
              className="chart-tooltip-bg"
            />
            <text x={points[hovered].x} y={points[hovered].y - 20} className="chart-tooltip-text">
              {points[hovered].date}: {points[hovered].avg_score} ({points[hovered].review_count} reviews)
            </text>
          </g>
        )}
      </svg>
    </div>
  );
}
