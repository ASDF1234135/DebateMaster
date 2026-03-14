/**
 * Composable: Debate session state and flow
 * Owns: sessionId, status, error, messages, summary.
 * Provides: startDebateRun(payload), reset.
 * Uses api/debate (mock now; replace with real API later).
 */

import { ref, readonly } from 'vue'
import { startDebate as apiStartDebate, streamDebate as apiStreamDebate } from '../api/debate.js'
import { useDebateHistory } from './useDebateHistory.js'

const sessionId = ref(null)
const status = ref('idle') // 'idle' | 'starting' | 'streaming' | 'done' | 'error'
const error = ref(null)
const messages = ref([])
const summary = ref(null)
// Tracks user-selected limits for current session (for header / display)
const maxRoundsConfig = ref(3)
const maxTrialsConfig = ref(1)

export function useDebateSession() {
  let cancelStream = null

  async function startDebateRun(payload) {
    error.value = null
    summary.value = null
    messages.value = []
    sessionId.value = null
    status.value = 'starting'

    try {
      const res = await apiStartDebate({
        prompt: payload.prompt,
        opponent_persona: payload.opponent_persona || undefined,
        my_persona: payload.my_persona || undefined,
        max_rounds: Number(payload.max_rounds) || 3,
        trial: Number(payload.trial) || 1,
        file: payload.file,
      })

      sessionId.value = res.session_id
      status.value = 'streaming'

      const maxRounds = Number(payload.max_rounds) || 3
      const trialCount = Number(payload.trial) || 1
      maxRoundsConfig.value = maxRounds
      maxTrialsConfig.value = trialCount

      const { addEntry } = useDebateHistory()
      addEntry({
        sessionId: res.session_id,
        prompt: payload.prompt,
        maxRounds,
        trial: trialCount,
      })

      cancelStream = apiStreamDebate(res.session_id, {
        maxRounds,
        trialCount,
        onMessage(data) {
          if (data.type === 'conversation') {
            messages.value = [...messages.value, data]
          } else if (data.type === 'summary') {
            summary.value = {
              pros: data.pros || [],
              cons: data.cons || [],
              improvement_tips: data.improvement_tips || [],
            }
          }
        },
        onComplete() {
          status.value = 'done'
          cancelStream = null
        },
      })
    } catch (e) {
      status.value = 'error'
      error.value = e?.message || 'Failed to start debate'
    }
  }

  function reset() {
    if (cancelStream) cancelStream()
    cancelStream = null
    sessionId.value = null
    status.value = 'idle'
    error.value = null
    messages.value = []
    summary.value = null
    maxRoundsConfig.value = 3
    maxTrialsConfig.value = 1
  }

  return {
    sessionId: readonly(sessionId),
    status: readonly(status),
    error: readonly(error),
    messages: readonly(messages),
    summary: readonly(summary),
    maxRoundsConfig: readonly(maxRoundsConfig),
    maxTrialsConfig: readonly(maxTrialsConfig),
    startDebateRun,
    reset,
  }
}
