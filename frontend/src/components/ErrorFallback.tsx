import { AlertTriangle, Home, RefreshCw, RotateCcw } from 'lucide-react';

interface ErrorFallbackProps {
  error?: Error | null;
  resetError?: () => void;
  title?: string;
  message?: string;
  showDetails?: boolean;
}

/**
 * ErrorFallback - A reusable error display component
 *
 * Can be used inside ErrorBoundary or standalone for displaying errors
 */
export default function ErrorFallback({
  error = null,
  resetError,
  title = 'Oops! Something went wrong',
  message = "We're sorry for the inconvenience. An unexpected error occurred.",
  showDetails = import.meta.env.DEV, // Show details only in development
}: ErrorFallbackProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-2xl w-full bg-slate-800/50 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/10 p-8 animate-in fade-in duration-500">
        {/* Error Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center animate-pulse">
            <AlertTriangle className="w-10 h-10 text-red-500" />
          </div>
        </div>

        {/* Error Title */}
        <h1 className="text-3xl font-bold text-white text-center mb-4">
          {title}
        </h1>

        {/* Error Description */}
        <p className="text-slate-300 text-center mb-6">
          {message}
        </p>

        {/* Error Details (Only in development) */}
        {showDetails && error && (
          <div className="mb-6">
            <details className="bg-slate-900/50 rounded-lg p-4 border border-red-500/20">
              <summary className="text-red-400 font-mono text-sm cursor-pointer hover:text-red-300 transition-colors flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                Error Details (Development Mode)
              </summary>
              <div className="mt-4 space-y-3">
                {/* Error Name */}
                <div>
                  <p className="text-xs text-slate-400 mb-1 font-semibold">Error Type:</p>
                  <pre className="text-xs text-red-400 font-mono overflow-auto bg-slate-950 p-3 rounded">
                    {error.name}
                  </pre>
                </div>

                {/* Error Message */}
                <div>
                  <p className="text-xs text-slate-400 mb-1 font-semibold">Error Message:</p>
                  <pre className="text-xs text-red-400 font-mono overflow-auto bg-slate-950 p-3 rounded">
                    {error.message}
                  </pre>
                </div>

                {/* Stack Trace */}
                {error.stack && (
                  <div>
                    <p className="text-xs text-slate-400 mb-1 font-semibold">Stack Trace:</p>
                    <pre className="text-xs text-red-400 font-mono overflow-auto bg-slate-950 p-3 rounded max-h-60">
                      {error.stack}
                    </pre>
                  </div>
                )}
              </div>
            </details>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          {resetError && (
            <button
              onClick={resetError}
              className="flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all duration-200 hover:scale-105"
            >
              <RotateCcw className="w-4 h-4" />
              Try Again
            </button>
          )}

          <button
            onClick={() => (window.location.href = '/')}
            className="flex items-center justify-center gap-2 px-6 py-3 bg-slate-700 text-white rounded-xl font-semibold hover:bg-slate-600 transition-all duration-200 hover:scale-105"
          >
            <Home className="w-4 h-4" />
            Go to Dashboard
          </button>

          <button
            onClick={() => window.location.reload()}
            className="flex items-center justify-center gap-2 px-6 py-3 bg-slate-700/50 text-slate-300 rounded-xl font-semibold hover:bg-slate-700 transition-all duration-200 border border-white/10 hover:scale-105"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh Page
          </button>
        </div>

        {/* Help Text */}
        <div className="mt-8 pt-6 border-t border-white/10">
          <p className="text-slate-400 text-sm text-center">
            If this problem persists, please try:
          </p>
          <ul className="text-slate-400 text-sm mt-3 space-y-2">
            <li className="flex items-center justify-center gap-2">
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
              Clearing your browser cache
            </li>
            <li className="flex items-center justify-center gap-2">
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
              Checking your internet connection
            </li>
            <li className="flex items-center justify-center gap-2">
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
              Contacting support if the issue continues
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

/**
 * PageErrorFallback - A smaller error component for page-level errors
 * (doesn't take full screen)
 */
export function PageErrorFallback({
  error = null,
  resetError,
  title = 'Failed to load this page',
  message = 'An error occurred while loading this content.',
}: ErrorFallbackProps) {
  return (
    <div className="flex items-center justify-center p-12">
      <div className="max-w-md w-full bg-slate-800/50 backdrop-blur-xl rounded-xl shadow-xl border border-white/10 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
            <AlertTriangle className="w-6 h-6 text-red-500" />
          </div>
          <h2 className="text-xl font-bold text-white">{title}</h2>
        </div>

        <p className="text-slate-300 text-sm mb-4">{message}</p>

        {import.meta.env.DEV && error && (
          <details className="mb-4 bg-slate-900/50 rounded p-3 border border-red-500/20">
            <summary className="text-xs text-red-400 cursor-pointer">Error Details</summary>
            <pre className="text-xs text-red-400 mt-2 overflow-auto max-h-32">
              {error.message}
            </pre>
          </details>
        )}

        <div className="flex gap-2">
          {resetError && (
            <button
              onClick={resetError}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              Try Again
            </button>
          )}
          <button
            onClick={() => window.location.reload()}
            className="flex-1 px-4 py-2 bg-slate-700 text-white rounded-lg text-sm font-medium hover:bg-slate-600 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>
    </div>
  );
}
