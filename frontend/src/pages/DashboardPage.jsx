import { useEffect, useMemo, useState } from 'react';
import { apiGet } from '../api';

const MONTHS = ['Ян', 'Фев', 'Мар', 'Апр', 'Май', 'Июн'];

export default function DashboardPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    apiGet('/dashboard').then(setData);
  }, []);

  if (!data) return <p>Загрузка...</p>;

  return (
    <section>
      <h1>Панель управления</h1>
      <div className="grid four">
        <Stat title="Всего сотрудников" value={data.totalEmployees} />
        <Stat title="Высокий риск" value={data.highRisk} />
        <Stat title="Средний риск" value={data.mediumRisk} />
        <Stat title="Средний балл риска" value={data.avgRisk} />
      </div>

      <div className="card">
        <h3>Тренд текучести: Факт vs Прогноз</h3>
        <TrendChart trend={data.trend} forecast={data.forecast} />
      </div>
    </section>
  );
}

function Stat({ title, value }) {
  return (
    <div className="card stat">
      <h4>{title}</h4>
      <strong>{value}</strong>
    </div>
  );
}

function TrendChart({ trend, forecast }) {
  const chartWidth = 780;
  const chartHeight = 260;
  const margin = { top: 16, right: 24, bottom: 44, left: 42 };
  const innerWidth = chartWidth - margin.left - margin.right;
  const innerHeight = chartHeight - margin.top - margin.bottom;

  const allValues = [...trend, ...forecast];
  const maxValue = Math.max(...allValues, 1);
  const yMax = Math.ceil(maxValue / 5) * 5;

  const points = useMemo(() => {
    const getPoint = (value, index, valuesLength) => {
      const x = margin.left + (index * innerWidth) / (valuesLength - 1);
      const y = margin.top + innerHeight - (value / yMax) * innerHeight;
      return { x, y, value };
    };

    return {
      trendPoints: trend.map((value, index) => getPoint(value, index, trend.length)),
      forecastPoints: forecast.map((value, index) => getPoint(value, index, forecast.length)),
    };
  }, [trend, forecast, innerWidth, innerHeight, margin.left, margin.top, yMax]);

  const getLinePath = (linePoints) => linePoints.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`).join(' ');

  const yTicks = [0, yMax / 3, (2 * yMax) / 3, yMax].map((tick) => Math.round(tick));

  return (
    <div className="trend-chart">
      <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} role="img" aria-label="График текучести">
        {yTicks.map((tick) => {
          const y = margin.top + innerHeight - (tick / yMax) * innerHeight;
          return (
            <g key={`tick-${tick}`}>
              <line x1={margin.left} y1={y} x2={chartWidth - margin.right} y2={y} className="chart-grid-line" />
              <text x={margin.left - 10} y={y + 4} textAnchor="end" className="chart-axis-label">
                {tick}
              </text>
            </g>
          );
        })}

        {MONTHS.map((month, index) => {
          const x = margin.left + (index * innerWidth) / (MONTHS.length - 1);
          return (
            <text key={month} x={x} y={chartHeight - 16} textAnchor="middle" className="chart-axis-label">
              {month}
            </text>
          );
        })}

        <path d={getLinePath(points.forecastPoints)} className="chart-line chart-line-forecast" />
        <path d={getLinePath(points.trendPoints)} className="chart-line chart-line-trend" />

        {points.trendPoints.map((point) => (
          <circle key={`trend-${point.x}`} cx={point.x} cy={point.y} r="4" className="chart-dot" />
        ))}
      </svg>

      <div className="chart-legend">
        <LegendItem className="trend" label="Фактическая текучесть" />
        <LegendItem className="forecast" label="Прогнозируемая текучесть" />
      </div>
    </div>
  );
}

function LegendItem({ className, label }) {
  return (
    <span className={`legend-item ${className}`}>
      <span className="legend-swatch" />
      {label}
    </span>
  );
}
