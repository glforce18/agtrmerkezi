<template>
  <Teleport to="body">
    <div class="toast-container" :class="position">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="toast"
          :class="[toast.type, { 'has-action': toast.action }]"
          @click="toast.action?.onClick"
        >
          <!-- Progress Bar -->
          <div
            v-if="toast.showProgress && toast.duration > 0"
            class="toast-progress"
            :style="{ animationDuration: `${toast.duration}ms` }"
          ></div>

          <!-- Icon -->
          <div class="toast-icon">
            <component :is="getIcon(toast.type)" />
          </div>

          <!-- Content -->
          <div class="toast-content">
            <div v-if="toast.title" class="toast-title">{{ toast.title }}</div>
            <div class="toast-message">{{ toast.message }}</div>
          </div>

          <!-- Action Button -->
          <button
            v-if="toast.action"
            class="toast-action"
            @click.stop="handleAction(toast)"
          >
            {{ toast.action.label }}
          </button>

          <!-- Close Button -->
          <button
            v-if="toast.closable"
            class="toast-close"
            @click.stop="dismiss(toast.id)"
          >
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { h } from 'vue'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  position: {
    type: String,
    default: 'top-right',
    validator: (v) => ['top-right', 'top-left', 'bottom-right', 'bottom-left', 'top-center', 'bottom-center'].includes(v)
  }
})

const { toasts, dismiss } = useToast()

// Icons for each toast type
const getIcon = (type) => {
  const icons = {
    success: () => h('svg', { viewBox: '0 0 24 24', width: 20, height: 20, fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('path', { d: 'M22 11.08V12a10 10 0 1 1-5.93-9.14' }),
      h('path', { d: 'M22 4L12 14.01l-3-3' })
    ]),
    error: () => h('svg', { viewBox: '0 0 24 24', width: 20, height: 20, fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('circle', { cx: 12, cy: 12, r: 10 }),
      h('path', { d: 'M15 9l-6 6M9 9l6 6' })
    ]),
    warning: () => h('svg', { viewBox: '0 0 24 24', width: 20, height: 20, fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('path', { d: 'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z' }),
      h('path', { d: 'M12 9v4M12 17h.01' })
    ]),
    info: () => h('svg', { viewBox: '0 0 24 24', width: 20, height: 20, fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('circle', { cx: 12, cy: 12, r: 10 }),
      h('path', { d: 'M12 16v-4M12 8h.01' })
    ])
  }
  return icons[type] || icons.info
}

const handleAction = (toast) => {
  if (toast.action?.onClick) {
    toast.action.onClick()
  }
  dismiss(toast.id)
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  z-index: 10000;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 400px;
  padding: 16px;
  pointer-events: none;
}

/* Positions */
.toast-container.top-right { top: 0; right: 0; }
.toast-container.top-left { top: 0; left: 0; }
.toast-container.bottom-right { bottom: 0; right: 0; flex-direction: column-reverse; }
.toast-container.bottom-left { bottom: 0; left: 0; flex-direction: column-reverse; }
.toast-container.top-center { top: 0; left: 50%; transform: translateX(-50%); }
.toast-container.bottom-center { bottom: 0; left: 50%; transform: translateX(-50%); flex-direction: column-reverse; }

.toast {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  background: var(--bg-primary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  pointer-events: auto;
}

.toast.has-action {
  cursor: pointer;
}

/* Progress Bar */
.toast-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: currentColor;
  opacity: 0.3;
  animation: progress linear forwards;
  transform-origin: left;
}

@keyframes progress {
  from { transform: scaleX(1); }
  to { transform: scaleX(0); }
}

/* Icon */
.toast-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Content */
.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 2px;
  color: var(--text-primary);
}

.toast-message {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.4;
}

/* Action Button */
.toast-action {
  flex-shrink: 0;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  cursor: pointer;
  transition: background 0.2s;
}

.toast-action:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* Close Button */
.toast-close {
  flex-shrink: 0;
  padding: 4px;
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.toast-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

/* Type Colors */
.toast.success {
  border-left: 3px solid #10b981;
}
.toast.success .toast-icon { color: #10b981; }
.toast.success .toast-progress { background: #10b981; }

.toast.error {
  border-left: 3px solid #ef4444;
}
.toast.error .toast-icon { color: #ef4444; }
.toast.error .toast-progress { background: #ef4444; }

.toast.warning {
  border-left: 3px solid #f59e0b;
}
.toast.warning .toast-icon { color: #f59e0b; }
.toast.warning .toast-progress { background: #f59e0b; }

.toast.info {
  border-left: 3px solid #3b82f6;
}
.toast.info .toast-icon { color: #3b82f6; }
.toast.info .toast-progress { background: #3b82f6; }

/* Transitions */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.top-left .toast-enter-from,
.bottom-left .toast-enter-from {
  transform: translateX(-100%);
}

.top-left .toast-leave-to,
.bottom-left .toast-leave-to {
  transform: translateX(-100%);
}

.top-center .toast-enter-from,
.bottom-center .toast-enter-from {
  transform: translateY(-20px);
}

.top-center .toast-leave-to,
.bottom-center .toast-leave-to {
  transform: translateY(-20px);
}
</style>
