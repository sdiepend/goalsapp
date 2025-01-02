import { defineStore } from 'pinia'
import { useAuthStore } from './auth'
import axios from 'axios'

const apiClient = axios

export const useStandardsStore = defineStore('standards', {
  state: () => ({
    categories: [],
    standards: [],
    todayProgress: [],
    loading: false,
    error: null,
    stats: {
      completionRate: 0,
      currentStreak: 0,
      totalStandards: 0,
      activeStandards: 0
    }
  }),

  getters: {
    standardsByCategory: (state) => {
      if (!Array.isArray(state.standards)) {
        return {}
      }
      return state.standards.reduce((grouped, standard) => {
        const categoryName = standard.category ? standard.category.name : 'Uncategorized'
        
        if (!grouped[categoryName]) {
          grouped[categoryName] = []
        }
        grouped[categoryName].push(standard)
        return grouped
      }, {})
    },

    activeStandards: (state) => {
      return state.standards.filter(standard => standard.is_active)
    },

    getTodayProgressByStandard: (state) => (standardId) => {
      return state.todayProgress.find(progress => progress.standard === standardId)
    },

    getDailyStandards: (state) => {
      return state.todayProgress.filter(progress => {
        const standard = state.standards.find(s => s.id === progress.standard)
        return standard && standard.frequency === 'daily'
      })
    },

    getWeeklyStandards: (state) => {
      return state.todayProgress.filter(progress => {
        const standard = state.standards.find(s => s.id === progress.standard)
        return standard && standard.frequency === 'weekly'
      })
    }
  },

  actions: {
    async fetchCategories() {
      const authStore = useAuthStore()
      this.loading = true
      try {
        console.log('Fetching categories...')
        const response = await apiClient.get('/standards/categories/', {
          headers: authStore.getAuthHeader()
        })
        console.log('Categories response:', response.data)
        this.categories = response.data
        console.log('Processed categories:', this.categories)
      } catch (error) {
        console.error('Error fetching categories:', error.response || error)
        this.error = error.response?.data || 'Failed to fetch categories'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createCategory(categoryData) {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const response = await apiClient.post('/standards/categories/', categoryData, {
          headers: authStore.getAuthHeader()
        })
        this.categories.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to create category'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchStandards() {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const response = await apiClient.get('/standards/', {
          headers: authStore.getAuthHeader()
        })
        this.standards = response.data.results || []
      } catch (error) {
        this.error = error.response?.data || 'Failed to fetch standards'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createStandard(standardData) {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const response = await apiClient.post('/standards/', standardData, {
          headers: authStore.getAuthHeader()
        })
        this.standards.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to create standard'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateStandard(standardId, standardData) {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const response = await apiClient.put(`/standards/${standardId}/`, standardData, {
          headers: authStore.getAuthHeader()
        })
        const index = this.standards.findIndex(s => s.id === standardId)
        if (index !== -1) {
          this.standards[index] = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to update standard'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteStandard(standardId) {
      const authStore = useAuthStore()
      try {
        await apiClient.delete(`/standards/${standardId}/`, {
          headers: authStore.getAuthHeader()
        })
        const index = this.standards.findIndex(s => s.id === standardId)
        if (index !== -1) {
          this.standards.splice(index, 1)
        }
      } catch (error) {
        this.error = error.response?.data || 'Failed to delete standard'
        throw error
      }
    },

    async fetchTodayProgress() {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const today = new Date().toISOString().split('T')[0]
        const response = await apiClient.get(`/standards/progress/date/${today}/`, {
          headers: authStore.getAuthHeader()
        })
        this.todayProgress = response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to fetch today\'s progress'
        throw error
      } finally {
        this.loading = false
      }
    },

    async toggleStandardCompletion(progressId, isCompleted) {
      const authStore = useAuthStore()
      try {
        const response = await apiClient.patch(
          `/standards/progress/${progressId}/`,
          { is_completed: isCompleted },
          { headers: authStore.getAuthHeader() }
        )
        const index = this.todayProgress.findIndex(p => p.id === progressId)
        if (index !== -1) {
          this.todayProgress[index] = response.data
        }
        await this.fetchStats()
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to update progress'
        throw error
      }
    },

    async fetchStats() {
      const authStore = useAuthStore()
      try {
        const response = await apiClient.get('/standards/analytics/completion-rate/', {
          headers: authStore.getAuthHeader()
        })
        this.stats = {
          completionRate: Math.round(response.data.completion_rate),
          currentStreak: response.data.current_streak,
          totalStandards: response.data.total_standards,
          completedStandards: response.data.completed_standards
        }
      } catch (error) {
        this.error = error.response?.data || 'Failed to fetch stats'
        throw error
      }
    },

    clearError() {
      this.error = null
    }
  }
})
