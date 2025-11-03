# Error Handling Guide - Fitness AI

## Overview

The Fitness AI application now includes comprehensive error handling with:
1. **Global Error Boundary** - Catches React component errors
2. **Toast Notifications** - User-friendly error messages
3. **Graceful Degradation** - App continues working when parts fail

---

## What Was Added

### 1. ErrorBoundary Component

**Location**: [frontend/src/components/ErrorBoundary.tsx](frontend/src/components/ErrorBoundary.tsx)

A React class component that catches JavaScript errors anywhere in the component tree.

**Features**:
- ✅ Catches render errors in child components
- ✅ Shows beautiful fallback UI with error details (dev mode)
- ✅ Provides "Try Again", "Go Home", and "Refresh" buttons
- ✅ Logs errors to console for debugging
- ✅ Can be extended to send errors to tracking services (Sentry, LogRocket)

**Usage**:
```tsx
import ErrorBoundary from './components/ErrorBoundary';

// Wrap entire app
<ErrorBoundary>
  <App />
</ErrorBoundary>

// Wrap specific sections
<ErrorBoundary fallback={<CustomErrorPage />}>
  <Dashboard />
</ErrorBoundary>
```

### 2. ErrorFallback Component

**Location**: [frontend/src/components/ErrorFallback.tsx](frontend/src/components/ErrorFallback.tsx)

Reusable error display components for different scenarios.

**Two variants**:
1. **ErrorFallback** - Full-screen error page
2. **PageErrorFallback** - Smaller inline error component

**Usage**:
```tsx
import ErrorFallback, { PageErrorFallback } from './components/ErrorFallback';

// Full-screen
<ErrorFallback
  error={error}
  resetError={() => retry()}
  title="Failed to load page"
  message="Custom error message"
/>

// Inline
<PageErrorFallback
  error={error}
  resetError={() => retry()}
/>
```

### 3. Toast Notification System

**Location**: [frontend/src/components/ToastProvider.tsx](frontend/src/components/ToastProvider.tsx)

Provides toast notifications using `react-hot-toast` library.

**Features**:
- ✅ Success, error, loading toasts
- ✅ Auto-dismisses after duration
- ✅ Styled to match app theme
- ✅ Supports custom icons and actions

**Usage**:
```tsx
import toast from 'react-hot-toast';

// Success message
toast.success('Task completed successfully!');

// Error message
toast.error('Failed to load data');

// Loading with promise
const promise = fetchData();
toast.promise(promise, {
  loading: 'Loading...',
  success: 'Data loaded!',
  error: 'Failed to load',
});

// Custom styled
toast('Custom message', {
  icon: '🎉',
  style: {
    background: '#3b82f6',
    color: '#fff',
  },
});

// With action buttons
toast((t) => (
  <div>
    <span>Delete item?</span>
    <button onClick={() => {
      handleDelete();
      toast.dismiss(t.id);
    }}>
      Delete
    </button>
  </div>
));
```

### 4. Integration in App

**Location**: [frontend/src/App.tsx](frontend/src/App.tsx)

The entire app is now wrapped with ErrorBoundary and ToastProvider:
```tsx
<ErrorBoundary>
  <ToastProvider />
  <Routes>
    {/* All routes */}
  </Routes>
</ErrorBoundary>
```

---

## Error Handling Patterns

### Pattern 1: Component Errors (Caught by ErrorBoundary)

**What it catches**:
- Errors in render methods
- Errors in lifecycle methods
- Errors in constructors
- Errors in hooks (useState, useEffect, etc.)

**Example**:
```tsx
function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    // If this throws, ErrorBoundary catches it
    const result = JSON.parse(invalidData);
    setData(result);
  }, []);

  // If this throws, ErrorBoundary catches it
  return <div>{data.title}</div>;
}

// Wrap with ErrorBoundary
<ErrorBoundary>
  <Dashboard />
</ErrorBoundary>
```

### Pattern 2: Async Errors (Use Toast)

