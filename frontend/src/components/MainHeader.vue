<script setup>
import { RouterLink, useRoute } from 'vue-router'

defineProps({
  transparent: { type: Boolean, default: false },
})

const route = useRoute()

function isActive(name) {
  return route.name === name
}
</script>

<template>
  <header
    class="sticky top-0 z-50 w-full transition-colors duration-200"
    :class="transparent ? 'bg-transparent border-transparent' : 'bg-white/80 backdrop-blur-md border-b border-slate-200'"
    data-purpose="navigation"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-center">
      <div class="flex items-center gap-8">
        <RouterLink
          to="/"
          class="flex items-center gap-2 hover:opacity-90 transition-opacity"
          :class="transparent ? 'text-white' : ''"
        >
          <div
            class="p-1.5 rounded-lg transition-colors"
            :class="transparent ? 'bg-white/20' : 'bg-blue-600'"
          >
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <span class="text-xl font-bold tracking-tight" :class="transparent ? 'text-white' : 'text-slate-800'">Debate Master</span>
        </RouterLink>
        <nav class="hidden md:flex items-center space-x-8 text-sm font-medium" :class="transparent ? 'text-white/90' : 'text-slate-600'">
          <RouterLink
            to="/"
            class="transition-colors"
            :class="transparent ? (isActive('Overview') ? 'text-white' : 'hover:text-white') : (isActive('Overview') ? 'text-blue-600' : 'hover:text-blue-600')"
          >
            Overview
          </RouterLink>
          <RouterLink
            to="/start"
            class="transition-colors"
            :class="transparent ? (isActive('GetStarted') ? 'text-white' : 'hover:text-white') : (isActive('GetStarted') ? 'text-blue-600' : 'hover:text-blue-600')"
          >
            Get started
          </RouterLink>
          <RouterLink
            to="/history"
            class="transition-colors"
            :class="transparent ? (isActive('History') ? 'text-white' : 'hover:text-white') : (isActive('History') ? 'text-blue-600' : 'hover:text-blue-600')"
          >
            History
          </RouterLink>
        </nav>
      </div>
    </div>
  </header>
</template>
