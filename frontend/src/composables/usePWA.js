/**
 * AGTR Merkezi - PWA Composable
 * Service Worker registration and PWA features
 */

import { ref, readonly, onMounted } from 'vue'

const isSupported = ref(false)
const isInstalled = ref(false)
const isOnline = ref(navigator.onLine)
const registration = ref(null)
const updateAvailable = ref(false)
const installPrompt = ref(null)

/**
 * Register service worker
 */
async function registerServiceWorker() {
  if (!('serviceWorker' in navigator)) {
    // Service Worker not supported
    return null
  }

  isSupported.value = true

  try {
    const reg = await navigator.serviceWorker.register('/sw.js', {
      scope: '/'
    })

    registration.value = reg
    // Service Worker registered

    // Check for updates
    reg.addEventListener('updatefound', () => {
      const newWorker = reg.installing

      newWorker.addEventListener('statechange', () => {
        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
          updateAvailable.value = true
          // New version available
        }
      })
    })

    return reg
  } catch (error) {
    // Service Worker registration failed
    return null
  }
}

/**
 * Update service worker
 */
async function updateServiceWorker() {
  if (!registration.value) return

  try {
    await registration.value.update()

    if (registration.value.waiting) {
      registration.value.waiting.postMessage({ type: 'SKIP_WAITING' })
      window.location.reload()
    }
  } catch (error) {
    // Update failed
  }
}

/**
 * Handle install prompt
 */
function handleInstallPrompt(event) {
  event.preventDefault()
  installPrompt.value = event
  // Install prompt captured
}

/**
 * Show install prompt
 */
async function showInstallPrompt() {
  if (!installPrompt.value) {
    // No install prompt available
    return false
  }

  installPrompt.value.prompt()

  const { outcome } = await installPrompt.value.userChoice
  // Install outcome captured

  installPrompt.value = null
  return outcome === 'accepted'
}

/**
 * Check if app is installed
 */
function checkInstalled() {
  // Check display-mode
  if (window.matchMedia('(display-mode: standalone)').matches) {
    isInstalled.value = true
    return true
  }

  // iOS check
  if (window.navigator.standalone === true) {
    isInstalled.value = true
    return true
  }

  return false
}

/**
 * Request notification permission
 */
async function requestNotificationPermission() {
  if (!('Notification' in window)) {
    // Notifications not supported
    return 'denied'
  }

  const permission = await Notification.requestPermission()
  // Notification permission received
  return permission
}

/**
 * Subscribe to push notifications
 */
async function subscribeToPush(vapidPublicKey) {
  if (!registration.value) return null

  try {
    const subscription = await registration.value.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
    })

    // Push subscribed
    return subscription
  } catch (error) {
    // Push subscription failed
    return null
  }
}

/**
 * Helper: Convert VAPID key
 */
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4)
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/')

  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }

  return outputArray
}

/**
 * PWA Composable
 */
export function usePWA() {
  onMounted(() => {
    // Register service worker
    registerServiceWorker()

    // Check installed state
    checkInstalled()

    // Listen for install prompt
    window.addEventListener('beforeinstallprompt', handleInstallPrompt)

    // Listen for app installed
    window.addEventListener('appinstalled', () => {
      isInstalled.value = true
      installPrompt.value = null
      // App installed
    })

    // Listen for online/offline
    window.addEventListener('online', () => {
      isOnline.value = true
    })

    window.addEventListener('offline', () => {
      isOnline.value = false
    })
  })

  return {
    isSupported: readonly(isSupported),
    isInstalled: readonly(isInstalled),
    isOnline: readonly(isOnline),
    updateAvailable: readonly(updateAvailable),
    canInstall: readonly(ref(() => !!installPrompt.value)),

    registerServiceWorker,
    updateServiceWorker,
    showInstallPrompt,
    requestNotificationPermission,
    subscribeToPush
  }
}

export default usePWA
