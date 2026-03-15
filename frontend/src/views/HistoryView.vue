<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDebates, getDebateMessages } from '../api/debate.js'
import ChatDisplay from '../components/ChatDisplay.vue'
import ResultSummary from '../components/ResultSummary.vue'

const router = useRouter()
const debates = ref([])
const loading = ref(false)
const loadError = ref(null)
const selectedSession = ref(null)
const sessionData = ref(null)
const selectedTrial = ref(1)

const loadingDetail = ref(false)
const detailError = ref(null)

function promptPreview(text, maxLen = 120) {
  if (!text) return 'No prompt'
  return text.length <= maxLen ? text : text.slice(0, maxLen) + '...'
}

function goToStart() {
  router.push('/start')
}

async function fetchDebates() {
  loading.value = true
  loadError.value = null
  try {
    const res = await getDebates()
    if (res.status === 'success' && Array.isArray(res.data)) {
      debates.value = res.data
    } else {
      debates.value = []
    }
  } catch (e) {
    loadError.value = e?.message || 'Failed to load history'
    debates.value = []
  } finally {
    loading.value = false
  }
}

async function openSection(session) {
  selectedSession.value = session
  sessionData.value = null
  selectedTrial.value = 1
  detailError.value = null
  loadingDetail.value = true
  try {
    const res = await getDebateMessages(session.session_id)
    if (res.status === 'success' && Array.isArray(res.data)) {
      const raw = res.data
      const messages = raw.filter((r) => r.type === 'conversation')
      const summaryRecord = raw.find((r) => r.type === 'summary' || (r.pros !== undefined && r.cons !== undefined))
      const summary = summaryRecord
        ? {
            pros: summaryRecord.pros || [],
            cons: summaryRecord.cons || [],
            improvement_tips: summaryRecord.improvement_tips || [],
          }
        : null
      sessionData.value = { messages, summary }
    } else {
      sessionData.value = { messages: [], summary: null }
    }
  } catch (e) {
    detailError.value = e?.message || 'Failed to load section content'
    sessionData.value = null
  } finally {
    loadingDetail.value = false
  }
}

function backToList() {
  selectedSession.value = null
  sessionData.value = null
  selectedTrial.value = 1
  detailError.value = null
}

const maxRounds = computed(() => {
  const s = selectedSession.value
  if (!s) return 3
  return s.max_round ?? 3
})

const maxTrials = computed(() => {
  const s = selectedSession.value
  if (!s) return 1
  return s.max_trial ?? 1
})

const trialOptions = computed(() => {
  if (!sessionData.value?.messages?.length) {
    const n = maxTrials.value
    return Array.from({ length: n }, (_, i) => i + 1)
  }
  const trials = [...new Set(sessionData.value.messages.map((m) => m.trial).filter(Boolean))].sort((a, b) => a - b)
  return trials.length ? trials : Array.from({ length: maxTrials.value }, (_, i) => i + 1)
})

const filteredMessages = computed(() => {
  if (!sessionData.value?.messages) return []
  return sessionData.value.messages.filter((m) => m.trial === selectedTrial.value)
})

const currentRound = computed(() => {
  if (filteredMessages.value.length === 0) return 0
  const last = filteredMessages.value[filteredMessages.value.length - 1]
  return last.round ?? 0
})

const currentTrial = computed(() => selectedTrial.value)

onMounted(() => {
  fetchDebates()
})
</script>

<template>
  <div class="bg-slate-50 text-slate-900 min-h-screen flex flex-col">
    <main class="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8 flex-1 w-full">
      <!-- List view: all sections -->
      <template v-if="selectedSession == null">
        <div class="flex items-center justify-between mb-8">
          <h1 class="text-2xl font-bold text-slate-800">History</h1>
          <button
            type="button"
            class="text-sm text-slate-500 hover:text-blue-600 transition-colors"
            @click="goToStart"
          >
            Start new debate
          </button>
        </div>

        <div v-if="loading" class="rounded-2xl border border-slate-200 bg-white p-12 text-center">
          <p class="text-slate-500">Loading...</p>
        </div>
        <div v-else-if="loadError" class="rounded-2xl border border-red-200 bg-red-50 p-6 text-center">
          <p class="text-red-700">{{ loadError }}</p>
          <button
            type="button"
            class="mt-3 text-sm text-red-600 hover:underline"
            @click="fetchDebates"
          >
            Retry
          </button>
        </div>
        <div v-else-if="!debates.length" class="rounded-2xl border border-slate-200 bg-white p-12 text-center">
          <p class="text-slate-500 mb-4">No past debates yet.</p>
          <button
            type="button"
            class="text-blue-600 font-medium hover:underline"
            @click="goToStart"
          >
            Start your first debate
          </button>
        </div>
        <ul v-else class="space-y-4">
          <li
            v-for="(item, index) in debates"
            :key="item.session_id + index"
            class="rounded-xl border border-slate-200 bg-white p-4 hover:border-blue-300 hover:bg-slate-50/50 transition-colors cursor-pointer"
            @click="openSection(item)"
          >
            <p class="text-slate-800 font-medium">{{ promptPreview(item.prompt) }}</p>
            <p class="text-sm text-slate-400 mt-2">
              {{ item.max_round ?? 3 }} rounds, {{ item.max_trial ?? 1 }} trial(s)
            </p>
          </li>
        </ul>
      </template>

      <!-- Detail view: selected section + trial selector + content -->
      <template v-else>
        <div class="mb-6 flex items-center gap-4">
          <button
            type="button"
            class="text-sm text-slate-600 hover:text-blue-600 transition-colors"
            @click="backToList"
          >
            Back to list
          </button>
          <h1 class="text-xl font-bold text-slate-800 truncate flex-1">
            {{ promptPreview(selectedSession.prompt, 80) }}
          </h1>
        </div>

        <div v-if="loadingDetail" class="rounded-2xl border border-slate-200 bg-white p-12 text-center">
          <p class="text-slate-500">Loading section...</p>
        </div>
        <div v-else-if="detailError" class="rounded-2xl border border-red-200 bg-red-50 p-6 text-center">
          <p class="text-red-700">{{ detailError }}</p>
          <button
            type="button"
            class="mt-3 text-sm text-red-600 hover:underline"
            @click="openSection(selectedSession)"
          >
            Retry
          </button>
        </div>
        <div v-else class="space-y-8">
          <ChatDisplay
            :messages="filteredMessages"
            :trial-options="trialOptions"
            :selected-trial="selectedTrial"
            :is-streaming="false"
            :max-rounds="maxRounds"
            :max-trials="maxTrials"
            :current-round="currentRound"
            :current-trial="currentTrial"
            @update:selected-trial="selectedTrial = $event"
          />
          <ResultSummary
            v-if="sessionData?.summary"
            :summary="sessionData.summary"
            :messages="sessionData.messages"
          />
        </div>
      </template>
    </main>
  </div>
</template>
