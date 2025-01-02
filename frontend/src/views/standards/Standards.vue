<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="sm:flex sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Standards</h1>
        <p class="mt-2 text-sm text-gray-700">
          Manage your daily, weekly, and monthly standards across different categories
        </p>
      </div>
      <div class="mt-4 sm:mt-0 space-x-4">
        <button
          @click="openCreateCategoryModal"
          class="btn-secondary inline-flex items-center"
        >
          <PlusIcon class="h-5 w-5 mr-2" />
          New Category
        </button>
        <button
          @click="openCreateStandardModal"
          class="btn-primary inline-flex items-center"
        >
          <PlusIcon class="h-5 w-5 mr-2" />
          New Standard
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <svg class="animate-spin h-8 w-8 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- Error State -->
    <div v-else-if="standardsStore.error" class="rounded-md bg-red-50 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <XCircleIcon class="h-5 w-5 text-red-400" aria-hidden="true" />
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">
            {{ standardsStore.error }}
          </h3>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!standardsStore.standards.length" class="text-center py-12">
      <h3 class="mt-2 text-sm font-medium text-gray-900">No standards yet</h3>
      <p class="mt-1 text-sm text-gray-500">Get started by creating a new standard.</p>
      <div class="mt-6">
        <button
          @click="openCreateStandardModal"
          class="btn-primary inline-flex items-center"
        >
          <PlusIcon class="h-5 w-5 mr-2" />
          New Standard
        </button>
      </div>
    </div>

    <!-- Content -->
    <div v-else class="space-y-8">
      <!-- Categories -->
      <div v-for="(standards, category) in standardsStore.standardsByCategory" 
           :key="category" 
           class="space-y-4"
      >
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-medium text-gray-900">{{ category }}</h2>
          <button
            @click="openCreateStandardModal(category)"
            class="btn-secondary text-sm"
          >
            Add Standard
          </button>
        </div>

        <!-- Standards List -->
        <div class="overflow-hidden bg-white shadow sm:rounded-md">
          <ul class="divide-y divide-gray-200">
            <li v-for="standard in standards" :key="standard.id">
              <div class="px-4 py-4 sm:px-6 hover:bg-gray-50">
                <div class="flex items-center justify-between">
                  <div class="flex items-center">
                    <div class="flex-shrink-0">
                      <button
                        @click="toggleStandard(standard)"
                        :class="[
                          getTodayProgress(standard.id)?.is_completed ? 'text-green-600' : 'text-gray-400',
                          'hover:text-green-700 focus:outline-none'
                        ]"
                      >
                        <CheckCircleIcon class="h-6 w-6" :class="{ 'fill-current': getTodayProgress(standard.id)?.is_completed }" />
                      </button>
                    </div>
                    <div class="ml-4">
                      <h3 class="text-sm font-medium text-gray-900">
                        {{ standard.title }}
                      </h3>
                      <div class="mt-1 flex items-center">
                        <span class="text-sm text-gray-500">
                          {{ standard.frequency }}
                          <span v-if="standard.time_of_day">
                            at {{ formatTime(standard.time_of_day) }}
                          </span>
                        </span>
                      </div>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <button
                      @click="editStandard(standard)"
                      class="text-gray-400 hover:text-gray-500"
                    >
                      <PencilIcon class="h-5 w-5" />
                    </button>
                    <button
                      @click="deleteStandard(standard)"
                      class="text-gray-400 hover:text-red-500"
                    >
                      <TrashIcon class="h-5 w-5" />
                    </button>
                  </div>
                </div>
                <div class="mt-2">
                  <div class="text-sm text-gray-500">
                    {{ standard.description }}
                  </div>
                  <div class="mt-2 text-sm text-gray-500">
                    <strong>Minimum requirement:</strong> {{ standard.minimum_requirement }}
                  </div>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Create Category Modal -->
    <TransitionRoot appear :show="isCategoryModalOpen" as="template">
      <Dialog as="div" @close="closeCategoryModal" class="relative z-10">
        <TransitionChild
          enter="ease-out duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black bg-opacity-25" />
        </TransitionChild>

        <div class="fixed inset-0 overflow-y-auto">
          <div class="flex min-h-full items-center justify-center p-4 text-center">
            <TransitionChild
              enter="ease-out duration-300"
              enter-from="opacity-0 scale-95"
              enter-to="opacity-100 scale-100"
              leave="ease-in duration-200"
              leave-from="opacity-100 scale-100"
              leave-to="opacity-0 scale-95"
            >
              <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                  Create New Category
                </DialogTitle>

                <form @submit.prevent="saveCategory" class="mt-4 space-y-4">
                  <div>
                    <label for="name" class="label">Name</label>
                    <input
                      id="name"
                      v-model="categoryForm.name"
                      type="text"
                      required
                      class="input"
                    />
                  </div>

                  <div>
                    <label for="description" class="label">Description</label>
                    <textarea
                      id="description"
                      v-model="categoryForm.description"
                      rows="3"
                      class="input"
                    ></textarea>
                  </div>

                  <div class="mt-6 flex justify-end space-x-3">
                    <button
                      type="button"
                      @click="closeCategoryModal"
                      class="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      class="btn-primary"
                      :disabled="standardsStore.loading"
                    >
                      Create Category
                    </button>
                  </div>
                </form>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Create/Edit Standard Modal -->
    <TransitionRoot appear :show="isStandardModalOpen" as="template">
      <Dialog as="div" @close="closeStandardModal" class="relative z-10">
        <TransitionChild
          enter="ease-out duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black bg-opacity-25" />
        </TransitionChild>

        <div class="fixed inset-0 overflow-y-auto">
          <div class="flex min-h-full items-center justify-center p-4 text-center">
            <TransitionChild
              enter="ease-out duration-300"
              enter-from="opacity-0 scale-95"
              enter-to="opacity-100 scale-100"
              leave="ease-in duration-200"
              leave-from="opacity-100 scale-100"
              leave-to="opacity-0 scale-95"
            >
              <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                  {{ editingStandard ? 'Edit Standard' : 'Create New Standard' }}
                </DialogTitle>

                <form @submit.prevent="saveStandard" class="mt-4 space-y-4">
                  <!-- Standard Form Fields -->
                  <div>
                    <label for="title" class="label">Title</label>
                    <input
                      id="title"
                      v-model="standardForm.title"
                      type="text"
                      required
                      class="input"
                    />
                  </div>

                  <div>
                    <label for="category" class="label">Category</label>
                    <select
                      id="category"
                      v-model="standardForm.category_id"
                      required
                      class="input"
                    >
                      <option value="">Select a category</option>
                      <option v-for="cat in standardsStore.categories" 
                              :key="cat.id" 
                              :value="cat.id"
                      >
                        {{ cat.name }}
                      </option>
                    </select>
                    <div v-if="!standardsStore.categories.length" class="mt-2">
                      <p class="text-sm text-red-600">
                        No categories available.
                      </p>
                      <button
                        type="button"
                        @click="openCreateCategoryModal"
                        class="mt-2 text-sm text-primary-600 hover:text-primary-500"
                      >
                        + Create Category
                      </button>
                    </div>
                  </div>

                  <div>
                    <label for="description" class="label">Description</label>
                    <textarea
                      id="description"
                      v-model="standardForm.description"
                      rows="3"
                      class="input"
                    ></textarea>
                  </div>

                  <div>
                    <label for="minimum_requirement" class="label">Minimum Requirement</label>
                    <textarea
                      id="minimum_requirement"
                      v-model="standardForm.minimum_requirement"
                      rows="2"
                      required
                      class="input"
                    ></textarea>
                  </div>

                  <div>
                    <label for="frequency" class="label">Frequency</label>
                    <select
                      id="frequency"
                      v-model="standardForm.frequency"
                      required
                      class="input"
                    >
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                      <option value="custom">Custom</option>
                    </select>
                  </div>

                  <div v-if="standardForm.frequency === 'custom'">
                    <label class="label">Days of Week</label>
                    <div class="space-y-2">
                      <label v-for="day in daysOfWeek" :key="day.value" class="flex items-center">
                        <input
                          type="checkbox"
                          :value="day.value"
                          v-model="standardForm.specific_days"
                          class="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                        />
                        <span class="ml-2 text-sm text-gray-700">{{ day.label }}</span>
                      </label>
                    </div>
                  </div>

                  <div>
                    <label for="time_of_day" class="label">Time of Day (optional)</label>
                    <input
                      id="time_of_day"
                      v-model="standardForm.time_of_day"
                      type="time"
                      class="input"
                    />
                  </div>

                  <div>
                    <label for="duration" class="label">Duration (minutes, optional)</label>
                    <input
                      id="duration"
                      v-model="standardForm.duration_minutes"
                      type="number"
                      min="0"
                      class="input"
                    />
                  </div>

                  <div class="mt-6 flex justify-end space-x-3">
                    <button
                      type="button"
                      @click="closeStandardModal"
                      class="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      class="btn-primary"
                      :disabled="standardsStore.loading"
                    >
                      {{ editingStandard ? 'Save Changes' : 'Create Standard' }}
                    </button>
                  </div>
                </form>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'
