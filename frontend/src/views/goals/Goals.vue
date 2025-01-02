<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="sm:flex sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Goals</h1>
        <p class="mt-2 text-sm text-gray-700">
          Manage your BIG goals, Medium Term Goals (MTGs), and Daily Processes (DPs)
        </p>
      </div>
      <div class="mt-4 sm:mt-0">
        <button
          @click="openCreateGoalModal('BIG')"
          class="btn-primary inline-flex items-center"
        >
          <PlusIcon class="h-5 w-5 mr-2" />
          New BIG Goal
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
    <div v-else-if="goalsStore.error" class="rounded-md bg-red-50 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <XCircleIcon class="h-5 w-5 text-red-400" aria-hidden="true" />
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">
            {{ goalsStore.error }}
          </h3>
        </div>
      </div>
    </div>

    <!-- Goals Content -->
    <div v-else class="space-y-8">
      <!-- BIG Goals -->
      <div v-for="bigGoal in goalsStore.bigGoals" :key="bigGoal.id" class="card">
        <!-- BIG Goal Header -->
        <div class="card-header flex items-center justify-between">
          <div>
            <h2 class="text-lg font-medium text-gray-900">{{ bigGoal.title }}</h2>
            <p class="mt-1 text-sm text-gray-500">{{ bigGoal.description }}</p>
          </div>
          <div class="flex items-center space-x-2">
            <button
              @click="openCreateGoalModal('MTG', bigGoal)"
              class="btn-secondary text-sm"
            >
              Add MTG
            </button>
            <button
              @click="editGoal(bigGoal)"
              class="text-gray-400 hover:text-gray-500"
            >
              <PencilIcon class="h-5 w-5" />
            </button>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="px-4 py-2 bg-gray-50 border-t border-b border-gray-200">
          <div class="flex items-center">
            <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                class="h-full bg-primary-600 rounded-full"
                :style="{ width: `${bigGoal.completion_percentage || 0}%` }"
              ></div>
            </div>
            <span class="ml-2 text-sm text-gray-600">
              {{ Math.round(bigGoal.completion_percentage || 0) }}%
            </span>
          </div>
        </div>

        <!-- MTGs -->
        <div class="card-body">
          <div class="space-y-6">
            <div v-for="mtg in getMTGsForBIG(bigGoal.id)" :key="mtg.id" class="bg-white shadow sm:rounded-lg">
              <!-- MTG Header -->
              <div class="px-4 py-5 sm:px-6 flex items-center justify-between">
                <div>
                  <h3 class="text-base font-medium text-gray-900">{{ mtg.title }}</h3>
                  <p class="mt-1 text-sm text-gray-500">{{ mtg.description }}</p>
                </div>
                <div class="flex items-center space-x-2">
                  <button
                    @click="openCreateGoalModal('DP', mtg)"
                    class="btn-secondary text-sm"
                  >
                    Add DP
                  </button>
                  <button
                    @click="editGoal(mtg)"
                    class="text-gray-400 hover:text-gray-500"
                  >
                    <PencilIcon class="h-5 w-5" />
                  </button>
                </div>
              </div>

              <!-- DPs -->
              <div class="border-t border-gray-200">
                <ul class="divide-y divide-gray-200">
                  <li v-for="dp in getDPsForMTG(mtg.id)" :key="dp.id" class="px-4 py-4">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center">
                        <button
                          @click="toggleProcess(dp)"
                          :class="[
                            getTodayProgress(dp.id)?.is_completed ? 'text-green-600' : 'text-gray-400',
                            'hover:text-green-700 focus:outline-none'
                          ]"
                        >
                          <CheckCircleIcon class="h-6 w-6" :class="{ 'fill-current': getTodayProgress(dp.id)?.is_completed }" />
                        </button>
                        <div class="ml-3">
                          <p class="text-sm font-medium text-gray-900">{{ dp.title }}</p>
                          <p class="text-sm text-gray-500">{{ dp.description }}</p>
                        </div>
                      </div>
                      <div class="flex items-center space-x-2">
                        <button
                          @click="editGoal(dp)"
                          class="text-gray-400 hover:text-gray-500"
                        >
                          <PencilIcon class="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Goal Modal -->
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
              <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                  {{ editingGoal ? 'Edit Goal' : `Create New ${goalForm.goal_type}` }}
                </DialogTitle>

                <form @submit.prevent="saveGoal" class="mt-4 space-y-4">
                  <div>
                    <label for="title" class="label">Title</label>
                    <input
                      id="title"
                      v-model="goalForm.title"
                      type="text"
                      required
                      class="input"
                    />
                  </div>

                  <div>
                    <label for="description" class="label">Description</label>
                    <textarea
                      id="description"
                      v-model="goalForm.description"
                      rows="3"
                      class="input"
                    ></textarea>
                  </div>

                  <div>
                    <label for="category" class="label">Category</label>
                    <input
                      id="category"
                      v-model="goalForm.category"
                      type="text"
                      required
                      class="input"
                    />
                  </div>

                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label for="start_date" class="label">Start Date</label>
                      <input
                        id="start_date"
                        v-model="goalForm.start_date"
                        type="date"
                        required
                        class="input"
                      />
                    </div>
                    <div>
                      <label for="target_date" class="label">Target Date</label>
                      <input
                        id="target_date"
                        v-model="goalForm.target_date"
                        type="date"
                        required
                        class="input"
                      />
                    </div>
                  </div>

                  <div>
                    <label class="label">Metrics</label>
                    <div class="space-y-2">
                      <div v-for="(metric, index) in goalForm.metrics" :key="index" class="flex gap-2">
                        <input
                          v-model="metric.measurementType"
                          placeholder="Measurement type"
                          class="input flex-1"
                        />
                        <input
                          v-model.number="metric.targetValue"
                          type="number"
                          placeholder="Target"
                          class="input w-24"
                        />
                        <button
                          type="button"
                          @click="removeMetric(index)"
                          class="text-red-500 hover:text-red-700"
                        >
                          <XMarkIcon class="h-5 w-5" />
                        </button>
                      </div>
                      <button
                        type="button"
                        @click="addMetric"
                        class="btn-secondary text-sm"
                      >
                        Add Metric
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
                      :disabled="goalsStore.loading"
                    >
                      {{ editingGoal ? 'Save Changes' : 'Create Goal' }}
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
  XCircleIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'
