<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="isOpen" class="command-palette-overlay" @click="close">
        <Transition name="scale">
          <div v-if="isOpen" class="command-palette" @click.stop>
            <!-- Search Input -->
            <div class="command-input-wrapper">
              <svg class="search-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8" />
                <path d="M21 21l-4.35-4.35" />
              </svg>
              <input
                ref="inputRef"
                v-model="query"
                type="text"
                class="command-input"
                placeholder="Ara veya komut yaz..."
                @keydown="handleKeydown"
              />
              <kbd class="shortcut-hint">ESC</kbd>
            </div>

            <!-- Results -->
            <div class="command-results" v-if="filteredItems.length > 0">
              <div
                v-for="(group, groupName) in groupedResults"
                :key="groupName"
                class="command-group"
              >
                <div class="group-label">{{ groupName }}</div>
                <div
                  v-for="(item, index) in group"
                  :key="item.id"
                  class="command-item"
                  :class="{ active: activeIndex === getGlobalIndex(groupName, index) }"
                  @click="executeItem(item)"
                  @mouseenter="activeIndex = getGlobalIndex(groupName, index)"
                >
                  <component :is="item.icon" class="item-icon" v-if="item.icon" />
                  <span v-else class="item-emoji">{{ item.emoji || '📄' }}</span>
                  <div class="item-content">
                    <span class="item-title">{{ item.title }}</span>
                    <span class="item-description" v-if="item.description">{{ item.description }}</span>
                  </div>
                  <kbd v-if="item.shortcut" class="item-shortcut">{{ item.shortcut }}</kbd>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else-if="query" class="command-empty">
              <span>"{{ query }}" için sonuç bulunamadı</span>
            </div>

            <!-- Footer -->
            <div class="command-footer">
              <div class="footer-hint">
                <kbd>↑↓</kbd> gezin
                <kbd>↵</kbd> seç
                <kbd>ESC</kbd> kapat
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isOpen = ref(false)
const query = ref('')
const activeIndex = ref(0)
const inputRef = ref(null)

// Define all available commands and pages
const items = computed(() => {
  const baseItems = [
    // Pages
    { id: 'home', type: 'page', title: 'Ana Sayfa', emoji: '🏠', action: () => router.push('/'), keywords: ['home', 'ana'] },
    { id: 'servers', type: 'page', title: 'Sunucular', emoji: '🖥️', action: () => router.push('/servers'), keywords: ['server', 'sunucu'] },
    { id: 'forum', type: 'page', title: 'Forum', emoji: '💬', action: () => router.push('/forum'), keywords: ['forum', 'tartisma'] },
    { id: 'shop', type: 'page', title: 'Mağaza', emoji: '🛒', action: () => router.push('/shop'), keywords: ['shop', 'mağaza', 'satin'] },
    { id: 'leaderboard', type: 'page', title: 'Sıralama', emoji: '🏆', action: () => router.push('/leaderboard'), keywords: ['leaderboard', 'siralama', 'top'] },
    { id: 'support', type: 'page', title: 'Destek', emoji: '🆘', action: () => router.push('/support'), keywords: ['support', 'destek', 'yardim'] },
  ]

  // Auth-required pages
  if (authStore.isAuthenticated) {
    baseItems.push(
      { id: 'dashboard', type: 'page', title: 'Dashboard', emoji: '📊', action: () => router.push('/dashboard'), keywords: ['dashboard', 'panel'] },
      { id: 'wallet', type: 'page', title: 'Cüzdan', emoji: '💰', action: () => router.push('/wallet'), keywords: ['wallet', 'cüzdan', 'bakiye'] },
      { id: 'profile', type: 'page', title: 'Profilim', emoji: '👤', action: () => router.push('/profile'), keywords: ['profile', 'profil'] },
      { id: 'jackpot', type: 'page', title: 'Jackpot', emoji: '🎰', action: () => router.push('/jackpot'), keywords: ['jackpot', 'oyun'] },
    )

    // Actions
    baseItems.push(
      { id: 'logout', type: 'action', title: 'Çıkış Yap', emoji: '🚪', action: () => { authStore.logout(); router.push('/') }, keywords: ['logout', 'çıkış'] },
    )
  } else {
    baseItems.push(
      { id: 'login', type: 'page', title: 'Giriş Yap', emoji: '🔐', action: () => router.push('/login'), keywords: ['login', 'giriş'] },
      { id: 'register', type: 'page', title: 'Kayıt Ol', emoji: '📝', action: () => router.push('/register'), keywords: ['register', 'kayıt'] },
    )
  }

  // Admin pages
  if (authStore.isAdmin) {
    baseItems.push(
      { id: 'admin', type: 'admin', title: 'Admin Panel', emoji: '⚙️', action: () => router.push('/admin'), keywords: ['admin', 'yonetim'] },
      { id: 'admin-users', type: 'admin', title: 'Kullanıcı Yönetimi', emoji: '👥', action: () => router.push('/admin/users'), keywords: ['users', 'kullanıcı'] },
      { id: 'admin-servers', type: 'admin', title: 'Sunucu Yönetimi', emoji: '🖥️', action: () => router.push('/admin/servers'), keywords: ['server', 'sunucu'] },
      { id: 'admin-payments', type: 'admin', title: 'Ödeme Yönetimi', emoji: '💳', action: () => router.push('/admin/payments'), keywords: ['payment', 'ödeme'] },
    )
  }

  return baseItems
})

