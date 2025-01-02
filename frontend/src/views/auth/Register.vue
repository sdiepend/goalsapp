<template>
  <form class="space-y-6" @submit.prevent="handleSubmit">
    <div>
      <label for="username" class="label">Username</label>
      <div class="mt-1">
        <input
          id="username"
          v-model="form.username"
          name="username"
          type="text"
          required
          class="input"
        />
      </div>
    </div>

    <div>
      <label for="email" class="label">Email address</label>
      <div class="mt-1">
        <input
          id="email"
          v-model="form.email"
          name="email"
          type="email"
          required
          class="input"
        />
      </div>
    </div>

    <div>
      <label for="password" class="label">Password</label>
      <div class="mt-1">
        <input
          id="password"
          v-model="form.password"
          name="password"
          type="password"
          required
          class="input"
        />
      </div>
    </div>

    <div>
      <label for="password2" class="label">Confirm Password</label>
      <div class="mt-1">
        <input
          id="password2"
          v-model="form.password2"
          name="password2"
          type="password"
          required
          class="input"
        />
      </div>
      <p v-if="passwordMismatch" class="mt-1 text-sm text-red-600">
        Passwords do not match
      </p>
    </div>

    <div>
      <label for="timezone" class="label">Timezone</label>
      <div class="mt-1">
        <select
          id="timezone"
          v-model="form.timezone"
          name="timezone"
          required
          class="input"
        >
          <option v-for="tz in timezones" :key="tz" :value="tz">
            {{ tz }}
          </option>
        </select>
      </div>
    </div>

    <div>
      <button 
        type="submit" 
        class="w-full btn-primary"
        :disabled="!isFormValid || authStore.loading"
      >
        Register
      </button>
    </div>

    <div class="text-sm text-center">
      <router-link
        to="/login"
        class="font-medium text-primary-600 hover:text-primary-500"
      >
        Already have an account? Sign in
      </router-link>
    </div>
  </form>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  password2: '',
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
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

const passwordMismatch = computed(() => {
  return form.value.password && 
         form.value.password2 && 
         form.value.password !== form.value.password2
})

const isFormValid = computed(() => {
  return form.value.username &&
         form.value.email &&
         form.value.password &&
         form.value.password2 &&
         form.value.timezone &&
         !passwordMismatch.value
})

const handleSubmit = async () => {
  if (!isFormValid.value) return

  const success = await authStore.register(form.value)
  if (success) {
    router.push('/app')
  }
}
</script>
