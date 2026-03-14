const API_URL = 'http://localhost:8000/api';

export async function apiGet(path) {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
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
    throw new Error('Ошибка входа');
  }
  return response.json();
}
