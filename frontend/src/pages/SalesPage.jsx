import { useEffect, useState } from 'react';
import { apiGet } from '../api';

export default function SalesPage() {
  const [data, setData] = useState(null);
  useEffect(() => {
    apiGet('/sales-analysis').then(setData);
  }, []);
  if (!data) return <p>Загрузка...</p>;

  return (
    <section>
      <h1>Анализ продаж</h1>
      <div className="grid four">
        <Item title="Выручка" value={data.revenue} />
        <Item title="Заказы" value={data.orders} />
        <Item title="Проданные единицы" value={data.units} />
        <Item title="Возвраты" value={data.returns} />
      </div>
      <div className="card">
        <h3>Топ товаров</h3>
        <ul>{data.topProducts.map((p) => <li key={p}>{p}</li>)}</ul>
        <h3>Популярные регионы</h3>
        <ul>{data.regions.map((r) => <li key={r}>{r}</li>)}</ul>
        <p>Средний чек: {data.avgCheck}</p>
        <p>Конверсия: {data.conversion}</p>
      </div>
    </section>
  );
}

function Item({ title, value }) {
  return <div className="card stat"><h4>{title}</h4><strong>{value}</strong></div>;
}
