<template>
  <div class="quick-categories-widget card">
    <div class="widget-header">
      <h3 class="widget-title">
        <span class="title-icon">📂</span>
        Kategoriler
      </h3>
    </div>

    <div class="category-list">
      <router-link
        v-for="category in displayCategories"
        :key="category.id"
        :to="`/forum/${category.slug}`"
        class="category-item"
      >
        <span class="category-icon">{{ getCategoryIcon(category) }}</span>
        <span class="category-name">{{ category.name }}</span>
        <span class="category-count">{{ category.topic_count || 0 }}</span>
      </router-link>
    </div>

    <div v-if="categories.length > maxDisplay" class="view-all">
      <router-link to="/forum" class="view-all-btn">
        Tüm Kategoriler →
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Props
const props = defineProps({
  categories: {
    type: Array,
    default: () => []
  },
  maxDisplay: {
    type: Number,
    default: 6
  }
})

// Computed
const displayCategories = computed(() => {
  return props.categories.slice(0, props.maxDisplay)
})

// Methods
const getCategoryIcon = (category) => {
  // Eger kategori iconu varsa kullan, yoksa varsayilan
  if (category.icon) {
    return category.icon
  }

  // Slug bazli ikonlar
  const iconMap = {
    'duyurular': '📢',
    'genel-sohbet': '💬',
    'cs-16': '🎮',
    'half-life': '🎯',
    'destek': '🛠️',
    'turnuvalar': '🏆',
    'rehberler': '📖',
    'tanitimlar': '📣',
    'oneriler': '💡',
    'hata-bildir': '🐛'
  }

  return iconMap[category.slug] || '📁'
}
</script>

<style scoped>
.quick-categories-widget {
  background: var(--bg-card, rgba(255, 255, 255, 0.05));
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.widget-header {
  margin-bottom: 10px;
}

.widget-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary, #ffffff);
}

.title-icon {
  font-size: 1.1rem;
}

/* Category List */
.category-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-primary, #ffffff);
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.category-item:hover {
  background: rgba(249, 115, 22, 0.1);
  transform: translateX(2px);
}

.category-item:hover .category-name {
  color: var(--primary, #f97316);
}

.category-icon {
  font-size: 1.2rem;
  width: 24px;
  text-align: center;
}

.category-name {
  flex: 1;
  font-size: 0.95rem;
  font-weight: 500;
  transition: color 0.2s ease;
}

.category-count {
  background: rgba(249, 115, 22, 0.15);
  color: var(--primary, #f97316);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 600;
}

/* View All */
.view-all {
  display: flex;
  justify-content: center;
  padding-top: 12px;
  margin-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.view-all-btn {
  background: transparent;
  border: none;
  color: var(--primary, #f97316);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.2s ease;
  text-decoration: none;
}

.view-all-btn:hover {
  background: rgba(249, 115, 22, 0.1);
}
</style>
