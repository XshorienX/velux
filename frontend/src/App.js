import React, { createContext, useContext, useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";
import { Toaster, toast } from "sonner";
import axios from "axios";
import { AnimatePresence, motion } from "framer-motion";
import { Lock, User, Terminal, ChevronRight, LogOut, Activity, ShieldAlert, Cpu, Plus, CreditCard, ShoppingBag, Code2, Play, Settings as SettingsIcon, Home, CheckCircle2, XCircle, LayoutDashboard, Globe, MessageSquare } from "lucide-react";

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

  useEffect(() => { checkAuth(); }, []);

  const logout = async () => {
    try {
      await axios.post("/api/auth/logout");
      setUser(false);
      setJustLoggedIn(false);
    } catch (e) {}
  };

  return (
    <AuthContext.Provider value={{ user, setUser, loading, logout, justLoggedIn, setJustLoggedIn, checkAuth }}>
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

const Input = React.forwardRef(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={`flex h-11 w-full rounded-xl border border-slate-800 bg-slate-900/50 px-4 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus-visible:outline-none focus-visible:border-slate-500 focus-visible:ring-1 focus-visible:ring-slate-500 transition-all ${className || ""}`}
    {...props}
  />
));

const Textarea = React.forwardRef(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={`flex min-h-[120px] w-full rounded-xl border border-slate-800 bg-slate-900/50 px-4 py-3 text-sm text-slate-200 placeholder:text-slate-600 focus-visible:outline-none focus-visible:border-slate-500 focus-visible:ring-1 focus-visible:ring-slate-500 transition-all resize-y font-mono ${className || ""}`}
    {...props}
  />
));

const Button = React.forwardRef(({ className, variant = "default", size = "default", ...props }, ref) => {
  const base = "inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]";
  const variants = {
    default: "bg-slate-200 text-slate-950 hover:bg-white shadow-sm",
    outline: "border border-slate-800 bg-transparent text-slate-300 hover:bg-slate-800/50",
    ghost: "hover:bg-slate-800/50 text-slate-400 hover:text-slate-200",
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

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { user, setUser, setJustLoggedIn } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate(user.role === "admin" ? "/admin" : "/app/home", { replace: true });
  }, [user, navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await axios.post("/api/auth/login", { username, password });
      setJustLoggedIn(true);
      setUser(data.user);
      navigate(data.user.role === "admin" ? "/admin" : "/app/home", { replace: true });
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail) || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="min-h-screen flex items-center justify-center p-4 relative bg-[#020617]">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-slate-800/10 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="w-full max-w-[420px] bg-[#090b14] border border-slate-800/80 rounded-2xl p-8 shadow-2xl relative z-10">
        <div className="flex flex-col items-center text-center mb-8">
          <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 flex items-center justify-center mb-5 shadow-lg">
            <Terminal className="h-6 w-6 text-slate-300" />
          </div>
          <h1 className="text-2xl font-semibold text-slate-100 tracking-tight">VeLuX System</h1>
          <p className="text-sm text-slate-500 mt-2">Enter credentials to access the terminal.</p>
        </div>
        <form onSubmit={handleLogin} className="space-y-5">
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-400 ml-1">Username</label>
            <div className="relative">
              <User className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
              <Input value={username} onChange={e => setUsername(e.target.value)} className="pl-10" required data-testid="login-username" />
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-400 ml-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
              <Input type="password" value={password} onChange={e => setPassword(e.target.value)} className="pl-10" required data-testid="login-password" />
            </div>
          </div>
          <Button type="submit" className="w-full mt-2" disabled={loading} data-testid="login-submit">
            {loading ? "Authenticating..." : "Sign In"}
          </Button>
        </form>
      </div>
    </motion.div>
  );
};

const VoidTransition = ({ onComplete }) => {
  useEffect(() => {
    const timer = setTimeout(() => onComplete(), 3000);
    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <motion.div className="fixed inset-0 bg-[#020617] z-50 flex items-center justify-center" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <motion.h2 
        className="font-mono text-slate-400 text-sm md:text-base tracking-[0.2em]"
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: [0, 1, 1, 0], y: [10, 0, 0, -10] }}
        transition={{ duration: 3, times: [0, 0.3, 0.7, 1], ease: "easeInOut" }}
      >
        Connecting to nodes...
      </motion.h2>
    </motion.div>
  );
};

