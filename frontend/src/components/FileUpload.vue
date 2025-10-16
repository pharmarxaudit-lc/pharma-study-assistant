<template>
  <div>
    <div class="drop-zone" :class="{ 'drag-over': isDragging }" @drop.prevent="handleDrop" @dragover.prevent="isDragging = true" @dragleave="isDragging = false" @click="fileInput?.click()">
      <input ref="fileInput" type="file" accept=".pdf" @change="handleSelect" style="display: none" />
      <div v-if="!file">
        <div style="font-size: 64px; margin-bottom: 20px;">📄</div>
        <h3>Drop PDF or click to browse</h3>
        <p>Max 50MB</p>
      </div>
      <div v-else>
        <div style="font-size: 48px;">✓</div>
        <h3>{{ file.name }}</h3>
        <p>{{ formatSize(file.size) }}</p>
      </div>
    </div>

    <div class="actions">
      <button v-if="!file" @click="fileInput?.click()">Choose File</button>
      <template v-else>
        <button @click="clear" style="background: #999;">Clear</button>
        <button @click="upload" :disabled="uploading">{{ uploading ? 'Uploading...' : 'Process' }}</button>
      </template>
    </div>

    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits<{ (e: 'uploaded', id: string): void }>()

const fileInput = ref<HTMLInputElement>()
const file = ref<File | null>(null)
const isDragging = ref(false)
const uploading = ref(false)
const error = ref('')

function handleSelect(e: Event) {
  console.log('[FileUpload] File select event triggered')
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) {
    file.value = target.files[0]
    console.log('[FileUpload] File selected:', file.value.name, 'Size:', file.value.size, 'bytes')
  }
}

function handleDrop(e: DragEvent) {
  console.log('[FileUpload] File drop event triggered')
  isDragging.value = false
  if (e.dataTransfer?.files?.[0]?.type === 'application/pdf') {
    file.value = e.dataTransfer.files[0]
    console.log('[FileUpload] File dropped:', file.value.name, 'Size:', file.value.size, 'bytes')
  } else {
    console.warn('[FileUpload] Dropped file is not a PDF')
  }
}

function clear() {
  console.log('[FileUpload] Clearing selected file')
  file.value = null
}

async function upload() {
  if (!file.value) {
    console.warn('[FileUpload] Upload attempted without file')
    return
  }

  console.log('[FileUpload] Starting upload for:', file.value.name)
  uploading.value = true
  error.value = ''

  const formData = new FormData()
  formData.append('file', file.value)

  try {
    console.log('[FileUpload] Sending POST to /api/upload')
    const res = await axios.post('/api/upload', formData)
    console.log('[FileUpload] Upload response:', res.data)
    console.log('[FileUpload] File ID:', res.data.file_id)
    emit('uploaded', res.data.file_id)
  } catch (err: any) {
    console.error('[FileUpload] Upload failed:', err)
    console.error('[FileUpload] Error response:', err.response?.data)
    error.value = err.response?.data?.error || 'Upload failed'
  } finally {
    uploading.value = false
    console.log('[FileUpload] Upload process completed')
  }
}

function formatSize(bytes: number) {
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ['B', 'KB', 'MB'][i]
}
</script>
