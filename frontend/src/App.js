import React, { createContext, useContext, useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { Toaster, toast } from "sonner";
import axios from "axios";
import { AnimatePresence, motion } from "framer-motion";
import { Lock, User, Terminal, ChevronRight, LogOut, Search, Activity, ShieldAlert, Cpu, Plus, CreditCard, ShoppingBag, Code2, Play, ChevronLeft } from "lucide-react";

axios.defaults.baseURL = process.env.REACT_APP_BACKEND_URL;
axios.defaults.withCredentials = true;

const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [justLoggedIn, setJustLoggedIn] = useState(false);

  const checkAuth = async () => {
    try {
      const { data } = await axios.get("/api/auth/me");
      setUser(data);
    } catch (e) {
      setUser(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const logout = async () => {
    try {
      await axios.post("/api/auth/logout");
      setUser(false);
      setJustLoggedIn(false);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <AuthContext.Provider value={{ user, setUser, loading, logout, justLoggedIn, setJustLoggedIn }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => useContext(AuthContext);

function formatApiError(detail) {
  if (!detail) return "An error occurred";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map(e => e.msg || JSON.stringify(e)).join(", ");
  if (detail.msg) return detail.msg;
  return String(detail);
}

// Modern Reusable Components
const Input = React.forwardRef(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={`flex h-11 w-full rounded-xl border border-white/10 bg-white/[0.02] px-4 py-2 text-sm text-white placeholder:text-zinc-600 focus-visible:outline-none focus-visible:border-white/20 focus-visible:ring-1 focus-visible:ring-white/20 transition-all ${className || ""}`}
    {...props}
  />
));

const Textarea = React.forwardRef(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={`flex min-h-[120px] w-full rounded-xl border border-white/10 bg-white/[0.02] px-4 py-3 text-sm text-white placeholder:text-zinc-600 focus-visible:outline-none focus-visible:border-white/20 focus-visible:ring-1 focus-visible:ring-white/20 transition-all resize-y font-mono ${className || ""}`}
    {...props}
  />
));

const Button = React.forwardRef(({ className, variant = "default", size = "default", ...props }, ref) => {
  const base = "inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/20 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]";
  const variants = {
    default: "bg-white text-black hover:bg-zinc-200 shadow-sm",
    outline: "border border-white/10 bg-transparent text-white hover:bg-white/5",
    ghost: "hover:bg-white/10 text-zinc-400 hover:text-white",
    danger: "bg-red-500/10 text-red-500 hover:bg-red-500/20 border border-red-500/20",
  };
  const sizes = {
    default: "h-11 px-4 py-2",
    sm: "h-9 rounded-lg px-3",
    icon: "h-10 w-10",
  };
  return (
    <button ref={ref} className={`${base} ${variants[variant]} ${sizes[size]} ${className || ""}`} {...props} />
  );
});

// Pages
const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { user, setUser, setJustLoggedIn } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      navigate(user.role === "admin" ? "/admin" : "/dashboard", { replace: true });
    }
  }, [user, navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await axios.post("/api/auth/login", { username, password });
      setJustLoggedIn(true);
      setUser(data.user);
      navigate(data.user.role === "admin" ? "/admin" : "/dashboard", { replace: true });
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail) || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ duration: 0.4 }}
      className="min-h-screen flex items-center justify-center p-4 relative z-10"
    >
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-white/[0.02] rounded-full blur-[100px] pointer-events-none"></div>

      <div className="w-full max-w-[420px] bg-[#09090b] border border-white/5 rounded-2xl p-8 shadow-2xl relative z-10">
        <div className="flex flex-col items-center text-center mb-8">
          <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-zinc-800 to-zinc-950 border border-white/10 flex items-center justify-center mb-5 shadow-lg">
            <Terminal className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-2xl font-semibold text-white tracking-tight">VeLuX System</h1>
          <p className="text-sm text-zinc-500 mt-2">Enter your credentials to access the checker.</p>
        </div>
        
        <form onSubmit={handleLogin} className="space-y-5">
          <div className="space-y-2">
            <label className="text-xs font-medium text-zinc-400 ml-1">Username</label>
            <div className="relative">
              <User className="absolute left-3.5 top-3.5 h-4 w-4 text-zinc-500" />
              <Input 
                value={username} 
                onChange={(e) => setUsername(e.target.value)} 
                className="pl-10" 
                placeholder="admin" 
                data-testid="login-username"
                required
              />
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-zinc-400 ml-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3.5 h-4 w-4 text-zinc-500" />
              <Input 
                type="password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                className="pl-10" 
                placeholder="••••••••" 
                data-testid="login-password"
                required
              />
            </div>
          </div>
          
          <Button 
            type="submit" 
            className="w-full mt-2 group" 
            disabled={loading}
            data-testid="login-submit"
          >
            {loading ? "Authenticating..." : "Sign In"}
            {!loading && <ChevronRight className="ml-1.5 h-4 w-4 opacity-50 group-hover:translate-x-0.5 transition-transform" />}
          </Button>
        </form>
      </div>
    </motion.div>
  );
};

