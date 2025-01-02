import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

export const useGoalsStore = defineStore('goals', {
  state: () => ({
    goals: {
      BIG: [],
      MTG: [],
      DP: []
    },
    dailyProgress: [],
    loading: false,
    error: null,
    stats: {
      totalGoals: 0,
      completedGoals: 0,
      completionRate: 0,
      activeProcesses: 0
    }
  }),

  getters: {
    bigGoals: (state) => state.goals.BIG || [],
    mediumTermGoals: (state) => state.goals.MTG || [],
    dailyProcesses: (state) => state.goals.DP || [],

    getGoalById: (state) => (id) => {
      return [...state.goals.BIG, ...state.goals.MTG, ...state.goals.DP]
        .find(goal => goal.id === id)
    },

    getChildGoals: (state) => (parentId) => {
      return [...state.goals.MTG, ...state.goals.DP]
        .filter(goal => goal.parent === parentId)
    },

    activeGoals: (state) => {
      return [...state.goals.BIG, ...state.goals.MTG, ...state.goals.DP]
        .filter(goal => !goal.is_completed)
    },

    getTodayProcessProgress: (state) => (processId) => {
      return state.dailyProgress.find(progress => progress.process === processId)
    }
  },

  actions: {
    async fetchAllGoals() {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const [bigResponse, mtgResponse, dpResponse] = await Promise.all([
          axios.get('/goals/type/BIG/', {
            headers: authStore.getAuthHeader()
          }),
          axios.get('/goals/type/MTG/', {
            headers: authStore.getAuthHeader()
          }),
          axios.get('/goals/type/DP/', {
            headers: authStore.getAuthHeader()
          })
        ])

        // Initialize with empty arrays
        const goals = {
          BIG: [],
          MTG: [],
          DP: []
        }

        // Handle both paginated and non-paginated responses
        goals.BIG = Array.isArray(bigResponse.data) ? bigResponse.data : (bigResponse.data.results || [])
        goals.MTG = Array.isArray(mtgResponse.data) ? mtgResponse.data : (mtgResponse.data.results || [])
        goals.DP = Array.isArray(dpResponse.data) ? dpResponse.data : (dpResponse.data.results || [])

        this.goals = goals
        console.log('Fetched goals:', this.goals)
      } catch (error) {
        console.error('Error fetching goals:', error.response || error)
        this.error = error.response?.data || 'Failed to fetch goals'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createGoal(goalData) {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const response = await axios.post('/goals/', goalData, {
          headers: authStore.getAuthHeader()
        })
        this.goals[response.data.goal_type].push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to create goal'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateGoal(goalId, goalData) {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const response = await axios.put(`/goals/${goalId}/`, goalData, {
          headers: authStore.getAuthHeader()
        })
        
        // Update goal in appropriate array
        const goalType = response.data.goal_type
        const index = this.goals[goalType].findIndex(g => g.id === goalId)
        if (index !== -1) {
          this.goals[goalType][index] = response.data
        }
        
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to update goal'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchTodayProgress() {
      const authStore = useAuthStore()
      this.loading = true
      try {
        const today = new Date().toISOString().split('T')[0]
        const response = await axios.get(`/goals/daily-progress/date/${today}/`, {
          headers: authStore.getAuthHeader()
        })
        console.log('Daily progress response:', response.data)
        this.dailyProgress = response.data.process_progress || []
        console.log('Processed daily progress:', this.dailyProgress)
      } catch (error) {
        console.error('Error fetching daily progress:', error.response || error)
        this.error = error.response?.data || 'Failed to fetch today\'s progress'
        throw error
      } finally {
        this.loading = false
      }
    },

    async toggleProcessCompletion(progressId, isCompleted, timeSpent = null) {
      const authStore = useAuthStore()
      try {
        console.log('Toggling process completion:', { progressId, isCompleted, timeSpent })
        const data = { is_completed: isCompleted }
        if (timeSpent !== null && timeSpent !== undefined) {
          data.time_spent_minutes = timeSpent
        }

        console.log('Sending PATCH request with data:', data)
        const response = await axios.patch(
          `/goals/process-progress/${progressId}/`,
          data,
          { headers: authStore.getAuthHeader() }
        )
        console.log('Process progress update response:', response.data)
        
        const index = this.dailyProgress.findIndex(p => p.id === progressId)
        if (index !== -1) {
          this.dailyProgress[index] = response.data
        }
        
        await this.fetchStats()
        return response.data
      } catch (error) {
        console.error('Error updating process progress:', error.response || error)
        this.error = error.response?.data || 'Failed to update progress'
        throw error
      }
    },

    async fetchStats() {
      const authStore = useAuthStore()
      try {
        const [completionResponse, chainResponse] = await Promise.all([
          axios.get('/goals/analytics/goal-completion/', {
            headers: authStore.getAuthHeader()
          }),
          axios.get('/goals/analytics/goal-chain-health/', {
            headers: authStore.getAuthHeader()
          })
        ])

        this.stats = {
          totalGoals: completionResponse.data.total_goals,
          completedGoals: completionResponse.data.completed_goals,
          completionRate: Math.round(completionResponse.data.completion_rate),
          chainHealth: chainResponse.data
        }
      } catch (error) {
        this.error = error.response?.data || 'Failed to fetch stats'
        throw error
      }
    },

    async completeGoal(goalId) {
      const authStore = useAuthStore()
      try {
        const response = await axios.patch(
          `/goals/${goalId}/`,
          {
            is_completed: true,
            completion_date: new Date().toISOString().split('T')[0]
          },
          { headers: authStore.getAuthHeader() }
        )
        
        // Update goal in appropriate array
        const goalType = response.data.goal_type
        const index = this.goals[goalType].findIndex(g => g.id === goalId)
        if (index !== -1) {
          this.goals[goalType][index] = response.data
        }
        
        await this.fetchStats()
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to complete goal'
        throw error
      }
    },

    clearError() {
      this.error = null
    }
  }
})
