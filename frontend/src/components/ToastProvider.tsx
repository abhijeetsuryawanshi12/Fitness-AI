import { Toaster } from 'react-hot-toast';

/**
 * ToastProvider - Configures and provides toast notifications for the entire app
 *
 * Features:
 * - Success, error, warning, and info messages
 * - Auto-dismisses after 4 seconds
 * - Styled to match app theme
 * - Supports emoji and custom icons
 *
 * Usage:
 * import toast from 'react-hot-toast';
 * toast.success('Plan generated successfully!');
 * toast.error('Failed to load tasks');
 */
export default function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      reverseOrder={false}
      gutter={8}
      containerClassName=""
      containerStyle={{}}
      toastOptions={{
        // Default options
        duration: 4000,

        // Default styling
        style: {
          background: '#1e293b', // slate-800
          color: '#f1f5f9', // slate-100
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '12px',
          padding: '16px',
          fontSize: '14px',
          fontWeight: '500',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)',
          backdropFilter: 'blur(10px)',
          maxWidth: '500px',
        },

        // Success toast styling
        success: {
          duration: 3000,
          style: {
            background: 'linear-gradient(135deg, #065f46 0%, #047857 100%)', // green gradient
            border: '1px solid rgba(16, 185, 129, 0.3)',
          },
          iconTheme: {
            primary: '#10b981', // green-500
            secondary: '#fff',
          },
        },

        // Error toast styling
        error: {
          duration: 5000,
          style: {
            background: 'linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%)', // red gradient
            border: '1px solid rgba(239, 68, 68, 0.3)',
          },
          iconTheme: {
            primary: '#ef4444', // red-500
            secondary: '#fff',
          },
        },

        // Loading toast styling
        loading: {
          style: {
            background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)', // blue gradient
            border: '1px solid rgba(59, 130, 246, 0.3)',
          },
          iconTheme: {
            primary: '#3b82f6', // blue-500
            secondary: '#fff',
          },
        },
      }}
    />
  );
}
