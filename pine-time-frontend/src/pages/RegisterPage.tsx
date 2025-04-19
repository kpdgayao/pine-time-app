import React, { useState } from 'react';
import { Typography } from '@mui/material';
import api from '../api/client';

const RegisterPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [msg, setMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/users/register', { username, email, password });
      setMsg('Registration successful! You can now log in.');
    } catch (err: any) {
      let message = 'Registration failed.';
      const data = err.response?.data;
      if (typeof data === 'string') {
        message = data;
      } else if (Array.isArray(data)) {
        message = data.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
      } else if (typeof data === 'object' && data !== null) {
        message = data.detail || data.msg || JSON.stringify(data);
      }
      setMsg(message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Typography variant="h5">Register</Typography>
      <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" required />
      <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" type="email" required />
      <input value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" type="password" required />
      <button type="submit">Register</button>
      <div>{msg}</div>
    </form>
  );
};

export default RegisterPage;