**What ErrorBoundary does NOT catch**:
- Event handler errors (onClick, onChange)
- Async code (setTimeout, fetch)
- Server-side rendering errors

**Solution**: Use try-catch + toast

**Example**:
```tsx
const handleFetchTasks = async () => {
  try {
    const response = await api.getTasks();
    setTasks(response.data);
    toast.success('Tasks loaded successfully!');
  } catch (error) {
    console.error('Failed to fetch tasks:', error);
    toast.error('Failed to load tasks. Please try again.');
  }
};

const handleDeleteTask = async (taskId) => {
  // Show loading toast
  const promise = api.deleteTask(taskId);

  toast.promise(promise, {
    loading: 'Deleting task...',
    success: 'Task deleted successfully!',
    error: 'Failed to delete task',
  });

  try {
    await promise;
    refetchTasks();
  } catch (error) {
    console.error('Delete failed:', error);
  }
};
```

### Pattern 3: API Error Handling

**Centralized API error handling**:

Create an Axios interceptor:
```tsx
// lib/api.ts
import axios from 'axios';
import toast from 'react-hot-toast';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const message = error.response.data?.message || 'An error occurred';

      switch (status) {
        case 401:
          toast.error('Session expired. Please login again.');
          // Redirect to login
          window.location.href = '/login';
          break;
        case 403:
          toast.error('You do not have permission to do that.');
          break;
        case 404:
          toast.error('Resource not found.');
          break;
        case 500:
          toast.error('Server error. Please try again later.');
          break;
        default:
          toast.error(message);
      }
    } else if (error.request) {
      // Request made but no response
      toast.error('Network error. Please check your connection.');
    } else {
      // Something else happened
      toast.error('An unexpected error occurred.');
    }

    return Promise.reject(error);
  }
);

export default api;
```

### Pattern 4: Page-Level Error Boundaries

Wrap individual pages to prevent one broken page from affecting others:

```tsx
<Routes>
  <Route
    path="/dashboard"
    element={
      <ErrorBoundary fallback={<PageErrorFallback />}>
        <Dashboard />
      </ErrorBoundary>
    }
  />
  <Route
    path="/chat"
    element={
      <ErrorBoundary fallback={<PageErrorFallback />}>
        <Chat />
      </ErrorBoundary>
    }
  />
</Routes>
```

---

## Testing Error Handling

### Test Page

**URL**: http://localhost:5173/test-errors

**Location**: [frontend/src/components/ErrorBoundaryTest.tsx](frontend/src/components/ErrorBoundaryTest.tsx)

A dedicated page for testing error handling:
- ✅ Trigger render errors (caught by ErrorBoundary)
- ✅ Trigger async errors (show toasts)
- ✅ Test success/error/loading toasts
- ✅ Test custom styled toasts
- ✅ Test toasts with action buttons

**Remove this route in production!**

### Manual Testing

**Test 1: Render Error**
```tsx
// Add this to any component temporarily
if (true) {
  throw new Error('Test error!');
}
```

**Expected**: ErrorBoundary fallback UI shows

**Test 2: API Error**
```tsx
const handleClick = async () => {
  try {
    await api.get('/nonexistent-endpoint');
  } catch (error) {
    toast.error('API call failed');
  }
};
```

**Expected**: Error toast appears

**Test 3: Form Validation**
```tsx
const handleSubmit = () => {
  if (!email) {
    toast.error('Email is required');
    return;
  }
  // proceed with submission
};
```

**Expected**: Error toast appears

---

## Best Practices

### ✅ DO

1. **Use ErrorBoundary for component errors**
   ```tsx
   <ErrorBoundary>
     <Component />
   </ErrorBoundary>
   ```

2. **Use toast for user actions**
   ```tsx
   toast.success('Saved successfully!');
   toast.error('Failed to save');
   ```

3. **Log errors to console**
   ```tsx
   catch (error) {
     console.error('Error details:', error);
     toast.error('Operation failed');
   }
   ```

