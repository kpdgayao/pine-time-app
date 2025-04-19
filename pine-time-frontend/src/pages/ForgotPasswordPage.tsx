import React, { useState } from 'react';
import { Typography } from '@mui/material';
import api from '../api/client';

const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [msg, setMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/auth/forgot-password', { email });
      setMsg(res.data.message || 'Check your email for instructions.');
    } catch (err: any) {
      let message = 'Error sending reset email.';
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
      <Typography variant="h5">Forgot Password</Typography>
      <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Your email" type="email" required />
      <button type="submit">Send Reset Link</button>
      <div>{msg}</div>
    </form>
  );
};

export default ForgotPasswordPage;
