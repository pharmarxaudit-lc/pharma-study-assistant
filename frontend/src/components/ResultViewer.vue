<template>
  <div style="text-align: center; padding: 40px;">
    <div style="font-size: 64px;">✅</div>
    <h2 style="color: #27ae60; margin: 20px 0;">Complete!</h2>

    <div style="background: #d4edda; border: 2px solid #28a745; border-radius: 12px; padding: 30px; margin: 30px 0;">
      <p><strong>Your files are ready!</strong></p>
      <p>Markdown + Analysis JSON generated</p>
    </div>

    <div class="actions">
      <button @click="download('markdown')" style="background: #27ae60;">Download Markdown</button>
      <button @click="download('analysis')" style="background: #3498db;">Download JSON</button>
    </div>

    <div class="actions" style="margin-top: 30px;">
      <button @click="emit('restart')" style="background: #999;">Process Another</button>
    </div>

    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const props = defineProps<{ fileId: string }>()
const emit = defineEmits<{ (e: 'restart'): void }>()

const error = ref('')

async function download(type: string) {
  console.log('[ResultViewer] Download requested for type:', type)
  console.log('[ResultViewer] File ID:', props.fileId)

  try {
    const url = `/api/download/${props.fileId}/${type}`
    console.log('[ResultViewer] Requesting download from:', url)

    const res = await axios.get(url, { responseType: 'blob' })
    console.log('[ResultViewer] Download response received, size:', res.data.size, 'bytes')

    const blobUrl = URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = blobUrl
    const filename = `pharmacy_${props.fileId}.${type === 'markdown' ? 'md' : 'json'}`
    link.download = filename

    console.log('[ResultViewer] Triggering download for:', filename)
    link.click()
    URL.revokeObjectURL(blobUrl)
    console.log('[ResultViewer] Download completed successfully')
  } catch (err: any) {
    console.error('[ResultViewer] Download failed:', err)
    console.error('[ResultViewer] Error response:', err.response?.data)
    error.value = 'Download failed'
  }
}
</script>