// Application Layout with Footer Navigation
const AppLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { id: 'home', path: '/app/home', icon: <Home className="w-5 h-5" />, label: 'Home' },
    { id: 'checker', path: '/app/checker', icon: <LayoutDashboard className="w-5 h-5" />, label: 'Checker' },
    { id: 'proxy', path: '/app/proxy', icon: <Globe className="w-5 h-5" />, label: 'Proxy' },
    { id: 'settings', path: '/app/settings', icon: <SettingsIcon className="w-5 h-5" />, label: 'Settings' }
  ];

  return (
    <div className="min-h-screen flex flex-col z-10 relative bg-[#020617]">
      <header className="h-16 border-b border-slate-800/80 bg-[#020617]/90 backdrop-blur-xl flex items-center justify-between px-6 sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-slate-800/50 border border-slate-700/50 flex items-center justify-center">
            <Terminal className="h-4 w-4 text-slate-200" />
          </div>
          <span className="font-semibold text-slate-100 tracking-tight text-sm">VeLuX</span>
          <span className="px-2 py-0.5 rounded-md bg-slate-800/50 border border-slate-700/50 text-[10px] uppercase font-mono text-slate-400 ml-2">
            {user.role}
          </span>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-4 mr-4">
            <div className="flex flex-col items-end">
              <span className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">User</span>
              <span className="text-xs text-slate-300 font-medium">{user.username}</span>
            </div>
            <div className="h-8 w-px bg-slate-800"></div>
            <div className="flex flex-col items-start">
              <span className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">Credits</span>
              <span className="text-xs text-slate-200 font-mono">{user.credits?.toLocaleString() || 0}</span>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={logout} className="h-9 px-3 gap-2 border-slate-800 text-slate-400">
            <LogOut className="h-4 w-4" />
            <span className="hidden sm:inline">Sign Out</span>
          </Button>
        </div>
      </header>

      <main className="flex-1 p-4 md:p-8 lg:p-10 relative z-10 pb-24">
        {children}
      </main>

      {/* Footer Navigation */}
      <div className="fixed bottom-0 left-0 right-0 h-16 bg-[#090b14]/90 backdrop-blur-xl border-t border-slate-800/80 z-50 flex items-center justify-center px-4">
        <div className="flex items-center gap-2 sm:gap-6 w-full max-w-lg justify-between">
          {navItems.map(item => {
            const isActive = location.pathname === item.path;
            return (
              <button 
                key={item.id}
                onClick={() => navigate(item.path)}
                className={`flex flex-col items-center justify-center w-16 h-12 rounded-xl transition-all ${isActive ? 'text-slate-100' : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/30'}`}
              >
                <div className={`mb-1 transition-transform ${isActive ? '-translate-y-1' : ''}`}>{item.icon}</div>
                <span className={`text-[10px] font-medium transition-opacity ${isActive ? 'opacity-100' : 'opacity-0'}`}>{item.label}</span>
                {isActive && <div className="absolute bottom-1 w-8 h-1 bg-slate-600 rounded-full blur-[2px]"></div>}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  );
};

// Pages Components
const HomeTab = () => {
  const { user } = useAuth();
  return (
    <div className="max-w-[1200px] mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-2xl md:text-3xl font-semibold text-slate-100 tracking-tight">Home Dashboard</h1>
        <p className="text-slate-500 mt-2">Welcome back, {user.username}. Here is your system overview.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-[#090b14] border border-slate-800/80 p-6 rounded-2xl shadow-xl relative overflow-hidden">
          <div className="h-10 w-10 rounded-xl bg-slate-800/50 border border-slate-700 flex items-center justify-center mb-4">
            <Activity className="h-5 w-5 text-slate-200" />
          </div>
          <h3 className="font-medium text-slate-300 mb-1">Lifetime Checked</h3>
          <div className="text-3xl font-mono text-slate-100 font-semibold">{user.total_checked_ccs?.toLocaleString() || 0}</div>
        </div>
        
        <div className="bg-[#090b14] border border-slate-800/80 p-6 rounded-2xl shadow-xl relative overflow-hidden">
          <div className="h-10 w-10 rounded-xl bg-slate-800/50 border border-slate-700 flex items-center justify-center mb-4">
            <Cpu className="h-5 w-5 text-slate-200" />
          </div>
          <h3 className="font-medium text-slate-300 mb-1">Available Credits</h3>
          <div className="text-3xl font-mono text-slate-100 font-semibold">{user.credits?.toLocaleString() || 0}</div>
        </div>

        <div className="bg-[#090b14] border border-slate-800/80 p-6 rounded-2xl shadow-xl relative overflow-hidden">
          <div className="h-10 w-10 rounded-xl bg-slate-800/50 border border-slate-700 flex items-center justify-center mb-4">
            <Globe className="h-5 w-5 text-slate-200" />
          </div>
          <h3 className="font-medium text-slate-300 mb-1">Node Status</h3>
          <div className="text-xl text-slate-400 mt-2">Operational</div>
        </div>
      </div>
    </div>
  );
};

const SettingsTab = () => {
  const { user, checkAuth } = useAuth();
  const [password, setPassword] = useState("");
  const [telegramId, setTelegramId] = useState(user.telegram_id || "");
  const [shopifyUrls, setShopifyUrls] = useState(user.shopify_urls || "");
  const [saving, setSaving] = useState(false);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await axios.patch("/api/auth/me", {
        password: password || undefined,
        telegram_id: telegramId,
        shopify_urls: shopifyUrls
      });
      toast.success("Settings updated successfully");
      setPassword("");
      checkAuth();
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-2xl md:text-3xl font-semibold text-slate-100 tracking-tight">Account Settings</h1>
        <p className="text-slate-500 mt-2">Manage your credentials, integrations, and default behaviors.</p>
      </div>

      <form onSubmit={handleSave} className="bg-[#090b14] border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-6">
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-slate-200 border-b border-slate-800 pb-2">Security</h3>
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-400">Change Password</label>
            <Input type="password" placeholder="Leave blank to keep current" value={password} onChange={e => setPassword(e.target.value)} />
          </div>
        </div>

        <div className="space-y-4 pt-4">
          <h3 className="text-lg font-medium text-slate-200 border-b border-slate-800 pb-2">Integrations</h3>
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-400 flex items-center gap-2"><MessageSquare className="w-3 h-3"/> Telegram ID (For bot notifications)</label>
            <Input placeholder="@username or ID" value={telegramId} onChange={e => setTelegramId(e.target.value)} />
          </div>
        </div>

        <div className="space-y-4 pt-4">
          <h3 className="text-lg font-medium text-slate-200 border-b border-slate-800 pb-2">Defaults</h3>
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-400 flex items-center gap-2"><ShoppingBag className="w-3 h-3"/> Default Shopify Product URLs</label>
            <Textarea placeholder="https://store.com/products/item-1" value={shopifyUrls} onChange={e => setShopifyUrls(e.target.value)} className="min-h-[100px]" />
          </div>
        </div>

        <div className="pt-4 flex justify-end">
          <Button type="submit" disabled={saving}>{saving ? "Saving..." : "Save Settings"}</Button>
        </div>
      </form>
    </div>
  );
};

const ProxyTab = () => {
  const [proxies, setProxies] = useState("");
  const [savedProxies, setSavedProxies] = useState([]);
  const [checking, setChecking] = useState(false);

  const fetchSaved = async () => {
    try {
      const { data } = await axios.get("/api/proxies");
      setSavedProxies(data);
    } catch (e) {}
  };
  useEffect(() => { fetchSaved(); }, []);

  const handleCheck = async (e) => {
    e.preventDefault();
    if (!proxies.trim()) return;
    setChecking(true);
    try {
      const { data } = await axios.post("/api/proxies/check", { proxies });
      toast.success(`Complete: ${data.successful} saved, ${data.failed} failed.`);
      setProxies("");
      fetchSaved();
    } catch (e) {
      toast.error("Failed to process proxies");
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
    <div className="max-w-[1200px] mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-2xl md:text-3xl font-semibold text-slate-100 tracking-tight">Proxy Management</h1>
        <p className="text-slate-500 mt-2">Validated against Stripe API and Shopify API before saving.</p>
      </div>
      
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <div className="bg-[#090b14] border border-slate-800/80 p-6 rounded-2xl shadow-xl">
          <h2 className="text-lg font-semibold text-slate-200 mb-4">Import Nodes</h2>
          <form onSubmit={handleCheck}>
            <Textarea 
              value={proxies} 
              onChange={e => setProxies(e.target.value)} 
              placeholder="192.168.1.1:8080&#10;192.168.1.1:8080:user:pass" 
              className="min-h-[250px] mb-4" 
              data-testid="proxies-textarea"
            />
            <Button type="submit" disabled={checking} className="w-full" data-testid="check-proxies-btn">
              {checking ? "Validating & Saving..." : "Check & Save Proxies"}
            </Button>
          </form>
        </div>
        
        <div className="bg-[#090b14] border border-slate-800/80 rounded-2xl shadow-xl flex flex-col h-[400px]">
          <div className="px-6 py-4 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/30">
            <h3 className="font-medium text-slate-200">Active Nodes</h3>
            <span className="text-xs text-slate-500 font-mono">{savedProxies.length} Saved</span>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            <table className="w-full text-left">
              <tbody>
                {savedProxies.map(p => (
                  <tr key={p._id} className="border-b border-slate-800/30 hover:bg-slate-800/20 group">
                    <td className="px-4 py-3 font-mono text-[13px] text-slate-300">{p.raw}</td>
                    <td className="px-4 py-3 text-right">
                      <Button variant="ghost" size="sm" className="h-8 px-2 text-red-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity" onClick={() => handleDelete(p._id)}>Remove</Button>
                    </td>
                  </tr>
                ))}
                {savedProxies.length === 0 && (
                  <tr>
                    <td colSpan="2" className="px-6 py-12 text-center text-slate-500 text-sm">No proxy nodes saved yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

const CheckerTab = () => {
  const { user } = useAuth();
  const [activeGateway, setActiveGateway] = useState("stripe");
  
  const [stripeSk, setStripeSk] = useState("");
  const [stripeCc, setStripeCc] = useState("");
  
  const [shopifyUrls, setShopifyUrls] = useState(user.shopify_urls || "");
  const [shopifyCc, setShopifyCc] = useState("");

  const gateways = [
    { id: 'stripe', name: 'Stripe', icon: <CreditCard className="w-4 h-4"/>, active: true },
    { id: 'shopify', name: 'Shopify', icon: <ShoppingBag className="w-4 h-4"/>, active: true },
    { id: 'braintree', name: 'Braintree', icon: <Code2 className="w-4 h-4"/>, active: true },
    { id: 'paypal', name: 'PayPal', icon: <Globe className="w-4 h-4"/>, active: false },
    { id: 'adyen', name: 'Adyen', icon: <ShieldAlert className="w-4 h-4"/>, active: false }
  ];

  const handleStartChecker = (e) => {
    e.preventDefault();
    toast.info("Checker engine initializing. Testing cards...");
  };

  return (
    <div className="max-w-[1400px] mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-semibold text-slate-100 tracking-tight">Validation Engine</h1>
          <p className="text-slate-500 mt-2">Select a gateway and input payloads to begin validation.</p>
        </div>
        
        {/* Gateway Selection Row */}
        <div className="flex flex-wrap items-center p-1 bg-slate-900/50 border border-slate-800/80 rounded-xl w-fit">
          {gateways.map(gw => (
            <button 
              key={gw.id}
              onClick={() => gw.active && setActiveGateway(gw.id)}
              disabled={!gw.active}
              className={`flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-lg transition-all ${
                activeGateway === gw.id 
                  ? 'bg-slate-700/50 text-slate-100 shadow-sm' 
                  : gw.active 
                    ? 'text-slate-500 hover:text-slate-300' 
                    : 'text-slate-600 opacity-50 cursor-not-allowed'
              }`}
            >
              {gw.icon}
              <span className="hidden sm:inline">{gw.name}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Checker Interface */}
        <div className="lg:col-span-3">
          <div className="bg-[#090b14] border border-slate-800/80 rounded-2xl shadow-xl overflow-hidden min-h-[500px]">
            <div className="p-6 md:p-8">
              <AnimatePresence mode="wait">
                
                {activeGateway === 'stripe' && (
                  <motion.form key="stripe" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onSubmit={handleStartChecker} className="space-y-5">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-2 bg-indigo-500/10 rounded-lg"><CreditCard className="w-5 h-5 text-indigo-400"/></div>
                      <h2 className="text-xl font-medium text-slate-200">Stripe Integration</h2>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-slate-400">Secret Key</label>
                      <Input type="password" placeholder="sk_live_..." value={stripeSk} onChange={(e) => setStripeSk(e.target.value)} required />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-slate-400">Card Payloads</label>
                      <Textarea placeholder="4111...|12|25|123" value={stripeCc} onChange={(e) => setStripeCc(e.target.value)} className="min-h-[250px]" required />
                    </div>
                    <Button type="submit" className="w-full gap-2 mt-4"><Play className="w-4 h-4" /> Start Validation</Button>
                  </motion.form>
                )}

                {activeGateway === 'shopify' && (
                  <motion.form key="shopify" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onSubmit={handleStartChecker} className="space-y-5">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-2 bg-green-500/10 rounded-lg"><ShoppingBag className="w-5 h-5 text-green-400"/></div>
                      <h2 className="text-xl font-medium text-slate-200">Shopify Gateway</h2>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-slate-400">Target URLs</label>
                      <Textarea placeholder="https://store.com/products/item-1" value={shopifyUrls} onChange={(e) => setShopifyUrls(e.target.value)} className="min-h-[100px]" required />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-slate-400">Card Payloads</label>
                      <Textarea placeholder="4111...|12|25|123" value={shopifyCc} onChange={(e) => setShopifyCc(e.target.value)} className="min-h-[180px]" required />
                    </div>
                    <Button type="submit" className="w-full gap-2 mt-4"><Play className="w-4 h-4" /> Start Validation</Button>
                  </motion.form>
                )}

                {activeGateway === 'braintree' && (
                  <motion.form key="braintree" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onSubmit={handleStartChecker} className="space-y-5">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-2 bg-blue-500/10 rounded-lg"><Code2 className="w-5 h-5 text-blue-400"/></div>
                      <h2 className="text-xl font-medium text-slate-200">Braintree Integration</h2>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-slate-400">Card Payloads</label>
                      <Textarea placeholder="4111...|12|25|123" value={stripeCc} onChange={(e) => setStripeCc(e.target.value)} className="min-h-[250px]" required />
                    </div>
                    <Button type="button" disabled className="w-full gap-2 mt-4 bg-slate-800 text-slate-400">Processing Module Offline</Button>
                  </motion.form>
                )}

              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* Lifetime Stats Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-[#090b14] border border-slate-800/80 p-6 rounded-2xl shadow-xl flex flex-col items-center text-center justify-center min-h-[200px] relative overflow-hidden">
             <div className="absolute top-0 right-0 p-4 opacity-5"><Activity className="w-32 h-32 text-slate-200"/></div>
             <div className="relative z-10">
               <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Lifetime Checked</div>
               <div className="text-5xl font-mono font-bold text-slate-100">{user.total_checked_ccs?.toLocaleString() || 0}</div>
             </div>
          </div>

          <div className="bg-[#090b14] border border-slate-800/80 p-6 rounded-2xl shadow-xl">
             <h3 className="font-medium text-slate-300 mb-4 text-sm">Session Results</h3>
             <div className="space-y-3">
               <div className="flex justify-between items-center bg-green-500/5 px-3 py-2 rounded-lg border border-green-500/10">
                 <span className="text-xs text-green-400/80 font-medium">Approved</span>
                 <span className="text-sm font-mono text-green-400 font-semibold">0</span>
               </div>
               <div className="flex justify-between items-center bg-red-500/5 px-3 py-2 rounded-lg border border-red-500/10">
                 <span className="text-xs text-red-400/80 font-medium">Declined</span>
                 <span className="text-sm font-mono text-red-400 font-semibold">0</span>
               </div>
               <div className="flex justify-between items-center bg-slate-800/30 px-3 py-2 rounded-lg border border-slate-700/30">
                 <span className="text-xs text-slate-400 font-medium">Errors</span>
                 <span className="text-sm font-mono text-slate-300 font-semibold">0</span>
               </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newCredits, setNewCredits] = useState(100);

  const fetchUsers = async () => {
    try { const { data } = await axios.get("/api/admin/users"); setUsers(data); } catch (e) {} finally { setLoading(false); }
  };
  useEffect(() => { fetchUsers(); }, []);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      await axios.post("/api/admin/users", { username: newUsername, password: newPassword, role: "user", credits: parseInt(newCredits, 10), limits: "standard" });
      toast.success("User created."); setNewUsername(""); setNewPassword(""); fetchUsers();
    } catch (e) { toast.error(formatApiError(e.response?.data?.detail)); }
  };

  const toggleStatus = async (user) => {
    try {
      await axios.patch(`/api/admin/users/${user._id}`, { status: user.status === "active" ? "banned" : "active" });
      fetchUsers();
    } catch (e) {}
  };
  
  const deleteUser = async (userId) => {
    if (!window.confirm("Confirm delete?")) return;
    try { await axios.delete(`/api/admin/users/${userId}`); fetchUsers(); } catch (e) {}
  };

  return (
    <div className="max-w-[1400px] mx-auto space-y-6">
      <h1 className="text-2xl font-semibold text-slate-100">Admin Control Panel</h1>
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-1 bg-[#090b14] border border-slate-800/80 rounded-2xl p-6 shadow-xl h-fit">
          <h3 className="font-medium text-slate-200 mb-4 flex items-center gap-2"><Plus className="w-4 h-4"/> Create User</h3>
          <form onSubmit={handleCreateUser} className="space-y-4">
            <Input value={newUsername} onChange={(e) => setNewUsername(e.target.value)} required placeholder="Username" />
            <Input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required placeholder="Password" />
            <Input type="number" value={newCredits} onChange={(e) => setNewCredits(e.target.value)} min="0" required placeholder="Credits" />
            <Button type="submit" className="w-full">Create</Button>
          </form>
        </div>
        <div className="xl:col-span-2 bg-[#090b14] border border-slate-800/80 rounded-2xl shadow-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-slate-800/80 bg-slate-900/30">
                  <th className="px-6 py-3 text-[11px] uppercase text-slate-500">User</th>
                  <th className="px-6 py-3 text-[11px] uppercase text-slate-500">Status</th>
                  <th className="px-6 py-3 text-[11px] uppercase text-slate-500 text-right">Credits</th>
                  <th className="px-6 py-3 text-[11px] uppercase text-slate-500 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u._id} className="border-b border-slate-800/30 hover:bg-slate-800/20">
                    <td className="px-6 py-4 font-medium text-slate-200">{u.username} <span className="text-[10px] text-slate-500 uppercase ml-2">{u.role}</span></td>
                    <td className="px-6 py-4">
                      <span className={`text-xs font-medium px-2 py-1 rounded-md ${u.status === 'active' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                        {u.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right font-mono text-slate-300">{u.credits?.toLocaleString()}</td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <Button variant="outline" size="sm" onClick={() => toggleStatus(u)}>{u.status === 'active' ? 'Ban' : 'Unban'}</Button>
                      <Button variant="danger" size="sm" onClick={() => deleteUser(u._id)}>Delete</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { user, loading, justLoggedIn, setJustLoggedIn } = useAuth();
  const [transitioning, setTransitioning] = useState(false);

  useEffect(() => {
    if (justLoggedIn) setTransitioning(true);
  }, [justLoggedIn]);

  if (loading) return <div className="min-h-screen bg-[#020617] flex items-center justify-center"><div className="w-6 h-6 border-2 border-slate-800 border-t-slate-200 rounded-full animate-spin"></div></div>;
  if (!user) return <Navigate to="/login" replace />;
  if (adminOnly && user.role !== "admin") return <Navigate to="/app/home" replace />;
  if (transitioning) return <VoidTransition onComplete={() => { setTransitioning(false); setJustLoggedIn(false); }} />;

  return (
    <motion.div initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="w-full h-full">
      {adminOnly ? (
        <div className="min-h-screen flex flex-col z-10 relative bg-[#020617]">
          <header className="h-16 border-b border-slate-800/80 bg-[#020617]/90 px-6 flex items-center justify-between">
            <div className="font-semibold text-slate-100">VeLuX Admin</div>
            <Button variant="outline" size="sm" onClick={() => { axios.post("/api/auth/logout"); window.location.href = "/"; }}>Logout</Button>
          </header>
          <main className="flex-1 p-6">{children}</main>
        </div>
      ) : (
        <AppLayout>{children}</AppLayout>
      )}
    </motion.div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <Toaster theme="dark" toastOptions={{ className: 'rounded-xl border border-slate-800 bg-[#090b14] text-slate-200 font-sans shadow-2xl' }} />
      <BrowserRouter>
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<Navigate to="/app/home" replace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/admin" element={<ProtectedRoute adminOnly><AdminDashboard /></ProtectedRoute>} />
            <Route path="/app/home" element={<ProtectedRoute><HomeTab /></ProtectedRoute>} />
            <Route path="/app/checker" element={<ProtectedRoute><CheckerTab /></ProtectedRoute>} />
            <Route path="/app/proxy" element={<ProtectedRoute><ProxyTab /></ProtectedRoute>} />
            <Route path="/app/settings" element={<ProtectedRoute><SettingsTab /></ProtectedRoute>} />
          </Routes>
        </AnimatePresence>
      </BrowserRouter>
    </AuthProvider>
  );
}