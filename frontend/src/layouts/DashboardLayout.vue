<template>
  <div class="min-h-full">
    <!-- Navigation -->
    <nav class="bg-white shadow">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex h-16 justify-between">
          <div class="flex">
            <!-- Logo -->
            <div class="flex flex-shrink-0 items-center">
              <h1 class="text-xl font-bold text-primary-600">Goals Tracker</h1>
            </div>
            <!-- Navigation Links -->
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <router-link
                v-for="item in navigation"
                :key="item.name"
                :to="item.to"
                :class="[
                  $route.name === item.name
                    ? 'border-primary-500 text-gray-900'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
                  'inline-flex items-center border-b-2 px-1 pt-1 text-sm font-medium'
                ]"
              >
                {{ item.text }}
              </router-link>
            </div>
          </div>

          <!-- User Menu -->
          <div class="hidden sm:ml-6 sm:flex sm:items-center">
            <Menu as="div" class="relative ml-3">
              <div>
                <MenuButton class="flex rounded-full bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
                  <span class="sr-only">Open user menu</span>
                  <UserCircleIcon class="h-8 w-8 text-gray-400" aria-hidden="true" />
                </MenuButton>
              </div>
              <transition
                enter-active-class="transition ease-out duration-200"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <MenuItems class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                  <MenuItem v-slot="{ active }">
                    <router-link
                      to="/app/profile"
                      :class="[active ? 'bg-gray-100' : '', 'block px-4 py-2 text-sm text-gray-700']"
                    >
                      Your Profile
                    </router-link>
                  </MenuItem>
                  <MenuItem v-slot="{ active }">
                    <a
                      href="#"
                      @click.prevent="handleLogout"
                      :class="[active ? 'bg-gray-100' : '', 'block px-4 py-2 text-sm text-gray-700']"
                    >
                      Sign out
                    </a>
                  </MenuItem>
                </MenuItems>
              </transition>
            </Menu>
          </div>

          <!-- Mobile menu -->
          <Disclosure v-slot="{ open }" class="sm:hidden">
            <div>
              <div class="flex items-center">
                <DisclosureButton class="inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500">
                  <span class="sr-only">Open main menu</span>
                  <Bars3Icon v-if="!open" class="block h-6 w-6" aria-hidden="true" />
                  <XMarkIcon v-else class="block h-6 w-6" aria-hidden="true" />
                </DisclosureButton>
              </div>
              <DisclosurePanel class="absolute left-0 right-0 top-16 bg-white shadow-lg sm:hidden">
                <div class="space-y-1 pb-3 pt-2">
                  <router-link
                    v-for="item in navigation"
                    :key="item.name"
                    :to="item.to"
                    :class="[
                      $route.name === item.name
                        ? 'bg-primary-50 border-primary-500 text-primary-700'
                        : 'border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700',
                      'block border-l-4 py-2 pl-3 pr-4 text-base font-medium'
                    ]"
                  >
                    {{ item.text }}
                  </router-link>
                </div>
                <div class="border-t border-gray-200 pb-3 pt-4">
                  <div class="flex items-center px-4">
                    <div class="flex-shrink-0">
                      <UserCircleIcon class="h-8 w-8 text-gray-400" aria-hidden="true" />
                    </div>
                    <div class="ml-3">
                      <div class="text-base font-medium text-gray-800">{{ authStore.user?.username }}</div>
                      <div class="text-sm font-medium text-gray-500">{{ authStore.user?.email }}</div>
                    </div>
                  </div>
                  <div class="mt-3 space-y-1">
                    <router-link
                      to="/app/profile"
                      class="block px-4 py-2 text-base font-medium text-gray-500 hover:bg-gray-100 hover:text-gray-800"
                    >
                      Your Profile
                    </router-link>
                    <a
                      href="#"
                      @click.prevent="handleLogout"
                      class="block px-4 py-2 text-base font-medium text-gray-500 hover:bg-gray-100 hover:text-gray-800"
                    >
                      Sign out
                    </a>
                  </div>
                </div>
              </DisclosurePanel>
            </div>
          </Disclosure>
        </div>
      </div>
    </nav>

    <!-- Main content -->
    <div class="py-6">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Menu, MenuButton, MenuItem, MenuItems, Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import { Bars3Icon, XMarkIcon, UserCircleIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const navigation = [
  { name: 'dashboard', to: '/app', text: 'Dashboard' },
  { name: 'standards', to: '/app/standards', text: 'Standards' },
  { name: 'goals', to: '/app/goals', text: 'Goals' },
  { name: 'reflections', to: '/app/reflections', text: 'Reflections' },
]

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
