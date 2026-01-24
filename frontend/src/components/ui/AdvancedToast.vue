<template>
  <Teleport to="body">
    <div class="toast-container" :class="position">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="toast"
          :class="[`toast-${toast.type}`, { 'toast-with-action': toast.action }]"
          @mouseenter="pauseTimer(toast)"
          @mouseleave="resumeTimer(toast)"
        >
          <!-- Icon -->
          <div class="toast-icon" :class="`toast-icon-${toast.type}`">
            <component :is="getIcon(toast.type)" class="w-5 h-5" />
          </div>

          <!-- Content -->
          <div class="toast-content">
            <div class="toast-title" v-if="toast.title">{{ toast.title }}</div>
            <div class="toast-message">{{ toast.message }}</div>
          </div>

          <!-- Action Button -->
          <button
            v-if="toast.action"
            class="toast-action"
            @click="handleAction(toast)"
          >
            {{ toast.action.label }}
          </button>

          <!-- Close Button -->
          <button class="toast-close" @click="removeToast(toast.id)">
            <XIcon class="w-4 h-4" />
          </button>

          <!-- Progress Bar -->
          <div
            v-if="toast.duration > 0"
            class="toast-progress"
            :class="`toast-progress-${toast.type}`"
            :style="{ animationDuration: `${toast.duration}ms` }"
          ></div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive } from 'vue'
import {
  CheckCircleIcon,
  XCircleIcon,
  AlertTriangleIcon,
  InfoIcon,
  XIcon
} from 'lucide-vue-next'

const props = defineProps({
  position: {
    type: String,
    default: 'top-right',
    validator: (v) => ['top-right', 'top-left', 'top-center', 'bottom-right', 'bottom-left', 'bottom-center'].includes(v)
  },
  maxToasts: {
    type: Number,
    default: 5
  }
})

// State
const toasts = ref([])
const timers = reactive({})
let toastId = 0

// Methods
const getIcon = (type) => {
  const icons = {
    success: CheckCircleIcon,
    error: XCircleIcon,
    warning: AlertTriangleIcon,
    info: InfoIcon
  }
  return icons[type] || InfoIcon
}

const addToast = (options) => {
  const id = ++toastId
  const toast = {
    id,
    type: options.type || 'info',
    title: options.title || '',
    message: options.message || '',
    duration: options.duration ?? 5000,
    action: options.action || null,
    onClose: options.onClose || null
  }

  // Limit max toasts
  if (toasts.value.length >= props.maxToasts) {
    toasts.value.shift()
  }

  toasts.value.push(toast)

  // Auto dismiss
  if (toast.duration > 0) {
    startTimer(toast)
  }

  // Play sound
  if (options.sound !== false) {
    playSound(toast.type)
  }

  return id
}

const removeToast = (id) => {
  const toast = toasts.value.find(t => t.id === id)
  if (toast?.onClose) {
    toast.onClose()
  }
  clearTimeout(timers[id])
  delete timers[id]
  toasts.value = toasts.value.filter(t => t.id !== id)
}

const startTimer = (toast) => {
  timers[toast.id] = setTimeout(() => {
    removeToast(toast.id)
  }, toast.duration)
  toast.startTime = Date.now()
  toast.remainingTime = toast.duration
}

const pauseTimer = (toast) => {
  if (timers[toast.id]) {
    clearTimeout(timers[toast.id])
    toast.remainingTime = toast.remainingTime - (Date.now() - toast.startTime)
  }
}

const resumeTimer = (toast) => {
  if (toast.remainingTime > 0) {
    timers[toast.id] = setTimeout(() => {
      removeToast(toast.id)
    }, toast.remainingTime)
    toast.startTime = Date.now()
  }
}

const handleAction = (toast) => {
  if (toast.action?.onClick) {
    toast.action.onClick()
  }
  removeToast(toast.id)
}

const playSound = (type) => {
  // Optional: Add sound effects
  // const sounds = { success: '/sounds/success.mp3', error: '/sounds/error.mp3' }
  // new Audio(sounds[type])?.play().catch(() => {})
}

// Convenience methods
const success = (message, options = {}) => addToast({ ...options, type: 'success', message })
const error = (message, options = {}) => addToast({ ...options, type: 'error', message })
const warning = (message, options = {}) => addToast({ ...options, type: 'warning', message })
const info = (message, options = {}) => addToast({ ...options, type: 'info', message })

// Expose methods
defineExpose({
  addToast,
  removeToast,
  success,
  error,
  warning,
  info
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  pointer-events: none;
  max-width: 420px;
  width: 100%;
}

.toast-container.top-right {
  top: 0;
  right: 0;
}

.toast-container.top-left {
  top: 0;
  left: 0;
}

.toast-container.top-center {
  top: 0;
  left: 50%;
  transform: translateX(-50%);
}

.toast-container.bottom-right {
  bottom: 0;
  right: 0;
  flex-direction: column-reverse;
}

.toast-container.bottom-left {
  bottom: 0;
  left: 0;
  flex-direction: column-reverse;
}

.toast-container.bottom-center {
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  flex-direction: column-reverse;
}

.toast {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  padding-right: 40px;
  background: #18181b;
  border: 1px solid #27272a;
  border-radius: 14px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  pointer-events: auto;
  overflow: hidden;
}

.toast-success {
  border-color: rgba(34, 197, 94, 0.3);
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, #18181b 100%);
}

.toast-error {
  border-color: rgba(239, 68, 68, 0.3);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, #18181b 100%);
}

.toast-warning {
  border-color: rgba(234, 179, 8, 0.3);
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.1) 0%, #18181b 100%);
}

.toast-info {
  border-color: rgba(6, 182, 212, 0.3);
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, #18181b 100%);
}

.toast-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  flex-shrink: 0;
}

.toast-icon-success {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.toast-icon-error {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.toast-icon-warning {
  background: rgba(234, 179, 8, 0.15);
  color: #eab308;
}

.toast-icon-info {
  background: rgba(6, 182, 212, 0.15);
  color: #06b6d4;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-size: 14px;
  font-weight: 600;
  color: #fafafa;
  margin-bottom: 2px;
}

.toast-message {
  font-size: 13px;
  color: #a1a1aa;
  line-height: 1.4;
}

.toast-action {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: #fafafa;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.toast-action:hover {
  background: rgba(255, 255, 255, 0.15);
}

.toast-close {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: #52525b;
  cursor: pointer;
  transition: all 0.2s;
}

.toast-close:hover {
  background: #27272a;
  color: #a1a1aa;
}

.toast-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: currentColor;
  transform-origin: left;
  animation: progress-shrink linear forwards;
}

.toast-progress-success { color: #22c55e; }
.toast-progress-error { color: #ef4444; }
.toast-progress-warning { color: #eab308; }
.toast-progress-info { color: #06b6d4; }

@keyframes progress-shrink {
  from { transform: scaleX(1); }
  to { transform: scaleX(0); }
}

/* Transitions */
.toast-enter-active {
  animation: toast-enter 0.3s ease-out;
}

.toast-leave-active {
  animation: toast-leave 0.2s ease-in forwards;
}

@keyframes toast-enter {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes toast-leave {
  to {
    opacity: 0;
    transform: translateX(100%);
  }
}

/* Mobile adjustments */
@media (max-width: 480px) {
  .toast-container {
    left: 8px;
    right: 8px;
    max-width: none;
    padding: 8px;
  }

  .toast-container.top-center,
  .toast-container.bottom-center {
    transform: none;
    left: 8px;
  }
}
</style>
