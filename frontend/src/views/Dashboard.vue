<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-2xl font-semibold text-gray-900">Dashboard</h1>
      <p class="mt-1 text-sm text-gray-500">
        Overview of your goals, standards, and daily progress
      </p>
    </div>

    <!-- Stats Overview -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5 mb-6">
      <!-- Points Overview -->
      <div class="card overflow-hidden">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <StarIcon class="h-6 w-6 text-yellow-500" aria-hidden="true" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Level {{ gamificationStore.stats.profile.level }}</dt>
                <dd>
                  <div class="text-lg font-medium text-gray-900">{{ gamificationStore.stats.profile.total_points }} pts</div>
                  <div class="text-xs text-gray-500">
                    {{ Math.round(gamificationStore.stats.progress_to_next_level) }}% to next level
                  </div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- Standards Completion Rate -->
      <div class="card overflow-hidden">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <ChartBarIcon class="h-6 w-6 text-primary-600" aria-hidden="true" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Standards Completion Rate</dt>
                <dd>
                  <div class="text-lg font-medium text-gray-900">{{ standardsStore.stats.completionRate }}%</div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="card overflow-hidden">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <FireIcon class="h-6 w-6 text-orange-600" aria-hidden="true" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Current Streak</dt>
                <dd>
                  <div class="text-lg font-medium text-gray-900">{{ standardsStore.stats.currentStreak }} days</div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="card overflow-hidden">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <FlagIcon class="h-6 w-6 text-green-600" aria-hidden="true" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Active Goals</dt>
                <dd>
                  <div class="text-lg font-medium text-gray-900">{{ goalsStore.stats.totalGoals - goalsStore.stats.completedGoals }}</div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="card overflow-hidden">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <CheckCircleIcon class="h-6 w-6 text-indigo-600" aria-hidden="true" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Goals Completed</dt>
                <dd>
                  <div class="text-lg font-medium text-gray-900">{{ goalsStore.stats.completedGoals }}</div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Today's Progress -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2 mb-6">
      <!-- Daily Standards -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-medium text-gray-900">Daily Standards</h2>
        </div>
        <div class="card-body">
          <div v-if="loading" class="flex justify-center py-4">
            <svg class="animate-spin h-5 w-5 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <div v-else-if="!getDailyStandards.length" class="text-center py-4 text-gray-500">
            No daily standards
          </div>
          <ul v-else class="divide-y divide-gray-200">
            <li v-for="progress in getDailyStandards" :key="progress.id" class="py-4">
              <div class="flex items-center space-x-4">
                <div class="flex-shrink-0">
                  <button
                    @click="toggleStandard(progress)"
                    :class="[
                      progress.is_completed ? 'text-green-600' : 'text-gray-400',
                      'hover:text-green-700 focus:outline-none'
                    ]"
                  >
                    <CheckCircleIcon class="h-6 w-6" :class="{ 'fill-current': progress.is_completed }" />
                  </button>
                </div>
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-gray-900">{{ progress.standard_title }}</p>
                  <p class="text-sm text-gray-500">{{ progress.category_name }}</p>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- Weekly Standards -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-medium text-gray-900">Weekly Standards</h2>
        </div>
        <div class="card-body">
          <div v-if="loading" class="flex justify-center py-4">
            <svg class="animate-spin h-5 w-5 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <div v-else-if="!getWeeklyStandards.length" class="text-center py-4 text-gray-500">
            No weekly standards
          </div>
          <ul v-else class="divide-y divide-gray-200">
            <li v-for="progress in getWeeklyStandards" :key="progress.id" class="py-4">
              <div class="flex items-center space-x-4">
                <div class="flex-shrink-0">
                  <button
                    @click="toggleStandard(progress)"
                    :class="[
                      progress.is_completed ? 'text-green-600' : 'text-gray-400',
                      'hover:text-green-700 focus:outline-none'
                    ]"
                  >
                    <CheckCircleIcon class="h-6 w-6" :class="{ 'fill-current': progress.is_completed }" />
                  </button>
                </div>
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-gray-900">{{ progress.standard_title }}</p>
                  <p class="text-sm text-gray-500">{{ progress.category_name }}</p>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- Daily Processes -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-medium text-gray-900">Today's Processes</h2>
        </div>
        <div class="card-body">
          <div v-if="loading" class="flex justify-center py-4">
            <svg class="animate-spin h-5 w-5 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <div v-else-if="!goalsStore.dailyProgress.length" class="text-center py-4 text-gray-500">
            No processes scheduled for today
          </div>
          <ul v-else class="divide-y divide-gray-200">
            <li v-for="progress in goalsStore.dailyProgress" :key="progress.id" class="py-4">
              <div class="flex items-center space-x-4">
                <div class="flex-shrink-0">
                  <button
                    @click="toggleProcess(progress)"
                    :class="[
                      progress.is_completed ? 'text-green-600' : 'text-gray-400',
                      'hover:text-green-700 focus:outline-none'
                    ]"
                  >
                    <CheckCircleIcon class="h-6 w-6" :class="{ 'fill-current': progress.is_completed }" />
                  </button>
                </div>
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-gray-900">{{ progress.process_title }}</p>
                  <p class="text-sm text-gray-500">{{ progress.parent_goal }}</p>
                </div>
                <div class="flex-shrink-0">
                  <span class="text-sm text-gray-500">{{ progress.time_spent_minutes || 0 }} min</span>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- Recent Achievements -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-medium text-gray-900">Recent Achievements</h2>
        </div>
        <div class="card-body">
          <div v-if="loading" class="flex justify-center py-4">
            <svg class="animate-spin h-5 w-5 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <div v-else-if="!gamificationStore.stats.recent_achievements.length" class="text-center py-4 text-gray-500">
            No achievements yet
          </div>
          <ul v-else class="divide-y divide-gray-200">
            <li v-for="achievement in gamificationStore.stats.recent_achievements" :key="achievement.id" class="py-4">
              <div class="flex items-center space-x-4">
                <div class="flex-shrink-0">
                  <div :class="[
                    'h-8 w-8 rounded-full flex items-center justify-center',
                    {
                      'bg-yellow-100': achievement.achievement.achievement_type === 'streak',
                      'bg-green-100': achievement.achievement.achievement_type === 'completion',
                      'bg-blue-100': achievement.achievement.achievement_type === 'level',
                      'bg-purple-100': achievement.achievement.achievement_type === 'special'
                    }
                  ]">
                    <TrophyIcon class="h-5 w-5 text-yellow-600" v-if="achievement.achievement.icon === 'trophy'" />
                    <FireIcon class="h-5 w-5 text-orange-600" v-else-if="achievement.achievement.icon === 'fire'" />
                    <StarIcon class="h-5 w-5 text-blue-600" v-else-if="achievement.achievement.icon === 'star'" />
                    <CheckCircleIcon class="h-5 w-5 text-green-600" v-else-if="achievement.achievement.icon === 'check'" />
                    <FlagIcon class="h-5 w-5 text-purple-600" v-else-if="achievement.achievement.icon === 'flag'" />
                  </div>
                </div>
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-gray-900">{{ achievement.achievement.name }}</p>
                  <p class="text-sm text-gray-500">{{ achievement.achievement.description }}</p>
                </div>
                <div class="flex-shrink-0">
                  <span class="text-sm text-gray-500">+{{ achievement.achievement.points }} pts</span>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Progress Calendar -->
    <ProgressCalendar />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ChartBarIcon, FireIcon, FlagIcon, CheckCircleIcon, StarIcon, TrophyIcon } from '@heroicons/vue/24/outline'
