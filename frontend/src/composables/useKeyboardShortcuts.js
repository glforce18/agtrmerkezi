/**
 * AGTR Merkezi - Keyboard Shortcuts System
 * Global ve component-level klavye kısayolları
 */

import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'

// Global shortcuts registry
const globalShortcuts = new Map()
const shortcutSequence = ref([])
const sequenceTimeout = ref(null)

/**
 * Parse shortcut string to key combo
 * Examples: "ctrl+k", "g+h", "shift+?", "escape"
 */
function parseShortcut(shortcut) {
  const parts = shortcut.toLowerCase().split('+')
  return {
    key: parts[parts.length - 1],
    ctrl: parts.includes('ctrl') || parts.includes('control'),
    alt: parts.includes('alt'),
    shift: parts.includes('shift'),
    meta: parts.includes('meta') || parts.includes('cmd')
  }
}

/**
 * Check if event matches shortcut
 */
function matchesShortcut(event, combo) {
  const key = event.key.toLowerCase()

  // Handle special keys
  const keyMap = {
    'escape': 'escape',
    'esc': 'escape',
    'enter': 'enter',
    'return': 'enter',
    'space': ' ',
    'arrowup': 'arrowup',
    'arrowdown': 'arrowdown',
    'arrowleft': 'arrowleft',
    'arrowright': 'arrowright'
  }

  const normalizedKey = keyMap[key] || key

  return (
    normalizedKey === combo.key &&
    event.ctrlKey === combo.ctrl &&
    event.altKey === combo.alt &&
    event.shiftKey === combo.shift &&
    event.metaKey === combo.meta
  )
}

/**
 * Check if user is typing in an input
 */
function isTyping(event) {
  const target = event.target
  const tagName = target.tagName.toLowerCase()

  if (['input', 'textarea', 'select'].includes(tagName)) {
    return true
  }

  if (target.isContentEditable) {
    return true
  }

  return false
}

/**
 * Global keyboard shortcut handler
 */
function handleGlobalKeydown(event) {
  // Check sequence shortcuts (like g+h for go home)
  const key = event.key.toLowerCase()

  // Clear sequence timeout
  if (sequenceTimeout.value) {
    clearTimeout(sequenceTimeout.value)
  }

  // Add to sequence
  shortcutSequence.value.push(key)

  // Set timeout to clear sequence
  sequenceTimeout.value = setTimeout(() => {
    shortcutSequence.value = []
  }, 500)

  // Check sequence shortcuts first
  const sequence = shortcutSequence.value.join('+')

  for (const [shortcut, handler] of globalShortcuts) {
    if (shortcut.includes('+') && !shortcut.includes('ctrl') && !shortcut.includes('alt')) {
      // This is a sequence shortcut like "g+h"
      if (sequence === shortcut) {
        if (!handler.allowInInput && isTyping(event)) continue

        event.preventDefault()
        handler.callback(event)
        shortcutSequence.value = []
        return
      }
    }
  }

  // Check regular shortcuts
  for (const [shortcut, handler] of globalShortcuts) {
    const combo = parseShortcut(shortcut)

    // Skip sequence shortcuts in regular check
    if (!combo.ctrl && !combo.alt && !combo.shift && !combo.meta && shortcut.includes('+')) {
      continue
    }

    if (matchesShortcut(event, combo)) {
      if (!handler.allowInInput && isTyping(event)) continue

      event.preventDefault()
      handler.callback(event)
      shortcutSequence.value = []
      return
    }
  }
}

/**
 * Register global shortcut
 */
export function registerShortcut(shortcut, callback, options = {}) {
  const normalizedShortcut = shortcut.toLowerCase()

  globalShortcuts.set(normalizedShortcut, {
    callback,
    allowInInput: options.allowInInput || false,
    description: options.description || ''
  })

  return () => {
    globalShortcuts.delete(normalizedShortcut)
  }
}

/**
 * Get all registered shortcuts
 */
export function getShortcuts() {
  const shortcuts = []
  for (const [shortcut, handler] of globalShortcuts) {
    shortcuts.push({
      shortcut,
      description: handler.description
    })
  }
  return shortcuts
}

/**
 * Composable for component-level shortcuts
 */
export function useKeyboardShortcuts(shortcuts = {}) {
  const router = useRouter()
  const unsubscribers = []

  onMounted(() => {
    // Register component shortcuts
    for (const [shortcut, config] of Object.entries(shortcuts)) {
      const callback = typeof config === 'function' ? config : config.callback
      const options = typeof config === 'function' ? {} : config

      const unsubscribe = registerShortcut(shortcut, callback, options)
      unsubscribers.push(unsubscribe)
    }
  })

  onUnmounted(() => {
    // Cleanup
    unsubscribers.forEach(unsub => unsub())
  })

  return {
    registerShortcut,
    getShortcuts
  }
}

/**
 * Default navigation shortcuts
 */
export function useNavigationShortcuts() {
  const router = useRouter()

  useKeyboardShortcuts({
    'g+h': {
      callback: () => router.push('/'),
      description: 'Ana Sayfa'
    },
    'g+s': {
      callback: () => router.push('/servers'),
      description: 'Sunucular'
    },
    'g+f': {
      callback: () => router.push('/forum'),
      description: 'Forum'
    },
    'g+w': {
      callback: () => router.push('/wallet'),
      description: 'Cüzdan'
    },
    'g+d': {
      callback: () => router.push('/dashboard'),
      description: 'Dashboard'
    },
    'g+p': {
      callback: () => router.push('/profile'),
      description: 'Profil'
    },
    'shift+?': {
      callback: () => {
        // Emit event to show shortcuts help
        window.dispatchEvent(new CustomEvent('show-shortcuts-help'))
      },
      description: 'Yardım'
    }
  })
}

// Initialize global listener
let initialized = false

export function initKeyboardShortcuts() {
  if (initialized) return

  document.addEventListener('keydown', handleGlobalKeydown)
  initialized = true

  return () => {
    document.removeEventListener('keydown', handleGlobalKeydown)
    initialized = false
  }
}

export default useKeyboardShortcuts
