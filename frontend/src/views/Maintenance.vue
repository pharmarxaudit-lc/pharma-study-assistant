<template>
  <div class="maintenance-view">
    <h2>🔧 Database Maintenance</h2>
    <p class="subtitle">Manage and monitor your database</p>

    <!-- Schema Check -->
    <div class="card">
      <h3>Schema Health Check</h3>
      <button @click="checkSchema" :disabled="checking" class="btn-primary">
        {{ checking ? 'Checking...' : 'Check Schema' }}
      </button>

      <div v-if="schemaResult" class="result-box" :class="schemaResult.schema_ok ? 'success' : 'error'">
        <p><strong>{{ schemaResult.message }}</strong></p>
        <div v-if="schemaResult.issues && schemaResult.issues.length > 0">
          <p class="error-label">Issues Found:</p>
          <ul>
            <li v-for="(issue, idx) in schemaResult.issues" :key="idx">
              <strong>{{ issue.table }}:</strong> {{ issue.issue }}
              <br><small>Fix: {{ issue.fix }}</small>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Database Info -->
    <div class="card">
      <h3>Database Information</h3>
      <button @click="loadDbInfo" :disabled="loadingInfo" class="btn-secondary">
        {{ loadingInfo ? 'Loading...' : 'Load Info' }}
      </button>

      <div v-if="dbInfo" class="info-box">
        <p><strong>Path:</strong> {{ dbInfo.database_path }}</p>
        <p><strong>Exists:</strong> {{ dbInfo.exists ? 'Yes' : 'No' }}</p>
        <p><strong>Size:</strong> {{ dbInfo.size_mb }} MB ({{ dbInfo.size_bytes.toLocaleString() }} bytes)</p>

        <h4>Record Counts:</h4>
        <ul>
          <li>Documents: {{ dbInfo.record_counts?.documents || 0 }}</li>
          <li>Questions: {{ dbInfo.record_counts?.questions || 0 }}</li>
          <li>Study Sessions: {{ dbInfo.record_counts?.study_sessions || 0 }}</li>
          <li>User Attempts: {{ dbInfo.record_counts?.user_attempts || 0 }}</li>
        </ul>

        <details v-if="dbInfo.tables && dbInfo.tables.length > 0">
          <summary><strong>Table Schemas ({{ dbInfo.tables.length }} tables)</strong></summary>
          <div v-for="table in dbInfo.tables" :key="table.name" class="table-info">
            <h5>{{ table.name }}</h5>
            <ul>
              <li v-for="col in table.columns" :key="col.name">
                {{ col.name }} <span class="type-badge">{{ col.type }}</span>
              </li>
            </ul>
          </div>
        </details>
      </div>
    </div>

    <!-- Database Reset -->
    <div class="card danger-zone">
      <h3>⚠️ Danger Zone</h3>
      <p class="warning-text">
        <strong>Warning:</strong> Resetting the database will permanently delete ALL data including documents, questions, sessions, and user attempts. This action cannot be undone!
      </p>

      <div v-if="!showResetConfirm">
        <button @click="showResetConfirm = true" class="btn-danger">
          Reset Database
        </button>
      </div>

      <div v-else class="confirm-box">
        <p><strong>Are you absolutely sure?</strong></p>
        <p>Type "RESET" to confirm:</p>
        <input
          v-model="resetConfirmText"
          type="text"
          placeholder="Type RESET"
          class="confirm-input"
        >
        <div class="button-group">
          <button
            @click="resetDatabase"
            :disabled="resetConfirmText !== 'RESET' || resetting"
            class="btn-danger"
          >
            {{ resetting ? 'Resetting...' : 'Confirm Reset' }}
          </button>
          <button @click="cancelReset" class="btn-secondary">
            Cancel
          </button>
        </div>
      </div>

      <div v-if="resetResult" class="result-box" :class="resetResult.success ? 'success' : 'error'">
        <p>{{ resetResult.message }}</p>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-box">
      <strong>Error:</strong> {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const API_BASE_URL = import.meta.env.PROD ? '' : 'http://localhost:5001'

const checking = ref(false)
const loadingInfo = ref(false)
const resetting = ref(false)
const showResetConfirm = ref(false)
const resetConfirmText = ref('')

const schemaResult = ref<any>(null)
const dbInfo = ref<any>(null)
const resetResult = ref<any>(null)
const error = ref<string | null>(null)

async function checkSchema() {
  checking.value = true
  error.value = null
  schemaResult.value = null

  try {
    const response = await fetch(`${API_BASE_URL}/api/maintenance/db-check-schema`)
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to check schema')
    }
    schemaResult.value = await response.json()
  } catch (err: any) {
    error.value = err.message
  } finally {
    checking.value = false
  }
}

