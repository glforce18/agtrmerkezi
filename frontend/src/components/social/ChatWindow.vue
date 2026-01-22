<template>
  <div class="chat-window" :class="{ minimized: isMinimized }">
    <!-- Header -->
    <div class="chat-header" @click="toggleMinimize">
      <div class="chat-user">
        <div class="user-avatar">
          <n-avatar :size="32" :src="participant?.avatar" round>
            {{ participant?.username?.charAt(0).toUpperCase() }}
          </n-avatar>
          <span
            class="status-indicator"
            :class="participant?.is_online ? 'online' : 'offline'"
          ></span>
        </div>
        <div class="user-info">
          <span class="username">{{ participant?.username || 'Kullanıcı' }}</span>
          <span class="status-text" v-if="typingText">
            {{ typingText }}
          </span>
          <span class="status-text" v-else>
            {{ participant?.is_online ? 'Çevrimiçi' : 'Çevrimdışı' }}
          </span>
        </div>
      </div>
      <div class="header-actions" @click.stop>
        <n-button size="tiny" quaternary circle @click="toggleMinimize">
          <template #icon>
            <Minus v-if="!isMinimized" class="w-4 h-4" />
            <Maximize2 v-else class="w-4 h-4" />
          </template>
        </n-button>
        <n-button size="tiny" quaternary circle @click="$emit('close')">
          <template #icon><X class="w-4 h-4" /></template>
        </n-button>
      </div>
    </div>

    <!-- Messages -->
    <div v-show="!isMinimized" class="chat-messages" ref="messagesContainer">
      <!-- Loading -->
      <div v-if="loading" class="loading-messages">
        <n-spin size="small" />
      </div>

      <!-- Empty State -->
      <div v-else-if="messages.length === 0" class="empty-messages">
        <MessageCircle class="w-12 h-12 text-gray-500" />
        <p>Henüz mesaj yok</p>
        <span>İlk mesajı sen gönder!</span>
      </div>

      <!-- Message List -->
      <template v-else>
        <div
          v-for="(message, index) in messages"
          :key="message.id"
          class="message-wrapper"
          :class="{ 'is-own': isOwnMessage(message) }"
        >
          <!-- Date Separator -->
          <div
            v-if="shouldShowDateSeparator(message, messages[index - 1])"
            class="date-separator"
          >
            {{ formatDateSeparator(message.created_at) }}
          </div>

          <!-- Message Bubble -->
          <div class="message-bubble" :class="{ failed: message.status === 'failed' }">
            <p class="message-content">{{ message.content }}</p>
            <div class="message-meta">
              <span class="message-time">{{ formatTime(message.created_at) }}</span>
              <span v-if="isOwnMessage(message)" class="message-status">
                <Check v-if="message.status === 'sent' || !message.status" class="w-3 h-3" />
                <Clock v-else-if="message.status === 'sending'" class="w-3 h-3" />
                <AlertCircle v-else-if="message.status === 'failed'" class="w-3 h-3 text-red-500" />
              </span>
            </div>
          </div>

          <!-- Retry Button for Failed Messages -->
          <button
            v-if="message.status === 'failed'"
            class="retry-btn"
            @click="retryMessage(message)"
          >
            Tekrar Dene
          </button>
        </div>
      </template>
    </div>

    <!-- Input -->
    <div v-show="!isMinimized" class="chat-input">
      <div class="input-wrapper">
        <n-input
          v-model:value="newMessage"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 4 }"
          placeholder="Mesaj yaz..."
          @keydown.enter.exact.prevent="sendMessage"
          @input="handleTyping"
        />
        <div class="input-actions">
          <n-button
            size="small"
            type="primary"
            circle
            :disabled="!newMessage.trim()"
            :loading="sending"
            @click="sendMessage"
          >
            <template #icon><Send class="w-4 h-4" /></template>
          </n-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { X, Minus, Maximize2, Send, Check, Clock, AlertCircle, MessageCircle } from 'lucide-vue-next'
import { useMessagesStore } from '@/stores/messages'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  conversation: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

const messagesStore = useMessagesStore()
const authStore = useAuthStore()

const { activeMessages, sendingMessage, typingUsers } = storeToRefs(messagesStore)

const isMinimized = ref(false)
const newMessage = ref('')
const messagesContainer = ref(null)
const loading = ref(false)

// Computed
const participant = computed(() => {
  return props.conversation?.participant ||
         props.conversation?.participants?.find(p => p.id !== authStore.user?.id) ||
         props.conversation?.user
})

