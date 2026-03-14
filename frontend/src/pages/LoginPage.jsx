import { useState } from 'react';
import { login } from '../api';

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    try {
      const data = await login(username, password);
      onLogin(data.token);
    } catch {
      setError('Неверные учетные данные');
    }
  };

  return (
    <div className="login-page">
      <form className="card" onSubmit={submit}>
        <h1>Вход в систему</h1>
        <p>Используйте свои учетные данные</p>
        <label>Имя пользователя</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} />
        <label>Пароль</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">Войти</button>
        {error && <div className="error">{error}</div>}
        <small>Тестовые учётные данные: admin/admin123, manager/manager123</small>
      </form>
    </div>
  );
}
