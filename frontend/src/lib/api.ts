import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';
import { getToken, clearToken } from './auth';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance
export const api = axios.create({
  baseURL,
  withCredentials: false,
  timeout: 30000, // 30 second timeout
});

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken()?.access_token;
    if (token) {
      config.headers = config.headers || {};
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Success response - return as is
    return response;
  },
  (error: AxiosError<{ message?: string; detail?: string }>) => {
    // Extract error information
    const status = error.response?.status;
    const errorMessage = error.response?.data?.message || error.response?.data?.detail || error.message;
    const url = error.config?.url || '';

    console.error('API Error:', {
      status,
      url,
      message: errorMessage,
      error,
    });

    // Handle different error types
    if (error.code === 'ECONNABORTED') {
      // Timeout error
      toast.error('Request timed out. Please check your connection and try again.');
    } else if (error.code === 'ERR_NETWORK') {
      // Network error
      toast.error('Network error. Please check your internet connection.');
    } else if (status) {
      // Server responded with error status
      switch (status) {
        case 400:
          // Bad Request - Show specific error message
          toast.error(errorMessage || 'Invalid request. Please check your input.');
          break;

        case 401:
          // Unauthorized - Clear token and redirect to login
          clearToken();
          toast.error('Your session has expired. Please login again.');
          if (typeof window !== 'undefined') {
            // Only redirect if not already on login page
            if (!window.location.pathname.includes('/login')) {
              window.location.href = '/login';
            }
          }
          break;

        case 403:
          // Forbidden
          toast.error('You do not have permission to perform this action.');
          break;

        case 404:
          // Not Found
          toast.error('Resource not found.');
          break;

        case 409:
          // Conflict - e.g., duplicate email
          toast.error(errorMessage || 'This resource already exists.');
          break;

        case 422:
          // Validation Error
          toast.error(errorMessage || 'Validation failed. Please check your input.');
          break;

        case 429:
          // Too Many Requests
          toast.error('Too many requests. Please slow down and try again later.');
          break;

        case 500:
          // Internal Server Error
          toast.error('Server error. Please try again later.');
          break;

        case 502:
          // Bad Gateway
          toast.error('Server is temporarily unavailable. Please try again.');
          break;

        case 503:
          // Service Unavailable
          toast.error('Service is temporarily unavailable. Please try again later.');
          break;

        default:
          // Generic error
          toast.error(errorMessage || 'An unexpected error occurred. Please try again.');
      }
    } else if (error.request) {
      // Request was made but no response received
      toast.error('No response from server. Please check your connection.');
    } else {
      // Something else happened
      toast.error('An unexpected error occurred. Please try again.');
    }

    return Promise.reject(error);
  }
);

/**
 * API call wrapper with loading toast
 * Use this for operations that should show loading feedback
 *
 * @example
 * const data = await apiWithLoading(
 *   api.post('/plans/generate', planData),
 *   'Generating plan...',
 *   'Plan generated successfully!'
 * );
 */
export const apiWithLoading = async <T,>(
  promise: Promise<AxiosResponse<T>>,
  loadingMessage: string = 'Loading...',
  successMessage?: string
): Promise<T> => {
  try {
    const response = await toast.promise(
      promise,
      {
        loading: loadingMessage,
        success: successMessage || 'Success!',
        error: 'Operation failed', // This won't show since we handle it in interceptor
      },
      {
        success: {
          duration: 3000,
        },
      }
    );
    return response.data;
  } catch (error) {
    // Error already handled by interceptor
    throw error;
  }
};

/**
 * Silent API call - doesn't show toast notifications
 * Use this for background operations or when you want to handle errors manually
 *
 * @example
 * try {
 *   const data = await apiSilent(api.get('/notifications'));
 *   // Handle success
 * } catch (error) {
 *   // Handle error manually
 * }
 */
export const apiSilent = async <T,>(
  promise: Promise<AxiosResponse<T>>
): Promise<T> => {
  const response = await promise;
  return response.data;
};

/**
 * Disable error toast for specific request
 * Add this config to axios request to suppress automatic error toasts
 *
 * @example
 * api.get('/optional-endpoint', { suppressErrorToast: true })
 */
declare module 'axios' {
  export interface AxiosRequestConfig {
    suppressErrorToast?: boolean;
  }
}

export default api; 