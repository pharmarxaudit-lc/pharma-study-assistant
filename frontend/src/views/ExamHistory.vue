<template>
  <div class="history-container">
    <div class="history-header">
      <h1>📊 Exam History</h1>
      <p class="subtitle">View your past exam sessions and track progress</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading history...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="error-box">
      <p>{{ errorMessage }}</p>
      <button @click="loadHistory" class="retry-button">Retry</button>
    </div>

    <!-- History Content -->
    <div v-else class="history-content">
      <!-- Filter Section -->
      <div class="filter-section">
        <div class="filter-group">
          <label for="session-type">Session Type:</label>
          <select id="session-type" v-model="filterType" @change="loadHistory">
            <option value="">All Types</option>
            <option value="study">Study</option>
            <option value="practice">Practice</option>
            <option value="mock">Mock Exam</option>
          </select>
        </div>

        <div class="stats-summary">
          <span class="stats-item">
            <strong>{{ totalSessions }}</strong> Total Sessions
          </span>
          <span class="stats-item">
            <strong>{{ averageScore }}%</strong> Average Score
          </span>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="sessions.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <h2>No History Yet</h2>
        <p>Complete your first exam to start tracking your progress!</p>
        <router-link to="/exam" class="start-exam-button">
          Start an Exam
        </router-link>
      </div>

      <!-- Sessions List -->
      <div v-else class="sessions-list">
        <div
          v-for="session in sessions"
          :key="session.id"
          class="session-card"
          :class="getSessionClass(session.percentage)"
          @click="viewSessionDetails(session.id)"
        >
          <div class="session-header">
            <div class="session-info">
              <h3 class="session-type">
                {{ getSessionTypeLabel(session.session_type) }}
              </h3>
              <p class="session-date">{{ formatDate(session.start_time) }}</p>
            </div>
            <div class="session-score">
              <div class="score-circle" :class="getScoreClass(session.percentage)">
                <span class="score-value">{{ session.percentage }}%</span>
              </div>
            </div>
          </div>

          <div class="session-details">
            <div class="detail-item">
              <span class="detail-label">Questions:</span>
              <span class="detail-value">{{ session.score }}/{{ session.total }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Duration:</span>
              <span class="detail-value">{{ formatDuration(session.start_time, session.end_time) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Status:</span>
              <span class="detail-value" :class="session.percentage >= (session.pass_threshold || 70) ? 'passed' : 'failed'">
                {{ session.percentage >= (session.pass_threshold || 70) ? 'Passed ✓' : 'Needs Review' }}
              </span>
            </div>
          </div>

          <div class="session-actions">
            <router-link :to="`/review/${session.id}`" class="action-button review-button" @click.stop>
              Review Answers
            </router-link>
            <button class="action-button view-button" @click.stop="viewSessionDetails(session.id)">
              View Results
            </button>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="sessions.length >= currentLimit && !isLoading" class="load-more-section">
        <button @click="loadMore" class="load-more-button">
          Load More Sessions
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { api, type SessionHistoryItem } from '../services/api'

const router = useRouter()

// State
const sessions = ref<SessionHistoryItem[]>([])
const isLoading = ref<boolean>(true)
const errorMessage = ref<string>('')
const filterType = ref<string>('')
const currentLimit = ref<number>(20)

// Computed properties
const totalSessions = computed(() => sessions.value.length)
const averageScore = computed(() => {
  if (sessions.value.length === 0) return 0
  const sum = sessions.value.reduce((acc, s) => acc + s.percentage, 0)
  return Math.round(sum / sessions.value.length)
})

// Load history on mount
onMounted(() => {
  loadHistory()
})

async function loadHistory(): Promise<void> {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await api.getSessionHistory(currentLimit.value, filterType.value || undefined)
    sessions.value = response.sessions
  } catch (error: any) {
    errorMessage.value = error.message || 'Failed to load session history'
    console.error('Error loading history:', error)
  } finally {
    isLoading.value = false
  }
}

async function loadMore(): Promise<void> {
  currentLimit.value += 20
  await loadHistory()
}

function getSessionTypeLabel(type: string): string {
  const labels: { [key: string]: string } = {
    'study': '📚 Study Session',
    'practice': '✏️ Practice Exam',
    'mock': '🎯 Mock Exam'
  }
  return labels[type] || type
}

function getSessionClass(percentage: number): string {
  if (percentage >= 90) return 'excellent'
  if (percentage >= 80) return 'great'
  if (percentage >= 70) return 'good'
  return 'needs-work'
}

function getScoreClass(percentage: number): string {
  if (percentage >= 90) return 'score-excellent'
  if (percentage >= 80) return 'score-great'
  if (percentage >= 70) return 'score-good'
  return 'score-needs-work'
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Today, ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  if (diffDays === 1) return 'Yesterday, ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  if (diffDays < 7) return diffDays + ' days ago'

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

function formatDuration(startString: string, endString: string): string {
  const start = new Date(startString)
  const end = new Date(endString)
  const diffMs = end.getTime() - start.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))

  if (diffMins < 1) return '< 1 min'
  if (diffMins < 60) return `${diffMins} min`

  const hours = Math.floor(diffMins / 60)
  const mins = diffMins % 60
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
}

function viewSessionDetails(sessionId: number): void {
  // Store session ID for results view
  sessionStorage.setItem('completedSessionId', sessionId.toString())
  router.push('/exam')
}
</script>

<style scoped>
.history-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

.history-header {
  text-align: center;
  margin-bottom: 3rem;
}

.history-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.1rem;
  color: #666;
}

