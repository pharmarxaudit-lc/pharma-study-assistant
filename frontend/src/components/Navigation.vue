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
  background: linear-gradient(180deg, #1a2332 0%, #2c3e50 50%, #34495e 100%);
  color: white;
  min-height: 100vh;
  width: 250px;
  padding: 2rem 0;
  position: fixed;
  left: 0;
  top: 0;
  transition: width 0.3s ease;
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
}

.navigation.collapsed {
  width: 70px;
}

.toggle-btn {
  position: absolute;
  top: 1.5rem;
  right: -12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  transform: translateX(2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
  border-color: rgba(255, 255, 255, 0.4);
}

.collapsed-title {
  text-align: center;
  font-size: 2rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.nav-header {
  padding: 0 1.5rem;
  margin-bottom: 2.5rem;
  position: relative;
}

.nav-header h1 {
  font-size: 1.4rem;
  margin: 0;
  color: white;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  letter-spacing: 0.5px;
}

.nav-header::after {
  content: '';
  position: absolute;
  bottom: -1rem;
  left: 1.5rem;
  right: 1.5rem;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent);
}

.navigation.collapsed .nav-header::after {
  display: none;
}

.nav-menu {
  list-style: none;
  padding: 0 0.75rem;
  margin: 0;
}

.nav-menu li {
  margin-bottom: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.85rem 1rem;
  color: #bdc3c7;
  text-decoration: none;
  transition: all 0.3s ease;
  border-radius: 12px;
  position: relative;
  overflow: hidden;
}

.nav-link::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 3px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.nav-link:hover {
  background: rgba(102, 126, 234, 0.15);
  color: white;
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.nav-link:hover::before {
  transform: scaleY(1);
}

.nav-link.router-link-active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.25) 0%, rgba(118, 75, 162, 0.25) 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.nav-link.router-link-active::before {
  transform: scaleY(1);
}

.nav-link.router-link-active .nav-icon {
  transform: scale(1.1);
  filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.6));
}

.nav-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
  width: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.navigation.collapsed .nav-icon {
  margin-right: 0;
}

.nav-label {
  font-size: 0.95rem;
  font-weight: 500;
  letter-spacing: 0.3px;
}
</style>
