import React, { useState, useEffect } from "react";
import { Box, Typography, Card, CardContent, TextField, Button, InputAdornment, IconButton, CircularProgress, Link } from '@mui/material';
import { Visibility, VisibilityOff, Person, Lock } from '@mui/icons-material';
import api from '../api/client';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';

const LoginPage: React.FC = () => {
  const { showToast } = useToast();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  // Removed unused error state - using Toast context instead
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Check for admin flags
  const searchParams = new URLSearchParams(location.search);
  const isAdminFlag = searchParams.get('admin') === 'true';
  const redirectToAdmin = isAdminFlag || localStorage.getItem('admin_redirect_path') !== null;
  const adminRedirectPath = localStorage.getItem('admin_redirect_path') || '';
  
  // Store that we need to redirect to admin after login
  useEffect(() => {
    if (isAdminFlag) {
      localStorage.setItem('return_to_admin', 'true');
    }
  }, [isAdminFlag]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      showToast('❗ Please enter both username/email and password.', 'warning');
      return;
    }
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);
      const res = await api.post('/login/access-token', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        timeout: 10000,
      });
      login(res.data.access_token, res.data.refresh_token);
      // Error handling now done through Toast
      showToast('✅ Login successful! Welcome to Pine Time App 🌲', 'success');
      // Redirect based on admin flag or user role
      const user: any = jwtDecode(res.data.access_token);
      const isAdmin = user.is_superuser || user.user_type === 'admin';
      
      // Check for redirect to admin flags
      const shouldGoToAdmin = redirectToAdmin || 
        localStorage.getItem('return_to_admin') === 'true' || 
        isAdminFlag;
      
      // Clear the admin return flag
      localStorage.removeItem('return_to_admin');
      
      if (shouldGoToAdmin && isAdmin) {
        // We came from admin dashboard and need to go back there
        // Store tokens for admin dashboard
        localStorage.setItem('admin_access_token', res.data.access_token);
        localStorage.setItem('admin_refresh_token', res.data.refresh_token);
        
        // Clear redirect path
        localStorage.removeItem('admin_redirect_path');
        
        // Use direct navigation to admin dashboard
        const isDev = import.meta.env.DEV;
        const adminUrl = isDev 
          ? `http://localhost:5174${adminRedirectPath || ''}` 
          : `/admin${adminRedirectPath || ''}`;
        
        showToast('✅ Redirecting to admin dashboard...', 'success');
        window.location.href = adminUrl;
      } else if (isAdmin && location.search.includes('admin=true')) {
        // User is admin and came from an admin link
        navigate('/admin');
      } else {
        // Regular user or no specific redirect
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
      showToast(`❌ Login failed: ${message}`, 'error');
    } finally {
      setLoading(false);
    }
  };


  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh" bgcolor="#f7f7f7">
      <Card sx={{ minWidth: 340, boxShadow: 3 }}>
        <CardContent>
          <Typography variant="h5" align="center" gutterBottom>Login</Typography>
          <form onSubmit={handleSubmit} autoComplete="on">
            <TextField
              label="Username or Email"
              value={username}
              onChange={e => setUsername(e.target.value)}
              fullWidth
              required
              margin="normal"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Person />
                  </InputAdornment>
                ),
              }}
              autoFocus
            />
            <TextField
              label="Password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={e => setPassword(e.target.value)}
              fullWidth
              required
              margin="normal"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => setShowPassword((show) => !show)}
                      edge="end"
                      size="large"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              type="submit"
              variant="contained"
              color="success"
              fullWidth
              disabled={loading}
              sx={{ mt: 2, mb: 1 }}
              aria-label="login"
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Login'}
            </Button>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Link href="#" underline="hover" color="primary" fontSize={14}>
                Forgot password?
              </Link>
              <Link href="/register" underline="hover" fontSize={14}>
                Register
              </Link>
            </Box>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
};

export default LoginPage;
