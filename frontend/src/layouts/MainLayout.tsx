// frontend/src/layouts/MainLayout.tsx
import { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from '@/components/Sidebar';
import OnboardingChecker from '@/components/OnboardingChecker';
import { registerAndSubscribe }  from '@/lib/push';

export default function MainLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const location = useLocation();
  const isChatPage = location.pathname.startsWith('/chat');

  // --- NEW: Register for push notifications on layout mount ---
  useEffect(() => {
    // We only want to run this for the user, not for bots or unsupported browsers
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      registerAndSubscribe();
    }
  }, []); // Empty dependency array ensures this runs only once when the component mounts

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