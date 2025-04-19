import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <AppBar position="static" color="primary" elevation={1}>
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Pine Time
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button color="inherit" component={RouterLink} to="/">Events</Button>
          <Button color="inherit" component={RouterLink} to="/leaderboard">Leaderboard</Button>
          <Button color="inherit" component={RouterLink} to="/badges">Badges</Button>
          <Button color="inherit" component={RouterLink} to="/points">Points</Button>
          <Button color="inherit" component={RouterLink} to="/profile">Profile</Button>
          {(user && (user.is_superuser || user.user_type === 'admin')) && (
            <Button color="inherit" component={RouterLink} to="/admin">Admin Dashboard</Button>
          )}
          {user ? (
            <Button color="inherit" onClick={logout}>Logout</Button>
          ) : (
            <>
              <Button color="inherit" component={RouterLink} to="/login">Login</Button>
              <Button color="inherit" component={RouterLink} to="/register">Register</Button>
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
