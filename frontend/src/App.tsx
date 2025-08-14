// src/App.tsx

import { Link, NavLink, Route, Routes, useNavigate, useLocation } from 'react-router-dom'
import { useState } from 'react'
import {
  LayoutDashboard,
  MessageCircle,
  CheckSquare,
  ClipboardList,
  TrendingUp,
  User,
  LogOut,
  Dumbbell,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Tasks from './pages/Tasks'
import Profile from './pages/Profile'
import Plan from './pages/Plan'
import Progress from './pages/Progress'
import { clearToken, isAuthenticated } from './lib/auth'

// Logo component (unchanged)
function Logo({ collapsed = false }) {
  return (
    <div className="flex items-center gap-3 p-4">
      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
        <Dumbbell className="w-5 h-5 text-white" />
      </div>
      {!collapsed && (
        <div className="flex flex-col">
          <span className="text-xl font-bold text-white">
            Fitness AI
          </span>
          <span className="text-xs text-slate-400">Your Personal Trainer</span>
        </div>
      )}
    </div>
  )
}

// Navigation items configuration (unchanged)
const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/chat', label: 'Chat', icon: MessageCircle },
  { to: '/tasks', label: 'Tasks', icon: CheckSquare },
  { to: '/plan', label: 'Plan', icon: ClipboardList },
  { to: '/progress', label: 'Progress', icon: TrendingUp },
]

// --- MODIFICATION 1: Update Sidebar to be a controlled component ---
function Sidebar({ collapsed, setCollapsed }) {
  const navigate = useNavigate()
  const location = useLocation()
  
  // The internal state is removed from here. It's now controlled by props.

  if (!isAuthenticated()) {
    return null
  }

  return (
    <div className={`
      bg-slate-900/95 backdrop-blur-xl border-r border-white/10 
      transition-all duration-300 
      ${collapsed ? 'w-20' : 'w-72'} 
      flex flex-col h-screen fixed left-0 top-0 z-50
      shadow-2xl
    `}>
      <div className="flex items-center justify-between border-b border-white/10">
        <Logo collapsed={collapsed} />
        <button
          // This now calls the function passed down from App.tsx
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 mr-4 hover:bg-white/10 rounded-xl transition-all duration-200 text-slate-400 hover:text-white"
        >
          {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </div>

      <nav className="flex-1 py-6">
        <div className="space-y-2 px-4">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname.startsWith(item.to)
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-200 group ${isActive ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/25' : 'text-slate-400 hover:text-white hover:bg-white/10'}`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'group-hover:text-white'}`} />
                {!collapsed && <span className="font-medium">{item.label}</span>}
                {!collapsed && isActive && <div className="ml-auto w-2 h-2 bg-white rounded-full" />}
              </NavLink>
            )
          })}
        </div>
      </nav>

      <div className="border-t border-white/10 p-4 space-y-2">
        <NavLink
          to="/profile"
          className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-200 group ${location.pathname === '/profile' ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/25' : 'text-slate-400 hover:text-white hover:bg-white/10'}`}
        >
          <User className="w-5 h-5" />
          {!collapsed && <span className="font-medium">Profile</span>}
        </NavLink>
        <button
          onClick={() => { clearToken(); navigate('/login') }}
          className={`w-full flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-200 group text-slate-400 hover:text-red-400 hover:bg-red-500/10 ${collapsed ? 'justify-center' : ''}`}
        >
          <LogOut className="w-5 h-5" />
          {!collapsed && <span className="font-medium">Logout</span>}
        </button>
      </div>
    </div>
  )
}

// AuthNavbar (unchanged)
function AuthNavbar() {
    const location = useLocation();
    if (isAuthenticated()) return null;
    return (
        <nav className="bg-slate-900/95 backdrop-blur-xl border-b border-white/10 shadow-2xl">
            <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
                <Logo />
                <div className="flex gap-4">
                    <NavLink to="/login" className={({ isActive }) => `px-6 py-2 rounded-xl transition-all duration-200 font-medium ${isActive ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/25' : 'text-slate-400 hover:text-white hover:bg-white/10 border border-white/20'}`}>Login</NavLink>
                    <NavLink to="/register" className={({ isActive }) => `px-6 py-2 rounded-xl transition-all duration-200 font-medium ${isActive ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/25' : 'text-slate-400 hover:text-white hover:bg-white/10 border border-white/20'}`}>Register</NavLink>
                </div>
            </div>
        </nav>
    );
}


export default function App() {
  // --- MODIFICATION 2: State is now managed here in the parent component ---
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const location = useLocation();

  // --- MODIFICATION 4: Check if we are on the chat page ---
  const isChatPage = location.pathname === '/chat';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <AuthNavbar />
      
      {/* --- MODIFICATION 3: Pass state and setter down to Sidebar --- */}
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} />
      
      {/* This main content wrapper now correctly reacts to the state changes */}
      <div className={`
        transition-all duration-300 
        ${isAuthenticated() ? (sidebarCollapsed ? 'ml-0 lg:ml-20' : 'ml-0 lg:ml-72') : ''}
      `}>
        <main className={`
          min-h-screen
          ${isAuthenticated() && !isChatPage ? 'p-6' : 'p-0'}
        `}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
            <Route path="/tasks" element={<ProtectedRoute><Tasks /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/plan" element={<ProtectedRoute><Plan /></ProtectedRoute>} />
            <Route path="/progress" element={<ProtectedRoute><Progress /></ProtectedRoute>} />
          </Routes>
        </main>
      </div>
    </div>
  )
}