<template>
  <div class="friend-item" :class="{ online: friend.is_online }">
    <div class="friend-avatar">
      <n-avatar :size="40" :src="friend.avatar" round>
        {{ friend.username?.charAt(0).toUpperCase() }}
      </n-avatar>
      <span class="status-dot" :class="friend.is_online ? 'online' : 'offline'"></span>
    </div>

    <div class="friend-info">
      <router-link :to="`/profile/${friend.id}`" class="friend-name">
        {{ friend.username }}
      </router-link>
      <span class="friend-status">
        <template v-if="friend.is_online">
          <span class="status-text online">Çevrimiçi</span>
          <span v-if="friend.current_game" class="current-game">
            • {{ friend.current_game }}
          </span>
        </template>
        <template v-else>
          <span class="status-text offline">
            {{ formatLastSeen(friend.last_seen) }}
          </span>
        </template>
      </span>
    </div>

    <div class="friend-actions">
      <n-tooltip trigger="hover">
        <template #trigger>
          <n-button size="small" quaternary circle @click="$emit('message', friend)">
            <template #icon><MessageCircle class="w-4 h-4" /></template>
          </n-button>
        </template>
        Mesaj Gönder
      </n-tooltip>

      <n-dropdown :options="moreOptions" trigger="click" @select="handleAction">
        <n-button size="small" quaternary circle>
          <template #icon><MoreVertical class="w-4 h-4" /></template>
        </n-button>
      </n-dropdown>
    </div>
  </div>
</template>

<script setup>
import { h } from 'vue'
import { MessageCircle, MoreVertical, UserMinus, Ban, Eye } from 'lucide-vue-next'
import { NIcon } from 'naive-ui'

const props = defineProps({
  friend: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['message', 'remove', 'block', 'view-profile'])

const renderIcon = (icon) => () => h(NIcon, null, { default: () => h(icon) })

const moreOptions = [
  {
    label: 'Profili Gör',
    key: 'view',
    icon: renderIcon(Eye)
  },
  {
    type: 'divider'
  },
  {
    label: 'Arkadaşlıktan Çıkar',
    key: 'remove',
    icon: renderIcon(UserMinus)
  },
  {
    label: 'Engelle',
    key: 'block',
    icon: renderIcon(Ban)
  }
]

const handleAction = (key) => {
  switch (key) {
    case 'view':
      emit('view-profile', props.friend)
      break
    case 'remove':
      emit('remove', props.friend)
      break
    case 'block':
      emit('block', props.friend)
      break
  }
}

const formatLastSeen = (lastSeen) => {
  if (!lastSeen) return 'Çevrimdışı'

  const date = new Date(lastSeen)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Az önce çevrimiçiydi'
  if (minutes < 60) return `${minutes} dk önce`
  if (hours < 24) return `${hours} saat önce`
  if (days < 7) return `${days} gün önce`

  return date.toLocaleDateString('tr-TR')
}
</script>

<style scoped>
.friend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  transition: background 0.2s;
}

.friend-item:hover {
  background: var(--bg-secondary);
}

.friend-item.online {
  background: rgba(34, 197, 94, 0.05);
}

.friend-item.online:hover {
  background: rgba(34, 197, 94, 0.1);
}

.friend-avatar {
  position: relative;
  flex-shrink: 0;
}

.status-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid var(--bg-primary);
}

.status-dot.online {
  background: #22c55e;
}

.status-dot.offline {
  background: #6b7280;
}

.friend-info {
  flex: 1;
  min-width: 0;
}

.friend-name {
  display: block;
  font-weight: 500;
  color: var(--text-primary);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.friend-name:hover {
  color: #f97316;
}

.friend-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.status-text.online {
  color: #22c55e;
}

.status-text.offline {
  color: var(--text-tertiary);
}

.current-game {
  color: #3b82f6;
}

.friend-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.friend-item:hover .friend-actions {
  opacity: 1;
}
</style>
