import { useEffect, useState } from 'react';
import { apiGet } from '../api';

export default function ForecastPage() {
  const [data, setData] = useState(null);
  const [draftFilters, setDraftFilters] = useState({
    category: 'Продукты питания',
    period: 'Последующие 30 дней',
  });
  const [filters, setFilters] = useState(draftFilters);

  useEffect(() => {
    apiGet('/forecast', filters).then(setData);
  }, [filters]);

  if (!data) return <p>Загрузка...</p>;

  const categoryOptions = data.filters?.categories ?? [];
  const periodOptions = data.filters?.periods ?? [];

  return (
    <section>
      <h1>Прогнозирование / Продажи</h1>

      <div className="card forecast-filters">
        <div className="forecast-filters-grid">
          <FilterSelect
            label="Категория"
            value={draftFilters.category}
            options={categoryOptions}
            onChange={(category) => setDraftFilters((prev) => ({ ...prev, category }))}
          />
          <FilterSelect
            label="Период"
            value={draftFilters.period}
            options={periodOptions}
            onChange={(period) => setDraftFilters((prev) => ({ ...prev, period }))}
          />
        </div>
        <button type="button" className="forecast-apply" onClick={() => setFilters(draftFilters)}>
          Применить
        </button>
      </div>

      <div className="grid three">
        <Metric name="Выручка" {...data.kpis.revenue} />
        <Metric name="Заказы" {...data.kpis.orders} />
        <Metric name="Средний чек" {...data.kpis.avgCheck} />
      </div>

      <div className="card forecast-chart-card">
        <h3>Динамика продаж</h3>
        <p className="sales-chart-subtitle">Выручка, ₽</p>
        <ForecastComboChart chart={data.chart} />
      </div>
    </section>
  );
}

function FilterSelect({ label, value, options, onChange }) {
  return (
    <label className="sales-filter-item">
      <span>{label}:</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => <option key={option} value={option}>{option}</option>)}
      </select>
    </label>
  );
}

function Metric({ name, value, delta }) {
  const positive = delta.startsWith('+');
  return (
    <div className="card stat">
      <h4>{name}</h4>
      <strong>{value}</strong>
      <p className={`delta ${positive ? 'up' : 'down'}`}>{positive ? '▲' : '▼'} {delta.replace('+', '').replace('-', '')}</p>
    </div>
  );
}

function ForecastComboChart({ chart }) {
  const width = 900;
  const height = 320;
  const margin = { top: 16, right: 56, bottom: 58, left: 70 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  const bars = [...chart.revenueHistory, ...chart.revenueForecast];
  const line = [...chart.ordersHistory, ...chart.ordersForecast];
  const labels = [...chart.labels, 'Прогноз 1', 'Прогноз 2', 'Прогноз 3', 'Прогноз 4'];

  const maxBar = Math.max(...bars, 1);
  const maxLine = Math.max(...line, 1);

  const segment = innerWidth / bars.length;
  const barWidth = segment * 0.62;

  const getBarY = (value) => margin.top + innerHeight - (value / maxBar) * innerHeight;
  const getLineY = (value) => margin.top + innerHeight - (value / maxLine) * innerHeight;
  const getX = (index) => margin.left + segment * index + segment / 2;

  const path = line
    .map((value, index) => `${index === 0 ? 'M' : 'L'} ${getX(index)} ${getLineY(value)}`)
    .join(' ');

  const leftTicks = [0, maxBar * 0.33, maxBar * 0.66, maxBar].map((tick) => Math.round(tick));
  const rightTicks = [0, maxLine * 0.33, maxLine * 0.66, maxLine].map((tick) => Math.round(tick));

  return (
    <div className="forecast-combo-chart">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="ML прогноз выручки и заказов">
        {leftTicks.map((tick) => {
          const y = getBarY(tick);
          return (
            <g key={`left-${tick}`}>
              <line x1={margin.left} y1={y} x2={width - margin.right} y2={y} className="sales-grid" />
              <text x={margin.left - 10} y={y + 4} textAnchor="end" className="sales-axis-text">
                {new Intl.NumberFormat('ru-RU').format(tick)}
              </text>
            </g>
          );
        })}

        {bars.map((value, index) => {
          const x = margin.left + segment * index + segment * 0.19;
          const y = getBarY(value);
          const barHeight = margin.top + innerHeight - y;
          const isForecast = index >= chart.revenueHistory.length;
          return (
            <rect
              key={`bar-${index}`}
              x={x}
              y={y}
              width={barWidth}
              height={barHeight}
              rx={3}
              className={isForecast ? 'forecast-bar-predicted' : 'forecast-bar-history'}
            />
          );
        })}

        <path d={path} className="forecast-line" />
        {line.map((value, index) => (
          <circle key={`dot-${index}`} cx={getX(index)} cy={getLineY(value)} r="3.2" className="forecast-dot" />
        ))}

        {labels.map((label, index) => (
          <text key={label + index} x={getX(index)} y={height - 24} textAnchor="middle" className="sales-axis-text">
            {index % 2 === 0 || index >= labels.length - 4 ? label : ''}
          </text>
        ))}

        {rightTicks.map((tick) => {
          const y = getLineY(tick);
          return (
            <text key={`right-${tick}`} x={width - margin.right + 8} y={y + 4} className="sales-axis-text">
              {tick}
            </text>
          );
        })}
      </svg>

      <div className="chart-legend">
        <span className="legend-item trend"><span className="legend-swatch forecast-legend-bar" />Выручка</span>
        <span className="legend-item forecast"><span className="legend-swatch forecast-legend-line" />Кол-во заказов</span>
      </div>
    </div>
  );
}