/* Loading and Error States */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-box {
  background: #fee;
  border: 2px solid #fcc;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
}

.retry-button {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

/* Filter Section */
.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.filter-group label {
  font-weight: 600;
  color: #333;
}

.filter-group select {
  padding: 0.5rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  background: white;
}

.stats-summary {
  display: flex;
  gap: 2rem;
}

.stats-item {
  color: #666;
}

.stats-item strong {
  color: #667eea;
  font-size: 1.2rem;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h2 {
  color: #333;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #666;
  margin-bottom: 2rem;
}

.start-exam-button {
  display: inline-block;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: transform 0.2s;
}

.start-exam-button:hover {
  transform: translateY(-2px);
}

/* Sessions List */
.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.session-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #ccc;
  cursor: pointer;
  transition: all 0.3s;
}

.session-card:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.session-card.excellent { border-left-color: #4CAF50; }
.session-card.great { border-left-color: #8BC34A; }
.session-card.good { border-left-color: #FFC107; }
.session-card.needs-work { border-left-color: #FF9800; }

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.session-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.3rem;
  color: #333;
}

.session-date {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.score-circle {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  color: white;
}

.score-excellent { background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); }
.score-great { background: linear-gradient(135deg, #8BC34A 0%, #7CB342 100%); }
.score-good { background: linear-gradient(135deg, #FFC107 0%, #FFA000 100%); }
.score-needs-work { background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%); }

.session-details {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.85rem;
  color: #666;
  font-weight: 600;
}

.detail-value {
  font-size: 1rem;
  color: #333;
  font-weight: 500;
}

.detail-value.passed {
  color: #4CAF50;
  font-weight: 700;
}

.detail-value.failed {
  color: #FF9800;
  font-weight: 700;
}

.session-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.action-button {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-block;
}

.review-button {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.review-button:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.view-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.view-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* Load More */
.load-more-section {
  text-align: center;
  margin-top: 2rem;
}

.load-more-button {
  padding: 1rem 2rem;
  background: white;
  border: 2px solid #667eea;
  color: #667eea;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.load-more-button:hover {
  background: #667eea;
  color: white;
}

/* Responsive */
@media (max-width: 768px) {
  .history-container {
    padding: 1rem;
  }

  .filter-section {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .stats-summary {
    justify-content: space-around;
  }

  .session-details {
    flex-direction: column;
    gap: 0.75rem;
  }

  .session-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .score-circle {
    align-self: flex-end;
  }
}
</style>
