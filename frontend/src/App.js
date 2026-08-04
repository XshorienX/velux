import React, { createContext, useContext, useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { Toaster, toast } from "sonner";
import axios from "axios";
import { AnimatePresence, motion } from "framer-motion";
import { Lock, User, Terminal, ChevronRight, LogOut, Search, Activity, ShieldAlert, Cpu } from "lucide-react";

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

// Components
const Input = React.forwardRef(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={`flex h-10 w-full rounded-none border border-zinc-800/80 bg-gradient-to-b from-[#0a0a0a] to-[#000000] px-3 py-2 text-sm text-white focus-visible:outline-none focus-visible:border-zinc-500 focus-visible:ring-1 focus-visible:ring-zinc-500 disabled:cursor-not-allowed disabled:opacity-50 transition-colors shadow-[inset_0_2px_10px_rgba(0,0,0,0.5)] ${className || ""}`}
    {...props}
  />
));

const Button = React.forwardRef(({ className, variant = "default", size = "default", ...props }, ref) => {
  const base = "inline-flex items-center justify-center whitespace-nowrap rounded-none text-sm font-bold transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-500 disabled:pointer-events-none disabled:opacity-50 uppercase tracking-widest active:scale-95";
  const variants = {
    default: "bg-gradient-to-b from-zinc-200 to-zinc-400 text-black hover:from-white hover:to-zinc-300 border-transparent shadow-[0_0_15px_rgba(255,255,255,0.1)]",
    outline: "border border-zinc-700 bg-gradient-to-b from-[#111] to-black text-zinc-300 hover:text-white hover:border-zinc-500 shadow-lg",
    ghost: "hover:bg-white/5 text-zinc-400 hover:text-white",
  };
  const sizes = {
    default: "h-10 px-4 py-2",
    sm: "h-9 rounded-md px-3",
    lg: "h-11 rounded-md px-8",
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
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.5 }}
      className="min-h-screen flex items-center justify-center p-4 relative z-10"
    >
      <div className="w-full max-w-md glass-panel p-8 md:p-12 relative overflow-hidden">
        {/* Decorative corner accents */}
        <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-zinc-600"></div>
        <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-zinc-600"></div>
        <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-zinc-600"></div>
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-zinc-600"></div>
        
        <div className="mb-10 text-left space-y-2">
          <h1 className="text-4xl md:text-5xl tracking-tighter font-black uppercase font-mono bg-gradient-to-b from-white via-zinc-400 to-zinc-700 bg-clip-text text-transparent pb-1">VeLuX</h1>
          <p className="text-xs tracking-[0.2em] uppercase font-bold text-zinc-600">Ultimate Checker Protocol</p>
        </div>
        
        <form onSubmit={handleLogin} className="space-y-6">
          <div className="space-y-2">
            <label className="text-xs tracking-[0.2em] uppercase font-bold text-zinc-500">Username</label>
            <div className="relative">
              <User className="absolute left-3 top-3 h-4 w-4 text-zinc-600" />
              <Input 
                value={username} 
                onChange={(e) => setUsername(e.target.value)} 
                className="pl-10" 
                placeholder="Enter identifier..." 
                data-testid="login-username"
                required
              />
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-xs tracking-[0.2em] uppercase font-bold text-zinc-500">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-4 w-4 text-zinc-600" />
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
            className="w-full mt-4 group" 
            disabled={loading}
            data-testid="login-submit"
          >
            {loading ? "Authenticating..." : "Initialize Sequence"}
            <ChevronRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
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
    }, 4500);
    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <motion.div 
      className="fixed inset-0 bg-black z-50 flex items-center justify-center overflow-hidden"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div 
        className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_#0a0a0a_0%,_#000000_100%)] bg-cover bg-center"
        initial={{ scale: 1, opacity: 0 }}
        animate={{ scale: 1.2, opacity: [0, 1, 0] }}
        transition={{ duration: 4.5, ease: "easeInOut" }}
      />
      <motion.h2 
        className="font-mono uppercase tracking-[0.5em] text-sm md:text-xl relative z-10 bg-gradient-to-b from-white via-zinc-400 to-zinc-700 bg-clip-text text-transparent"
        initial={{ opacity: 0, letterSpacing: "0.2em", filter: "blur(10px)" }}
        animate={{ opacity: [0, 1, 1, 0], letterSpacing: "1em", filter: ["blur(10px)", "blur(0px)", "blur(0px)", "blur(10px)"] }}
        transition={{ duration: 4, times: [0, 0.4, 0.8, 1], ease: "easeInOut" }}
      >
        Welcome to NetherWorld......
      </motion.h2>
    </motion.div>
  );
};

