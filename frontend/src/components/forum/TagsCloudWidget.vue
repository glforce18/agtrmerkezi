<template>
  <div class="tags-cloud-widget">
    <div class="tags-cloud-title">
      <HashIcon class="w-4 h-4" />
      Popüler Etiketler
    </div>
    <div class="tags-cloud">
      <button
        v-for="tag in tags"
        :key="tag.name"
        :class="['tag-cloud-item', { active: activeTag === tag.name }]"
        @click="$emit('tag-click', tag.name)"
      >
        #{{ tag.name }}
        <span class="tag-count">{{ tag.count }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { HashIcon } from 'lucide-vue-next'

defineProps({
  tags: {
    type: Array,
    default: () => [
      { name: 'amxmodx', count: 42 },
      { name: 'plugin', count: 38 },
      { name: 'sunucu', count: 31 },
      { name: 'yardim', count: 28 },
      { name: 'cfg', count: 24 },
      { name: 'hlds', count: 19 },
      { name: 'metamod', count: 17 },
      { name: 'turnuva', count: 15 }
    ]
  },
  activeTag: {
    type: String,
    default: null
  }
})

defineEmits(['tag-click'])
</script>

<style scoped>
.tags-cloud-widget {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 10px;
}

.tags-cloud-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary, #a1a1aa);
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-cloud-item {
  padding: 4px 8px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 6px;
  font-size: 11px;
  color: #a78bfa;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag-cloud-item:hover {
  background: rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.4);
  transform: scale(1.05);
}

.tag-cloud-item.active {
  background: #8b5cf6;
  color: white;
  border-color: #8b5cf6;
}

.tag-count {
  margin-left: 4px;
  opacity: 0.7;
  font-size: 10px;
}
</style>
