/**
 * Debate Master - API client (Real API Implementation)
 */

const API_BASE_URL = 'http://127.0.0.1:8000' 

/**
 * @param {{
 * prompt: string
 * opponent_persona?: string
 * my_persona?: string
 * max_rounds: number
 * trial: number
 * file?: File
 * }} payload
 * @returns {Promise<{ status: string, session_id: string, message: string }>}
 */
export async function startDebate(payload) {
  if (!payload.prompt?.trim()) {
    throw new Error('Prompt is required')
  }

  const formData = new FormData()
  formData.append('prompt', payload.prompt)
  formData.append('opponent_persona', payload.opponent_persona || 'Strict opponents')
  formData.append('max_rounds', payload.max_rounds)
  formData.append('trial', payload.trial)
  
  if (payload.file) {
    formData.append('file', payload.file)
  }

  if (payload.my_persona) {
    formData.append('my_persona', payload.my_persona)
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/debate/start`, {
      method: 'POST',
      body: formData, 
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Start failed:', error)
    throw error
  }
}

/**
 * @param {string} sessionId
 * @param {{
 * onMessage: (data: object) => void
 * onComplete?: () => void
 * }} callbacks
 */
export function streamDebate(sessionId, { onMessage, onComplete }) {
  if (!sessionId) {
    onComplete?.()
    return () => {} 
  }

  const eventSource = new EventSource(`${API_BASE_URL}/api/v1/debate/stream/${sessionId}`)

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      
      onMessage(data)

      if (data.type === 'summary') {
        eventSource.close() 
        onComplete?.()
      }
    } catch (err) {
      console.error('SSE fail:', err)
    }
  }

  eventSource.onerror = (err) => {
    console.error('SSE connectiono error:', err)
    eventSource.close() 
    onComplete?.()
  }

  return () => {
    console.log('SSE connection terminated')
    eventSource.close()
  }
}