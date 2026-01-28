<template>
  <aside class="space-y-4 sticky top-6">
    <!-- Categories with modern design -->
    <div class="rounded-xl border border-dark-border/50 bg-gradient-to-br from-dark-card/80 to-dark-elevated/80 backdrop-blur-sm overflow-hidden">
      <div class="p-4 bg-gradient-to-r from-primary/10 to-transparent border-b border-dark-border/30">
        <h3 class="text-sm font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
          <svg class="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
          </svg>
          Kategoriler
        </h3>
      </div>
      <nav class="p-2">
        <router-link
          to="/forum"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group"
          :class="!selectedCategory ? 'bg-primary/15 text-primary border border-primary/30 shadow-lg shadow-primary/10' : 'text-text-secondary hover:bg-dark-hover hover:text-text-primary'"
        >
          <div class="p-2 rounded-lg transition-colors" :class="!selectedCategory ? 'bg-primary/20' : 'bg-dark-elevated group-hover:bg-dark-hover'">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
            </svg>
          </div>
          <span class="font-semibold">Tüm Konular</span>
        </router-link>

        <router-link
          v-for="category in categories"
          :key="category.id"
          :to="`/forum/category/${category.id}`"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group mt-1"
          :class="selectedCategory === category.id ? 'bg-primary/15 text-primary border border-primary/30 shadow-lg shadow-primary/10' : 'text-text-secondary hover:bg-dark-hover hover:text-text-primary'"
        >
          <div class="flex-shrink-0 text-2xl">{{ getCategoryIcon(category.slug) }}</div>
          <div class="flex-1 min-w-0">
            <div class="font-semibold truncate text-sm">{{ category.name }}</div>
            <div class="text-xs opacity-60">{{ category.topic_count || 0 }} konu</div>
          </div>
        </router-link>
      </nav>
    </div>

    <!-- Quick Actions with gradient -->
    <div class="rounded-xl border border-dark-border/50 bg-gradient-to-br from-dark-card/80 to-dark-elevated/80 backdrop-blur-sm overflow-hidden">
      <div class="p-4 bg-gradient-to-r from-orange-500/10 to-transparent border-b border-dark-border/30">
        <h3 class="text-sm font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
          <svg class="w-4 h-4 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
          Hızlı İşlemler
        </h3>
      </div>
      <div class="p-4">
        <router-link
          v-if="isAuthenticated"
          to="/forum/topic/new"
          class="flex items-center justify-center gap-2 w-full px-4 py-3 bg-gradient-to-r from-primary to-orange-600 hover:from-primary/90 hover:to-orange-500 text-white font-semibold rounded-lg shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/40 transition-all duration-300 hover:scale-105"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Yeni Konu Aç
        </router-link>
        <router-link
          v-else
          to="/login"
          class="flex items-center justify-center gap-2 w-full px-4 py-3 bg-dark-elevated hover:bg-dark-hover text-text-primary font-semibold rounded-lg border border-dark-border hover:border-primary/50 transition-all duration-300"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/>
          </svg>
          Giriş Yap
        </router-link>
      </div>
    </div>

    <!-- Enhanced Filters -->
    <div class="rounded-xl border border-dark-border/50 bg-gradient-to-br from-dark-card/80 to-dark-elevated/80 backdrop-blur-sm overflow-hidden">
      <div class="p-4 bg-gradient-to-r from-green-500/10 to-transparent border-b border-dark-border/30">
        <h3 class="text-sm font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
          <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
          </svg>
          Filtrele
        </h3>
      </div>
      <div class="p-2">
        <button
          v-for="filter in filters"
          :key="filter.value"
          @click="$emit('filter-change', filter.value)"
          class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200"
          :class="selectedFilter === filter.value ? 'bg-primary/15 text-primary border border-primary/30 shadow-lg shadow-primary/10' : 'text-text-secondary hover:bg-dark-hover hover:text-text-primary'"
        >
          <span class="text-lg">{{ filter.icon }}</span>
          <span>{{ filter.label }}</span>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  categories: {
    type: Array,
    default: () => []
  },
  selectedCategory: {
    type: [Number, String],
    default: null
  },
  selectedFilter: {
    type: String,
    default: 'recent'
  }
})

defineEmits(['filter-change'])

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

const filters = [
  { value: 'recent', label: 'Son Konular', icon: '🕒' },
  { value: 'popular', label: 'Popüler', icon: '🔥' },
  { value: 'unanswered', label: 'Yanıtsız', icon: '💬' },
  { value: 'solved', label: 'Çözüldü', icon: '✅' }
]

const getCategoryIcon = (slug) => {
  const icons = {
    'announcements': '📢',
    'general': '💬',
    'help': '❓',
    'bugs': '🐛',
    'suggestions': '💡',
    'servers': '🖥️',
    'plugins': '🔌',
    'maps': '🗺️',
    'off-topic': '🎮'
  }
  return icons[slug] || '📁'
}
</script>

<style scoped>
.sidebar-link {
  @apply flex items-center gap-3 px-3 py-2.5 rounded-lg text-text-secondary hover:bg-dark-hover hover:text-text-primary transition-colors;
}

.sidebar-link.active {
  @apply bg-primary/10 text-primary;
}
</style>
