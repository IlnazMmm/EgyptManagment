import { Link, useLocation } from 'react-router-dom';

const links = [
  ['Панель управления', '/dashboard'],
  ['Сотрудники', '/employees'],
  ['Отчёты', '/reports'],
  ['Анализ продаж', '/sales'],
  ['Прогнозирование', '/forecast'],
  ['Алерты', '/alerts'],
  ['Пользователи', '/users'],
];

export default function Layout({ children }) {
  const location = useLocation();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h2>Анализ ИИ</h2>
        <nav>
          {links.map(([label, href]) => (
            <Link key={href} className={location.pathname.startsWith(href) ? 'active' : ''} to={href}>
              {label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
