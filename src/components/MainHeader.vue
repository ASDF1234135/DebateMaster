<script setup>
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()

function isActive(name) {
  return route.name === name
}
</script>

<template>
  <header
    class="sticky top-0 z-50 w-full bg-white/80 backdrop-blur-md border-b border-slate-200"
    data-purpose="navigation"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <RouterLink to="/" class="flex items-center gap-2 hover:opacity-90 transition-opacity">
        <div class="bg-blue-600 p-1.5 rounded-lg">
          <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
          </svg>
        </div>
        <h1 class="text-xl font-bold tracking-tight text-slate-800">Debate Master</h1>
      </RouterLink>
      <nav class="hidden md:flex items-center space-x-8 text-sm font-medium text-slate-600">
        <RouterLink
          to="/"
          class="transition-colors"
          :class="isActive('Overview') ? 'text-blue-600' : 'hover:text-blue-600'"
        >
          Overview
        </RouterLink>
        <RouterLink
          to="/start"
          class="transition-colors"
          :class="isActive('GetStarted') ? 'text-blue-600' : 'hover:text-blue-600'"
        >
          Get started
        </RouterLink>
        <RouterLink
          to="/history"
          class="transition-colors"
          :class="isActive('History') ? 'text-blue-600' : 'hover:text-blue-600'"
        >
          History
        </RouterLink>
      </nav>
      <div class="flex items-center">
        <button type="button" class="text-sm font-medium text-slate-600 hover:text-slate-900">Sign in</button>
      </div>
    </div>
  </header>
</template>
