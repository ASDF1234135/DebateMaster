<script setup>
import { computed } from 'vue'
import { jsPDF } from 'jspdf'

const props = defineProps({
  /**
   * Judge summary: { pros, cons, improvement_tips }
   * When null/undefined, section can hide or show placeholder.
   */
  summary: {
    type: Object,
    default: null,
    validator: (v) =>
      v === null ||
      v === undefined ||
      (Array.isArray(v.pros) && Array.isArray(v.cons) && Array.isArray(v.improvement_tips)),
  },
  /** Full list of conversation messages for this session */
  messages: {
    type: Array,
    default: () => [],
  },
})

const hasSummary = computed(
  () =>
    props.summary &&
    (props.summary.pros?.length ||
      props.summary.cons?.length ||
      props.summary.improvement_tips?.length)
)

function severityClass(severity) {
  if (severity === 'high') return 'text-amber-600'
  if (severity === 'mid') return 'text-slate-600'
  return 'text-slate-500'
}

function exportPdf() {
  if (!props.summary && !props.messages.length) return

  const doc = new jsPDF({ unit: 'mm', format: 'a4' })
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const margin = 15
  let y = 20
  const lineHeight = 6
  const maxWidth = pageWidth - margin * 2

  function ensureSpace(lines = 1) {
    if (y + lines * lineHeight > pageHeight - margin) {
      doc.addPage()
      y = margin
    }
  }

  function addTitle(text) {
    ensureSpace(2)
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(18)
    doc.text(text, margin, y)
    y += lineHeight + 2
  }

  function addSubTitle(text) {
    ensureSpace(2)
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(13)
    doc.text(text, margin, y)
    y += lineHeight
  }

  function addTextBlock(text, options = {}) {
    if (!text) return
    const { fontSize = 10, bold = false, extraGap = 2 } = options
    doc.setFont('helvetica', bold ? 'bold' : 'normal')
    doc.setFontSize(fontSize)
    const lines = doc.splitTextToSize(String(text), maxWidth)
    ensureSpace(lines.length)
    doc.text(lines, margin, y)
    y += lines.length * lineHeight + extraGap
  }

  // Title and timestamp
  addTitle('Debate Report')
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(9)
  doc.text(new Date().toLocaleString(), margin, y)
  y += lineHeight + 2

  // Conversation messages
  if (props.messages.length) {
    addSubTitle('Debate messages')
    props.messages.forEach((m) => {
      const speakerLabel = m.speaker === 'agent_pro' ? 'Pro' : m.speaker === 'agent_con' ? 'Con' : m.speaker
      const header = `Trial ${m.trial}, Round ${m.round} - ${speakerLabel}`
      addTextBlock(header, { bold: true, extraGap: 0 })
      addTextBlock(m.content, { bold: false, extraGap: 2 })
    })
  }

  // Summary sections (pros / cons / tips)
  if (props.summary) {
    addSubTitle('Judge summary')

    if (props.summary.pros?.length) {
      addTextBlock('Pros analysis', { bold: true, extraGap: 1 })
      props.summary.pros.forEach((item) => {
        const line = `${item.point}: ${item.description}`
        addTextBlock(`- ${line}`, { extraGap: 1 })
      })
    }

    if (props.summary.cons?.length) {
      addTextBlock('Cons analysis', { bold: true, extraGap: 1 })
      props.summary.cons.forEach((item) => {
        const line = `${item.point}: ${item.description}`
        addTextBlock(`- ${line}`, { extraGap: 1 })
      })
    }

    if (props.summary.improvement_tips?.length) {
      addTextBlock('Improvement tips', { bold: true, extraGap: 1 })
      props.summary.improvement_tips.forEach((tip) => {
        addTextBlock(`- ${tip}`, { extraGap: 1 })
      })
    }
  }

  const filename = `debate-report-${Date.now()}.pdf`
  doc.save(filename)
}
</script>

<template>
  <section v-if="hasSummary" class="space-y-4" data-purpose="summary-analysis">
    <div class="flex items-center gap-2 mb-2">
      <h2 class="text-xl font-bold text-slate-800">Trial summary</h2>
      <span class="px-2 py-0.5 bg-blue-100 text-blue-700 text-[10px] font-bold rounded-full uppercase">Final Report</span>
    </div>
    <div class="glass-card rounded-2xl overflow-hidden border-l-4 border-l-blue-600 shadow-sm">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-slate-800 mb-4">Debate summary</h3>
        <div class="space-y-4">
          <!-- Pros -->
          <div v-if="summary.pros?.length" class="p-4 bg-emerald-50/50 rounded-xl border border-emerald-100">
            <h4 class="text-sm font-bold text-slate-700 mb-2 flex items-center gap-2">
              <svg class="h-4 w-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
              </svg>
              Pros analysis
            </h4>
            <ul class="text-sm text-slate-600 space-y-2 list-disc list-inside">
              <li v-for="(item, i) in summary.pros" :key="i">
                <span :class="['font-medium', severityClass(item.severity)]">{{ item.point }}:</span>
                {{ item.description }}
              </li>
            </ul>
          </div>
          <!-- Cons -->
          <div v-if="summary.cons?.length" class="p-4 bg-slate-50 rounded-xl border border-slate-100">
            <h4 class="text-sm font-bold text-slate-700 mb-2 flex items-center gap-2">
              <svg class="h-4 w-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
              </svg>
              Cons analysis
            </h4>
            <ul class="text-sm text-slate-600 space-y-2 list-disc list-inside">
              <li v-for="(item, i) in summary.cons" :key="i">
                <span :class="['font-medium', severityClass(item.severity)]">{{ item.point }}:</span>
                {{ item.description }}
              </li>
            </ul>
          </div>
          <!-- Improvement tips -->
          <div v-if="summary.improvement_tips?.length" class="p-4 bg-slate-50 rounded-xl border border-slate-100">
            <h4 class="text-sm font-bold text-slate-700 mb-2 flex items-center gap-2">
              <svg class="h-4 w-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
              </svg>
              Improvement tips
            </h4>
            <ul class="text-sm text-slate-600 space-y-1 list-disc list-inside">
              <li v-for="(tip, i) in summary.improvement_tips" :key="i">{{ tip }}</li>
            </ul>
          </div>
        </div>
        <div class="mt-6 flex justify-end">
          <button
            type="button"
            class="bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium py-2 px-4 rounded-lg text-sm transition-colors border border-slate-200"
            @click="exportPdf"
          >
            Export report (PDF)
          </button>
        </div>
      </div>
    </div>
  </section>
</template>