4. **Provide helpful error messages**
   ```tsx
   // Good
   toast.error('Failed to load tasks. Please check your connection.');

   // Bad
   toast.error('Error');
   ```

5. **Show loading states**
   ```tsx
   toast.promise(fetchData(), {
     loading: 'Loading data...',
     success: 'Data loaded!',
     error: 'Failed to load',
   });
   ```

### ❌ DON'T

1. **Don't rely on ErrorBoundary for async errors**
   ```tsx
   // This won't be caught by ErrorBoundary!
   const onClick = async () => {
     throw new Error('Async error');
   };
   ```

2. **Don't show technical error messages to users**
   ```tsx
   // Bad
   toast.error(error.stack);

   // Good
   toast.error('Something went wrong. Please try again.');
   console.error(error); // Log technical details
   ```

3. **Don't use alerts or console.log for errors**
   ```tsx
   // Bad
   alert('Error!');
   console.log('Error occurred');

   // Good
   toast.error('Operation failed');
   console.error('Detailed error:', error);
   ```

4. **Don't ignore errors silently**
   ```tsx
   // Bad
   try {
     await api.call();
   } catch (error) {
     // Silent failure - user doesn't know what happened
   }

   // Good
   try {
     await api.call();
   } catch (error) {
     console.error('API call failed:', error);
     toast.error('Operation failed. Please try again.');
   }
   ```

---

## Future Enhancements

### 1. Error Tracking Service

Integrate Sentry or LogRocket:

```tsx
// ErrorBoundary.tsx
componentDidCatch(error, errorInfo) {
  console.error('Error caught:', error, errorInfo);

  // Send to Sentry
  Sentry.captureException(error, {
    contexts: {
      react: {
        componentStack: errorInfo.componentStack,
      },
    },
  });
}
```

### 2. Offline Detection

Show toast when user goes offline:

```tsx
useEffect(() => {
  const handleOffline = () => {
    toast.error('You are offline. Some features may not work.');
  };

  const handleOnline = () => {
    toast.success('Back online!');
  };

  window.addEventListener('offline', handleOffline);
  window.addEventListener('online', handleOnline);

  return () => {
    window.removeEventListener('offline', handleOffline);
    window.removeEventListener('online', handleOnline);
  };
}, []);
```

### 3. Error Retry Logic

Automatic retry for failed API calls:

```tsx
const fetchWithRetry = async (fn, retries = 3) => {
  try {
    return await fn();
  } catch (error) {
    if (retries > 0) {
      toast('Retrying...', { icon: '🔄' });
      await new Promise(r => setTimeout(r, 1000));
      return fetchWithRetry(fn, retries - 1);
    }
    throw error;
  }
};
```

### 4. Error Recovery Actions

Provide recovery options in error UI:

```tsx
<ErrorFallback
  error={error}
  actions={[
    { label: 'Retry', onClick: () => retry() },
    { label: 'Go Home', onClick: () => navigate('/') },
    { label: 'Contact Support', onClick: () => navigate('/support') },
  ]}
/>
```

---

## Summary

Your Fitness AI app now has:
- ✅ **Global Error Boundary** catching React errors
- ✅ **Toast Notifications** for user feedback
- ✅ **Graceful error handling** throughout the app
- ✅ **Test page** for verifying error handling
- ✅ **Developer-friendly** error details in dev mode
- ✅ **Production-ready** user-friendly messages

**Result**: Better user experience, easier debugging, and more professional app!

---

## Quick Reference

| Scenario | Solution |
|----------|----------|
| Component render error | ErrorBoundary catches it automatically |
| API call fails | `try-catch` + `toast.error()` |
| Form validation fails | `toast.error('Field is required')` |
| Loading data | `toast.promise(promise, { loading, success, error })` |
| User action succeeds | `toast.success('Done!')` |
| Network offline | `toast.error('No connection')` |

---

**Next Steps**: Test the error handling by visiting http://localhost:5173/test-errors and trying different scenarios!
