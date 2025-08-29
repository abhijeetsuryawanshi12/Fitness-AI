import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, MessageCircle, CheckSquare, ClipboardList, TrendingUp, User,
  LogOut, Dumbbell, ChevronLeft, ChevronRight
} from 'lucide-react';
import { clearToken } from '@/lib/auth';

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
  );
}

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/chat', label: 'Chat', icon: MessageCircle },
  { to: '/tasks', label: 'Tasks', icon: CheckSquare },
  { to: '/plan', label: 'Plan', icon: ClipboardList },
  { to: '/progress', label: 'Progress', icon: TrendingUp },
];

export default function Sidebar({ collapsed, setCollapsed }: { collapsed: boolean, setCollapsed: (c: boolean) => void }) {
  const navigate = useNavigate();
  const location = useLocation();

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
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 mr-4 hover:bg-white/10 rounded-xl transition-all duration-200 text-slate-400 hover:text-white"
        >
          {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </div>

      <nav className="flex-1 py-6">
        <div className="space-y-2 px-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.to);
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
            );
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
          onClick={() => { clearToken(); navigate('/login'); }}
          className={`w-full flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-200 group text-slate-400 hover:text-red-400 hover:bg-red-500/10 ${collapsed ? 'justify-center' : ''}`}
        >
          <LogOut className="w-5 h-5" />
          {!collapsed && <span className="font-medium">Logout</span>}
        </button>
      </div>
    </div>
  );
}