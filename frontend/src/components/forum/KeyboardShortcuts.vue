<template>
  <!-- Shortcuts Hint -->
  <div class="shortcuts-hint" @click="showModal = true" v-if="!isMobile">
    <kbd>?</kbd>
    <span>Klavye kisayollari</span>
  </div>

  <!-- Shortcuts Modal -->
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="showModal" class="shortcuts-modal" @click.self="showModal = false">
        <div class="shortcuts-content">
          <div class="shortcuts-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="4" width="20" height="16" rx="2" />
              <path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M6 16h8" />
            </svg>
            Klavye Kisayollari
          </div>

          <div class="shortcuts-list">
            <div class="shortcut-item" v-for="shortcut in shortcuts" :key="shortcut.key">
              <span class="shortcut-label">{{ shortcut.label }}</span>
              <span class="shortcut-key">
                <kbd v-for="k in shortcut.keys" :key="k">{{ k }}</kbd>
              </span>
            </div>
          </div>

          <div class="shortcuts-footer">
            <span class="shortcuts-esc">ESC ile kapat</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showModal = ref(false)

const isMobile = computed(() => {
  if (typeof window === 'undefined') return false
  return window.innerWidth < 768
})

const shortcuts = [
  { key: 'n', keys: ['N'], label: 'Yeni konu ac' },
  { key: '/', keys: ['/'], label: 'Arama kutusuna odaklan' },
  { key: 't', keys: ['T'], label: 'Sayfa basina git' },
  { key: 'j', keys: ['J'], label: 'Sonraki konuya git' },
  { key: 'k', keys: ['K'], label: 'Onceki konuya git' },
  { key: 'enter', keys: ['Enter'], label: 'Konuyu ac' },
  { key: 'h', keys: ['H'], label: 'Ana sayfaya git' },
  { key: 'f', keys: ['F'], label: 'Forum ana sayfasina git' },
  { key: 'escape', keys: ['Esc'], label: 'Modali kapat' },
  { key: '?', keys: ['?'], label: 'Bu yardimi göster' }
]

const handleKeydown = (e) => {
  // Ignore if typing in input
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return

  switch (e.key) {
    case '?':
      e.preventDefault()
      showModal.value = !showModal.value
      break
    case 'Escape':
      showModal.value = false
      break
    case 'h':
    case 'H':
      if (!e.ctrlKey && !e.metaKey) {
        e.preventDefault()
        router.push('/')
      }
      break
    case 'f':
    case 'F':
      if (!e.ctrlKey && !e.metaKey) {
        e.preventDefault()
        router.push('/forum')
      }
      break
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.shortcuts-hint {
  position: fixed;
  bottom: 20px;
  left: 20px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  font-size: 11px;
  color: var(--text-secondary, #a1a1aa);
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 50;
}

.shortcuts-hint:hover {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
  color: #f97316;
}

.shortcuts-hint kbd {
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  font-family: monospace;
  font-size: 10px;
}

.shortcuts-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.shortcuts-content {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(11, 15, 20, 0.98));
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 16px;
  padding: 20px;
  max-width: 360px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.shortcuts-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
}

.shortcuts-title svg {
  color: #f97316;
}

.shortcuts-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.shortcut-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  border-radius: 8px;
  transition: background 0.2s ease;
}

.shortcut-item:hover {
  background: rgba(255, 255, 255, 0.03);
}

.shortcut-label {
  font-size: 13px;
  color: var(--text-secondary, #a1a1aa);
}

.shortcut-key {
  display: flex;
  gap: 4px;
}

.shortcut-key kbd {
  padding: 4px 10px;
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
  border-radius: 6px;
  font-family: monospace;
  font-size: 12px;
  font-weight: 600;
  min-width: 28px;
  text-align: center;
}

.shortcuts-footer {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.shortcuts-esc {
  font-size: 11px;
  color: var(--text-secondary, #a1a1aa);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
