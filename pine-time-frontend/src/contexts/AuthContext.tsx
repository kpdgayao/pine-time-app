import { createContext, useContext, useState, ReactNode } from 'react';
import { jwtDecode } from 'jwt-decode';

interface AuthContextType {
  user: any;
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
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

  const login = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem('access_token', newToken);
    setUser(jwtDecode(newToken));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
  };

  // Token refresh logic
  const refreshToken = async () => {
    try {
      const res = await fetch('/api/v1/login/refresh-token', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!res.ok) throw new Error('Failed to refresh token');
      const data = await res.json();
      if (data.access_token) {
        login(data.access_token);
      } else {
        logout();
      }
    } catch {
      logout();
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, refreshToken }}>
      {children}
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
