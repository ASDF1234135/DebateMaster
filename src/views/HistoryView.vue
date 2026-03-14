<script setup>
import { useDebateHistory } from '../composables/useDebateHistory.js'
import { useRouter } from 'vue-router'

const { history, clearHistory } = useDebateHistory()
const router = useRouter()

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function promptPreview(text, maxLen = 120) {
  if (!text) return 'No prompt'
  return text.length <= maxLen ? text : text.slice(0, maxLen) + '...'
}

function goToStart() {
  router.push('/start')
}
</script>

<template>
  <div class="bg-slate-50 text-slate-900 min-h-screen flex flex-col">
    <main class="max-w-3xl mx-auto px-4 py-8 sm:px-6 lg:px-8 flex-1 w-full">
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
      <div v-if="!history.length" class="rounded-2xl border border-slate-200 bg-white p-12 text-center">
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
          class="rounded-xl border border-slate-200 bg-white p-4 hover:border-slate-300 transition-colors"
        >
          <p class="text-slate-800">{{ promptPreview(item.prompt) }}</p>
          <p class="text-sm text-slate-400 mt-2">
            {{ formatDate(item.startedAt) }} · {{ item.maxRounds }} rounds, {{ item.trial }} trial(s)
          </p>
        </li>
      </ul>
    </main>
  </div>
</template>
