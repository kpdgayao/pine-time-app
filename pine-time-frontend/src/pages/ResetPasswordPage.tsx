import React, { useState } from 'react';
import { Typography } from '@mui/material';
import api from '../api/client';

const ResetPasswordPage: React.FC = () => {
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [msg, setMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/auth/reset-password', { token, new_password: newPassword });
      setMsg(res.data.message || 'Password reset successfully.');
    } catch (err: any) {
      let message = 'Error resetting password.';
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
      <Typography variant="h5">Reset Password</Typography>
      <input value={token} onChange={e => setToken(e.target.value)} placeholder="Reset token" required />
      <input value={newPassword} onChange={e => setNewPassword(e.target.value)} placeholder="New password" type="password" required />
      <button type="submit">Reset Password</button>
      <div>{msg}</div>
    </form>
  );
};

export default ResetPasswordPage;
