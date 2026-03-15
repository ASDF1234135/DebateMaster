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
  <div class="min-h-screen text-slate-900 flex flex-col">
    <main class="max-w-3xl mx-auto px-4 py-8 sm:px-6 lg:px-8 flex-1 w-full">
      <!-- 歷史區放在半透明底板上 -->
      <div class="rounded-2xl bg-white/85 backdrop-blur-xl shadow-xl border border-white/20 p-6 sm:p-8">
        <div class="flex items-center justify-between mb-8">
          <h1 class="text-2xl font-bold text-slate-800">History</h1>
          <button
            v-if="history.length"
            type="button"
            class="text-sm text-slate-500 hover:text-red-600 transition-colors"
            @click="clearHistory"
          >
            Clear history
          </button>
        </div>
        <div v-if="!history.length" class="rounded-xl border border-slate-200 bg-white/60 p-12 text-center">
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
            v-for="(item, index) in history"
            :key="item.sessionId + index"
            class="rounded-xl border border-slate-200 bg-white/70 p-4 hover:border-slate-300 hover:bg-white/90 transition-colors"
          >
            <p class="text-slate-800">{{ promptPreview(item.prompt) }}</p>
            <p class="text-sm text-slate-400 mt-2">
              {{ formatDate(item.startedAt) }} · {{ item.maxRounds }} rounds, {{ item.trial }} trial(s)
            </p>
          </li>
        </ul>
      </div>
    </main>
  </div>
</template>
