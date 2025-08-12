import { Link, NavLink, Route, Routes, useNavigate, useLocation } from 'react-router-dom'
import { useState } from 'react'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Tasks from './pages/Tasks'
import Profile from './pages/Profile'
import Plan from './pages/Plan'
import Documents from './pages/Documents'
import Food from './pages/Food'
import Progress from './pages/Progress'
import Voice from './pages/Voice'
import { clearToken, isAuthenticated } from './lib/auth'

// Logo component - you can replace this with an actual logo image
function Logo() {
  return (
    <div className="flex items-center gap-2 p-4">
      <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
        <span className="text-white font-bold text-sm">F</span>
      </div>
      <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
        Fitness AI
      </span>
    </div>
  )
}


// Navigation items configuration
const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/chat', label: 'Chat', icon: '💬' },
  { to: '/tasks', label: 'Tasks', icon: '✅' },
  { to: '/plan', label: 'Plan', icon: '📋' },
  { to: '/documents', label: 'Docs', icon: '📄' },
  { to: '/food', label: 'Food', icon: '🍎' },
  { to: '/progress', label: 'Progress', icon: '📈' },
  { to: '/voice', label: 'Voice', icon: '🎤' },
]

function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)

  if (!isAuthenticated()) {
    return null
  }

  return (
    <div className={`bg-white shadow-lg border-r border-gray-200 transition-all duration-300 ${collapsed ? 'w-16' : 'w-64'} flex flex-col h-screen fixed left-0 top-0 z-30`}>
      {/* Logo and collapse button */}
      <div className="flex items-center justify-between border-b border-gray-200">
        {!collapsed && <Logo />}

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-3 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <span className="text-gray-600 text-lg">
            {collapsed ? '→' : '←'}
          </span>
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4">
        <div className="space-y-2 px-3">
          {navItems.map((item) => {
            const isActive = location.pathname === item.to
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-50 text-blue-600 border-l-4 border-blue-600 font-medium'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                {!collapsed && <span className="text-sm">{item.label}</span>}
              </NavLink>
            )
          })}
        </div>
      </nav>

      {/* User section */}
      <div className="border-t border-gray-200 p-3">
        <NavLink
          to="/profile"
          className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 mb-2 ${
            location.pathname === '/profile'
              ? 'bg-blue-50 text-blue-600 border-l-4 border-blue-600 font-medium'
              : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'
          }`}
        >
          <span className="text-lg">👤</span>
          {!collapsed && <span className="text-sm">Profile</span>}
        </NavLink>
        
        <button
          onClick={() => { clearToken(); navigate('/login') }}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-700 hover:bg-red-50 hover:text-red-600 transition-all duration-200 ${
            collapsed ? 'justify-center' : ''
          }`}
        >
          <span className="text-lg">🚪</span>
          {!collapsed && <span className="text-sm">Logout</span>}
        </button>
      </div>
    </div>
  )
}

function AuthNavbar() {
  const location = useLocation()
  
  if (isAuthenticated()) {
    return null
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 mb-8">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <Logo />
        <div className="flex gap-6">
          <NavLink
            to="/login"
            className={`px-4 py-2 rounded-lg transition-colors text-sm ${
              location.pathname === '/login'
                ? 'bg-blue-600 text-white'
                : 'text-gray-700 hover:text-blue-600 hover:bg-blue-50'
            }`}
          >
            Login
          </NavLink>
          <NavLink
            to="/register"
            className={`px-4 py-2 rounded-lg transition-colors text-sm ${
              location.pathname === '/register'
                ? 'bg-blue-600 text-white'
                : 'text-gray-700 hover:text-blue-600 hover:bg-blue-50'
            }`}
          >
            Register
          </NavLink>
        </div>
      </div>
    </nav>
  )
}

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <AuthNavbar />
      <Sidebar />
      
      <div className={`transition-all duration-300 ${isAuthenticated() ? 'ml-64' : ''}`}>
        <main className="p-6">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
            <Route path="/tasks" element={<ProtectedRoute><Tasks /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/plan" element={<ProtectedRoute><Plan /></ProtectedRoute>} />
            <Route path="/documents" element={<ProtectedRoute><Documents /></ProtectedRoute>} />
            <Route path="/food" element={<ProtectedRoute><Food /></ProtectedRoute>} />
            <Route path="/progress" element={<ProtectedRoute><Progress /></ProtectedRoute>} />
            <Route path="/voice" element={<ProtectedRoute><Voice /></ProtectedRoute>} />
          </Routes>
        </main>
      </div>
    </div>
  )
}