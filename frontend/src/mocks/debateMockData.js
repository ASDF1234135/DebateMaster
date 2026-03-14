/**
 * Mock data for Debate Master - matches API spec exactly.
 * Used by mock API to simulate stream events.
 */

/** Content pool for first 3 rounds, trial 1 (Pro then Con per round) */
const ROUND_1_3_TRIAL_1 = [
  [
    'Regarding the claim that "fully autonomous driving should be legalized immediately," I see significant risks in technical maturity and infrastructure. Current sensors can still misjudge in extreme weather. Should we prioritize clarifying regulatory liability first?',
    "That's a pointed rebuttal. However, statistics show human error accounts for over 90% of traffic incidents. Even if the technology isn't perfect, the safety gains already justify moving toward legalization. On liability, we should build a new product-liability insurance framework rather than reusing the old driver-responsibility model.",
  ],
  [
    'Insurance may address compensation, but not the moral "trolley problem." When the AI must choose between collision targets, algorithmic transparency and social consensus are the real safeguards. Isn\'t full legalization premature without a broad ethical consensus?',
    'We can mandate public disclosure of decision logic and run citizen assemblies to set ethical guidelines before rollout. Phased legalization with clear milestones would address the timing concern while keeping safety gains.',
  ],
  [
    'Agreed that phased approach and transparency help. My main remaining concern is edge cases: sensor failure in weather, adversarial attacks on perception, and liability in mixed human-AI traffic. How would you address those?',
    'Edge cases are real but not unique to autonomy—human drivers also fail in bad weather and face uncertainty. We should set performance benchmarks (e.g., minimum uptime, fail-safe behavior) and require cybersecurity certification, similar to aviation. That strengthens the case for legalization with guardrails.',
  ],
]

/**
 * Build mock conversation events for given max_rounds and trial count.
 * Used so mock stream respects user's Max rounds and Trial settings.
 * @param {number} maxRounds
 * @param {number} trialCount
 * @returns {Array<{ event: string, data: object }>}
 */
export function buildMockConversation(maxRounds, trialCount) {
  const events = []
  for (let t = 1; t <= trialCount; t++) {
    for (let r = 1; r <= maxRounds; r++) {
      const roundIndex = r - 1
      const trial1Content = ROUND_1_3_TRIAL_1[roundIndex]
      const proContent =
        trial1Content && t === 1
          ? trial1Content[0]
          : `[Trial ${t}] Pro argument for round ${r}: addressing the topic with evidence and reasoning.`
      const conContent =
        trial1Content && t === 1
          ? trial1Content[1]
          : `[Trial ${t}] Con argument for round ${r}: countering with alternative perspective and data.`
      events.push(
        {
          event: 'message',
          data: {
            type: 'conversation',
            speaker: 'agent_pro',
            round: r,
            trial: t,
            content: proContent,
          },
        },
        {
          event: 'message',
          data: {
            type: 'conversation',
            speaker: 'agent_con',
            round: r,
            trial: t,
            content: conContent,
          },
        }
      )
    }
  }
  return events
}

