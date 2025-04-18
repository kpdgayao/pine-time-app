import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

// Utility to check token expiry (duplicated for use outside React hooks)
function isTokenExpired(token: string | null): boolean {
  if (!token) return true;
  try {
    const { exp } = jwtDecode<{ exp: number }>(token);
    if (!exp) return true;
    return Date.now() / 1000 > exp;
  } catch {
    return true;
  }
}

api.interceptors.request.use(async config => {
  let token = localStorage.getItem('access_token');
  const refreshToken = localStorage.getItem('refresh_token');
  if (token && isTokenExpired(token) && refreshToken) {
    // Try to refresh
    try {
      const res = await axios.post(
        `${API_URL}/login/refresh-token`,
        { refresh_token: refreshToken },
        { headers: { 'Content-Type': 'application/json' } }
      );
      const data = res.data;
      if (data.access_token) {
        token = data.access_token;
        localStorage.setItem('access_token', data.access_token);
        if (data.refresh_token) {
          localStorage.setItem('refresh_token', data.refresh_token);
        }
      } else {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        throw new axios.Cancel('Refresh failed. Logging out.');
      }
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
      throw new axios.Cancel('Refresh failed. Logging out.');
    }
  }
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
