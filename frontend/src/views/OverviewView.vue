<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goToStart() {
  router.push('/start')
}
</script>

<template>
  <div class="min-h-[calc(100vh-4rem)] flex flex-col bg-transparent">
    <main class="max-w-4xl mx-auto px-4 py-16 sm:px-6 lg:px-8 flex-1">
      <section class="text-center">
        <h1 class="text-4xl font-bold text-white tracking-tight drop-shadow-sm">Debate Master</h1>
        <p class="mt-4 text-lg text-white/90 max-w-2xl mx-auto">
          Run AI-powered debates to stress-test your arguments. Set a topic, choose rounds and trials, and get structured feedback from a judge.
        </p>
        <button type="button" class="btn-madflows mt-8" @click="goToStart">
          <span class="btn-madflows-content">Get started</span>
        </button>
      </section>
    </main>
  </div>
</template>
