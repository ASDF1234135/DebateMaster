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
  maxRoundsConfig,
  maxTrialsConfig,
  startDebateRun,
  reset,
} = useDebateSession()

const selectedTrial = ref(1)

const isFormDisabled = computed(() => status.value === 'starting' || status.value === 'streaming')
const isStreaming = computed(() => status.value === 'streaming')

// Total rounds/trials from user config
const maxRounds = computed(() => maxRoundsConfig.value || 3)
const maxTrials = computed(() => maxTrialsConfig.value || 1)

// Trial options for dropdown: prefer observed trials, otherwise 1..maxTrials
const trialOptions = computed(() => {
  const observed = [...new Set(messages.value.map((m) => m.trial).filter(Boolean))].sort((a, b) => a - b)
  if (observed.length) return observed
  const n = maxTrials.value
  return Array.from({ length: n }, (_, i) => i + 1)
})

const filteredMessages = computed(() =>
  messages.value.filter((m) => m.trial === selectedTrial.value)
)

// Live progress from latest streamed message (0 before any messages)
const currentRound = computed(() => {
  if (messages.value.length === 0) return 0
  const last = messages.value[messages.value.length - 1]
  return last.round ?? 0
})

const currentTrial = computed(() => {
  if (messages.value.length === 0) return 0
  const last = messages.value[messages.value.length - 1]
  return last.trial ?? 0
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
            :max-trials="maxTrials"
            :current-round="currentRound"
            :current-trial="currentTrial"
            @update:selected-trial="selectedTrial = $event"
          />
          <ResultSummary :summary="summary" :messages="messages" />
        </div>
      </div>
    </main>
    <MainFooter />
  </div>
</template>
