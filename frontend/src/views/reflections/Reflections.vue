<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="sm:flex sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Reflections</h1>
        <p class="mt-2 text-sm text-gray-700">
          Review and reflect on your progress weekly, monthly, quarterly, and yearly
        </p>
      </div>
      <div class="mt-4 sm:mt-0">
        <Menu as="div" class="relative inline-block text-left">
          <div>
            <MenuButton class="btn-primary inline-flex items-center">
              <PlusIcon class="h-5 w-5 mr-2" />
              New Reflection
              <ChevronDownIcon class="h-5 w-5 ml-2" />
            </MenuButton>
          </div>
          <transition
            enter-active-class="transition ease-out duration-100"
            enter-from-class="transform opacity-0 scale-95"
            enter-to-class="transform opacity-100 scale-100"
            leave-active-class="transition ease-in duration-75"
            leave-from-class="transform opacity-100 scale-100"
            leave-to-class="transform opacity-0 scale-95"
          >
            <MenuItems class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
              <div class="py-1">
                <MenuItem v-for="type in reflectionTypes" :key="type.value">
                  <button
                    @click="openCreateReflectionModal(type.value)"
                    class="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
                  >
                    {{ type.label }}
                  </button>
                </MenuItem>
              </div>
            </MenuItems>
          </transition>
        </Menu>
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
    <div v-else-if="reflectionsStore.error" class="rounded-md bg-red-50 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <XCircleIcon class="h-5 w-5 text-red-400" aria-hidden="true" />
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">
            {{ reflectionsStore.error }}
          </h3>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div v-else class="space-y-8">
      <!-- Latest Reflections -->
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div v-for="type in reflectionTypes" :key="type.value" class="card">
          <div class="card-header">
            <h2 class="text-lg font-medium text-gray-900">{{ type.label }}</h2>
          </div>
          <div class="card-body">
            <div v-if="latestReflections[type.value]" class="space-y-4">
              <div>
                <p class="text-sm text-gray-500">Latest reflection:</p>
                <p class="mt-1 text-sm font-medium text-gray-900">
                  {{ formatDateRange(
                    latestReflections[type.value].start_date,
                    latestReflections[type.value].end_date
                  ) }}
                </p>
              </div>
              <button
                @click="viewReflection(latestReflections[type.value])"
                class="btn-secondary w-full"
              >
                View Reflection
              </button>
            </div>
            <div v-else class="text-center py-4">
              <p class="text-sm text-gray-500">No reflections yet</p>
              <button
                @click="openCreateReflectionModal(type.value)"
                class="mt-2 btn-secondary text-sm"
              >
                Create First Reflection
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Past Reflections -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-medium text-gray-900">Past Reflections</h2>
        </div>
        <div class="card-body">
          <div class="space-y-4">
            <div class="flex gap-4">
              <select v-model="selectedType" class="input">
                <option value="">All Types</option>
                <option v-for="type in reflectionTypes" :key="type.value" :value="type.value">
                  {{ type.label }}
                </option>
              </select>
              <input
                type="month"
                v-model="selectedMonth"
                class="input"
              />
            </div>
            <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
              <table class="min-w-full divide-y divide-gray-300">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Period</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Type</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Highlights</th>
                    <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                      <span class="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white">
                  <tr v-for="reflection in filteredReflections" :key="reflection.id">
                    <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                      {{ formatDateRange(reflection.start_date, reflection.end_date) }}
                    </td>
                    <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {{ getReflectionTypeLabel(reflection.reflection_type) }}
                    </td>
                    <td class="px-3 py-4 text-sm text-gray-500">
                      {{ reflection.highlights[0] || 'No highlights' }}
                    </td>
                    <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                      <button
                        @click="viewReflection(reflection)"
                        class="text-primary-600 hover:text-primary-900"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Reflection Modal -->
    <TransitionRoot appear :show="isModalOpen" as="template">
      <Dialog as="div" @close="closeModal" class="relative z-10">
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
              <DialogPanel class="w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                  {{ editingReflection ? 'Edit Reflection' : 'New Reflection' }}
                </DialogTitle>

                <form @submit.prevent="saveReflection" class="mt-4 space-y-4">
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label for="start_date" class="label">Start Date</label>
                      <input
                        id="start_date"
                        v-model="reflectionForm.start_date"
                        type="date"
                        required
                        class="input"
                      />
                    </div>
                    <div>
                      <label for="end_date" class="label">End Date</label>
                      <input
                        id="end_date"
                        v-model="reflectionForm.end_date"
                        type="date"
                        required
                        class="input"
                      />
                    </div>
                  </div>

                  <div>
                    <label for="content" class="label">Reflection</label>
                    <textarea
                      id="content"
                      v-model="reflectionForm.content"
                      rows="6"
                      required
                      class="input"
                      placeholder="Write your reflection here..."
                    ></textarea>
                  </div>

                  <div>
                    <label class="label">Highlights</label>
                    <div class="space-y-2">
                      <div v-for="(highlight, index) in reflectionForm.highlights" :key="index" class="flex gap-2">
                        <input
                          v-model="reflectionForm.highlights[index]"
                          type="text"
                          class="input flex-1"
                          placeholder="Add a highlight..."
                        />
                        <button
                          type="button"
                          @click="removeHighlight(index)"
                          class="text-red-500 hover:text-red-700"
                        >
                          <XMarkIcon class="h-5 w-5" />
                        </button>
                      </div>
                      <button
                        type="button"
                        @click="addHighlight"
                        class="btn-secondary text-sm"
                      >
                        Add Highlight
                      </button>
                    </div>
                  </div>

                  <div>
                    <label class="label">Challenges</label>
                    <div class="space-y-2">
                      <div v-for="(challenge, index) in reflectionForm.challenges" :key="index" class="flex gap-2">
                        <input
                          v-model="reflectionForm.challenges[index]"
                          type="text"
                          class="input flex-1"
                          placeholder="Add a challenge..."
                        />
                        <button
                          type="button"
                          @click="removeChallenge(index)"
                          class="text-red-500 hover:text-red-700"
                        >
                          <XMarkIcon class="h-5 w-5" />
                        </button>
                      </div>
                      <button
                        type="button"
                        @click="addChallenge"
                        class="btn-secondary text-sm"
                      >
                        Add Challenge
                      </button>
                    </div>
                  </div>

                  <div>
                    <label class="label">Action Items</label>
                    <div class="space-y-2">
                      <div v-for="(action, index) in reflectionForm.action_items" :key="index" class="flex gap-2">
                        <input
                          v-model="reflectionForm.action_items[index]"
                          type="text"
                          class="input flex-1"
                          placeholder="Add an action item..."
                        />
                        <button
                          type="button"
                          @click="removeActionItem(index)"
                          class="text-red-500 hover:text-red-700"
                        >
                          <XMarkIcon class="h-5 w-5" />
                        </button>
                      </div>
                      <button
                        type="button"
                        @click="addActionItem"
                        class="btn-secondary text-sm"
                      >
                        Add Action Item
                      </button>
                    </div>
                  </div>

                  <div class="mt-6 flex justify-end space-x-3">
                    <button
                      type="button"
                      @click="closeModal"
                      class="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      class="btn-primary"
                      :disabled="reflectionsStore.loading"
                    >
                      {{ editingReflection ? 'Save Changes' : 'Create Reflection' }}
                    </button>
                  </div>
                </form>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- View Reflection Modal -->
    <TransitionRoot appear :show="isViewModalOpen" as="template">
      <Dialog as="div" @close="closeViewModal" class="relative z-10">
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
              <DialogPanel class="w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                  {{ getReflectionTypeLabel(selectedReflection?.reflection_type) }} Reflection
                </DialogTitle>

                <div class="mt-4 space-y-6">
                  <div>
                    <p class="text-sm text-gray-500">Period</p>
                    <p class="mt-1 text-base text-gray-900">
                      {{ formatDateRange(selectedReflection?.start_date, selectedReflection?.end_date) }}
                    </p>
                  </div>

                  <div>
                    <p class="text-sm text-gray-500">Reflection</p>
                    <p class="mt-1 text-base text-gray-900 whitespace-pre-line">
                      {{ selectedReflection?.content }}
                    </p>
                  </div>

                  <div v-if="selectedReflection?.highlights.length">
                    <p class="text-sm text-gray-500">Highlights</p>
                    <ul class="mt-1 list-disc list-inside space-y-1">
                      <li v-for="highlight in selectedReflection.highlights" :key="highlight" class="text-base text-gray-900">
                        {{ highlight }}
                      </li>
                    </ul>
                  </div>

                  <div v-if="selectedReflection?.challenges.length">
                    <p class="text-sm text-gray-500">Challenges</p>
                    <ul class="mt-1 list-disc list-inside space-y-1">
                      <li v-for="challenge in selectedReflection.challenges" :key="challenge" class="text-base text-gray-900">
                        {{ challenge }}
                      </li>
                    </ul>
                  </div>

                  <div v-if="selectedReflection?.action_items.length">
                    <p class="text-sm text-gray-500">Action Items</p>
                    <ul class="mt-1 list-disc list-inside space-y-1">
                      <li v-for="action in selectedReflection.action_items" :key="action" class="text-base text-gray-900">
                        {{ action }}
                      </li>
                    </ul>
                  </div>

                  <div class="mt-6 flex justify-end space-x-3">
                    <button
                      @click="editReflection(selectedReflection)"
                      class="btn-secondary"
                    >
                      Edit
                    </button>
                    <button
                      @click="closeViewModal"
                      class="btn-primary"
                    >
                      Close
                    </button>
                  </div>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'