import ProgressCalendar from '../components/ProgressCalendar.vue'
import { useStandardsStore } from '../stores/standards'
import { useGoalsStore } from '../stores/goals'
import { useGamificationStore } from '../stores/gamification'

const standardsStore = useStandardsStore()
const goalsStore = useGoalsStore()
const gamificationStore = useGamificationStore()
const loading = ref(true)

const getDailyStandards = computed(() => standardsStore.getDailyStandards)
const getWeeklyStandards = computed(() => standardsStore.getWeeklyStandards)

onMounted(async () => {
  try {
    await Promise.all([
      standardsStore.fetchStats(),
      standardsStore.fetchStandards(),
      standardsStore.fetchTodayProgress(),
      goalsStore.fetchStats(),
      goalsStore.fetchTodayProgress(),
      gamificationStore.fetchStats()
    ])
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  } finally {
    loading.value = false
  }
})

const toggleStandard = async (progress) => {
  try {
    await standardsStore.toggleStandardCompletion(
      progress.id,
      !progress.is_completed
    )
    await gamificationStore.fetchStats()
  } catch (error) {
    console.error('Error toggling standard:', error)
  }
}

const toggleProcess = async (progress) => {
  try {
    console.log('Toggling process:', progress)
    await goalsStore.toggleProcessCompletion(
      progress.id,
      !progress.is_completed,
      progress.time_spent_minutes
    )
    await gamificationStore.fetchStats()
  } catch (error) {
    console.error('Error toggling process:', error)
  }
}
</script>
