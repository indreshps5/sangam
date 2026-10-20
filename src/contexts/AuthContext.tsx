/**
 * Authentication context for React.
 * Provides authentication state and methods to all components.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import apiClient from '../lib/api';

interface User {
  id: string;
  email: string;
  full_name: string | null;
  roles: string[];
  permissions: string[];
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const currentUser = apiClient.getCurrentUser();
    if (currentUser && apiClient.isAuthenticated()) {
      setUser(currentUser);
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const userData = await apiClient.login(email, password);
    setUser(userData);
  };

  const logout = async () => {
    await apiClient.logout();
    setUser(null);
  };

  const hasPermission = (permission: string) => {
    return apiClient.hasPermission(permission);
  };

  const hasRole = (role: string) => {
    return apiClient.hasRole(role);
  };

  const value = {
    user,
    isAuthenticated: !!user && apiClient.isAuthenticated(),
    isLoading,
    login,
    logout,
    hasPermission,
    hasRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
