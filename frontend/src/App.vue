<template>
  <div class="min-h-full">
    <router-view></router-view>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

onMounted(async () => {
  // If we have a token, try to fetch the user data
  if (authStore.isAuthenticated) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      // If fetching user fails, redirect to login
      authStore.logout()
      router.push('/login')
    }
  } else {
    // If not authenticated, redirect to login
    router.push('/login')
  }
})
</script>

<style>
@import './assets/main.css';
</style>
