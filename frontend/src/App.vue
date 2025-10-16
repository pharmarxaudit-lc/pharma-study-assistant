<template>
  <div class="container">
    <h1>📚 Pharmacy Exam Prep</h1>
    <p class="subtitle">Phase 1: PDF to Structured Markdown</p>

    <FileUpload v-if="step === 'upload'" @uploaded="handleUpload" />
    <ProcessingStatus v-if="step === 'process'" :fileId="fileId" @complete="step = 'result'" @restart="resetApp" />
    <ResultViewer v-if="step === 'result'" :fileId="fileId" @restart="resetApp" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FileUpload from './components/FileUpload.vue'
import ProcessingStatus from './components/ProcessingStatus.vue'
import ResultViewer from './components/ResultViewer.vue'

const step = ref<'upload' | 'process' | 'result'>('upload')
const fileId = ref('')

console.log('[App] Application initialized')

function handleUpload(id: string) {
  console.log('[App] File uploaded with ID:', id)
  fileId.value = id
  step.value = 'process'
  console.log('[App] Switching to processing step')
}

function resetApp() {
  console.log('[App] Resetting application')
  step.value = 'upload'
  fileId.value = ''
}
</script>
