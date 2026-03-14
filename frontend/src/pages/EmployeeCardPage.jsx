import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiGet } from '../api';

export default function EmployeeCardPage() {
  const { id } = useParams();
  const [item, setItem] = useState(null);

  useEffect(() => {
    apiGet(`/employees/${id}`).then(setItem);
  }, [id]);

  if (!item) return <p>Загрузка...</p>;

  return (
    <section>
      <h1>{item.name}</h1>
      <div className="grid three">
        <Info title="Возраст" value={item.age} />
        <Info title="Стаж" value={item.experience} />
        <Info title="Зарплата" value={item.salary} />
        <Info title="Удовлетворенность" value={item.engagement} />
        <Info title="Производительность" value={item.performance} />
        <Info title="Часы работы" value={item.workHours} />
      </div>
      <div className="card">
        <h3>Анализ важности признаков</h3>
        <p className="factor-subtitle">Факторы, влияющие на прогноз риска текучести</p>
        <FeatureImportanceChart factors={item.factors} />
      </div>
    </section>
  );
}

function Info({ title, value }) {
  return <div className="card"><h4>{title}</h4><strong>{value}</strong></div>;
}

function FeatureImportanceChart({ factors }) {
  const sortedFactors = useMemo(
    () => [...factors].sort((a, b) => Number(b.value) - Number(a.value)),
    [factors],
  );

  const chartWidth = 920;
  const rowHeight = 34;
  const margin = { top: 12, right: 40, bottom: 42, left: 210 };
  const barHeight = 22;
  const chartHeight = margin.top + margin.bottom + sortedFactors.length * rowHeight;
  const innerWidth = chartWidth - margin.left - margin.right;
  const maxValue = Math.max(...sortedFactors.map((factor) => Number(factor.value)), 0.01);
  const tickCount = 4;
  const ticks = Array.from({ length: tickCount + 1 }, (_, i) => (maxValue * i) / tickCount);

  return (
    <div className="feature-importance-chart">
      <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} role="img" aria-label="График важности признаков">
        {ticks.map((tick) => {
          const x = margin.left + (tick / maxValue) * innerWidth;
          return (
            <g key={`tick-${tick}`}>
              <line
                x1={x}
                y1={margin.top}
                x2={x}
                y2={chartHeight - margin.bottom}
                className="feature-grid-line"
              />
              <text
                x={x}
                y={chartHeight - 16}
                textAnchor="middle"
                className="feature-axis-label"
              >
                {tick.toFixed(2)}
              </text>
            </g>
          );
        })}

        {sortedFactors.map((factor, index) => {
          const y = margin.top + index * rowHeight;
          const width = (Number(factor.value) / maxValue) * innerWidth;
          return (
            <g key={factor.name}>
              <text
                x={margin.left - 12}
                y={y + barHeight / 2 + 4}
                textAnchor="end"
                className="feature-y-label"
              >
                {factor.name}
              </text>
              <rect
                x={margin.left}
                y={y}
                width={Math.max(width, 3)}
                height={barHeight}
                rx={4}
                className="feature-bar"
              />
            </g>
          );
        })}
      </svg>
    </div>
  );
}
