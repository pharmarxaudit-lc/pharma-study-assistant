<template>
  <div style="text-align: center; padding: 40px;">
    <div v-if="!error" style="font-size: 64px; animation: spin 2s linear infinite;">⚙️</div>
    <div v-else style="font-size: 64px;">❌</div>

    <h2 v-if="!error">Processing...</h2>
    <h2 v-else style="color: #c62828;">Processing Failed</h2>

    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: progress + '%' }">{{ progress }}%</div>
    </div>

    <p style="color: #666; font-size: 1.1em; margin-top: 20px;">{{ message }}</p>

    <div v-if="error" class="error">
      {{ error }}
      <div style="margin-top: 15px;">
        <button @click="emit('restart')" style="background: #667eea;">Start Over</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{ fileId: string }>()
const emit = defineEmits<{
  (e: 'complete'): void
  (e: 'restart'): void
}>()

const progress = ref(0)
const message = ref('Starting...')
const error = ref('')
let eventSource: EventSource | null = null

onMounted(async () => {
  console.log('[ProcessingStatus] Component mounted for file_id:', props.fileId)
  console.log('[ProcessingStatus] Starting processing request')

  try {
    const url = `/api/process/${props.fileId}`
    console.log('[ProcessingStatus] POST request to:', url)

    const response = await fetch(url, {
      method: 'POST'
    })

    console.log('[ProcessingStatus] Response status:', response.status)

    if (!response.ok) {
      console.error('[ProcessingStatus] Response not OK:', response.statusText)
      error.value = 'Failed to start processing'
      return
    }

    console.log('[ProcessingStatus] Starting to read response stream...')

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      console.error('[ProcessingStatus] Failed to get response reader')
      error.value = 'Failed to read response'
      return
    }

    let chunkCount = 0
    while (true) {
      const { done, value } = await reader.read()
      chunkCount++

      if (done) {
        console.log('[ProcessingStatus] Stream complete. Total chunks:', chunkCount)
        break
      }

      const chunk = decoder.decode(value)
      console.log(`[ProcessingStatus] Chunk ${chunkCount}:`, chunk.substring(0, 100) + '...')

      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const jsonData = line.substring(6)
            const data = JSON.parse(jsonData)

            console.log('[ProcessingStatus] Parsed data:', data)

            if (data.error) {
              console.error('[ProcessingStatus] Error in stream:', data.error)
              error.value = data.error
              return
            }

            if (data.progress !== undefined) {
              progress.value = data.progress
              console.log('[ProcessingStatus] Progress update:', data.progress + '%')
            }

            if (data.message) {
              message.value = data.message
              console.log('[ProcessingStatus] Message update:', data.message)
            }

            if (data.progress === 100) {
              console.log('[ProcessingStatus] Processing complete!')
              setTimeout(() => {
                console.log('[ProcessingStatus] Emitting complete event')
                emit('complete')
              }, 500)
              return
            }
          } catch (e) {
            console.warn('[ProcessingStatus] Failed to parse line:', line, 'Error:', e)
          }
        }
      }
    }
  } catch (err: any) {
    console.error('[ProcessingStatus] Fatal error:', err)
    console.error('[ProcessingStatus] Error stack:', err.stack)
    error.value = err.message || 'Processing failed'
  }
})

onUnmounted(() => eventSource?.close())
</script>

<style scoped>
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
</style>
