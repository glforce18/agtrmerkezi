<template>
  <div class="chat-manager">
    <!-- Chat Windows -->
    <div class="chat-windows">
      <ChatWindow
        v-for="conversation in openChats"
        :key="conversation.id"
        :conversation="conversation"
        @close="closeChat(conversation.id)"
      />
    </div>

    <!-- Chat Launcher -->
    <div class="chat-launcher" v-if="authStore.isAuthenticated">
      <n-badge :value="totalUnread" :max="99">
        <n-button
          circle
          size="large"
          type="primary"
          class="launcher-btn"
          @click="showInbox = !showInbox"
        >
          <template #icon>
            <MessageCircle class="w-6 h-6" />
          </template>
        </n-button>
      </n-badge>
    </div>

    <!-- Inbox Dropdown -->
    <Transition name="inbox">
      <div v-if="showInbox" class="chat-inbox">
        <div class="inbox-header">
          <h4>Mesajlar</h4>
          <n-button size="tiny" quaternary circle @click="showInbox = false">
            <template #icon><X class="w-4 h-4" /></template>
          </n-button>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="inbox-loading">
          <n-spin size="small" />
        </div>

        <!-- Empty State -->
        <div v-else-if="conversations.length === 0" class="inbox-empty">
          <MessageCircle class="w-10 h-10 text-gray-500" />
          <p>Henüz mesajın yok</p>
        </div>

        <!-- Conversation List -->
        <div v-else class="inbox-list">
          <div
            v-for="conversation in sortedConversations"
            :key="conversation.id"
            class="inbox-item"
            :class="{ unread: unreadCounts[conversation.id] > 0 }"
            @click="openChat(conversation)"
          >
            <div class="item-avatar">
              <n-avatar :size="40" :src="getParticipant(conversation)?.avatar" round>
                {{ getParticipant(conversation)?.username?.charAt(0).toUpperCase() }}
              </n-avatar>
              <span
                class="online-dot"
                :class="getParticipant(conversation)?.is_online ? 'online' : 'offline'"
              ></span>
            </div>
            <div class="item-info">
              <div class="item-header">
                <span class="item-name">{{ getParticipant(conversation)?.username }}</span>
                <span class="item-time">{{ formatTime(conversation.last_message?.created_at) }}</span>
              </div>
              <p class="item-preview">
                <span v-if="conversation.last_message?.sender?.id === authStore.user?.id">Sen: </span>
                {{ conversation.last_message?.content || 'Mesaj yok' }}
              </p>
            </div>
            <div v-if="unreadCounts[conversation.id]" class="unread-badge">
              {{ unreadCounts[conversation.id] > 9 ? '9+' : unreadCounts[conversation.id] }}
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { MessageCircle, X } from 'lucide-vue-next'
import { useMessagesStore } from '@/stores/messages'
import { useAuthStore } from '@/stores/auth'
import ChatWindow from './ChatWindow.vue'

const messagesStore = useMessagesStore()
const authStore = useAuthStore()

const {
  conversations,
  sortedConversations,
  loading,
  totalUnread,
  unreadCounts
} = storeToRefs(messagesStore)

const showInbox = ref(false)
const openChats = ref([]) // Array of open chat conversations

// Maximum number of chat windows
const MAX_OPEN_CHATS = 3

// Methods
const getParticipant = (conversation) => {
  return conversation?.participant ||
         conversation?.participants?.find(p => p.id !== authStore.user?.id) ||
         conversation?.user
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''

  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Şimdi'
  if (minutes < 60) return `${minutes}dk`
  if (hours < 24) return `${hours}s`
  if (days < 7) return `${days}g`

  return date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })
}

const openChat = async (conversation) => {
  // Check if already open
  const existingIndex = openChats.value.findIndex(c => c.id === conversation.id)
  if (existingIndex !== -1) {
    // Bring to front (move to end of array)
    const existing = openChats.value.splice(existingIndex, 1)[0]
    openChats.value.push(existing)
    showInbox.value = false
    return
  }

  // Limit open chats
  if (openChats.value.length >= MAX_OPEN_CHATS) {
    openChats.value.shift() // Remove oldest
  }

  // Open conversation in store and add to open chats
  await messagesStore.openConversation(conversation)
  openChats.value.push(conversation)
  showInbox.value = false
}

const closeChat = (conversationId) => {
  openChats.value = openChats.value.filter(c => c.id !== conversationId)
  if (messagesStore.activeConversation?.id === conversationId) {
    messagesStore.closeConversation()
  }
}

// Public method to open chat from outside (e.g., from friend list)
const openChatWithUser = async (userId) => {
  const conversation = await messagesStore.openConversation(userId)
  if (conversation) {
    // Check if already open
    const existingIndex = openChats.value.findIndex(c => c.id === conversation.id)
    if (existingIndex === -1) {
      if (openChats.value.length >= MAX_OPEN_CHATS) {
        openChats.value.shift()
      }
      openChats.value.push(conversation)
    }
  }
}

// Expose method for parent components
defineExpose({ openChatWithUser })

// Close inbox when clicking outside
const handleClickOutside = (event) => {
  const inbox = document.querySelector('.chat-inbox')
  const launcher = document.querySelector('.chat-launcher')
  if (inbox && launcher &&
      !inbox.contains(event.target) &&
      !launcher.contains(event.target)) {
    showInbox.value = false
  }
}

// Load conversations when authenticated
watch(() => authStore.isAuthenticated, async (isAuth) => {
  if (isAuth) {
    await messagesStore.init()
  } else {
    messagesStore.reset()
    openChats.value = []
  }
}, { immediate: true })

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.chat-manager {
  position: fixed;
  bottom: 0;
  right: 20px;
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.chat-windows {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.chat-launcher {
  margin-bottom: 20px;
}

.launcher-btn {
  width: 56px !important;
  height: 56px !important;
  box-shadow: 0 4px 20px rgba(249, 115, 22, 0.3);
}

.chat-inbox {
  position: absolute;
  bottom: 80px;
  right: 0;
  width: 340px;
  max-height: 480px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.inbox-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.inbox-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.inbox-loading,
.inbox-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 12px;
  color: var(--text-secondary);
}

.inbox-empty p {
  margin: 0;
}

.inbox-list {
  flex: 1;
  overflow-y: auto;
}

.inbox-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.inbox-item:hover {
  background: var(--bg-secondary);
}

.inbox-item.unread {
  background: rgba(249, 115, 22, 0.05);
}

.inbox-item.unread:hover {
  background: rgba(249, 115, 22, 0.1);
}

.item-avatar {
  position: relative;
  flex-shrink: 0;
}

.online-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid var(--bg-primary);
}

.online-dot.online {
  background: #22c55e;
}

.online-dot.offline {
  background: #6b7280;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.item-name {
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.inbox-item.unread .item-name {
  font-weight: 600;
}

.item-time {
  font-size: 11px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.item-preview {
  margin: 2px 0 0 0;
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.inbox-item.unread .item-preview {
  color: var(--text-primary);
  font-weight: 500;
}

.unread-badge {
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: #f97316;
  color: white;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Animations */
.inbox-enter-active,
.inbox-leave-active {
  transition: all 0.2s ease;
}

.inbox-enter-from,
.inbox-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .chat-manager {
    right: 16px;
  }

  .chat-windows {
    display: none; /* Hide chat windows on mobile, full screen instead */
  }

  .chat-inbox {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    max-height: 70vh;
    border-radius: 16px 16px 0 0;
  }

  .launcher-btn {
    width: 48px !important;
    height: 48px !important;
  }
}
</style>
