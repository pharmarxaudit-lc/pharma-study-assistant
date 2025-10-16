<template>
  <div class="results-summary">
    <!-- Loading state -->
    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading results...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="errorMessage" class="error-container">
      <div class="error-message">{{ errorMessage }}</div>
      <button class="action-button secondary" @click="startNewSession">
        Start New Session
      </button>
    </div>

    <!-- Results content -->
    <template v-else-if="sessionResults">
      <!-- Results Header -->
      <div class="results-header">
        <div class="score-circle" :class="getScoreClass()">
          <div class="score-content">
            <div class="score-number">{{ sessionResults.scorePercentage }}%</div>
            <div class="score-label">Score</div>
          </div>
        </div>

        <!-- Pass/Fail Badge -->
        <div :class="['pass-fail-badge', getPassFailStatus()]">
          <span class="badge-icon">{{ getPassFailStatus() === 'passed' ? '✓' : '✗' }}</span>
          <span class="badge-text">{{ getPassFailMessage() }}</span>
        </div>

        <h2>{{ getResultMessage() }}</h2>
        <p class="session-type-label">{{ getSessionTypeLabel() }}</p>
      </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">✓</div>
        <div class="stat-value">{{ sessionResults.correctAnswers }}</div>
        <div class="stat-label">Correct</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✗</div>
        <div class="stat-value">{{ sessionResults.incorrectAnswers }}</div>
        <div class="stat-label">Incorrect</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📝</div>
        <div class="stat-value">{{ sessionResults.totalQuestions }}</div>
        <div class="stat-label">Total Questions</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⏱️</div>
        <div class="stat-value">{{ formatTime(sessionResults.timeSpent) }}</div>
        <div class="stat-label">Time Spent</div>
      </div>
    </div>

    <!-- Performance by Topic -->
    <div class="section-card">
      <h3>Performance by Topic</h3>
      <div class="topic-performance-list">
        <div v-for="topic in sessionResults.topicBreakdown" :key="topic.name" class="topic-item">
          <div class="topic-info">
            <span class="topic-name">{{ topic.name }}</span>
            <span class="topic-stats">{{ topic.correct }}/{{ topic.total }} correct</span>
          </div>
          <div class="topic-bar">
            <div
              class="topic-bar-fill"
              :style="{ width: (topic.correct / topic.total * 100) + '%' }"
              :class="getTopicBarClass(topic.correct, topic.total)"
            ></div>
          </div>
          <div class="topic-percentage">{{ Math.round(topic.correct / topic.total * 100) }}%</div>
        </div>
      </div>
    </div>

    <!-- Performance by Difficulty -->
    <div class="section-card">
      <h3>Performance by Difficulty</h3>
      <div class="difficulty-grid">
        <div v-for="diff in sessionResults.difficultyBreakdown" :key="diff.level" class="difficulty-card">
          <div :class="['difficulty-header', diff.level]">
            <span class="difficulty-label">{{ getDifficultyLabel(diff.level) }}</span>
          </div>
          <div class="difficulty-stats">
            <div class="difficulty-score">{{ diff.correct }}/{{ diff.total }}</div>
            <div class="difficulty-percentage">{{ Math.round(diff.correct / diff.total * 100) }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Questions to Review -->
    <div class="section-card">
      <h3>Questions to Review</h3>
      <p class="section-subtitle">Focus on these questions to improve your understanding</p>
      <div class="review-list">
        <div v-for="question in sessionResults.incorrectQuestions" :key="question.id" class="review-item">
          <div class="review-header">
            <span :class="['difficulty-badge', question.difficulty]">
              {{ getDifficultyLabel(question.difficulty) }}
            </span>
            <span class="topic-badge">{{ question.topic }}</span>
          </div>
          <div class="review-question">{{ question.question }}</div>
          <div class="review-answer">
            <span class="review-label">Your answer:</span>
            <span class="incorrect-answer">{{ question.userAnswer }}</span>
          </div>
          <div class="review-answer">
            <span class="review-label">Correct answer:</span>
            <span class="correct-answer">{{ question.correctAnswer }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <button class="action-button primary" @click="reviewIncorrect">
        Review Incorrect Questions
      </button>
      <button class="action-button secondary" @click="startNewSession">
        Start New Session
      </button>
      <button class="action-button tertiary" @click="viewHistory">
        View Session History
      </button>
    </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api, type SessionResults as ApiSessionResults } from '../services/api'

// Router
const router = useRouter()

// Type definitions for UI
interface TopicPerformance {
  name: string
  correct: number
  total: number
}

interface DifficultyPerformance {
  level: 'basic' | 'intermediate' | 'advanced'
  correct: number
  total: number
}

interface IncorrectQuestion {
  id: number
  topic: string
  difficulty: 'basic' | 'intermediate' | 'advanced'
  question: string
  userAnswer: string
  correctAnswer: string
}

interface SessionResults {
  scorePercentage: number
  correctAnswers: number
  incorrectAnswers: number
  totalQuestions: number
  timeSpent: number // seconds
  sessionType: 'study' | 'practice' | 'mock'
  topicBreakdown: TopicPerformance[]
  difficultyBreakdown: DifficultyPerformance[]
  incorrectQuestions: IncorrectQuestion[]
}

// State
const sessionResults = ref<SessionResults | null>(null)
const isLoading = ref<boolean>(true)
const errorMessage = ref<string>('')
const passThreshold = ref<number>(70) // Default, will be loaded from session

// Load session results on mount
onMounted(async () => {
  const completedSessionId = sessionStorage.getItem('completedSessionId')

  if (!completedSessionId) {
    console.error('No completed session ID found')
    errorMessage.value = 'No session results found'
    isLoading.value = false
    return
  }

  // Load pass threshold from session storage
  const sessionData = sessionStorage.getItem('currentSession')
  if (sessionData) {
    try {
      const session = JSON.parse(sessionData)
      if (session.passThreshold) {
        passThreshold.value = session.passThreshold
      }
    } catch (e) {
      console.error('Failed to parse session data:', e)
    }
  }

  try {
    // Fetch results from API
    const apiResults = await api.getSessionResults(Number(completedSessionId))

    // Calculate derived data
    const incorrectCount = apiResults.total - apiResults.score
    const incorrectAttempts = apiResults.attempts.filter(a => !a.is_correct)

    // Group by difficulty
    const difficultyMap: Record<string, { correct: number; total: number }> = {}
    apiResults.attempts.forEach(a => {
      if (!difficultyMap[a.difficulty]) {
        difficultyMap[a.difficulty] = { correct: 0, total: 0 }
      }
      difficultyMap[a.difficulty].total++
      if (a.is_correct) {
        difficultyMap[a.difficulty].correct++
      }
    })

    // Transform API response to UI format
    sessionResults.value = {
      scorePercentage: Math.round(apiResults.percentage),
      correctAnswers: apiResults.score,
      incorrectAnswers: incorrectCount,
      totalQuestions: apiResults.total,
      timeSpent: apiResults.duration_seconds,
      sessionType: apiResults.session_type as 'study' | 'practice' | 'mock',
      topicBreakdown: (apiResults.topic_breakdown || []).map(t => ({
        name: t.topic,
        correct: t.correct,
        total: t.total
      })),
      difficultyBreakdown: Object.entries(difficultyMap).map(([level, stats]) => ({
        level: level as 'basic' | 'intermediate' | 'advanced',
        correct: stats.correct,
        total: stats.total
      })),
      incorrectQuestions: incorrectAttempts.map(q => ({
        id: q.question_id,
        topic: q.topic_name,
        difficulty: q.difficulty as 'basic' | 'intermediate' | 'advanced',
        question: q.question_text,
        userAnswer: q.selected_answer,
        correctAnswer: q.correct_answer
      }))
    }

    console.log('Session results loaded:', sessionResults.value)

  } catch (error) {
    console.error('Failed to load session results:', error)
    errorMessage.value = error instanceof Error
      ? error.message
      : 'Failed to load session results'
  } finally {
    isLoading.value = false
  }
})

function getScoreClass(): string {
  if (!sessionResults.value) return ''
  const score = sessionResults.value.scorePercentage
  if (score >= 80) return 'excellent'
  if (score >= 70) return 'good'
  if (score >= 60) return 'fair'
  return 'needs-improvement'
}

function getSessionTypeLabel(): string {
  if (!sessionResults.value) return 'Session'
  const labels: Record<string, string> = {
    study: 'Study Session',
    practice: 'Practice Session',
    mock: 'Mock Exam'
  }
  return labels[sessionResults.value.sessionType] || 'Session'
}

function getDifficultyLabel(difficulty: 'basic' | 'intermediate' | 'advanced'): string {
  const labels: Record<string, string> = {
    basic: 'Basic',
    intermediate: 'Intermediate',
    advanced: 'Advanced'
  }
  return labels[difficulty] || difficulty
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}m ${secs}s`
}

function getTopicBarClass(correct: number, total: number): string {
  const percentage = (correct / total) * 100
  if (percentage >= 80) return 'excellent'
  if (percentage >= 70) return 'good'
  if (percentage >= 60) return 'fair'
  return 'needs-improvement'
}

function reviewIncorrect(): void {
  // TODO: Implement review mode - start new session with only incorrect questions
  console.log('Review feature coming soon')
  alert('Review feature will be implemented in a future update')
}

function startNewSession(): void {
  // Clear session data and navigate to config
  sessionStorage.removeItem('currentSession')
  sessionStorage.removeItem('sessionComplete')
  sessionStorage.removeItem('completedSessionId')
  router.push('/exam')
}

function viewHistory(): void {
  // TODO: Implement session history view
  console.log('Session history feature coming soon')
  alert('Session history feature will be implemented in a future update')
}

function getPassFailStatus(): 'passed' | 'failed' {
  if (!sessionResults.value) return 'failed'
  return sessionResults.value.scorePercentage >= passThreshold.value ? 'passed' : 'failed'
}

function getPassFailMessage(): string {
  const status = getPassFailStatus()
  return status === 'passed'
    ? `You Passed! (${passThreshold.value}% required)`
    : `Keep Practicing (${passThreshold.value}% required)`
}

function getResultMessage(): string {
  const status = getPassFailStatus()
  if (status === 'passed') {
    if (sessionResults.value!.scorePercentage >= 90) {
      return 'Excellent Work! 🎉'
    } else if (sessionResults.value!.scorePercentage >= 80) {
      return 'Great Job! 👏'
    } else {
      return 'Good Work! ✓'
    }
  } else {
    return 'Keep Practicing! 💪'
  }
}
</script>

<style scoped>
.results-summary {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* Results Header */
.results-header {
  text-align: center;
  margin-bottom: 3rem;
}

.score-circle {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  margin: 0 auto 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 8px solid #e0e0e0;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.score-circle.excellent {
  border-color: #4CAF50;
}

.score-circle.good {
  border-color: #2196F3;
}

.score-circle.fair {
  border-color: #FF9800;
}

.score-circle.needs-improvement {
  border-color: #F44336;
}

.score-content {
  text-align: center;
}

.score-number {
  font-size: 3rem;
  font-weight: 700;
  color: #2c3e50;
}

.score-label {
  font-size: 1rem;
  color: #666;
  margin-top: 0.25rem;
}

.results-header h2 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 2rem;
}

.session-type-label {
  color: #666;
  font-size: 1.1rem;
  margin: 0;
}

/* Pass/Fail Badge */
.pass-fail-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 30px;
  font-weight: 700;
  font-size: 1.1rem;
  margin: 1rem 0 1.5rem 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.5s ease;
}

.pass-fail-badge.passed {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
}

.pass-fail-badge.failed {
  background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
  color: white;
}

.badge-icon {
  font-size: 1.5rem;
  font-weight: 700;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.95rem;
  color: #666;
}

/* Section Cards */
.section-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.section-card h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.section-subtitle {
  color: #666;
  margin: 0 0 1.5rem 0;
  font-size: 0.95rem;
}

/* Topic Performance */
.topic-performance-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.topic-item {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1rem;
  align-items: center;
}

.topic-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.topic-name {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
}

.topic-stats {
  font-size: 0.85rem;
  color: #666;
}

.topic-bar {
  grid-column: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.topic-bar-fill {
  height: 100%;
  transition: width 0.5s ease;
}

.topic-bar-fill.excellent {
  background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%);
}

.topic-bar-fill.good {
  background: linear-gradient(90deg, #2196F3 0%, #1976D2 100%);
}

.topic-bar-fill.fair {
  background: linear-gradient(90deg, #FF9800 0%, #F57C00 100%);
}

.topic-bar-fill.needs-improvement {
  background: linear-gradient(90deg, #F44336 0%, #D32F2F 100%);
}

.topic-percentage {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
}

/* Difficulty Grid */
.difficulty-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.difficulty-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.difficulty-header {
  padding: 1rem;
  text-align: center;
  font-weight: 600;
  font-size: 1.1rem;
}

.difficulty-header.basic {
  background: #e8f5e9;
  color: #2E7D32;
}

.difficulty-header.intermediate {
  background: #fff3e0;
  color: #E65100;
}

.difficulty-header.advanced {
  background: #ffebee;
  color: #C62828;
}

.difficulty-stats {
  background: white;
  padding: 1.5rem;
  text-align: center;
}

.difficulty-score {
  font-size: 1.75rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.difficulty-percentage {
  font-size: 0.95rem;
  color: #666;
}

/* Review List */
.review-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.review-item {
  padding: 1.5rem;
  background: #f9f9f9;
  border-radius: 8px;
  border-left: 4px solid #F44336;
}

.review-header {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.difficulty-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.difficulty-badge.basic {
  background: #e8f5e9;
  color: #2E7D32;
}

.difficulty-badge.intermediate {
  background: #fff3e0;
  color: #E65100;
}

.difficulty-badge.advanced {
  background: #ffebee;
  color: #C62828;
}

.topic-badge {
  background: #e3f2fd;
  color: #1976D2;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.review-question {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.review-answer {
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.review-label {
  font-weight: 600;
  color: #666;
  margin-right: 0.5rem;
}

.incorrect-answer {
  color: #F44336;
  font-weight: 500;
}

.correct-answer {
  color: #4CAF50;
  font-weight: 500;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 3rem;
  flex-wrap: wrap;
}

.action-button {
  padding: 1rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.action-button.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-button.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.action-button.secondary {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
}

.action-button.secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
}

.action-button.tertiary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.action-button.tertiary:hover {
  background: #f0f3ff;
  transform: translateY(-2px);
}

/* Loading Container */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 1rem;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(102, 126, 234, 0.2);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-container p {
  color: #666;
  font-size: 1.1rem;
}

/* Error Container */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 2rem;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 1.5rem 2rem;
  border-radius: 8px;
  font-weight: 500;
  border: 1px solid #ef9a9a;
  text-align: center;
  max-width: 500px;
}
</style>