const DashboardLayout = ({ children, title }) => {
  const { user, logout } = useAuth();
  
  return (
    <div className="min-h-screen flex flex-col z-10 relative">
      <header className="h-16 border-b border-zinc-800/80 bg-gradient-to-b from-[#0a0a0a]/90 to-[#000000]/80 backdrop-blur-xl flex items-center justify-between px-6 sticky top-0 z-40 shadow-[0_10px_30px_rgba(0,0,0,0.8)]">
        <div className="flex items-center gap-4">
          <Terminal className="h-5 w-5 text-zinc-300" />
          <h1 className="font-mono text-xl font-bold uppercase tracking-widest bg-gradient-to-r from-white to-zinc-500 bg-clip-text text-transparent">
            VeLuX<span className="text-zinc-600 text-sm ml-2">[{user.role}]</span>
          </h1>
        </div>
        <div className="flex items-center gap-6">
          <div className="text-xs font-mono text-zinc-400 hidden md:block">
            <span className="text-zinc-600 mr-2">ID:</span>{user.username}
          </div>
          <div className="text-xs font-mono text-zinc-400 hidden md:block">
            <span className="text-zinc-600 mr-2">CREDITS:</span>{user.credits?.toLocaleString()}
          </div>
          <Button variant="ghost" size="icon" onClick={logout} data-testid="logout-btn">
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </header>
      <main className="flex-1 p-6 md:p-12 relative z-10">
        <div className="max-w-7xl mx-auto space-y-8">
          <div className="flex items-center gap-4 pb-4 border-b border-zinc-800/60">
            <h2 className="text-2xl font-mono uppercase tracking-widest bg-gradient-to-r from-white to-zinc-500 bg-clip-text text-transparent">{title}</h2>
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
      toast.success("User initialized");
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
      toast.success(`User status updated to ${newStatus}`);
      fetchUsers();
    } catch (e) {
      toast.error("Failed to update status");
    }
  };
  
  const deleteUser = async (userId) => {
    if (!window.confirm("Confirm deletion of entity?")) return;
    try {
      await axios.delete(`/api/admin/users/${userId}`);
      toast.success("User erased");
      fetchUsers();
    } catch (e) {
      toast.error("Failed to delete user");
    }
  };

  return (
    <DashboardLayout title="System Administration">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Create User Panel */}
        <div className="lg:col-span-1">
          <div className="glass-panel p-6">
            <h3 className="text-sm tracking-[0.2em] uppercase font-bold text-zinc-400 mb-6 flex items-center">
              <User className="mr-2 h-4 w-4" /> Initialize Entity
            </h3>
            <form onSubmit={handleCreateUser} className="space-y-4">
              <div className="space-y-2">
                <label className="text-xs text-zinc-500 uppercase font-bold tracking-widest">Identifier</label>
                <Input value={newUsername} onChange={(e) => setNewUsername(e.target.value)} required data-testid="create-user-username" />
              </div>
              <div className="space-y-2">
                <label className="text-xs text-zinc-500 uppercase font-bold tracking-widest">Keyphrase</label>
                <Input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required data-testid="create-user-password" />
              </div>
              <div className="space-y-2">
                <label className="text-xs text-zinc-500 uppercase font-bold tracking-widest">Initial Credits</label>
                <Input type="number" value={newCredits} onChange={(e) => setNewCredits(e.target.value)} min="0" required />
              </div>
              <Button type="submit" className="w-full mt-2" data-testid="create-user-submit">Deploy</Button>
            </form>
          </div>
        </div>

        {/* Users List */}
        <div className="lg:col-span-2">
          <div className="glass-panel overflow-hidden">
            <div className="p-4 border-b border-zinc-800/80 bg-gradient-to-b from-[#111111] to-transparent">
              <h3 className="text-sm tracking-[0.2em] uppercase font-bold text-zinc-400">Entity Matrix</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-zinc-800/50">
                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-zinc-500">Identifier</th>
                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-zinc-500">Role</th>
                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-zinc-500">Status</th>
                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-zinc-500 text-right">Credits</th>
                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-zinc-500 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="font-mono text-sm">
                  {users.map(u => (
                    <tr key={u._id} className="border-b border-zinc-800/30 hover:bg-white/[0.02] transition-colors">
                      <td className="px-6 py-4 text-zinc-300">{u.username}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-[10px] uppercase tracking-widest border bg-black/40 ${u.role === 'admin' ? 'border-zinc-500 text-zinc-300' : 'border-zinc-800 text-zinc-500'}`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`flex items-center gap-2 ${u.status === 'active' ? 'text-zinc-400' : 'text-red-500'}`}>
                          <div className={`w-2 h-2 rounded-none ${u.status === 'active' ? 'bg-zinc-400 shadow-[0_0_5px_rgba(255,255,255,0.5)]' : 'bg-red-500 shadow-[0_0_5px_rgba(255,0,0,0.5)]'}`}></div>
                          {u.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right text-zinc-400">{u.credits?.toLocaleString()}</td>
                      <td className="px-6 py-4 text-right space-x-2">
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className={`text-xs h-7 px-2 ${u.status === 'banned' ? 'border-zinc-600 text-zinc-300' : 'border-red-900/50 text-red-500/80 hover:text-red-400'}`}
                          onClick={() => toggleStatus(u)}
                          data-testid={`toggle-status-${u._id}`}
                        >
                          {u.status === 'active' ? 'BAN' : 'UNBAN'}
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="text-xs h-7 px-2 border-red-900/30 text-red-800 hover:border-red-900 hover:text-red-600"
                          onClick={() => deleteUser(u._id)}
                          data-testid={`delete-user-${u._id}`}
                        >
                          ERASE
                        </Button>
                      </td>
                    </tr>
                  ))}
                  {users.length === 0 && !loading && (
                    <tr>
                      <td colSpan="5" className="px-6 py-8 text-center text-zinc-600 italic">No entities found in matrix.</td>
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

const UserDashboard = () => {
  return (
    <DashboardLayout title="Checker Protocol">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="glass-panel p-6 border-l-2 border-l-zinc-500">
          <Activity className="h-6 w-6 text-zinc-400 mb-4" />
          <h3 className="font-mono text-xl text-zinc-200 mb-2">Protocol Status</h3>
          <p className="text-zinc-500 text-sm">Main AI key checker module is currently offline. Awaiting sequence initialization from the administrator.</p>
        </div>
        <div className="glass-panel p-6 border-l-2 border-l-zinc-800 opacity-60">
          <Cpu className="h-6 w-6 text-zinc-600 mb-4" />
          <h3 className="font-mono text-xl text-zinc-500 mb-2">Proxy Node</h3>
          <p className="text-zinc-600 text-sm">COMING SOON. High-speed HTTP/SOCKS5 validation engine.</p>
        </div>
        <div className="glass-panel p-6 border-l-2 border-l-zinc-800 opacity-60">
          <ShieldAlert className="h-6 w-6 text-zinc-600 mb-4" />
          <h3 className="font-mono text-xl text-zinc-500 mb-2">AI API Vault</h3>
          <p className="text-zinc-600 text-sm">COMING SOON. Multi-provider key validation and quota checking.</p>
        </div>
      </div>
      
      <div className="mt-8 glass-panel p-8 border border-zinc-800 flex flex-col items-center justify-center text-center py-24 bg-gradient-to-t from-[#0a0a0a] to-[#000000]">
        <Search className="h-12 w-12 text-zinc-700 mb-6 drop-shadow-[0_0_15px_rgba(255,255,255,0.05)]" />
        <h2 className="text-2xl font-mono bg-gradient-to-b from-zinc-300 to-zinc-600 bg-clip-text text-transparent uppercase tracking-widest mb-2">Awaiting Deployment</h2>
        <p className="text-zinc-600 max-w-md">The Ultimate Checker UI is currently being forged in the NetherWorld. Check back later for the next update.</p>
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

  if (loading) return <div className="min-h-screen bg-[#050505] flex items-center justify-center"><div className="w-8 h-8 border-2 border-zinc-600 border-t-zinc-200 animate-spin"></div></div>;
  
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
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="w-full h-full"
    >
      {children}
    </motion.div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen text-white selection:bg-zinc-800 selection:text-white font-sans relative bg-gradient-to-br from-[#121212] via-[#050505] to-[#000000]">
        <div className="bg-noise" />
        <Toaster theme="dark" toastOptions={{ className: 'rounded-none border-zinc-800/80 bg-gradient-to-b from-[#111111] to-black text-zinc-300 font-mono uppercase tracking-wider text-xs shadow-2xl' }} />
        
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
