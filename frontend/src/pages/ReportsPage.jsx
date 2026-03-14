import { useEffect, useState } from 'react';
import { apiGet } from '../api';

export default function ReportsPage() {
  const [data, setData] = useState(null);
  useEffect(() => {
    apiGet('/reports').then(setData);
  }, []);
  if (!data) return <p>Загрузка...</p>;

  return (
    <section>
      <h1>Отчёты о производительности модели</h1>
      <div className="grid four">
        <Card title="AUC-ROC" value={data.auc} />
        <Card title="Средняя точность" value={data.accuracy} />
        <Card title="Истинно положительные" value={data.tp} />
        <Card title="Ложно положительные" value={data.fp} />
      </div>
      <div className="grid four">
        <Card title="Ложно отрицательные" value={data.fn} />
        <Card title="Истинно отрицательные" value={data.tn} />
      </div>
    </section>
  );
}

function Card({ title, value }) {
  return <div className="card stat"><h4>{title}</h4><strong>{value}</strong></div>;
}
