# API Error Handling Guide - Fitness AI

## Overview

Your Fitness AI application now has **comprehensive, centralized API error handling** with automatic toast notifications for all error scenarios.

### What's Implemented

✅ **Automatic error interception** - All API errors are caught globally
✅ **Smart error messages** - Context-aware error messages for different HTTP status codes
✅ **Toast notifications** - User-friendly visual feedback
✅ **Token expiry handling** - Automatic redirect to login on 401
✅ **Network error detection** - Special handling for timeout and offline scenarios
✅ **Helper functions** - `apiWithLoading` and `apiSilent` for different use cases

---

## How It Works

### Architecture

```
Component → API Call → Axios Interceptor → Handle Error → Show Toast
                              ↓
                         Server Response
                              ↓
                        Success/Error
```

### Error Flow

1. **Component makes API call**
2. **Axios intercept** catches the response
3. **If error**, extract status code and message
4. **Match error type** to appropriate handler
5. **Show toast notification** with helpful message
6. **Log to console** for debugging
7. **Return rejected promise** for component-level handling (optional)

---

## Usage Patterns

### Pattern 1: Simple API Call (Default)

The simplest way - errors are automatically handled:

```tsx
import api from '@/lib/api';
import { useState } from 'react';

function MyComponent() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await api.get('/tasks');
      setData(response.data);
      // ✅ Success - no toast needed, just update state
    } catch (error) {
      // ❌ Error already shown in toast by interceptor
      // Just handle cleanup if needed
      console.error('Fetch failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return <button onClick={fetchData}>Load Tasks</button>;
}
```

**Result**:
- ✅ Network error → "Network error. Please check your internet connection."
- ✅ 500 error → "Server error. Please try again later."
- ✅ 404 error → "Resource not found."

### Pattern 2: With Loading Toast (Recommended for Actions)

Show loading state with automatic success/error messages:

```tsx
import { apiWithLoading } from '@/lib/api';
import api from '@/lib/api';

async function generatePlan() {
  try {
    const data = await apiWithLoading(
      api.post('/plans/generate', { type: 'workout', duration: 7 }),
      'Generating your personalized plan...', // Loading message
      'Plan generated successfully!' // Success message
    );

    // data is already unwrapped (response.data)
    setPlan(data);
  } catch (error) {
    // Error already shown in toast
    console.error('Plan generation failed:', error);
  }
}
```

**Result**:
- 🔵 Shows loading toast: "Generating your personalized plan..."
- ✅ On success: "Plan generated successfully!"
- ❌ On error: Specific error message from interceptor

### Pattern 3: Silent API Call (No Toast)

For background operations where you don't want to show toasts:

```tsx
import { apiSilent } from '@/lib/api';
import api from '@/lib/api';

async function checkNotifications() {
  try {
    const data = await apiSilent(api.get('/notifications'));
    updateBadgeCount(data.unread);
  } catch (error) {
    // Handle silently - no toast shown
    console.log('Notification check failed');
  }
}
```

**Use cases for silent calls**:
- Background polling
- Non-critical data fetching
- When you want custom error handling

### Pattern 4: Manual Success Toast

For operations where you want custom success feedback:

```tsx
import api from '@/lib/api';
import toast from 'react-hot-toast';

async function completeTask(taskId: string) {
  try {
    await api.patch(`/tasks/${taskId}/complete`);
    toast.success('Great job! Task completed! 💪');
  } catch (error) {
    // Error already handled by interceptor
  }
}
```

### Pattern 5: Delete with Confirmation

Show confirmation before action:

```tsx
import api from '@/lib/api';
import toast from 'react-hot-toast';

async function deleteTask(taskId: string) {
  // Show confirmation toast
  toast((t) => (
    <div className="flex items-center gap-3">
      <span>Delete this task?</span>
      <button
        onClick={async () => {
          toast.dismiss(t.id);
          try {
            await api.delete(`/tasks/${taskId}`);
            toast.success('Task deleted');
            refetchTasks();
          } catch (error) {
            // Error shown by interceptor
          }
        }}
        className="px-3 py-1 bg-red-600 rounded text-sm"
      >
        Delete
      </button>
      <button
        onClick={() => toast.dismiss(t.id)}
        className="px-3 py-1 bg-gray-600 rounded text-sm"
      >
        Cancel
      </button>
    </div>
  ), {
    duration: 6000,
  });
}
```

---

## HTTP Status Code Handling

| Status | Error Message | Additional Action |
|--------|---------------|-------------------|
| **400** | Bad Request - Shows specific error from server | None |
| **401** | "Your session has expired. Please login again." | Clears token, redirects to login |
| **403** | "You do not have permission to perform this action." | None |
| **404** | "Resource not found." | None |
| **409** | "This resource already exists." | None |
| **422** | "Validation failed. Please check your input." | Shows server message if available |
| **429** | "Too many requests. Please slow down and try again later." | None |
| **500** | "Server error. Please try again later." | None |
| **502** | "Server is temporarily unavailable. Please try again." | None |
| **503** | "Service is temporarily unavailable. Please try again later." | None |
| **Network** | "Network error. Please check your internet connection." | None |
| **Timeout** | "Request timed out. Please check your connection and try again." | None |

