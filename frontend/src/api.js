import { frontendLog } from './logger';

const API_URL = import.meta.env.VITE_API_URL || '/api';

export async function apiGet(path, params) {
  const url = new URL(`${API_URL}${path}`, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.set(key, value);
      }
    });
  }

  const response = await fetch(url.pathname + url.search);
  if (!response.ok) {
    frontendLog('warn', `API GET failed: ${path}`, {
      status: response.status,
      query: Object.fromEntries(url.searchParams.entries()),
    });
    throw new Error(`API ${path} failed`);
  }

  return response.json();
}

export async function login(username, password) {
  const response = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    frontendLog('warn', 'Login failed', { status: response.status, username });
    throw new Error('Ошибка входа');
  }

  frontendLog('info', 'User login success', { username });
  return response.json();
}
