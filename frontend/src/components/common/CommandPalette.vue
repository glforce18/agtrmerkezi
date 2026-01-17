<template>
  <Teleport to="body">
    <Transition name="command-palette">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-[9999] flex items-start justify-center pt-[10vh] px-4"
        @click.self="close"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="close"></div>

        <!-- Command Palette -->
        <div class="relative w-full max-w-2xl bg-base-300/95 backdrop-blur-xl border border-base-300/50 rounded-2xl shadow-2xl overflow-hidden">
          <!-- Search Input -->
          <div class="flex items-center gap-3 px-6 py-4 border-b border-base-300/50">
            <Search class="w-5 h-5 opacity-60" />
            <input
              ref="searchInput"
              v-model="query"
              type="text"
              placeholder="Hızlı aramak yaz veya bir komut seç..."
              class="flex-1 bg-transparent border-none outline-none text-lg placeholder-slate-500"
              @keydown="handleKeyDown"
            />
            <kbd class="kbd kbd-sm bg-base-200">ESC</kbd>
          </div>

          <!-- Results -->
          <div class="max-h-[60vh] overflow-y-auto custom-scrollbar">
            <!-- Category: Quick Actions -->
            <div v-if="filteredQuickActions.length > 0" class="p-2">
              <div class="px-4 py-2 text-xs font-semibold opacity-50 uppercase tracking-wider">
                Hızlı İşlemler
              </div>
              <div
                v-for="(action, index) in filteredQuickActions"
                :key="action.id"
                class="command-item flex items-center gap-4 px-4 py-3 rounded-xl cursor-pointer transition-all"
                :class="{ 'bg-primary/10': index === selectedIndex }"
                @click="executeAction(action)"
                @mouseenter="selectedIndex = index"
              >
                <div class="w-10 h-10 rounded-lg flex items-center justify-center bg-primary/20">
                  <component :is="action.icon" class="w-5 h-5 text-primary" />
                </div>
                <div class="flex-1">
                  <div class="font-medium">{{ action.title }}</div>
                  <div class="text-xs opacity-50">{{ action.description }}</div>
                </div>
                <div v-if="action.shortcut" class="flex gap-1">
                  <kbd v-for="key in action.shortcut" :key="key" class="kbd kbd-xs">{{ key }}</kbd>
                </div>
              </div>
            </div>

            <!-- Category: Navigation -->
            <div v-if="filteredPages.length > 0" class="p-2">
              <div class="px-4 py-2 text-xs font-semibold opacity-50 uppercase tracking-wider">
                Sayfalar
              </div>
              <div
                v-for="(page, index) in filteredPages"
                :key="page.path"
                class="command-item flex items-center gap-4 px-4 py-3 rounded-xl cursor-pointer transition-all"
                :class="{ 'bg-primary/10': index + filteredQuickActions.length === selectedIndex }"
                @click="navigate(page.path)"
                @mouseenter="selectedIndex = index + filteredQuickActions.length"
              >
                <div class="w-10 h-10 rounded-lg flex items-center justify-center bg-secondary/20">
                  <component :is="page.icon" class="w-5 h-5 text-secondary" />
                </div>
                <div class="flex-1">
                  <div class="font-medium">{{ page.title }}</div>
                  <div class="text-xs opacity-50">{{ page.path }}</div>
                </div>
              </div>
            </div>

            <!-- No Results -->
            <div v-if="filteredQuickActions.length === 0 && filteredPages.length === 0 && query" class="p-12 text-center">
              <SearchX class="w-16 h-16 mx-auto mb-4 opacity-40" />
              <p class="opacity-60 font-medium">Sonuç bulunamadı</p>
              <p class="text-sm opacity-50 mt-2">"{{ query }}" için hiçbir şey bulunamadı</p>
            </div>

            <!-- Default State -->
            <div v-if="!query" class="p-8">
              <div class="text-sm opacity-50 space-y-2">
                <p class="font-semibold">İpuçları:</p>
                <ul class="list-disc list-inside space-y-1 ml-2">
                  <li>Hızlı arama için yazmaya başlayın</li>
                  <li><kbd class="kbd kbd-xs">↑</kbd> <kbd class="kbd kbd-xs">↓</kbd> ile gezin</li>
                  <li><kbd class="kbd kbd-xs">Enter</kbd> ile seçin</li>
                  <li><kbd class="kbd kbd-xs">ESC</kbd> ile kapatın</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="flex items-center justify-between px-6 py-3 border-t border-base-300/50 bg-base-200/50 text-xs opacity-50">
            <div class="flex items-center gap-4">
              <span class="flex items-center gap-1">
                <kbd class="kbd kbd-xs">↑↓</kbd> Gezin
              </span>
              <span class="flex items-center gap-1">
                <kbd class="kbd kbd-xs">Enter</kbd> Seç
              </span>
            </div>
            <div class="flex items-center gap-1">
              <kbd class="kbd kbd-xs">ESC</kbd> Kapat
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search,
  SearchX,
  Home,
  Server,
  Settings,
  User,
  Trophy,
  MessageSquare,
  ShoppingBag,
  LayoutDashboard,
  Shield,
  Plus,
  RefreshCw,
  LogOut,
  Sun,
  Moon
} from 'lucide-vue-next'

