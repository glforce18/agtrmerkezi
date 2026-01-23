/**
 * AGTR Merkezi - Toast Notification System
 * Kullanım: const { showToast, showSuccess, showError } = useToast()
 */

import { ref, readonly } from 'vue'

// Global toast state
const toasts = ref([])
let toastId = 0

// Toast types with icons and colors
const TOAST_TYPES = {
  success: { icon: '✓', bgClass: 'toast-success', duration: 3000 },
  error: { icon: '✕', bgClass: 'toast-error', duration: 5000 },
  warning: { icon: '⚠', bgClass: 'toast-warning', duration: 4000 },
  info: { icon: 'ℹ', bgClass: 'toast-info', duration: 3000 },
  armor: { icon: '🛡️', bgClass: 'toast-armor', duration: 4000 },
  level: { icon: '⬆️', bgClass: 'toast-level', duration: 5000 },
  badge: { icon: '🏆', bgClass: 'toast-badge', duration: 5000 }
}

function addToast(message, type = 'info', options = {}) {
  const id = ++toastId
  const typeConfig = TOAST_TYPES[type] || TOAST_TYPES.info
  const duration = options.duration || typeConfig.duration

  const toast = {
    id,
    message,
    type,
    icon: options.icon || typeConfig.icon,
    bgClass: typeConfig.bgClass,
    title: options.title || null,
    visible: true,
    progress: 100
  }

  toasts.value.push(toast)

  // Auto dismiss with progress
  if (duration > 0) {
    const startTime = Date.now()
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime
      const remaining = Math.max(0, 100 - (elapsed / duration) * 100)
      const t = toasts.value.find(t => t.id === id)
      if (t) t.progress = remaining
      if (remaining <= 0) {
        clearInterval(interval)
        removeToast(id)
      }
    }, 50)
  }
  return id
}

function removeToast(id) {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value[index].visible = false
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, 300)
  }
}

export function useToast() {
  return {
    toasts: readonly(toasts),
    showToast: (message, type = 'info', options = {}) => addToast(message, type, options),
    showSuccess: (message, options = {}) => addToast(message, 'success', options),
    showError: (message, options = {}) => addToast(message, 'error', options),
    showWarning: (message, options = {}) => addToast(message, 'warning', options),
    showInfo: (message, options = {}) => addToast(message, 'info', options),
    showArmorEarned: (amount, reason = '') => addToast(`+${amount} Armor kazandin!${reason ? ' ' + reason : ''}`, 'armor', { title: 'Armor Kazanildi' }),
    showLevelUp: (newLevel) => addToast(`Tebrikler! Level ${newLevel} oldun!`, 'level', { title: 'Level Atladin!' }),
    showBadgeEarned: (badgeName) => addToast(`"${badgeName}" rozetini kazandin!`, 'badge', { title: 'Yeni Rozet!' }),
    removeToast
  }
}

export { toasts, addToast, removeToast }
