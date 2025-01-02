<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-2xl font-semibold text-gray-900">Profile Settings</h1>
      <p class="mt-2 text-sm text-gray-700">
        Manage your account settings and preferences
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <svg class="animate-spin h-8 w-8 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- Error State -->
    <div v-else-if="authStore.error" class="rounded-md bg-red-50 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <XCircleIcon class="h-5 w-5 text-red-400" aria-hidden="true" />
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">
            {{ authStore.error }}
          </h3>
        </div>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="rounded-md bg-green-50 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <CheckCircleIcon class="h-5 w-5 text-green-400" aria-hidden="true" />
        </div>
        <div class="ml-3">
          <p class="text-sm font-medium text-green-800">
            {{ successMessage }}
          </p>
        </div>
      </div>
    </div>

    <!-- Profile Form -->
    <form @submit.prevent="saveProfile" class="space-y-8">
      <!-- Basic Information -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-medium text-gray-900">Basic Information</h2>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label for="username" class="label">Username</label>
              <input
                id="username"
                v-model="profileForm.username"
                type="text"
                required
                class="input"
              />
            </div>
            <div>
              <label for="email" class="label">Email</label>
              <input
                id="email"
                v-model="profileForm.email"
                type="email"
                required
                class="input"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Preferences -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-medium text-gray-900">Preferences</h2>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label for="timezone" class="label">Timezone</label>
              <select
                id="timezone"
                v-model="profileForm.timezone"
                required
                class="input"
              >
                <option v-for="tz in timezones" :key="tz" :value="tz">
                  {{ tz }}
                </option>
              </select>
            </div>
            <div>
              <label for="preferred_reminder_time" class="label">Preferred Reminder Time</label>
              <input
                id="preferred_reminder_time"
                v-model="profileForm.preferred_reminder_time"
                type="time"
                class="input"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Notification Settings -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-medium text-gray-900">Notification Settings</h2>
        </div>
        <div class="card-body">
          <div class="space-y-4">
            <div class="flex items-start">
              <div class="flex h-5 items-center">
                <input
                  id="email_notifications"
                  v-model="profileForm.notification_preferences.email_enabled"
                  type="checkbox"
                  class="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
              </div>
              <div class="ml-3">
                <label for="email_notifications" class="text-sm font-medium text-gray-700">Email Notifications</label>
                <p class="text-sm text-gray-500">Receive daily and weekly summaries via email</p>
              </div>
            </div>
            <div class="flex items-start">
              <div class="flex h-5 items-center">
                <input
                  id="browser_notifications"
                  v-model="profileForm.notification_preferences.browser_enabled"
                  type="checkbox"
                  class="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
              </div>
              <div class="ml-3">
                <label for="browser_notifications" class="text-sm font-medium text-gray-700">Browser Notifications</label>
                <p class="text-sm text-gray-500">Receive real-time notifications in your browser</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="flex justify-end">
        <button
          type="submit"
          class="btn-primary"
          :disabled="authStore.loading"
        >
          Save Changes
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { XCircleIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const successMessage = ref('')

const profileForm = ref({
  username: '',
  email: '',
  timezone: '',
  preferred_reminder_time: '',
  notification_preferences: {
    email_enabled: false,
    browser_enabled: false
  }
})

// List of common timezones
const timezones = [
  'UTC',
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'America/Phoenix',
  'America/Anchorage',
  'Pacific/Honolulu',
  'Europe/London',
  'Europe/Paris',
  'Europe/Berlin',
  'Asia/Tokyo',
  'Asia/Shanghai',
  'Australia/Sydney',
  'Pacific/Auckland'
]

onMounted(async () => {
  loading.value = true
  try {
    const user = authStore.getUser
    if (user) {
      profileForm.value = {
        username: user.username,
        email: user.email,
        timezone: user.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone,
        preferred_reminder_time: user.preferred_reminder_time || '',
        notification_preferences: user.notification_preferences || {
          email_enabled: false,
          browser_enabled: false
        }
      }
    }
  } catch (error) {
    console.error('Error loading profile:', error)
  } finally {
    loading.value = false
  }
})

const saveProfile = async () => {
  try {
    await authStore.updateProfile(profileForm.value)
    successMessage.value = 'Profile updated successfully'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    console.error('Error saving profile:', error)
  }
}
</script>
