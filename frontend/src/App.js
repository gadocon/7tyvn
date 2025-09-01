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
  AlertTriangle
} from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Navigation Component
const Navigation = () => {
  const location = useLocation();
  
  const navItems = [
    { path: "/", label: "Dashboard", icon: Home },
    { path: "/check-bill", label: "Kiểm Tra Mã Điện", icon: FileCheck },
    { path: "/inventory", label: "Kho Bill", icon: Package },
    { path: "/customers", label: "Khách Hàng", icon: Users },
    { path: "/sales", label: "Bán Bill", icon: ShoppingCart }
  ];

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">FPT Bill Manager</span>
          </div>
          
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
        </div>
        
        <div className="flex items-center space-x-4">
          <Badge variant="outline" className="text-green-600 border-green-200">
            Đang hoạt động
          </Badge>
        </div>
      </div>
    </nav>
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
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedBills, setSelectedBills] = useState([]);
  const [checkAllSelected, setCheckAllSelected] = useState(false);
  const [processingStep, setProcessingStep] = useState("");
  const [processedCount, setProcessedCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);

  const handleCheckBills = async () => {
    if (!codes.trim()) {
      toast.error("Vui lòng nhập mã điện");
      return;
    }

    setLoading(true);
    setProcessingStep("Đang chuẩn bị...");
    setProcessedCount(0);
    
    try {
      const codeList = codes
        .split('\n')
        .map(code => code.trim())
        .filter(code => code.length > 0);

      setTotalCount(codeList.length);
      setProcessingStep(`Đang kiểm tra ${codeList.length} mã điện qua cổng FPT...`);

      const response = await axios.post(`${API}/bill/check`, {
        gateway: "FPT",
        provider_region: provider,
        codes: codeList
      });

      setProcessingStep("Đang xử lý kết quả...");
      setProcessedCount(codeList.length);

      setTimeout(() => {
        setResults(response.data);
        setSelectedBills([]);
        setCheckAllSelected(false);
        setProcessingStep("");
        
        if (response.data.summary.ok > 0) {
          toast.success(`Tìm thấy ${response.data.summary.ok} bill hợp lệ`);
        }
        if (response.data.summary.error > 0) {
          toast.warning(`${response.data.summary.error} mã không tìm thấy`);
        }
      }, 800);
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
      const validBills = results?.items?.filter(bill => bill.status === "OK") || [];
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
      // For now, we'll use customer_code as bill_id since we don't have actual bill IDs from check
      // In real implementation, the check API should return bill IDs
      const billIds = selectedBills.map(bill => bill.customer_code); // This is temporary
      
      const response = await axios.post(`${API}/inventory/add`, {
        bill_ids: billIds,
        note: `Thêm từ kiểm tra mã điện - ${new Date().toLocaleDateString('vi-VN')}`,
        batch_name: `Check_${Date.now()}`
      });

      if (response.data.success) {
        toast.success(response.data.message);
        setSelectedBills([]);
        setCheckAllSelected(false);
        
        // Update results to remove added bills
        const remainingResults = {
          ...results,
          items: results.items.map(item => 
            selectedBills.some(b => b.customer_code === item.customer_code)
              ? { ...item, status: "ADDED_TO_INVENTORY" }
              : item
          )
        };
        setResults(remainingResults);
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
                  placeholder="PA22040522471&#10;PA22040506503,1,676,138&#10;PA22060724572,2,017,202"
                  value={codes}
                  onChange={(e) => setCodes(e.target.value)}
                  rows={6}
                  className="font-mono"
                />
                <p className="text-sm text-gray-500">
                  Có thể dán kèm số tiền (sẽ tự động loại bỏ). Ví dụ: PA22040522471,1,250,000
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
      {results && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Kết Quả Kiểm Tra</CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                Tìm thấy {results.summary.ok} bill hợp lệ, {results.summary.error} lỗi
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
                    {results.items.some(bill => bill.status === "OK") && (
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
                {results.items.map((bill, index) => (
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

  useEffect(() => {
    fetchInventoryData();
  }, [activeTab, searchTerm]);

  const fetchInventoryData = async () => {
    try {
      // Fetch stats
      const statsResponse = await axios.get(`${API}/inventory/stats`);
      setInventoryStats(statsResponse.data);

      // Fetch inventory items
      const params = new URLSearchParams();
      if (activeTab === "available") {
        params.append("status", "AVAILABLE");
      }
      if (searchTerm) {
        params.append("search", searchTerm);
      }

      const itemsResponse = await axios.get(`${API}/inventory?${params.toString()}`);
      setInventoryItems(itemsResponse.data);
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
        <Button className="bg-blue-600 hover:bg-blue-700">
          <Plus className="h-4 w-4 mr-2" />
          Thêm Bill Mới
        </Button>
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
              <TabsTrigger value="all">Tất Cả Bills ({inventoryStats?.total_bills || 0})</TabsTrigger>
            </TabsList>
          </Tabs>

          {/* Inventory Table */}
          {inventoryItems.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Mã Điện</TableHead>
                  <TableHead>Tên Khách Hàng</TableHead>
                  <TableHead>Địa Chỉ</TableHead>
                  <TableHead>Số Tiền</TableHead>
                  <TableHead>Kỳ Thanh Toán</TableHead>
                  <TableHead>Vùng</TableHead>
                  <TableHead>Trạng Thái</TableHead>
                  <TableHead>Ghi Chú</TableHead>
                  <TableHead>Ngày Thêm</TableHead>
                  <TableHead>Thao Tác</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {inventoryItems.map((item) => (
                  <TableRow key={item.id}>
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
                      ) : (
                        <Badge className="bg-gray-100 text-gray-800">
                          Đã Bán
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="max-w-xs truncate">
                      {item.note || "-"}
                    </TableCell>
                    <TableCell>{formatDate(item.created_at)}</TableCell>
                    <TableCell>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRemoveFromInventory(item.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <XCircle className="h-3 w-3 mr-1" />
                        Xóa
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-12">
              <Package className="h-16 w-16 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Kho trống</h3>
              <p className="text-gray-500 mb-4">
                {activeTab === "available" 
                  ? "Không có bill nào sẵn sàng trong kho" 
                  : "Chưa có bill nào trong kho"}
              </p>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Thêm Bill Đầu Tiên
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

const Customers = () => (
  <div className="p-6">
    <div className="text-center py-12">
      <Users className="h-16 w-16 mx-auto text-gray-400 mb-4" />
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Quản Lý Khách Hàng</h2>
      <p className="text-gray-600">Tính năng đang được phát triển</p>
    </div>
  </div>
);

const Sales = () => (
  <div className="p-6">
    <div className="text-center py-12">
      <ShoppingCart className="h-16 w-16 mx-auto text-gray-400 mb-4" />
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Bán Bill</h2>
      <p className="text-gray-600">Tính năng đang được phát triển</p>
    </div>
  </div>
);

// Main App Component
function App() {
  return (
    <div className="App min-h-screen bg-gray-50">
      <BrowserRouter>
        <Navigation />
        <main className="min-h-screen">
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