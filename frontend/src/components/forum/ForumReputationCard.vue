<template>
  <n-card size="small" class="reputation-card" :loading="loading">
    <template #header>
      <div class="card-header">
        <n-avatar :src="user?.avatar" :size="40" round />
        <div class="user-info">
          <span class="username">{{ user?.username }}</span>
          <n-tag :type="levelColor" size="small">
            {{ reputation?.level_name }}
          </n-tag>
        </div>
      </div>
    </template>

    <div class="reputation-content" v-if="reputation">
      <!-- Level Progress -->
      <div class="level-progress">
        <div class="progress-label">
          <span>Seviye {{ reputation.level }}</span>
          <span>{{ reputation.points }} / {{ reputation.next_level_at }}</span>
        </div>
        <n-progress
          type="line"
          :percentage="reputation.progress_percent"
          :height="8"
          :border-radius="4"
          :fill-border-radius="4"
          indicator-placement="inside"
          :show-indicator="false"
        />
      </div>

      <!-- Stats Grid -->
      <n-grid :cols="3" :x-gap="8" :y-gap="8" class="stats-grid">
        <n-gi>
          <div class="stat-item">
            <div class="stat-value">{{ reputation.stats.topics_count }}</div>
            <div class="stat-label">Konu</div>
          </div>
        </n-gi>
        <n-gi>
          <div class="stat-item">
            <div class="stat-value">{{ reputation.stats.replies_count }}</div>
            <div class="stat-label">Yanit</div>
          </div>
        </n-gi>
        <n-gi>
          <div class="stat-item">
            <div class="stat-value">{{ reputation.stats.likes_received }}</div>
            <div class="stat-label">Begeni</div>
          </div>
        </n-gi>
        <n-gi>
          <div class="stat-item">
            <div class="stat-value">{{ reputation.stats.best_answers }}</div>
            <div class="stat-label">Cozum</div>
          </div>
        </n-gi>
        <n-gi>
          <div class="stat-item">
            <div class="stat-value">{{ reputation.stats.likes_given }}</div>
            <div class="stat-label">Verilen</div>
          </div>
        </n-gi>
        <n-gi>
          <div class="stat-item">
            <div class="stat-value">{{ reputation.weekly_activity }}</div>
            <div class="stat-label">Haftalik</div>
          </div>
        </n-gi>
      </n-grid>
    </div>

    <template #footer v-if="showViewProfile">
      <n-button text block @click="viewProfile">
        Profili Goruntule
      </n-button>
    </template>
  </n-card>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NAvatar, NTag, NProgress, NGrid, NGi, NButton } from 'naive-ui'
import { reputationApi } from '@/services/forumAdvanced.js'

const router = useRouter()

const props = defineProps({
  userId: {
    type: Number,
    default: null
  },
  user: {
    type: Object,
    default: null
  },
  showViewProfile: {
    type: Boolean,
    default: true
  }
})

// State
const reputation = ref(null)
const loading = ref(false)

// Computed
const levelColor = computed(() => {
  if (!reputation.value) return 'default'
  const level = reputation.value.level

  if (level >= 7) return 'error' // Legend
  if (level >= 5) return 'warning' // Master+
  if (level >= 3) return 'success' // Degerli+
  if (level >= 2) return 'info' // Aktif
  return 'default'
})

// Methods
const fetchReputation = async () => {
  if (!props.userId && !props.user?.id) return

  loading.value = true
  try {
    const id = props.userId || props.user?.id
    const { data } = await reputationApi.getUserReputation(id)
    if (data.success) {
      reputation.value = data.reputation
    }
  } catch (err) {
    // Silent fail
  } finally {
    loading.value = false
  }
}

const viewProfile = () => {
  const id = props.userId || props.user?.id
  if (id) {
    router.push(`/profile/${id}`)
  }
}

// Watch for user changes
watch(() => props.userId, fetchReputation)
watch(() => props.user?.id, fetchReputation)

// Lifecycle
onMounted(fetchReputation)
</script>

<style scoped>
.reputation-card {
  width: 100%;
  max-width: 300px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.username {
  font-weight: 600;
}

.reputation-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.level-progress {
  margin-bottom: 8px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--n-text-color-3);
  margin-bottom: 4px;
}

.stats-grid {
  margin-top: 8px;
}

.stat-item {
  text-align: center;
  padding: 8px;
  background: var(--n-color);
  border-radius: 6px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
}

.stat-label {
  font-size: 10px;
  color: var(--n-text-color-3);
  text-transform: uppercase;
}
</style>
