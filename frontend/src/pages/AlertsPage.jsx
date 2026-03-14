import { useEffect, useState } from 'react';
import { apiGet } from '../api';

export default function AlertsPage() {
  const [data, setData] = useState(null);
  useEffect(() => {
    apiGet('/alerts').then(setData);
  }, []);
  if (!data) return <p>Загрузка...</p>;

  return (
    <section>
      <h1>Алерты</h1>
      <div className="grid three">
        <Alert title="Критические" count={data.critical} />
        <Alert title="Предупреждения" count={data.warning} />
        <Alert title="Информация" count={data.info} />
      </div>
      <div className="card">Событий пока нет.</div>
    </section>
  );
}

function Alert({ title, count }) {
  return <div className="card stat"><h4>{title}</h4><strong>{count}</strong></div>;
}
