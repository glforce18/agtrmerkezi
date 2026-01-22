<template>
  <div class="friends-list">
    <!-- Header -->
    <div class="friends-header">
      <h3 class="friends-title">
        <Users class="w-5 h-5" />
        <span>Arkadaşlar</span>
        <span class="friend-count">{{ friendsStore.friendCount }}</span>
      </h3>
      <div class="friends-actions">
        <n-badge :value="friendsStore.pendingCount" :max="9" v-if="friendsStore.hasPendingRequests">
          <n-button size="small" quaternary @click="activeTab = 'requests'">
            <template #icon><UserPlus class="w-4 h-4" /></template>
          </n-button>
        </n-badge>
        <n-button size="small" quaternary @click="showAddFriend = true">
          <template #icon><Search class="w-4 h-4" /></template>
        </n-button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="friends-tabs">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'online' }"
        @click="activeTab = 'online'"
      >
        <span class="online-dot"></span>
        Çevrimiçi ({{ friendsStore.onlineFriends.length }})
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'all' }"
        @click="activeTab = 'all'"
      >
        Tümü ({{ friendsStore.friendCount }})
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'requests' }"
        @click="activeTab = 'requests'"
      >
        İstekler
        <span v-if="friendsStore.pendingCount" class="badge">{{ friendsStore.pendingCount }}</span>
      </button>
    </div>

    <!-- Content -->
    <div class="friends-content">
      <!-- Loading -->
      <div v-if="friendsStore.loading" class="loading-state">
        <n-spin size="small" />
        <span>Yükleniyor...</span>
      </div>

      <!-- Online Friends -->
      <template v-else-if="activeTab === 'online'">
        <div v-if="friendsStore.onlineFriends.length === 0" class="empty-state">
          <UserX class="w-12 h-12 text-gray-500" />
          <p>Çevrimiçi arkadaş yok</p>
        </div>
        <div v-else class="friend-items">
          <FriendItem
            v-for="friend in friendsStore.onlineFriends"
            :key="friend.id"
            :friend="friend"
            @message="openChat(friend)"
            @remove="confirmRemove(friend)"
          />
        </div>
      </template>

      <!-- All Friends -->
      <template v-else-if="activeTab === 'all'">
        <div v-if="friendsStore.friends.length === 0" class="empty-state">
          <Users class="w-12 h-12 text-gray-500" />
          <p>Henüz arkadaşın yok</p>
          <n-button type="primary" size="small" @click="showAddFriend = true">
            Arkadaş Ekle
          </n-button>
        </div>
        <div v-else class="friend-items">
          <FriendItem
            v-for="friend in friendsStore.friends"
            :key="friend.id"
            :friend="friend"
            @message="openChat(friend)"
            @remove="confirmRemove(friend)"
          />
        </div>
      </template>

      <!-- Friend Requests -->
      <template v-else-if="activeTab === 'requests'">
        <div v-if="friendsStore.pendingRequests.length === 0 && friendsStore.sentRequests.length === 0" class="empty-state">
          <UserPlus class="w-12 h-12 text-gray-500" />
          <p>Bekleyen istek yok</p>
        </div>
        <div v-else class="request-items">
          <!-- Received Requests -->
          <div v-if="friendsStore.pendingRequests.length > 0" class="request-section">
            <h4 class="section-title">Gelen İstekler</h4>
            <FriendRequest
              v-for="request in friendsStore.pendingRequests"
              :key="request.id"
              :request="request"
              type="received"
              @accept="handleAccept(request)"
              @reject="handleReject(request)"
            />
          </div>
          <!-- Sent Requests -->
          <div v-if="friendsStore.sentRequests.length > 0" class="request-section">
            <h4 class="section-title">Gönderilen İstekler</h4>
            <FriendRequest
              v-for="request in friendsStore.sentRequests"
              :key="request.id || request.to_user_id"
              :request="request"
              type="sent"
              @cancel="handleCancel(request)"
            />
          </div>
        </div>
      </template>
    </div>

    <!-- Add Friend Modal -->
    <n-modal v-model:show="showAddFriend" preset="card" title="Arkadaş Ekle" style="max-width: 400px;">
      <div class="add-friend-form">
        <n-input
          v-model:value="searchUsername"
          placeholder="Kullanıcı adı ara..."
          clearable
          @keyup.enter="searchUsers"
        >
          <template #prefix>
            <Search class="w-4 h-4 text-gray-400" />
          </template>
        </n-input>

        <div v-if="searchLoading" class="search-loading">
          <n-spin size="small" />
        </div>

        <div v-else-if="searchResults.length > 0" class="search-results">
          <div
            v-for="user in searchResults"
            :key="user.id"
            class="search-result-item"
          >
            <n-avatar :size="36" :src="user.avatar" round>
              {{ user.username?.charAt(0).toUpperCase() }}
            </n-avatar>
            <div class="user-info">
              <span class="username">{{ user.username }}</span>
              <span class="user-status">{{ user.is_online ? 'Çevrimiçi' : 'Çevrimdışı' }}</span>
            </div>
            <n-button
              v-if="friendsStore.isFriend(user.id)"
              size="small"
              disabled
            >
              Arkadaş
            </n-button>
            <n-button
              v-else-if="friendsStore.isPending(user.id)"
              size="small"
              disabled
            >
              Bekliyor
            </n-button>
            <n-button
              v-else
              size="small"
              type="primary"
              @click="sendRequest(user)"
              :loading="sendingRequest === user.id"
            >
              <UserPlus class="w-4 h-4 mr-1" />
              Ekle
            </n-button>
          </div>
        </div>

        <div v-else-if="searchUsername && !searchLoading" class="no-results">
          Kullanıcı bulunamadı
        </div>
      </div>
    </n-modal>

    <!-- Remove Confirmation -->
    <n-modal v-model:show="showRemoveConfirm" preset="dialog" type="warning" title="Arkadaşı Kaldır">
      <template #default>
        <strong>{{ selectedFriend?.username }}</strong> arkadaşlıktan çıkarılacak. Emin misin?
      </template>
      <template #action>
        <n-button @click="showRemoveConfirm = false">İptal</n-button>
        <n-button type="error" @click="handleRemove" :loading="removing">Kaldır</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { Users, UserPlus, UserX, Search } from 'lucide-vue-next'
