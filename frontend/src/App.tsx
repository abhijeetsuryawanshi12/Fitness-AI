import { Route, Routes, NavLink } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import ToastProvider from './components/ToastProvider';

import Login from './pages/Login';
import Register from './pages/Register';
import Onboarding from './pages/Onboarding';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Tasks from './pages/Tasks';
import Profile from './pages/Profile';
import Plan from './pages/Plan';
import Progress from './pages/Progress';
import ErrorBoundaryTest from './components/ErrorBoundaryTest';
import { Dumbbell } from 'lucide-react';

import Prism from './components/react_bits/Prism';


function Logo() {
  return (
    <div className="flex items-center gap-3 p-4">
      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
        <Dumbbell className="w-5 h-5 text-white" />
      </div>
      <div className="flex flex-col">
        <span className="text-xl font-bold text-white">
          Fitness AI
        </span>
        <span className="text-xs text-slate-400">Your Personal Trainer</span>
      </div>
    </div>
  );
}

// A layout for public auth pages like Login and Register
function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex flex-col">
      <nav className="bg-slate-900/50 backdrop-blur-xl border-b border-white/10 shadow-2xl">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Logo />
          <div className="flex gap-4">
            <NavLink to="/login" className={({ isActive }) => `px-6 py-2 rounded-xl transition-all duration-200 font-medium ${isActive ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/25' : 'text-slate-400 hover:text-white hover:bg-white/10 border border-white/20'}`}>Login</NavLink>
            <NavLink to="/register" className={({ isActive }) => `px-6 py-2 rounded-xl transition-all duration-200 font-medium ${isActive ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/25' : 'text-slate-400 hover:text-white hover:bg-white/10 border border-white/20'}`}>Register</NavLink>
          </div>
        </div>
      </nav>
      <div className="flex-grow flex items-center justify-center p-6">
        {children}
      </div>
    </div>
  );
}


export default function App() {
  return (
    <ErrorBoundary>
      <ToastProvider />
      <div className="relative min-h-screen overflow-hidden">
        {/* Background */}
        {/* <div style={{ width: '100%', height: '600px', position: 'relative' }}>
          <Prism
            animationType="rotate"
            timeScale={0.5}
            height={3.5}
            baseWidth={5.5}
            scale={3.6}
            hueShift={0}
            colorFrequency={1}
            noise={0.5}
            glow={1}
          />
        </div> */}

        {/* Foreground (all routes) */}
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<AuthLayout><Login /></AuthLayout>} />
          <Route path="/register" element={<AuthLayout><Register /></AuthLayout>} />

          {/* Onboarding route */}
          <Route
            path="/onboarding"
            element={
              <ProtectedRoute>
                <Onboarding />
              </ProtectedRoute>
            }
          />

          {/* Test route (development only - remove in production) */}
          <Route path="/test-errors" element={<ErrorBoundaryTest />} />

          {/* Main application routes */}
          <Route element={<MainLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/plan" element={<Plan />} />
            <Route path="/progress" element={<Progress />} />
          </Route>
        </Routes>
      </div>
    </ErrorBoundary>
  );
}
