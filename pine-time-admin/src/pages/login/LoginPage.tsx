import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  TextField, 
  Button, 
  Container, 
  CircularProgress,
  Alert,
  InputAdornment,
  IconButton
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { ADMIN_ROUTES } from '../../config';

/**
 * LoginPage component for Pine Time Admin Dashboard
 * Provides secure authentication with proper error handling and validation
 */
const LoginPage: React.FC = () => {
  // State for form fields
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  
  // State for form submission
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Authentication context and navigation
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get the redirect URL from location state or default to dashboard
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || ADMIN_ROUTES.DASHBOARD;
  
  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    // Basic validation
    if (!email.trim()) {
      setError('Email is required');
      return;
    }
    
    if (!password) {
      setError('Password is required');
      return;
    }
    
    try {
      setIsSubmitting(true);
      setError(null);
      
      // Attempt to login with a 10 second timeout
      const loginSuccess = await Promise.race([
        login(email, password),
        new Promise<boolean>((_, reject) => 
          setTimeout(() => reject(new Error('Login request timed out')), 10000)
        )
      ]) as boolean;
      
      if (loginSuccess) {
        // Login successful, navigate to the redirect URL
        navigate(from, { replace: true });
      } else {
        // Login failed, but no exception thrown
        setError('Invalid email or password');
      }
    } catch (err) {
      // Handle login errors gracefully
      console.error('Login error:', err);
      
      // Provide user-friendly error messages
      if (err instanceof Error && err.message.includes('timed out')) {
        setError('Login request timed out. Please try again.');
      } else {
        setError('Authentication failed. Please check your credentials and try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Toggle password visibility
  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };
  
  return (
    <Container maxWidth="sm" sx={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Paper 
        elevation={3} 
        sx={{ 
          p: 4, 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          width: '100%',
          maxWidth: 500,
          borderRadius: 2,
        }}
      >
        <Typography 
          variant="h4" 
          gutterBottom 
          sx={{ 
            fontWeight: 700, 
            color: 'primary.main',
            textAlign: 'center'
          }}
        >
          Pine Time Admin
        </Typography>
        
        <Typography variant="subtitle1" sx={{ mb: 3, textAlign: 'center' }}>
          Enter your credentials to access the admin dashboard
        </Typography>
        
        {error && (
          <Alert 
            severity="error" 
            sx={{ mb: 3, width: '100%' }}
            onClose={() => setError(null)}
          >
            {error}
          </Alert>
        )}
        
        <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="email"
            autoFocus
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isSubmitting}
            InputProps={{
              sx: { borderRadius: 1 }
            }}
          />
          
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type={showPassword ? 'text' : 'password'}
            id="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isSubmitting}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={handleTogglePasswordVisibility}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
              sx: { borderRadius: 1 }
            }}
          />
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ 
              mt: 3, 
              mb: 2, 
              py: 1.5,
              bgcolor: 'primary.main',
              '&:hover': {
                bgcolor: 'primary.dark',
              },
              borderRadius: 1
            }}
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} color="inherit" /> : 'Sign In'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default LoginPage;
