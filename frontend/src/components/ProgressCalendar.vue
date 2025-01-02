<template>
  <div>
    <!-- Day Details Modal -->
    <div v-if="selectedDay" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">
              {{ selectedDay.date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}
            </h3>
            <button @click="selectedDay = null" class="text-gray-400 hover:text-gray-500">
              <span class="sr-only">Close</span>
              <XMarkIcon class="h-6 w-6" />
            </button>
          </div>
        </div>
        <div class="px-6 py-4">
          <div class="space-y-4">
            <!-- Standards -->
            <div>
              <h4 class="font-medium text-gray-900">Standards</h4>
              <div class="mt-2">
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">Completed</span>
                  <span class="text-gray-900">{{ selectedDay.progress?.standards_completed || 0 }} / {{ selectedDay.progress?.standards_total || 0 }}</span>
                </div>
                <div class="mt-1 bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-green-500 rounded-full h-2"
                    :style="{
                      width: selectedDay.progress?.standards_total
                        ? `${(selectedDay.progress.standards_completed / selectedDay.progress.standards_total) * 100}%`
                        : '0%'
                    }"
                  ></div>
                </div>
              </div>
            </div>
            
            <!-- Processes -->
            <div>
              <h4 class="font-medium text-gray-900">Processes</h4>
              <div class="mt-2">
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">Completed</span>
                  <span class="text-gray-900">{{ selectedDay.progress?.processes_completed || 0 }} / {{ selectedDay.progress?.processes_total || 0 }}</span>
                </div>
                <div class="mt-1 bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-blue-500 rounded-full h-2"
                    :style="{
                      width: selectedDay.progress?.processes_total
                        ? `${(selectedDay.progress.processes_completed / selectedDay.progress.processes_total) * 100}%`
                        : '0%'
                    }"
                  ></div>
                </div>
              </div>
            </div>

            <!-- Overall Completion -->
            <div>
              <h4 class="font-medium text-gray-900">Overall Completion</h4>
              <div class="mt-2">
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">Total Completed</span>
                  <span class="text-gray-900">
                    {{ (selectedDay.progress?.standards_completed || 0) + (selectedDay.progress?.processes_completed || 0) }} /
                    {{ (selectedDay.progress?.standards_total || 0) + (selectedDay.progress?.processes_total || 0) }}
                  </span>
                </div>
                <div class="mt-1 bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-primary-500 rounded-full h-2"
                    :style="{
                      width: getOverallCompletionRate(selectedDay.progress)
                    }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header flex justify-between items-center">
        <h2 class="text-lg font-medium text-gray-900">Progress History</h2>
        <div class="flex space-x-2">
          <button
            @click="viewMode = 'week'"
            :class="[
              'px-3 py-1 rounded-md text-sm',
              viewMode === 'week'
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-500 hover:bg-gray-100'
            ]"
          >
            Week
          </button>
          <button
            @click="viewMode = 'month'"
            :class="[
              'px-3 py-1 rounded-md text-sm',
              viewMode === 'month'
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-500 hover:bg-gray-100'
            ]"
          >
            Month
          </button>
        </div>
      </div>
      <div class="card-body">
        <div v-if="loading" class="flex justify-center py-4">
          <svg class="animate-spin h-5 w-5 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        <div v-else>
          <!-- Calendar Header -->
          <div class="grid grid-cols-7 gap-px bg-gray-200 text-center text-xs leading-6 text-gray-700 mb-px">
            <div v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="day" class="bg-white py-2">
              {{ day }}
            </div>
          </div>

          <!-- Calendar Grid -->
          <div class="grid grid-cols-7 gap-px bg-gray-200">
            <div
              v-for="(day, index) in calendarDays"
              :key="index"
              class="bg-white min-h-[100px] p-2"
              :class="{
                'opacity-50': !isCurrentMonth(day.date)
              }"
            >
              <button
                @click="showDayDetails(day)"
                class="w-full h-full flex flex-col"
                :class="{ 'hover:bg-gray-50': day.progress }"
              >
                <div class="flex justify-between items-start">
                  <span class="text-sm" :class="{ 'text-primary-600 font-semibold': isToday(day.date) }">
                    {{ day.date.getDate() }}
                  </span>
                  <div v-if="day.progress" class="flex space-x-1">
                    <div
                      v-if="day.progress.standards_completed > 0"
                      class="h-2 w-2 rounded-full bg-green-500"
                      :title="`${day.progress.standards_completed} standards completed`"
                    />
                    <div
                      v-if="day.progress.processes_completed > 0"
                      class="h-2 w-2 rounded-full bg-blue-500"
                      :title="`${day.progress.processes_completed} processes completed`"
                    />
                  </div>
                </div>
                <div v-if="day.progress" class="mt-1">
                  <div v-if="day.progress.standards_completed > 0" class="text-xs text-gray-500">
                    {{ day.progress.standards_completed }} standards
                  </div>
                  <div v-if="day.progress.processes_completed > 0" class="text-xs text-gray-500">
                    {{ day.progress.processes_completed }} processes
                  </div>
                </div>
              </button>
            </div>
          </div>

          <!-- Legend -->
          <div class="mt-4 flex items-center justify-end space-x-4 text-sm">
            <div class="flex items-center">
              <div class="h-2 w-2 rounded-full bg-green-500 mr-2"></div>
              <span class="text-gray-600">Standards</span>
            </div>
            <div class="flex items-center">
              <div class="h-2 w-2 rounded-full bg-blue-500 mr-2"></div>
              <span class="text-gray-600">Processes</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { useStandardsStore } from '../stores/standards'
