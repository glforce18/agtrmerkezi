/**
 * Simple Toast Notification Composable
 * Displays temporary notification messages to the user
 */

let toastContainer = null

// Initialize toast container
const initToastContainer = () => {
  if (toastContainer) return

  toastContainer = document.createElement('div')
  toastContainer.id = 'toast-container'
  toastContainer.className = 'fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none'
  document.body.appendChild(toastContainer)
}

// Toast types with styling
const toastStyles = {
  success: 'bg-green-500/90 text-white',
  error: 'bg-red-500/90 text-white',
  warning: 'bg-yellow-500/90 text-white',
  info: 'bg-blue-500/90 text-white'
}

// Toast icons
const toastIcons = {
  success: '✅',
  error: '❌',
  warning: '⚠️',
  info: 'ℹ️'
}

export function useToast() {
  const show = (message, type = 'success', duration = 3000) => {
    // Initialize container if needed
    initToastContainer()

    // Create toast element
    const toast = document.createElement('div')
    const styleClass = toastStyles[type] || toastStyles.info
    const icon = toastIcons[type] || toastIcons.info

    toast.className = `${styleClass} px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 pointer-events-auto animate-slide-in-right max-w-sm backdrop-blur-sm`
    toast.innerHTML = `
      <span class="text-lg">${icon}</span>
      <span class="font-medium">${message}</span>
    `

    // Add to container
    toastContainer.appendChild(toast)

    // Auto remove after duration
    setTimeout(() => {
      toast.style.animation = 'slide-out-right 0.3s ease-out'
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast)
        }
      }, 300)
    }, duration)
  }

  return { show }
}

// Add CSS animations via style tag (if not already added)
if (typeof document !== 'undefined' && !document.getElementById('toast-animations')) {
  const style = document.createElement('style')
  style.id = 'toast-animations'
  style.textContent = `
    @keyframes slide-in-right {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }

    @keyframes slide-out-right {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(100%);
        opacity: 0;
      }
    }

    .animate-slide-in-right {
      animation: slide-in-right 0.3s ease-out;
    }
  `
  document.head.appendChild(style)
}
