<template>
  <div class="empty-state" :class="[variant, { compact }]">
    <div class="empty-state-icon" :style="iconStyle">
      <slot name="icon">
        <component :is="icon" :size="compact ? 32 : 48" />
      </slot>
    </div>
    <h3 class="empty-state-title">{{ title }}</h3>
    <p class="empty-state-description">{{ description }}</p>
    <div v-if="$slots.action || actionText" class="empty-state-action">
      <slot name="action">
        <button v-if="actionText" class="btn-primary-cta empty-action-btn" @click="$emit('action')">
          <component v-if="actionIcon" :is="actionIcon" :size="20" />
          {{ actionText }}
        </button>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  FileQuestion,
  Users,
  Server,
  ShoppingBag,
  MessageSquare,
  Search,
  Inbox
} from 'lucide-vue-next'

const props = defineProps({
  title: {
    type: String,
    default: 'Veri bulunamadı'
  },
  description: {
    type: String,
    default: 'Henüz içerik eklenmemis.'
  },
  icon: {
    type: [Object, String],
    default: () => FileQuestion
  },
  iconColor: {
    type: String,
    default: null
  },
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'glass', 'minimal'].includes(v)
  },
  compact: {
    type: Boolean,
    default: false
  },
  actionText: {
    type: String,
    default: null
  },
  actionIcon: {
    type: Object,
    default: null
  }
})

defineEmits(['action'])

const iconStyle = computed(() => {
  if (props.iconColor) {
    return {
      color: props.iconColor,
      borderColor: `${props.iconColor}40`
    }
  }
  return {}
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  text-align: center;
}

.empty-state.compact {
  padding: 40px 20px;
}

.empty-state.glass {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--card-radius);
  backdrop-filter: blur(12px);
}

.empty-state.minimal {
  padding: 32px 16px;
}

.empty-state-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 50%;
  color: var(--text-tertiary);
  transition: all 0.3s ease;
}

.compact .empty-state-icon {
  width: 64px;
  height: 64px;
  padding: 16px;
  margin-bottom: 16px;
}

.empty-state:hover .empty-state-icon {
  transform: scale(1.05);
  border-color: rgba(249, 115, 22, 0.3);
}

.empty-state-title {
  font-family: 'Poppins', 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.compact .empty-state-title {
  font-size: 16px;
}

.empty-state-description {
  font-size: 15px;
  color: var(--text-secondary);
  max-width: 400px;
  margin: 0 0 24px 0;
  line-height: 1.6;
}

.compact .empty-state-description {
  font-size: 14px;
  margin-bottom: 16px;
}

.empty-state-action {
  margin-top: 8px;
}

.empty-action-btn {
  padding: 12px 28px;
  font-size: 15px;
}

.compact .empty-action-btn {
  padding: 10px 24px;
  font-size: 14px;
}
</style>
