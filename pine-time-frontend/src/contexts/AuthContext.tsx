import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import api from '../api/client';

// Add a simple modal dialog for session expiry warning
const SessionExpiryDialog: React.FC<{ secondsLeft: number; onLogout: () => void; onContinue: () => void }> = ({ secondsLeft, onLogout, onContinue }) => (
  <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
    <div style={{ background: '#fff', padding: 32, borderRadius: 8, boxShadow: '0 2px 16px #0002', minWidth: 320, textAlign: 'center' }}>
      <h3>Session Expiring Soon</h3>
      <p>Your session will expire in <b>{secondsLeft}</b> seconds.<br />Would you like to stay signed in?</p>
      <button onClick={onContinue} style={{ marginRight: 16 }}>Continue Session</button>
      <button onClick={onLogout}>Logout</button>
    </div>
  </div>
);

interface AuthContextType {
  user: any;
  token: string | null;
  refreshTokenValue: string | null;
  login: (token: string, refreshToken: string) => void;
  logout: () => void;
  refreshToken: () => Promise<void>;
  isTokenExpired: () => boolean;
  getTokenClaims: () => any | null;
} 

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  // Session expiry warning state
  const [showExpiryWarning, setShowExpiryWarning] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState<number | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [refreshTokenValue, setRefreshTokenValue] = useState<string | null>(localStorage.getItem('refresh_token'));
  const [user, setUser] = useState<any>(() => {
    if (token) {
      try {
        return jwtDecode(token);
      } catch {
        return null;
      }
    }
    return null;
  });

  // Utility to check if token is expired
  const isTokenExpired = (): boolean => {
    if (!token) return true;
    try {
      const { exp } = jwtDecode<{ exp: number }>(token);
      if (!exp) return true;
      return Date.now() / 1000 > exp;
    } catch {
      return true;
    }
  };

  // Utility to decode token claims for debugging
  const getTokenClaims = () => {
    if (!token) return null;
    try {
      return jwtDecode(token);
    } catch {
      return null;
    }
  };

  const login = (newToken: string, newRefreshToken: string) => {
    setToken(newToken);
    setRefreshTokenValue(newRefreshToken);
    localStorage.setItem('access_token', newToken);
    localStorage.setItem('refresh_token', newRefreshToken);
    setUser(jwtDecode(newToken));
  };

  const logout = () => {
    setToken(null);
    setRefreshTokenValue(null);
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  // Token refresh logic
  const refreshToken = async () => {
    if (!refreshTokenValue) {
      logout();
      return;
    }
    try {
      const res = await api.post('/login/refresh-token', {
        refresh_token: refreshTokenValue
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = res.data;
      if (data.access_token && data.refresh_token) {
        login(data.access_token, data.refresh_token);
      } else if (data.access_token) {
        // fallback if backend only returns new access_token
        login(data.access_token, refreshTokenValue);
      } else {
        logout();
      }
    } catch {
      logout();
    }
  };

  // On mount, check token expiry and logout if expired
  useEffect(() => {
    if (isTokenExpired()) {
      logout();
    }
    // Periodic session expiry check (every 30s)
    const interval = setInterval(() => {
      if (!token) return;
      try {
        const { exp } = jwtDecode<{ exp: number }>(token);
        if (!exp) return;
        const now = Date.now() / 1000;
        const secondsToExpiry = exp - now;
        // Show warning if <2min left and not already shown
        if (secondsToExpiry < 120 && secondsToExpiry > 0 && !showExpiryWarning) {
          setSecondsLeft(Math.floor(secondsToExpiry));
          setShowExpiryWarning(true);
        }
        // Auto logout if expired
        if (secondsToExpiry <= 0) {
          logout();
        }
      } catch {
        logout();
      }
    }, 30000); // 30 seconds
    return () => clearInterval(interval);
  }, [token, showExpiryWarning]);

  return (
    <AuthContext.Provider value={{ user, token, refreshTokenValue, login, logout, refreshToken, isTokenExpired, getTokenClaims }}>
      {children}
      {showExpiryWarning && secondsLeft !== null && (
        <SessionExpiryDialog
          secondsLeft={secondsLeft}
          onLogout={() => { setShowExpiryWarning(false); logout(); }}
          onContinue={async () => {
            setShowExpiryWarning(false);
            setSecondsLeft(null);
            await refreshToken();
          }}
        />
      )}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
