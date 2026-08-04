import React, { createContext, useContext, useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { Toaster, toast } from "sonner";
import axios from "axios";
import { AnimatePresence, motion } from "framer-motion";
import { Lock, User, Terminal, ChevronRight, LogOut, Search, Activity, ShieldAlert, Cpu, Plus, MoreHorizontal } from "lucide-react";

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
      {/* Soft ambient glow behind the login box */}
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
    }, 3000); // Shortened transition for a snappier experience
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
        
        {/* Create User Panel */}
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

        {/* Users List */}
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

const UserDashboard = () => {
  return (
    <DashboardLayout title="Overview">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-[#09090b] border border-white/5 p-6 rounded-2xl shadow-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
            <Activity className="w-24 h-24" />
          </div>
          <div className="h-10 w-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center mb-4 relative z-10">
            <Activity className="h-5 w-5 text-white" />
          </div>
          <h3 className="font-medium text-white mb-2 relative z-10">Protocol Status</h3>
          <p className="text-zinc-500 text-sm leading-relaxed relative z-10">Main AI key checker module is currently offline. Awaiting sequence initialization.</p>
        </div>
        
        <div className="bg-[#09090b] border border-white/5 p-6 rounded-2xl shadow-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
            <Cpu className="w-24 h-24" />
          </div>
          <div className="h-10 w-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center mb-4 relative z-10">
            <Cpu className="h-5 w-5 text-zinc-400" />
          </div>
          <h3 className="font-medium text-zinc-300 mb-2 relative z-10">Proxy Node</h3>
          <p className="text-zinc-600 text-sm leading-relaxed relative z-10"><span className="text-xs font-semibold uppercase text-zinc-400 mr-2">Coming Soon</span> High-speed HTTP/SOCKS5 validation engine.</p>
        </div>

        <div className="bg-[#09090b] border border-white/5 p-6 rounded-2xl shadow-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
            <ShieldAlert className="w-24 h-24" />
          </div>
          <div className="h-10 w-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center mb-4 relative z-10">
            <ShieldAlert className="h-5 w-5 text-zinc-400" />
          </div>
          <h3 className="font-medium text-zinc-300 mb-2 relative z-10">AI API Vault</h3>
          <p className="text-zinc-600 text-sm leading-relaxed relative z-10"><span className="text-xs font-semibold uppercase text-zinc-400 mr-2">Coming Soon</span> Multi-provider key validation and quota checking.</p>
        </div>
      </div>
      
      <div className="mt-8 bg-[#09090b] border border-white/5 rounded-2xl shadow-xl p-12 flex flex-col items-center justify-center text-center">
        <div className="h-16 w-16 rounded-full bg-white/[0.02] border border-white/5 flex items-center justify-center mb-6">
          <Search className="h-6 w-6 text-zinc-500" />
        </div>
        <h2 className="text-xl font-medium text-white mb-3">Awaiting Deployment</h2>
        <p className="text-zinc-500 max-w-md mx-auto leading-relaxed">The primary checker interface is currently being deployed. Please check back later for the next system update.</p>
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
