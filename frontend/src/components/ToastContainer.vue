<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="['toast', toast.bgClass, { 'toast-hiding': !toast.visible }]"
          @click="removeToast(toast.id)"
        >
          <div class="toast-icon">{{ toast.icon }}</div>
          <div class="toast-content">
            <div v-if="toast.title" class="toast-title">{{ toast.title }}</div>
            <div class="toast-message">{{ toast.message }}</div>
          </div>
          <button class="toast-close" @click.stop="removeToast(toast.id)">×</button>
          <div class="toast-progress" :style="{ width: toast.progress + '%' }"></div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
const { toasts, removeToast } = useToast()
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 380px;
  pointer-events: none;
}

.toast {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  padding-right: 40px;
  border-radius: 12px;
  background: rgba(21, 27, 35, 0.95);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  pointer-events: auto;
  overflow: hidden;
}

.toast-icon {
  font-size: 20px;
  line-height: 1;
  flex-shrink: 0;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  font-size: 14px;
  color: #fff;
  margin-bottom: 4px;
}

.toast-message {
  font-size: 13px;
  color: #a0aec0;
  line-height: 1.4;
}

.toast-close {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #718096;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.toast-close:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.toast-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: currentColor;
  opacity: 0.5;
  transition: width 0.05s linear;
  border-radius: 0 0 0 12px;
}

/* Toast types */
.toast-success {
  border-left: 3px solid #22c55e;
  color: #22c55e;
}

.toast-error {
  border-left: 3px solid #ef4444;
  color: #ef4444;
}

.toast-warning {
  border-left: 3px solid #f59e0b;
  color: #f59e0b;
}

.toast-info {
  border-left: 3px solid #3b82f6;
  color: #3b82f6;
}

.toast-armor {
  border-left: 3px solid #f97316;
  color: #f97316;
  background: linear-gradient(135deg, rgba(21, 27, 35, 0.95), rgba(249, 115, 22, 0.1));
}

.toast-level {
  border-left: 3px solid #a855f7;
  color: #a855f7;
  background: linear-gradient(135deg, rgba(21, 27, 35, 0.95), rgba(168, 85, 247, 0.1));
}

.toast-badge {
  border-left: 3px solid #eab308;
  color: #eab308;
  background: linear-gradient(135deg, rgba(21, 27, 35, 0.95), rgba(234, 179, 8, 0.1));
}

/* Animations */
.toast-enter-active {
  animation: toast-in 0.3s ease-out;
}

.toast-leave-active {
  animation: toast-out 0.3s ease-in;
}

@keyframes toast-in {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes toast-out {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

.toast-hiding {
  animation: toast-out 0.3s ease-in forwards;
}

/* Mobile */
@media (max-width: 480px) {
  .toast-container {
    left: 12px;
    right: 12px;
    max-width: none;
  }
}
</style>
