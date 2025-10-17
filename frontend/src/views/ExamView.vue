<template>
  <div class="exam-view">
    <!-- Show SessionConfig if no active session -->
    <SessionConfig v-if="!hasActiveSession" />

    <!-- Show QuestionDisplay if session is active and not completed -->
    <QuestionDisplay v-else-if="hasActiveSession && !sessionComplete" />

    <!-- Show ResultsSummary if session is completed -->
    <ResultsSummary v-else-if="sessionComplete" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import SessionConfig from '../components/SessionConfig.vue'
import QuestionDisplay from '../components/QuestionDisplay.vue'
import ResultsSummary from '../components/ResultsSummary.vue'

// Session state
const hasActiveSession = ref<boolean>(false)
const sessionComplete = ref<boolean>(false)

// Check session status
function checkSessionStatus() {
  // Check for active session first
  const sessionData = sessionStorage.getItem('currentSession')

  // If there's no current session, clear any completion flags
  // This handles the case when user navigates to Exam Prep after a page reload
  if (!sessionData) {
    sessionStorage.removeItem('sessionComplete')
    sessionStorage.removeItem('completedSessionId')
    hasActiveSession.value = false
    sessionComplete.value = false
    return
  }

  // Check if session is complete
  const isComplete = sessionStorage.getItem('sessionComplete')
  if (isComplete === 'true') {
    sessionComplete.value = true
    hasActiveSession.value = true
    console.log('[ExamView] Session complete, showing results')
    return
  }

  // Active session found
  hasActiveSession.value = true
  sessionComplete.value = false
  console.log('[ExamView] Active session found')
}

// Check for active session on mount
onMounted(() => {
  checkSessionStatus()

  // Listen for custom session events
  window.addEventListener('sessionStarted', () => {
    console.log('[ExamView] Session started event received')
    checkSessionStatus()
  })

  window.addEventListener('sessionComplete', () => {
    console.log('[ExamView] Session complete event received')
    checkSessionStatus()
  })
})

console.log('[ExamView] Initialized')
</script>

<style scoped>
.exam-view {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 2rem 0;
}
</style>
