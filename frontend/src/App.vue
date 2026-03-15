<script setup>
import { useRoute } from 'vue-router'
import MainHeader from './components/MainHeader.vue'
import Iridescence from './components/Iridescence.vue'

const route = useRoute()
const hasEffectBackground = () =>
  ['Overview', 'GetStarted', 'History'].includes(route.name)
</script>

<template>
  <div class="min-h-screen antialiased relative" :class="{ 'bg-slate-50': !hasEffectBackground() }">
    <Iridescence
      v-if="hasEffectBackground()"
      :color="[0.5, 0.6, 0.8]"
      :mouse-react="true"
      :amplitude="0.1"
      :speed="1"
      class="fixed inset-0 z-0 w-full h-full"
    />
    <MainHeader :transparent="hasEffectBackground()" />
    <main class="relative z-10">
      <router-view />
    </main>
  </div>
</template>
