import { useEffect, useState } from 'react';
import { apiGet } from '../api';

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
        <p>Фактические значения: {data.trend.join(' • ')}</p>
        <p>Прогнозные значения: {data.forecast.join(' • ')}</p>
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
