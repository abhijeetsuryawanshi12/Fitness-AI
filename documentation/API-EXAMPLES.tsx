/**
 * API Error Handling - Code Examples
 * Copy and paste these examples into your components
 */

import { useState } from 'react';
import api, { apiWithLoading, apiSilent } from '@/lib/api';
import toast from 'react-hot-toast';

// ============================================================================
// EXAMPLE 1: Plan Generation with Loading Toast
// ============================================================================
export function ExamplePlanGeneration() {
  const [plan, setPlan] = useState(null);
  const [generating, setGenerating] = useState(false);

  async function generatePlan(planType: 'workout' | 'diet' | 'combined') {
    setGenerating(true);
    try {
      const data = await apiWithLoading(
        api.post('/plans/generate', {
          plan_type: planType,
          duration: 7,
        }),
        `Generating your ${planType} plan... This may take 30 seconds.`,
        `${planType.charAt(0).toUpperCase() + planType.slice(1)} plan generated successfully!`
      );

      setPlan(data);
    } catch (error) {
      // Error already shown by interceptor
      console.error('Plan generation failed:', error);
    } finally {
      setGenerating(false);
    }
  }

  return (
    <button onClick={() => generatePlan('workout')} disabled={generating}>
      {generating ? 'Generating...' : 'Generate Workout Plan'}
    </button>
  );
}

// ============================================================================
// EXAMPLE 2: Task Completion Toggle
// ============================================================================
export function ExampleTaskCompletion() {
  async function toggleTask(taskId: string, currentStatus: boolean) {
    const newStatus = !currentStatus;

    try {
      await api.patch(`/tasks/${taskId}`, {
        completed: newStatus,
      });

      if (newStatus) {
        toast.success('Great job! Task completed! 🎉', {
          icon: '✅',
          duration: 3000,
        });
      } else {
        toast('Task marked as incomplete', {
          icon: '⏳',
        });
      }

      // Refetch or update local state
    } catch (error) {
      // Error already handled by interceptor
      console.error('Task update failed:', error);
    }
  }

  return <button onClick={() => toggleTask('task-123', false)}>Complete Task</button>;
}

// ============================================================================
// EXAMPLE 3: Task Deletion with Confirmation
// ============================================================================
export function ExampleTaskDeletion() {
  async function deleteTask(taskId: string) {
    // Show confirmation toast
    toast((t) => (
      <div className="flex items-center gap-3">
        <span className="text-white">Delete this task?</span>
        <button
          onClick={async () => {
            toast.dismiss(t.id);

            try {
              await api.delete(`/tasks/${taskId}`);
              toast.success('Task deleted successfully!');
              // Refetch tasks
            } catch (error) {
              // Error shown by interceptor
              console.error('Delete failed:', error);
            }
          }}
          className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm font-medium text-white transition-colors"
        >
          Delete
        </button>
        <button
          onClick={() => toast.dismiss(t.id)}
          className="px-3 py-1 bg-gray-600 hover:bg-gray-700 rounded text-sm font-medium text-white transition-colors"
        >
          Cancel
        </button>
      </div>
    ), {
      duration: 6000,
      style: {
        background: '#1e293b',
      },
    });
  }

  return <button onClick={() => deleteTask('task-123')}>Delete Task</button>;
}

// ============================================================================
// EXAMPLE 4: Document Upload with Progress
// ============================================================================
export function ExampleDocumentUpload() {
  const [uploading, setUploading] = useState(false);

  async function uploadDocument(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const toastId = toast.loading('Uploading document...');
    setUploading(true);

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
    } finally {
      setUploading(false);
    }
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      uploadDocument(file);
    }
  }

  return (
    <input
      type="file"
      accept=".pdf,.doc,.docx"
      onChange={handleFileChange}
      disabled={uploading}
    />
  );
}

// ============================================================================
// EXAMPLE 5: Profile Form Submission
// ============================================================================
export function ExampleProfileForm() {
  const [formData, setFormData] = useState({
    name: '',
    age: 0,
    email: '',
  });
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    // Client-side validation
    if (!formData.name.trim()) {
      toast.error('Name is required');
      return;
    }

    if (formData.age < 18) {
      toast.error('You must be at least 18 years old');
      return;
    }

    if (!formData.email.includes('@')) {
      toast.error('Please enter a valid email address');
      return;
    }

    setSaving(true);
    try {
      await api.put('/profile/me', formData);
      toast.success('Profile updated successfully!');
    } catch (error) {
      // Error shown by interceptor (e.g., duplicate email -> 409)
      console.error('Save failed:', error);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        placeholder="Name"
        required
      />
      <input
        type="number"
        value={formData.age}
        onChange={(e) => setFormData({ ...formData, age: parseInt(e.target.value) })}
        placeholder="Age"
        required
      />
      <input
        type="email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        placeholder="Email"
        required
      />
      <button type="submit" disabled={saving}>
        {saving ? 'Saving...' : 'Save Profile'}
      </button>
    </form>
  );
}

// ============================================================================
// EXAMPLE 6: Fetching Data with Loading State
// ============================================================================
export function ExampleDataFetching() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);

  async function fetchTasks() {
    setLoading(true);
    try {
      const response = await api.get('/tasks');
      setTasks(response.data);
    } catch (error) {
      // Error shown by interceptor
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  }

  // Fetch on component mount
  // useEffect(() => {
  //   fetchTasks();
  // }, []);

  if (loading) return <div>Loading tasks...</div>;

  return (
    <div>
      <button onClick={fetchTasks}>Refresh Tasks</button>
      {tasks.map((task: any) => (
        <div key={task.id}>{task.title}</div>
      ))}
    </div>
  );
}

