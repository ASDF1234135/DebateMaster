<script setup>
import { ref, computed, watch } from 'vue'
import SimulationForm from '../components/SimulationForm.vue'
import ChatDisplay from '../components/ChatDisplay.vue'
import ResultSummary from '../components/ResultSummary.vue'
import MainFooter from '../components/MainFooter.vue'
import { useDebateSession } from '../composables/useDebateSession.js'

const {
  status,
  error,
  messages,
  summary,
  startDebateRun,
  reset,
} = useDebateSession()

const selectedTrial = ref(1)

const isFormDisabled = computed(() => status.value === 'starting' || status.value === 'streaming')
const isStreaming = computed(() => status.value === 'streaming')

const trialOptions = computed(() => {
  const trials = [...new Set(messages.value.map((m) => m.trial).filter(Boolean))].sort((a, b) => a - b)
  return trials.length ? trials : [1]
})

const filteredMessages = computed(() =>
  messages.value.filter((m) => m.trial === selectedTrial.value)
)

const maxRounds = computed(() => {
  if (filteredMessages.value.length === 0) return 3
  const max = Math.max(...filteredMessages.value.map((m) => m.round || 0), 1)
  return max
})

watch(trialOptions, (options) => {
  if (options.length && !options.includes(selectedTrial.value)) {
    selectedTrial.value = options[0]
  }
})

function onFormSubmit(payload) {
  selectedTrial.value = 1
  startDebateRun(payload)
}
</script>

<template>
  <div class="bg-slate-50 text-slate-900 flex flex-col flex-1">
    <main class="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8 flex-1 w-full">
      <!-- Error banner -->
      <div
        v-if="error"
        class="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm flex items-center justify-between gap-4"
      >
        <span>{{ error }}</span>
        <button
          type="button"
          class="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
          @click="reset"
        >
          Dismiss
        </button>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div class="lg:col-span-4">
          <SimulationForm :disabled="isFormDisabled" @submit="onFormSubmit" />
        </div>
        <div class="lg:col-span-8 space-y-8">
          <ChatDisplay
            :messages="filteredMessages"
            :trial-options="trialOptions"
            :selected-trial="selectedTrial"
            :is-streaming="isStreaming"
            :max-rounds="maxRounds"
            @update:selected-trial="selectedTrial = $event"
          />
          <ResultSummary :summary="summary" />
        </div>
      </div>
    </main>
    <MainFooter />
  </div>
</template>
