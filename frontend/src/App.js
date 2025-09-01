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

  const handleSellBill = (inventoryItem) => {
    setSelectedBillForSale(inventoryItem);
    setShowSellModal(true);
  };

  const handleSellComplete = () => {
    setShowSellModal(false);
    setSelectedBillForSale(null);
    fetchInventoryData(); // Refresh data
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
                      <div className="flex items-center space-x-2">
                        {item.status === "AVAILABLE" && (
                          <Button
                            size="sm"
                            onClick={() => handleSellBill(item)}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            <DollarSign className="h-3 w-3 mr-1" />
                            Bán
                          </Button>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleRemoveFromInventory(item.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <XCircle className="h-3 w-3 mr-1" />
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

      {/* Sell Bill Modal */}
      <SellBillModal
        show={showSellModal}
        billItem={selectedBillForSale}
        onClose={() => setShowSellModal(false)}
        onComplete={handleSellComplete}
      />
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

  const handleDeleteCustomer = async (customerId) => {
    if (!window.confirm("Bạn có chắc chắn muốn xóa khách hàng này?")) return;
    
    try {
      await axios.delete(`${API}/customers/${customerId}`);
      toast.success("Đã xóa khách hàng thành công");
      fetchCustomersData();
    } catch (error) {
      console.error("Error deleting customer:", error);
      toast.error(error.response?.data?.detail || "Có lỗi xảy ra khi xóa khách hàng");
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
        <Button onClick={() => setShowAddModal(true)} className="bg-blue-600 hover:bg-blue-700">
          <Plus className="h-4 w-4 mr-2" />
          Thêm Khách Hàng
        </Button>
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
                  <TableHead>Tên Khách Hàng</TableHead>
                  <TableHead>Loại</TableHead>
                  <TableHead>Điện Thoại</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Số Giao Dịch</TableHead>
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
                    <TableCell>{customer.email || "-"}</TableCell>
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
                        {customer.total_transactions === 0 && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDeleteCustomer(customer.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            Xóa
                          </Button>
                        )}
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
                  <TableHead>Ngày</TableHead>
                  <TableHead>Loại</TableHead>
                  <TableHead>Tổng Tiền</TableHead>
                  <TableHead>Lợi Nhuận</TableHead>
                  <TableHead>Trả Khách</TableHead>
                  <TableHead>PT Thanh Toán</TableHead>
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

const Sales = () => (
  <div className="p-6">
    <div className="text-center py-12">
      <ShoppingCart className="h-16 w-16 mx-auto text-gray-400 mb-4" />
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Bán Bill</h2>
      <p className="text-gray-600">Tính năng đang được phát triển</p>
    </div>
  </div>
);

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

// Main App Component  
function App() {
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