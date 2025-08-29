import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '@/lib/auth';
import React from 'react';

// This is now a simple guard for routes that require authentication
// but should NOT have the main application layout (like the Onboarding page).
export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}