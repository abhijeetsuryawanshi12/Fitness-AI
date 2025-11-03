import { useState } from 'react';
import toast from 'react-hot-toast';
import { Bug, CheckCircle, AlertTriangle, Info } from 'lucide-react';

/**
 * ErrorBoundaryTest - A test component to demonstrate error boundaries and toasts
 *
 * This component is for testing purposes only. Remove it in production or hide it from normal users.
 *
 * Usage:
 * Import and add this to any route temporarily to test error handling:
 * <Route path="/test-errors" element={<ErrorBoundaryTest />} />
 */
export default function ErrorBoundaryTest() {
  const [shouldThrowError, setShouldThrowError] = useState(false);

  if (shouldThrowError) {
    // This will be caught by ErrorBoundary
    throw new Error('Test error: This is a simulated component error!');
  }

  const handleRenderError = () => {
    setShouldThrowError(true);
  };

  const handleAsyncError = async () => {
    // This will NOT be caught by ErrorBoundary (async errors aren't caught)
    // Instead, show error toast
    try {
      await new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Simulated API error')), 1000)
      );
    } catch (error) {
      toast.error('Failed to fetch data: ' + (error as Error).message);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
          <div className="flex items-center gap-3 mb-4">
            <Bug className="w-8 h-8 text-red-500" />
            <h1 className="text-3xl font-bold text-white">Error Handling Test Page</h1>
          </div>
          <p className="text-slate-300">
            This page demonstrates error boundaries and toast notifications. Use the buttons below to test different error scenarios.
          </p>
        </div>

        {/* Error Boundary Tests */}
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-500" />
            Error Boundary Tests
          </h2>
          <p className="text-slate-300 text-sm mb-4">
            These errors will be caught by the ErrorBoundary component and show the fallback UI.
          </p>
          <button
            onClick={handleRenderError}
            className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl font-semibold transition-all duration-200 flex items-center gap-2"
          >
            <Bug className="w-4 h-4" />
            Throw Render Error
          </button>
        </div>

        {/* Toast Notification Tests */}
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Info className="w-5 h-5 text-blue-500" />
            Toast Notification Tests
          </h2>
          <p className="text-slate-300 text-sm mb-4">
            These show different types of toast notifications for various scenarios.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              onClick={() => toast.success('Operation completed successfully!')}
              className="px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-all duration-200"
            >
              Show Success Toast
            </button>
            <button
              onClick={() => toast.error('An error occurred while processing your request.')}
              className="px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-all duration-200"
            >
              Show Error Toast
            </button>
            <button
              onClick={() => {
                const promise = new Promise((resolve) =>
                  setTimeout(() => resolve('Done!'), 2000)
                );
                toast.promise(promise, {
                  loading: 'Generating plan...',
                  success: 'Plan generated successfully!',
                  error: 'Failed to generate plan',
                });
              }}
              className="px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all duration-200"
            >
              Show Loading Toast
            </button>
            <button
              onClick={handleAsyncError}
              className="px-4 py-3 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-medium transition-all duration-200"
            >
              Simulate API Error
            </button>
          </div>
        </div>

        {/* Custom Toast Examples */}
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            Custom Toast Examples
          </h2>
          <p className="text-slate-300 text-sm mb-4">
            Examples of custom styled toasts with icons and actions.
          </p>
          <div className="grid grid-cols-1 gap-3">
            <button
              onClick={() =>
                toast.success('Task completed!', {
                  icon: '✅',
                  duration: 3000,
                })
              }
              className="px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-all duration-200 text-left"
            >
              Toast with Custom Icon
            </button>
            <button
              onClick={() =>
                toast('New notification', {
                  icon: '🔔',
                  style: {
                    background: '#3b82f6',
                    color: '#fff',
                  },
                })
              }
              className="px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-all duration-200 text-left"
            >
              Custom Styled Toast
            </button>
            <button
              onClick={() =>
                toast((t) => (
                  <div className="flex items-center gap-3">
                    <span>Want to delete this?</span>
                    <button
                      onClick={() => {
                        toast.success('Deleted!');
                        toast.dismiss(t.id);
                      }}
                      className="px-3 py-1 bg-red-600 rounded text-sm font-medium"
                    >
                      Delete
                    </button>
                    <button
                      onClick={() => toast.dismiss(t.id)}
                      className="px-3 py-1 bg-slate-600 rounded text-sm font-medium"
                    >
                      Cancel
                    </button>
                  </div>
                ), {
                  duration: 6000,
                })
              }
              className="px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-all duration-200 text-left"
            >
              Toast with Action Buttons
            </button>
          </div>
        </div>

        {/* Documentation */}
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
          <h2 className="text-xl font-bold text-white mb-4">How to Use</h2>
          <div className="space-y-4 text-slate-300 text-sm">
            <div>
              <h3 className="font-semibold text-white mb-2">Error Boundaries:</h3>
              <pre className="bg-slate-900 p-3 rounded-lg overflow-x-auto">
{`import ErrorBoundary from './components/ErrorBoundary';

<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>`}
              </pre>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-2">Toast Notifications:</h3>
              <pre className="bg-slate-900 p-3 rounded-lg overflow-x-auto">
{`import toast from 'react-hot-toast';

// Success
toast.success('Operation successful!');

// Error
toast.error('Something went wrong');

// Loading with promise
toast.promise(
  fetchData(),
  {
    loading: 'Loading...',
    success: 'Data loaded!',
    error: 'Failed to load data',
  }
);`}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
