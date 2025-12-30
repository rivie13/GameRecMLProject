import axios from 'axios'
import toast from 'react-hot-toast'

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 60000, // Increased to 60 seconds for ML predictions
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response
      
      if (status === 401) {
        // Unauthorized - clear token and redirect to home
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        window.location.href = '/'
        toast.error('Session expired. Please log in again.')
      } else if (status === 403) {
        toast.error('Access denied')
      } else if (status === 404) {
        toast.error('Resource not found')
      } else if (status === 429) {
        toast.error('Too many requests. Please try again later.')
      } else if (status >= 500) {
        toast.error('Server error. Please try again later.')
      } else {
        toast.error(data.detail || 'An error occurred')
      }
    } else if (error.request) {
      // Request made but no response received
      toast.error('Network error. Please check your connection.')
    } else {
      // Something else happened
      toast.error('An unexpected error occurred')
    }
    
    return Promise.reject(error)
  }
)

// API endpoint functions
export const api = {
  // Auth
  auth: {
    getMe: () => apiClient.get('/api/auth/me'),
    logout: () => apiClient.post('/api/auth/logout'),
  },
  
  // Profile
  profile: {
    get: (steamId) => apiClient.get(`/api/profile/${steamId}`),
    getStats: (steamId) => apiClient.get(`/api/profile/${steamId}/stats`),
    sync: (steamId) => apiClient.post(`/api/profile/${steamId}/sync`),
  },
  
  // Recommendations
  recommendations: {
    get: (steamId, params = {}) => 
      apiClient.get(`/api/recommendations/${steamId}`, { params }),
    explain: (steamId, appid) => 
      apiClient.get(`/api/recommendations/${steamId}/explain/${appid}`),
  },
  
  // Feedback
  feedback: {
    submit: (data) => apiClient.post('/api/feedback', data),
  },
  
  // Catalog
  catalog: {
    getGame: (appid) => apiClient.get(`/api/catalog/${appid}`),
  },
}

export default apiClient
