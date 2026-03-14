import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiGet } from '../api';

export default function EmployeesPage() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    apiGet('/employees').then((d) => setItems(d.items));
  }, []);

  return (
    <section>
      <h1>Все сотрудники</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th><th>Имя</th><th>Должность</th><th>Отдел</th><th>Риск</th><th>Действие</th>
          </tr>
        </thead>
        <tbody>
          {items.map((e) => (
            <tr key={e.id}>
              <td>{e.id}</td>
              <td>{e.name}</td>
              <td>{e.position}</td>
              <td>{e.department}</td>
              <td>{e.risk}</td>
              <td><Link to={`/employees/${e.id}`}>Смотреть</Link></td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
