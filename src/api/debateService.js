/**
 * Debate Master - Real FastAPI integration
 * POST /api/v1/debate/start (multipart/form-data)
 * GET /api/v1/debate/stream/{session_id} (SSE)
 */

const API_BASE = typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL != null
  ? import.meta.env.VITE_API_BASE_URL
  : ''

/**
 * Start a debate session (real API).
 * Uses FormData; do NOT send JSON body.
 * @param {{
 *   prompt: string
 *   opponent_persona?: string
 *   max_rounds: number
 *   trial: number
 *   file?: File
 * }} formState - Backend does not accept my_persona yet; see comment below for future.
 * @returns {Promise<{ status: string, session_id: string, message: string }>}
 */
export async function startDebate(formState) {
  const formData = new FormData()
  formData.append('prompt', formState.prompt ?? '')
  formData.append('opponent_persona', formState.opponent_persona ?? '')
  formData.append('max_rounds', String(Number(formState.max_rounds) || 3))
  formData.append('trial', String(Number(formState.trial) || 1))
  if (formState.file != null) {
    formData.append('file', formState.file)
  }
  // When backend supports my_persona: formData.append('my_persona', formState.my_persona ?? '')

  const url = `${API_BASE}/api/v1/debate/start`
  const res = await fetch(url, {
    method: 'POST',
    body: formData,
    // Do not set Content-Type; browser sets multipart/form-data with boundary
  })

  if (!res.ok) {
    let message = `Start failed: ${res.status} ${res.statusText}`
    try {
      const body = await res.json()
      if (body.detail) message = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
    } catch (_) {
      const text = await res.text()
      if (text) message = text
    }
    throw new Error(message)
  }

  const data = await res.json()
  if (data.status !== 'success' || !data.session_id) {
    throw new Error(data.message || 'Invalid start response')
  }
  return data
}

/**
 * Stream debate events via SSE (real API).
 * Backend sends event type "message" with JSON data. Data types: init, conversation, summary, error.
 * @param {string} sessionId
 * @param {{
 *   onMessage?: (data: object) => void
 *   onComplete?: () => void
 *   onError?: (message: string) => void
 * }} callbacks
 * @returns {() => void} Cleanup function: call to close EventSource and stop stream
 */
export function streamDebate(sessionId, { onMessage, onComplete, onError }) {
  if (!sessionId) {
    onComplete?.()
    return () => {}
  }

  const url = `${API_BASE}/api/v1/debate/stream/${encodeURIComponent(sessionId)}`
  const es = new EventSource(url)
  let receivedSummary = false

  function close() {
    es.close()
    onComplete?.()
  }

  es.addEventListener('message', (event) => {
    let data
    try {
      data = JSON.parse(event.data)
    } catch (_) {
      onError?.('Invalid stream data')
      close()
      return
    }

    const type = data?.type

    if (type === 'error') {
      onError?.(data.message || 'Stream error')
      close()
      return
    }

    if (type === 'init') {
      onMessage?.(data)
      return
    }

    if (type === 'conversation') {
      onMessage?.(data)
      return
    }

    if (type === 'summary') {
      receivedSummary = true
      onMessage?.(data)
      return
    }

    onMessage?.(data)
  })

  es.onerror = () => {
    es.close()
    // EventSource also fires error when server closes connection after stream; only report if we never got summary
    if (!receivedSummary) onError?.('Stream connection failed')
    onComplete?.()
  }

  return () => {
    es.close()
    onComplete?.()
  }
}