const messages = computed(() => activeMessages.value)

const sending = computed(() => sendingMessage.value)

const typingText = computed(() => {
  const conversationId = props.conversation?.id
  const typing = typingUsers.value[conversationId]
  if (typing && typing.length > 0) {
    return 'yazıyor...'
  }
  return null
})

// Methods
const isOwnMessage = (message) => {
  return message.sender?.id === authStore.user?.id ||
         message.sender?.id === 'me' ||
         message.is_own
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleTimeString('tr-TR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDateSeparator = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  if (date.toDateString() === today.toDateString()) {
    return 'Bugün'
  }
  if (date.toDateString() === yesterday.toDateString()) {
    return 'Dün'
  }
  return date.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'long',
    year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
  })
}

const shouldShowDateSeparator = (message, prevMessage) => {
  if (!prevMessage) return true
  const currentDate = new Date(message.created_at).toDateString()
  const prevDate = new Date(prevMessage.created_at).toDateString()
  return currentDate !== prevDate
}

const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || sending.value) return

  const content = newMessage.value
  newMessage.value = ''

  await messagesStore.sendMessage(content)
  scrollToBottom()
}

let typingTimeout = null
const handleTyping = () => {
  if (typingTimeout) clearTimeout(typingTimeout)
  messagesStore.sendTypingIndicator()
  typingTimeout = setTimeout(() => {
    // Typing stopped
  }, 2000)
}

const retryMessage = async (message) => {
  // Remove failed message and resend
  const conversationId = props.conversation?.id
  if (messagesStore.messages[conversationId]) {
    messagesStore.messages[conversationId] = messagesStore.messages[conversationId].filter(
      m => m.id !== message.id
    )
  }
  newMessage.value = message.content
  await sendMessage()
}

// Load messages when conversation changes
watch(() => props.conversation?.id, async (newId) => {
  if (newId) {
    loading.value = true
    await messagesStore.openConversation(props.conversation)
    loading.value = false
    scrollToBottom()
  }
}, { immediate: true })

// Scroll to bottom when new messages arrive
watch(() => messages.value.length, () => {
  scrollToBottom()
})

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  width: 320px;
  height: 420px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px 12px 0 0;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.chat-window.minimized {
  height: auto;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
}

.chat-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  position: relative;
  flex-shrink: 0;
}

.status-indicator {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid var(--bg-secondary);
}

.status-indicator.online {
  background: #22c55e;
}

.status-indicator.offline {
  background: #6b7280;
}

.user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.username {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-text {
  font-size: 11px;
  color: var(--text-tertiary);
}

.header-actions {
  display: flex;
  gap: 4px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.loading-messages,
.empty-messages {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 8px;
  color: var(--text-secondary);
  text-align: center;
}

.empty-messages p {
  margin: 0;
  font-weight: 500;
}

.empty-messages span {
  font-size: 12px;
  color: var(--text-tertiary);
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: 80%;
}

.message-wrapper.is-own {
  align-items: flex-end;
  align-self: flex-end;
}

.date-separator {
  align-self: center;
  font-size: 11px;
  color: var(--text-tertiary);
  padding: 4px 12px;
  background: var(--bg-secondary);
  border-radius: 10px;
  margin: 8px 0;
}

.message-bubble {
  padding: 10px 14px;
  border-radius: 16px;
  background: var(--bg-secondary);
  max-width: 100%;
}

.is-own .message-bubble {
  background: linear-gradient(135deg, #f97316, #fb923c);
  color: white;
}

.message-bubble.failed {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.message-content {
  margin: 0;
  font-size: 14px;
  line-height: 1.4;
  word-wrap: break-word;
}

.message-meta {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
  margin-top: 4px;
}

.message-time {
  font-size: 10px;
  opacity: 0.7;
}

.message-status {
  display: flex;
  opacity: 0.7;
}

.retry-btn {
  margin-top: 4px;
  padding: 4px 10px;
  background: transparent;
  border: 1px solid #ef4444;
  border-radius: 6px;
  color: #ef4444;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-btn:hover {
  background: rgba(239, 68, 68, 0.1);
}

.chat-input {
  padding: 12px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.input-wrapper :deep(.n-input) {
  flex: 1;
}

.input-wrapper :deep(.n-input__textarea-el) {
  resize: none;
}

.input-actions {
  flex-shrink: 0;
}
</style>