import {
  PlusIcon,
  ChevronDownIcon,
  XCircleIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'
import { useReflectionsStore } from '../../stores/reflections'

const reflectionsStore = useReflectionsStore()
const loading = ref(false)
const isModalOpen = ref(false)
const isViewModalOpen = ref(false)
const editingReflection = ref(null)
const selectedReflection = ref(null)
const selectedType = ref('')
const selectedMonth = ref(new Date().toISOString().slice(0, 7))

const reflectionTypes = [
  { value: 'weekly', label: 'Weekly Reflection' },
  { value: 'monthly', label: 'Monthly Reflection' },
  { value: 'quarterly', label: 'Quarterly Reflection' },
  { value: 'yearly', label: 'Yearly Reflection' }
]

const reflectionForm = ref({
  reflection_type: '',
  start_date: '',
  end_date: '',
  content: '',
  highlights: [],
  challenges: [],
  action_items: []
})

onMounted(async () => {
  loading.value = true
  try {
    await reflectionsStore.fetchAllReflections()
  } catch (error) {
    console.error('Error loading reflections:', error)
  } finally {
    loading.value = false
  }
})

const latestReflections = computed(() => reflectionsStore.latestReflections)

const filteredReflections = computed(() => {
  let reflections = Object.values(reflectionsStore.reflections).flat()

  if (selectedType.value) {
    reflections = reflections.filter(r => r.reflection_type === selectedType.value)
  }

  if (selectedMonth.value) {
    const [year, month] = selectedMonth.value.split('-')
    reflections = reflections.filter(r => {
      const date = new Date(r.start_date)
      return date.getFullYear() === parseInt(year) && date.getMonth() === parseInt(month) - 1
    })
  }

  return reflections.sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
})

const openCreateReflectionModal = (type) => {
  editingReflection.value = null
  const period = reflectionsStore.generateReflectionPeriod(type)
  reflectionForm.value = {
    reflection_type: type,
    start_date: period.start_date,
    end_date: period.end_date,
    content: '',
    highlights: [],
    challenges: [],
    action_items: []
  }
  isModalOpen.value = true
}

const editReflection = (reflection) => {
  editingReflection.value = reflection
  reflectionForm.value = { ...reflection }
  closeViewModal()
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  editingReflection.value = null
}

const viewReflection = (reflection) => {
  selectedReflection.value = reflection
  isViewModalOpen.value = true
}

const closeViewModal = () => {
  isViewModalOpen.value = false
  selectedReflection.value = null
}

const addHighlight = () => {
  reflectionForm.value.highlights.push('')
}

const removeHighlight = (index) => {
  reflectionForm.value.highlights.splice(index, 1)
}

const addChallenge = () => {
  reflectionForm.value.challenges.push('')
}

const removeChallenge = (index) => {
  reflectionForm.value.challenges.splice(index, 1)
}

const addActionItem = () => {
  reflectionForm.value.action_items.push('')
}

const removeActionItem = (index) => {
  reflectionForm.value.action_items.splice(index, 1)
}

const saveReflection = async () => {
  try {
    // Filter out empty strings
    reflectionForm.value.highlights = reflectionForm.value.highlights.filter(Boolean)
    reflectionForm.value.challenges = reflectionForm.value.challenges.filter(Boolean)
    reflectionForm.value.action_items = reflectionForm.value.action_items.filter(Boolean)

    if (editingReflection.value) {
      await reflectionsStore.updateReflection(editingReflection.value.id, reflectionForm.value)
    } else {
      await reflectionsStore.createReflection(reflectionForm.value)
    }
    closeModal()
  } catch (error) {
    console.error('Error saving reflection:', error)
  }
}

const getReflectionTypeLabel = (type) => {
  return reflectionTypes.find(t => t.value === type)?.label || type
}

const formatDateRange = (start, end) => {
  if (!start || !end) return ''
  
  const startDate = new Date(start)
  const endDate = new Date(end)
  
  return `${startDate.toLocaleDateString()} - ${endDate.toLocaleDateString()}`
}
</script>