import {
  PlusIcon,
  CheckCircleIcon,
  PencilIcon,
  TrashIcon,
  XCircleIcon,
} from '@heroicons/vue/24/outline'
import { useStandardsStore } from '../../stores/standards'

const standardsStore = useStandardsStore()
const loading = ref(false)
const isStandardModalOpen = ref(false)
const isCategoryModalOpen = ref(false)
const editingStandard = ref(null)

const standardForm = ref({
  title: '',
  category_id: '',
  description: '',
  minimum_requirement: '',
  frequency: 'daily',
  specific_days: [],
  time_of_day: '',
  duration_minutes: null
})

const categoryForm = ref({
  name: '',
  description: ''
})

const daysOfWeek = [
  { value: 0, label: 'Sunday' },
  { value: 1, label: 'Monday' },
  { value: 2, label: 'Tuesday' },
  { value: 3, label: 'Wednesday' },
  { value: 4, label: 'Thursday' },
  { value: 5, label: 'Friday' },
  { value: 6, label: 'Saturday' }
]

  onMounted(async () => {
    loading.value = true
    try {
      // Fetch categories first to ensure they're available
      await standardsStore.fetchCategories()
      console.log('Categories after fetch:', standardsStore.categories)
      
      // Then fetch standards and progress
      await Promise.all([
        standardsStore.fetchStandards(),
        standardsStore.fetchTodayProgress()
      ])
    } catch (error) {
      console.error('Error loading standards:', error)
      standardsStore.error = error.response?.data?.detail || error.message || 'Failed to load data'
    } finally {
      loading.value = false
    }
  })

