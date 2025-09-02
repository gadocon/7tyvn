import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader } from './ui/card';
import { Eye, EyeOff, User, Lock, Phone, Mail } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LoginPage = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    login: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const detectLoginType = (input) => {
    if (!input) return 'username';
    if (input.includes('@')) return 'email';
    if (/^\d{10,15}$/.test(input.replace(/\s/g, ''))) return 'phone';
    return 'username';
  };

  const getPlaceholder = () => {
    const type = detectLoginType(formData.login);
    switch (type) {
      case 'email':
        return 'Nhập email (ví dụ: admin@7ty.vn)';
      case 'phone':
        return 'Nhập số điện thoại (ví dụ: 0901234567)';
      default:
        return 'Nhập tên đăng nhập (ví dụ: admin)';
    }
  };

  const getIcon = () => {
    const type = detectLoginType(formData.login);
    switch (type) {
      case 'email':
        return <Mail className="h-4 w-4" />;
      case 'phone':
        return <Phone className="h-4 w-4" />;
      default:
        return <User className="h-4 w-4" />;
    }
  };

  const getInputLabel = () => {
    const type = detectLoginType(formData.login);
    switch (type) {
      case 'email':
        return 'Email';
      case 'phone':
        return 'Số điện thoại';
      default:
        return 'Tên đăng nhập';
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/login`, formData);
      
      // Store token and user info
      const { access_token, user } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      toast.success(`Chào mừng ${user.full_name}! Đăng nhập thành công.`);
      
      // Call parent onLogin callback
      if (onLogin) {
        onLogin(user);
      }
      
      // Navigate to dashboard
      navigate('/');
      
    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = error.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng thử lại.';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleLoginModeChange = (mode) => {
    setLoginMode(mode);
    setFormData({ ...formData, login: '' });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-indigo-400/20 to-pink-400/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-cyan-400/10 to-blue-400/10 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      {/* Glassmorphism Login Card */}
      <div className="relative z-10 w-full max-w-md mx-4">
        <Card className="backdrop-blur-xl bg-white/30 border border-white/20 shadow-2xl">
          <CardHeader className="text-center pb-2">
            {/* Logo */}
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                <img 
                  src="https://customer-assets.emergentagent.com/job_crm-analytics-2/artifacts/1sk73ms1_logo7ty.svg" 
                  alt="7ty.vn Logo" 
                  className="w-10 h-10 text-white"
                />
              </div>
            </div>
            
            <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
              7ty.vn CRM
            </h1>
            <p className="text-gray-600 text-sm mt-1">
              Đăng nhập để truy cập hệ thống
            </p>
          </CardHeader>

          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Login Method Selector */}
              <div className="flex space-x-1 bg-white/50 p-1 rounded-lg">
                {[
                  { key: 'username', label: 'Tên TK', icon: User },
                  { key: 'email', label: 'Email', icon: Mail },
                  { key: 'phone', label: 'SĐT', icon: Phone }
                ].map((mode) => (
                  <button
                    key={mode.key}
                    type="button"
                    onClick={() => handleLoginModeChange(mode.key)}
                    className={`flex-1 flex items-center justify-center space-x-1 py-2 px-3 rounded-md text-xs font-medium transition-all duration-200 ${
                      loginMode === mode.key
                        ? 'bg-white text-gray-900 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
                    }`}
                  >
                    <mode.icon className="h-3 w-3" />
                    <span>{mode.label}</span>
                  </button>
                ))}
              </div>

              {/* Login Input */}
              <div className="space-y-2">
                <Label htmlFor="login" className="text-gray-700 font-medium">
                  {loginMode === 'email' ? 'Email' : loginMode === 'phone' ? 'Số điện thoại' : 'Tên đăng nhập'}
                </Label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                    {getIcon()}
                  </div>
                  <Input
                    id="login"
                    name="login"
                    type="text"
                    value={formData.login}
                    onChange={handleInputChange}
                    placeholder={getPlaceholder()}
                    className="pl-10 bg-white/70 border-white/30 focus:bg-white/90 transition-all duration-200"
                    required
                  />
                </div>
              </div>

              {/* Password Input */}
              <div className="space-y-2">
                <Label htmlFor="password" className="text-gray-700 font-medium">
                  Mật khẩu
                </Label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                    <Lock className="h-4 w-4" />
                  </div>
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="Nhập mật khẩu"
                    className="pl-10 pr-10 bg-white/70 border-white/30 focus:bg-white/90 transition-all duration-200"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {/* Login Button */}
              <Button 
                type="submit" 
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-medium py-3 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Đang đăng nhập...</span>
                  </div>
                ) : (
                  'Đăng nhập'
                )}
              </Button>
            </form>

            {/* Footer */}
            <div className="text-center pt-4 border-t border-white/20">
              <p className="text-xs text-gray-500">
                © 2025 7ty.vn CRM - Hệ thống quản lý khách hàng
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default LoginPage;