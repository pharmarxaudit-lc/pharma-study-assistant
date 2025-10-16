<template>
  <div class="progress-view">
    <h2>📊 Progress Dashboard</h2>
    <p class="subtitle">Track your learning progress and exam history</p>

    <div class="placeholder">
      <div class="placeholder-icon">🚧</div>
      <h3>Coming Soon</h3>
      <p>Progress tracking features are under development.</p>
      <p>This section will include:</p>
      <ul>
        <li>Overall statistics and accuracy rates</li>
        <li>Study streak calendar</li>
        <li>Performance trends over time</li>
        <li>Topic strength analysis</li>
        <li>Exam history and results</li>
        <li>Spaced repetition review queue</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
console.log('[ProgressView] Initialized')
</script>

<style scoped>
.progress-view {
  max-width: 1200px;
  margin: 0 auto;
}

.subtitle {
  color: #666;
  margin-bottom: 2rem;
}

h2 {
  margin-bottom: 0.5rem;
}

.placeholder {
  background: #f9f9f9;
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 3rem 2rem;
  text-align: center;
  margin-top: 2rem;
}

.placeholder-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.placeholder h3 {
  color: #333;
  margin-bottom: 1rem;
}

.placeholder p {
  color: #666;
  margin-bottom: 1rem;
}

.placeholder ul {
  list-style: none;
  padding: 0;
  margin-top: 1.5rem;
}

.placeholder li {
  color: #666;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

.placeholder li:last-child {
  border-bottom: none;
}
</style>
