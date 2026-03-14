<script setup>
import { computed } from 'vue'

const props = defineProps({
  /** List of conversation messages (filtered by trial) */
  messages: { type: Array, default: () => [] },
  /** Available trial numbers for dropdown */
  trialOptions: { type: Array, default: () => [1] },
  /** Currently selected trial */
  selectedTrial: { type: Number, default: 1 },
  /** True while stream is active (show thinking indicator) */
  isStreaming: { type: Boolean, default: false },
  /** Max rounds for header display (per trial) */
  maxRounds: { type: Number, default: 3 },
  /** Max trials for header display */
  maxTrials: { type: Number, default: 1 },
  /** Live current round from parent (0 before start) */
  currentRound: { type: Number, default: 0 },
  /** Live current trial from parent (0 before start) */
  currentTrial: { type: Number, default: 0 },
})

const emit = defineEmits(['update:selectedTrial'])

function onTrialChange(e) {
  const val = e.target?.value
  if (val != null) emit('update:selectedTrial', Number(val))
}

const isThinking = computed(() => {
  if (!props.isStreaming || props.messages.length === 0) return false
  const last = props.messages[props.messages.length - 1]
  return last.speaker === 'agent_pro'
})

function speakerLabel(speaker) {
  return speaker === 'agent_pro' ? 'Pro' : 'Con'
}
</script>

<template>
  <section
    class="bg-white rounded-2xl shadow-sm border border-slate-200 flex flex-col overflow-hidden"
    data-purpose="chat-display"
  >
    <div class="p-4 border-b border-slate-100 bg-slate-50/50 flex flex-wrap items-center justify-between gap-3">
      <h2 class="text-sm font-semibold text-slate-700 flex items-center gap-2">
        <span
          class="w-2 h-2 rounded-full"
          :class="isStreaming ? 'bg-green-500 animate-pulse' : 'bg-slate-400'"
        />
        Debate {{ isStreaming ? 'in progress' : 'arena' }} (Round {{ currentRound }}/{{ maxRounds }}, Trial {{ currentTrial }}/{{ maxTrials }})
      </h2>
      <div class="flex items-center gap-2">
        <label class="text-xs font-medium text-slate-500" for="trial-select">Trial</label>
        <select
          id="trial-select"
          :value="selectedTrial"
          class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-700 focus:border-blue-500 focus:ring-blue-500"
          @change="onTrialChange"
        >
          <option v-for="t in trialOptions" :key="t" :value="t">Trial {{ t }}</option>
        </select>
      </div>
    </div>
    <div
      class="chat-container p-6 space-y-6 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-opacity-5"
    >
      <template v-for="(msg, index) in messages" :key="index">
        <div
          v-if="msg.type === 'conversation'"
          class="flex items-start gap-3"
          :class="msg.speaker === 'agent_con' ? 'flex-row-reverse' : ''"
          :data-purpose="msg.speaker === 'agent_pro' ? 'ai-a-bubble' : 'ai-b-bubble'"
        >
          <div
            class="w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center border"
            :class="msg.speaker === 'agent_pro' ? 'bg-blue-100 border-blue-200' : 'bg-purple-100 border-purple-200'"
          >
            <span
              class="text-xs font-bold"
              :class="msg.speaker === 'agent_pro' ? 'text-blue-600' : 'text-purple-600'"
            >
              {{ msg.speaker === 'agent_pro' ? 'A' : 'B' }}
            </span>
          </div>
          <div class="max-w-[80%]" :class="msg.speaker === 'agent_con' ? 'text-right' : ''">
            <div
              class="text-[10px] font-medium text-slate-400 mb-1 uppercase tracking-tight"
              :class="msg.speaker === 'agent_con' ? 'mr-1' : 'ml-1'"
            >
              {{ speakerLabel(msg.speaker) }} (Round {{ msg.round }}, Trial {{ msg.trial }})
            </div>
            <div
              class="p-4 rounded-2xl shadow-sm text-slate-800 text-left"
              :class="
                msg.speaker === 'agent_pro'
                  ? 'bg-blue-50 border border-blue-100 rounded-tl-none'
                  : 'bg-purple-50 border border-purple-100 rounded-tr-none'
             "
            >
              <p class="text-sm leading-relaxed">{{ msg.content }}</p>
            </div>
          </div>
        </div>
      </template>
    </div>
    <div v-if="isThinking" class="p-4 bg-slate-50 border-t border-slate-100">
      <div class="flex items-center gap-2 text-slate-400">
        <div class="flex gap-1">
          <span class="w-1 h-1 bg-slate-400 rounded-full animate-bounce" />
          <span class="w-1 h-1 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]" />
          <span class="w-1 h-1 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]" />
        </div>
        <span class="text-xs italic font-medium">Con is thinking...</span>
      </div>
    </div>
  </section>
</template>
