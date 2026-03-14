<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goToStart() {
  router.push('/start')
}
</script>

<template>
  <div class="bg-slate-50 text-slate-900 min-h-screen flex flex-col">
    <main class="max-w-4xl mx-auto px-4 py-16 sm:px-6 lg:px-8 flex-1">
      <section class="text-center">
        <h1 class="text-4xl font-bold text-slate-800 tracking-tight">Debate Master</h1>
        <p class="mt-4 text-lg text-slate-600 max-w-2xl mx-auto">
          Run AI-powered debates to stress-test your arguments. Set a topic, choose rounds and trials, and get structured feedback from a judge.
        </p>
        <button
          type="button"
          class="mt-8 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-xl transition-colors shadow-md"
          @click="goToStart"
        >
          Get started
        </button>
      </section>
    </main>
  </div>
</template>
