<template>
  <nav class="navigation">
    <div class="nav-header">
      <h1>📚 Pharmacy Exam Prep</h1>
    </div>
    <ul class="nav-menu">
      <li>
        <router-link to="/process" class="nav-link">
          <span class="nav-icon">📄</span>
          <span class="nav-label">Process PDFs</span>
        </router-link>
      </li>
      <li>
        <router-link to="/exam" class="nav-link">
          <span class="nav-icon">📝</span>
          <span class="nav-label">Exam Prep</span>
        </router-link>
      </li>
      <li>
        <router-link to="/progress" class="nav-link">
          <span class="nav-icon">📊</span>
          <span class="nav-label">Progress</span>
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
console.log('[Navigation] Initialized')
</script>

<style scoped>
.navigation {
  background: #2c3e50;
  color: white;
  min-height: 100vh;
  width: 250px;
  padding: 2rem 0;
  position: fixed;
  left: 0;
  top: 0;
}

.nav-header {
  padding: 0 1.5rem;
  margin-bottom: 2rem;
}

.nav-header h1 {
  font-size: 1.5rem;
  margin: 0;
  color: white;
}

.nav-menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  color: #ecf0f1;
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  border-left-color: #3498db;
}

.nav-link.router-link-active {
  background: rgba(52, 152, 219, 0.2);
  border-left-color: #3498db;
  color: white;
}

.nav-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
  width: 2rem;
  text-align: center;
}

.nav-label {
  font-size: 1rem;
  font-weight: 500;
}
</style>
