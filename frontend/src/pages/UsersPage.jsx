import { useEffect, useState } from 'react';
import { apiGet } from '../api';

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  useEffect(() => {
    apiGet('/users').then((d) => setUsers(d.items));
  }, []);

  return (
    <section>
      <h1>Пользователи</h1>
      {users.map((u) => (
        <div className="card" key={u.id}>
          <h3>{u.name}</h3>
          <p>{u.email}</p>
          <p>{u.role}</p>
          <strong>{u.status}</strong>
        </div>
      ))}
    </section>
  );
}