import { useGoalsStore } from '../stores/goals'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const standardsStore = useStandardsStore()
const goalsStore = useGoalsStore()
const authStore = useAuthStore()
const loading = ref(true)
const viewMode = ref('week')
const progressData = ref({})
const selectedDay = ref(null)

// Get start and end dates for the calendar
const getDateRange = () => {
  const today = new Date()
  let start, end
  
  if (viewMode.value === 'week') {
    // Start from current week's Sunday
    start = new Date(today)
    start.setDate(today.getDate() - today.getDay())
    end = new Date(today)
    end.setDate(start.getDate() + 13) // Show 2 weeks
  } else {
    // Show current month
    start = new Date(today.getFullYear(), today.getMonth(), 1)
    end = new Date(today.getFullYear(), today.getMonth() + 1, 0)
  }
  
  return { start, end }
}

// Generate calendar days
const calendarDays = computed(() => {
  const { start, end } = getDateRange()
  const days = []
  const current = new Date(start)
  
  while (current <= end) {
    days.push({
      date: new Date(current),
      progress: progressData.value[current.toISOString().split('T')[0]]
    })
    current.setDate(current.getDate() + 1)
  }
  
  return days
})

// Helper functions
const isToday = (date) => {
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

const isCurrentMonth = (date) => {
  const today = new Date()
  return date.getMonth() === today.getMonth()
}

const getOverallCompletionRate = (progress) => {
  if (!progress) return '0%'
  
  const totalItems = progress.standards_total + progress.processes_total
  if (totalItems === 0) return '0%'
  
  const completedItems = progress.standards_completed + progress.processes_completed
  return `${(completedItems / totalItems) * 100}%`
}

const showDayDetails = (day) => {
  if (day.progress) {
    selectedDay.value = day
  }
}

// Fetch progress data
const fetchProgressData = async () => {
  loading.value = true
  try {
    const { start, end } = getDateRange()
    const response = await axios.get(
      `/goals/progress/history/?start=${start.toISOString().split('T')[0]}&end=${end.toISOString().split('T')[0]}`,
      {
        headers: authStore.getAuthHeader()
      }
    )
    progressData.value = response.data
  } catch (error) {
    console.error('Error fetching progress data:', error)
    progressData.value = {}
  } finally {
    loading.value = false
  }
}

// Watch for view mode changes
watch(viewMode, () => {
  fetchProgressData()
})

onMounted(() => {
  fetchProgressData()
})
</script>
