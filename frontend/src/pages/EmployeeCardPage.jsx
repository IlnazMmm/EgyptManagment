import { useEffect, useState } from 'react';
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
        <ul>
          {item.factors.map((f) => (
            <li key={f.name}>{f.name}: {f.value}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}

function Info({ title, value }) {
  return <div className="card"><h4>{title}</h4><strong>{value}</strong></div>;
}
