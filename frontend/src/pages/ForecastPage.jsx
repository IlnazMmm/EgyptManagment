import { useEffect, useState } from 'react';
import { apiGet } from '../api';
import LineChart from '../components/LineChart';

export default function ForecastPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    apiGet('/forecast').then(setData);
  }, []);

  if (!data) return <p>Загрузка...</p>;

  return (
    <section>
      <h1>Прогнозирование</h1>
      <p>Период анализа: {data.period}</p>

      <div className="grid three">
        <Metric name="Выручка" {...data.kpis.revenue} />
        <Metric name="Заказы" {...data.kpis.orders} />
        <Metric name="Средний чек" {...data.kpis.avgCheck} />
      </div>

      <div className="card">
        <h3>Тренд выручки: Факт vs Прогноз</h3>
        <LineChart labels={data.labels} series={data.revenueSeries} />
      </div>

      <div className="card">
        <h3>Тренд заказов: Факт vs Прогноз</h3>
        <LineChart labels={data.labels} series={data.ordersSeries} />
      </div>
    </section>
  );
}

function Metric({ name, value, delta }) {
  return (
    <div className="card stat">
      <h4>{name}</h4>
      <strong>{value}</strong>
      <small>{delta}</small>
    </div>
  );
}
