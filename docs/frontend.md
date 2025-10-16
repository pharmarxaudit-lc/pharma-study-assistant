// ============================================================================
// FRONTEND FILES FOR PHARMACY EXAM PREP
// ============================================================================

// ============================================================================
// FILE: frontend/package.json
// ============================================================================
/*
{
  "name": "pharmacy-exam-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vue-tsc": "^1.8.0"
  }
}
*/

// ============================================================================
// FILE: frontend/vite.config.ts
// ============================================================================
/*
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
})
*/

// ============================================================================
// FILE: frontend/tsconfig.json
// ============================================================================
/*
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
*/

// ============================================================================
// FILE: frontend/tsconfig.node.json
// ============================================================================
/*
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
*/

// ============================================================================
// FILE: frontend/index.html
// ============================================================================
/*
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pharmacy Exam Prep - Phase 1</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
*/

// ============================================================================
// FILE: frontend/src/main.ts
// ============================================================================
import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

createApp(App).mount('#app')

// ============================================================================
// FILE: frontend/src/style.css
// ============================================================================
/*
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

#app {
  max-width: 1200px;
  margin: 0 auto;
}

.container {
  background: white;
  border-radius: 16px;
  padding: 50px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

h1 {
  color: #333;
  margin-bottom: 10px;
  font-size: 2.8em;
  font-weight: 700;
}

.subtitle {
  color: #666;
  margin-bottom: 40px;
  font-size: 1.2em;
}

.badge {
  display: inline-block;
  background: #667eea;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85em;
  margin-left: 10px;
  font-weight: 500;
}

button {
  background: #667eea;
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

button:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

button:active:not(:disabled) {
  transform: translateY(0);
}

.progress-bar {
  width: 100%;
  height: 40px;
  background: #e8eaf6;
  border-radius: 20px;
  overflow: hidden;
  margin: 25px 0;
  border: 2px solid #c5cae9;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 16px;
}

.error {
  background: #ffebee;
  border: 2px solid #ef5350;
  border-radius: 8px;
  padding: 16px;
  color: #c62828;
  margin-top: 20px;
  font-weight: 600;
}

.success {
  background: #e8f5e9;
  border: 2px solid #66bb6a;
  border-radius: 8px;
  padding: 16px;
  color: #2e7d32;
  margin-top: 20px;
  font-weight: 600;
}

.info-box {
  background: #e3f2fd;
  border: 2px solid #42a5f5;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
}

.info-box h3 {
  color: #1565c0;
  margin-bottom: 10px;
}

.info-box p {
  color: #0d47a1;
  margin: 5px 0;
}
*/

// ============================================================================
// FILE: frontend/src/App.vue
// ============================================================================
/*
<template>
  <div class="container">
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
      <h1>📚 Pharmacy Exam Prep</h1>
      <span class="badge">Phase 1</span>
    </div>
    <p class="subtitle">PDF to Structured Markdown with AI Analysis</p>
    
    <FileUpload 
      v-if="currentStep === 'upload'"
      @file-uploaded="handleFileUploaded"
    />
    
    <ProcessingStatus
      v-if="currentStep === 'processing'"
      :file-id="fileId"
      @processing-complete="handleProcessingComplete"
    />
    
    <ResultViewer
      v-if="currentStep === 'complete'"
      :file-id="fileId"
      @start-over="resetApp"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FileUpload from './components/FileUpload.vue'
import ProcessingStatus from './components/ProcessingStatus.vue'
import ResultViewer from './components/ResultViewer.vue'

const currentStep = ref<'upload' | 'processing' | 'complete'>('upload')
const fileId = ref('')

function handleFileUploaded(id: string) {
  fileId.value = id
  currentStep.value = 'processing'
}

function handleProcessingComplete() {
  currentStep.value = 'complete'
}

function resetApp() {
  currentStep.value = 'upload'
  fileId.value = ''
}
</script>
*/

