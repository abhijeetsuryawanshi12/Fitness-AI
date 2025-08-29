import { useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import api from '@/lib/api';
import { isAuthenticated } from '@/lib/auth';

export default function OnboardingChecker({ children }: { children: React.ReactNode }) {
  const [isOnboarded, setIsOnboarded] = useState<boolean | null>(null);
  const location = useLocation();

  useEffect(() => {
    // This check is redundant if used within an auth-protected layout, but good for standalone use.
    if (!isAuthenticated()) {
      setIsOnboarded(false);
      return;
    }

    const checkOnboardingStatus = async () => {
      try {
        const { data: userProfile } = await api.get('/profile/me');
        // If age is present, we assume they are onboarded. 'age' is a required field in our onboarding flow.
        if (userProfile && (userProfile.age !== null && userProfile.age !== undefined)) {
          setIsOnboarded(true);
        } else {
          setIsOnboarded(false);
        }
      } catch (error) {
        console.error("Failed to check onboarding status:", error);
        // If API fails, we can't determine status. For safety, prevent access.
        // In a real app, you might want to show an error page or log the user out.
        setIsOnboarded(false);
      }
    };

    checkOnboardingStatus();
  }, [location.pathname]); // Re-check if the path changes, ensures it runs on first load of the layout.

  // While checking, show a full-screen loader
  if (isOnboarded === null) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // If not onboarded and they are trying to access any page other than onboarding, redirect them.
  if (!isOnboarded && location.pathname !== '/onboarding') {
    return <Navigate to="/onboarding" replace />;
  }

  // If they are already onboarded but somehow try to access the onboarding page, send them to the dashboard.
  if (isOnboarded && location.pathname === '/onboarding') {
    return <Navigate to="/dashboard" replace />;
  }

  // If checks pass, render the requested page content.
  return <>{children}</>;
}