<script setup>
import MainHeader from './components/MainHeader.vue'
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <MainHeader />
    <router-view />
  </div>
</template>
