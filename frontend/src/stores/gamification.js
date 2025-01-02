import { defineStore } from 'pinia'
import { useAuthStore } from './auth'
import axios from 'axios'

export const useGamificationStore = defineStore('gamification', {
  state: () => ({
    stats: {
      profile: {
        total_points: 0,
        level: 1,
        current_streak: 0,
        longest_streak: 0
      },
      recent_achievements: [],
      recent_transactions: [],
      next_level_points: 100,
      progress_to_next_level: 0
    },
    achievements: [],
    availableAchievements: [],
    loading: false,
    error: null
  }),

  actions: {
    async fetchStats() {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const response = await axios.get('/gamification/stats/', {
          headers: authStore.getAuthHeader()
        })
        this.stats = response.data
      } catch (error) {
        console.error('Error fetching gamification stats:', error)
        this.error = error.response?.data || 'Failed to fetch gamification stats'
      } finally {
        this.loading = false
      }
    },

    async fetchAchievements() {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const [achievementsResponse, availableResponse] = await Promise.all([
          axios.get('/gamification/achievements/', {
            headers: authStore.getAuthHeader()
          }),
          axios.get('/gamification/achievements/available/', {
            headers: authStore.getAuthHeader()
          })
        ])
        this.achievements = achievementsResponse.data
        this.availableAchievements = availableResponse.data
      } catch (error) {
        console.error('Error fetching achievements:', error)
        this.error = error.response?.data || 'Failed to fetch achievements'
      } finally {
        this.loading = false
      }
    },

    async fetchPointHistory(days = 30) {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const response = await axios.get(`/gamification/points/history/?days=${days}`, {
          headers: authStore.getAuthHeader()
        })
        return response.data
      } catch (error) {
        console.error('Error fetching point history:', error)
        this.error = error.response?.data || 'Failed to fetch point history'
      } finally {
        this.loading = false
      }
    },

    clearError() {
      this.error = null
    }
  }
})