import { useGoalsStore } from '../../stores/goals'

const goalsStore = useGoalsStore()
const loading = ref(false)
const isModalOpen = ref(false)
const editingGoal = ref(null)

const goalForm = ref({
  title: '',
  description: '',
  category: '',
  goal_type: 'BIG',
  parent: null,
  start_date: '',
  target_date: '',
  metrics: []
})

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      goalsStore.fetchAllGoals(),
      goalsStore.fetchTodayProgress()
    ])
  } catch (error) {
    console.error('Error loading goals:', error)
  } finally {
    loading.value = false
  }
})

const getMTGsForBIG = (bigId) => {
  const mtgs = goalsStore.mediumTermGoals || []
  return mtgs.filter(mtg => mtg.parent === bigId)
}

const getDPsForMTG = (mtgId) => {
  const dps = goalsStore.dailyProcesses || []
  return dps.filter(dp => dp.parent === mtgId)
}

const getTodayProgress = (processId) => {
  return goalsStore.getTodayProcessProgress(processId)
}

const openCreateGoalModal = (type, parentGoal = null) => {
  editingGoal.value = null
  goalForm.value = {
    title: '',
    description: '',
    category: parentGoal?.category || '',
    goal_type: type,
    parent: parentGoal?.id || null,
    start_date: new Date().toISOString().split('T')[0],
    target_date: '',
    metrics: []
  }
  isModalOpen.value = true
}

const editGoal = (goal) => {
  editingGoal.value = goal
  goalForm.value = {
    ...goal,
    metrics: goal.metrics || []
  }
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  editingGoal.value = null
}

const addMetric = () => {
  goalForm.value.metrics.push({
    measurementType: '',
    targetValue: null,
    currentValue: 0
  })
}

const removeMetric = (index) => {
  goalForm.value.metrics.splice(index, 1)
}

const saveGoal = async () => {
  try {
    if (editingGoal.value) {
      await goalsStore.updateGoal(editingGoal.value.id, goalForm.value)
    } else {
      await goalsStore.createGoal(goalForm.value)
    }
    closeModal()
  } catch (error) {
    console.error('Error saving goal:', error)
  }
}

const toggleProcess = async (process) => {
  const progress = getTodayProgress(process.id)
  if (!progress) return

  try {
    await goalsStore.toggleProcessCompletion(
      progress.id,
      !progress.is_completed
    )
  } catch (error) {
    console.error('Error toggling process:', error)
  }
}
</script>
