<template>
  <div class="app-layout">
    <Navigation />
    <main class="main-content" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import Navigation from './components/Navigation.vue'

const isSidebarCollapsed = ref(false)

function handleSidebarToggle(event: Event) {
  const customEvent = event as CustomEvent
  isSidebarCollapsed.value = customEvent.detail
}

onMounted(() => {
  window.addEventListener('sidebar-toggle', handleSidebarToggle)
  // Check saved preference
  const saved = localStorage.getItem('sidebarCollapsed')
  if (saved === 'true') {
    isSidebarCollapsed.value = true
  }
})

onUnmounted(() => {
  window.removeEventListener('sidebar-toggle', handleSidebarToggle)
})

console.log('[App] Application initialized with router')
</script>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-layout {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  margin-left: 250px;
  padding: 2rem;
  background: #f5f5f5;
  transition: margin-left 0.3s ease;
}

.main-content.sidebar-collapsed {
  margin-left: 70px;
}
</style>