---

## Real-World Examples

### Example 1: Login Page

**File**: `frontend/src/pages/Login.tsx`

```tsx
import { useState } from 'react';
import api from '@/lib/api';
import { setToken } from '@/lib/auth';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);

    try {
      const body = new URLSearchParams();
      body.append('username', email);
      body.append('password', password);

      const { data: tokenData } = await api.post('/auth/token', body, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      setToken(tokenData);

      const { data: userProfile } = await api.get('/profile/me');
      toast.success('Welcome back!');

      // Navigate based on onboarding status
      if (userProfile.age === null) {
        navigate('/onboarding');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      // Error already shown by interceptor
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  }

  return (/* form JSX */);
}
```

**Error Scenarios**:
- Wrong credentials → "Invalid request. Please check your input." (400)
- Server down → "Network error. Please check your internet connection."
- Rate limited → "Too many requests. Please slow down and try again later." (429)

### Example 2: Plan Generation

```tsx
import { apiWithLoading } from '@/lib/api';
import api from '@/lib/api';
import { useState } from 'react';

function PlanGenerator() {
  const [plan, setPlan] = useState(null);
  const [generating, setGenerating] = useState(false);

  async function generateWorkoutPlan() {
    setGenerating(true);
    try {
      const data = await apiWithLoading(
        api.post('/plans/generate', {
          plan_type: 'workout',
          duration: 7,
        }),
        'Generating your workout plan... This may take 30 seconds.',
        'Workout plan generated successfully!'
      );

      setPlan(data);
    } catch (error) {
      // Error shown automatically
      console.error('Generation failed:', error);
    } finally {
      setGenerating(false);
    }
  }

  return (
    <button onClick={generateWorkoutPlan} disabled={generating}>
      {generating ? 'Generating...' : 'Generate Plan'}
    </button>
  );
}
```

**User sees**:
- 🔵 Loading: "Generating your workout plan... This may take 30 seconds."
- ✅ Success: "Workout plan generated successfully!"
- ❌ Error: Specific error (timeout, server error, etc.)

### Example 3: Task Completion

```tsx
import api from '@/lib/api';
import toast from 'react-hot-toast';

async function toggleTaskCompletion(taskId: string, currentStatus: boolean) {
  const newStatus = !currentStatus;

  try {
    await api.patch(`/tasks/${taskId}`, {
      completed: newStatus,
    });

    if (newStatus) {
      toast.success('Great job! Task completed! 🎉', {
        icon: '✅',
      });
    } else {
      toast('Task marked as incomplete', {
        icon: '⏳',
      });
    }

    refetchTasks();
  } catch (error) {
    // Error shown by interceptor
    console.error('Task update failed:', error);
  }
}
```

### Example 4: File Upload with Progress

```tsx
import api from '@/lib/api';
import toast from 'react-hot-toast';

async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  const toastId = toast.loading('Uploading document...');

  try {
    const response = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          toast.loading(`Uploading... ${percentCompleted}%`, { id: toastId });
        }
      },
    });

    toast.success('Document uploaded successfully!', { id: toastId });
    return response.data;
  } catch (error) {
    toast.dismiss(toastId);
    // Error shown by interceptor
    console.error('Upload failed:', error);
  }
}
```

### Example 5: Form Submission

```tsx
import api from '@/lib/api';
import toast from 'react-hot-toast';
import { useState } from 'react';

function ProfileForm() {
  const [formData, setFormData] = useState({ name: '', age: 0 });
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    // Validation
    if (!formData.name) {
      toast.error('Name is required');
      return;
    }

    if (formData.age < 18) {
      toast.error('You must be at least 18 years old');
      return;
    }

    setSaving(true);
    try {
      await api.put('/profile/me', formData);
      toast.success('Profile updated successfully!');
    } catch (error) {
      // Error shown by interceptor
      console.error('Save failed:', error);
    } finally {
      setSaving(false);
    }
  }

  return (/* form JSX */);
}
```

---

## Advanced Usage

### Suppress Error Toast for Specific Requests

Sometimes you want to handle errors manually without showing the automatic toast:

```tsx
// Option 1: Use apiSilent
import { apiSilent } from '@/lib/api';

try {
  const data = await apiSilent(api.get('/optional-data'));
} catch (error) {
  // Handle error manually without toast
  handleError(error);
}

// Option 2: Add suppressErrorToast config (if implemented)
try {
  const response = await api.get('/data', {
    suppressErrorToast: true
  });
} catch (error) {
  // Handle manually
  toast.error('Custom error message');
}
```

### Retry Failed Requests