// Filter items based on query
const filteredItems = computed(() => {
  if (!query.value) return items.value

  const q = query.value.toLowerCase()
  return items.value.filter(item => {
    const titleMatch = item.title.toLowerCase().includes(q)
    const keywordMatch = item.keywords?.some(k => k.includes(q))
    return titleMatch || keywordMatch
  })
})

// Group results by type
const groupedResults = computed(() => {
  const groups = {}
  const typeLabels = {
    page: 'Sayfalar',
    action: 'Eylemler',
    admin: 'Admin',
    server: 'Sunucular'
  }

  for (const item of filteredItems.value) {
    const groupName = typeLabels[item.type] || 'Diğer'
    if (!groups[groupName]) groups[groupName] = []
    groups[groupName].push(item)
  }

  return groups
})

// Get global index for keyboard navigation
const getGlobalIndex = (groupName, localIndex) => {
  let globalIndex = 0
  for (const [name, group] of Object.entries(groupedResults.value)) {
    if (name === groupName) {
      return globalIndex + localIndex
    }
    globalIndex += group.length
  }
  return globalIndex
}

// Get item by global index
const getItemByIndex = (index) => {
  let currentIndex = 0
  for (const group of Object.values(groupedResults.value)) {
    for (const item of group) {
      if (currentIndex === index) return item
      currentIndex++
    }
  }
  return null
}

// Keyboard navigation
const handleKeydown = (e) => {
  const totalItems = filteredItems.value.length

  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault()
      activeIndex.value = (activeIndex.value + 1) % totalItems
      break
    case 'ArrowUp':
      e.preventDefault()
      activeIndex.value = (activeIndex.value - 1 + totalItems) % totalItems
      break
    case 'Enter':
      e.preventDefault()
      const item = getItemByIndex(activeIndex.value)
      if (item) executeItem(item)
      break
    case 'Escape':
      close()
      break
  }
}

// Execute selected item
const executeItem = (item) => {
  if (item.action) {
    item.action()
  }
  close()
}

// Open/Close
const open = () => {
  isOpen.value = true
  query.value = ''
  activeIndex.value = 0
  nextTick(() => inputRef.value?.focus())
}

const close = () => {
  isOpen.value = false
}

const toggle = () => {
  if (isOpen.value) close()
  else open()
}

// Global keyboard shortcut (Ctrl+K or Cmd+K)
const handleGlobalKeydown = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    toggle()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeydown)
})

// Reset active index when results change
watch(filteredItems, () => {
  activeIndex.value = 0
})

// Expose for external usage
defineExpose({ open, close, toggle })
</script>

<style scoped>
.command-palette-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 15vh;
}

.command-palette {
  width: 100%;
  max-width: 600px;
  background: var(--bg-primary, #0f0f1a);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

.command-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color, #2a2a4a);
}

.search-icon {
  color: var(--text-secondary);
  flex-shrink: 0;
}

.command-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 16px;
  color: var(--text-primary);
}

.command-input::placeholder {
  color: var(--text-secondary);
}

.shortcut-hint {
  font-size: 11px;
  padding: 4px 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  color: var(--text-secondary);
}

.command-results {
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
}

.command-group {
  margin-bottom: 8px;
}

.group-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-secondary);
  padding: 8px 12px 4px;
}

.command-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.1s;
}

.command-item:hover,
.command-item.active {
  background: var(--bg-secondary);
}

.item-icon,
.item-emoji {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-title {
  display: block;
  font-weight: 500;
  color: var(--text-primary);
}

.item-description {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-shortcut {
  font-size: 11px;
  padding: 4px 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  color: var(--text-secondary);
}

.command-empty {
  padding: 40px 20px;
  text-align: center;
  color: var(--text-secondary);
}

.command-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--border-color, #2a2a4a);
  background: var(--bg-secondary);
}

.footer-hint {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-secondary);
}

.footer-hint kbd {
  font-size: 10px;
  padding: 2px 6px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  margin-right: 4px;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
  transition: transform 0.2s, opacity 0.2s;
}

.scale-enter-from,
.scale-leave-to {
  transform: scale(0.95);
  opacity: 0;
}
</style>