const router = useRouter()
const isOpen = ref(false)
const query = ref('')
const selectedIndex = ref(0)
const searchInput = ref(null)

const quickActions = [
  {
    id: 'new-server',
    title: 'Yeni Sunucu Oluştur',
    description: 'Hızlıca yeni bir CS 1.6 sunucusu oluştur',
    icon: Plus,
    action: () => router.push('/dashboard?action=new-server'),
    shortcut: ['⌘', 'N']
  },
  {
    id: 'refresh',
    title: 'Sayfayı Yenile',
    description: 'Mevcut sayfayı yenile',
    icon: RefreshCw,
    action: () => window.location.reload(),
    shortcut: ['⌘', 'R']
  },
  {
    id: 'toggle-theme',
    title: 'Temayı Değiştir',
    description: 'Açık/Koyu tema arasında geçiş yap',
    icon: Sun,
    action: () => toggleTheme()
  },
  {
    id: 'logout',
    title: 'Çıkış Yap',
    description: 'Hesabından çıkış yap',
    icon: LogOut,
    action: () => {
      close()
      router.push('/login')
    }
  }
]

const pages = [
  { path: '/', title: 'Ana Sayfa', icon: Home },
  { path: '/dashboard', title: 'Dashboard', icon: LayoutDashboard },
  { path: '/servers', title: 'Sunucularım', icon: Server },
  { path: '/leaderboard', title: 'Lider Tablosu', icon: Trophy },
  { path: '/forum', title: 'Forum', icon: MessageSquare },
  { path: '/shop', title: 'Premium Paketler', icon: ShoppingBag },
  { path: '/profile', title: 'Profil', icon: User },
  { path: '/admin', title: 'Admin Panel', icon: Shield },
  { path: '/profile', title: 'Ayarlar', icon: Settings }
]

const filteredQuickActions = computed(() => {
  if (!query.value) return quickActions
  const q = query.value.toLowerCase()
  return quickActions.filter(action =>
    action.title.toLowerCase().includes(q) ||
    action.description.toLowerCase().includes(q)
  )
})

const filteredPages = computed(() => {
  if (!query.value) return pages.slice(0, 5)
  const q = query.value.toLowerCase()
  return pages.filter(page =>
    page.title.toLowerCase().includes(q) ||
    page.path.toLowerCase().includes(q)
  )
})

const totalResults = computed(() => {
  return filteredQuickActions.value.length + filteredPages.value.length
})

const open = () => {
  isOpen.value = true
  nextTick(() => {
    searchInput.value?.focus()
  })
}

const close = () => {
  isOpen.value = false
  query.value = ''
  selectedIndex.value = 0
}

const executeAction = (action) => {
  action.action()
  close()
}

const navigate = (path) => {
  router.push(path)
  close()
}

const toggleTheme = () => {
  const html = document.documentElement
  const isDark = html.classList.contains('dark')
  if (isDark) {
    html.setAttribute('data-theme', 'agtr_light')
    html.classList.remove('dark')
  } else {
    html.setAttribute('data-theme', 'agtr_dark')
    html.classList.add('dark')
  }
}

const handleKeyDown = (e) => {
  if (e.key === 'Escape') {
    close()
  } else if (e.key === 'ArrowDown') {
    e.preventDefault()
    selectedIndex.value = (selectedIndex.value + 1) % totalResults.value
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    selectedIndex.value = selectedIndex.value === 0
      ? totalResults.value - 1
      : selectedIndex.value - 1
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (selectedIndex.value < filteredQuickActions.value.length) {
      executeAction(filteredQuickActions.value[selectedIndex.value])
    } else {
      const pageIndex = selectedIndex.value - filteredQuickActions.value.length
      navigate(filteredPages.value[pageIndex].path)
    }
  }
}

watch(query, () => {
  selectedIndex.value = 0
})

onMounted(() => {
  window.addEventListener('open-command-palette', open)

  const handleKeyboard = (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault()
      open()
    }
  }

  window.addEventListener('keydown', handleKeyboard)

  onUnmounted(() => {
    window.removeEventListener('open-command-palette', open)
    window.removeEventListener('keydown', handleKeyboard)
  })
})

defineExpose({
  open,
  close
})
</script>

<style scoped>
.command-palette-enter-active,
.command-palette-leave-active {
  transition: opacity 0.2s ease;
}

.command-palette-enter-from,
.command-palette-leave-to {
  opacity: 0;
}

.command-palette-enter-active > div:last-child,
.command-palette-leave-active > div:last-child {
  transition: transform 0.3s ease, opacity 0.2s ease;
}

.command-palette-enter-from > div:last-child {
  transform: scale(0.95) translateY(-20px);
  opacity: 0;
}

.command-palette-leave-to > div:last-child {
  transform: scale(0.95) translateY(-20px);
  opacity: 0;
}

.command-item:hover {
  background-color: rgba(99, 102, 241, 0.05);
}

.custom-scrollbar::-webkit-scrollbar {
  @apply w-2;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background-color: rgba(15, 23, 42, 0.5);
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  @apply rounded-full;
  background-color: rgba(99, 102, 241, 0.3);
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(99, 102, 241, 0.5);
}

.kbd {
  @apply px-1.5 py-0.5 text-xs font-mono rounded bg-base-200 border border-base-300;
}
</style>
