<template>
  <div class="session-config">
    <div class="config-card">
      <h2>Configure Study Session</h2>

      <!-- Session Type Selection -->
      <div class="form-section">
        <label class="section-label">Session Type</label>
        <div class="button-group">
          <button
            v-for="type in sessionTypes"
            :key="type.value"
            :class="['type-button', { active: sessionType === type.value }]"
            @click="sessionType = type.value"
          >
            <span class="type-icon">{{ type.icon }}</span>
            <span class="type-name">{{ type.label }}</span>
            <span class="type-desc">{{ type.description }}</span>
          </button>
        </div>
      </div>

      <!-- Number of Questions -->
      <div class="form-section">
        <label class="section-label">Number of Questions</label>
        <div class="question-count-options">
          <button
            v-for="count in questionCounts"
            :key="count"
            :class="['count-button', { active: numQuestions === count }]"
            @click="numQuestions = count"
          >
            {{ count }}
          </button>
        </div>
      </div>

      <!-- Topic Selection -->
      <div class="form-section">
        <label class="section-label">Topics</label>
        <div class="topic-selection">
          <button
            :class="['topic-mode-button', { active: topicMode === 'all' }]"
            @click="topicMode = 'all'; selectedTopics = []"
          >
            All Topics (325 questions)
          </button>
          <button
            :class="['topic-mode-button', { active: topicMode === 'select' }]"
            @click="topicMode = 'select'"
          >
            Select Specific Topics
          </button>
        </div>

        <!-- Topic List (shown when select mode) -->
        <div v-if="topicMode === 'select'" class="topic-list">
          <label v-for="topic in availableTopics" :key="topic.id" class="topic-checkbox">
            <input
              type="checkbox"
              :value="topic.name"
              v-model="selectedTopics"
            />
            <span class="topic-name">{{ topic.name }}</span>
            <span class="topic-count">({{ topic.questionCount }} questions)</span>
          </label>
        </div>
      </div>

      <!-- Difficulty Filter -->
      <div class="form-section">
        <label class="section-label">Difficulty (Optional)</label>
        <div class="difficulty-options">
          <button
            v-for="diff in difficulties"
            :key="diff.value"
            :class="['difficulty-button', diff.value, { active: difficulty === diff.value }]"
            @click="difficulty = difficulty === diff.value ? null : diff.value"
          >
            {{ diff.label }}
          </button>
        </div>
      </div>

      <!-- Additional Options -->
      <div class="form-section">
        <label class="section-label">Additional Options</label>
        <label class="checkbox-option">
          <input type="checkbox" v-model="includeReview" />
          <span class="option-text">Prioritize low accuracy questions</span>
          <span class="option-hint">(Useful for reviewing difficult questions)</span>
        </label>
      </div>

      <!-- Pass Threshold -->
      <div class="form-section">
        <label class="section-label">
          Pass Threshold: <span class="threshold-value">{{ passThreshold }}%</span>
        </label>
        <div class="slider-container">
          <input
            type="range"
            v-model.number="passThreshold"
            min="50"
            max="100"
            step="5"
            class="threshold-slider"
          />
          <div class="slider-labels">
            <span>50%</span>
            <span>75%</span>
            <span>100%</span>
          </div>
        </div>
        <p class="slider-hint">Minimum score required to pass the exam</p>
      </div>

      <!-- Start Button -->
      <div class="action-section">
        <!-- Error message -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <button class="start-button" @click="startSession" :disabled="isLoading">
          <span v-if="isLoading" class="loading-spinner"></span>
          {{ isLoading ? 'Starting Session...' : 'Start Session' }}
        </button>
        <p class="session-summary">
          {{ getSessionSummary() }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../services/api'

// Type definitions
interface SessionType {
  value: 'study' | 'practice' | 'mock'
  label: string
  icon: string
  description: string
}

interface Difficulty {
  value: 'basic' | 'intermediate' | 'advanced'
  label: string
}

interface Topic {
  id: number
  name: string
  questionCount: number
}

// Router
const router = useRouter()

// Session configuration
const sessionType = ref<'study' | 'practice' | 'mock'>('study')
const numQuestions = ref<number>(25)
const topicMode = ref<'all' | 'select'>('all')
const selectedTopics = ref<string[]>([])
const difficulty = ref<'basic' | 'intermediate' | 'advanced' | null>(null)
const includeReview = ref<boolean>(false)
const passThreshold = ref<number>(70) // Default 70%

// Loading and error states
const isLoading = ref<boolean>(false)
const errorMessage = ref<string>('')

// Available options (MOCK DATA - will come from API)
const sessionTypes: SessionType[] = [
  {
    value: 'study',
    label: 'Study',
    icon: '📚',
    description: 'See answers immediately'
  },
  {
    value: 'practice',
    label: 'Practice',
    icon: '✏️',
    description: 'See answers at the end'
  },
  {
    value: 'mock',
    label: 'Mock Exam',
    icon: '🎯',
    description: 'Full timed exam'
  }
]

const questionCounts: number[] = [10, 25, 50, 100]

const difficulties: Difficulty[] = [
  { value: 'basic', label: 'Basic' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' }
]

// MOCK DATA - will come from API
const availableTopics: Topic[] = [
  { id: 1, name: 'La Profesión de Farmacia - Responsabilidad Social', questionCount: 25 },
  { id: 2, name: 'Requisitos para ejercer como Farmacéutico', questionCount: 25 },
  { id: 3, name: 'Denegación y Suspensión de Licencia', questionCount: 25 },
  { id: 4, name: 'Funciones del Farmacéutico', questionCount: 25 },
  { id: 5, name: 'Farmacéutico Regente y Preceptor', questionCount: 25 },
  { id: 6, name: 'Delitos y Conductas Prohibidas', questionCount: 25 },
  { id: 7, name: 'Recetas y Dispensación', questionCount: 25 },
  { id: 8, name: 'Sustancias Controladas', questionCount: 25 },
  { id: 9, name: 'Farmacia Comunitaria', questionCount: 25 },
  { id: 10, name: 'Consulta Farmacéutica', questionCount: 25 },
  { id: 11, name: 'Aspectos Éticos', questionCount: 25 },
  { id: 12, name: 'Responsabilidad Legal', questionCount: 25 },
  { id: 13, name: 'Procedimientos Administrativos', questionCount: 25 }
]

function getSessionSummary(): string {
  const typeLabel = sessionTypes.find(t => t.value === sessionType.value)?.label || 'Study'
  const topicText = topicMode.value === 'all'
    ? 'all topics'
    : `${selectedTopics.value.length} topic(s) selected`
  const diffText = difficulty.value ? ` (${difficulties.find(d => d.value === difficulty.value)?.label})` : ''

  return `${typeLabel}: ${numQuestions.value} questions from ${topicText}${diffText}`
}

async function startSession(): Promise<void> {
  // Validation
  if (topicMode.value === 'select' && selectedTopics.value.length === 0) {
    errorMessage.value = 'Please select at least one topic'
    return
  }

  // Clear previous errors
  errorMessage.value = ''
  isLoading.value = true

  try {
    // Build session config
    const config = {
      file_id: '20251016_113156', // Using the document file_id from database
      session_type: sessionType.value,
      num_questions: numQuestions.value,
      topic_filter: topicMode.value === 'select' && selectedTopics.value.length > 0
        ? selectedTopics.value
        : undefined,
      difficulty_filter: difficulty.value || undefined,
      prioritize_weak: includeReview.value
    }

    console.log('Starting session with config:', config)

    // Call API to start session
    const response = await api.startSession(config)

    console.log('Session started successfully:', response)

    // Store session data in sessionStorage for the exam view to use
    sessionStorage.setItem('currentSession', JSON.stringify({
      sessionId: response.session_id,
      sessionType: response.session_type,
      totalQuestions: response.total_questions,
      currentQuestionNumber: 1, // Always start at question 1
      currentQuestion: response.first_question,
      passThreshold: passThreshold.value // Store pass threshold
    }))

    // Dispatch custom event to notify ExamView
    window.dispatchEvent(new Event('sessionStarted'))

    // Navigate to exam view (will stay on same page if already there)
    await router.push('/exam')

  } catch (error) {
    console.error('Failed to start session:', error)
    errorMessage.value = error instanceof Error
      ? error.message
      : 'Failed to start session. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.session-config {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1rem;
}

.config-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  margin: 0 0 2rem 0;
  color: #2c3e50;
  font-size: 1.75rem;
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.form-section:last-of-type {
  border-bottom: none;
}

.section-label {
  display: block;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

/* Session Type Buttons */
.button-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.type-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  color: #2c3e50;
  cursor: pointer;
  transition: all 0.2s;
}

.type-button:hover {
  border-color: #4CAF50;
  transform: translateY(-2px);
}

.type-button.active {
  border-color: #4CAF50;
  background: #f1f8f4;
}

.type-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.type-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.type-desc {
  font-size: 0.85rem;
  color: #666;
  text-align: center;
}

/* Question Count */
.question-count-options {
  display: flex;
  gap: 1rem;
}

.count-button {
  flex: 1;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  color: #2c3e50;
  font-size: 1.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.count-button:hover {
  border-color: #2196F3;
  color: #2196F3;
}

.count-button.active {
  border-color: #2196F3;
  background: #e3f2fd;
  color: #1976D2;
}

/* Topic Selection */
.topic-selection {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.topic-mode-button {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  color: #2c3e50;
  cursor: pointer;
  transition: all 0.2s;
}

.topic-mode-button:hover {
  border-color: #9C27B0;
  color: #9C27B0;
}

.topic-mode-button.active {
  border-color: #9C27B0;
  background: #f3e5f5;
  color: #7B1FA2;
  font-weight: 600;
}

.topic-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 0.5rem;
  margin-top: 1rem;
  max-height: 300px;
  overflow-y: auto;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 8px;
}

.topic-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  cursor: pointer;
  transition: background 0.2s;
  border-radius: 4px;
}

.topic-checkbox:hover {
  background: white;
}

.topic-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.topic-name {
  flex: 1;
  font-size: 0.9rem;
  color: #2c3e50;
}

.topic-count {
  font-size: 0.85rem;
  color: #666;
}

/* Difficulty Buttons */
.difficulty-options {
  display: flex;
  gap: 1rem;
}

.difficulty-button {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  color: #2c3e50;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.difficulty-button:hover {
  transform: translateY(-2px);
  border-color: #667eea;
  color: #667eea;
}

.difficulty-button.basic.active {
  border-color: #4CAF50;
  background: #e8f5e9;
  color: #2E7D32;
}

.difficulty-button.intermediate.active {
  border-color: #FF9800;
  background: #fff3e0;
  color: #E65100;
}

.difficulty-button.advanced.active {
  border-color: #F44336;
  background: #ffebee;
  color: #C62828;
}

/* Checkbox Options */
.checkbox-option {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 8px;
  cursor: pointer;
}

.checkbox-option input[type="checkbox"] {
  width: 20px;
  height: 20px;
  margin-top: 0.25rem;
  cursor: pointer;
}

.option-text {
  font-weight: 500;
  color: #2c3e50;
}

.option-hint {
  display: block;
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.25rem;
}

/* Action Section */
.action-section {
  margin-top: 2rem;
  text-align: center;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-weight: 500;
  border: 1px solid #ef9a9a;
}

.start-button {
  width: 100%;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.start-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.6);
}

.start-button:active:not(:disabled) {
  transform: translateY(0);
}

.start-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.session-summary {
  margin-top: 1rem;
  color: #666;
  font-size: 0.95rem;
}

/* Pass Threshold Slider */
.threshold-value {
  color: #667eea;
  font-weight: 700;
  font-size: 1.2rem;
}

.slider-container {
  margin: 1rem 0;
}

.threshold-slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(to right, #F44336 0%, #FF9800 50%, #4CAF50 100%);
  outline: none;
  -webkit-appearance: none;
  cursor: pointer;
}

.threshold-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: white;
  border: 3px solid #667eea;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.2s;
}

.threshold-slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.threshold-slider::-moz-range-thumb {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: white;
  border: 3px solid #667eea;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.2s;
}

.threshold-slider::-moz-range-thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #666;
}

.slider-hint {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #666;
  text-align: center;
}
</style>
