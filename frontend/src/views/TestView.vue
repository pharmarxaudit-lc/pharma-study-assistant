<template>
  <div class="test-view">
    <div class="test-header">
      <h2>Mock Screen Previews</h2>
      <p>Preview different screens for review</p>
    </div>

    <div class="screen-selector">
      <button
        v-for="screen in screens"
        :key="screen.id"
        :class="['screen-button', { active: currentScreen === screen.id }]"
        @click="currentScreen = screen.id"
      >
        {{ screen.name }}
      </button>
    </div>

    <div class="screen-display">
      <SessionConfig v-if="currentScreen === 'config'" />
      <QuestionDisplay v-if="currentScreen === 'question'" />
      <ResultsSummary v-if="currentScreen === 'results'" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SessionConfig from '../components/SessionConfig.vue'
import QuestionDisplay from '../components/QuestionDisplay.vue'
import ResultsSummary from '../components/ResultsSummary.vue'

interface Screen {
  id: 'config' | 'question' | 'results'
  name: string
}

const currentScreen = ref<'config' | 'question' | 'results'>('config')

const screens: Screen[] = [
  { id: 'config', name: '1. Session Config' },
  { id: 'question', name: '2. Question Display' },
  { id: 'results', name: '3. Results Summary' }
]
</script>

<style scoped>
.test-view {
  min-height: 100vh;
  background: #f5f5f5;
}

.test-header {
  background: white;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.test-header h2 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.test-header p {
  margin: 0;
  color: #666;
}

.screen-selector {
  display: flex;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.screen-button {
  padding: 0.75rem 1.5rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  color: #2c3e50;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.screen-button:hover {
  border-color: #667eea;
  color: #667eea;
}

.screen-button.active {
  border-color: #667eea;
  background: #667eea;
  color: white;
}

.screen-display {
  padding: 0 2rem 2rem 2rem;
}

.placeholder {
  background: white;
  padding: 4rem 2rem;
  border-radius: 12px;
  text-align: center;
  font-size: 1.25rem;
  color: #999;
}
</style>
