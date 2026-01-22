<template>
  <div class="friend-request" :class="type">
    <n-avatar :size="40" :src="user?.avatar" round>
      {{ user?.username?.charAt(0).toUpperCase() }}
    </n-avatar>

    <div class="request-info">
      <router-link :to="`/profile/${user?.id}`" class="request-name">
        {{ user?.username || 'Bilinmeyen Kullanıcı' }}
      </router-link>
      <span class="request-time">{{ formatTime(request.created_at) }}</span>
    </div>

    <div class="request-actions">
      <template v-if="type === 'received'">
        <n-button size="small" type="primary" @click="$emit('accept')" :loading="loading">
          <Check class="w-4 h-4 mr-1" />
          Kabul Et
        </n-button>
        <n-button size="small" @click="$emit('reject')">
          <X class="w-4 h-4" />
        </n-button>
      </template>
      <template v-else>
        <n-button size="small" @click="$emit('cancel')">
          İptal Et
        </n-button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Check, X } from 'lucide-vue-next'

const props = defineProps({
  request: {
    type: Object,
    required: true
  },
  type: {
    type: String,
    default: 'received' // 'received' or 'sent'
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['accept', 'reject', 'cancel'])

const user = computed(() => {
  if (props.type === 'received') {
    return props.request.from_user || props.request.user
  } else {
    return props.request.to_user || props.request.user
  }
})

const formatTime = (dateStr) => {
  if (!dateStr) return ''

  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Az önce'
  if (minutes < 60) return `${minutes} dk önce`
  if (hours < 24) return `${hours} saat önce`
  if (days < 7) return `${days} gün önce`

  return date.toLocaleDateString('tr-TR')
}
</script>

<style scoped>
.friend-request {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 10px;
  margin-bottom: 8px;
}

.friend-request.received {
  border-left: 3px solid #22c55e;
}

.friend-request.sent {
  border-left: 3px solid #3b82f6;
}

.request-info {
  flex: 1;
  min-width: 0;
}

.request-name {
  display: block;
  font-weight: 500;
  color: var(--text-primary);
  text-decoration: none;
}

.request-name:hover {
  color: #f97316;
}

.request-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.request-actions {
  display: flex;
  gap: 8px;
}
</style>