/** @deprecated Use buildMockConversation(maxRounds, trialCount) so stream respects user input. */
export const MOCK_CONVERSATION = [
  {
    event: 'message',
    data: {
      type: 'conversation',
      speaker: 'agent_pro',
      round: 1,
      trial: 1,
      content:
        'Regarding the claim that "fully autonomous driving should be legalized immediately," I see significant risks in technical maturity and infrastructure. Current sensors can still misjudge in extreme weather. Should we prioritize clarifying regulatory liability first?',
    },
  },
  {
    event: 'message',
    data: {
      type: 'conversation',
      speaker: 'agent_con',
      round: 1,
      trial: 1,
      content:
        "That's a pointed rebuttal. However, statistics show human error accounts for over 90% of traffic incidents. Even if the technology isn't perfect, the safety gains already justify moving toward legalization. On liability, we should build a new product-liability insurance framework rather than reusing the old driver-responsibility model.",
    },
  },
  {
    event: 'message',
    data: {
      type: 'conversation',
      speaker: 'agent_pro',
      round: 2,
      trial: 1,
      content:
        'Insurance may address compensation, but not the moral "trolley problem." When the AI must choose between collision targets, algorithmic transparency and social consensus are the real safeguards. Isn\'t full legalization premature without a broad ethical consensus?',
    },
  },
  {
    event: 'message',
    data: {
      type: 'conversation',
      speaker: 'agent_con',
      round: 2,
      trial: 1,
      content:
        'We can mandate public disclosure of decision logic and run citizen assemblies to set ethical guidelines before rollout. Phased legalization with clear milestones would address the timing concern while keeping safety gains.',
    },
  },
  {
    event: 'message',
    data: {
      type: 'conversation',
      speaker: 'agent_pro',
      round: 3,
      trial: 1,
      content:
        'Agreed that phased approach and transparency help. My main remaining concern is edge cases: sensor failure in weather, adversarial attacks on perception, and liability in mixed human-AI traffic. How would you address those?',
    },
  },
  {
    event: 'message',
    data: {
      type: 'conversation',
      speaker: 'agent_con',
      round: 3,
      trial: 1,
      content:
        'Edge cases are real but not unique to autonomy—human drivers also fail in bad weather and face uncertainty. We should set performance benchmarks (e.g., minimum uptime, fail-safe behavior) and require cybersecurity certification, similar to aviation. That strengthens the case for legalization with guardrails.',
    },
  },
  // Trial 2 (same structure, different content for dropdown testing)
  {
    event: 'message',
    data: {
      type: 'conversation',
      speaker: 'agent_pro',
      round: 1,
      trial: 2,
      content:
        '[Trial 2] The same topic from a different run. I argue that full legalization without phased rollout risks public backlash and undermines trust in the technology.',
    },
  },
  {
    event: 'message',
    data: {
      type: 'conversation',
      speaker: 'agent_con',
      round: 1,
      trial: 2,
      content:
        '[Trial 2] A counter-run perspective: delaying legalization has its own costs in lives lost to human error. We should move faster with strong oversight.',
    },
  },
  {
    event: 'message',
    data: {
      type: 'conversation',
      speaker: 'agent_pro',
      round: 2,
      trial: 2,
      content: '[Trial 2] Round 2 Pro: Oversight requires capacity that regulators do not yet have. We need time to build it.',
    },
  },
  {
    event: 'message',
    data: {
      type: 'conversation',
      speaker: 'agent_con',
      round: 2,
      trial: 2,
      content: '[Trial 2] Round 2 Con: Industry can co-fund regulatory capacity. The framework can grow with rollout.',
    },
  },
  {
    event: 'message',
    data: {
      type: 'conversation',
      speaker: 'agent_pro',
      round: 3,
      trial: 2,
      content: '[Trial 2] Round 3 Pro: Agreed that co-funding helps. My remaining concern is international alignment so we avoid regulatory arbitrage.',
    },
  },
  {
    event: 'message',
    data: {
      type: 'conversation',
      speaker: 'agent_con',
      round: 3,
      trial: 2,
      content: '[Trial 2] Round 3 Con: International bodies are already working on this. We can align domestic law with emerging standards.',
    },
  },
]

/** Mock summary event (single event with type summary) */
export const MOCK_SUMMARY_EVENT = {
  event: 'message',
  data: {
    type: 'summary',
    speaker: 'agent_judge',
    pros: [
      {
        point: 'Strong use of statistics',
        severity: 'high',
        description: 'Pro side effectively cited human error rates to support safety gains from automation.',
      },
      {
        point: 'Concrete policy proposals',
        severity: 'mid',
        description: 'Phased legalization and transparency mandates were specific and actionable.',
      },
    ],
    cons: [
      {
        point: 'Ethical accountability',
        severity: 'high',
        description: 'The argument lacked depth on moral responsibility for AI decisions in edge cases.',
      },
      {
        point: 'Edge case handling',
        severity: 'mid',
        description: 'Defense logic for atypical weather and cybersecurity threats could be stronger.',
      },
    ],
    improvement_tips: [
      'Strengthen the case for phased legalization with clear milestones.',
      'Introduce "blockchain black box" or similar for data transparency and liability.',
      'Address trolley-problem style objections with concrete governance proposals.',
    ],
  },
}
