<template>
  <aside class="space-y-6">
    <!-- Categories -->
    <div class="card p-4">
      <h3 class="text-sm font-semibold text-text-primary uppercase tracking-wide mb-4">Kategoriler</h3>
      <nav class="space-y-1">
        <router-link
          to="/forum"
          class="sidebar-link"
          :class="{ 'active': !selectedCategory }"
        >
          <span class="text-xl">🏠</span>
          <span>Tüm Konular</span>
        </router-link>

        <router-link
          v-for="category in categories"
          :key="category.id"
          :to="`/forum/category/${category.id}`"
          class="sidebar-link"
          :class="{ 'active': selectedCategory === category.id }"
        >
          <span class="text-xl">{{ getCategoryIcon(category.slug) }}</span>
          <div class="flex-1 min-w-0">
            <div class="font-medium truncate">{{ category.name }}</div>
            <div class="text-xs text-text-muted">{{ category.topic_count || 0 }} konu</div>
          </div>
        </router-link>
      </nav>
    </div>

    <!-- Quick Actions -->
    <div class="card p-4">
      <h3 class="text-sm font-semibold text-text-primary uppercase tracking-wide mb-4">Hızlı İşlemler</h3>
      <div class="space-y-2">
        <router-link
          v-if="isAuthenticated"
          to="/forum/topic/new"
          class="btn btn-primary w-full text-sm"
        >
          + Yeni Konu Aç
        </router-link>
        <router-link
          v-else
          to="/auth/login"
          class="btn btn-secondary w-full text-sm"
        >
          Giriş Yap
        </router-link>
      </div>
    </div>

    <!-- Filters (Optional) -->
    <div class="card p-4">
      <h3 class="text-sm font-semibold text-text-primary uppercase tracking-wide mb-4">Filtrele</h3>
      <div class="space-y-2">
        <button
          v-for="filter in filters"
          :key="filter.value"
          @click="$emit('filter-change', filter.value)"
          class="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors"
          :class="selectedFilter === filter.value ? 'bg-primary/10 text-primary' : 'text-text-secondary hover:bg-dark-hover'"
        >
          <span class="mr-2">{{ filter.icon }}</span>
          {{ filter.label }}
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
