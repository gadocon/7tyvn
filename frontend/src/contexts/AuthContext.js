import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext({});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const storedUser = localStorage.getItem('user');

        if (token && storedUser) {
          // Set axios header
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Verify token by getting current user
          try {
            const response = await axios.get(`${API}/auth/me`);
            const userData = response.data;
            
            setUser(userData);
            setIsAuthenticated(true);
            
            // Update stored user data
            localStorage.setItem('user', JSON.stringify(userData));
            
          } catch (error) {
            // Token is invalid, clear storage
            console.error('Token validation failed:', error);
            logout();
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        logout();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (loginData) => {
    try {
      const response = await axios.post(`${API}/auth/login`, loginData);
      const { access_token, user: userData } = response.data;

      // Store token and user data
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));

      // Set axios header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      // Update state
      setUser(userData);
      setIsAuthenticated(true);

      return { success: true, user: userData };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Đăng nhập thất bại';
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    // Clear storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');

    // Clear axios header
    delete axios.defaults.headers.common['Authorization'];

    // Update state
    setUser(null);
    setIsAuthenticated(false);
  };

  const updateProfile = async (updateData) => {
    try {
      const response = await axios.put(`${API}/auth/profile`, updateData);
      const updatedUser = response.data;

      // Update state and storage
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));

      return { success: true, user: updatedUser };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Cập nhật thông tin thất bại';
      return { success: false, error: errorMessage };
    }
  };

  const changePassword = async (passwordData) => {
    try {
      await axios.post(`${API}/auth/change-password`, passwordData);
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Đổi mật khẩu thất bại';
      return { success: false, error: errorMessage };
    }
  };

  const hasRole = (roles) => {
    if (!user) return false;
    if (Array.isArray(roles)) {
      return roles.includes(user.role);
    }
    return user.role === roles;
  };

  const isAdmin = () => hasRole('admin');
  const isManager = () => hasRole(['admin', 'manager']);

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    updateProfile,
    changePassword,
    hasRole,
    isAdmin,
    isManager
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;