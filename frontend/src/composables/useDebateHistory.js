/**
 * Debate history - stored in localStorage for frontend-only.
 * Replace with API when backend is ready.
 */

import { ref } from 'vue'

const STORAGE_KEY = 'debate-master-history'
const MAX_ENTRIES = 50

const history = ref([])

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) history.value = JSON.parse(raw)
    else history.value = []
  } catch {
    history.value = []
  }
}

load()

function save() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history.value))
  } catch (_) {}
}

export function useDebateHistory() {

  function addEntry(entry) {
    const item = {
      sessionId: entry.sessionId,
      prompt: entry.prompt || '',
      maxRounds: entry.maxRounds ?? 3,
      trial: entry.trial ?? 1,
      startedAt: entry.startedAt || new Date().toISOString(),
    }
    history.value = [item, ...history.value].slice(0, MAX_ENTRIES)
    save()
  }

  function clearHistory() {
    history.value = []
    save()
  }

  return {
    history,
    addEntry,
    clearHistory,
    load,
  }
}