async function loadDbInfo() {
  loadingInfo.value = true
  error.value = null
  dbInfo.value = null

  try {
    const response = await fetch(`${API_BASE_URL}/api/maintenance/db-info`)
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to load database info')
    }
    dbInfo.value = await response.json()
  } catch (err: any) {
    error.value = err.message
  } finally {
    loadingInfo.value = false
  }
}

async function resetDatabase() {
  if (resetConfirmText.value !== 'RESET') return

  resetting.value = true
  error.value = null
  resetResult.value = null

  try {
    const response = await fetch(`${API_BASE_URL}/api/maintenance/db-reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ confirm: true })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to reset database')
    }

    resetResult.value = await response.json()

    // Reset form
    showResetConfirm.value = false
    resetConfirmText.value = ''

    // Reload database info
    await loadDbInfo()
    await checkSchema()

  } catch (err: any) {
    error.value = err.message
    resetResult.value = { success: false, message: err.message }
  } finally {
    resetting.value = false
  }
}

function cancelReset() {
  showResetConfirm.value = false
  resetConfirmText.value = ''
  resetResult.value = null
}
</script>

<style scoped>
.maintenance-view {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  color: #2c3e50;
  margin-bottom: 8px;
}

.subtitle {
  color: #666;
  margin-bottom: 30px;
}

.card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.card h3 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #2c3e50;
}

.danger-zone {
  border-color: #ff4444;
  background: #fff8f8;
}

.btn-primary, .btn-secondary, .btn-danger {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #45a049;
}

.btn-secondary {
  background: #2196F3;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #0b7dda;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #da190b;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.result-box, .info-box, .error-box {
  margin-top: 16px;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid;
}

.result-box.success {
  background: #d4edda;
  border-color: #c3e6cb;
  color: #155724;
}

.result-box.error {
  background: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
}

.info-box {
  background: #e7f3ff;
  border-color: #b3d9ff;
  color: #004085;
}

.error-box {
  background: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
}

.error-label {
  font-weight: bold;
  margin-top: 12px;
  margin-bottom: 8px;
}

.info-box ul, .result-box ul {
  margin: 12px 0;
  padding-left: 24px;
}

.info-box li, .result-box li {
  margin: 6px 0;
}

.table-info {
  margin: 16px 0;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.table-info h5 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.type-badge {
  display: inline-block;
  background: #666;
  color: white;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 12px;
  margin-left: 8px;
}

.warning-text {
  background: #fff3cd;
  border: 1px solid #ffc107;
  padding: 12px;
  border-radius: 6px;
  color: #856404;
  margin-bottom: 16px;
}

.confirm-box {
  margin-top: 16px;
}

.confirm-input {
  width: 100%;
  padding: 10px;
  margin: 12px 0;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
}

.confirm-input:focus {
  outline: none;
  border-color: #f44336;
}

.button-group {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

details {
  margin-top: 16px;
  cursor: pointer;
}

summary {
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
  user-select: none;
}

summary:hover {
  background: #e9e9e9;
}
</style>
