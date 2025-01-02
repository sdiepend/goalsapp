import { defineStore } from 'pinia'
import axios from 'axios'

// Use the global axios instance
const apiClient = axios

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    getUser: (state) => state.user,
    getError: (state) => state.error
  },

  actions: {
    async login(credentials) {
      this.loading = true
      this.error = null
      try {
        const response = await apiClient.post('/token/', credentials)
        this.setTokens(response.data)
        await this.fetchUser()
        return true
      } catch (error) {
        this.error = error.response?.data?.detail || 'Login failed'
        return false
      } finally {
        this.loading = false
      }
    },

    async register(userData) {
      this.loading = true
      this.error = null
      try {
        await apiClient.post('/users/register/', userData)
        return await this.login({
          username: userData.username,
          password: userData.password
        })
      } catch (error) {
        this.error = error.response?.data || 'Registration failed'
        return false
      } finally {
        this.loading = false
      }
    },

    async fetchUser() {
      this.loading = true
      try {
        const response = await apiClient.get('/users/profile/', {
          headers: this.getAuthHeader()
        })
        this.user = response.data
      } catch (error) {
        if (error.response?.status === 401) {
          await this.refreshAccessToken()
          return this.fetchUser()
        }
        this.error = error.response?.data?.detail || 'Failed to fetch user data'
      } finally {
        this.loading = false
      }
    },

    async refreshAccessToken() {
      try {
        const response = await apiClient.post('/token/refresh/', {
          refresh: this.refreshToken
        })
        this.token = response.data.access
        localStorage.setItem('token', response.data.access)
        return true
      } catch (error) {
        this.logout()
        return false
      }
    },

    async updateProfile(profileData) {
      this.loading = true
      this.error = null
      try {
        const response = await apiClient.put(
          '/users/profile/update/',
          profileData,
          { headers: this.getAuthHeader() }
        )
        this.user = response.data
        return true
      } catch (error) {
        this.error = error.response?.data || 'Failed to update profile'
        return false
      } finally {
        this.loading = false
      }
    },

    async updateSettings(settings) {
      this.loading = true
      this.error = null
      try {
        const response = await apiClient.put(
          '/users/settings/',
          settings,
          { headers: this.getAuthHeader() }
        )
        this.user = response.data
        return true
      } catch (error) {
        this.error = error.response?.data || 'Failed to update settings'
        return false
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
    },

    setTokens(data) {
      this.token = data.access
      this.refreshToken = data.refresh
      localStorage.setItem('token', data.access)
      localStorage.setItem('refreshToken', data.refresh)
    },

    getAuthHeader() {
      return {
        Authorization: `Bearer ${this.token}`
      }
    }
  }
})

// Flag to track if token refresh is in progress
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Axios interceptor for automatic token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue the request if refresh is in progress
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return apiClient(originalRequest)
          })
          .catch(err => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      const authStore = useAuthStore()
      try {
        const refreshed = await authStore.refreshAccessToken()
        if (refreshed) {
          processQueue(null, authStore.token)
          originalRequest.headers.Authorization = `Bearer ${authStore.token}`
          return apiClient(originalRequest)
        }
        processQueue(new Error('Failed to refresh token'))
        return Promise.reject(error)
      } catch (refreshError) {
        processQueue(refreshError)
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)