const openCreateCategoryModal = () => {
  categoryForm.value = {
    name: '',
    description: ''
  }
  isCategoryModalOpen.value = true
}

const openCreateStandardModal = async (categoryName = null) => {
  try {
    loading.value = true
    editingStandard.value = null
    // Refresh categories to ensure we have the latest data
    await standardsStore.fetchCategories()
    const categories = Array.isArray(standardsStore.categories) ? standardsStore.categories : []
    const category = categoryName ? categories.find(c => c.name === categoryName) : null
    standardForm.value = {
      title: '',
      category_id: category?.id || '',
      description: '',
      minimum_requirement: '',
      frequency: 'daily',
      specific_days: [],
      time_of_day: '',
      duration_minutes: null
    }
    isStandardModalOpen.value = true
  } catch (error) {
    console.error('Error opening standard modal:', error)
    standardsStore.error = 'Failed to load categories'
  } finally {
    loading.value = false
  }
}

const editStandard = async (standard) => {
  try {
    loading.value = true
    // Refresh categories to ensure we have the latest data
    await standardsStore.fetchCategories()
    editingStandard.value = standard
    standardForm.value = {
      ...standard,
      category_id: standard.category?.id || '',
      specific_days: standard.specific_days || []
    }
    isStandardModalOpen.value = true
  } catch (error) {
    console.error('Error opening standard modal:', error)
    standardsStore.error = 'Failed to load categories'
  } finally {
    loading.value = false
  }
}

const closeStandardModal = () => {
  isStandardModalOpen.value = false
  editingStandard.value = null
}

const closeCategoryModal = () => {
  isCategoryModalOpen.value = false
}

const saveCategory = async () => {
  try {
    loading.value = true
    await standardsStore.createCategory(categoryForm.value)
    await standardsStore.fetchCategories() // Refresh categories after saving
    closeCategoryModal()
  } catch (error) {
    console.error('Error saving category:', error)
    standardsStore.error = error.response?.data?.detail || 'Failed to create category'
  } finally {
    loading.value = false
  }
}

const saveStandard = async () => {
  try {
    loading.value = true
    if (editingStandard.value) {
      await standardsStore.updateStandard(editingStandard.value.id, standardForm.value)
    } else {
      await standardsStore.createStandard(standardForm.value)
    }
    await standardsStore.fetchStandards() // Refresh standards after saving
    closeStandardModal()
  } catch (error) {
    console.error('Error saving standard:', error)
    standardsStore.error = error.response?.data?.detail || 'Failed to save standard'
  } finally {
    loading.value = false
  }
}

const deleteStandard = async (standard) => {
  if (!confirm('Are you sure you want to delete this standard?')) return
  
  try {
    await standardsStore.deleteStandard(standard.id)
    await standardsStore.fetchStandards() // Refresh standards after deleting
  } catch (error) {
    console.error('Error deleting standard:', error)
  }
}

const getTodayProgress = (standardId) => {
  return standardsStore.getTodayProgressByStandard(standardId)
}

const toggleStandard = async (standard) => {
  const progress = getTodayProgress(standard.id)
  if (!progress) return

  try {
    await standardsStore.toggleStandardCompletion(
      progress.id,
      !progress.is_completed
    )
  } catch (error) {
    console.error('Error toggling standard:', error)
  }
}

const formatTime = (time) => {
  return new Date(`2000-01-01T${time}`).toLocaleTimeString([], {
    hour: 'numeric',
    minute: '2-digit'
  })
}
</script>
