import { useEffect, useMemo, useState } from 'react';
import { apiGet } from '../api';

const CATEGORY_OPTIONS = ['Продукты питания', 'Напитки', 'Бытовая химия'];
const PERIOD_OPTIONS = ['Последние 30 дней', 'Последние 14 дней', 'Последние 7 дней'];
const WAREHOUSE_OPTIONS = ['Все склады', 'Склад Север', 'Склад Центр', 'Склад Юг'];

const CATEGORY_FACTORS = {
  'Продукты питания': { revenue: 1, orders: 1, units: 1, returns: 1, bars: 1, line: 1 },
  Напитки: { revenue: 0.92, orders: 0.95, units: 0.9, returns: 0.82, bars: 0.9, line: 0.95 },
  'Бытовая химия': { revenue: 1.08, orders: 0.9, units: 0.86, returns: 0.7, bars: 0.85, line: 0.9 },
};

const PERIOD_FACTORS = {
  'Последние 30 дней': { revenue: 1, orders: 1, units: 1, returns: 1, bars: 1, line: 1 },
  'Последние 14 дней': { revenue: 0.66, orders: 0.62, units: 0.64, returns: 0.55, bars: 0.63, line: 0.66 },
  'Последние 7 дней': { revenue: 0.38, orders: 0.35, units: 0.36, returns: 0.29, bars: 0.37, line: 0.39 },
};

const WAREHOUSE_FACTORS = {
  'Все склады': { revenue: 1, orders: 1, units: 1, returns: 1, bars: 1, line: 1 },
  'Склад Север': { revenue: 0.42, orders: 0.45, units: 0.44, returns: 0.5, bars: 0.44, line: 0.46 },
  'Склад Центр': { revenue: 0.36, orders: 0.34, units: 0.35, returns: 0.3, bars: 0.35, line: 0.33 },
  'Склад Юг': { revenue: 0.29, orders: 0.27, units: 0.28, returns: 0.26, bars: 0.27, line: 0.28 },
};

const DAILY_BARS = [180, 160, 200, 175, 230, 155, 190, 168, 145, 172, 159, 198, 162, 210, 166, 197];
const DAILY_LINE = [210, 205, 225, 240, 222, 214, 218, 233, 228, 242, 236, 226, 232, 248, 251, 245];

