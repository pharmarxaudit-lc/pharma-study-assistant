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

      <!-- Start Button -->
      <div class="action-section">
        <button class="start-button" @click="startSession">
          Start Session
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

// Session configuration
const sessionType = ref<'study' | 'practice' | 'mock'>('study')
const numQuestions = ref<number>(25)
const topicMode = ref<'all' | 'select'>('all')
const selectedTopics = ref<string[]>([])
const difficulty = ref<'basic' | 'intermediate' | 'advanced' | null>(null)
const includeReview = ref<boolean>(false)

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

function startSession(): void {
  console.log('Starting session with config:', {
    sessionType: sessionType.value,
    numQuestions: numQuestions.value,
    topicMode: topicMode.value,
    selectedTopics: selectedTopics.value,
    difficulty: difficulty.value,
    includeReview: includeReview.value
  })

  // TODO: Call API to start session
  // TODO: Navigate to study/practice/mock view
  alert('Mock: Session would start here!')
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
  font-size: 1.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.count-button:hover {
  border-color: #2196F3;
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
  cursor: pointer;
  transition: all 0.2s;
}

.topic-mode-button:hover {
  border-color: #9C27B0;
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
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.difficulty-button:hover {
  transform: translateY(-2px);
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
}

.start-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.6);
}

.start-button:active {
  transform: translateY(0);
}

.session-summary {
  margin-top: 1rem;
  color: #666;
  font-size: 0.95rem;
}
</style>
