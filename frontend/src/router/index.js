import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Layouts
import AuthLayout from '../layouts/AuthLayout.vue'
import DashboardLayout from '../layouts/DashboardLayout.vue'

// Auth Views
import Login from '../views/auth/Login.vue'
import Register from '../views/auth/Register.vue'

// Main Views
import Dashboard from '../views/Dashboard.vue'
import Standards from '../views/standards/Standards.vue'
import Goals from '../views/goals/Goals.vue'
import Reflections from '../views/reflections/Reflections.vue'
import Profile from '../views/Profile.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'login',
        component: Login,
        meta: { requiresGuest: true }
      },
      {
        path: 'register',
        name: 'register',
        component: Register,
        meta: { requiresGuest: true }
      }
    ]
  },
  {
    path: '/app',
    component: DashboardLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: Dashboard
      },
      {
        path: 'standards',
        name: 'standards',
        component: Standards
      },
      {
        path: 'goals',
        name: 'goals',
        component: Goals
      },
      {
        path: 'reflections',
        name: 'reflections',
        component: Reflections
      },
      {
        path: 'profile',
        name: 'profile',
        component: Profile
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated

  // Handle routes that require authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({ name: 'login', query: { redirect: to.fullPath } })
    } else {
      next()
    }
  }

  // Handle routes that require guest access (login, register)
  else if (to.matched.some(record => record.meta.requiresGuest)) {
    if (isAuthenticated) {
      next({ name: 'dashboard' })
    } else {
      next()
    }
  }

  // Default allow access
  else {
    next()
  }
})

export default router
