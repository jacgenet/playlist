import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  console.log('AuthProvider initialized'); // Debug log

  // Configure axios defaults
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    
    // Set base URL for API calls
    // In production (Railway), the frontend is served by the same backend, so use relative URLs
    // In development, use the explicit localhost URL
    const isProduction = window.location.hostname !== 'localhost';
    const apiUrl = isProduction ? '' : (process.env.REACT_APP_API_URL || 'http://localhost:8000');
    console.log('API URL:', apiUrl, 'isProduction:', isProduction); // Debug log
    axios.defaults.baseURL = apiUrl;
  }, []);

  const login = async (email, password) => {
    try {
      console.log('Attempting login with:', { email, baseURL: axios.defaults.baseURL }); // Debug log
      const response = await axios.post('/api/auth/login', {
        email,
        password
      });
      
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Get user info
      const userResponse = await axios.get('/api/auth/me');
      console.log('User data received:', userResponse.data); // Debug log
      setUser(userResponse.data);
      console.log('User state set, isAuthenticated should be true'); // Debug log
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      const response = await axios.get('/api/auth/me');
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const isAuthenticated = !!user;
  console.log('AuthContext render - user:', user, 'isAuthenticated:', isAuthenticated); // Debug log
  
  const value = {
    user,
    login,
    logout,
    loading,
    isAuthenticated
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
