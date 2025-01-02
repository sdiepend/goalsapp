import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

export const useReflectionsStore = defineStore('reflections', {
  state: () => ({
    reflections: {
      weekly: [],
      monthly: [],
      quarterly: [],
      yearly: []
    },
    currentReflection: null,
    loading: false,
    error: null
  }),

  getters: {
    weeklyReflections: (state) => state.reflections.weekly,
    monthlyReflections: (state) => state.reflections.monthly,
    quarterlyReflections: (state) => state.reflections.quarterly,
    yearlyReflections: (state) => state.reflections.yearly,

    getReflectionById: (state) => (id) => {
      return Object.values(state.reflections)
        .flat()
        .find(reflection => reflection.id === id)
    },

    getReflectionsByDateRange: (state) => (startDate, endDate) => {
      const start = new Date(startDate)
      const end = new Date(endDate)
      
      return Object.values(state.reflections)
        .flat()
        .filter(reflection => {
          const reflectionDate = new Date(reflection.start_date)
          return reflectionDate >= start && reflectionDate <= end
        })
        .sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
    },

    latestReflections: (state) => {
      const result = {}
      Object.keys(state.reflections).forEach(type => {
        const sorted = [...state.reflections[type]].sort(
          (a, b) => new Date(b.start_date) - new Date(a.start_date)
        )
        result[type] = sorted[0] || null
      })
      return result
    }
  },

  actions: {
    async fetchAllReflections() {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const types = ['weekly', 'monthly', 'quarterly', 'yearly']
        const responses = await Promise.all(
          types.map(type =>
            axios.get(`/goals/reflections/type/${type}/`, {
              headers: authStore.getAuthHeader()
            })
          )
        )

        types.forEach((type, index) => {
          this.reflections[type] = responses[index].data
        })
      } catch (error) {
        this.error = error.response?.data || 'Failed to fetch reflections'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createReflection(reflectionData) {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const response = await axios.post('/goals/reflections/', reflectionData, {
          headers: authStore.getAuthHeader()
        })
        this.reflections[response.data.reflection_type].push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to create reflection'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateReflection(reflectionId, reflectionData) {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const response = await axios.put(
          `/goals/reflections/${reflectionId}/`,
          reflectionData,
          { headers: authStore.getAuthHeader() }
        )
        
        const type = response.data.reflection_type
        const index = this.reflections[type].findIndex(r => r.id === reflectionId)
        if (index !== -1) {
          this.reflections[type][index] = response.data
        }
        
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to update reflection'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchReflection(reflectionId) {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const response = await axios.get(`/goals/reflections/${reflectionId}/`, {
          headers: authStore.getAuthHeader()
        })
        this.currentReflection = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to fetch reflection'
        throw error
      } finally {
        this.loading = false
      }
    },

    generateReflectionPeriod(type) {
      const today = new Date()
      let startDate = new Date()
      let endDate = new Date()

      switch (type) {
        case 'weekly':
          // Start from last Sunday, end on Saturday
          startDate.setDate(today.getDate() - today.getDay())
          endDate.setDate(startDate.getDate() + 6)
          break
        case 'monthly':
          // Start from first day of month, end on last day
          startDate.setDate(1)
          endDate.setMonth(today.getMonth() + 1, 0)
          break
        case 'quarterly':
          // Start from first day of quarter, end on last day
          const quarter = Math.floor(today.getMonth() / 3)
          startDate.setMonth(quarter * 3, 1)
          endDate.setMonth(quarter * 3 + 3, 0)
          break
        case 'yearly':
          // Start from January 1st, end on December 31st
          startDate = new Date(today.getFullYear(), 0, 1)
          endDate = new Date(today.getFullYear(), 11, 31)
          break
      }

      return {
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
      }
    },

    clearCurrentReflection() {
      this.currentReflection = null
    },

    clearError() {
      this.error = null
    }
  }
})
