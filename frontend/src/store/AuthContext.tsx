import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  loginAsGuest: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('signbridge_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const savedUser = localStorage.getItem('signbridge_user');
    if (savedUser && token) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('signbridge_user');
        localStorage.removeItem('signbridge_token');
      }
    }
    setIsLoading(false);
  }, [token]);

  const handleAuthSuccess = (accessToken: string, authUser: User) => {
    setToken(accessToken);
    setUser(authUser);
    localStorage.setItem('signbridge_token', accessToken);
    localStorage.setItem('signbridge_user', JSON.stringify(authUser));
  };

  const login = async (email: string, password: string) => {
    const res = await api.login({ email, password });
    handleAuthSuccess(res.access_token, res.user);
  };

  const register = async (email: string, password: string, fullName?: string) => {
    const res = await api.register({ email, password, full_name: fullName });
    handleAuthSuccess(res.access_token, res.user);
  };

  const loginAsGuest = async () => {
    const res = await api.guestLogin();
    handleAuthSuccess(res.access_token, res.user);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('signbridge_token');
    localStorage.removeItem('signbridge_user');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        isLoading,
        login,
        register,
        loginAsGuest,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
