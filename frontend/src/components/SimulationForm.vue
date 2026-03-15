<script setup>
import { ref } from 'vue'

defineProps({
  /** Disable form and submit button when debate is starting or streaming */
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['submit'])

const prompt = ref('')
const opponentPersona = ref('')
const myPersona = ref('')
const maxRounds = ref('3')
const trial = ref('1')
const fileInput = ref(null)
const uploadedFiles = ref([])
const acceptedTypes = '.pdf,.doc,.docx,.txt'
const maxFileSizeMB = 10

function openFilePicker() {
  fileInput.value?.click()
}

function onFileChange(e) {
  const files = Array.from(e.target.files || [])
  const valid = files.filter((file) => file.size <= maxFileSizeMB * 1024 * 1024)
  uploadedFiles.value = [...uploadedFiles.value, ...valid]
  e.target.value = ''
}

function removeFile(index) {
  uploadedFiles.value = uploadedFiles.value.filter((_, i) => i !== index)
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function onSubmit(e) {
  e.preventDefault()
  const file = uploadedFiles.value[0] || undefined
  emit('submit', {
    prompt: prompt.value,
    opponent_persona: opponentPersona.value.trim() || undefined,
    my_persona: myPersona.value.trim() || undefined,
    max_rounds: Number(maxRounds.value) || 3,
    trial: Number(trial.value) || 1,
    file,
  })
}
</script>

<template>
  <aside class="space-y-6" data-purpose="simulation-settings">
    <section class="glass-card rounded-2xl p-6 shadow-sm border border-slate-200">
      <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
        <svg class="h-5 w-5 text-slate-800" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
        </svg>
        Simulation settings
      </h2>
      <form class="space-y-5" @submit="onSubmit">
        <div data-purpose="scenario-input">
          <div class="flex items-center justify-between gap-2 mb-2">
            <label class="text-sm font-medium text-slate-700" for="prompt">Prompt</label>
            <input
              ref="fileInput"
              type="file"
              class="hidden"
              :accept="acceptedTypes"
              multiple
              @change="onFileChange"
            />
            <button
              type="button"
              class="p-1.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
              title="Upload documents"
              @click="openFilePicker"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
          <textarea
            id="prompt"
            v-model="prompt"
            class="w-full rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-blue-500 text-sm placeholder:text-slate-400"
            placeholder="Describe the debate topic or thesis, e.g. a claim to argue for or against..."
            rows="4"
          />
          <div class="mt-4 space-y-3">
            <div>
              <label class="block text-xs font-medium text-slate-500 mb-1" for="opponent_persona">Opponent persona (optional)</label>
              <input
                id="opponent_persona"
                v-model="opponentPersona"
                type="text"
                class="w-full rounded-lg border border-slate-200 focus:border-blue-500 focus:ring-blue-500 text-sm placeholder:text-slate-400"
                placeholder="e.g. Skeptical economist"
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-500 mb-1" for="my_persona">My persona (optional)</label>
              <input
                id="my_persona"
                v-model="myPersona"
                type="text"
                class="w-full rounded-lg border border-slate-200 focus:border-blue-500 focus:ring-blue-500 text-sm placeholder:text-slate-400"
                placeholder="e.g. Tech advocate"
              />
            </div>
          </div>
          <ul v-if="uploadedFiles.length" class="mt-2 space-y-1.5">
            <li
              v-for="(file, index) in uploadedFiles"
              :key="index"
              class="flex items-center justify-between gap-2 py-2 px-3 bg-slate-50 rounded-lg border border-slate-200 text-sm text-slate-700"
            >
              <span class="truncate min-w-0" :title="file.name">{{ file.name }}</span>
              <span class="text-xs text-slate-400 flex-shrink-0">{{ formatSize(file.size) }}</span>
              <button
                type="button"
                class="p-1 text-slate-400 hover:text-red-600 rounded transition-colors flex-shrink-0"
                title="Remove"
                @click="removeFile(index)"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </li>
          </ul>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2" for="rounds">Max rounds</label>
            <select
              id="rounds"
              v-model="maxRounds"
              class="w-full rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-blue-500 text-sm"
            >
              <option v-for="n in 10" :key="n" :value="String(n)">{{ n }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2" for="trials">Trial</label>
            <select
              id="trials"
              v-model="trial"
              class="w-full rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-blue-500 text-sm"
            >
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="5">5</option>
              <option value="10">10</option>
            </select>
          </div>
        </div>
        <button
          type="submit"
          class="btn-madflows btn-madflows--transparent w-full mt-4"
          :disabled="disabled"
        >
          <span class="btn-madflows-content flex items-center justify-center gap-2">
            <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path clip-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" fill-rule="evenodd" />
            </svg>
            Start debate
          </span>
        </button>
      </form>
    </section>
    <div class="p-4 bg-blue-50 rounded-xl border border-blue-100">
      <h3 class="text-xs font-bold text-blue-800 uppercase tracking-wider mb-2">Tip</h3>
      <p class="text-xs text-blue-700 leading-relaxed">
        Click Start simulation when ready. The AI models will debate based on your scenario and help surface potential weaknesses in the argument.
      </p>
    </div>
  </aside>
</template>
