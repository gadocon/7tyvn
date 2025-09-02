import { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, NavLink, useLocation } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Textarea } from "./components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Badge } from "./components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./components/ui/table";
import { Separator } from "./components/ui/separator";
import { Toaster } from "./components/ui/sonner";
import { toast } from "sonner";
import { 
  BarChart3, 
  FileCheck, 
  Package, 
  Users, 
  ShoppingCart, 
  TrendingUp,
  Search,
  Plus,
  DollarSign,
  Clock,
  CheckCircle,
  XCircle,
  Home,
  AlertTriangle,
  Upload,
  Download,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Trash2,
  RefreshCw,
  CreditCard
} from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Navigation Component
const Navigation = () => {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const navItems = [
    { path: "/", label: "Dashboard", icon: Home },
    { path: "/check-bill", label: "Kiểm Tra Mã Điện", icon: FileCheck },
    { path: "/inventory", label: "Kho Bill", icon: Package },
    { path: "/customers", label: "Khách Hàng", icon: Users },
    { path: "/credit-cards", label: "Quản Lý Thẻ", icon: CreditCard },
    { path: "/sales", label: "Bán Bill", icon: ShoppingCart }
  ];

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <>
      {/* Top Navigation Bar */}
      <nav className="bg-white border-b border-gray-200 px-4 lg:px-6 py-4 fixed top-0 left-0 right-0 z-40">
        <div className="flex items-center justify-between">
          {/* Mobile Menu Button */}
          <div className="flex items-center space-x-4">
            <button
              onClick={toggleSidebar}
              className="md:hidden p-2 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <svg
                className="w-6 h-6 text-gray-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>

            {/* Logo */}
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900 hidden sm:block">FPT Bill Manager</span>
              <span className="text-lg font-bold text-gray-900 sm:hidden">FPT</span>
            </div>
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive 
                      ? "bg-blue-100 text-blue-700" 
                      : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </div>
          
          {/* Status Badge */}
          <div className="flex items-center space-x-4">
            <Badge variant="outline" className="text-green-600 border-green-200 hidden sm:flex">
              Đang hoạt động
            </Badge>
          </div>
        </div>
      </nav>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-50 md:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Mobile Sidebar */}
      <div className={`fixed top-0 left-0 h-full w-80 bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out md:hidden ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <BarChart3 className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">FPT Bill Manager</span>
          </div>
          <button
            onClick={closeSidebar}
            className="p-2 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <svg
              className="w-6 h-6 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Sidebar Navigation */}
        <div className="p-4">
          <div className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={closeSidebar}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors w-full ${
                    isActive 
                      ? "bg-blue-100 text-blue-700 border-r-4 border-blue-700" 
                      : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.label}</span>
                  {isActive && (
                    <div className="ml-auto">
                      <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                    </div>
                  )}
                </NavLink>
              );
            })}
          </div>

          {/* Sidebar Footer */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex items-center space-x-3 px-4 py-3">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">Hệ thống đang hoạt động</span>
            </div>
            <div className="px-4 py-2">
              <p className="text-xs text-gray-500">© 2025 FPT Bill Manager</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

// Dashboard Page
const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching dashboard stats:", error);
      toast.error("Không thể tải dữ liệu dashboard");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  const formatDateTimeVN = (dateString) => {
    const date = new Date(dateString);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear().toString().slice(-2);
    
    return `${hours}:${minutes} ${day}/${month}/${year}`;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="pb-2">
                <div className="h-4 bg-gray-200 rounded w-24"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 rounded w-16 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-20"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Tổng quan hệ thống quản lý bill điện</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <FileCheck className="h-4 w-4 mr-2" />
              Tổng Bill
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{stats?.total_bills || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Tất cả hóa đơn</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <CheckCircle className="h-4 w-4 mr-2" />
              Bill Có Sẵn
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.available_bills || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Sẵn sàng bán</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <Users className="h-4 w-4 mr-2" />
              Khách Hàng
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{stats?.total_customers || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Tổng khách hàng</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-orange-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <DollarSign className="h-4 w-4 mr-2" />
              Doanh Thu
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {formatCurrency(stats?.total_revenue || 0)}
            </div>
            <p className="text-xs text-gray-500 mt-1">Tổng lợi nhuận</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="h-5 w-5 mr-2" />
            Thao Tác Nhanh
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-24 flex flex-col items-center justify-center space-y-2">
              <Search className="h-6 w-6" />
              <span className="text-sm">Tra Cứu Bill</span>
            </Button>
            <Button variant="outline" className="h-24 flex flex-col items-center justify-center space-y-2">
              <Plus className="h-6 w-6" />
              <span className="text-sm">Thêm Vào Kho</span>
            </Button>
            <Button variant="outline" className="h-24 flex flex-col items-center justify-center space-y-2">
              <Users className="h-6 w-6" />
              <span className="text-sm">Quản Lý KH</span>
            </Button>
            <Button variant="outline" className="h-24 flex flex-col items-center justify-center space-y-2">
              <ShoppingCart className="h-6 w-6" />
              <span className="text-sm">Bán Bill</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activities */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Clock className="h-5 w-5 mr-2" />
            Hoạt Động Gần Đây
          </CardTitle>
        </CardHeader>
        <CardContent>
          {stats?.recent_activities?.length > 0 ? (
            <div className="space-y-4">
              {stats.recent_activities.map((activity, index) => (
                <div key={activity.id || index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-green-100 rounded-full">
                      <ShoppingCart className="h-4 w-4 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{activity.description}</p>
                      <p className="text-sm text-gray-500">{formatDate(activity.created_at)}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">{formatCurrency(activity.amount)}</p>
                    <p className="text-sm text-green-600">+{formatCurrency(activity.profit)}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Clock className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>Chưa có hoạt động gần đây</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Check Bill Page
const CheckBill = () => {
  const [codes, setCodes] = useState("");
  const [provider, setProvider] = useState("MIEN_NAM");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedBills, setSelectedBills] = useState([]);
  const [checkAllSelected, setCheckAllSelected] = useState(false);
  const [processingStep, setProcessingStep] = useState("");
  const [processedCount, setProcessedCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [okCount, setOkCount] = useState(0);
  const [errorCount, setErrorCount] = useState(0);

  const handleCheckBills = async () => {
    if (!codes.trim()) {
      toast.error("Vui lòng nhập mã điện");
      return;
    }

    setLoading(true);
    setProcessingStep("Đang chuẩn bị...");
    setProcessedCount(0);
    setResults([]);
    setSelectedBills([]);
    setOkCount(0);
    setErrorCount(0);
    
    try {
      const codeList = codes
        .split('\n')
        .map(code => code.trim())
        .filter(code => code.length > 0);

      setTotalCount(codeList.length);
      setProcessingStep(`Đang kiểm tra ${codeList.length} mã điện qua cổng FPT...`);

      // Process each bill one by one for realtime display
      const allResults = [];
      let currentOkCount = 0;
      let currentErrorCount = 0;

      for (let i = 0; i < codeList.length; i++) {
        const code = codeList[i];
        setProcessingStep(`Đang kiểm tra mã ${code}... (${i + 1}/${codeList.length})`);
        
        try {
          const response = await axios.post(`${API}/bill/check/single`, null, {
            params: {
              customer_code: code,
              provider_region: provider
            }
          });

          const result = response.data;
          allResults.push(result);
          
          if (result.status === "OK") {
            currentOkCount++;
            setOkCount(currentOkCount);
          } else {
            currentErrorCount++;
            setErrorCount(currentErrorCount);
          }

          // Update results in real-time
          setResults([...allResults]);
          setProcessedCount(i + 1);
          
        } catch (error) {
          // Handle individual bill errors
          const errorResult = {
            customer_code: code,
            status: "ERROR",
            errors: { message: "Lỗi kết nối" }
          };
          allResults.push(errorResult);
          currentErrorCount++;
          setErrorCount(currentErrorCount);
          setResults([...allResults]);
          setProcessedCount(i + 1);
        }

        // Small delay between requests to avoid overwhelming the server
        if (i < codeList.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      }

      setProcessingStep("Hoàn thành kiểm tra!");
      
      setTimeout(() => {
        setProcessingStep("");
        if (currentOkCount > 0) {
          toast.success(`Tìm thấy ${currentOkCount} bill hợp lệ`);
        }
        if (currentErrorCount > 0) {
          toast.warning(`${currentErrorCount} mã không tìm thấy`);
        }
      }, 1000);

    } catch (error) {
      console.error("Error checking bills:", error);
      toast.error("Có lỗi xảy ra khi kiểm tra bill");
      setProcessingStep("");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectBill = (bill, checked) => {
    if (bill.status !== "OK") return;
    
    if (checked) {
      setSelectedBills([...selectedBills, bill]);
    } else {
      setSelectedBills(selectedBills.filter(b => b.customer_code !== bill.customer_code));
      setCheckAllSelected(false);
    }
  };

  const handleCheckAll = (checked) => {
    setCheckAllSelected(checked);
    if (checked) {
      const validBills = results.filter(bill => bill.status === "OK") || [];
      setSelectedBills(validBills);
    } else {
      setSelectedBills([]);
    }
  };

  const handleAddToInventory = async () => {
    if (selectedBills.length === 0) {
      toast.error("Chưa chọn bill nào để thêm vào kho");
      return;
    }

    try {
      // Use bill_ids from the check results
      const billIds = selectedBills.map(bill => bill.bill_id).filter(id => id);
      
      if (billIds.length === 0) {
        toast.error("Không tìm thấy ID bill để thêm vào kho");
        return;
      }
      
      const response = await axios.post(`${API}/inventory/add`, {
        bill_ids: billIds,
        note: `Thêm từ kiểm tra mã điện - ${new Date().toLocaleDateString('vi-VN')}`,
        batch_name: `Check_${Date.now()}`
      });

      if (response.data.success) {
        toast.success(response.data.message);
        setSelectedBills([]);
        setCheckAllSelected(false);
        
        // Update results to show bills added to inventory
        setResults(results.map(item => 
          selectedBills.some(b => b.customer_code === item.customer_code)
            ? { ...item, status: "ADDED_TO_INVENTORY" }
            : item
        ));
      }
    } catch (error) {
      console.error("Error adding to inventory:", error);
      toast.error("Có lỗi xảy ra khi thêm vào kho");
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Kiểm Tra Mã Điện</h1>
        <p className="text-gray-600 mt-1">Tra cứu thông tin hóa đơn điện qua các cổng</p>
      </div>

      {/* Form Card */}
      <Card>
        <CardHeader>
          <CardTitle>Thông Tin Tra Cứu</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Gateway Tabs */}
          <Tabs defaultValue="fpt" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="fpt">Cổng FPT</TabsTrigger>
              <TabsTrigger value="shopee" disabled>
                Cổng Shopee
                <Badge variant="secondary" className="ml-2">Đang xây dựng</Badge>
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="fpt" className="space-y-4 mt-4">
              {/* Provider Selection */}
              <div className="space-y-2">
                <Label htmlFor="provider">Nhà Cung Cấp Điện</Label>
                <Select value={provider} onValueChange={setProvider}>
                  <SelectTrigger>
                    <SelectValue placeholder="Chọn nhà cung cấp" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="MIEN_BAC">Miền Bắc</SelectItem>
                    <SelectItem value="MIEN_NAM">Miền Nam</SelectItem>
                    <SelectItem value="HCMC">TP.HCM</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Code Input */}
              <div className="space-y-2">
                <Label htmlFor="codes">Mã Điện (mỗi dòng một mã)</Label>
                <Textarea
                  id="codes"
                  placeholder="PA2204000000&#10;PA22040522471&#10;INVALID123"
                  value={codes}
                  onChange={(e) => setCodes(e.target.value)}
                  rows={6}
                  className="font-mono"
                />
                <p className="text-sm text-gray-500">
                  Có thể dán kèm số tiền (sẽ tự động loại bỏ). Thử mã: <strong>PA2204000000</strong> (thành công)
                </p>
              </div>

              {/* Check Button */}
              <Button 
                onClick={handleCheckBills} 
                disabled={loading}
                className="w-full"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    {processingStep || "Đang kiểm tra..."}
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4 mr-2" />
                    Kiểm Tra Qua Cổng FPT  
                  </>
                )}
              </Button>

              {/* Processing Animation */}
              {loading && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center space-x-3">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-blue-900">{processingStep}</p>
                      {totalCount > 0 && (
                        <div className="mt-2">
                          <div className="bg-blue-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${(processedCount / totalCount) * 100}%` }}
                            ></div>
                          </div>
                          <p className="text-xs text-blue-700 mt-1">
                            {processedCount}/{totalCount} mã đã xử lý
                            {(okCount > 0 || errorCount > 0) && (
                              <span className="ml-2">
                                • <span className="text-green-600">{okCount} thành công</span>
                                • <span className="text-red-600">{errorCount} lỗi</span>
                              </span>
                            )}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Results */}
      {results.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Kết Quả Kiểm Tra</CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                Tìm thấy {okCount} bill hợp lệ, {errorCount} lỗi
                {loading && ` (đang xử lý...)`}
              </p>
            </div>
            {selectedBills.length > 0 && (
              <Button onClick={handleAddToInventory} className="bg-green-600 hover:bg-green-700">
                <Plus className="h-4 w-4 mr-2" />
                Thêm Vào Kho ({selectedBills.length})
              </Button>
            )}
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    {results.some(bill => bill.status === "OK") && (
                      <input
                        type="checkbox"
                        checked={checkAllSelected}
                        onChange={(e) => handleCheckAll(e.target.checked)}
                        className="rounded border-gray-300"
                        title="Chọn tất cả"
                      />
                    )}
                  </TableHead>
                  <TableHead>Mã Điện</TableHead>
                  <TableHead>Tên Khách Hàng</TableHead>
                  <TableHead>Địa Chỉ</TableHead>
                  <TableHead>Số Tiền</TableHead>
                  <TableHead>Kỳ Thanh Toán</TableHead>
                  <TableHead>Trạng Thái</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {results.map((bill, index) => (
                  <TableRow key={bill.customer_code} className={bill.status === "ERROR" ? "bg-red-50" : ""}>
                    <TableCell>
                      {bill.status === "OK" && (
                        <input
                          type="checkbox"
                          checked={selectedBills.some(b => b.customer_code === bill.customer_code)}
                          onChange={(e) => handleSelectBill(bill, e.target.checked)}
                          className="rounded border-gray-300"
                        />
                      )}
                    </TableCell>
                    <TableCell className="font-mono">{bill.customer_code}</TableCell>
                    <TableCell>{bill.full_name || "-"}</TableCell>
                    <TableCell className="max-w-xs truncate">{bill.address || "-"}</TableCell>
                    <TableCell>
                      {bill.amount ? formatCurrency(bill.amount) : "-"}
                    </TableCell>
                    <TableCell>{bill.billing_cycle || "-"}</TableCell>
                    <TableCell>
                      {bill.status === "OK" ? (
                        <Badge className="bg-green-100 text-green-800">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Hợp lệ
                        </Badge>
                      ) : bill.status === "ADDED_TO_INVENTORY" ? (
                        <Badge className="bg-blue-100 text-blue-800">
                          <Package className="h-3 w-3 mr-1" />
                          Đã thêm vào kho
                        </Badge>
                      ) : (
                        <Badge variant="destructive">
                          <XCircle className="h-3 w-3 mr-1" />
                          {bill.errors?.message || "Lỗi"}
                        </Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// Placeholder pages
// Inventory/Kho Bill Page
const Inventory = () => {
  const [inventoryStats, setInventoryStats] = useState(null);
  const [inventoryItems, setInventoryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("available");
  const [searchTerm, setSearchTerm] = useState("");
  const [showSellModal, setShowSellModal] = useState(false);
  const [selectedBillForSale, setSelectedBillForSale] = useState(null);
  const [showAddBillModal, setShowAddBillModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [allBills, setAllBills] = useState([]);
  const [showBulkDeleteConfirm, setShowBulkDeleteConfirm] = useState(false);
  const [recheckingBillId, setRecheckingBillId] = useState(null);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [billToTransfer, setBillToTransfer] = useState(null);

  useEffect(() => {
    fetchInventoryData();
    
    // Debug: Make functions globally accessible
    window.debugSelectItem = handleSelectItem;
    window.debugSelectedItems = selectedItems;
    console.log('=== Inventory Component Mounted ===');
  }, [activeTab, searchTerm]);

  const fetchInventoryData = async () => {
    try {
      // Fetch stats
      const statsResponse = await axios.get(`${API}/inventory/stats`);
      setInventoryStats(statsResponse.data);

      if (activeTab === "available") {
        // Fetch AVAILABLE bills (changed from inventory items to all available bills)
        const params = new URLSearchParams();
        params.append("status", "AVAILABLE");
        if (searchTerm) {
          params.append("search", searchTerm);
        }
        const billsResponse = await axios.get(`${API}/bills?${params.toString()}&limit=100`);
        setInventoryItems(billsResponse.data);
        setAllBills([]);
      } else {
        // Fetch all bills for "Tất cả bills" tab
        const params = new URLSearchParams();
        if (searchTerm) {
          params.append("search", searchTerm);
        }
        const billsResponse = await axios.get(`${API}/bills?${params.toString()}&limit=100`);
        setAllBills(billsResponse.data);
        setInventoryItems([]);
      }
    } catch (error) {
      console.error("Error fetching inventory data:", error);
      toast.error("Không thể tải dữ liệu kho");
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFromInventory = async (inventoryId) => {
    try {
      await axios.delete(`${API}/inventory/${inventoryId}`);
      toast.success("Đã xóa khỏi kho thành công");
      fetchInventoryData(); // Refresh data
    } catch (error) {
      console.error("Error removing from inventory:", error);
      toast.error("Có lỗi xảy ra khi xóa khỏi kho");
    }
  };

  const handleSellBill = (inventoryItem) => {
    setSelectedBillForSale(inventoryItem);
    setShowSellModal(true);
  };

  const handleSellComplete = () => {
    setShowSellModal(false);
    setSelectedBillForSale(null);
    fetchInventoryData(); // Refresh data
  };

  const handleDeleteBill = async (billId) => {
    // Use toast for simple confirmation instead of confirm()
    try {
      await axios.delete(`${API}/bills/${billId}`);
      toast.success("Đã xóa bill thành công");
      fetchInventoryData();
    } catch (error) {
      console.error("Error deleting bill:", error);
      // Show specific error message from backend
      const errorMessage = error.response?.data?.detail || "Có lỗi xảy ra khi xóa bill";
      toast.error(errorMessage);
    }
  };

  const handleAddBill = async (billData) => {
    try {
      await axios.post(`${API}/bills/create`, billData);
      toast.success("Đã thêm bill mới thành công!");
      setShowAddBillModal(false);
      fetchInventoryData(); // Refresh data
    } catch (error) {
      console.error("Error adding new bill:", error);
      toast.error(error.response?.data?.detail || "Có lỗi xảy ra khi thêm bill");
    }
  };

  const handleRecheckBill = async (bill) => {
    if (recheckingBillId === bill.id) return; // Prevent double clicks
    
    setRecheckingBillId(bill.id);
    
    try {
      // Call external API to check bill status (same as "Kiểm Tra Mã Điện" page)
      const response = await axios.post(`${API}/bill/check/single`, {
        bill_code: bill.customer_code,
        provider: bill.provider_region
      });

      if (response.data.status === "OK") {
        // Bill is valid - update status and show success
        toast.success(`Bill ${bill.customer_code} hợp lệ - Đã cập nhật trạng thái`);
        
        // Update bill's last_checked time in database
        await axios.put(`${API}/bills/${bill.id}`, {
          ...bill,
          last_checked: new Date().toISOString()
        });
        
        fetchInventoryData(); // Refresh data
        
      } else {
        // Bill not found - customer không nợ cước -> status "Đã Gạch"
        await axios.put(`${API}/bills/${bill.id}`, {
          ...bill,
          status: "CROSSED",
          full_name: "khách hàng ko nợ cước",
          last_checked: new Date().toISOString()
        });
        
        toast.info(`Bill ${bill.customer_code} - Khách hàng không nợ cước`);
        
        // Show transfer confirmation modal
        setBillToTransfer(bill);
        setShowTransferModal(true);
        
        fetchInventoryData(); // Refresh data
      }
      
    } catch (error) {
      console.error("Error rechecking bill:", error);
      toast.error("Có lỗi xảy ra khi check lại bill");
    } finally {
      setRecheckingBillId(null);
    }
  };

  // Bulk selection functions
  const handleSelectAll = (checked) => {
    if (checked) {
      const currentItems = activeTab === "available" ? inventoryItems : allBills;
      setSelectedItems(currentItems.map(item => item.id));
    } else {
      setSelectedItems([]);
    }
  };

  const handleSelectItem = (itemId, checked) => {
    console.log('=== handleSelectItem called ===', { itemId, checked });
    try {
      if (checked) {
        setSelectedItems(prev => {
          const newItems = [...prev, itemId];
          console.log('Adding item, prev:', prev, 'new:', newItems);
          return newItems;
        });
      } else {
        setSelectedItems(prev => {
          const newItems = prev.filter(id => id !== itemId);
          console.log('Removing item, prev:', prev, 'new:', newItems);
          return newItems;
        });
      }
    } catch (error) {
      console.error('Error in handleSelectItem:', error);
    }
  };

  // Sorting function
  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  // Apply sorting to data
  const getSortedData = () => {
    const currentItems = activeTab === "available" ? inventoryItems : allBills;
    if (!sortConfig.key) return currentItems;

    return [...currentItems].sort((a, b) => {
      const aValue = a[sortConfig.key] || '';
      const bValue = b[sortConfig.key] || '';
      
      if (sortConfig.direction === 'asc') {
        return aValue.toString().localeCompare(bValue.toString());
      } else {
        return bValue.toString().localeCompare(aValue.toString());
      }
    });
  };

  // Bulk actions
  const handleBulkDelete = async () => {
    if (selectedItems.length === 0) {
      toast.error("Vui lòng chọn ít nhất một item");
      return;
    }
    
    // Show custom confirmation modal instead of confirm()
    setShowBulkDeleteConfirm(true);
  };

  const confirmBulkDelete = async () => {
    console.log('=== confirmBulkDelete called ===');
    console.log('activeTab:', activeTab);
    console.log('selectedItems:', selectedItems);
    
    try {
      // For available items, remove from inventory
      if (activeTab === "available") {
        console.log('Deleting from inventory...');
        await Promise.all(selectedItems.map(id => {
          console.log(`DELETE ${API}/inventory/${id}`);
          return axios.delete(`${API}/inventory/${id}`);
        }));
        toast.success(`Đã xóa ${selectedItems.length} items khỏi kho`);
      } else {
        // For all bills, delete bills (if allowed)
        console.log('Deleting bills...');
        await Promise.all(selectedItems.map(id => {
          console.log(`DELETE ${API}/bills/${id}`);
          return axios.delete(`${API}/bills/${id}`);
        }));
        toast.success(`Đã xóa ${selectedItems.length} bills`);
      }
      
      setSelectedItems([]);
      setShowBulkDeleteConfirm(false);
      fetchInventoryData();
    } catch (error) {
      console.error("Error bulk deleting:", error);
      toast.error("Có lỗi xảy ra khi xóa hàng loạt");
      setShowBulkDeleteConfirm(false);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await axios.get(`${API}/inventory/template`, {
        responseType: 'blob'
      });
      
      // Create blob link to download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'template_import_bills.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success("Đã tải template thành công!");
    } catch (error) {
      console.error("Error downloading template:", error);
      toast.error("Có lỗi xảy ra khi tải template");
    }
  };

  const handleExportData = async (filters) => {
    try {
      const params = new URLSearchParams();
      if (filters.status && filters.status !== "ALL") params.append('status', filters.status);
      if (filters.provider_region && filters.provider_region !== "ALL") params.append('provider_region', filters.provider_region);
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      
      const response = await axios.get(`${API}/inventory/export?${params.toString()}`, {
        responseType: 'blob'
      });
      
      // Create blob link to download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'kho_bill_export.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success("Đã xuất dữ liệu thành công!");
      setShowExportModal(false);
    } catch (error) {
      console.error("Error exporting data:", error);
      toast.error("Có lỗi xảy ra khi xuất dữ liệu");
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="pb-2">
                <div className="h-4 bg-gray-200 rounded w-24"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 rounded w-16 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-20"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Kho Bill</h1>
          <p className="text-gray-600 mt-1">Quản lý hóa đơn điện trong kho</p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline"
            onClick={() => setShowImportModal(true)}
          >
            <Upload className="h-4 w-4 mr-2" />
            Import Excel
          </Button>
          <Button 
            variant="outline"
            onClick={() => setShowExportModal(true)}
          >
            <Download className="h-4 w-4 mr-2" />
            Export Excel
          </Button>
          <Button 
            className="bg-blue-600 hover:bg-blue-700"
            onClick={() => setShowAddBillModal(true)}
          >
            <Plus className="h-4 w-4 mr-2" />
            Thêm Bill Mới
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <Package className="h-4 w-4 mr-2" />
              Tổng Bill
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{inventoryStats?.total_bills || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Tất cả trong kho</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <CheckCircle className="h-4 w-4 mr-2" />
              Có Sẵn
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{inventoryStats?.available_bills || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Sẵn sàng bán</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-yellow-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <Clock className="h-4 w-4 mr-2" />
              Chờ Thanh Toán
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{inventoryStats?.pending_bills || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Đang xử lý</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <DollarSign className="h-4 w-4 mr-2" />
              Tổng Giá Trị
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {formatCurrency(inventoryStats?.total_value || 0)}
            </div>
            <p className="text-xs text-gray-500 mt-1">Giá trị kho</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Danh Sách Bill</CardTitle>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Tìm kiếm mã điện, tên khách hàng..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
            <TabsList>
              <TabsTrigger value="available">Bills Có Sẵn ({inventoryStats?.available_bills || 0})</TabsTrigger>
              <TabsTrigger value="all">Tất Cả Bills ({inventoryStats?.total_bills_in_system || allBills.length})</TabsTrigger>
            </TabsList>
          </Tabs>

          {/* Bulk Actions */}
          {selectedItems.length > 0 && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg flex justify-between items-center">
              <span className="text-blue-800">
                Đã chọn {selectedItems.length} item(s)
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={handleBulkDelete}
                className="text-red-600 hover:text-red-700"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Xóa Hàng Loạt
              </Button>
            </div>
          )}

          {/* Table */}
          {(() => {
            const currentItems = getSortedData();
            const showData = activeTab === "available" ? inventoryItems.length > 0 : allBills.length > 0;
            
            return showData ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">
                      <button
                        onClick={() => {
                          const shouldSelectAll = !(currentItems.length > 0 && selectedItems.length === currentItems.length);
                          console.log('Select all clicked:', shouldSelectAll);
                          handleSelectAll(shouldSelectAll);
                        }}
                        className="w-4 h-4 border border-gray-300 rounded cursor-pointer flex items-center justify-center hover:bg-blue-50"
                      >
                        {(currentItems.length > 0 && selectedItems.length === currentItems.length) && (
                          <CheckCircle className="h-3 w-3 text-blue-600" />
                        )}
                      </button>
                    </TableHead>
                    <TableHead 
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => handleSort(activeTab === "available" ? "customer_code" : "customer_code")}
                    >
                      <div className="flex items-center">
                        Mã Điện
                        {sortConfig.key === "customer_code" ? (
                          sortConfig.direction === 'asc' ? <ArrowUp className="h-4 w-4 ml-1" /> : <ArrowDown className="h-4 w-4 ml-1" />
                        ) : (
                          <ArrowUpDown className="h-4 w-4 ml-1" />
                        )}
                      </div>
                    </TableHead>
                    <TableHead 
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => handleSort("full_name")}
                    >
                      <div className="flex items-center">
                        Tên
                        {sortConfig.key === "full_name" ? (
                          sortConfig.direction === 'asc' ? <ArrowUp className="h-4 w-4 ml-1" /> : <ArrowDown className="h-4 w-4 ml-1" />
                        ) : (
                          <ArrowUpDown className="h-4 w-4 ml-1" />
                        )}
                      </div>
                    </TableHead>
                    <TableHead>Địa Chỉ</TableHead>
                    <TableHead 
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => handleSort("amount")}
                    >
                      <div className="flex items-center">
                        Số Tiền
                        {sortConfig.key === "amount" ? (
                          sortConfig.direction === 'asc' ? <ArrowUp className="h-4 w-4 ml-1" /> : <ArrowDown className="h-4 w-4 ml-1" />
                        ) : (
                          <ArrowUpDown className="h-4 w-4 ml-1" />
                        )}
                      </div>
                    </TableHead>
                    <TableHead>Kỳ</TableHead>
                    <TableHead 
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => handleSort("status")}
                    >
                      <div className="flex items-center">
                        Trạng Thái
                        {sortConfig.key === "status" ? (
                          sortConfig.direction === 'asc' ? <ArrowUp className="h-4 w-4 ml-1" /> : <ArrowDown className="h-4 w-4 ml-1" />
                        ) : (
                          <ArrowUpDown className="h-4 w-4 ml-1" />
                        )}
                      </div>
                    </TableHead>
                    <TableHead 
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => handleSort("created_at")}
                    >
                      <div className="flex items-center">
                        Ngày Thêm
                        {sortConfig.key === "created_at" ? (
                          sortConfig.direction === 'asc' ? <ArrowUp className="h-4 w-4 ml-1" /> : <ArrowDown className="h-4 w-4 ml-1" />
                        ) : (
                          <ArrowUpDown className="h-4 w-4 ml-1" />
                        )}
                      </div>
                    </TableHead>
                    <TableHead>Ghi Chú</TableHead>
                    <TableHead>Thao Tác</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {currentItems.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <button
                          onClick={() => {
                            console.log('=== BUTTON CLICKED ===', item.id);
                            const isCurrentlySelected = selectedItems.includes(item.id);
                            console.log('Current selected items:', selectedItems);
                            console.log('Is currently selected:', isCurrentlySelected);
                            handleSelectItem(item.id, !isCurrentlySelected);
                          }}
                          className="w-4 h-4 border border-gray-300 rounded cursor-pointer flex items-center justify-center hover:bg-blue-50"
                        >
                          {selectedItems.includes(item.id) && (
                            <CheckCircle className="h-3 w-3 text-blue-600" />
                          )}
                        </button>
                      </TableCell>
                      <TableCell className="font-mono">{item.customer_code}</TableCell>
                      <TableCell>{item.full_name || "-"}</TableCell>
                      <TableCell className="max-w-xs truncate">{item.address || "-"}</TableCell>
                      <TableCell>{item.amount ? formatCurrency(item.amount) : "-"}</TableCell>
                      <TableCell>{item.billing_cycle || "-"}</TableCell>
                      <TableCell>
                        {item.status === "AVAILABLE" ? (
                          <Badge className="bg-green-100 text-green-800">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Có Sẵn  
                          </Badge>
                        ) : item.status === "PENDING" ? (
                          <Badge className="bg-yellow-100 text-yellow-800">
                            <Clock className="h-3 w-3 mr-1" />
                            Chờ Thanh Toán
                          </Badge>
                        ) : item.status === "SOLD" ? (
                          <Badge className="bg-red-100 text-red-800">
                            <XCircle className="h-3 w-3 mr-1" />
                            Đã Bán
                          </Badge>
                        ) : item.status === "CROSSED" ? (
                          <Badge className="bg-orange-100 text-orange-800">
                            <XCircle className="h-3 w-3 mr-1" />
                            Đã Gạch
                          </Badge>
                        ) : (
                          <Badge className="bg-gray-100 text-gray-800">
                            {item.status}
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-xs">
                        {item.created_at ? (() => {
                          const date = new Date(item.created_at);
                          const hours = date.getHours().toString().padStart(2, '0');
                          const minutes = date.getMinutes().toString().padStart(2, '0');
                          const day = date.getDate().toString().padStart(2, '0');
                          const month = (date.getMonth() + 1).toString().padStart(2, '0');
                          return `${hours}:${minutes} ${day}/${month}`;
                        })() : "-"}
                      </TableCell>
                      <TableCell className="max-w-xs truncate">
                        {item.note || "-"}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {/* Check lại button - only for AVAILABLE bills */}
                          {item.status === "AVAILABLE" && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleRecheckBill(item)}
                              disabled={recheckingBillId === item.id}
                              className="text-blue-600 hover:text-blue-700"
                              title="Check lại mã điện"
                            >
                              <RefreshCw className={`h-3 w-3 ${recheckingBillId === item.id ? 'animate-spin' : ''}`} />
                            </Button>
                          )}
                          
                          {item.status === "AVAILABLE" && activeTab === "available" && (
                            <Button
                              size="sm"
                              onClick={() => handleSellBill(item)}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              Bán
                            </Button>
                          )}
                          {/* Hide delete button for SOLD and CROSSED bills to prevent data integrity issues */}
                          {item.status !== "SOLD" && item.status !== "CROSSED" && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => activeTab === "available" 
                                ? handleRemoveFromInventory(item.id)
                                : handleDeleteBill(item.id)
                              }
                              className="text-red-600 hover:text-red-700"
                            >
                              Xóa
                            </Button>
                          )}
                          {/* Show info for SOLD/CROSSED bills instead of delete button */}
                          {(item.status === "SOLD" || item.status === "CROSSED") && (
                            <span className="text-sm text-gray-500 italic">
                              {item.status === "SOLD" ? "Không thể xóa bill đã bán" : "Không thể xóa bill đã gạch"}
                            </span>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-12">
                <Package className="h-16 w-16 mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {activeTab === "available" ? "Chưa có bill nào trong kho" : "Chưa có bill nào"}
                </h3>
                <p className="text-gray-500 mb-4">
                  {activeTab === "available" 
                    ? "Thêm bill vào kho để bắt đầu quản lý"
                    : "Thêm bill mới để bắt đầu"
                  }
                </p>
                <Button onClick={() => setShowAddBillModal(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Thêm Bill Đầu Tiên
                </Button>
              </div>
            );
          })()}
        </CardContent>
      </Card>

      {/* Sell Bill Modal */}
      <SellBillModal
        show={showSellModal}
        billItem={selectedBillForSale}
        onClose={() => setShowSellModal(false)}
        onComplete={handleSellComplete}
      />

      {/* Add Bill Modal */}
      <AddBillModal
        show={showAddBillModal}
        onClose={() => setShowAddBillModal(false)}
        onSubmit={handleAddBill}
      />

      {/* Import Modal */}
      <ImportModal
        show={showImportModal}
        onClose={() => setShowImportModal(false)}
        onImportComplete={() => {
          setShowImportModal(false);
          fetchInventoryData();
        }}
        onDownloadTemplate={handleDownloadTemplate}
      />

      {/* Export Modal */}
      <ExportModal
        show={showExportModal}
        onClose={() => setShowExportModal(false)}
        onExport={handleExportData}
      />

      {/* Bulk Delete Confirmation Modal */}
      {showBulkDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex items-center mb-4">
              <AlertTriangle className="h-6 w-6 text-red-600 mr-3" />
              <h2 className="text-xl font-semibold text-gray-900">Xác Nhận Xóa</h2>
            </div>
            
            <p className="text-gray-600 mb-6">
              Bạn có chắc muốn xóa <strong>{selectedItems.length}</strong> item(s) đã chọn? 
              Hành động này không thể hoàn tác.
            </p>
            
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setShowBulkDeleteConfirm(false)}
                className="flex-1"
              >
                Hủy
              </Button>
              <Button
                onClick={confirmBulkDelete}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Xóa
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Transfer Bill Confirmation Modal */}
      {showTransferModal && billToTransfer && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex items-center mb-4">
              <AlertTriangle className="h-6 w-6 text-orange-600 mr-3" />
              <h2 className="text-xl font-semibold text-gray-900">Bill Đã Gạch</h2>
            </div>
            
            <div className="mb-6">
              <p className="text-gray-800 mb-3">
                Bill <strong>{billToTransfer.customer_code}</strong> - Khách hàng không nợ cước.
              </p>
              <p className="text-gray-600">
                Bạn có muốn chuyển đơn này cho khách hàng?
              </p>
            </div>
            
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => {
                  setShowTransferModal(false);
                  setBillToTransfer(null);
                }}
                className="flex-1"
              >
                Không
              </Button>
              <Button
                onClick={() => {
                  // Open sell bill modal
                  setSelectedBillForSale(billToTransfer);
                  setShowSellModal(true);
                  setShowTransferModal(false);
                  setBillToTransfer(null);
                }}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white"
              >
                Chuyển
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Customers/Khách Hàng Page
const Customers = () => {
  const [customers, setCustomers] = useState([]);
  const [customerStats, setCustomerStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [customerType, setCustomerType] = useState("");
  const [isActive, setIsActive] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [customerDetail, setCustomerDetail] = useState(null);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [customerToDelete, setCustomerToDelete] = useState(null);

  useEffect(() => {
    fetchCustomersData();
  }, [searchTerm, customerType, isActive]);

  const fetchCustomersData = async () => {
    try {
      // Fetch stats
      const statsResponse = await axios.get(`${API}/customers/stats`);
      setCustomerStats(statsResponse.data);

      // Fetch customers with filters
      const params = new URLSearchParams();
      if (searchTerm) params.append("search", searchTerm);
      if (customerType) params.append("customer_type", customerType);
      if (isActive !== "") params.append("is_active", isActive);

      const customersResponse = await axios.get(`${API}/customers?${params.toString()}`);
      setCustomers(customersResponse.data);
    } catch (error) {
      console.error("Error fetching customers data:", error);
      toast.error("Không thể tải dữ liệu khách hàng");
    } finally {
      setLoading(false);
    }
  };

  const handleAddCustomer = async (customerData) => {
    try {
      await axios.post(`${API}/customers`, customerData);
      toast.success("Đã thêm khách hàng thành công");
      setShowAddModal(false);
      fetchCustomersData();
    } catch (error) {
      console.error("Error adding customer:", error);
      toast.error(error.response?.data?.detail || "Có lỗi xảy ra khi thêm khách hàng");
    }
  };

  const handleUpdateCustomer = async (customerId, customerData) => {
    try {
      await axios.put(`${API}/customers/${customerId}`, customerData);
      toast.success("Đã cập nhật khách hàng thành công");
      setEditingCustomer(null);
      fetchCustomersData();
    } catch (error) {
      console.error("Error updating customer:", error);
      toast.error(error.response?.data?.detail || "Có lỗi xảy ra khi cập nhật khách hàng");
    }
  };

  const handleDeleteCustomer = (customer) => {
    setCustomerToDelete(customer);
    setShowDeleteConfirm(true);
  };

  const confirmDeleteCustomer = async () => {
    if (!customerToDelete) return;
    
    try {
      const response = await axios.delete(`${API}/customers/${customerToDelete.id}`);
      toast.success(response.data.message || "Đã xóa khách hàng thành công");
      setShowDeleteConfirm(false);
      setCustomerToDelete(null);
      fetchCustomersData();
    } catch (error) {
      console.error("Error deleting customer:", error);
      toast.error(error.response?.data?.detail || "Có lỗi xảy ra khi xóa khách hàng");
      setShowDeleteConfirm(false);
    }
  };

  const handleViewCustomerDetail = async (customerId) => {
    try {
      const response = await axios.get(`${API}/customers/${customerId}/transactions`);
      setCustomerDetail(response.data);
    } catch (error) {
      console.error("Error fetching customer detail:", error);
      toast.error("Không thể tải chi tiết khách hàng");
    }
  };

  const handleExportCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers/export`, {
        responseType: 'blob'
      });
      
      // Create blob link to download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'khach_hang_export.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success("Đã xuất dữ liệu khách hàng thành công!");
      setShowExportModal(false);
    } catch (error) {
      console.error("Error exporting customers:", error);
      toast.error("Có lỗi xảy ra khi xuất dữ liệu");
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="pb-2">
                <div className="h-4 bg-gray-200 rounded w-24"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 rounded w-16 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-20"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Quản Lý Khách Hàng</h1>
          <p className="text-gray-600 mt-1">Danh sách khách hàng và thông tin giao dịch</p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline"
            onClick={() => setShowExportModal(true)}
          >
            <Download className="h-4 w-4 mr-2" />
            Export Excel
          </Button>
          <Button onClick={() => setShowAddModal(true)} className="bg-blue-600 hover:bg-blue-700">
            <Plus className="h-4 w-4 mr-2" />
            Thêm Khách Hàng
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <Users className="h-4 w-4 mr-2" />
              Tổng Khách Hàng
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{customerStats?.total_customers || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Tất cả khách hàng</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <Users className="h-4 w-4 mr-2" />
              Cá Nhân
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{customerStats?.individual_customers || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Khách cá nhân</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <Users className="h-4 w-4 mr-2" />
              Đại Lý
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{customerStats?.agent_customers || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Đại lý/Doanh nghiệp</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-yellow-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <CheckCircle className="h-4 w-4 mr-2" />
              Hoạt Động
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{customerStats?.active_customers || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Đang hoạt động</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-orange-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <DollarSign className="h-4 w-4 mr-2" />
              Tổng Giá Trị
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {formatCurrency(customerStats?.total_customer_value || 0)}
            </div>
            <p className="text-xs text-gray-500 mt-1">Giá trị khách hàng</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Danh Sách Khách Hàng</CardTitle>
            <div className="flex items-center space-x-4">
              <select 
                value={customerType || ""} 
                onChange={(e) => setCustomerType(e.target.value)}
                className="border border-gray-300 rounded px-3 py-2 text-sm w-40"
              >
                <option value="">Tất cả loại</option>
                <option value="INDIVIDUAL">Cá nhân</option>
                <option value="AGENT">Đại lý</option>
              </select>

              <select 
                value={isActive || ""} 
                onChange={(e) => setIsActive(e.target.value)}
                className="border border-gray-300 rounded px-3 py-2 text-sm w-40"
              >
                <option value="">Tất cả trạng thái</option>
                <option value="true">Hoạt động</option>
                <option value="false">Ngưng</option>
              </select>

              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Tìm kiếm khách hàng..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Customer Table */}
          {customers.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tên</TableHead>
                  <TableHead>Loại</TableHead>
                  <TableHead>Điện Thoại</TableHead>
                  <TableHead>Số GD</TableHead>
                  <TableHead>Tổng Giá Trị</TableHead>
                  <TableHead>Lợi Nhuận</TableHead>
                  <TableHead>Trạng Thái</TableHead>
                  <TableHead>Thao Tác</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {customers.map((customer) => (
                  <TableRow key={customer.id}>
                    <TableCell className="font-medium">{customer.name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {customer.type === "INDIVIDUAL" ? "Cá nhân" : "Đại lý"}
                      </Badge>
                    </TableCell>
                    <TableCell>{customer.phone || "-"}</TableCell>
                    <TableCell>{customer.total_transactions}</TableCell>
                    <TableCell>{formatCurrency(customer.total_value)}</TableCell>
                    <TableCell>{formatCurrency(customer.total_profit_generated)}</TableCell>
                    <TableCell>
                      {customer.is_active ? (
                        <Badge className="bg-green-100 text-green-800">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Hoạt động
                        </Badge>
                      ) : (
                        <Badge variant="secondary">
                          <XCircle className="h-3 w-3 mr-1" />
                          Ngưng
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleViewCustomerDetail(customer.id)}
                        >
                          Xem
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setEditingCustomer(customer)}
                        >
                          Sửa
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteCustomer(customer)}
                          className="text-red-600 hover:text-red-700"
                        >
                          Xóa
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-12">
              <Users className="h-16 w-16 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Chưa có khách hàng</h3>
              <p className="text-gray-500 mb-4">Bắt đầu bằng cách thêm khách hàng đầu tiên</p>
              <Button onClick={() => setShowAddModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Thêm Khách Hàng Đầu Tiên
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add/Edit Customer Modal */}
      <CustomerModal
        show={showAddModal || editingCustomer}
        customer={editingCustomer}
        onClose={() => {
          setShowAddModal(false);
          setEditingCustomer(null);
        }}
        onSave={editingCustomer ? handleUpdateCustomer : handleAddCustomer}
      />

      {/* Customer Detail Modal */}
      <CustomerDetailModal
        customerDetail={customerDetail}
        onClose={() => setCustomerDetail(null)}
      />

      {/* Customer Export Modal */}
      <CustomerExportModal
        show={showExportModal}
        onClose={() => setShowExportModal(false)}
        onExport={handleExportCustomers}
      />

      {/* Customer Delete Confirmation Modal */}
      {showDeleteConfirm && customerToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <div className="flex items-center mb-4">
              <AlertTriangle className="h-8 w-8 text-red-600 mr-3" />
              <h2 className="text-xl font-semibold text-gray-900">Cảnh Báo Xóa Khách Hàng</h2>
            </div>
            
            <div className="mb-6">
              <p className="text-gray-800 mb-3">
                Bạn có chắc muốn xóa khách hàng <strong>"{customerToDelete.name}"</strong>?
              </p>
              
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h4 className="font-semibold text-red-800 mb-2">⚠️ Hành động này sẽ:</h4>
                <ul className="text-red-700 text-sm space-y-1">
                  <li>• <strong>Xóa vĩnh viễn</strong> khách hàng "{customerToDelete.name}"</li>
                  <li>• <strong>Xóa tất cả</strong> giao dịch liên quan ({customerToDelete.total_transactions} giao dịch)</li>
                  <li>• <strong>Xóa tất cả</strong> mã bill điện liên quan</li>
                  <li>• <strong>Không thể khôi phục</strong> sau khi xóa</li>
                </ul>
              </div>
            </div>
            
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setCustomerToDelete(null);
                }}
                className="flex-1"
              >
                Hủy
              </Button>
              <Button
                onClick={confirmDeleteCustomer}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Xóa Vĩnh Viễn
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Customer Modal Component
const CustomerModal = ({ show, customer, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: "",
    type: "INDIVIDUAL",
    phone: "",
    email: "",
    address: "",
    notes: ""
  });

  useEffect(() => {
    if (customer) {
      setFormData({
        name: customer.name || "",
        type: customer.type || "INDIVIDUAL",
        phone: customer.phone || "",
        email: customer.email || "",
        address: customer.address || "",
        notes: customer.notes || ""
      });
    } else {
      setFormData({
        name: "",
        type: "INDIVIDUAL",
        phone: "",
        email: "",
        address: "",
        notes: ""
      });
    }
  }, [customer]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      toast.error("Vui lòng nhập tên khách hàng");
      return;
    }

    if (customer) {
      onSave(customer.id, formData);
    } else {
      onSave(formData);
    }
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">
          {customer ? "Sửa Khách Hàng" : "Thêm Khách Hàng"}
        </h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="name">Tên Khách Hàng *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Nhập tên khách hàng"
              required
            />
          </div>

          <div>
            <Label htmlFor="type">Loại Khách Hàng</Label>
            <Select value={formData.type} onValueChange={(value) => setFormData({ ...formData, type: value })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="INDIVIDUAL">Cá nhân</SelectItem>
                <SelectItem value="AGENT">Đại lý</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="phone">Số Điện Thoại</Label>
            <Input
              id="phone"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              placeholder="Nhập số điện thoại"
            />
          </div>

          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="Nhập email"
            />
          </div>

          <div>
            <Label htmlFor="address">Địa Chỉ</Label>
            <Textarea
              id="address"
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              placeholder="Nhập địa chỉ"
              rows={2}
            />
          </div>

          <div>
            <Label htmlFor="notes">Ghi Chú</Label>
            <Textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              placeholder="Nhập ghi chú"
              rows={2}
            />
          </div>

          <div className="flex justify-end space-x-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Hủy
            </Button>
            <Button type="submit">
              {customer ? "Cập nhật" : "Thêm"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Customer Detail Modal Component
const CustomerDetailModal = ({ customerDetail, onClose }) => {
  if (!customerDetail) return null;

  const { customer, transactions, summary } = customerDetail;

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  const formatDateTimeVN = (dateString) => {
    const date = new Date(dateString);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear().toString().slice(-2);
    
    return `${hours}:${minutes} ${day}/${month}/${year}`;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold">Chi Tiết Khách Hàng</h3>
          <Button variant="outline" onClick={onClose}>
            <XCircle className="h-4 w-4" />
          </Button>
        </div>

        {/* Customer Info */}
        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-3">Thông Tin Khách Hàng</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div><strong>Tên:</strong> {customer.name}</div>
            <div><strong>Loại:</strong> {customer.type === "INDIVIDUAL" ? "Cá nhân" : "Đại lý"}</div>
            <div><strong>Điện thoại:</strong> {customer.phone || "-"}</div>
            <div><strong>Email:</strong> {customer.email || "-"}</div>
            <div className="col-span-2"><strong>Địa chỉ:</strong> {customer.address || "-"}</div>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-blue-600">{summary.total_transactions}</div>
              <p className="text-xs text-gray-500">Tổng Giao Dịch</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-green-600">{formatCurrency(summary.total_value)}</div>
              <p className="text-xs text-gray-500">Tổng Giá Trị</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-purple-600">{formatCurrency(summary.total_profit)}</div>
              <p className="text-xs text-gray-500">Tổng Lợi Nhuận</p>
            </CardContent>
          </Card>
        </div>

        {/* Transaction History */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3">Lịch Sử Giao Dịch</h4>
          {transactions.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Mã GD</TableHead>
                  <TableHead>Mã Bill/Thẻ</TableHead>
                  <TableHead>Ngày Giờ</TableHead>
                  <TableHead>Loại</TableHead>
                  <TableHead>Tổng Tiền</TableHead>
                  <TableHead>Lợi Nhuận</TableHead>
                  <TableHead>Trả Khách</TableHead>
                  <TableHead>Trạng Thái</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {transactions.map((transaction) => (
                  <TableRow key={transaction.id}>
                    <TableCell className="font-mono text-xs">
                      {transaction.id.slice(-8)}
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {transaction.bill_codes && transaction.bill_codes.length > 0 
                        ? transaction.bill_codes.join(", ") 
                        : "-"}
                    </TableCell>
                    <TableCell className="text-xs">
                      {formatDateTimeVN(transaction.created_at)}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">Bán Bill</Badge>
                    </TableCell>
                    <TableCell>{formatCurrency(transaction.total)}</TableCell>
                    <TableCell>{formatCurrency(transaction.profit_value)}</TableCell>
                    <TableCell>{formatCurrency(transaction.payback)}</TableCell>
                    <TableCell>
                      <Badge className="bg-green-100 text-green-800">
                        {transaction.status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>Chưa có giao dịch nào</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Customer Export Modal Component
const CustomerExportModal = ({ show, onClose, onExport }) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Export Khách Hàng</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="space-y-4">
          <div className="border rounded-lg p-4 bg-green-50">
            <h3 className="font-medium text-green-900 mb-2">Dữ Liệu Export</h3>
            <ul className="text-green-700 text-sm space-y-1">
              <li>• Danh sách tất cả khách hàng</li>
              <li>• Thông tin chi tiết (tên, SĐT, email, địa chỉ)</li>
              <li>• Thống kê giao dịch và lợi nhuận</li>
              <li>• Lịch sử giao dịch (sheet riêng)</li>
            </ul>
          </div>

          <div className="border rounded-lg p-4 bg-blue-50">
            <h3 className="font-medium text-blue-900 mb-2">File Excel</h3>
            <p className="text-blue-700 text-sm">
              File sẽ có 2 sheets: "Khách Hàng" và "Giao Dịch" với đầy đủ thông tin và định dạng chuyên nghiệp.
            </p>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <Button
            variant="outline"
            onClick={onClose}
            className="flex-1"
          >
            Hủy
          </Button>
          <Button
            onClick={onExport}
            className="flex-1 bg-green-600 hover:bg-green-700"
          >
            <Download className="h-4 w-4 mr-2" />
            Export Excel
          </Button>
        </div>
      </div>
    </div>
  );
};

const Sales = () => {
  const [showExportModal, setShowExportModal] = useState(false);

  const handleExportSales = async () => {
    try {
      const response = await axios.get(`${API}/sales/export`, {
        responseType: 'blob'
      });
      
      // Create blob link to download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'lich_su_ban_bill.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success("Đã xuất lịch sử bán bill thành công!");
      setShowExportModal(false);
    } catch (error) {
      console.error("Error exporting sales:", error);
      toast.error("Có lỗi xảy ra khi xuất dữ liệu");
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Lịch Sử Bán Bill</h1>
          <p className="text-gray-600 mt-1">Quản lý và xuất dữ liệu giao dịch bán bill</p>
        </div>
        <Button 
          variant="outline"
          onClick={() => setShowExportModal(true)}
        >
          <Download className="h-4 w-4 mr-2" />
          Export Excel
        </Button>
      </div>

      {/* Stats or Table would go here - for now showing export feature */}
      <Card>
        <CardContent className="p-8">
          <div className="text-center">
            <ShoppingCart className="h-16 w-16 mx-auto text-green-600 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Export Lịch Sử Giao Dịch</h3>
            <p className="text-gray-500 mb-6">
              Xuất toàn bộ lịch sử bán bill ra file Excel với đầy đủ thông tin giao dịch
            </p>
            <Button 
              onClick={() => setShowExportModal(true)}
              className="bg-green-600 hover:bg-green-700"
            >
              <Download className="h-4 w-4 mr-2" />
              Export Dữ Liệu
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Sales Export Modal */}
      <SalesExportModal
        show={showExportModal}
        onClose={() => setShowExportModal(false)}
        onExport={handleExportSales}
      />
    </div>
  );
};

// Sell Bill Modal Component
const SellBillModal = ({ show, billItem, onClose, onComplete }) => {
  const [customers, setCustomers] = useState([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState("");
  const [profitPct, setProfitPct] = useState(10);
  const [paymentMethod, setPaymentMethod] = useState("CASH");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  
  // Calculated values
  const billAmount = billItem?.amount || 0;
  const profitValue = Math.round(billAmount * profitPct / 100);
  const paybackAmount = billAmount - profitValue;

  useEffect(() => {
    if (show) {
      fetchCustomers();
      // Reset form
      setSelectedCustomerId("");
      setProfitPct(10);
      setPaymentMethod("CASH");
      setNotes("");
    }
  }, [show]);

  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers?is_active=true`);
      setCustomers(response.data);
    } catch (error) {
      console.error("Error fetching customers:", error);
      toast.error("Không thể tải danh sách khách hàng");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedCustomerId) {
      toast.error("Vui lòng chọn khách hàng");
      return;
    }

    if (profitPct < 0 || profitPct > 100) {
      toast.error("% Lợi nhuận phải từ 0 đến 100");
      return;
    }

    setLoading(true);
    
    try {
      const saleData = {
        customer_id: selectedCustomerId,
        bill_ids: [billItem.bill_id],
        profit_pct: profitPct,
        method: paymentMethod,
        notes: notes || `Bán bill ${billItem.customer_code} - ${new Date().toLocaleDateString('vi-VN')}`
      };

      await axios.post(`${API}/sales`, saleData);
      
      toast.success("Đã tạo giao dịch bán bill thành công!");
      onComplete();
      
    } catch (error) {
      console.error("Error creating sale:", error);
      toast.error(error.response?.data?.detail || "Có lỗi xảy ra khi tạo giao dịch");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount);
  };

  if (!show || !billItem) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold">Bán Bill</h3>
          <Button variant="outline" onClick={onClose}>
            <XCircle className="h-4 w-4" />
          </Button>
        </div>

        {/* Bill Info */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-3">Thông Tin Bill</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div><strong>Mã điện:</strong> {billItem.customer_code}</div>
            <div><strong>Tên KH:</strong> {billItem.full_name || "-"}</div>
            <div><strong>Số tiền:</strong> {formatCurrency(billAmount)}</div>
            <div><strong>Kỳ thanh toán:</strong> {billItem.billing_cycle || "-"}</div>
            <div className="col-span-2"><strong>Địa chỉ:</strong> {billItem.address || "-"}</div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Customer Selection */}
          <div>
            <Label htmlFor="customer">Chọn Khách Hàng *</Label>
            <select
              id="customer"
              value={selectedCustomerId}
              onChange={(e) => setSelectedCustomerId(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm mt-1"
              required
            >
              <option value="">-- Chọn khách hàng --</option>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name} - {customer.type === "INDIVIDUAL" ? "Cá nhân" : "Đại lý"}
                  {customer.phone && ` - ${customer.phone}`}
                </option>
              ))}
            </select>
          </div>

          {/* Profit Percentage */}
          <div>
            <Label htmlFor="profitPct">% Lợi Nhuận *</Label>
            <Input
              id="profitPct"
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={profitPct}
              onChange={(e) => setProfitPct(parseFloat(e.target.value) || 0)}
              className="mt-1"
              required
            />
            <p className="text-sm text-gray-500 mt-1">Nhập % lợi nhuận từ 0 đến 100</p>
          </div>

          {/* Payment Method */}
          <div>
            <Label htmlFor="paymentMethod">Phương Thức Thanh Toán</Label>
            <select
              id="paymentMethod"
              value={paymentMethod}
              onChange={(e) => setPaymentMethod(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm mt-1"
            >
              <option value="CASH">Tiền mặt</option>
              <option value="BANK_TRANSFER">Chuyển khoản</option>
              <option value="OTHER">Khác</option>
            </select>
          </div>

          {/* Notes */}
          <div>
            <Label htmlFor="notes">Ghi Chú</Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Nhập ghi chú cho giao dịch..."
              rows={3}
              className="mt-1"
            />
          </div>

          {/* Calculation Summary */}
          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-3">Tính Toán Giao Dịch</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex justify-between">
                <span>Tổng giá bill:</span>
                <span className="font-semibold">{formatCurrency(billAmount)}</span>
              </div>
              <div className="flex justify-between">
                <span>% Lợi nhuận:</span>
                <span className="font-semibold">{profitPct}%</span>
              </div>
              <div className="flex justify-between text-green-600">
                <span>Lợi nhuận:</span>
                <span className="font-semibold">{formatCurrency(profitValue)}</span>
              </div>
              <div className="flex justify-between text-blue-600">
                <span>Số tiền trả khách:</span>
                <span className="font-semibold">{formatCurrency(paybackAmount)}</span>
              </div>
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-2">
            <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
              Hủy
            </Button>
            <Button 
              type="submit" 
              disabled={loading}
              className="bg-green-600 hover:bg-green-700"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Đang xử lý...
                </>
              ) : (
                <>
                  <DollarSign className="h-4 w-4 mr-2" />
                  Tạo Giao Dịch Bán
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Add Bill Modal Component
const AddBillModal = ({ show, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    customer_code: "",
    provider_region: "MIEN_NAM",
    full_name: "",
    address: "",
    amount: "",
    billing_cycle: "",
    status: "AVAILABLE"
  });
  const [loading, setLoading] = useState(false);

  // Reset form when modal opens
  useEffect(() => {
    if (show) {
      setFormData({
        customer_code: "",
        provider_region: "MIEN_NAM",
        full_name: "",
        address: "",
        amount: "",
        billing_cycle: "",
        status: "AVAILABLE"
      });
    }
  }, [show]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.customer_code.trim()) {
      toast.error("Vui lòng nhập mã điện");
      return;
    }

    setLoading(true);
    
    try {
      // Prepare data for API
      const submitData = {
        ...formData,
        amount: formData.amount ? parseFloat(formData.amount) : null
      };
      
      await onSubmit(submitData);
    } catch (error) {
      console.error("Error submitting form:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Thêm Bill Mới</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Mã điện */}
          <div>
            <Label htmlFor="customer_code" className="text-sm font-medium text-gray-700">
              Mã điện <span className="text-red-500">*</span>
            </Label>
            <Input
              id="customer_code"
              type="text"
              value={formData.customer_code}
              onChange={(e) => handleInputChange("customer_code", e.target.value)}
              placeholder="Nhập mã điện"
              className="mt-1"
              required
            />
          </div>

          {/* Nhà cung cấp */}
          <div>
            <Label htmlFor="provider_region" className="text-sm font-medium text-gray-700">
              Nhà Cung Cấp Điện
            </Label>
            <Select 
              value={formData.provider_region} 
              onValueChange={(value) => handleInputChange("provider_region", value)}
            >
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Chọn nhà cung cấp" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="MIEN_BAC">Miền Bắc</SelectItem>
                <SelectItem value="MIEN_NAM">Miền Nam</SelectItem>
                <SelectItem value="HCMC">TP. Hồ Chí Minh</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Tên khách hàng */}
          <div>
            <Label htmlFor="full_name" className="text-sm font-medium text-gray-700">
              Tên Khách Hàng
            </Label>
            <Input
              id="full_name"
              type="text"
              value={formData.full_name}
              onChange={(e) => handleInputChange("full_name", e.target.value)}
              placeholder="Nhập tên khách hàng"
              className="mt-1"
            />
          </div>

          {/* Địa chỉ */}
          <div>
            <Label htmlFor="address" className="text-sm font-medium text-gray-700">
              Địa Chỉ
            </Label>
            <Textarea
              id="address"
              value={formData.address}
              onChange={(e) => handleInputChange("address", e.target.value)}
              placeholder="Nhập địa chỉ"
              className="mt-1"
              rows={2}
            />
          </div>

          {/* Nợ cước */}
          <div>
            <Label htmlFor="amount" className="text-sm font-medium text-gray-700">
              Nợ Cước (VND)
            </Label>
            <Input
              id="amount"
              type="number"
              value={formData.amount}
              onChange={(e) => handleInputChange("amount", e.target.value)}
              placeholder="Nhập số tiền nợ cước"
              className="mt-1"
              min="0"
              step="1000"
            />
          </div>

          {/* Chu kỳ thanh toán */}
          <div>
            <Label htmlFor="billing_cycle" className="text-sm font-medium text-gray-700">
              Chu Kỳ Thanh Toán
            </Label>
            <Input
              id="billing_cycle"
              type="text"
              value={formData.billing_cycle}
              onChange={(e) => handleInputChange("billing_cycle", e.target.value)}
              placeholder="MM/YYYY (VD: 09/2025)"
              className="mt-1"
              pattern="[0-9]{2}/[0-9]{4}"
            />
          </div>

          {/* Trạng thái */}
          <div>
            <Label htmlFor="status" className="text-sm font-medium text-gray-700">
              Trạng Thái
            </Label>
            <Select 
              value={formData.status} 
              onValueChange={(value) => handleInputChange("status", value)}
            >
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Chọn trạng thái" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="AVAILABLE">Có Sẵn</SelectItem>
                <SelectItem value="PENDING">Chờ Xử Lý</SelectItem>
                <SelectItem value="SOLD">Đã Bán</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
              disabled={loading}
            >
              Hủy
            </Button>
            <Button
              type="submit"
              className="flex-1 bg-blue-600 hover:bg-blue-700"
              disabled={loading}
            >
              {loading ? "Đang thêm..." : "Thêm Bill"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Import Modal Component
const ImportModal = ({ show, onClose, onImportComplete, onDownloadTemplate }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState([]);

  // Reset state when modal opens
  useEffect(() => {
    if (show) {
      setSelectedFile(null);
      setPreviewData(null);
      setErrors([]);
    }
  }, [show]);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewData(null);
      setErrors([]);
    }
  };

  const handlePreview = async () => {
    if (!selectedFile) {
      toast.error("Vui lòng chọn file Excel");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${API}/inventory/import/preview`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setPreviewData(response.data);
      setErrors(response.data.errors || []);
    } catch (error) {
      console.error("Error previewing import:", error);
      toast.error(error.response?.data?.detail || "Có lỗi xảy ra khi preview file");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmImport = async () => {
    if (!previewData) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API}/inventory/import/confirm`, {
        data: previewData.data
      });

      toast.success(response.data.message);
      onImportComplete();
    } catch (error) {
      console.error("Error confirming import:", error);
      toast.error(error.response?.data?.detail || "Có lỗi xảy ra khi import dữ liệu");
    } finally {
      setLoading(false);
    }
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Import Bills từ Excel</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="space-y-4">
          {/* Download Template */}
          <div className="border rounded-lg p-4 bg-blue-50">
            <h3 className="font-medium text-blue-900 mb-2">1. Tải Template Excel</h3>
            <p className="text-blue-700 text-sm mb-3">
              Tải file mẫu để đảm bảo định dạng dữ liệu chính xác
            </p>
            <Button
              variant="outline"
              onClick={onDownloadTemplate}
              className="border-blue-200 text-blue-700 hover:bg-blue-100"
            >
              <Download className="h-4 w-4 mr-2" />
              Tải Template
            </Button>
          </div>

          {/* File Upload */}
          <div className="border rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">2. Chọn File Excel</h3>
            <input
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileSelect}
              className="mb-3"
            />
            {selectedFile && (
              <p className="text-sm text-gray-600 mb-3">
                Đã chọn: {selectedFile.name}
              </p>
            )}
            <Button
              onClick={handlePreview}
              disabled={!selectedFile || loading}
              className="bg-green-600 hover:bg-green-700"
            >
              {loading ? "Đang xử lý..." : "Preview Dữ Liệu"}
            </Button>
          </div>

          {/* Preview Data */}
          {previewData && (
            <div className="border rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-2">3. Preview Dữ Liệu</h3>
              <div className="mb-3">
                <p className="text-sm text-gray-600">
                  Tổng cộng: {previewData.total_rows} bills
                  {previewData.has_more && " (hiển thị 50 đầu tiên)"}
                </p>
              </div>

              {/* Errors */}
              {errors.length > 0 && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
                  <h4 className="font-medium text-red-800 mb-2">Lỗi dữ liệu:</h4>
                  <ul className="text-sm text-red-700 space-y-1">
                    {errors.slice(0, 10).map((error, index) => (
                      <li key={index}>• {error}</li>
                    ))}
                    {errors.length > 10 && (
                      <li className="font-medium">... và {errors.length - 10} lỗi khác</li>
                    )}
                  </ul>
                </div>
              )}

              {/* Data Table */}
              <div className="overflow-x-auto">
                <table className="min-w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border border-gray-300 px-2 py-1 text-xs">Mã điện</th>
                      <th className="border border-gray-300 px-2 py-1 text-xs">Nhà cung cấp</th>
                      <th className="border border-gray-300 px-2 py-1 text-xs">Tên KH</th>
                      <th className="border border-gray-300 px-2 py-1 text-xs">Nợ cước</th>
                      <th className="border border-gray-300 px-2 py-1 text-xs">Chu kỳ</th>
                    </tr>
                  </thead>
                  <tbody>
                    {previewData.data.slice(0, 10).map((item, index) => (
                      <tr key={index}>
                        <td className="border border-gray-300 px-2 py-1 text-xs">{item.customer_code}</td>
                        <td className="border border-gray-300 px-2 py-1 text-xs">{item.provider_region}</td>
                        <td className="border border-gray-300 px-2 py-1 text-xs">{item.full_name}</td>
                        <td className="border border-gray-300 px-2 py-1 text-xs">{item.amount}</td>
                        <td className="border border-gray-300 px-2 py-1 text-xs">{item.billing_cycle}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="flex gap-3 mt-4">
                <Button
                  onClick={handleConfirmImport}
                  disabled={loading || errors.length > 0}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {loading ? "Đang import..." : `Import ${previewData.total_rows} Bills`}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setPreviewData(null)}
                >
                  Chọn File Khác
                </Button>
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end mt-6">
          <Button variant="outline" onClick={onClose}>
            Đóng
          </Button>
        </div>
      </div>
    </div>
  );
};

// Export Modal Component
const ExportModal = ({ show, onClose, onExport }) => {
  const [filters, setFilters] = useState({
    status: "ALL",
    provider_region: "ALL",
    start_date: "",
    end_date: ""
  });

  // Reset filters when modal opens
  useEffect(() => {
    if (show) {
      setFilters({
        status: "ALL",
        provider_region: "ALL",
        start_date: "",
        end_date: ""
      });
    }
  }, [show]);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleExport = () => {
    onExport(filters);
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Export Dữ Liệu</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="space-y-4">
          {/* Status Filter */}
          <div>
            <Label className="text-sm font-medium text-gray-700">Trạng Thái</Label>
            <Select 
              value={filters.status} 
              onValueChange={(value) => handleFilterChange("status", value)}
            >
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Tất cả trạng thái" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Tất cả trạng thái</SelectItem>
                <SelectItem value="AVAILABLE">Có Sẵn</SelectItem>
                <SelectItem value="PENDING">Chờ Xử Lý</SelectItem>
                <SelectItem value="SOLD">Đã Bán</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Provider Filter */}
          <div>
            <Label className="text-sm font-medium text-gray-700">Nhà Cung Cấp</Label>
            <Select 
              value={filters.provider_region} 
              onValueChange={(value) => handleFilterChange("provider_region", value)}
            >
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Tất cả nhà cung cấp" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Tất cả nhà cung cấp</SelectItem>
                <SelectItem value="MIEN_BAC">Miền Bắc</SelectItem>
                <SelectItem value="MIEN_NAM">Miền Nam</SelectItem>
                <SelectItem value="HCMC">TP. Hồ Chí Minh</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Date Range */}
          <div>
            <Label className="text-sm font-medium text-gray-700">Từ Ngày</Label>
            <Input
              type="date"
              value={filters.start_date}
              onChange={(e) => handleFilterChange("start_date", e.target.value)}
              className="mt-1"
            />
          </div>

          <div>
            <Label className="text-sm font-medium text-gray-700">Đến Ngày</Label>
            <Input
              type="date"
              value={filters.end_date}
              onChange={(e) => handleFilterChange("end_date", e.target.value)}
              className="mt-1"
            />
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <Button
            variant="outline"
            onClick={onClose}
            className="flex-1"
          >
            Hủy
          </Button>
          <Button
            onClick={handleExport}
            className="flex-1 bg-green-600 hover:bg-green-700"
          >
            <Download className="h-4 w-4 mr-2" />
            Export Excel
          </Button>
        </div>
      </div>
    </div>
  );
};

// Sales Export Modal Component
const SalesExportModal = ({ show, onClose, onExport }) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">Export Lịch Sử Bán Bill</h3>
        
        <div className="space-y-4">
          <div className="text-center py-6">
            <Download className="h-12 w-12 mx-auto text-green-600 mb-3" />
            <p className="text-gray-600 mb-4">
              Xuất toàn bộ lịch sử giao dịch bán bill ra file Excel
            </p>
            <p className="text-sm text-gray-500">
              File sẽ bao gồm: Mã điện, tên khách hàng, số tiền, lợi nhuận, ngày bán
            </p>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <Button
            variant="outline"
            onClick={onClose}
            className="flex-1"
          >
            Hủy
          </Button>
          <Button
            onClick={onExport}
            className="flex-1 bg-green-600 hover:bg-green-700"
          >
            <Download className="h-4 w-4 mr-2" />
            Export Excel
          </Button>
        </div>
      </div>
    </div>
  );
};



// Credit Cards Component
const CreditCards = () => {
  const [cards, setCards] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [cardStats, setCardStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedCard, setSelectedCard] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [showInfoModal, setShowInfoModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showDaoModal, setShowDaoModal] = useState(false);
  const [cardDetail, setCardDetail] = useState(null);

  useEffect(() => {
    fetchCreditCards();
    fetchCustomers();
    fetchCardStats();
  }, []);

  const fetchCreditCards = async () => {
    try {
      const response = await axios.get(`${API}/credit-cards?page_size=100`);
      setCards(response.data);
    } catch (error) {
      console.error("Error fetching credit cards:", error);
      toast.error("Không thể tải dữ liệu thẻ tín dụng");
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers?page_size=100`);
      setCustomers(response.data);
    } catch (error) {
      console.error("Error fetching customers:", error);
    }
  };

  const fetchCardStats = async () => {
    try {
      const response = await axios.get(`${API}/credit-cards/stats`);
      setCardStats(response.data);
    } catch (error) {
      console.error("Error fetching card stats:", error);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount);
  };

  const maskCardNumber = (cardNumber) => {
    if (!cardNumber) return "";
    const lastFour = cardNumber.slice(-4);
    return `**** **** **** ${lastFour}`;
  };

  const getCardTypeIcon = (cardType) => {
    switch (cardType) {
      case "VISA":
        return "💳";
      case "MASTERCARD":
        return "💳";
      case "JCB":
        return "💳";
      case "AMEX":
        return "💳";
      default:
        return "💳";
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "Đã đáo":
        return "bg-green-100 text-green-800";
      case "Cần đáo":
        return "bg-red-100 text-red-800";
      case "Chưa đến hạn":
        return "bg-yellow-100 text-yellow-800";
      case "Quá Hạn":
        return "bg-red-500 text-white font-bold animate-pulse"; // Red alert for overdue
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const handleViewCard = async (card) => {
    console.log("handleViewCard called with card:", card);
    try {
      console.log("Making API call to:", `${API}/credit-cards/${card.id}/detail`);
      const response = await axios.get(`${API}/credit-cards/${card.id}/detail`);
      console.log("API response:", response.data);
      setCardDetail(response.data);
      setSelectedCard(card);
      setShowInfoModal(true);
      console.log("Modal should open now");
    } catch (error) {
      console.error("Error getting card detail:", error);
      toast.error("Không thể tải thông tin chi tiết thẻ");
    }
  };

  const handleEditCard = (card) => {
    setSelectedCard(card);
    setShowEditModal(true);
  };

  const handleDeleteCard = (card) => {
    setSelectedCard(card);
    setShowDeleteModal(true);
  };

  const handleDaoCard = (card) => {
    setSelectedCard(card);
    setShowDaoModal(true);
  };

  const filteredCards = cards.filter(card => 
    card.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    card.cardholder_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    card.bank_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    card.card_number?.includes(searchTerm)
  );

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Đang tải dữ liệu thẻ...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Quản Lý Thẻ Tín Dụng</h1>
          <p className="text-gray-600 mt-1">Quản lý thẻ tín dụng và theo dõi thanh toán</p>
        </div>
        <Button 
          onClick={() => setShowAddModal(true)} 
          className="bg-green-600 hover:bg-green-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Thêm Thẻ Mới
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <CreditCard className="h-4 w-4 mr-2" />
              Tổng Thẻ
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{cardStats.total_cards || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Tất cả thẻ trong hệ thống</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <CheckCircle className="h-4 w-4 mr-2" />
              Đã Đáo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{cardStats.paid_off_cards || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Thẻ đã thanh toán</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-red-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Cần Đáo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{cardStats.need_payment_cards || 0}</div>
            <p className="text-xs text-gray-500 mt-1">Thẻ cần thanh toán</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
              <DollarSign className="h-4 w-4 mr-2" />
              Tổng Hạn Mức
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{formatCurrency(cardStats.total_credit_limit || 0)}</div>
            <p className="text-xs text-gray-500 mt-1">Tổng hạn mức tín dụng</p>
          </CardContent>
        </Card>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Tìm kiếm theo tên khách hàng, chủ thẻ, ngân hàng..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Visual Credit Cards Gallery */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Thẻ Tín Dụng</h2>
        {filteredCards.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredCards.slice(0, 8).map((card) => (
              <div key={card.id} className="relative">
                {/* Credit Card Visual */}
                <div className="bg-gradient-to-br from-green-400 to-green-600 rounded-xl p-6 text-white shadow-xl hover:shadow-2xl transition-all duration-300 cursor-pointer transform hover:scale-105"
                     onClick={() => setSelectedCard(card)}>
                  
                  {/* Card Type Icon */}
                  <div className="flex justify-between items-start mb-8">
                    <div className="text-2xl">{getCardTypeIcon(card.card_type)}</div>
                    <div className="text-right">
                      <p className="text-xs opacity-80">{card.bank_name}</p>
                      <p className="text-xs opacity-60">{card.card_type}</p>
                    </div>
                  </div>
                  
                  {/* Card Number */}
                  <div className="mb-6">
                    <p className="text-lg font-mono tracking-wider">
                      {maskCardNumber(card.card_number)}
                    </p>
                  </div>
                  
                  {/* Card Info */}
                  <div className="flex justify-between items-end">
                    <div>
                      <p className="text-xs opacity-60 mb-1">CARDHOLDER NAME</p>
                      <p className="font-semibold text-sm uppercase tracking-wide">
                        {card.cardholder_name}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs opacity-60 mb-1">VALID THRU</p>
                      <p className="font-mono text-sm">{card.expiry_date}</p>
                    </div>
                  </div>
                  
                  {/* Status Badge */}
                  <div className="absolute top-4 left-4">
                    <Badge className={`${getStatusColor(card.status)} border-0`}>
                      {card.status}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <CreditCard className="h-16 w-16 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Chưa có thẻ nào</h3>
            <p className="text-gray-500 mb-4">Bắt đầu bằng cách thêm thẻ tín dụng đầu tiên</p>
            <Button onClick={() => setShowAddModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Thêm Thẻ Đầu Tiên
            </Button>
          </div>
        )}
      </div>

      {/* Credit Cards Table */}
      <Card>
        <CardHeader>
          <CardTitle>Danh Sách Chi Tiết</CardTitle>
        </CardHeader>
        <CardContent>
          {filteredCards.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Khách Hàng</TableHead>
                  <TableHead>Chủ Thẻ</TableHead>
                  <TableHead>Số Thẻ</TableHead>
                  <TableHead>Ngân Hàng</TableHead>
                  <TableHead>Loại Thẻ</TableHead>
                  <TableHead>Hạn Mức</TableHead>
                  <TableHead>Ngày SK</TableHead>
                  <TableHead>Hạn TT</TableHead>
                  <TableHead>Trạng Thái</TableHead>
                  <TableHead>Thao Tác</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCards.map((card) => (
                  <TableRow key={card.id}>
                    <TableCell className="font-medium">{card.customer_name}</TableCell>
                    <TableCell>{card.cardholder_name}</TableCell>
                    <TableCell className="font-mono">{maskCardNumber(card.card_number)}</TableCell>
                    <TableCell>{card.bank_name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{card.card_type}</Badge>
                    </TableCell>
                    <TableCell>{formatCurrency(card.credit_limit)}</TableCell>
                    <TableCell>{card.statement_date}</TableCell>
                    <TableCell>{card.payment_due_date}</TableCell>
                    <TableCell>
                      <Badge className={`${getStatusColor(card.status)} border-0`}>
                        {card.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Button size="sm" variant="outline" onClick={() => handleViewCard(card)}>
                          Xem
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => handleEditCard(card)}>
                          Sửa
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => handleDeleteCard(card)} className="text-red-600">
                          Xóa
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8 text-gray-500">
              Không tìm thấy thẻ nào
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Card Modal */}
      <AddCreditCardModal 
        show={showAddModal}
        customers={customers}
        onClose={() => setShowAddModal(false)}
        onSuccess={() => {
          setShowAddModal(false);
          fetchCreditCards();
          fetchCardStats();
        }}
      />

      {/* Info Card Modal */}
      <CreditCardInfoModal 
        show={showInfoModal}
        cardDetail={cardDetail}
        onClose={() => {
          setShowInfoModal(false);
          setCardDetail(null);
          setSelectedCard(null);
        }}
        onDao={() => {
          setShowInfoModal(false);
          setShowDaoModal(true);
        }}
        onEdit={() => {
          setShowInfoModal(false);
          setShowEditModal(true);
        }}
        onDelete={() => {
          setShowInfoModal(false);
          setShowDeleteModal(true);
        }}
      />

      {/* Đáo Card Modal */}
      <DaoCardModal 
        show={showDaoModal}
        card={selectedCard}
        onClose={() => {
          setShowDaoModal(false);
          setSelectedCard(null);
        }}
        onSuccess={() => {
          setShowDaoModal(false);
          setSelectedCard(null);
          fetchCreditCards();
          fetchCardStats();
        }}
      />

      {/* Edit Card Modal */}
      <EditCreditCardModal 
        show={showEditModal}
        card={selectedCard}
        onClose={() => {
          setShowEditModal(false);
          setSelectedCard(null);
        }}
        onSuccess={() => {
          setShowEditModal(false);
          setSelectedCard(null);
          fetchCreditCards();
        }}
      />

      {/* Delete Card Modal */}
      <DeleteCreditCardModal 
        show={showDeleteModal}
        card={selectedCard}
        onClose={() => {
          setShowDeleteModal(false);
          setSelectedCard(null);
        }}
        onSuccess={() => {
          setShowDeleteModal(false);
          setSelectedCard(null);
          fetchCreditCards();
          fetchCardStats();
        }}
      />
    </div>
  );
};

// Add Credit Card Modal Component
const AddCreditCardModal = ({ show, customers, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    customer_id: "",
    card_number: "",
    cardholder_name: "",
    bank_name: "",
    card_type: "VISA",
    expiry_date: "",
    ccv: "",
    statement_date: 1,
    payment_due_date: 15,
    credit_limit: "",
    status: "Chưa đến hạn",
    notes: ""
  });

  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Validate required fields
      if (!formData.customer_id || !formData.card_number || !formData.cardholder_name) {
        toast.error("Vui lòng điền đầy đủ thông tin bắt buộc");
        return;
      }

      // Format data for API
      const apiData = {
        customer_id: formData.customer_id,
        card_number: formData.card_number.replace(/\s/g, ''), // Remove spaces
        cardholder_name: formData.cardholder_name,
        bank_name: formData.bank_name,
        card_type: formData.card_type,
        expiry_date: formData.expiry_date,
        ccv: formData.ccv,
        statement_date: parseInt(formData.statement_date),
        payment_due_date: parseInt(formData.payment_due_date),
        credit_limit: parseFloat(formData.credit_limit) || 0,
        status: formData.status,
        notes: formData.notes || null
      };

      await axios.post(`${API}/credit-cards`, apiData);
      toast.success("Đã thêm thẻ mới thành công!");
      onSuccess();
      
      // Reset form
      setFormData({
        customer_id: "",
        card_number: "",
        cardholder_name: "",
        bank_name: "",
        card_type: "VISA",
        expiry_date: "",
        ccv: "",
        statement_date: 1,
        payment_due_date: 15,
        credit_limit: "",
        status: "Chưa đến hạn",
        notes: ""
      });

    } catch (error) {
      console.error("Error adding credit card:", error);
      toast.error(error.response?.data?.detail || "Có lỗi xảy ra khi thêm thẻ");
    } finally {
      setLoading(false);
    }
  };

  const formatCardNumber = (value) => {
    // Remove all non-digits
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    // Add spaces every 4 digits
    const matches = v.match(/\d{4,16}/g);
    const match = matches && matches[0] || '';
    const parts = [];
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4));
    }
    if (parts.length) {
      return parts.join(' ');
    } else {
      return v;
    }
  };

  const handleCardNumberChange = (e) => {
    const formatted = formatCardNumber(e.target.value);
    setFormData({ ...formData, card_number: formatted });
  };

  const maskCardNumberForPreview = (cardNumber) => {
    if (!cardNumber) return "**** **** **** ****";
    const digits = cardNumber.replace(/\s/g, '');
    if (digits.length <= 4) {
      return cardNumber.padEnd(19, '*').replace(/(.{4})/g, '$1 ').trim();
    }
    const lastFour = digits.slice(-4);
    const masked = '**** **** **** ' + lastFour;
    return masked;
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold">Thêm Thẻ Tín Dụng Mới</h3>
          <Button variant="outline" onClick={onClose}>
            <XCircle className="h-4 w-4" />
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Live Card Preview */}
          <div>
            <h4 className="font-medium text-gray-900 mb-4">Xem Trước Thẻ</h4>
            <div className="bg-gradient-to-br from-green-400 to-green-600 rounded-xl p-6 text-white shadow-xl max-w-sm">
              
              {/* Card Type Icon */}
              <div className="flex justify-between items-start mb-8">
                <div className="text-2xl">💳</div>
                <div className="text-right">
                  <p className="text-xs opacity-80">{formData.bank_name || "BANK NAME"}</p>
                  <p className="text-xs opacity-60">{formData.card_type}</p>
                </div>
              </div>
              
              {/* Card Number */}
              <div className="mb-6">
                <p className="text-lg font-mono tracking-wider">
                  {maskCardNumberForPreview(formData.card_number)}
                </p>
              </div>
              
              {/* Card Info */}
              <div className="flex justify-between items-end">
                <div>
                  <p className="text-xs opacity-60 mb-1">CARDHOLDER NAME</p>
                  <p className="font-semibold text-sm uppercase tracking-wide">
                    {formData.cardholder_name || "CARDHOLDER NAME"}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs opacity-60 mb-1">VALID THRU</p>
                  <p className="font-mono text-sm">{formData.expiry_date || "MM/YY"}</p>
                </div>
              </div>
              
              {/* Status Badge */}
              <div className="absolute top-4 left-4">
                <Badge className="bg-white/20 text-white border-white/30">
                  {formData.status}
                </Badge>
              </div>
            </div>
          </div>

          {/* Form */}
          <div>
            <form onSubmit={handleSubmit} className="space-y-4">
              
              {/* Customer Selection */}
              <div>
                <Label htmlFor="customer_id">Khách Hàng *</Label>
                <Select 
                  value={formData.customer_id} 
                  onValueChange={(value) => setFormData({ ...formData, customer_id: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Chọn khách hàng" />
                  </SelectTrigger>
                  <SelectContent>
                    {customers.map((customer) => (
                      <SelectItem key={customer.id} value={customer.id}>
                        {customer.name} - {customer.phone || "N/A"}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Card Number */}
              <div>
                <Label htmlFor="card_number">Số Thẻ *</Label>
                <Input
                  id="card_number"
                  value={formData.card_number}
                  onChange={handleCardNumberChange}
                  placeholder="1234 5678 9012 3456"
                  maxLength={19}
                  required
                />
              </div>

              {/* Cardholder Name */}
              <div>
                <Label htmlFor="cardholder_name">Tên Chủ Thẻ *</Label>
                <Input
                  id="cardholder_name"
                  value={formData.cardholder_name}
                  onChange={(e) => setFormData({ ...formData, cardholder_name: e.target.value })}
                  placeholder="NGUYEN VAN A"
                  required
                />
              </div>

              {/* Bank and Card Type */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="bank_name">Ngân Hàng</Label>
                  <Input
                    id="bank_name"
                    value={formData.bank_name}
                    onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                    placeholder="Vietcombank"
                  />
                </div>
                <div>
                  <Label htmlFor="card_type">Loại Thẻ</Label>
                  <Select 
                    value={formData.card_type}
                    onValueChange={(value) => setFormData({ ...formData, card_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="VISA">VISA</SelectItem>
                      <SelectItem value="MASTERCARD">MASTERCARD</SelectItem>
                      <SelectItem value="JCB">JCB</SelectItem>
                      <SelectItem value="AMEX">AMEX</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Expiry and CCV */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="expiry_date">Ngày Hết Hạn (MM/YY)</Label>
                  <Input
                    id="expiry_date"
                    value={formData.expiry_date}
                    onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                    placeholder="12/25"
                    maxLength={5}
                  />
                </div>
                <div>
                  <Label htmlFor="ccv">CCV</Label>
                  <Input
                    id="ccv"
                    value={formData.ccv}
                    onChange={(e) => setFormData({ ...formData, ccv: e.target.value })}
                    placeholder="123"
                    maxLength={4}
                  />
                </div>
              </div>

              {/* Statement and Payment Dates */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="statement_date">Ngày Sao Kê</Label>
                  <Input
                    id="statement_date"
                    type="number"
                    min="1"
                    max="31"
                    value={formData.statement_date}
                    onChange={(e) => setFormData({ ...formData, statement_date: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="payment_due_date">Hạn Thanh Toán</Label>
                  <Input
                    id="payment_due_date"
                    type="number"
                    min="1"
                    max="31"
                    value={formData.payment_due_date}
                    onChange={(e) => setFormData({ ...formData, payment_due_date: e.target.value })}
                  />
                </div>
              </div>

              {/* Credit Limit and Status */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="credit_limit">Hạn Mức (VND)</Label>
                  <Input
                    id="credit_limit"
                    type="number"
                    value={formData.credit_limit}
                    onChange={(e) => setFormData({ ...formData, credit_limit: e.target.value })}
                    placeholder="50000000"
                  />
                </div>
                <div>
                  <Label htmlFor="status">Trạng Thái</Label>
                  <Select 
                    value={formData.status}
                    onValueChange={(value) => setFormData({ ...formData, status: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Chưa đến hạn">Chưa đến hạn</SelectItem>
                      <SelectItem value="Cần đáo">Cần đáo</SelectItem>
                      <SelectItem value="Đã đáo">Đã đáo</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Notes */}
              <div>
                <Label htmlFor="notes">Ghi Chú</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Ghi chú thêm về thẻ..."
                  rows={3}
                />
              </div>

              {/* Submit Buttons */}
              <div className="flex gap-3 pt-4">
                <Button type="button" variant="outline" onClick={onClose} className="flex-1">
                  Hủy
                </Button>
                <Button type="submit" disabled={loading} className="flex-1 bg-green-600 hover:bg-green-700">
                  {loading ? "Đang thêm..." : "Thêm Thẻ"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

// Credit Card Info Modal Component
const CreditCardInfoModal = ({ show, cardDetail, onClose, onDao, onEdit, onDelete }) => {
  if (!show || !cardDetail) return null;

  const { card, customer, recent_transactions, total_transactions } = cardDetail;

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "Đã đáo":
        return "bg-green-100 text-green-800";
      case "Cần đáo":
        return "bg-red-100 text-red-800";
      case "Chưa đến hạn":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[95vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold">Chi Tiết Thẻ Tín Dụng</h3>
          <Button variant="outline" onClick={onClose}>
            <XCircle className="h-4 w-4" />
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Side - Card Visual & Info */}
          <div>
            {/* Visual Credit Card */}
            <div className="bg-gradient-to-br from-green-400 to-green-600 rounded-xl p-6 text-white shadow-xl mb-6">
              
              {/* Card Type Icon */}
              <div className="flex justify-between items-start mb-8">
                <div className="text-2xl">💳</div>
                <div className="text-right">
                  <p className="text-xs opacity-80">{card.bank_name}</p>
                  <p className="text-xs opacity-60">{card.card_type}</p>
                </div>
              </div>
              
              {/* Card Number - FULL NUMBER SHOWN */}
              <div className="mb-6">
                <p className="text-lg font-mono tracking-wider">
                  {card.card_number?.replace(/(.{4})/g, '$1 ').trim()}
                </p>
              </div>
              
              {/* Card Info */}
              <div className="flex justify-between items-end">
                <div>
                  <p className="text-xs opacity-60 mb-1">CARDHOLDER NAME</p>
                  <p className="font-semibold text-sm uppercase tracking-wide">
                    {card.cardholder_name}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs opacity-60 mb-1">VALID THRU</p>
                  <p className="font-mono text-sm">{card.expiry_date}</p>
                </div>
              </div>
              
              {/* Status Badge */}
              <div className="absolute top-4 left-4">
                <Badge className={`${getStatusColor(card.status)} border-0`}>
                  {card.status}
                </Badge>
              </div>
            </div>

            {/* Customer Info */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="text-sm">Thông Tin Khách Hàng</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Tên:</span>
                    <span className="font-medium">{customer.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Số ĐT:</span>
                    <span className="font-medium">{customer.phone || "N/A"}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="grid grid-cols-3 gap-3">
              <Button 
                onClick={onDao} 
                className="bg-green-600 hover:bg-green-700"
                disabled={card.status === "Đã đáo"}
              >
                Đáo
              </Button>
              <Button onClick={onEdit} variant="outline">
                Sửa
              </Button>
              <Button onClick={onDelete} variant="outline" className="text-red-600 hover:text-red-700">
                Xóa
              </Button>
            </div>
          </div>

          {/* Right Side - Card Details & Transactions */}
          <div>
            {/* Card Details */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="text-sm">Chi Tiết Thẻ</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Hạn Mức:</span>
                    <div className="font-medium">{formatCurrency(card.credit_limit)}</div>
                  </div>
                  <div>
                    <span className="text-gray-600">CCV:</span>
                    <div className="font-mono">{card.ccv}</div>
                  </div>
                  <div>
                    <span className="text-gray-600">Ngày Sao Kê:</span>
                    <div className="font-medium">{card.statement_date}</div>
                  </div>
                  <div>
                    <span className="text-gray-600">Hạn Thanh Toán:</span>
                    <div className="font-medium">{card.payment_due_date}</div>
                  </div>
                </div>
                {card.notes && (
                  <div className="mt-4 pt-4 border-t">
                    <span className="text-gray-600 text-sm">Ghi Chú:</span>
                    <p className="text-sm mt-1">{card.notes}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Transactions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Giao Dịch Gần Đây ({total_transactions} tổng)</CardTitle>
              </CardHeader>
              <CardContent>
                {recent_transactions && recent_transactions.length > 0 ? (
                  <div className="space-y-3">
                    {recent_transactions.map((transaction, index) => (
                      <div key={transaction.id} className="border rounded-lg p-3 bg-gray-50">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <span className="text-xs text-gray-500">
                              {new Date(transaction.created_at).toLocaleDateString('vi-VN')}
                            </span>
                            <p className="font-medium text-sm">
                              {transaction.payment_method} - {formatCurrency(transaction.total_amount)}
                            </p>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {transaction.profit_pct}% lợi nhuận
                          </Badge>
                        </div>
                        {transaction.notes && (
                          <p className="text-xs text-gray-600">{transaction.notes}</p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6 text-gray-500">
                    <CreditCard className="h-8 w-8 mx-auto mb-2" />
                    <p className="text-sm">Chưa có giao dịch nào</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

// Dao Card Modal Component
const DaoCardModal = ({ show, card, onClose, onSuccess }) => {
  const [activeTab, setActiveTab] = useState("POS");
  const [loading, setLoading] = useState(false);
  
  // POS method states
  const [posAmount, setPosAmount] = useState("");
  const [profitPct, setProfitPct] = useState("");
  const [notes, setNotes] = useState("");
  
  // BILL method states
  const [availableBills, setAvailableBills] = useState([]);
  const [selectedBills, setSelectedBills] = useState([]);
  const [billsLoading, setBillsLoading] = useState(false);

  useEffect(() => {
    if (show && activeTab === "BILL") {
      fetchAvailableBills();
    }
  }, [show, activeTab]);

  const fetchAvailableBills = async () => {
    setBillsLoading(true);
    try {
      const response = await axios.get(`${API}/bills?status=AVAILABLE&limit=100`);
      setAvailableBills(response.data || []);
    } catch (error) {
      console.error("Error fetching available bills:", error);
      toast.error("Không thể tải danh sách bill");
    } finally {
      setBillsLoading(false);
    }
  };

  const handleBillSelection = (bill, isSelected) => {
    if (isSelected) {
      setSelectedBills(prev => [...prev, bill]);
    } else {
      setSelectedBills(prev => prev.filter(b => b.id !== bill.id));
    }
  };

  const calculateTotals = () => {
    if (activeTab === "POS") {
      const amount = parseFloat(posAmount) || 0;
      const profit = parseFloat(profitPct) || 0;
      const profitValue = Math.round(amount * profit / 100);
      const payback = amount - profitValue;
      return { total: amount, profitValue, payback };
    } else {
      const total = selectedBills.reduce((sum, bill) => sum + (bill.amount || 0), 0);
      const profit = parseFloat(profitPct) || 0;
      const profitValue = Math.round(total * profit / 100);
      const payback = total - profitValue;
      return { total, profitValue, payback };
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!profitPct) {
      toast.error("Vui lòng nhập % lợi nhuận");
      return;
    }

    if (activeTab === "POS" && !posAmount) {
      toast.error("Vui lòng nhập số tiền đáo");
      return;
    }

    if (activeTab === "BILL" && selectedBills.length === 0) {
      toast.error("Vui lòng chọn ít nhất một bill điện");
      return;
    }

    setLoading(true);
    
    try {
      const paymentData = {
        payment_method: activeTab,
        profit_pct: parseFloat(profitPct),
        notes: notes || undefined
      };

      if (activeTab === "POS") {
        paymentData.total_amount = parseFloat(posAmount);
      } else {
        paymentData.bill_ids = selectedBills.map(bill => bill.id);
      }

      const response = await axios.post(`${API}/credit-cards/${card.id}/dao`, paymentData);
      
      toast.success(response.data.message || "Đáo thẻ thành công!");
      
      // Reset form
      setPosAmount("");
      setProfitPct("");
      setNotes("");
      setSelectedBills([]);
      
      onSuccess();
      
    } catch (error) {
      console.error("Error processing dao:", error);
      
      // Handle different error response formats
      let errorMessage = "Có lỗi xảy ra khi đáo thẻ";
      
      if (error.response?.data) {
        const { detail } = error.response.data;
        
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          // If detail is array of validation errors
          errorMessage = detail.map(err => err.msg || err.message || 'Validation error').join(', ');
        } else if (detail && typeof detail === 'object') {
          // If detail is object with validation info
          errorMessage = detail.msg || detail.message || 'Validation error';
        }
      }
      
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount);
  };

  const { total, profitValue, payback } = calculateTotals();

  if (!show || !card) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[95vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-xl font-semibold">Đáo Thẻ Tín Dụng</h3>
            <p className="text-gray-600 text-sm">****{card.card_number?.slice(-4)} - {card.cardholder_name}</p>
          </div>
          <Button variant="outline" onClick={onClose}>
            <XCircle className="h-4 w-4" />
          </Button>
        </div>

        {/* Tab Navigation */}
        <div className="flex mb-6 border-b">
          <button
            className={`px-6 py-3 font-medium border-b-2 transition-colors ${
              activeTab === "POS" 
                ? "border-green-500 text-green-600 bg-green-50" 
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
            onClick={() => setActiveTab("POS")}
          >
            💳 Thanh Toán POS
          </button>
          <button
            className={`px-6 py-3 font-medium border-b-2 transition-colors ${
              activeTab === "BILL" 
                ? "border-green-500 text-green-600 bg-green-50" 
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
            onClick={() => setActiveTab("BILL")}
          >
            ⚡ Thanh Toán Bill Điện
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Side - Payment Method */}
            <div className="lg:col-span-2">
              {activeTab === "POS" ? (
                // POS Method
                <Card>
                  <CardHeader>
                    <CardTitle className="text-green-600">💳 Thanh Toán POS</CardTitle>
                    <p className="text-sm text-gray-600">Nhập số tiền và % lợi nhuận để đáo thẻ qua POS</p>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="posAmount">Số Tiền Đáo (VND) *</Label>
                      <Input
                        id="posAmount"
                        type="number"
                        value={posAmount}
                        onChange={(e) => setPosAmount(e.target.value)}
                        placeholder="5000000"
                        className="text-lg"
                      />
                    </div>
                    <div>
                      <Label htmlFor="profitPct">% Lợi Nhuận *</Label>
                      <Input
                        id="profitPct"
                        type="number"
                        step="0.1"
                        value={profitPct}
                        onChange={(e) => setProfitPct(e.target.value)}
                        placeholder="3.5"
                        className="text-lg"
                      />
                    </div>
                    <div>
                      <Label htmlFor="notes">Ghi Chú</Label>
                      <Textarea
                        id="notes"
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        placeholder="Ghi chú thêm về giao dịch..."
                        rows={3}
                      />
                    </div>
                  </CardContent>
                </Card>
              ) : (
                // BILL Method
                <Card>
                  <CardHeader>
                    <CardTitle className="text-green-600">⚡ Thanh Toán Bill Điện</CardTitle>
                    <p className="text-sm text-gray-600">Chọn nhiều bill điện có sẵn trong kho để đáo thẻ</p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="profitPctBill">% Lợi Nhuận *</Label>
                        <Input
                          id="profitPctBill"
                          type="number"
                          step="0.1"
                          value={profitPct}
                          onChange={(e) => setProfitPct(e.target.value)}
                          placeholder="3.5"
                          className="text-lg"
                        />
                      </div>

                      {/* Bill Selection */}
                      <div>
                        <Label>Chọn Bill Điện ({selectedBills.length} đã chọn)</Label>
                        <div className="border rounded-lg max-h-60 overflow-y-auto mt-2">
                          {billsLoading ? (
                            <div className="p-4 text-center">
                              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600 mx-auto"></div>
                              <p className="text-sm text-gray-600 mt-2">Đang tải bill...</p>
                            </div>
                          ) : availableBills.length > 0 ? (
                            <div className="p-2 space-y-1">
                              {availableBills.map((bill) => {
                                const isSelected = selectedBills.some(b => b.id === bill.id);
                                return (
                                  <div
                                    key={bill.id}
                                    className={`p-3 border rounded cursor-pointer transition-colors ${
                                      isSelected 
                                        ? "bg-green-50 border-green-300" 
                                        : "bg-white border-gray-200 hover:bg-gray-50"
                                    }`}
                                    onClick={() => handleBillSelection(bill, !isSelected)}
                                  >
                                    <div className="flex justify-between items-center">
                                      <div>
                                        <p className="font-medium text-sm">{bill.customer_code}</p>
                                        <p className="text-xs text-gray-600">{bill.full_name}</p>
                                      </div>
                                      <div className="text-right">
                                        <p className="font-medium text-green-600">{formatCurrency(bill.amount || 0)}</p>
                                        <div className="flex items-center">
                                          {isSelected && <CheckCircle className="h-4 w-4 text-green-600 mr-1" />}
                                          <span className="text-xs text-gray-500">{bill.billing_cycle}</span>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          ) : (
                            <div className="p-4 text-center text-gray-500">
                              <Package className="h-8 w-8 mx-auto mb-2" />
                              <p className="text-sm">Không có bill điện khả dụng</p>
                            </div>
                          )}
                        </div>
                      </div>

                      <div>
                        <Label htmlFor="notesBill">Ghi Chú</Label>
                        <Textarea
                          id="notesBill"
                          value={notes}
                          onChange={(e) => setNotes(e.target.value)}
                          placeholder="Ghi chú thêm về giao dịch..."
                          rows={2}
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Right Side - Summary */}
            <div>
              <Card className="sticky top-4">
                <CardHeader>
                  <CardTitle className="text-sm">Tóm Tắt Giao Dịch</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {activeTab === "BILL" && (
                    <div className="pb-3 border-b">
                      <p className="text-xs text-gray-600 mb-2">Bills đã chọn:</p>
                      <p className="text-sm font-medium">{selectedBills.length} bill(s)</p>
                    </div>
                  )}
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Tổng tiền:</span>
                      <span className="font-medium">{formatCurrency(total)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Lợi nhuận ({profitPct || 0}%):</span>
                      <span className="font-medium text-green-600">+{formatCurrency(profitValue)}</span>
                    </div>
                    <div className="flex justify-between border-t pt-2">
                      <span className="text-gray-900 font-medium">Trả khách:</span>
                      <span className="font-bold text-blue-600">{formatCurrency(payback)}</span>
                    </div>
                  </div>

                  <div className="pt-4 space-y-3">
                    <Button
                      type="submit"
                      disabled={loading || (activeTab === "POS" && (!posAmount || !profitPct)) || (activeTab === "BILL" && (selectedBills.length === 0 || !profitPct))}
                      className="w-full bg-green-600 hover:bg-green-700"
                    >
                      {loading ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Đang xử lý...
                        </>
                      ) : (
                        `Xác Nhận Đáo ${formatCurrency(total)}`
                      )}
                    </Button>
                    
                    <Button type="button" variant="outline" onClick={onClose} className="w-full">
                      Hủy Bỏ
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

// Edit Credit Card Modal Component
const EditCreditCardModal = ({ show, card, customers, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    customer_id: "",
    card_number: "",
    cardholder_name: "",
    bank_name: "",
    card_type: "VISA",
    expiry_date: "",
    ccv: "",
    statement_date: "",
    payment_due_date: "",
    credit_limit: "",
    status: "Chưa đến hạn",
    notes: ""
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (card) {
      setFormData({
        customer_id: card.customer_id || "",
        card_number: card.card_number || "",
        cardholder_name: card.cardholder_name || "",
        bank_name: card.bank_name || "",
        card_type: card.card_type || "VISA",
        expiry_date: card.expiry_date || "",
        ccv: card.ccv || "",
        statement_date: card.statement_date || "",
        payment_due_date: card.payment_due_date || "",
        credit_limit: card.credit_limit || "",
        status: card.status || "Chưa đến hạn",
        notes: card.notes || ""
      });
    }
  }, [card]);

  if (!show) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit(formData);
      onClose();
    } catch (error) {
      console.error("Error updating card:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[95vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Chỉnh Sửa Thẻ Tín Dụng</h3>
          <Button variant="outline" onClick={onClose}>
            <XCircle className="h-4 w-4" />
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="customer_id">Khách Hàng</Label>
              <Select value={formData.customer_id} onValueChange={(value) => handleChange("customer_id", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Chọn khách hàng" />
                </SelectTrigger>
                <SelectContent>
                  {customers?.map((customer) => (
                    <SelectItem key={customer.id} value={customer.id}>
                      {customer.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="card_number">Số Thẻ</Label>
              <Input
                id="card_number"
                value={formData.card_number}
                onChange={(e) => handleChange("card_number", e.target.value)}
                placeholder="1234 5678 9012 3456"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="cardholder_name">Tên Chủ Thẻ</Label>
              <Input
                id="cardholder_name"
                value={formData.cardholder_name}
                onChange={(e) => handleChange("cardholder_name", e.target.value)}
                placeholder="NGUYEN VAN A"
                required
              />
            </div>

            <div>
              <Label htmlFor="bank_name">Ngân Hàng</Label>
              <Input
                id="bank_name"
                value={formData.bank_name}
                onChange={(e) => handleChange("bank_name", e.target.value)}
                placeholder="Vietcombank"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <Label htmlFor="card_type">Loại Thẻ</Label>
              <Select value={formData.card_type} onValueChange={(value) => handleChange("card_type", value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="VISA">VISA</SelectItem>
                  <SelectItem value="MASTERCARD">MASTERCARD</SelectItem>
                  <SelectItem value="JCB">JCB</SelectItem>
                  <SelectItem value="AMEX">AMEX</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="expiry_date">Ngày Hết Hạn</Label>
              <Input
                id="expiry_date"
                value={formData.expiry_date}
                onChange={(e) => handleChange("expiry_date", e.target.value)}
                placeholder="MM/YY"
                required
              />
            </div>

            <div>
              <Label htmlFor="ccv">CCV</Label>
              <Input
                id="ccv"
                value={formData.ccv}
                onChange={(e) => handleChange("ccv", e.target.value)}
                placeholder="123"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="statement_date">Ngày Sao Kê</Label>
              <Input
                id="statement_date"
                value={formData.statement_date}
                onChange={(e) => handleChange("statement_date", e.target.value)}
                placeholder="15"
              />
            </div>

            <div>
              <Label htmlFor="payment_due_date">Hạn Thanh Toán</Label>
              <Input
                id="payment_due_date"
                value={formData.payment_due_date}
                onChange={(e) => handleChange("payment_due_date", e.target.value)}
                placeholder="05"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="credit_limit">Hạn Mức</Label>
              <Input
                id="credit_limit"
                type="number"
                value={formData.credit_limit}
                onChange={(e) => handleChange("credit_limit", e.target.value)}
                placeholder="50000000"
                required
              />
            </div>

            <div>
              <Label htmlFor="status">Trạng Thái</Label>
              <Select value={formData.status} onValueChange={(value) => handleChange("status", value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Đã đáo">Đã đáo</SelectItem>
                  <SelectItem value="Cần đáo">Cần đáo</SelectItem>
                  <SelectItem value="Chưa đến hạn">Chưa đến hạn</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div>
            <Label htmlFor="notes">Ghi Chú</Label>
            <Textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => handleChange("notes", e.target.value)}
              placeholder="Ghi chú thêm..."
              rows={3}
            />
          </div>

          <div className="flex gap-3">
            <Button type="button" variant="outline" onClick={onClose} className="flex-1">
              Hủy
            </Button>
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? "Đang cập nhật..." : "Cập Nhật"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Delete Credit Card Modal Component
const DeleteCreditCardModal = ({ show, card, onClose, onConfirm }) => {
  const [loading, setLoading] = useState(false);

  if (!show || !card) return null;

  const handleDelete = async () => {
    setLoading(true);
    try {
      await onConfirm();
      onClose();
    } catch (error) {
      console.error("Error deleting card:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex items-center mb-4">
          <AlertTriangle className="h-6 w-6 text-red-600 mr-3" />
          <h2 className="text-xl font-semibold text-gray-900">Xác Nhận Xóa Thẻ</h2>
        </div>
        
        <div className="mb-6">
          <p className="text-gray-800 mb-3">
            Bạn có chắc muốn xóa thẻ tín dụng <strong>{card.card_number?.slice(-4)}</strong>?
          </p>
          <p className="text-gray-600">
            Hành động này không thể hoàn tác. Tất cả dữ liệu liên quan đến thẻ này sẽ bị xóa vĩnh viễn.
          </p>
        </div>
        
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={onClose}
            className="flex-1"
            disabled={loading}
          >
            Hủy
          </Button>
          <Button
            onClick={handleDelete}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white"
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Đang xóa...
              </>
            ) : (
              <>
                <Trash2 className="h-4 w-4 mr-2" />
                Xóa Vĩnh Viễn
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

// Main App Component  
function App() {
  return (
    <div className="App min-h-screen bg-gray-50">
      <BrowserRouter>
        <Navigation />
        <main className="min-h-screen pt-20">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/check-bill" element={<CheckBill />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/credit-cards" element={<CreditCards />} />
            <Route path="/sales" element={<Sales />} />
          </Routes>
        </main>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;