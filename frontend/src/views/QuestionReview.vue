<template>
  <div class="review-container">
    <div class="review-header">
      <h1>📝 Question Review</h1>
      <p class="subtitle">Review your answers and learn from explanations</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading session results...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="error-box">
      <p>{{ errorMessage }}</p>
      <router-link to="/history" class="back-button">Back to History</router-link>
    </div>

    <!-- Review Content -->
    <div v-else class="review-content">
      <!-- Session Summary -->
      <div class="session-summary">
        <div class="summary-card">
          <div class="summary-stat">
            <span class="stat-label">Score</span>
            <span class="stat-value">{{ results?.score }}/{{ results?.total }}</span>
          </div>
          <div class="summary-stat">
            <span class="stat-label">Percentage</span>
            <span class="stat-value" :class="getScoreClass(results?.percentage || 0)">
              {{ results?.percentage }}%
            </span>
          </div>
          <div class="summary-stat">
            <span class="stat-label">Duration</span>
            <span class="stat-value">{{ formatDuration(results?.duration_seconds || 0) }}</span>
          </div>
          <div class="summary-stat">
            <span class="stat-label">Status</span>
            <span class="stat-value" :class="results?.percentage >= (results?.pass_threshold || 70) ? 'passed' : 'failed'">
              {{ results?.percentage >= (results?.pass_threshold || 70) ? 'Passed ✓' : 'Needs Review' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Filter Controls -->
      <div class="filter-controls">
        <button
          v-for="filter in filters"
          :key="filter.value"
          @click="activeFilter = filter.value"
          class="filter-button"
          :class="{ active: activeFilter === filter.value }"
        >
          {{ filter.label }} ({{ getFilterCount(filter.value) }})
        </button>
      </div>

      <!-- Questions List -->
      <div class="questions-list">
        <div
          v-for="(attempt, index) in filteredAttempts"
          :key="attempt.question_id"
          class="question-card"
          :class="{ correct: attempt.is_correct, incorrect: !attempt.is_correct }"
        >
          <!-- Question Header -->
          <div class="question-header">
            <h3>Question {{ index + 1 }}</h3>
            <span class="result-badge" :class="attempt.is_correct ? 'correct-badge' : 'incorrect-badge'">
              {{ attempt.is_correct ? '✓ Correct' : '✗ Incorrect' }}
            </span>
          </div>

          <!-- Topic & Difficulty -->
          <div class="question-meta">
            <span class="meta-tag topic-tag">{{ attempt.topic_name }}</span>
            <span class="meta-tag difficulty-tag">{{ attempt.difficulty }}</span>
            <span class="meta-tag time-tag">{{ attempt.time_spent_seconds }}s</span>
          </div>

          <!-- Question Text -->
          <div class="question-text">
            {{ attempt.question_text }}
          </div>

          <!-- Options -->
          <div class="options-list">
            <div
              v-for="(text, letter) in attempt.options"
              :key="letter"
              class="option-item"
              :class="{
                'user-selected': isSelected(letter, attempt.selected_answer),
                'correct-answer': isCorrectAnswer(letter, attempt.correct_answer),
                'wrong-answer': isSelected(letter, attempt.selected_answer) && !attempt.is_correct
              }"
            >
              <span class="option-letter">{{ letter }}.</span>
              <span class="option-text">{{ text }}</span>
              <span v-if="isCorrectAnswer(letter, attempt.correct_answer)" class="answer-marker correct-marker">
                ✓ Correct Answer
              </span>
              <span v-else-if="isSelected(letter, attempt.selected_answer) && !attempt.is_correct" class="answer-marker wrong-marker">
                ✗ Your Answer
              </span>
            </div>
          </div>

          <!-- Explanation -->
          <div class="explanation-box">
            <h4>Explanation:</h4>
            <p>{{ attempt.explanation }}</p>
          </div>
        </div>
      </div>

      <!-- Back Button -->
      <div class="actions">
        <router-link to="/history" class="back-button">
          Back to History
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { api, type SessionResults } from '../services/api'

const route = useRoute()

// State
const results = ref<SessionResults | null>(null)
const isLoading = ref<boolean>(true)
const errorMessage = ref<string>('')
const activeFilter = ref<'all' | 'correct' | 'incorrect'>('all')

// Filters
const filters = [
  { value: 'all' as const, label: 'All Questions' },
  { value: 'correct' as const, label: 'Correct' },
  { value: 'incorrect' as const, label: 'Incorrect' }
]

// Computed
const filteredAttempts = computed(() => {
  if (!results.value?.attempts) return []

  if (activeFilter.value === 'correct') {
    return results.value.attempts.filter(a => a.is_correct)
  } else if (activeFilter.value === 'incorrect') {
    return results.value.attempts.filter(a => !a.is_correct)
  }
  return results.value.attempts
})

// Load session results on mount
onMounted(async () => {
  const sessionId = route.params.sessionId as string

  if (!sessionId) {
    errorMessage.value = 'No session ID provided'
    isLoading.value = false
    return
  }

  try {
    results.value = await api.getSessionResults(parseInt(sessionId))
  } catch (error: any) {
    errorMessage.value = error.message || 'Failed to load session results'
    console.error('Error loading session results:', error)
  } finally {
    isLoading.value = false
  }
})

// Helper functions
function getFilterCount(filter: 'all' | 'correct' | 'incorrect'): number {
  if (!results.value?.attempts) return 0

  if (filter === 'all') return results.value.attempts.length
  if (filter === 'correct') return results.value.attempts.filter(a => a.is_correct).length
  return results.value.attempts.filter(a => !a.is_correct).length
}

function isSelected(letter: string, selectedAnswer: string): boolean {
  const selected = selectedAnswer.split(',').map(s => s.trim())
  return selected.includes(letter)
}

function isCorrectAnswer(letter: string, correctAnswer: string): boolean {
  const correct = correctAnswer.split(',').map(s => s.trim())
  return correct.includes(letter)
}

function getScoreClass(percentage: number): string {
  if (percentage >= 90) return 'score-excellent'
  if (percentage >= 80) return 'score-great'
  if (percentage >= 70) return 'score-good'
  return 'score-needs-work'
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60

  if (mins === 0) return `${secs}s`
  if (secs === 0) return `${mins}m`
  return `${mins}m ${secs}s`
}
</script>

<style scoped>
.review-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

.review-header {
  text-align: center;
  margin-bottom: 2rem;
}

.review-header h1 {
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

/* Session Summary */
.session-summary {
  margin-bottom: 2rem;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-around;
  gap: 2rem;
}

.summary-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  font-weight: 600;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
}

.stat-value.passed {
  color: #4CAF50;
}

.stat-value.failed {
  color: #FF9800;
}

.score-excellent { color: #4CAF50; }
.score-great { color: #8BC34A; }
.score-good { color: #FFC107; }
.score-needs-work { color: #FF9800; }

/* Filter Controls */
.filter-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  justify-content: center;
}

.filter-button {
  padding: 0.75rem 1.5rem;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.filter-button:hover {
  border-color: #667eea;
  color: #667eea;
}

.filter-button.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
}

/* Questions List */
.questions-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.question-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #ccc;
}

.question-card.correct {
  border-left-color: #4CAF50;
}

.question-card.incorrect {
  border-left-color: #FF5252;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.question-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.3rem;
}

.result-badge {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.9rem;
}

.correct-badge {
  background: #E8F5E9;
  color: #4CAF50;
}

.incorrect-badge {
  background: #FFEBEE;
  color: #FF5252;
}

/* Question Meta */
.question-meta {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.meta-tag {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
}

.topic-tag {
  background: #E3F2FD;
  color: #1976D2;
}

.difficulty-tag {
  background: #F3E5F5;
  color: #7B1FA2;
}

.time-tag {
  background: #FFF3E0;
  color: #F57C00;
}

/* Question Text */
.question-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #333;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

/* Options */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  position: relative;
}

.option-item.correct-answer {
  border-color: #4CAF50;
  background: #E8F5E9;
}

.option-item.wrong-answer {
  border-color: #FF5252;
  background: #FFEBEE;
}

.option-letter {
  font-weight: 700;
  font-size: 1.1rem;
  color: #333;
  min-width: 30px;
}

.option-text {
  flex: 1;
  color: #333;
}

.answer-marker {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 700;
  white-space: nowrap;
}

.correct-marker {
  background: #4CAF50;
  color: white;
}

.wrong-marker {
  background: #FF5252;
  color: white;
}

/* Explanation */
.explanation-box {
  background: #f8f9fa;
  border-left: 4px solid #667eea;
  padding: 1.5rem;
  border-radius: 8px;
}

.explanation-box h4 {
  margin: 0 0 0.75rem 0;
  color: #667eea;
  font-size: 1rem;
}

.explanation-box p {
  margin: 0;
  line-height: 1.6;
  color: #333;
}

/* Actions */
.actions {
  text-align: center;
  margin-top: 3rem;
}

.back-button {
  display: inline-block;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: transform 0.2s;
}

.back-button:hover {
  transform: translateY(-2px);
}

/* Responsive */
@media (max-width: 768px) {
  .review-container {
    padding: 1rem;
  }

  .summary-card {
    flex-direction: column;
    gap: 1rem;
  }

  .filter-controls {
    flex-direction: column;
  }

  .question-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .question-meta {
    flex-wrap: wrap;
  }
}
</style>
