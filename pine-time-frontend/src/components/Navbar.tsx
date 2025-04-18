import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <nav style={{ display: 'flex', gap: '1rem', padding: '1rem', borderBottom: '1px solid #eee' }}>
      <Link to="/">Events</Link>
      <Link to="/leaderboard">Leaderboard</Link>
      <Link to="/badges">Badges</Link>
      <Link to="/points">Points</Link>
      <Link to="/profile">Profile</Link>
      {user && (user.is_superuser || user.user_type === 'admin') && (
        <Link to="/admin">Admin Dashboard</Link>
      )}
      {user ? (
        <button onClick={logout}>Logout</button>
      ) : (
        <>
          <Link to="/login">Login</Link>
          <Link to="/register">Register</Link>
        </>
      )}
    </nav>
  );
};

export default Navbar;
