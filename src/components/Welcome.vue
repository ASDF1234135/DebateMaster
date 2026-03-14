<script setup>
import { ref } from 'vue'

const count = ref(0)
</script>

<template>
  <div class="text-center">
    <h1 class="text-3xl font-semibold text-gray-800 mb-4">
      Vue 3 + Vite + Tailwind
    </h1>
    <p class="text-gray-600 mb-6">
      專案已成功啟動，可以開始開發了。
    </p>
    <button
      type="button"
      class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
      @click="count++"
    >
      Count is {{ count }}
    </button>
  </div>
</template>
