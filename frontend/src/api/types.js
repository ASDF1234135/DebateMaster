/**
 * Debate Master - API types
 * Matches FastAPI contract exactly. Used by mock and (later) real API client.
 */

/** @typedef {'agent_pro' | 'agent_con'} ConversationSpeaker */
/** @typedef {'high' | 'mid' | 'low'} Severity */

/**
 * Start debate request (POST /api/v1/debate/start)
 * @typedef {{
 *   prompt: string
 *   opponent_persona?: string
 *   my_persona?: string
 *   max_rounds: number
 *   trial: number
 *   file?: File
 * }} StartDebateInput
 */

/**
 * Start debate response
 * @typedef {{ status: string, session_id: string, message: string }} StartDebateResponse
 */

/**
 * Stream event: conversation message
 * @typedef {{
 *   event: 'message'
 *   data: {
 *     type: 'conversation'
 *     speaker: ConversationSpeaker
 *     round: number
 *     trial: number
 *     content: string
 *   }
 * }} ConversationEvent
 */

/**
 * Stream event: judge summary
 * @typedef {{
 *   event: 'message'
 *   data: {
 *     type: 'summary'
 *     speaker: 'agent_judge'
 *     pros: Array<{ point: string, severity: Severity, description: string }>
 *     cons: Array<{ point: string, severity: Severity, description: string }>
 *     improvement_tips: string[]
 *   }
 * }} SummaryEvent
 */

/** @typedef {ConversationEvent | SummaryEvent} StreamEvent */

/**
 * Normalized conversation item for UI
 * @typedef {{ type: 'conversation', speaker: ConversationSpeaker, round: number, trial: number, content: string }} ConversationMessage
 */

/**
 * Normalized summary for UI
 * @typedef {{
 *   pros: Array<{ point: string, severity: Severity, description: string }>
 *   cons: Array<{ point: string, severity: Severity, description: string }>
 *   improvement_tips: string[]
 * }} DebateSummary
 */

export default {}
