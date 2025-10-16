<template>
  <div class="question-display">
    <!-- Progress Header -->
    <div class="progress-header">
      <div class="progress-info">
        <span class="question-number">Question {{ currentQuestion }} of {{ totalQuestions }}</span>
        <span class="topic-badge">{{ mockQuestion.topic }}</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
    </div>

    <!-- Question Card -->
    <div class="question-card">
      <!-- Difficulty Badge -->
      <div class="question-meta">
        <span :class="['difficulty-badge', mockQuestion.difficulty]">
          {{ getDifficultyLabel(mockQuestion.difficulty) }}
        </span>
        <span :class="['type-badge', mockQuestion.type]">
          {{ mockQuestion.type === 'single_answer' ? 'Single Answer' : 'Select All That Apply' }}
        </span>
      </div>

      <!-- Question Text -->
      <div class="question-text">
        <p>{{ mockQuestion.question }}</p>
      </div>

      <!-- Answer Options -->
      <div class="answer-options">
        <div
          v-for="option in mockQuestion.options"
          :key="option.id"
          :class="['option', {
            'selected': isSelected(option.id),
            'correct': showFeedback && option.isCorrect,
            'incorrect': showFeedback && isSelected(option.id) && !option.isCorrect
          }]"
          @click="selectOption(option.id)"
        >
          <div class="option-checkbox">
            <input
              :type="mockQuestion.type === 'single_answer' ? 'radio' : 'checkbox'"
              :checked="isSelected(option.id)"
              :disabled="showFeedback"
            />
          </div>
          <div class="option-content">
            <span class="option-letter">{{ option.id }}.</span>
            <span class="option-text">{{ option.text }}</span>
            <span v-if="showFeedback && option.isCorrect" class="correct-icon">✓</span>
            <span v-if="showFeedback && isSelected(option.id) && !option.isCorrect" class="incorrect-icon">✗</span>
          </div>
        </div>
      </div>

      <!-- Submit Button (only show if not showing feedback) -->
      <div v-if="!showFeedback" class="submit-section">
        <button
          class="submit-button"
          :disabled="selectedAnswers.length === 0"
          @click="submitAnswer"
        >
          Submit Answer
        </button>
      </div>

      <!-- Feedback Section (shown after submitting) -->
      <div v-if="showFeedback" class="feedback-section">
        <div :class="['feedback-header', isCorrect ? 'correct' : 'incorrect']">
          <span class="feedback-icon">{{ isCorrect ? '✓' : '✗' }}</span>
          <span class="feedback-title">{{ isCorrect ? 'Correct!' : 'Incorrect' }}</span>
        </div>

        <!-- Explanation -->
        <div class="explanation">
          <h4>Explanation:</h4>
          <p>{{ mockQuestion.explanation }}</p>
        </div>

        <!-- Key Terms -->
        <div v-if="mockQuestion.keyTerms.length > 0" class="key-terms">
          <h4>Key Terms:</h4>
          <div class="terms-list">
            <div v-for="term in mockQuestion.keyTerms" :key="term.term" class="term-item">
              <strong>{{ term.term }}:</strong> {{ term.definition }}
            </div>
          </div>
        </div>

        <!-- Regulatory Context -->
        <div v-if="mockQuestion.regulatory" class="regulatory-info">
          <h4>📋 Legal References:</h4>
          <p>{{ mockQuestion.regulatory }}</p>
        </div>

        <!-- Next Question Button -->
        <div class="next-section">
          <button class="next-button" @click="nextQuestion">
            {{ currentQuestion < totalQuestions ? 'Next Question →' : 'View Results' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Exit Button -->
    <div class="exit-section">
      <button class="exit-button" @click="exitSession">
        Exit Session
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Type definitions
interface QuestionOption {
  id: string
  text: string
  isCorrect: boolean
}

interface KeyTerm {
  term: string
  definition: string
}

interface Question {
  id: number
  topic: string
  difficulty: 'basic' | 'intermediate' | 'advanced'
  type: 'single_answer' | 'choose_all'
  question: string
  options: QuestionOption[]
  explanation: string
  keyTerms: KeyTerm[]
  regulatory: string
}

// Mock data for demonstration
const currentQuestion = ref<number>(5)
const totalQuestions = ref<number>(25)
const selectedAnswers = ref<string[]>([])
const showFeedback = ref<boolean>(false)
const isCorrect = ref<boolean>(false)

const mockQuestion = ref<Question>({
  id: 123,
  topic: 'Requisitos para ejercer como Farmacéutico',
  difficulty: 'intermediate',
  type: 'single_answer',
  question: 'Según la Ley 247 de 2004, ¿cuántas horas de experiencia práctica debe completar un farmacéutico en Puerto Rico para obtener su licencia?',
  options: [
    { id: 'A', text: '1000 horas de internado supervisado', isCorrect: false },
    { id: 'B', text: '1500 horas de práctica supervisada', isCorrect: true },
    { id: 'C', text: '2000 horas de experiencia clínica', isCorrect: false },
    { id: 'D', text: '500 horas de práctica comunitaria', isCorrect: false }
  ],
  explanation: 'La Ley 247 de 2004 establece que los farmacéuticos deben completar 1500 horas de práctica supervisada bajo la supervisión de un farmacéutico licenciado en Puerto Rico. Este requisito asegura que los nuevos farmacéuticos tengan experiencia práctica suficiente antes de ejercer de manera independiente.',
  keyTerms: [
    { term: 'Práctica Supervisada', definition: 'Experiencia práctica realizada bajo la supervisión directa de un farmacéutico licenciado' },
    { term: 'Ley 247', definition: 'Ley para Reglamentar el Ejercicio de la Profesión de Farmacia en Puerto Rico' }
  ],
  regulatory: 'Ley 247 de 2004, Artículo 6 - Requisitos de Licenciatura'
})

const progressPercent = computed((): number => {
  return (currentQuestion.value / totalQuestions.value) * 100
})

function getDifficultyLabel(difficulty: 'basic' | 'intermediate' | 'advanced'): string {
  const labels: Record<string, string> = {
    basic: 'Basic',
    intermediate: 'Intermediate',
    advanced: 'Advanced'
  }
  return labels[difficulty] || difficulty
}

function isSelected(optionId: string): boolean {
  return selectedAnswers.value.includes(optionId)
}

function selectOption(optionId: string): void {
  if (showFeedback.value) return // Can't change answer after submitting

  if (mockQuestion.value.type === 'single_answer') {
    selectedAnswers.value = [optionId]
  } else {
    // Multiple selection
    const index = selectedAnswers.value.indexOf(optionId)
    if (index > -1) {
      selectedAnswers.value.splice(index, 1)
    } else {
      selectedAnswers.value.push(optionId)
    }
  }
}

function submitAnswer(): void {
  // Check if answer is correct
  const correctOptions = mockQuestion.value.options
    .filter(opt => opt.isCorrect)
    .map(opt => opt.id)

  const selectedSet = new Set(selectedAnswers.value)
  const correctSet = new Set(correctOptions)

  isCorrect.value = selectedSet.size === correctSet.size &&
    [...selectedSet].every(id => correctSet.has(id))

  showFeedback.value = true

  // TODO: Send answer to API
  console.log('Answer submitted:', {
    questionId: mockQuestion.value.id,
    selected: selectedAnswers.value,
    correct: correctOptions,
    isCorrect: isCorrect.value
  })
}

function nextQuestion(): void {
  // Reset for next question
  selectedAnswers.value = []
  showFeedback.value = false
  isCorrect.value = false

  if (currentQuestion.value < totalQuestions.value) {
    currentQuestion.value++
    // TODO: Load next question from API
    alert('Mock: Would load next question here')
  } else {
    // TODO: Navigate to results page
    alert('Mock: Would show results page here')
  }
}

function exitSession(): void {
  if (confirm('Are you sure you want to exit? Your progress will be saved.')) {
    // TODO: Save session and navigate away
    alert('Mock: Would exit session here')
  }
}
</script>

<style scoped>
.question-display {
  max-width: 900px;
  margin: 0 auto;
  padding: 1rem;
}

/* Progress Header */
.progress-header {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.question-number {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1.1rem;
}

.topic-badge {
  background: #e3f2fd;
  color: #1976D2;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

/* Question Card */
.question-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.question-meta {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.difficulty-badge,
.type-badge {
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
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

.type-badge {
  background: #f3e5f5;
  color: #7B1FA2;
}

/* Question Text */
.question-text {
  margin-bottom: 2rem;
}

.question-text p {
  font-size: 1.15rem;
  line-height: 1.6;
  color: #2c3e50;
  margin: 0;
}

/* Answer Options */
.answer-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.option {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.option:hover:not(.correct):not(.incorrect) {
  border-color: #667eea;
  background: #f8f9ff;
}

.option.selected:not(.correct):not(.incorrect) {
  border-color: #667eea;
  background: #f0f3ff;
}

.option.correct {
  border-color: #4CAF50;
  background: #e8f5e9;
}

.option.incorrect {
  border-color: #F44336;
  background: #ffebee;
}

.option-checkbox {
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.option-checkbox input {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.option-content {
  flex: 1;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.option-letter {
  font-weight: 700;
  color: #667eea;
  flex-shrink: 0;
}

.option-text {
  flex: 1;
  font-size: 1rem;
  line-height: 1.5;
  color: #2c3e50;
}

.correct-icon,
.incorrect-icon {
  font-weight: 700;
  font-size: 1.25rem;
  margin-left: auto;
}

.correct-icon {
  color: #4CAF50;
}

.incorrect-icon {
  color: #F44336;
}

/* Submit Button */
.submit-section {
  text-align: center;
  margin-top: 2rem;
}

.submit-button {
  padding: 1rem 3rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.submit-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Feedback Section */
.feedback-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #e0e0e0;
}

.feedback-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.feedback-header.correct {
  background: #e8f5e9;
  border: 2px solid #4CAF50;
}

.feedback-header.incorrect {
  background: #ffebee;
  border: 2px solid #F44336;
}

.feedback-icon {
  font-size: 1.75rem;
  font-weight: 700;
}

.feedback-header.correct .feedback-icon {
  color: #4CAF50;
}

.feedback-header.incorrect .feedback-icon {
  color: #F44336;
}

.feedback-title {
  font-size: 1.25rem;
  font-weight: 700;
}

.feedback-header.correct .feedback-title {
  color: #2E7D32;
}

.feedback-header.incorrect .feedback-title {
  color: #C62828;
}

/* Explanation */
.explanation,
.key-terms,
.regulatory-info {
  margin-bottom: 1.5rem;
}

.explanation h4,
.key-terms h4,
.regulatory-info h4 {
  color: #2c3e50;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
}

.explanation p,
.regulatory-info p {
  line-height: 1.6;
  color: #555;
  margin: 0;
}

.terms-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.term-item {
  background: #f9f9f9;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  border-left: 3px solid #667eea;
  font-size: 0.95rem;
  line-height: 1.5;
}

.term-item strong {
  color: #667eea;
}

.regulatory-info {
  background: #f0f3ff;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

/* Next Button */
.next-section {
  text-align: center;
  margin-top: 2rem;
}

.next-button {
  padding: 1rem 3rem;
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.next-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
}

/* Exit Button */
.exit-section {
  text-align: center;
}

.exit-button {
  padding: 0.75rem 2rem;
  background: white;
  color: #666;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.exit-button:hover {
  border-color: #F44336;
  color: #F44336;
}
</style>
