import { Navigate, Route, Routes } from 'react-router-dom';
import { useEffect, useState } from 'react';
import LoginPage from './pages/LoginPage';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import EmployeesPage from './pages/EmployeesPage';
import EmployeeCardPage from './pages/EmployeeCardPage';
import ReportsPage from './pages/ReportsPage';
import SalesPage from './pages/SalesPage';
import ForecastPage from './pages/ForecastPage';
import AlertsPage from './pages/AlertsPage';
import UsersPage from './pages/UsersPage';

const AUTH_TOKEN_KEY = 'authToken';

export default function App() {
  const [isAuthed, setIsAuthed] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (token) {
      setIsAuthed(true);
    }
  }, []);

  const handleLogin = (token) => {
    if (token) {
      localStorage.setItem(AUTH_TOKEN_KEY, token);
    }
    setIsAuthed(true);
  };

  const handleLogout = () => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    setIsAuthed(false);
  };

  if (!isAuthed) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <Layout onLogout={handleLogout}>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/employees" element={<EmployeesPage />} />
        <Route path="/employees/:id" element={<EmployeeCardPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/sales" element={<SalesPage />} />
        <Route path="/forecast" element={<ForecastPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        <Route path="/users" element={<UsersPage />} />
      </Routes>
    </Layout>
  );
}
