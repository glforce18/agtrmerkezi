<template>
  <div class="live-chat">
    <div class="chat-header">
      <h3>💬 Canlı Sohbet</h3>
      <div class="chat-status">
        <span :class="['status-dot', isConnected ? 'connected' : 'disconnected']"></span>
        <span>{{ isConnected ? 'Bağlı' : 'Bağlantı Yok' }}</span>
      </div>
    </div>

    <div class="chat-room-selector">
      <button
        v-for="room in availableRooms"
        :key="room.id"
        :class="['room-btn', { active: currentRoom === room.id }]"
        @click="joinRoom(room.id)"
      >
        {{ room.name }}
      </button>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="no-messages">
        Henüz mesaj yok. İlk mesajı sen gönder!
      </div>

      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['message', message.type]"
      >
        <div v-if="message.type === 'system'" class="system-message">
          {{ message.message }}
        </div>

        <div v-else class="user-message">
          <div class="message-header">
            <span class="username">{{ message.user }}</span>
            <span class="timestamp">{{ formatTime(message.timestamp) }}</span>
          </div>
          <div class="message-content">
            {{ message.message }}
          </div>
        </div>
      </div>
    </div>

    <form class="chat-input" @submit.prevent="handleSend">
      <input
        v-model="inputMessage"
        type="text"
        placeholder="Mesajınızı yazın..."
        maxlength="500"
        :disabled="!isConnected"
      />
      <button type="submit" :disabled="!isConnected || !inputMessage.trim()">
        Gönder
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useChatWS } from '@/composables/useWebSocket'

const availableRooms = [
  { id: 'global', name: 'Genel' },
  { id: 'turkish', name: 'Türkçe' },
  { id: 'english', name: 'English' },
  { id: 'support', name: 'Destek' }
]

const { messages, currentRoom, isConnected, sendMessage, joinRoom } = useChatWS('global')

const inputMessage = ref('')
const messagesContainer = ref(null)

function handleSend() {
  if (inputMessage.value.trim() && isConnected.value) {
    sendMessage(inputMessage.value.trim())
    inputMessage.value = ''
  }
}

function formatTime(timestamp) {
  const date = new Date(timestamp * 1000)
  return date.toLocaleTimeString('tr-TR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Auto-scroll to bottom on new messages
watch(messages, async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}, { deep: true })
</script>

<style scoped>
.live-chat {
  display: flex;
  flex-direction: column;
  height: 600px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.chat-header h3 {
  margin: 0;
  font-size: 18px;
}

.chat-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--text-secondary);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.connected {
  background: var(--success-color, #10b981);
}

.status-dot.disconnected {
  background: var(--error-color, #ef4444);
}

.chat-room-selector {
  display: flex;
  gap: 8px;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  overflow-x: auto;
}

.room-btn {
  padding: 6px 16px;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.room-btn:hover {
  background: var(--bg-tertiary);
}

.room-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.no-messages {
  text-align: center;
  color: var(--text-secondary);
  padding: 2rem;
}

.message.system .system-message {
  text-align: center;
  font-size: 13px;
  color: var(--text-secondary);
  font-style: italic;
}

.user-message {
  background: var(--bg-tertiary);
  border-radius: 8px;
  padding: 8px 12px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.username {
  font-weight: 600;
  font-size: 14px;
  color: var(--primary-color);
}

.timestamp {
  font-size: 12px;
  color: var(--text-secondary);
}

.message-content {
  font-size: 14px;
  color: var(--text-primary);
  word-wrap: break-word;
}

.chat-input {
  display: flex;
  gap: 8px;
  padding: 1rem;
  border-top: 1px solid var(--border-color);
}

.chat-input input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
}

.chat-input input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.chat-input button {
  padding: 10px 20px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.chat-input button:hover:not(:disabled) {
  opacity: 0.9;
}

.chat-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
