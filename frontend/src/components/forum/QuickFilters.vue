<template>
  <div class="quick-filters">
    <button
      v-for="filter in filters"
      :key="filter.id"
      :class="['quick-filter-chip', { active: activeFilter === filter.id, 'filter-active-badge': activeFilter === filter.id }]"
      @click="$emit('filter', filter.id)"
    >
      <component :is="filter.icon" class="filter-icon" />
      <span>{{ filter.label }}</span>
      <span v-if="filter.count !== undefined" class="filter-chip-count">{{ filter.count }}</span>
    </button>
  </div>
</template>

<script setup>
import { markRaw } from 'vue'
import {
  CheckCircleIcon,
  FlameIcon,
  MessageSquareIcon,
  ClockIcon,
  StarIcon
} from 'lucide-vue-next'

defineProps({
  activeFilter: {
    type: String,
    default: 'all'
  },
  counts: {
    type: Object,
    default: () => ({})
  }
})

defineEmits(['filter'])

const filters = [
  { id: 'all', label: 'Tümu', icon: markRaw(StarIcon) },
  { id: 'popular', label: 'Popüler', icon: markRaw(FlameIcon) },
  { id: 'solved', label: 'Cozulmus', icon: markRaw(CheckCircleIcon) },
  { id: 'unanswered', label: 'Cevasiz', icon: markRaw(MessageSquareIcon) },
  { id: 'recent', label: 'Yeni', icon: markRaw(ClockIcon) }
]
</script>

<style scoped>
.quick-filters {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.quick-filter-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-size: 11px;
  color: var(--text-secondary, #a1a1aa);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.quick-filter-chip:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.2);
}

.quick-filter-chip.active {
  background: rgba(249, 115, 22, 0.15);
  border-color: rgba(249, 115, 22, 0.4);
  color: #f97316;
}

.filter-icon {
  width: 12px;
  height: 12px;
}

.filter-chip-count {
  padding: 1px 5px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  font-size: 10px;
  font-weight: 600;
}

.quick-filter-chip.active .filter-chip-count {
  background: rgba(249, 115, 22, 0.3);
}

.filter-active-badge::after {
  content: '';
  position: absolute;
  top: -2px;
  right: -2px;
  width: 6px;
  height: 6px;
  background: #f97316;
  border-radius: 50%;
  animation: filter-badge-pulse 1.5s ease-in-out infinite;
}

@keyframes filter-badge-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.7; }
}

@media (max-width: 768px) {
  .quick-filters {
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 6px;
    -webkit-overflow-scrolling: touch;
  }

  .quick-filter-chip {
    flex-shrink: 0;
  }
}
</style>