import { useFriendsStore } from '@/stores/friends'
import api from '@/services/api'
import FriendItem from './FriendItem.vue'
import FriendRequest from './FriendRequest.vue'

const emit = defineEmits(['open-chat'])

const message = useMessage()
const friendsStore = useFriendsStore()

const activeTab = ref('online')
const showAddFriend = ref(false)
const showRemoveConfirm = ref(false)
const selectedFriend = ref(null)
const removing = ref(false)

// Search
const searchUsername = ref('')
const searchResults = ref([])
const searchLoading = ref(false)
const sendingRequest = ref(null)

const searchUsers = async () => {
  if (!searchUsername.value || searchUsername.value.length < 2) return

  searchLoading.value = true
  try {
    const response = await api.get('/users/search', { q: searchUsername.value, limit: 10 })
    searchResults.value = response.users || response || []
  } catch (e) {
    console.error('Search failed:', e)
    searchResults.value = []
  } finally {
    searchLoading.value = false
  }
}

const sendRequest = async (user) => {
  sendingRequest.value = user.id
  const result = await friendsStore.sendFriendRequest(user.id)
  sendingRequest.value = null

  if (result.success) {
    message.success(result.message)
  } else {
    message.error(result.message)
  }
}

const handleAccept = async (request) => {
  const result = await friendsStore.acceptFriendRequest(request.id, request.from_user_id)
  if (result.success) {
    message.success(result.message)
  } else {
    message.error(result.message)
  }
}

const handleReject = async (request) => {
  const result = await friendsStore.rejectFriendRequest(request.id)
  if (result.success) {
    message.success(result.message)
  } else {
    message.error(result.message)
  }
}

const handleCancel = async (request) => {
  const result = await friendsStore.cancelFriendRequest(request.to_user_id)
  if (result.success) {
    message.success(result.message)
  } else {
    message.error(result.message)
  }
}

const confirmRemove = (friend) => {
  selectedFriend.value = friend
  showRemoveConfirm.value = true
}

const handleRemove = async () => {
  if (!selectedFriend.value) return

  removing.value = true
  const result = await friendsStore.removeFriend(selectedFriend.value.id)
  removing.value = false
  showRemoveConfirm.value = false

  if (result.success) {
    message.success(result.message)
  } else {
    message.error(result.message)
  }
}

const openChat = (friend) => {
  emit('open-chat', friend)
}

onMounted(() => {
  friendsStore.init()
})
</script>

<style scoped>
.friends-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-primary);
  border-radius: 12px;
  overflow: hidden;
}

.friends-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.friends-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.friend-count {
  font-size: 12px;
  padding: 2px 8px;
  background: var(--bg-tertiary);
  border-radius: 10px;
  color: var(--text-secondary);
}

.friends-actions {
  display: flex;
  gap: 4px;
}

.friends-tabs {
  display: flex;
  padding: 8px 16px;
  gap: 4px;
  border-bottom: 1px solid var(--border-color);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: transparent;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: var(--bg-secondary);
}

.tab-btn.active {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.online-dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
}

.badge {
  padding: 2px 6px;
  background: #ef4444;
  color: white;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

.friends-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px 20px;
  color: var(--text-secondary);
  text-align: center;
}

.friend-items,
.request-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.request-section {
  margin-bottom: 16px;
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  padding: 8px 12px;
  margin: 0;
}

/* Add Friend Modal */
.add-friend-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-loading {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 500;
  color: var(--text-primary);
}

.user-status {
  font-size: 12px;
  color: var(--text-secondary);
}

.no-results {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
}
</style>
