/**
 * Debate Master - API client
 * Currently MOCK implementation. Replace with real fetch/SSE when backend is ready.
 * Contract matches: POST /api/v1/debate/start, GET /api/v1/debate/stream/{session_id}
 */

import { buildMockConversation, MOCK_SUMMARY_EVENT } from '../mocks/debateMockData.js'

const MOCK_START_DELAY_MS = 600
const MOCK_MESSAGE_DELAY_MS = 800
const MOCK_SUMMARY_DELAY_MS = 400

/**
 * Simulate POST /api/v1/debate/start
 * @param {{
 *   prompt: string
 *   opponent_persona?: string
 *   my_persona?: string
 *   max_rounds: number
 *   trial: number
 *   file?: File
 * }} payload
 * @returns {Promise<{ status: string, session_id: string, message: string }>}
 */
export async function startDebate(payload) {
  // MOCK: delay then return fixed response. Replace with:
  // const formData = new FormData(); formData.set('prompt', payload.prompt); ...
  // const res = await fetch('/api/v1/debate/start', { method: 'POST', body: formData });
  await new Promise((r) => setTimeout(r, MOCK_START_DELAY_MS))

  if (!payload.prompt?.trim()) {
    throw new Error('Prompt is required')
  }

  return {
    status: 'success',
    session_id: `mock-session-${Date.now()}`,
    message: 'Debate session started.',
  }
}

/**
 * Simulate GET /api/v1/debate/stream/{session_id}
 * Sends conversation events one by one with delay (respecting maxRounds and trialCount), then summary, then onComplete.
 * @param {string} sessionId
 * @param {{
 *   maxRounds?: number
 *   trialCount?: number
 *   onMessage: (data: object) => void
 *   onComplete?: () => void
 * }} callbacks
 */
export function streamDebate(sessionId, { maxRounds = 3, trialCount = 1, onMessage, onComplete }) {
  // MOCK: simulate streaming. Replace with EventSource/fetch when backend is ready.
  if (!sessionId) {
    onComplete?.()
    return
  }

  const conversation = buildMockConversation(maxRounds, trialCount)
  let cancelled = false

  async function run() {
    for (const event of conversation) {
      if (cancelled) return
      onMessage(event.data)
      await new Promise((r) => setTimeout(r, MOCK_MESSAGE_DELAY_MS))
    }
    if (cancelled) return
    await new Promise((r) => setTimeout(r, MOCK_SUMMARY_DELAY_MS))
    onMessage(MOCK_SUMMARY_EVENT.data)
    onComplete?.()
  }

  run()

  return () => {
    cancelled = true
  }
}
