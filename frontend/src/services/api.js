import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// User API
export const userAPI = {
  create: (userData) => api.post('/api/users', userData),
  get: (userId) => api.get(`/api/users/${userId}`),
}

// Portfolio API
export const portfolioAPI = {
  get: (userId) => api.get(`/api/users/${userId}/portfolio`),
  reset: (userId) => api.post(`/api/users/${userId}/portfolio/reset`),
}

// Trading API
export const tradingAPI = {
  executeTrade: (userId, tradeData) => api.post(`/api/users/${userId}/trades`, tradeData),
  getHistory: (userId) => api.get(`/api/users/${userId}/trades`),
}

// Forex API
export const forexAPI = {
  getExchangeRate: () => api.get('/api/forex/usd-inr'),
  getChartData: (interval = '5min', outputsize = 'compact') => 
    api.get(`/api/forex/chart-data?interval=${interval}&outputsize=${outputsize}`),
}

// Chat API
export const chatAPI = {
  sendMessage: (userId, message) => api.post(`/api/users/${userId}/chat`, { content: message }),
  getHistory: (userId, limit = 50) => api.get(`/api/users/${userId}/chat?limit=${limit}`),
}

export default api