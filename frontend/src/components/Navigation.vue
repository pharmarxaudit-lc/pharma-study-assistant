<template>
  <nav class="navigation" :class="{ collapsed: isCollapsed }">
    <button class="toggle-btn" @click="toggleSidebar" :title="isCollapsed ? 'Expand' : 'Collapse'">
      {{ isCollapsed ? '▶' : '◀' }}
    </button>

    <div class="nav-header">
      <h1 v-if="!isCollapsed">📚 Pharmacy Exam Prep</h1>
      <h1 v-else class="collapsed-title">📚</h1>
    </div>
    <ul class="nav-menu">
      <li>
        <router-link to="/process" class="nav-link">
          <span class="nav-icon">📄</span>
          <span class="nav-label" v-if="!isCollapsed">Process PDFs</span>
        </router-link>
      </li>
      <li>
        <router-link to="/exam" class="nav-link">
          <span class="nav-icon">📝</span>
          <span class="nav-label" v-if="!isCollapsed">Exam Prep</span>
        </router-link>
      </li>
      <li>
        <router-link to="/history" class="nav-link">
          <span class="nav-icon">📜</span>
          <span class="nav-label" v-if="!isCollapsed">History</span>
        </router-link>
      </li>
      <li>
        <router-link to="/progress" class="nav-link">
          <span class="nav-icon">📊</span>
          <span class="nav-label" v-if="!isCollapsed">Progress</span>
        </router-link>
      </li>
      <li>
        <router-link to="/maintenance" class="nav-link">
          <span class="nav-icon">🔧</span>
          <span class="nav-label" v-if="!isCollapsed">Maintenance</span>
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isCollapsed = ref(false)

function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value
  // Store preference
  localStorage.setItem('sidebarCollapsed', String(isCollapsed.value))
  // Emit event for main content to adjust
  window.dispatchEvent(new CustomEvent('sidebar-toggle', { detail: isCollapsed.value }))
}

// Load saved preference on mount
const saved = localStorage.getItem('sidebarCollapsed')
if (saved === 'true') {
  isCollapsed.value = true
}

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
  transition: width 0.3s ease;
}

.navigation.collapsed {
  width: 70px;
}

.toggle-btn {
  position: absolute;
  top: 1rem;
  right: -15px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.toggle-btn:hover {
  background: #2980b9;
}

.collapsed-title {
  text-align: center;
  font-size: 2rem;
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
