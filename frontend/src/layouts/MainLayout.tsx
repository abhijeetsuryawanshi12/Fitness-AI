import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from '@/components/Sidebar';
import OnboardingChecker from '@/components/OnboardingChecker';

export default function MainLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const location = useLocation();
  const isChatPage = location.pathname.startsWith('/chat');

  return (
    <OnboardingChecker>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} />
        <div className={`
            transition-all duration-300 
            ${sidebarCollapsed ? 'ml-0 lg:ml-20' : 'ml-0 lg:ml-72'}
        `}>
          <main className={`min-h-screen ${isChatPage ? 'p-0' : 'p-6'}`}>
            <Outlet />
          </main>
        </div>
      </div>
    </OnboardingChecker>
  );
}