<template>
  <div class="online-users-widget card">
    <div class="widget-header">
      <h3 class="widget-title">
        <span class="title-icon">👥</span>
        Çevrimiçi
        <span class="user-count">({{ total }})</span>
      </h3>
    </div>

    <div class="user-grid">
      <div
        v-for="user in displayUsers"
        :key="user.username"
        class="user-item"
        @click="goToProfile(user.username)"
      >
        <div class="user-avatar-wrapper">
          <img
            :src="user.avatar || '/static/images/default-avatar.png'"
            :alt="user.username"
            class="user-avatar"
            @error="handleAvatarError"
          />
          <div class="online-pulse"></div>
          <div class="user-level">{{ user.level || 1 }}</div>
        </div>
        <div class="user-tooltip">
          {{ user.username }}
        </div>
      </div>

      <!-- Daha Fazla Göstergesi -->
      <div v-if="remainingCount > 0" class="more-users" @click="showAllUsers">
        <span class="more-count">+{{ remainingCount }}</span>
        <span class="more-label">diger</span>
      </div>
    </div>

    <!-- Tümunu Gör Butonu -->
    <div v-if="total > maxDisplay" class="view-all">
      <button class="view-all-btn" @click="showAllUsers">
        Tümunu Gör →
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Props
const props = defineProps({
  users: {
    type: Array,
    default: () => []
  },
  total: {
    type: Number,
    default: 0
  },
  maxDisplay: {
    type: Number,
    default: 12
  }
})

// Computed
const displayUsers = computed(() => {
  return props.users.slice(0, props.maxDisplay)
})

const remainingCount = computed(() => {
  return Math.max(0, props.total - props.maxDisplay)
})

// Methods
const goToProfile = (username) => {
  router.push(`/profile/${username}`)
}

const showAllUsers = () => {
  // Online users modal veya sayfaya yonlendir
  router.push('/community-servers')
}

const handleAvatarError = (e) => {
  e.target.src = '/static/images/default-avatar.png'
}
</script>

<style scoped>
.online-users-widget {
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

.user-count {
  color: var(--primary, #f97316);
  font-size: 0.85rem;
}

/* User Grid */
.user-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(38px, 1fr));
  gap: 8px;
  margin-bottom: 8px;
}

.user-item {
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-item:hover {
  transform: translateY(-2px);
}

.user-item:hover .user-tooltip {
  opacity: 1;
  visibility: visible;
}

.user-avatar-wrapper {
  position: relative;
  width: 38px;
  height: 38px;
}

.user-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid #39ff14;
  object-fit: cover;
  transition: all 0.3s ease;
}

.user-item:hover .user-avatar {
  border-color: var(--primary, #f97316);
  transform: scale(1.1);
}

/* Online Pulse Animation */
.online-pulse {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  background: #39ff14;
  border: 2px solid var(--bg-card, #18181b);
  border-radius: 50%;
  animation: online-pulse 2s infinite;
}

@keyframes online-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(57, 255, 20, 0.7);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(57, 255, 20, 0);
  }
}

/* User Level Badge */
.user-level {
  position: absolute;
  top: -4px;
  left: -4px;
  background: var(--primary, #f97316);
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 700;
  border: 2px solid var(--bg-card, #18181b);
  min-width: 20px;
  text-align: center;
}

/* Tooltip */
.user-tooltip {
  position: absolute;
  bottom: -28px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  pointer-events: none;
  z-index: 10;
}

.user-tooltip::before {
  content: "";
  position: absolute;
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 4px solid rgba(0, 0, 0, 0.9);
}

/* More Users Indicator */
.more-users {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  background: rgba(249, 115, 22, 0.1);
  border: 2px dashed var(--primary, #f97316);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
}

.more-users:hover {
  background: rgba(249, 115, 22, 0.2);
  transform: translateY(-4px);
}

.more-count {
  font-size: 1rem;
  font-weight: 700;
  color: var(--primary, #f97316);
}

.more-label {
  font-size: 0.7rem;
  color: var(--text-secondary, #a1a1aa);
}

/* View All Button */
.view-all {
  display: flex;
  justify-content: center;
  padding-top: 8px;
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
}

.view-all-btn:hover {
  background: rgba(249, 115, 22, 0.1);
}

/* Responsive */
@media (max-width: 768px) {
  .user-grid {
    grid-template-columns: repeat(auto-fill, minmax(45px, 1fr));
    gap: 10px;
  }

  .user-avatar-wrapper {
    width: 45px;
    height: 45px;
  }
}
</style>
