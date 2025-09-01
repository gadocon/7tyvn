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
  Trash2
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
        // Fetch inventory items (available only)
        const params = new URLSearchParams();
        params.append("status", "AVAILABLE");
        if (searchTerm) {
          params.append("search", searchTerm);
        }
        const itemsResponse = await axios.get(`${API}/inventory?${params.toString()}`);
        setInventoryItems(itemsResponse.data);
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
      toast.error("Có lỗi xảy ra khi xóa bill");
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
                        Tên Khách Hàng
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
                    <TableHead>Kỳ Thanh Toán</TableHead>
                    <TableHead>Vùng</TableHead>
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
                    <TableHead>
                      {activeTab === "available" ? "Ghi Chú" : "Ngày Tạo"}
                    </TableHead>
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
                        <Badge variant="outline">
                          {item.provider_region === "MIEN_BAC" ? "Miền Bắc" : 
                           item.provider_region === "MIEN_NAM" ? "Miền Nam" : "TP.HCM"}
                        </Badge>
                      </TableCell>
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
                        ) : (
                          <Badge className="bg-gray-100 text-gray-800">
                            {item.status}
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="max-w-xs truncate">
                        {activeTab === "available" 
                          ? (item.note || "-")
                          : new Date(item.created_at).toLocaleDateString('vi-VN')
                        }
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {item.status === "AVAILABLE" && activeTab === "available" && (
                            <Button
                              size="sm"
                              onClick={() => handleSellBill(item)}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              Bán
                            </Button>
                          )}
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
                    <TableCell>{formatDate(transaction.created_at)}</TableCell>
                    <TableCell>
                      <Badge variant="outline">Bán Bill</Badge>
                    </TableCell>
                    <TableCell>{formatCurrency(transaction.total)}</TableCell>
                    <TableCell>{formatCurrency(transaction.profit_value)}</TableCell>
                    <TableCell>{formatCurrency(transaction.payback)}</TableCell>
                    <TableCell>{transaction.method}</TableCell>
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
            <Route path="/sales" element={<Sales />} />
          </Routes>
        </main>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;