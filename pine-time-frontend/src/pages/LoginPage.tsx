import React, { useState } from "react";
import { Typography } from '@mui/material';
import api from '../api/client';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);

      const res = await api.post('/login/access-token', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      login(res.data.access_token, res.data.refresh_token);
      setError('');
      // Redirect based on user role
      const user: any = jwtDecode(res.data.access_token);
      if (user.is_superuser || user.user_type === 'admin') {
        navigate('/admin');
      } else {
        navigate('/');
      }
    } catch (err: any) {
      let message = 'Login failed';
      const data = err.response?.data;
      if (typeof data === 'string') {
        message = data;
      } else if (Array.isArray(data)) {
        message = data.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
      } else if (typeof data === 'object' && data !== null) {
        message = data.detail || data.msg || JSON.stringify(data);
      }
      setError(message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Typography variant="h5">Login</Typography>
      <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Username or Email" required />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" required />
      <button type="submit" disabled={loading}>{loading ? 'Logging in...' : 'Login'}</button>
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </form>
  );
};

export default LoginPage;
