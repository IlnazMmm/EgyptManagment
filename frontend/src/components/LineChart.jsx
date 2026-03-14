const DEFAULT_COLORS = ['#3b82f6', '#f59e0b'];

export default function LineChart({ labels = [], series = [] }) {
  if (!labels.length || !series.length) {
    return <p>Недостаточно данных для графика.</p>;
  }

  const width = 760;
  const height = 280;
  const padding = { top: 20, right: 16, bottom: 40, left: 44 };

  const allValues = series.flatMap((item) => item.values);
  const minValue = Math.min(...allValues);
  const maxValue = Math.max(...allValues);
  const range = maxValue - minValue || 1;

  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const xStep = labels.length > 1 ? chartWidth / (labels.length - 1) : 0;
  const yTicks = 5;

  const getX = (index) => padding.left + index * xStep;
  const getY = (value) => padding.top + ((maxValue - value) / range) * chartHeight;

  const buildPath = (values) => values.map((value, index) => `${index === 0 ? 'M' : 'L'} ${getX(index)} ${getY(value)}`).join(' ');

  return (
    <div className="line-chart">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Линейный график">
        {Array.from({ length: yTicks + 1 }).map((_, index) => {
          const tickValue = minValue + (range / yTicks) * index;
          const y = getY(tickValue);
          return (
            <g key={`y-${index}`}>
              <line x1={padding.left} y1={y} x2={width - padding.right} y2={y} className="chart-grid-line" />
              <text x={padding.left - 8} y={y + 4} className="chart-axis-label" textAnchor="end">
                {Math.round(tickValue)}
              </text>
            </g>
          );
        })}

        {labels.map((label, index) => (
          <text key={label} x={getX(index)} y={height - 14} className="chart-axis-label" textAnchor="middle">
            {label}
          </text>
        ))}

        {series.map((item, idx) => {
          const color = item.color || DEFAULT_COLORS[idx % DEFAULT_COLORS.length];
          return (
            <g key={item.name}>
              <path d={buildPath(item.values)} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" />
              {item.values.map((value, index) => (
                <circle key={`${item.name}-${index}`} cx={getX(index)} cy={getY(value)} r="3" fill={color} />
              ))}
            </g>
          );
        })}
      </svg>

      <div className="chart-legend">
        {series.map((item, idx) => {
          const color = item.color || DEFAULT_COLORS[idx % DEFAULT_COLORS.length];
          return (
            <span key={`legend-${item.name}`}>
              <i style={{ backgroundColor: color }} />
              {item.name}
            </span>
          );
        })}
      </div>
    </div>
  );
}