```tsx
async function fetchWithRetry(url: string, retries = 3): Promise<any> {
  try {
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    if (retries > 0) {
      toast('Retrying...', { icon: '🔄' });
      await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1s
      return fetchWithRetry(url, retries - 1);
    }
    throw error;
  }
}
```

### Batch Operations

```tsx
import api from '@/lib/api';
import toast from 'react-hot-toast';

async function deleteMult ipleTasks(taskIds: string[]) {
  const toastId = toast.loading(`Deleting ${taskIds.length} tasks...`);

  try {
    await Promise.all(
      taskIds.map(id => api.delete(`/tasks/${id}`))
    );

    toast.success(`${taskIds.length} tasks deleted!`, { id: toastId });
    refetchTasks();
  } catch (error) {
    toast.error('Failed to delete some tasks', { id: toastId });
    // Individual errors already shown by interceptor
  }
}
```

---

## Testing Error Handling

### Test Different Error Scenarios

1. **401 Unauthorized**
   - Manually clear your token
   - Make any API request
   - Should show "Session expired" and redirect to login

2. **Network Error**
   - Turn off your backend server
   - Try any operation
   - Should show "Network error"

3. **Timeout**
   - Set a very short timeout in api.ts (e.g., 100ms)
   - Try loading large data
   - Should show "Request timed out"

4. **500 Server Error**
   - Trigger a server error (bad data, etc.)
   - Should show "Server error. Please try again later."

5. **Validation Error (422)**
   - Submit invalid data
   - Should show validation error message

---

## Configuration

### Timeout Settings

Default timeout is 30 seconds. Adjust in `lib/api.ts`:

```tsx
export const api = axios.create({
  baseURL,
  withCredentials: false,
  timeout: 30000, // Change this (in milliseconds)
});
```

### Custom Error Messages

Edit the error interceptor in `lib/api.ts` to customize messages:

```tsx
case 500:
  toast.error('Oops! Something went wrong on our end. 😅');
  break;
```

---

## Best Practices

### ✅ DO

1. **Always use try-catch** for API calls
   ```tsx
   try {
     await api.post('/data', payload);
   } catch (error) {
     console.error('Operation failed:', error);
   }
   ```

2. **Show loading states** for user feedback
   ```tsx
   const [loading, setLoading] = useState(false);
   // Set loading before API call
   ```

3. **Log errors** for debugging
   ```tsx
   catch (error) {
     console.error('Detailed error:', error);
   }
   ```

4. **Use apiWithLoading** for user actions
   ```tsx
   apiWithLoading(promise, 'Saving...', 'Saved!');
   ```

5. **Add client-side validation** before API calls
   ```tsx
   if (!email) {
     toast.error('Email is required');
     return;
   }
   ```

### ❌ DON'T

1. **Don't show double error messages**
   ```tsx
   // Bad - error shown twice!
   catch (error) {
     toast.error('Failed'); // Interceptor already shows error
   }
   ```

2. **Don't ignore errors silently**
   ```tsx
   // Bad
   try {
     await api.post('/data');
   } catch {} // Empty catch - no logging!
   ```

3. **Don't hardcode error messages**
   ```tsx
   // Bad
   toast.error('Error 500');

   // Good - let interceptor handle it
   // It shows: "Server error. Please try again later."
   ```

4. **Don't block UI indefinitely**
   ```tsx
   // Always have finally block to reset loading
   finally {
     setLoading(false);
   }
   ```

---

## Troubleshooting

### Toast Not Showing

**Problem**: API errors don't show toasts

**Solutions**:
1. Check ToastProvider is in App.tsx
2. Ensure `import toast from 'react-hot-toast'` in api.ts
3. Check browser console for JavaScript errors

### Double Toast Messages

**Problem**: Two error toasts appear

**Solution**:
- Remove manual `toast.error()` in catch block
- Let interceptor handle it

### Wrong Error Message

**Problem**: Generic error instead of specific message

**Solution**:
- Check server returns proper error format: `{ message: "..." }`
- Or `{ detail: "..." }` for FastAPI
- Update interceptor to parse your API's error format

---

## Summary

Your API error handling system:

✅ **Centralized** - All errors handled in one place
✅ **User-Friendly** - Clear, helpful messages
✅ **Automatic** - No need to handle errors in every component
✅ **Flexible** - Options for loading toasts, silent calls, custom handling
✅ **Production-Ready** - Handles all edge cases (network, timeout, auth, etc.)

**Result**: Better UX, less code duplication, easier maintenance!

---

## Quick Reference

| Function | Use Case | Shows Toast? |
|----------|----------|--------------|
| `api.get()`, `api.post()`, etc. | Normal API calls | ❌ On error (auto) |
| `apiWithLoading()` | User actions needing feedback | ✅ Loading, ✅ Success, ❌ Error |
| `apiSilent()` | Background operations | ❌ Never |
| `toast.success()` | Custom success messages | ✅ Success only |

**Need help?** Check [ERROR-HANDLING-GUIDE.md](ERROR-HANDLING-GUIDE.md) for React error boundaries!
