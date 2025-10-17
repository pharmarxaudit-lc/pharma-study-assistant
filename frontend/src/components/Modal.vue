<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">{{ title }}</h3>
            <button v-if="showClose" class="modal-close" @click="cancel" aria-label="Close">
              ×
            </button>
          </div>

          <div class="modal-body">
            <slot>{{ message }}</slot>
          </div>

          <div class="modal-footer">
            <button
              v-if="!hideCancel"
              class="modal-button modal-button-cancel"
              @click="cancel"
            >
              {{ cancelText }}
            </button>
            <button
              class="modal-button modal-button-confirm"
              :class="confirmClass"
              @click="confirm"
            >
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  show: boolean
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  type?: 'info' | 'warning' | 'danger' | 'success'
  hideCancel?: boolean
  showClose?: boolean
  closeOnOverlay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Confirm',
  message: '',
  confirmText: 'OK',
  cancelText: 'Cancel',
  type: 'info',
  hideCancel: false,
  showClose: true,
  closeOnOverlay: true
})

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const confirmClass = computed(() => {
  return `modal-button-${props.type}`
})

function confirm() {
  emit('confirm')
}

function cancel() {
  emit('cancel')
}

function handleOverlayClick() {
  if (props.closeOnOverlay) {
    cancel()
  }
}
</script>

<style scoped>
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

/* Modal Container */
.modal-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Modal Header */
.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
}

.modal-close {
  background: none;
  border: none;
  font-size: 2rem;
  line-height: 1;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #f5f5f5;
  color: #666;
}

/* Modal Body */
.modal-body {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
  color: #555;
  font-size: 1rem;
  line-height: 1.6;
}

/* Modal Footer */
.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.modal-button {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  min-width: 80px;
}

.modal-button-cancel {
  background: white;
  color: #666;
  border: 2px solid #ddd;
}

.modal-button-cancel:hover {
  background: #f5f5f5;
  border-color: #ccc;
}

.modal-button-confirm {
  color: white;
}

.modal-button-info {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.modal-button-info:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.modal-button-success {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
}

.modal-button-success:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.modal-button-warning {
  background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
}

.modal-button-warning:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

.modal-button-danger {
  background: linear-gradient(135deg, #F44336 0%, #D32F2F 100%);
}

.modal-button-danger:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.3);
}

/* Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9);
  opacity: 0;
}
</style>
