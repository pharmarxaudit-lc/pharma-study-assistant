<template>
  <div class="process-view">
    <h2>📄 Process PDFs</h2>
    <p class="subtitle">Upload and extract content from pharmacy law PDFs</p>

    <FileUpload v-if="step === 'upload'" @uploaded="handleUpload" />
    <ProcessingStatus v-if="step === 'process'" :fileId="fileId" @complete="step = 'result'" @restart="resetApp" />
    <ResultViewer v-if="step === 'result'" :fileId="fileId" @restart="resetApp" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FileUpload from '../components/FileUpload.vue'
import ProcessingStatus from '../components/ProcessingStatus.vue'
import ResultViewer from '../components/ResultViewer.vue'

const step = ref<'upload' | 'process' | 'result'>('upload')
const fileId = ref('')

console.log('[ProcessView] Initialized')

function handleUpload(id: string) {
  console.log('[ProcessView] File uploaded with ID:', id)
  fileId.value = id
  step.value = 'process'
}

function resetApp() {
  console.log('[ProcessView] Resetting to upload')
  step.value = 'upload'
  fileId.value = ''
}
</script>

<style scoped>
.process-view {
  max-width: 1200px;
  margin: 0 auto;
}

.subtitle {
  color: #666;
  margin-bottom: 2rem;
}

h2 {
  margin-bottom: 0.5rem;
}
</style>