// ============================================================================
// FILE: frontend/src/components/FileUpload.vue
// ============================================================================
/*
<template>
  <div class="upload-container">
    <div 
      class="drop-zone"
      :class="{ 'drag-over': isDragging }"
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @click="$refs.fileInput.click()"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".pdf"
        @change="handleFileSelect"
        style="display: none"
      />
      
      <div v-if="!selectedFile" class="drop-prompt">
        <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        <h3>Drop PDF here or click to browse</h3>
        <p>Maximum file size: 50MB</p>
        <p style="margin-top: 10px; font-size: 0.9em; color: #999;">
          PowerPoint-to-PDF files work great!
        </p>
      </div>
      
      <div v-else class="file-info">
        <div style="font-size: 48px; margin-bottom: 15px;">📄</div>
        <h3>{{ selectedFile.name }}</h3>
        <p><strong>Size:</strong> {{ formatFileSize(selectedFile.size) }}</p>
        <p v-if="fileDetails"><strong>Pages:</strong> {{ fileDetails.total_pages }}</p>
      </div>
    </div>
    
    <div class="actions">
      <button v-if="!selectedFile" @click="$refs.fileInput.click()">
        📁 Choose File
      </button>
      <template v-else>
        <button @click="clearFile" style="background: #999;">
          ✕ Clear
        </button>
        <button @click="uploadFile" :disabled="uploading">
          {{ uploading ? '⏳ Uploading...' : '🚀 Upload & Process' }}
        </button>
      </template>
    </div>
    
    <div v-if="error" class="error">
      ⚠️ {{ error }}
    </div>
    
    <div class="info-box" style="margin-top: 30px;">
      <h3>🤖 What happens during processing?</h3>
      <p><strong>1. Extraction:</strong> Text extracted from PDF page-by-page</p>
      <p><strong>2. Analysis:</strong> Claude AI analyzes content for key terms, exam points, relationships</p>
      <p><strong>3. Formatting:</strong> Creates clean markdown with metadata</p>
      <p><strong>4. Output:</strong> Download formatted .md + analysis .json files</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits<{
  (e: 'file-uploaded', fileId: string): void
}>()

const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const fileDetails = ref<any>(null)
const isDragging = ref(false)
const uploading = ref(false)
const error = ref('')

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
    fileDetails.value = null
    error.value = ''
  }
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    const file = event.dataTransfer.files[0]
    
    if (file.type === 'application/pdf') {
      selectedFile.value = file
      fileDetails.value = null
      error.value = ''
    } else {
      error.value = 'Please upload a PDF file'
    }
  }
}

function clearFile() {
  selectedFile.value = null
  fileDetails.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function uploadFile() {
  if (!selectedFile.value) return
  
  uploading.value = true
  error.value = ''
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  
  try {
    const response = await axios.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    fileDetails.value = response.data
    
    // Automatically start processing
    setTimeout(() => {
      emit('file-uploaded', response.data.file_id)
    }, 500)
    
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Upload failed. Please try again.'
  } finally {
    uploading.value = false
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

<style scoped>
.upload-container {
  margin: 30px 0;
}

.drop-zone {
  border: 3px dashed #ccc;
  border-radius: 16px;
  padding: 80px 40px;
  text-align: center;
  transition: all 0.3s;
  cursor: pointer;
  background: #fafafa;
}

.drop-zone:hover {
  border-color: #667eea;
  background: #f8f9ff;
  transform: scale(1.01);
}

.drop-zone.drag-over {
  border-color: #667eea;
  background: #e8eaf6;
  border-style: solid;
  transform: scale(1.02);
}

.drop-prompt svg {
  color: #667eea;
  margin-bottom: 25px;
}

.drop-prompt h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.4em;
}

.drop-prompt p {
  color: #666;
  font-size: 1.05em;
}

.file-info {
  padding: 20px;
}

.file-info h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.3em;
}

.file-info p {
  color: #666;
  margin: 8px 0;
  font-size: 1.05em;
}

.actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 25px;
}
</style>
*/

// ============================================================================
// FILE: frontend/src/components/ProcessingStatus.vue
// ============================================================================
/*
<template>
  <div class="processing-container">
    <div class="icon-container">
      <div class="spinner">⚙️</div>
    </div>
    
    <h2>Processing Your PDF...</h2>
    
    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: localProgress + '%' }">
        {{ localProgress }}%
      </div>
    </div>
    
    <p class="status-message">{{ localMessage }}</p>
    
    <div v-if="processingSteps.length > 0" class="steps-log">
      <h3>📋 Processing Log:</h3>
      <div class="log-entries">
        <div 
          v-for="(step, index) in processingSteps" 
          :key="index"
          class="log-entry"
          :class="{ 'current': index === processingSteps.length - 1 }"
        >
          <span class="check">{{ step.progress === 100 ? '✅' : '▶️' }}</span>
          {{ step.message }}
        </div>
      </div>
    </div>
    
    <div v-if="error" class="error">
      ⚠️ {{ error }}
    </div>
    
    <div class="info-box" style="margin-top: 30px;">
      <p><strong>💡 Pro Tip:</strong> Processing takes 2-5 minutes depending on PDF size. 
      Claude is analyzing each section for key terms, exam points, and question potential!</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  fileId: string
}>()

const emit = defineEmits<{
  (e: 'processing-complete'): void
}>()

const error = ref('')
const localProgress = ref(0)
const localMessage = ref('Initializing...')
const processingSteps = ref<Array<{ message: string, progress: number }>>([])
let eventSource: EventSource | null = null

onMounted(() => {
  startProcessing()
})

onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
  }
})

function startProcessing() {
  eventSource = new EventSource(`/api/process/${props.fileId}`)
  
  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      
      if (data.error) {
        error.value = data.error
        eventSource?.close()
        return
      }
      
      localProgress.value = data.progress || 0
      localMessage.value = data.message || ''
      
      // Add to processing log
      if (data.message) {
        processingSteps.value.push({
          message: data.message,
          progress: data.progress
        })
        
        // Keep only last 10 steps for display
        if (processingSteps.value.length > 10) {
          processingSteps.value.shift()
        }
      }
      
      if (data.progress === 100) {
        setTimeout(() => {
          emit('processing-complete')
          eventSource?.close()
        }, 1000)
      }
    } catch (err) {
      console.error('Error parsing SSE data:', err)
    }
  }
  
  eventSource.onerror = () => {
    error.value = 'Connection lost. Please refresh and try again.'
    eventSource?.close()
  }
}
</script>

<style scoped>
.processing-container {
  text-align: center;
  padding: 40px 20px;
}

.icon-container {
  margin-bottom: 20px;
}

.spinner {
  font-size: 64px;
  animation: spin 2s linear infinite;
  display: inline-block;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

h2 {
  color: #333;
  margin-bottom: 30px;
  font-size: 2em;
}

.status-message {
  color: #666;
  margin-top: 20px;
  font-size: 1.15em;
  font-weight: 500;
}

.steps-log {
  margin-top: 40px;
  text-align: left;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.steps-log h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.2em;
}

.log-entries {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 15px;
  max-height: 300px;
  overflow-y: auto;
}

.log-entry {
  padding: 8px 12px;
  margin: 4px 0;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 0.95em;
}

.log-entry.current {
  background: #e8eaf6;
  color: #667eea;
  font-weight: 600;
}

.log-entry .check {
  margin-right: 8px;
}
</style>
*/

