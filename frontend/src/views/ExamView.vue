<template>
  <div class="exam-view">
    <SessionConfig />
  </div>
</template>

<script setup lang="ts">
import SessionConfig from '../components/SessionConfig.vue'

console.log('[ExamView] Initialized')
</script>

<style scoped>
.exam-view {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 2rem 0;
}
</style>