export default function SalesPage() {
  const [data, setData] = useState(null);
  const [draftFilters, setDraftFilters] = useState({
    category: CATEGORY_OPTIONS[0],
    period: PERIOD_OPTIONS[0],
    warehouse: WAREHOUSE_OPTIONS[0],
  });
  const [filters, setFilters] = useState(draftFilters);

  useEffect(() => {
    apiGet('/sales-analysis').then(setData);
  }, []);

  const filteredData = useMemo(() => {
    if (!data) return null;

    const categoryFactor = CATEGORY_FACTORS[filters.category];
    const periodFactor = PERIOD_FACTORS[filters.period];
    const warehouseFactor = WAREHOUSE_FACTORS[filters.warehouse];

    const getFactor = (key) => categoryFactor[key] * periodFactor[key] * warehouseFactor[key];

    const orders = Math.round(data.orders * getFactor('orders'));
    const units = Math.round(data.units * getFactor('units'));
    const returns = Math.round(data.returns * getFactor('returns'));
    const revenue = Math.round(1250000 * getFactor('revenue'));

    const bars = DAILY_BARS.map((value) => Math.round(value * getFactor('bars')));
    const line = DAILY_LINE.map((value) => Math.round(value * getFactor('line')));

    const avgCheckValue = orders > 0 ? Math.round(revenue / orders) : 0;
    const conversionValue = Math.max(1.2, Number((4.8 * getFactor('orders')).toFixed(1)));

    return {
      ...data,
      revenue: `${new Intl.NumberFormat('ru-RU').format(revenue)} ₽`,
      orders,
      units,
      returns,
      avgCheck: `${new Intl.NumberFormat('ru-RU').format(avgCheckValue)} ₽`,
      conversion: `${conversionValue.toFixed(1)}%`,
      bars,
      line,
    };
  }, [data, filters]);

  if (!filteredData) return <p>Загрузка...</p>;

  return (
    <section>
      <h1>Анализ продаж</h1>

      <div className="card sales-filters">
        <div className="sales-filters-grid">
          <FilterSelect
            label="Категория"
            value={draftFilters.category}
            options={CATEGORY_OPTIONS}
            onChange={(category) => setDraftFilters((prev) => ({ ...prev, category }))}
          />
          <FilterSelect
            label="Период"
            value={draftFilters.period}
            options={PERIOD_OPTIONS}
            onChange={(period) => setDraftFilters((prev) => ({ ...prev, period }))}
          />
          <FilterSelect
            label="Склад"
            value={draftFilters.warehouse}
            options={WAREHOUSE_OPTIONS}
            onChange={(warehouse) => setDraftFilters((prev) => ({ ...prev, warehouse }))}
          />
        </div>
        <button type="button" className="sales-apply" onClick={() => setFilters(draftFilters)}>
          Применить
        </button>
      </div>

      <div className="grid four sales-kpis">
        <SalesStat title="Выручка" value={filteredData.revenue} delta="12%" positive />
        <SalesStat title="Заказы" value={filteredData.orders} delta="15%" positive />
        <SalesStat title="Проданные единицы" value={filteredData.units} delta="18%" positive />
        <SalesStat title="Возвраты" value={filteredData.returns} delta="8%" />
      </div>

      <div className="sales-layout">
        <div className="card sales-main-chart">
          <h3>Динамика продаж</h3>
          <p className="sales-chart-subtitle">Выручка, ₽</p>
          <SalesComboChart bars={filteredData.bars} line={filteredData.line} />
          <div className="sales-bottom-stats">
            <div className="card"><span>Средний чек:</span> <strong>{filteredData.avgCheck}</strong></div>
            <div className="card"><span>Конверсия:</span> <strong>{filteredData.conversion}</strong></div>
          </div>
        </div>

        <div className="sales-side-column">
          <div className="card">
            <h3>Топ товаров</h3>
            <ul className="sales-list">{filteredData.topProducts.map((p) => <li key={p}>🍎 {p}</li>)}</ul>
          </div>
          <div className="card">
            <h3>Популярные регионы</h3>
            <ul className="sales-list">{filteredData.regions.map((r) => <li key={r}>🇷🇺 {r}</li>)}</ul>
          </div>
        </div>
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

function SalesStat({ title, value, delta, positive = false }) {
  return (
    <div className="card stat">
      <h4>{title}</h4>
      <strong>{value}</strong>
      <p className={`delta ${positive ? 'up' : 'down'}`}>{positive ? '▲' : '▼'} {delta}</p>
    </div>
  );
}

function SalesComboChart({ bars, line }) {
  const width = 760;
  const height = 290;
  const margin = { top: 14, right: 52, bottom: 46, left: 42 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;
  const maxValue = Math.max(...bars, ...line, 1);

  const getX = (index, size) => margin.left + (index * innerWidth) / (size - 1);
  const getY = (value) => margin.top + innerHeight - (value / maxValue) * innerHeight;

  const linePath = line
    .map((value, index) => `${index === 0 ? 'M' : 'L'} ${getX(index, line.length)} ${getY(value)}`)
    .join(' ');

  const yTicks = [0, maxValue * 0.25, maxValue * 0.5, maxValue * 0.75, maxValue].map((tick) => Math.round(tick));

  return (
    <div className="sales-combo-chart">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Комбинированный график продаж">
        {yTicks.map((tick) => {
          const y = getY(tick);
          return (
            <g key={tick}>
              <line x1={margin.left} y1={y} x2={width - margin.right} y2={y} className="sales-grid" />
              <text x={margin.left - 8} y={y + 4} textAnchor="end" className="sales-axis-text">{tick}</text>
            </g>
          );
        })}

        {bars.map((value, index) => {
          const segment = innerWidth / bars.length;
          const barWidth = segment * 0.64;
          const x = margin.left + index * segment + segment * 0.18;
          const y = getY(value);
          const barHeight = margin.top + innerHeight - y;
          return <rect key={`bar-${index}`} x={x} y={y} width={barWidth} height={barHeight} className="sales-bar" rx={3} />;
        })}

        <path d={linePath} className="sales-line" />
        {line.map((value, index) => (
          <circle key={`dot-${index}`} cx={getX(index, line.length)} cy={getY(value)} r="3" className="sales-dot" />
        ))}

        <text x={width - margin.right} y={16} textAnchor="end" className="sales-axis-text">Шт., Кол-во заказов</text>
      </svg>
    </div>
  );
}