// ============================================================================
// EXAMPLE 7: Background Polling (Silent API)
// ============================================================================
export function ExampleBackgroundPolling() {
  async function checkNotifications() {
    try {
      // Silent API call - no toast on error
      const data = await apiSilent(api.get('/notifications/unread'));
      updateBadgeCount(data.count);
    } catch (error) {
      // Handle silently - maybe just log
      console.log('Notification check failed:', error);
    }
  }

  function updateBadgeCount(count: number) {
    // Update UI badge
  }

  // Poll every 30 seconds
  // useEffect(() => {
  //   const interval = setInterval(checkNotifications, 30000);
  //   return () => clearInterval(interval);
  // }, []);

  return <button onClick={checkNotifications}>Check Notifications</button>;
}

// ============================================================================
// EXAMPLE 8: Batch Operations
// ============================================================================
export function ExampleBatchOperations() {
  async function deleteMultipleTasks(taskIds: string[]) {
    if (taskIds.length === 0) {
      toast.error('No tasks selected');
      return;
    }

    const toastId = toast.loading(`Deleting ${taskIds.length} tasks...`);

    try {
      // Delete all tasks in parallel
      await Promise.all(
        taskIds.map(id => api.delete(`/tasks/${id}`))
      );

      toast.success(`Successfully deleted ${taskIds.length} tasks!`, { id: toastId });
      // Refetch tasks
    } catch (error) {
      toast.error('Failed to delete some tasks', { id: toastId });
      // Individual errors already logged by interceptor
      console.error('Batch delete failed:', error);
    }
  }

  return <button onClick={() => deleteMultipleTasks(['1', '2', '3'])}>Delete Selected</button>;
}

// ============================================================================
// EXAMPLE 9: Retry Failed Requests
// ============================================================================
export function ExampleRetryLogic() {
  async function fetchWithRetry(url: string, retries = 3): Promise<any> {
    try {
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      if (retries > 0) {
        toast(`Retrying... (${4 - retries}/3)`, { icon: '🔄' });
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1s
        return fetchWithRetry(url, retries - 1);
      }
      throw error; // All retries exhausted
    }
  }

  async function loadImportantData() {
    try {
      const data = await fetchWithRetry('/important-endpoint');
      // Use data
    } catch (error) {
      toast.error('Failed after 3 retries. Please try again later.');
      console.error('Failed with retries:', error);
    }
  }

  return <button onClick={loadImportantData}>Load Important Data</button>;
}

// ============================================================================
// EXAMPLE 10: Chat Message Sending
// ============================================================================
export function ExampleChatMessage() {
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);

  async function sendMessage() {
    if (!message.trim()) {
      toast.error('Please enter a message');
      return;
    }

    setSending(true);
    try {
      const response = await api.post('/chat/message', {
        message: message,
      });

      // Clear input on success
      setMessage('');

      // Optional: Show success feedback
      // toast.success('Message sent');

      return response.data;
    } catch (error) {
      // Error shown by interceptor
      console.error('Send failed:', error);
    } finally {
      setSending(false);
    }
  }

  return (
    <div>
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message..."
        disabled={sending}
      />
      <button onClick={sendMessage} disabled={sending}>
        {sending ? 'Sending...' : 'Send'}
      </button>
    </div>
  );
}

// ============================================================================
// EXAMPLE 11: Weight Logging
// ============================================================================
export function ExampleWeightLogging() {
  const [weight, setWeight] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [saving, setSaving] = useState(false);

  async function logWeight() {
    const weightNum = parseFloat(weight);

    if (isNaN(weightNum) || weightNum <= 0) {
      toast.error('Please enter a valid weight');
      return;
    }

    setSaving(true);
    try {
      await api.post('/progress/weight', {
        weight: weightNum,
        date: date,
        unit: 'kg',
      });

      toast.success('Weight logged successfully! 📊');
      setWeight('');
    } catch (error) {
      // Error shown by interceptor
      console.error('Weight log failed:', error);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <input
        type="number"
        value={weight}
        onChange={(e) => setWeight(e.target.value)}
        placeholder="Weight (kg)"
        step="0.1"
      />
      <input
        type="date"
        value={date}
        onChange={(e) => setDate(e.target.value)}
      />
      <button onClick={logWeight} disabled={saving}>
        {saving ? 'Logging...' : 'Log Weight'}
      </button>
    </div>
  );
}

// ============================================================================
// EXAMPLE 12: Search with Debounce
// ============================================================================
export function ExampleSearchWithDebounce() {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);

  // Debounce search
  // useEffect(() => {
  //   const timer = setTimeout(() => {
  //     if (searchQuery.length >= 3) {
  //       performSearch(searchQuery);
  //     }
  //   }, 500);
  //   return () => clearTimeout(timer);
  // }, [searchQuery]);

  async function performSearch(query: string) {
    setSearching(true);
    try {
      const response = await api.get(`/search?q=${encodeURIComponent(query)}`);
      setResults(response.data);
    } catch (error) {
      // Error shown by interceptor
      setResults([]);
      console.error('Search failed:', error);
    } finally {
      setSearching(false);
    }
  }

  return (
    <div>
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search..."
      />
      {searching && <div>Searching...</div>}
      {results.map((result: any) => (
        <div key={result.id}>{result.title}</div>
      ))}
    </div>
  );
}
