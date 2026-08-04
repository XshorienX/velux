import React, { createContext, useContext, useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";
import { Toaster, toast } from "sonner";
import axios from "axios";
import { AnimatePresence, motion } from "framer-motion";
import { Lock, User, Terminal, ChevronRight, LogOut, Activity, ShieldAlert, Cpu, Plus, CreditCard, ShoppingBag, Code2, Play, Settings as SettingsIcon, Home, Compass, MessageSquare, Globe, Check, Link, Search } from "lucide-react";

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
    className={`flex h-12 w-full rounded-full border border-neutral-800 bg-neutral-900/40 px-5 py-2 text-sm text-neutral-200 placeholder:text-neutral-600 focus-visible:outline-none focus-visible:border-neutral-500 focus-visible:ring-1 focus-visible:ring-neutral-500 transition-all ${className || ""}`}
    {...props}
  />
));

const Textarea = React.forwardRef(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={`flex min-h-[120px] w-full rounded-3xl border border-neutral-800 bg-neutral-900/40 px-5 py-4 text-sm text-neutral-200 placeholder:text-neutral-600 focus-visible:outline-none focus-visible:border-neutral-500 focus-visible:ring-1 focus-visible:ring-neutral-500 transition-all resize-y font-mono ${className || ""}`}
    {...props}
  />
));

const Button = React.forwardRef(({ className, variant = "default", size = "default", ...props }, ref) => {
  const base = "inline-flex items-center justify-center whitespace-nowrap rounded-full font-medium transition-all focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]";
  const variants = {
    default: "bg-white text-black hover:bg-neutral-200 shadow-sm",
    outline: "border border-neutral-800 bg-transparent text-neutral-300 hover:bg-neutral-800/80",
    ghost: "hover:bg-neutral-800/50 text-neutral-400 hover:text-white",
    danger: "bg-red-500/10 text-red-500 hover:bg-red-500/20 border border-red-500/20",
  };
  const sizes = {
    default: "h-12 px-6 py-2 text-sm",
    sm: "h-10 px-4 text-xs",
    icon: "h-12 w-12 text-sm",
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
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="min-h-screen flex items-center justify-center p-4 relative bg-black">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-white/[0.015] rounded-full blur-[100px] pointer-events-none"></div>
      
      <div className="w-full max-w-[400px] bg-[#0A0A0A] border border-neutral-800/80 rounded-[2rem] p-8 shadow-2xl relative z-10">
        <div className="flex flex-col items-center text-center mb-8">
          <div className="h-12 w-12 rounded-2xl bg-neutral-900 border border-neutral-800 flex items-center justify-center mb-5 shadow-lg">
            <Terminal className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-2xl font-semibold text-white tracking-tight">VeLuX System</h1>
          <p className="text-sm text-neutral-500 mt-2">Sign in to access your dashboard.</p>
        </div>
        <form onSubmit={handleLogin} className="space-y-5">
          <div className="space-y-2">
            <label className="text-xs font-medium text-neutral-400 ml-1">Username</label>
            <div className="relative">
              <User className="absolute left-4 top-3.5 h-5 w-5 text-neutral-500" />
              <Input value={username} onChange={e => setUsername(e.target.value)} className="pl-12" required data-testid="login-username" />
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-neutral-400 ml-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-4 top-3.5 h-5 w-5 text-neutral-500" />
              <Input type="password" value={password} onChange={e => setPassword(e.target.value)} className="pl-12" required data-testid="login-password" />
            </div>
          </div>
          <Button type="submit" className="w-full mt-2" disabled={loading} data-testid="login-submit">
            {loading ? "Authenticating..." : "Continue"}
          </Button>
        </form>
      </div>
    </motion.div>
  );
};

const VoidTransition = ({ onComplete }) => {
  useEffect(() => {
    const timer = setTimeout(() => onComplete(), 2500);
    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <motion.div className="fixed inset-0 bg-black z-50 flex items-center justify-center" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <motion.h2 
        className="font-mono text-neutral-400 text-sm tracking-[0.2em]"
        initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: [0, 1, 1, 0], scale: [0.95, 1, 1, 1.05] }}
        transition={{ duration: 2.5, times: [0, 0.2, 0.8, 1], ease: "easeInOut" }}
      >
        Establishing secure connection...
      </motion.h2>
    </motion.div>
  );
};

const AppLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { id: 'home', path: '/app/home', icon: <Home className="w-6 h-6 sm:w-5 sm:h-5" />, label: 'Home' },
    { id: 'checker', path: '/app/checker', icon: <Compass className="w-6 h-6 sm:w-5 sm:h-5" />, label: 'Checker' },
    { id: 'proxy', path: '/app/proxy', icon: <Globe className="w-6 h-6 sm:w-5 sm:h-5" />, label: 'Proxy' },
    { id: 'settings', path: '/app/settings', icon: <SettingsIcon className="w-6 h-6 sm:w-5 sm:h-5" />, label: 'Settings' }
  ];

  return (
    <div className="min-h-screen flex flex-col z-10 relative bg-black">
      <header className="h-16 border-b border-neutral-800/80 bg-black/80 backdrop-blur-md flex items-center justify-between px-4 sm:px-6 sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-neutral-900 border border-neutral-800 flex items-center justify-center">
            <Terminal className="h-4 w-4 text-white" />
          </div>
          <span className="font-semibold text-white tracking-tight text-sm hidden sm:inline">VeLuX</span>
          <span className="px-2 py-0.5 rounded-md bg-neutral-900 border border-neutral-800 text-[10px] uppercase font-mono text-neutral-400 ml-1">
            {user.role}
          </span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-4 mr-2">
            <div className="flex flex-col items-end hidden sm:flex">
              <span className="text-[10px] font-medium text-neutral-500 uppercase tracking-wider">User</span>
              <span className="text-xs text-neutral-300 font-medium">{user.username}</span>
            </div>
            <div className="h-8 w-px bg-neutral-800 hidden sm:block"></div>
            <div className="flex flex-col items-start">
              <span className="text-[10px] font-medium text-neutral-500 uppercase tracking-wider">Credits</span>
              <span className="text-xs text-white font-mono">{user.credits?.toLocaleString() || 0}</span>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={logout} className="h-10 w-10 text-neutral-400">
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </header>

      <main className="flex-1 p-4 md:p-8 lg:p-10 relative z-10 pb-28">
        {children}
      </main>

      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-[24rem] sm:max-w-[28rem]">
        <div className="ios-glass rounded-full p-2 flex items-center justify-between shadow-[0_20px_40px_rgba(0,0,0,0.6)]">
          {navItems.map(item => {
            const isActive = location.pathname === item.path;
            return (
              <button 
                key={item.id}
                onClick={() => navigate(item.path)}
                className={`relative flex flex-col items-center justify-center w-full h-16 sm:h-14 rounded-full transition-all duration-300 ${isActive ? 'text-white' : 'text-neutral-500 hover:text-neutral-300'}`}
              >
                {isActive && (
                  <motion.div layoutId="active-nav" className="absolute inset-0 bg-white/10 rounded-full border border-white/5" transition={{ type: "spring", stiffness: 300, damping: 30 }} />
                )}
                <div className="relative z-10 flex flex-col items-center">
                  <div className={`mb-1 transition-transform ${isActive ? 'scale-110' : ''}`}>{item.icon}</div>
                  <span className="text-[10px] font-medium tracking-wide hidden sm:block">{item.label}</span>
                </div>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  );
};

const HomeTab = () => {
  const { user } = useAuth();
  return (
    <div className="max-w-[1200px] mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-2xl md:text-3xl font-semibold text-white tracking-tight">Home Dashboard</h1>
        <p className="text-neutral-500 mt-1">Welcome back, {user.username}. Here is your system overview.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        <div className="ios-glass-card p-6 rounded-3xl relative overflow-hidden">
          <div className="h-10 w-10 rounded-xl bg-neutral-900 border border-neutral-800 flex items-center justify-center mb-4">
            <Activity className="h-5 w-5 text-white" />
          </div>
          <h3 className="font-medium text-neutral-400 mb-1">Lifetime Checked</h3>
          <div className="text-3xl font-mono text-white font-semibold">{user.total_checked_ccs?.toLocaleString() || 0}</div>
        </div>
        
        <div className="ios-glass-card p-6 rounded-3xl relative overflow-hidden">
          <div className="h-10 w-10 rounded-xl bg-neutral-900 border border-neutral-800 flex items-center justify-center mb-4">
            <Cpu className="h-5 w-5 text-white" />
          </div>
          <h3 className="font-medium text-neutral-400 mb-1">Available Credits</h3>
          <div className="text-3xl font-mono text-white font-semibold">{user.credits?.toLocaleString() || 0}</div>
        </div>

        <div className="ios-glass-card p-6 rounded-3xl relative overflow-hidden sm:col-span-2 lg:col-span-1">
          <div className="h-10 w-10 rounded-xl bg-neutral-900 border border-neutral-800 flex items-center justify-center mb-4">
            <Globe className="h-5 w-5 text-white" />
          </div>
          <h3 className="font-medium text-neutral-400 mb-1">System Health</h3>
          <div className="text-xl text-green-500 mt-2 font-medium flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div> Operational
          </div>
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
  const [stripeSk, setStripeSk] = useState(user.stripe_sk || "");
  const [saving, setSaving] = useState(false);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await axios.patch("/api/auth/me", {
        password: password || undefined,
        telegram_id: telegramId,
        shopify_urls: shopifyUrls,
        stripe_sk: stripeSk
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
        <h1 className="text-2xl md:text-3xl font-semibold text-white tracking-tight">Account Settings</h1>
        <p className="text-neutral-500 mt-1">Manage your credentials, integrations, and default behaviors.</p>
      </div>

      <form onSubmit={handleSave} className="ios-glass-card rounded-3xl p-6 sm:p-8 space-y-8">
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-white border-b border-neutral-800/50 pb-2">Security</h3>
          <div className="space-y-2">
            <label className="text-xs font-medium text-neutral-400">Change Password</label>
            <Input type="password" placeholder="Leave blank to keep current" value={password} onChange={e => setPassword(e.target.value)} />
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-medium text-white border-b border-neutral-800/50 pb-2">Integrations</h3>
          <div className="space-y-2">
            <label className="text-xs font-medium text-neutral-400 flex items-center gap-2"><MessageSquare className="w-3 h-3"/> Telegram ID (For bot notifications)</label>
            <Input placeholder="@username or ID" value={telegramId} onChange={e => setTelegramId(e.target.value)} />
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-medium text-white border-b border-neutral-800/50 pb-2">Defaults</h3>
          <div className="space-y-2">
            <label className="text-xs font-medium text-neutral-400 flex items-center gap-2"><CreditCard className="w-3 h-3"/> Default Stripe Secret Key</label>
            <Input type="password" placeholder="sk_live_..." value={stripeSk} onChange={e => setStripeSk(e.target.value)} />
          </div>
          <div className="space-y-2 mt-4">
            <label className="text-xs font-medium text-neutral-400 flex items-center gap-2"><Link className="w-3 h-3"/> Default Shopify Product URLs</label>
            <Textarea placeholder="https://store.com/products/item-1" value={shopifyUrls} onChange={e => setShopifyUrls(e.target.value)} className="min-h-[100px]" />
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <Button type="submit" disabled={saving} className="w-full sm:w-auto">{saving ? "Saving..." : "Save Settings"}</Button>
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
    try { const { data } = await axios.get("/api/proxies"); setSavedProxies(data); } catch (e) {}
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
    try { await axios.delete(`/api/proxies/${id}`); fetchSaved(); } catch (e) {}
  };

  return (
    <div className="max-w-[1200px] mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-2xl md:text-3xl font-semibold text-white tracking-tight">Proxy Management</h1>
        <p className="text-neutral-500 mt-1">Validated against external APIs before saving.</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
        <div className="ios-glass-card p-6 sm:p-8 rounded-3xl">
          <h2 className="text-lg font-semibold text-white mb-4">Import Nodes</h2>
          <form onSubmit={handleCheck}>
            <Textarea 
              value={proxies} 
              onChange={e => setProxies(e.target.value)} 
              placeholder="192.168.1.1:8080\ngw.proxyrise.com:443:user:pass" 
              className="min-h-[200px] mb-4" 
              data-testid="proxies-textarea"
            />
            <Button type="submit" disabled={checking} className="w-full" data-testid="check-proxies-btn">
              {checking ? "Validating & Saving..." : "Check & Save Proxies"}
            </Button>
          </form>
        </div>
        
        <div className="ios-glass-card rounded-3xl flex flex-col h-[400px]">
          <div className="px-6 py-5 border-b border-neutral-800/50 flex items-center justify-between">
            <h3 className="font-medium text-white">Active Nodes</h3>
            <span className="text-xs text-neutral-500 font-mono">{savedProxies.length} Saved</span>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            <table className="w-full text-left">
              <tbody>
                {savedProxies.map(p => (
                  <tr key={p._id} className="border-b border-neutral-800/30 hover:bg-white/[0.02] group transition-colors">
                    <td className="px-4 py-3 font-mono text-[12px] sm:text-[13px] text-neutral-300 break-all">{p.raw}</td>
                    <td className="px-4 py-3 text-right">
                      <Button variant="ghost" size="sm" className="h-8 px-2 text-red-500/80 hover:text-red-400 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity" onClick={() => handleDelete(p._id)}>Remove</Button>
                    </td>
                  </tr>
                ))}
                {savedProxies.length === 0 && (
                  <tr>
                    <td colSpan="2" className="px-6 py-12 text-center text-neutral-500 text-sm">No proxy nodes saved yet.</td>
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

const formatCard = (line) => {
  const digitsOnly = line.replace(/\D+/g, ' ').trim().split(' ');
  const ccIndex = digitsOnly.findIndex(part => part.length >= 13 && part.length <= 19);
  
  if (ccIndex !== -1 && digitsOnly.length >= ccIndex + 4) {
    return `${digitsOnly[ccIndex]}|${digitsOnly[ccIndex+1]}|${digitsOnly[ccIndex+2]}|${digitsOnly[ccIndex+3]}`;
  }
  
  const parts = line.split(/[\/\:\|\,\s]+/);
  if (parts.length >= 4) {
    return `${parts[0].replace(/\D/g, '')}|${parts[1].replace(/\D/g, '')}|${parts[2].replace(/\D/g, '')}|${parts[3].replace(/\D/g, '')}`;
  }
  return line.trim();
};

const CheckerTab = () => {
  const { user, checkAuth } = useAuth();
  const [activeGateway, setActiveGateway] = useState("stripe");
  
  const [stripeSkType, setStripeSkType] = useState("sk_based");
  const [stripeSk, setStripeSk] = useState("");
  const [stripeCc, setStripeCc] = useState("");
  
  const [shopifySiteType, setShopifySiteType] = useState("own");
  const [shopifyCc, setShopifyCc] = useState("");

  const [running, setRunning] = useState(false);
  const [results, setResults] = useState([]);
  const [stats, setStats] = useState({ approved: 0, declined: 0, errors: 0 });

  // Shopify Tools State
  const [shToolsKeyword, setShToolsKeyword] = useState("donation");
  const [shToolsPages, setShToolsPages] = useState("10");
  const [shToolsPrice, setShToolsPrice] = useState("1-10");
  const [shToolsVerify, setShToolsVerify] = useState(false);
  const [shToolsOutput, setShToolsOutput] = useState([]);
  const [shToolsUrls, setShToolsUrls] = useState([]);
  const [shToolsRunning, setShToolsRunning] = useState(false);

  const gateways = [
    { id: 'stripe', name: 'Stripe', icon: <CreditCard className="w-5 h-5 md:w-4 md:h-4"/>, active: true },
    { id: 'shopify', name: 'Shopify', icon: <ShoppingBag className="w-5 h-5 md:w-4 md:h-4"/>, active: true },
    { id: 'shopify_tools', name: 'Shopify Tools', icon: <Search className="w-5 h-5 md:w-4 md:h-4"/>, active: true },
    { id: 'paypal', name: 'PayPal', icon: <Globe className="w-5 h-5 md:w-4 md:h-4"/>, active: false, soon: true },
    { id: 'adyen', name: 'Adyen', icon: <ShieldAlert className="w-5 h-5 md:w-4 md:h-4"/>, active: false, soon: true }
  ];

  const handleStartChecker = async (e) => {
    e.preventDefault();
    
    let rawCards = activeGateway === 'stripe' ? stripeCc : shopifyCc;
    const initialLines = rawCards.split('\n');
    let validCards = [];
    
    for (const line of initialLines) {
      if (line.trim()) validCards.push(formatCard(line));
    }
    
    if (validCards.length === 0) return toast.error("No valid cards provided.");

    setRunning(true);
    setResults([]);
    setStats({ approved: 0, declined: 0, errors: 0 });
    toast.info("Checker engine initialized. Testing cards...");
    
    let remainingCards = [...validCards];

    for (let i = 0; i < validCards.length; i++) {
      const card = validCards[i];
      const resultId = Date.now() + i;
      
      remainingCards.shift();
      if (activeGateway === 'stripe') setStripeCc(remainingCards.join('\n'));
      else setShopifyCc(remainingCards.join('\n'));

      // Fetch BIN Info from backend API
      let binStr = "";
      try {
         const binRes = await axios.get(`/api/bin/${card.substring(0,6)}`);
         const bData = binRes.data;
         binStr = `${bData.bank?.name?.toUpperCase() || 'UNKNOWN BANK'} | ${bData.country?.alpha2 || 'XX'} | ${(bData.type || 'UNKNOWN').toUpperCase()} | ${(bData.scheme || '').toUpperCase()}`;
      } catch (e) {
         binStr = "UNKNOWN BIN DATA";
      }

      setResults(prev => [{ 
        id: resultId, 
        card, 
        binInfo: binStr, 
        response: "Processing validation...", 
        loading: true, 
        time: new Date().toLocaleTimeString() 
      }, ...prev]);

      try {
        const payload = {
          gateway: activeGateway,
          card: card,
          sk_type: activeGateway === 'stripe' ? stripeSkType : undefined,
          sk: activeGateway === 'stripe' ? stripeSk : undefined,
          site_type: activeGateway === 'shopify' ? shopifySiteType : undefined
        };
        
        const { data } = await axios.post("/api/checker/run", payload);
        
        let isApproved = false;
        let stat = "DECLINED";
        let msg = "";
        let price = "";
        
        if (activeGateway === 'stripe') {
           if (data.status === true && data.result) {
             isApproved = data.result.status?.toLowerCase() === "charged" || data.result.status?.toLowerCase() === "live";
             stat = data.result.status?.toUpperCase() || (isApproved ? "LIVE" : "DECLINED");
           } else if (data.Status) {
             const rawStatus = (data.Status || "").toString().toUpperCase();
             isApproved = rawStatus === "CHARGED" || rawStatus === "LIVE";
             stat = rawStatus;
           } else {
             stat = "UNKNOWN";
           }
           msg = JSON.stringify(data);
           price = data.Price || data.price || "";
        } else {
           if (data.status === true && data.result) {
             isApproved = data.result.status?.toLowerCase() === "charged" || data.result.status?.toLowerCase() === "live";
             stat = data.result.status?.toUpperCase() || (isApproved ? "LIVE" : "DECLINED");
             msg = data.result.message || data.result.decline_code || "Processed";
             price = data.result.price || data.result.amount || "";
           } else if (data.Status || data.status) {
             const rawStatus = (data.Status || data.status).toString().toUpperCase();
             isApproved = rawStatus === "CHARGED" || rawStatus === "LIVE" || rawStatus === "APPROVED";
             stat = rawStatus;
             msg = data.Response || data.message || data.result?.message || "Processed";
             price = data.Price || data.price || data.amount || "";
           } else {
             stat = "UNKNOWN";
             msg = "Unexpected response format";
           }
        }

        setResults(prev => prev.map(r => r.id === resultId ? {
          ...r,
          loading: false,
          isApproved,
          stat,
          msg,
          price
        } : r));
        
        if (isApproved) {
          setStats(prev => ({ ...prev, approved: prev.approved + 1 }));
        } else {
          setStats(prev => ({ ...prev, declined: prev.declined + 1 }));
        }
        
        if (i % 5 === 0) checkAuth();
        
      } catch (err) {
        setResults(prev => prev.map(r => r.id === resultId ? {
          ...r,
          loading: false,
          isApproved: false,
          error: true,
          stat: "ERROR",
          msg: "Network Error or Timeout"
        } : r));
        setStats(prev => ({ ...prev, errors: prev.errors + 1 }));
      }
    }
    
    setRunning(false);
    checkAuth();
    toast.success("Validation sequence complete.");
  };

  const handleStartScraper = async (e) => {
    e.preventDefault();
    setShToolsRunning(true);
    setShToolsOutput([]);
    setShToolsUrls([]);
    const limit = parseInt(shToolsPages, 10);
    
    let allStores = [];
    setShToolsOutput(p => [...p, `Starting scraping for keyword '${shToolsKeyword}' up to page ${limit}...`]);
    
    for (let page = 1; page <= limit; page++) {
      try {
        setShToolsOutput(p => [...p, `Fetching page ${page}...`]);
        const res = await axios.get(`/api/shopify_tools/stores?keyword=${shToolsKeyword}&page=${page}`);
        if (res.data.stores && res.data.stores.length > 0) {
          allStores = [...allStores, ...res.data.stores];
          setShToolsOutput(p => [...p, `Page ${page}: found ${res.data.stores.length} stores`]);
        }
      } catch (e) {
        setShToolsOutput(p => [...p, `Page ${page}: error occurred`]);
      }
    }
    
    setShToolsOutput(p => [...p, `Total unique stores collected: ${new Set(allStores).size}`]);
    
    let [min_p, max_p] = shToolsPrice.split('-').map(Number);
    if (!max_p) max_p = 10;

    setShToolsOutput(p => [...p, `Extracting products in price range $${min_p} - $${max_p}...`]);
    try {
      const prodRes = await axios.post(`/api/shopify_tools/products`, {
        stores: Array.from(new Set(allStores)),
        min_price: min_p,
        max_price: max_p
      });
      let prods = prodRes.data.products || [];
      setShToolsOutput(p => [...p, `Found ${prods.length} products matching criteria.`]);
      
      if (shToolsVerify && prods.length > 0) {
        setShToolsOutput(p => [...p, `Verifying ${prods.length} URLs via checkout API...`]);
        let verified = [];
        for (const p_url of prods) {
          try {
            const vRes = await axios.post("/api/checker/run", {
              gateway: 'shopify',
              card: '4118101051591193|02|30|646',
              site_type: 'own', 
              sk_type: null,
              sk: null,
              product_url: p_url
            });
            const vMsg = (vRes.data.message || vRes.data.Response || JSON.stringify(vRes.data)).toUpperCase();
            if (vMsg.includes("CAPTCHA_REQUIRED") || vMsg.includes("DECLINE")) {
              verified.push(p_url);
              setShToolsOutput(p => [...p, `[VALID] ${p_url}`]);
            }
          } catch(e) {}
        }
        prods = verified;
        setShToolsOutput(p => [...p, `Verification complete. ${prods.length} valid URLs kept.`]);
      }
      
      setShToolsUrls(prods);
    } catch (e) {
      setShToolsOutput(p => [...p, `Error extracting products.`]);
    }
    
    setShToolsRunning(false);
  };

  const saveShUrlsToDefault = async () => {
    if (shToolsUrls.length === 0) return;
    try {
      const current = user.shopify_urls ? user.shopify_urls + '\n' : '';
      await axios.patch("/api/auth/me", {
        shopify_urls: current + shToolsUrls.join('\n')
      });
      toast.success("Added URLs to your Default Shopify Product URLs");
      checkAuth();
    } catch (e) { toast.error("Failed to save"); }
  };

  return (
    <div className="max-w-[1400px] mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-semibold text-white tracking-tight">Validation Engine</h1>
          <p className="text-neutral-500 mt-1">Select a gateway and input payloads to begin validation.</p>
        </div>
        
        <div className="flex flex-wrap items-center p-1 bg-neutral-900/50 border border-neutral-800/80 rounded-2xl w-fit">
          {gateways.map(gw => (
            <button 
              key={gw.id}
              onClick={() => { if (!running && !shToolsRunning && gw.active) setActiveGateway(gw.id); }}
              disabled={running || shToolsRunning || !gw.active}
              className={`flex items-center gap-1.5 py-3 px-4 text-base md:text-sm md:py-2 md:px-3 font-medium rounded-xl transition-all whitespace-nowrap ${
                activeGateway === gw.id 
                  ? 'bg-neutral-800 text-white shadow-sm' 
                  : gw.active && !running && !shToolsRunning
                    ? 'text-neutral-500 hover:text-neutral-300 hover:bg-white/5' 
                    : 'text-neutral-600 opacity-50 cursor-not-allowed'
              }`}
            >
              {gw.icon}
              <span>{gw.name}</span>
              {gw.soon && <span className="text-[9px] uppercase tracking-wider bg-black border border-neutral-800 px-1.5 py-0.5 rounded-md ml-1">Soon</span>}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 lg:gap-8">
        <div className="lg:col-span-3 space-y-6">
          <div className="ios-glass-card rounded-3xl overflow-hidden min-h-[450px]">
            <div className="p-6 md:p-8">
              <AnimatePresence mode="wait">
                
                {activeGateway === 'stripe' && (
                  <motion.form key="stripe" initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} onSubmit={handleStartChecker} className="space-y-6">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-indigo-500/10 rounded-2xl"><CreditCard className="w-6 h-6 text-indigo-400"/></div>
                        <h2 className="text-xl font-medium text-neutral-200">Stripe Integration</h2>
                      </div>
                      <div className="flex items-center gap-2 bg-neutral-900 border border-neutral-800 rounded-xl p-1">
                        <button type="button" onClick={() => setStripeSkType("sk_based")} className={`px-4 py-2 text-xs font-medium rounded-lg transition-all ${stripeSkType === "sk_based" ? "bg-neutral-800 text-white shadow-sm" : "text-neutral-500 hover:text-neutral-300"}`}>SK-Based</button>
                        <button type="button" onClick={() => setStripeSkType("non_sk")} className={`px-4 py-2 text-xs font-medium rounded-lg transition-all ${stripeSkType === "non_sk" ? "bg-neutral-800 text-white shadow-sm" : "text-neutral-500 hover:text-neutral-300"}`}>Non-SK Based</button>
                      </div>
                    </div>
                    {stripeSkType === 'sk_based' && !user.stripe_sk && (
                      <div className="space-y-2">
                        <label className="text-xs font-medium text-neutral-400 ml-1">Secret Key</label>
                        <Input type="password" placeholder="sk_live_..." value={stripeSk} onChange={(e) => setStripeSk(e.target.value)} required disabled={running} />
                      </div>
                    )}
                    {stripeSkType === 'sk_based' && user.stripe_sk && (
                       <div className="bg-white/[0.03] border border-white/[0.05] rounded-2xl px-5 py-4 flex items-center justify-between">
                         <div>
                           <span className="text-sm font-medium text-neutral-300 block mb-1">Using Saved Default SK Key</span>
                           <span className="text-xs text-neutral-500">Configured in your account settings.</span>
                         </div>
                         <Check className="w-5 h-5 text-green-500" />
                       </div>
                    )}
                    {stripeSkType === 'non_sk' && (
                       <div className="bg-white/[0.03] border border-white/[0.05] rounded-2xl px-5 py-4 flex items-center justify-between">
                         <div>
                           <span className="text-sm font-medium text-neutral-300 block mb-1">Using Global Admin Configured Secret Key</span>
                           <span className="text-xs text-neutral-500">Admin managed key.</span>
                         </div>
                         <Check className="w-5 h-5 text-green-500" />
                       </div>
                    )}
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-neutral-400 ml-1">Card Payloads</label>
                      <Textarea placeholder="4111...|12|25|123" value={stripeCc} onChange={(e) => setStripeCc(e.target.value)} className="min-h-[200px]" required disabled={running} />
                    </div>
                    <Button type="submit" disabled={running} className="w-full gap-2 mt-2">
                      {running ? <><div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></div> Validating...</> : <><Play className="w-4 h-4" /> Start Validation</>}
                    </Button>
                  </motion.form>
                )}

                {activeGateway === 'shopify' && (
                  <motion.form key="shopify" initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} onSubmit={handleStartChecker} className="space-y-6">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-green-500/10 rounded-2xl"><ShoppingBag className="w-6 h-6 text-green-400"/></div>
                        <h2 className="text-xl font-medium text-neutral-200">Shopify Gateway</h2>
                      </div>
                      <div className="flex items-center gap-2 bg-neutral-900 border border-neutral-800 rounded-xl p-1">
                        <button type="button" onClick={() => setShopifySiteType("own")} className={`px-4 py-2 text-xs font-medium rounded-lg transition-all ${shopifySiteType === "own" ? "bg-neutral-800 text-white shadow-sm" : "text-neutral-500 hover:text-neutral-300"}`}>Own Site</button>
                        <button type="button" onClick={() => setShopifySiteType("inbuilt")} className={`px-4 py-2 text-xs font-medium rounded-lg transition-all ${shopifySiteType === "inbuilt" ? "bg-neutral-800 text-white shadow-sm" : "text-neutral-500 hover:text-neutral-300"}`}>Inbuilt Site</button>
                      </div>
                    </div>
                    {shopifySiteType === 'own' && (
                       <div className="bg-white/[0.03] border border-white/[0.05] rounded-2xl px-5 py-4 flex items-center justify-between">
                         <div>
                           <span className="text-sm font-medium text-neutral-300 block mb-1">Using Saved Personal Product URLs</span>
                           <span className="text-xs text-neutral-500">Configured in your account settings.</span>
                         </div>
                         <Check className="w-5 h-5 text-green-500" />
                       </div>
                    )}
                    {shopifySiteType === 'inbuilt' && (
                       <div className="bg-white/[0.03] border border-white/[0.05] rounded-2xl px-5 py-4 flex items-center justify-between">
                         <div>
                           <span className="text-sm font-medium text-neutral-300 block mb-1">Using Global Admin Configured Product URLs</span>
                           <span className="text-xs text-neutral-500">Admin managed list.</span>
                         </div>
                         <Check className="w-5 h-5 text-green-500" />
                       </div>
                    )}
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-neutral-400 ml-1">Card Payloads</label>
                      <Textarea placeholder="4111...|12|25|123" value={shopifyCc} onChange={(e) => setShopifyCc(e.target.value)} className="min-h-[200px]" required disabled={running} />
                    </div>
                    <Button type="submit" disabled={running} className="w-full gap-2 mt-2">
                      {running ? <><div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></div> Validating...</> : <><Play className="w-4 h-4" /> Start Validation</>}
                    </Button>
                  </motion.form>
                )}

                {activeGateway === 'shopify_tools' && (
                  <motion.form key="shopify_tools" initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} onSubmit={handleStartScraper} className="space-y-6">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-2 bg-blue-500/10 rounded-2xl"><Search className="w-6 h-6 text-blue-400"/></div>
                      <h2 className="text-xl font-medium text-neutral-200">Shopify Product Scraper</h2>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <label className="text-xs font-medium text-neutral-400 ml-1">Keyword</label>
                        <Input value={shToolsKeyword} onChange={e => setShToolsKeyword(e.target.value)} required disabled={shToolsRunning} />
                      </div>
                      <div className="space-y-2">
                        <label className="text-xs font-medium text-neutral-400 ml-1">Pages to Scrape</label>
                        <select value={shToolsPages} onChange={e => setShToolsPages(e.target.value)} disabled={shToolsRunning} className="flex h-12 w-full rounded-full border border-neutral-800 bg-neutral-900/40 px-5 py-2 text-sm text-neutral-200 focus-visible:outline-none focus-visible:border-neutral-500">
                          <option value="10">10 Pages</option>
                          <option value="50">50 Pages</option>
                          <option value="100">100 Pages</option>
                        </select>
                      </div>
                      <div className="space-y-2">
                        <label className="text-xs font-medium text-neutral-400 ml-1">Price Range</label>
                        <select value={shToolsPrice} onChange={e => setShToolsPrice(e.target.value)} disabled={shToolsRunning} className="flex h-12 w-full rounded-full border border-neutral-800 bg-neutral-900/40 px-5 py-2 text-sm text-neutral-200 focus-visible:outline-none focus-visible:border-neutral-500">
                          <option value="1-10">$1 - $10</option>
                          <option value="10-15">$10 - $15</option>
                          <option value="1-20">$1 - $20</option>
                        </select>
                      </div>
                    </div>
                    <label className="flex items-center gap-3 cursor-pointer">
                      <input type="checkbox" checked={shToolsVerify} onChange={e => setShToolsVerify(e.target.checked)} disabled={shToolsRunning} className="w-5 h-5 rounded border-neutral-800 bg-neutral-900" />
                      <span className="text-sm font-medium text-neutral-300">Verify URLs (Filters dead checkouts via Shopify API)</span>
                    </label>
                    <Button type="submit" disabled={shToolsRunning} className="w-full gap-2 mt-2">
                      {shToolsRunning ? <><div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></div> Scraping & Analyzing...</> : <><Search className="w-4 h-4" /> Start Scraping</>}
                    </Button>

                    {shToolsOutput.length > 0 && (
                      <div className="mt-6 p-4 rounded-2xl border border-neutral-800/50 bg-black/50 font-mono text-[11px] text-neutral-400 space-y-1 h-[200px] overflow-y-auto">
                        {shToolsOutput.map((l, i) => <div key={i}>{l}</div>)}
                      </div>
                    )}
                    
                    {shToolsUrls.length > 0 && !shToolsRunning && (
                      <div className="mt-4">
                        <h4 className="text-sm font-medium text-white mb-2">Generated URLs</h4>
                        <Textarea value={shToolsUrls.join('\n')} readOnly className="min-h-[150px] mb-3" />
                        <Button type="button" onClick={saveShUrlsToDefault} className="w-full bg-neutral-800 text-white hover:bg-neutral-700">Save to Default Configuration</Button>
                      </div>
                    )}
                  </motion.form>
                )}
              </AnimatePresence>
            </div>
          </div>

          {activeGateway !== 'shopify_tools' && results.length > 0 && (
            <div className="ios-glass-card rounded-3xl p-6">
              <h3 className="text-sm font-medium text-white mb-4">Terminal Output</h3>
              <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 font-mono text-[11px] sm:text-xs">
                {results.map((r, i) => (
                  <div key={r.id || i} className={`p-4 rounded-2xl border flex flex-col gap-2 ${
                    r.loading ? 'bg-neutral-800/30 border-neutral-700/30 text-neutral-400' :
                    r.isApproved ? 'bg-green-500/10 border-green-500/20 text-green-400' : 
                    r.error ? 'bg-neutral-800/50 border-neutral-700/50 text-neutral-400' : 
                    'bg-red-500/10 border-red-500/20 text-red-400'
                  }`}>
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-white/5 pb-2 mb-1 gap-2">
                      <div className="flex items-center gap-2">
                        <span className="opacity-50">[{r.time}]</span>
                        <span className="font-semibold text-white tracking-widest">{r.card}</span>
                      </div>
                      {r.binInfo && (
                        <div className="text-[10px] text-neutral-400 font-sans tracking-wide">
                          {r.binInfo}
                        </div>
                      )}
                    </div>
                    {r.loading ? (
                      <div className="flex items-center gap-2 text-neutral-400">
                        <div className="w-3 h-3 border-2 border-neutral-500 border-t-transparent rounded-full animate-spin"></div>
                        <span>Processing validation...</span>
                      </div>
                    ) : (
                      <div className="flex flex-col gap-0.5 mt-1 break-words whitespace-pre-wrap max-w-full">
                        <div className="text-neutral-200 break-words w-full"><span className="opacity-50 mr-2 shrink-0">Status:</span> <span className="break-all">{r.stat}</span></div>
                        <div className="text-neutral-200 break-words w-full"><span className="opacity-50 mr-2 shrink-0">Response:</span> <span className="break-all whitespace-pre-wrap">{r.msg}</span></div>
                        {r.price && <div className="text-neutral-200 break-words w-full"><span className="opacity-50 mr-2 shrink-0">Price:</span> <span className="break-all">{r.price}</span></div>}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Dashboard Side Widget */}
        <div className="lg:col-span-1 space-y-6">
          <div className="ios-glass-card p-6 rounded-3xl flex flex-col items-center text-center justify-center min-h-[200px] relative overflow-hidden">
             <div className="absolute top-0 right-0 p-4 opacity-5"><Activity className="w-32 h-32 text-white"/></div>
             <div className="relative z-10">
               <div className="text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-2">Lifetime Checked</div>
               <div className="text-5xl font-mono font-bold text-white">{user.total_checked_ccs?.toLocaleString() || 0}</div>
             </div>
          </div>

          <div className="ios-glass-card p-6 rounded-3xl">
             <h3 className="font-medium text-neutral-300 mb-4 text-sm">Session Results</h3>
             <div className="space-y-3">
               <div className="flex justify-between items-center bg-white/[0.02] px-3 py-2 rounded-xl border border-white/[0.05]">
                 <span className="text-xs text-neutral-400 font-medium flex items-center gap-1.5"><Check className="w-3 h-3 text-green-500"/> Approved</span>
                 <span className="text-sm font-mono text-white font-semibold">{stats.approved}</span>
               </div>
               <div className="flex justify-between items-center bg-white/[0.02] px-3 py-2 rounded-xl border border-white/[0.05]">
                 <span className="text-xs text-neutral-400 font-medium flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-red-500"></span> Declined</span>
                 <span className="text-sm font-mono text-white font-semibold">{stats.declined}</span>
               </div>
               <div className="flex justify-between items-center bg-white/[0.02] px-3 py-2 rounded-xl border border-white/[0.05]">
                 <span className="text-xs text-neutral-400 font-medium flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-neutral-600"></span> Errors</span>
                 <span className="text-sm font-mono text-white font-semibold">{stats.errors}</span>
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

  const { user, checkAuth } = useAuth();
  const [globalSk, setGlobalSk] = useState("");
  const [globalUrls, setGlobalUrls] = useState("");

  const fetchUsers = async () => {
    try { const { data } = await axios.get("/api/admin/users"); setUsers(data); } catch (e) {} finally { setLoading(false); }
  };
  
  useEffect(() => { 
    fetchUsers(); 
    if (user) {
      setGlobalSk(user.stripe_sk || "");
      setGlobalUrls(user.shopify_urls || "");
    }
  }, [user]);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      await axios.post("/api/admin/users", { username: newUsername, password: newPassword, role: "user", credits: parseInt(newCredits, 10), limits: "standard" });
      toast.success("User created."); setNewUsername(""); setNewPassword(""); fetchUsers();
    } catch (e) { toast.error(formatApiError(e.response?.data?.detail)); }
  };

  const handleSaveGlobal = async (e) => {
    e.preventDefault();
    try {
      await axios.patch("/api/auth/me", { stripe_sk: globalSk, shopify_urls: globalUrls });
      toast.success("Global config updated");
      checkAuth();
    } catch (e) { toast.error(formatApiError(e.response?.data?.detail)); }
  };

  const toggleStatus = async (u) => {
    try {
      await axios.patch(`/api/admin/users/${u._id}`, { status: u.status === "active" ? "banned" : "active" });
      fetchUsers();
    } catch (e) {}
  };
  
  const deleteUser = async (userId) => {
    if (!window.confirm("Confirm delete?")) return;
    try { await axios.delete(`/api/admin/users/${userId}`); fetchUsers(); } catch (e) {}
  };

  return (
    <div className="max-w-[1400px] mx-auto space-y-6">
      <h1 className="text-2xl font-semibold text-white">Admin Control Panel</h1>
      
      <div className="ios-glass-card rounded-3xl p-6 mb-6">
        <h3 className="font-medium text-neutral-200 mb-4">Global API Configuration</h3>
        <form onSubmit={handleSaveGlobal} className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-xs font-medium text-neutral-400">Global Stripe SK (For Non-SK Based)</label>
            <Input type="password" value={globalSk} onChange={e => setGlobalSk(e.target.value)} placeholder="sk_live_..." />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-neutral-400">Global Shopify URLs (For Inbuilt Site)</label>
            <Textarea value={globalUrls} onChange={e => setGlobalUrls(e.target.value)} placeholder="https://store.com/products/1" className="min-h-[100px]" />
          </div>
          <div className="md:col-span-2">
            <Button type="submit">Save Global Config</Button>
          </div>
        </form>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-1 ios-glass-card rounded-3xl p-6 h-fit">
          <h3 className="font-medium text-neutral-200 mb-4 flex items-center gap-2"><Plus className="w-4 h-4"/> Create User</h3>
          <form onSubmit={handleCreateUser} className="space-y-4">
            <Input value={newUsername} onChange={(e) => setNewUsername(e.target.value)} required placeholder="Username" />
            <Input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required placeholder="Password" />
            <Input type="number" value={newCredits} onChange={(e) => setNewCredits(e.target.value)} min="0" required placeholder="Credits" />
            <Button type="submit" className="w-full">Create Account</Button>
          </form>
        </div>
        <div className="xl:col-span-2 ios-glass-card rounded-3xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-neutral-800/50 bg-white/[0.02]">
                  <th className="px-6 py-4 text-[11px] uppercase text-neutral-500">User</th>
                  <th className="px-6 py-4 text-[11px] uppercase text-neutral-500">Status</th>
                  <th className="px-6 py-4 text-[11px] uppercase text-neutral-500 text-right">Credits</th>
                  <th className="px-6 py-4 text-[11px] uppercase text-neutral-500 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u._id} className="border-b border-neutral-800/30 hover:bg-white/[0.02]">
                    <td className="px-6 py-4 font-medium text-neutral-200">{u.username} <span className="text-[10px] text-neutral-500 uppercase ml-2">{u.role}</span></td>
                    <td className="px-6 py-4">
                      <span className={`text-xs font-medium px-2.5 py-1 rounded-lg ${u.status === 'active' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                        {u.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right font-mono text-neutral-300">{u.credits?.toLocaleString()}</td>
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

  if (loading) return <div className="min-h-screen bg-black flex items-center justify-center"><div className="w-6 h-6 border-2 border-neutral-800 border-t-neutral-200 rounded-full animate-spin"></div></div>;
  if (!user) return <Navigate to="/login" replace />;
  if (adminOnly && user.role !== "admin") return <Navigate to="/app/home" replace />;
  if (transitioning) return <VoidTransition onComplete={() => { setTransitioning(false); setJustLoggedIn(false); }} />;

  return (
    <motion.div initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="w-full h-full">
      {adminOnly ? (
        <div className="min-h-screen flex flex-col z-10 relative bg-black">
          <header className="h-16 border-b border-neutral-800/80 bg-black/90 px-6 flex items-center justify-between sticky top-0 z-40">
            <div className="font-semibold text-white">VeLuX Admin Panel</div>
            <Button variant="outline" size="sm" onClick={() => { axios.post("/api/auth/logout"); window.location.href = "/"; }}>Logout</Button>
          </header>
          <main className="flex-1 p-6 lg:p-10">{children}</main>
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
      <Toaster theme="dark" toastOptions={{ className: 'rounded-2xl border border-neutral-800/50 bg-[#0A0A0A]/90 backdrop-blur-xl text-neutral-200 font-sans shadow-2xl' }} />
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