// ============================================================================
// FILE: frontend/src/components/ResultViewer.vue
// ============================================================================
/*
<template>
  <div class="result-container">
    <div style="font-size: 64px; margin-bottom: 20px;">✅</div>
    <h2>Processing Complete!</h2>
    
    <div class="success-message">
      <p><strong>🎉 Your pharmacy study materials are ready!</strong></p>
      <p>Two files have been generated:</p>
      <ul>
        <li><strong>Formatted Markdown</strong> - Clean, structured content for studying</li>
        <li><strong>Analysis JSON</strong> - Rich metadata for Phase 2 question generation</li>
      </ul>
    </div>
    
    <div class="download-section">
      <h3>📥 Download Your Files</h3>
      <div class="download-buttons">
        <button @click="downloadFile('markdown')" class="primary">
          📄 Download Markdown (.md)
        </button>
        <button @click="downloadFile('analysis')" class="secondary">
          📊 Download Analysis (.json)
        </button>
      </div>
    </div>
    
    <div class="info-box" style="margin-top: 30px;">
      <h3>🚀 Next Steps (Phase 2)</h3>
      <p>The analysis.json file contains:</p>
      <ul style="text-align: left; margin-top: 10px;">
        <li>✓ Content classification and difficulty levels</li>
        <li>✓ Key terms with definitions</li>
        <li>✓ Exam-critical points categorized</li>
        <li>✓ Question generation potential scores</li>
        <li>✓ Relationships between topics</li>
      </ul>
      <p style="margin-top: 15px;">
        This will power the exam question generator in Phase 2!
      </p>
    </div>
    
    <div class="actions" style="margin-top: 30px;">
      <button @click="emit('start-over')" style="background: #999;">
        🔄 Process Another PDF
      </button>
    </div>
    
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const props = defineProps<{
  fileId: string
}>()

const emit = defineEmits<{
  (e: 'start-over'): void
}>()

const error = ref('')

async function downloadFile(type: 'markdown' | 'analysis') {
  try {
    const response = await axios.get(`/api/download/${props.fileId}/${type}`, {
      responseType: 'blob'
    })
    
    const extension = type === 'markdown' ? 'md' : 'json'
    const filename = `pharmacy_study_${props.fileId}.${extension}`
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err: any) {
    error.value = `Download failed: ${err.response?.data?.error || err.message}`
  }
}
</script>

<style scoped>
.result-container {
  text-align: center;
  padding: 40px 20px;
}

h2 {
  color: #27ae60;
  margin-bottom: 30px;
  font-size: 2.2em;
  font-weight: 700;
}

.success-message {
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
  border: 2px solid #28a745;
  border-radius: 12px;
  padding: 30px;
  margin: 30px 0;
}

.success-message p {
  color: #155724;
  margin: 12px 0;
  font-size: 1.15em;
}

.success-message ul {
  list-style: none;
  margin-top: 15px;
  text-align: left;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.success-message li {
  padding: 8px 0;
  color: #155724;
}

.download-section {
  margin: 40px 0;
}

.download-section h3 {
  color: #333;
  margin-bottom: 20px;
  font-size: 1.5em;
}

.download-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.primary {
  background: #27ae60;
  font-size: 18px;
  padding: 16px 32px;
}

.primary:hover {
  background: #229954;
}

.secondary {
  background: #3498db;
  font-size: 18px;
  padding: 16px 32px;
}

.secondary:hover {
  background: #2980b9;
}

.info-box ul {
  list-style: none;
  padding-left: 0;
}

.info-box li {
  padding: 5px 0;
}

.actions {
  display: flex;
  justify-content: center;
}
</style>
*/