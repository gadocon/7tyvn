import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader } from './ui/card';
import { Eye, EyeOff, User, Lock, Phone, Mail } from 'lucide-react';
import { toast } from 'sonner';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    login: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

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
      const result = await login(formData);
      
      if (result.success) {
        toast.success(`Chào mừng ${result.user.full_name}! Đăng nhập thành công.`);
        navigate('/');
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      console.error('Login error:', error);
      toast.error('Đăng nhập thất bại. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };



  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-700 via-green-800 to-green-900 relative overflow-hidden">
      {/* Modern Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Floating Geometric Shapes */}
        <div className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-br from-green-400/20 to-green-500/30 rounded-full blur-xl animate-float"></div>
        <div className="absolute top-40 right-32 w-20 h-20 bg-gradient-to-br from-green-300/25 to-green-400/35 rounded-lg rotate-45 blur-lg animate-float-delayed"></div>
        <div className="absolute bottom-32 left-32 w-24 h-24 bg-gradient-to-br from-green-500/20 to-green-600/30 rounded-full blur-lg animate-float-slow"></div>
        <div className="absolute bottom-20 right-20 w-28 h-28 bg-gradient-to-br from-green-400/15 to-green-500/25 rounded-lg rotate-12 blur-xl animate-float-delayed"></div>
        
        {/* Moving Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-green-600/10 to-transparent animate-gradient-shift"></div>
        
        {/* Subtle Grid Pattern */}
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: `
            linear-gradient(90deg, rgba(34, 197, 94, 0.1) 1px, transparent 1px),
            linear-gradient(180deg, rgba(34, 197, 94, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '40px 40px'
        }}></div>
        
        {/* Large Background Accent */}
        <div className="absolute -top-60 -right-60 w-96 h-96 bg-gradient-to-br from-green-400/5 to-green-600/10 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute -bottom-60 -left-60 w-96 h-96 bg-gradient-to-tr from-green-500/5 to-green-700/10 rounded-full blur-3xl animate-pulse-slow delay-1000"></div>
      </div>

      {/* Enhanced Glassmorphism Login Card */}
      <div className="relative z-10 w-full max-w-md mx-4">
        <Card className="backdrop-blur-xl bg-white/10 border border-white/20 shadow-2xl hover:shadow-3xl transition-all duration-500">
          <CardHeader className="text-center pb-2">
            {/* Logo */}
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-green-600 rounded-2xl flex items-center justify-center shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300">
                <img 
                  src="https://customer-assets.emergentagent.com/job_crm-analytics-2/artifacts/1sk73ms1_logo7ty.svg" 
                  alt="7ty.vn Logo" 
                  className="w-10 h-10 text-white filter brightness-0 invert"
                />
              </div>
            </div>
            
            <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-green-100 bg-clip-text text-transparent">
              7ty.vn CRM
            </h1>
            <p className="text-green-100/80 text-sm mt-1">
              Đăng nhập để truy cập hệ thống
            </p>
          </CardHeader>

          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Smart Login Input - Auto-detects Username/Email/Phone */}
              <div className="space-y-2">
                <Label htmlFor="login" className="text-white/90 font-medium">
                  {getInputLabel()}
                </Label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-green-400">
                    {getIcon()}
                  </div>
                  <Input
                    id="login"
                    name="login"
                    type="text"
                    value={formData.login}
                    onChange={handleInputChange}
                    placeholder={getPlaceholder()}
                    className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/60 focus:bg-white/20 focus:border-green-400 transition-all duration-200"
                    required
                  />
                </div>
                {/* Smart Detection Indicator */}
                {formData.login && (
                  <div className="text-xs text-green-200/80 ml-1">
                    <span className="inline-flex items-center">
                      {getIcon()}
                      <span className="ml-1">
                        Phát hiện: {getInputLabel().toLowerCase()}
                      </span>
                    </span>
                  </div>
                )}
              </div>

              {/* Password Input */}
              <div className="space-y-2">
                <Label htmlFor="password" className="text-white/90 font-medium">
                  Mật khẩu
                </Label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-green-400">
                    <Lock className="h-4 w-4" />
                  </div>
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="Nhập mật khẩu"
                    className="pl-10 pr-10 bg-white/10 border-white/20 text-white placeholder:text-white/60 focus:bg-white/20 focus:border-green-400 transition-all duration-200"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-green-400 hover:text-green-300 transition-colors"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {/* Login Button */}
              <Button 
                type="submit" 
                disabled={loading}
                className="w-full bg-gradient-to-r from-green-500 to-purple-600 hover:from-green-600 hover:to-purple-700 text-white font-medium py-3 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
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