const VoidTransition = ({ onComplete }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onComplete();
    }, 3000); 
    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <motion.div 
      className="fixed inset-0 bg-black z-50 flex items-center justify-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.h2 
        className="font-mono text-zinc-400 text-sm md:text-base tracking-[0.2em]"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: [0, 1, 1, 0], y: [10, 0, 0, -10] }}
        transition={{ duration: 3, times: [0, 0.3, 0.7, 1], ease: "easeInOut" }}
      >
        Welcome to NetherWorld.
      </motion.h2>
    </motion.div>
  );
};

const DashboardLayout = ({ children, title }) => {
  const { user, logout } = useAuth();
  
  return (
    <div className="min-h-screen flex flex-col z-10 relative">
      <header className="h-16 border-b border-white/5 bg-[#000000]/80 backdrop-blur-xl flex items-center justify-between px-6 sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
            <Terminal className="h-4 w-4 text-white" />
          </div>
          <span className="font-semibold text-white tracking-tight text-sm">VeLuX</span>
          <span className="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-[10px] uppercase font-mono text-zinc-400 ml-2">
            {user.role}
          </span>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-4 mr-4">
            <div className="flex flex-col items-end">
              <span className="text-[10px] font-medium text-zinc-500 uppercase tracking-wider">User</span>
              <span className="text-xs text-zinc-300 font-medium">{user.username}</span>
            </div>
            <div className="h-8 w-px bg-white/10"></div>
            <div className="flex flex-col items-start">
              <span className="text-[10px] font-medium text-zinc-500 uppercase tracking-wider">Credits</span>
              <span className="text-xs text-white font-mono">{user.credits?.toLocaleString()}</span>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={logout} data-testid="logout-btn" className="h-9 px-3 gap-2">
            <LogOut className="h-4 w-4" />
            <span className="hidden sm:inline">Sign Out</span>
          </Button>
        </div>
      </header>
      <main className="flex-1 p-6 md:p-8 lg:p-12 relative z-10">
        <div className="max-w-[1200px] mx-auto space-y-8">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl md:text-3xl font-semibold text-white tracking-tight">{title}</h1>
          </div>
          {children}
        </div>
      </main>
    </div>
  );
};

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // New user form state
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newCredits, setNewCredits] = useState(100);

  const fetchUsers = async () => {
    try {
      const { data } = await axios.get("/api/admin/users");
      setUsers(data);
    } catch (e) {
      toast.error("Failed to fetch users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      await axios.post("/api/admin/users", {
        username: newUsername,
        password: newPassword,
        role: "user",
        credits: parseInt(newCredits, 10),
        limits: "standard"
      });
      toast.success("User successfully created.");
      setNewUsername("");
      setNewPassword("");
      fetchUsers();
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail) || "Failed to create user");
    }
  };

  const toggleStatus = async (user) => {
    try {
      const newStatus = user.status === "active" ? "banned" : "active";
      await axios.patch(`/api/admin/users/${user._id}`, { status: newStatus });
      toast.success(`User status changed to ${newStatus}`);
      fetchUsers();
    } catch (e) {
      toast.error("Failed to update status");
    }
  };
  
  const deleteUser = async (userId) => {
    if (!window.confirm("Are you sure you want to delete this user? This cannot be undone.")) return;
    try {
      await axios.delete(`/api/admin/users/${userId}`);
      toast.success("User deleted.");
      fetchUsers();
    } catch (e) {
      toast.error("Failed to delete user");
    }
  };

  return (
    <DashboardLayout title="Users & Access">
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        <div className="xl:col-span-1">
          <div className="bg-[#09090b] border border-white/5 rounded-2xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="h-8 w-8 rounded-lg bg-white/5 flex items-center justify-center">
                <Plus className="h-4 w-4 text-white" />
              </div>
              <h3 className="font-medium text-white">Create User</h3>
            </div>
            <form onSubmit={handleCreateUser} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-400 ml-1">Username</label>
                <Input value={newUsername} onChange={(e) => setNewUsername(e.target.value)} required placeholder="johndoe" data-testid="create-user-username" />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-400 ml-1">Password</label>
                <Input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required placeholder="••••••••" data-testid="create-user-password" />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-400 ml-1">Initial Credits</label>
                <Input type="number" value={newCredits} onChange={(e) => setNewCredits(e.target.value)} min="0" required />
              </div>
              <Button type="submit" className="w-full mt-4" data-testid="create-user-submit">Create Account</Button>
            </form>
          </div>
        </div>

        <div className="xl:col-span-2">
          <div className="bg-[#09090b] border border-white/5 rounded-2xl shadow-xl overflow-hidden flex flex-col h-full">
            <div className="px-6 py-5 border-b border-white/5 flex items-center justify-between">
              <h3 className="font-medium text-white">Directory</h3>
              <span className="text-xs text-zinc-500 font-mono">{users.length} Total</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-white/5 bg-white/[0.02]">
                    <th className="px-6 py-3 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">User</th>
                    <th className="px-6 py-3 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">Status</th>
                    <th className="px-6 py-3 text-[11px] font-semibold uppercase tracking-wider text-zinc-500 text-right">Credits</th>
                    <th className="px-6 py-3 text-[11px] font-semibold uppercase tracking-wider text-zinc-500 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  {users.map(u => (
                    <tr key={u._id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-zinc-800 to-zinc-900 border border-white/5 flex items-center justify-center shrink-0">
                            <span className="text-xs font-medium text-zinc-300">{u.username.substring(0,2).toUpperCase()}</span>
                          </div>
                          <div>
                            <div className="font-medium text-zinc-200">{u.username}</div>
                            <div className="text-[10px] text-zinc-500 uppercase tracking-wider mt-0.5">{u.role}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${u.status === 'active' ? 'bg-green-500/10 text-green-500 border-green-500/20' : 'bg-red-500/10 text-red-500 border-red-500/20'}`}>
                          <div className={`w-1.5 h-1.5 rounded-full ${u.status === 'active' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                          {u.status === 'active' ? 'Active' : 'Banned'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className="font-mono text-zinc-300">{u.credits?.toLocaleString()}</span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex justify-end gap-2">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => toggleStatus(u)}
                            data-testid={`toggle-status-${u._id}`}
                          >
                            {u.status === 'active' ? 'Ban' : 'Unban'}
                          </Button>
                          <Button 
                            variant="danger" 
                            size="sm" 
                            onClick={() => deleteUser(u._id)}
                            data-testid={`delete-user-${u._id}`}
                          >
                            Delete
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {users.length === 0 && !loading && (
                    <tr>
                      <td colSpan="4" className="px-6 py-12 text-center text-zinc-500">No users found.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

const ProxyManager = ({ onBack }) => {
  const [proxies, setProxies] = useState("");
  const [savedProxies, setSavedProxies] = useState([]);
  const [checking, setChecking] = useState(false);

  const fetchSaved = async () => {
    try {
      const { data } = await axios.get("/api/proxies");
      setSavedProxies(data);
    } catch (e) {
      console.error(e);
    }
  };
  
  useEffect(() => { fetchSaved(); }, []);

  const handleCheck = async (e) => {
    e.preventDefault();
    if (!proxies.trim()) return;
    setChecking(true);
    try {
      const { data } = await axios.post("/api/proxies/check", { proxies });
      toast.success(`Check complete. ${data.successful} saved, ${data.failed} failed.`);
      setProxies("");
      fetchSaved();
    } catch (e) {
      toast.error("Failed to check proxies");
    } finally {
      setChecking(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`/api/proxies/${id}`);
      fetchSaved();
    } catch (e) {}
  };

  return (
    <DashboardLayout title="Proxy Nodes">
      <Button variant="ghost" onClick={onBack} className="mb-2 -mt-4 pl-0 hover:bg-transparent" data-testid="back-to-gateways">
        <ChevronLeft className="w-4 h-4 mr-1" />
        Back to Checker Gateways
      </Button>
      
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <div className="bg-[#09090b] border border-white/5 p-6 rounded-2xl shadow-xl">
          <h2 className="text-xl font-semibold text-white mb-2">Import Nodes</h2>
          <p className="text-sm text-zinc-500 mb-6">Enter proxies (ip:port or ip:port:user:pass). We will test them against Stripe and Shopify APIs before saving.</p>
          <form onSubmit={handleCheck}>
            <Textarea 
              value={proxies} 
              onChange={e => setProxies(e.target.value)} 
              placeholder="192.168.1.1:8080&#10;test:proxy" 
              className="min-h-[250px] mb-4" 
              data-testid="proxies-textarea"
            />
            <Button type="submit" disabled={checking} className="w-full" data-testid="check-proxies-btn">
              {checking ? "Checking..." : "Check & Save Proxies"}
            </Button>
          </form>
        </div>
        
        <div className="bg-[#09090b] border border-white/5 rounded-2xl shadow-xl overflow-hidden flex flex-col h-[500px]">
          <div className="px-6 py-5 border-b border-white/5 flex items-center justify-between">
            <h3 className="font-medium text-white">Active Nodes</h3>
            <span className="text-xs text-zinc-500 font-mono">{savedProxies.length} Saved</span>
          </div>
          <div className="flex-1 overflow-y-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-white/5 bg-white/[0.02]">
                  <th className="px-6 py-3 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">Proxy Address</th>
                  <th className="px-6 py-3 text-[11px] font-semibold uppercase tracking-wider text-zinc-500 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {savedProxies.map(p => (
                  <tr key={p._id} className="border-b border-white/5 hover:bg-white/[0.02]">
                    <td className="px-6 py-4 font-mono text-sm text-zinc-300">{p.raw}</td>
                    <td className="px-6 py-4 text-right">
                      <Button variant="danger" size="sm" onClick={() => handleDelete(p._id)}>Remove</Button>
                    </td>
                  </tr>
                ))}
                {savedProxies.length === 0 && (
                  <tr>
                    <td colSpan="2" className="px-6 py-12 text-center text-zinc-500 text-sm">No proxy nodes saved yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

const UserDashboard = () => {
  const [view, setView] = useState("gateways"); // 'gateways' | 'proxies'
  const [activeGateway, setActiveGateway] = useState("stripe");
  const [proxyCount, setProxyCount] = useState(0);

  const [stripeSk, setStripeSk] = useState("");
  const [stripeCc, setStripeCc] = useState("");
  const [shopifyUrls, setShopifyUrls] = useState("");
  const [shopifyCc, setShopifyCc] = useState("");

  useEffect(() => {
    axios.get("/api/proxies").then(res => setProxyCount(res.data.length)).catch(() => {});
  }, [view]);

  if (view === "proxies") {
    return <ProxyManager onBack={() => setView("gateways")} />;
  }

  const handleStartChecker = (e) => {
    e.preventDefault();
    if (proxyCount === 0) {
      toast.error("Please add and configure at least one proxy node before starting.");
      return;
    }
    toast.info("Checker engine is currently initializing. Please stand by.");
  };

  return (
    <DashboardLayout title="Checker Protocol">
      
      <div className="flex items-center p-1 space-x-1 bg-white/[0.02] border border-white/5 rounded-xl w-fit mb-2 shadow-sm">
        <button 
          onClick={() => setActiveGateway('stripe')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${activeGateway === 'stripe' ? 'bg-white/10 text-white shadow-sm' : 'text-zinc-500 hover:text-zinc-300'}`}
        >
          <CreditCard className="w-4 h-4" />
          Stripe
        </button>
        <button 
          onClick={() => setActiveGateway('shopify')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${activeGateway === 'shopify' ? 'bg-white/10 text-white shadow-sm' : 'text-zinc-500 hover:text-zinc-300'}`}
        >
          <ShoppingBag className="w-4 h-4" />
          Shopify
        </button>
        <button 
          onClick={() => setActiveGateway('braintree')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${activeGateway === 'braintree' ? 'bg-white/10 text-white shadow-sm' : 'text-zinc-500 hover:text-zinc-300'}`}
        >
          <Code2 className="w-4 h-4" />
          Braintree
        </button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        {/* Main Checker Interface */}
        <div className="xl:col-span-2">
          <AnimatePresence mode="wait">
            
            {activeGateway === 'stripe' && (
              <motion.div 
                key="stripe"
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}
                className="bg-[#09090b] border border-white/5 p-6 md:p-8 rounded-2xl shadow-xl"
              >
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-white">Stripe Validation</h2>
                  <p className="text-sm text-zinc-500 mt-1">Check cards against a live Stripe Secret Key.</p>
                </div>

                <form onSubmit={handleStartChecker} className="space-y-5">
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-zinc-400 ml-1">Stripe Secret Key (sk_live_...)</label>
                    <Input 
                      type="password"
                      placeholder="sk_live_..."
                      value={stripeSk}
                      onChange={(e) => setStripeSk(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-zinc-400 ml-1">Credit Card List</label>
                    <Textarea 
                      placeholder="4111111111111111|12|2025|123&#10;5111111111111111|09|2026|456"
                      value={stripeCc}
                      onChange={(e) => setStripeCc(e.target.value)}
                      className="min-h-[200px]"
                      required
                    />
                    <p className="text-[10px] text-zinc-600 ml-1">Format: CC|MM|YY|CVV</p>
                  </div>
                  <div className="pt-2">
                    <Button type="submit" className="w-full sm:w-auto min-w-[200px] gap-2">
                      <Play className="w-4 h-4" />
                      Start Checker
                    </Button>
                  </div>
                </form>
              </motion.div>
            )}

            {activeGateway === 'shopify' && (
              <motion.div 
                key="shopify"
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}
                className="bg-[#09090b] border border-white/5 p-6 md:p-8 rounded-2xl shadow-xl"
              >
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-white">Shopify Gateway</h2>
                  <p className="text-sm text-zinc-500 mt-1">Check cards via live Shopify product checkout routes.</p>
                </div>

                <form onSubmit={handleStartChecker} className="space-y-5">
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-zinc-400 ml-1">Product URLs</label>
                    <Textarea 
                      placeholder="https://store.com/products/item-1&#10;https://store.com/products/item-2"
                      value={shopifyUrls}
                      onChange={(e) => setShopifyUrls(e.target.value)}
                      className="min-h-[100px]"
                      required
                    />
                    <p className="text-[10px] text-zinc-600 ml-1">One URL per line.</p>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-zinc-400 ml-1">Credit Card List</label>
                    <Textarea 
                      placeholder="4111111111111111|12|2025|123"
                      value={shopifyCc}
                      onChange={(e) => setShopifyCc(e.target.value)}
                      className="min-h-[150px]"
                      required
                    />
                    <p className="text-[10px] text-zinc-600 ml-1">Format: CC|MM|YY|CVV</p>
                  </div>
                  <div className="pt-2">
                    <Button type="submit" className="w-full sm:w-auto min-w-[200px] gap-2">
                      <Play className="w-4 h-4" />
                      Start Checker
                    </Button>
                  </div>
                </form>
              </motion.div>
            )}

            {activeGateway === 'braintree' && (
              <motion.div 
                key="braintree"
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}
                className="bg-[#09090b] border border-white/5 p-6 md:p-8 rounded-2xl shadow-xl min-h-[450px] flex flex-col items-center justify-center text-center relative overflow-hidden group"
              >
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(255,255,255,0.03)_0%,_transparent_70%)] opacity-0 group-hover:opacity-100 transition-opacity duration-1000"></div>
                <div className="h-16 w-16 rounded-2xl bg-white/[0.02] border border-white/5 flex items-center justify-center mb-6 relative z-10">
                  <Code2 className="h-8 w-8 text-zinc-600" />
                </div>
                <h2 className="text-xl font-medium text-white mb-2 relative z-10">Braintree Integration</h2>
                <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs font-medium text-zinc-400 mb-4 inline-block relative z-10">Coming Soon</span>
                <p className="text-zinc-500 max-w-sm mx-auto leading-relaxed relative z-10">
                  The Braintree processing module is currently under active development. It will support direct client token extraction and payload validation.
                </p>
              </motion.div>
            )}

          </AnimatePresence>

        </div>

        {/* Status Sidebar */}
        <div className="xl:col-span-1 space-y-6">
          <div className="bg-[#09090b] border border-white/5 p-6 rounded-2xl shadow-xl">
             <div className="flex items-center gap-3 mb-4">
                <div className="h-8 w-8 rounded-lg bg-green-500/10 border border-green-500/20 flex items-center justify-center">
                  <Activity className="h-4 w-4 text-green-500" />
                </div>
                <h3 className="font-medium text-white">System Status</h3>
             </div>
             <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-zinc-500">Core Engine</span>
                  <span className="text-sm text-green-500 font-medium">Online</span>
                </div>
                <div className="h-px w-full bg-white/5"></div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-zinc-500">Proxy Nodes</span>
                  <span className={`text-sm font-medium ${proxyCount > 0 ? 'text-white' : 'text-zinc-400'}`}>{proxyCount} Active</span>
                </div>
                <div className="h-px w-full bg-white/5"></div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-zinc-500">API Vault</span>
                  <span className="text-[10px] uppercase font-bold text-zinc-600 tracking-wider">Deploying</span>
                </div>
             </div>
          </div>

          <div className="bg-[#09090b] border border-white/5 p-6 rounded-2xl shadow-xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
              <Cpu className="w-16 h-16" />
            </div>
            <div className="h-8 w-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center mb-4 relative z-10">
              <Cpu className="h-4 w-4 text-zinc-400" />
            </div>
            <h3 className="font-medium text-zinc-300 mb-2 relative z-10">Dedicated Proxies</h3>
            <p className="text-zinc-600 text-sm leading-relaxed relative z-10"><span className="text-[10px] font-semibold uppercase text-zinc-400 mr-2 bg-white/5 px-2 py-0.5 rounded">Setup</span> Configure proxies before starting the checker to avoid rate limits.</p>
            <Button variant="outline" size="sm" className="w-full mt-4 relative z-10" onClick={() => setView("proxies")} data-testid="manage-nodes-btn">
              Manage Nodes
            </Button>
          </div>
        </div>

      </div>
    </DashboardLayout>
  );
};

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { user, loading, justLoggedIn, setJustLoggedIn } = useAuth();
  const [transitioning, setTransitioning] = useState(false);

  useEffect(() => {
    if (justLoggedIn) {
      setTransitioning(true);
    }
  }, [justLoggedIn]);

  if (loading) return <div className="min-h-screen bg-[#000] flex items-center justify-center"><div className="w-6 h-6 border-2 border-zinc-800 border-t-white rounded-full animate-spin"></div></div>;
  
  if (!user) return <Navigate to="/login" replace />;
  
  if (adminOnly && user.role !== "admin") return <Navigate to="/dashboard" replace />;

  if (transitioning) {
    return (
      <VoidTransition 
        onComplete={() => {
          setTransitioning(false);
          setJustLoggedIn(false);
        }} 
      />
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.32, 0.72, 0, 1] }}
      className="w-full h-full"
    >
      {children}
    </motion.div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen text-white font-sans relative bg-[#000]">
        <div className="bg-noise" />
        <Toaster theme="dark" toastOptions={{ className: 'rounded-xl border border-white/10 bg-[#0a0a0a] text-zinc-200 font-sans shadow-2xl' }} />
        
        <BrowserRouter>
          <AnimatePresence mode="wait">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/login" element={<Login />} />
              <Route 
                path="/admin" 
                element={
                  <ProtectedRoute adminOnly>
                    <AdminDashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <DashboardRouter />
                  </ProtectedRoute>
                } 
              />
            </Routes>
          </AnimatePresence>
        </BrowserRouter>
      </div>
    </AuthProvider>
  );
}

const DashboardRouter = () => {
  const { user } = useAuth();
  if (user?.role === "admin") return <Navigate to="/admin" replace />;
  return <UserDashboard />;
};
