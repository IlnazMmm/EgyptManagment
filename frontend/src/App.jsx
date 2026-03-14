import { Navigate, Route, Routes } from 'react-router-dom';
import { useState } from 'react';
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

export default function App() {
  const [isAuthed, setIsAuthed] = useState(false);

  if (!isAuthed) {
    return <LoginPage onLogin={() => setIsAuthed(true)} />;
  }

  return (
    <Layout>
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
