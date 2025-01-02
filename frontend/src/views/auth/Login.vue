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
      <button type="submit" class="w-full btn-primary">
        Sign in
      </button>
    </div>

    <div class="text-sm text-center">
      <router-link
        to="/register"
        class="font-medium text-primary-600 hover:text-primary-500"
      >
        Don't have an account? Register
      </router-link>
    </div>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: ''
})

const handleSubmit = async () => {
  const success = await authStore.login(form.value)
  if (success) {
    // Redirect to the originally requested URL or dashboard
    const redirectPath = route.query.redirect || '/app'
    router.push(redirectPath)
  }
}
</script>
