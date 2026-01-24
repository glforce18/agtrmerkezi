<template>
  <n-card class="forum-leaderboard">
    <template #header>
      <div class="header-content">
        <n-icon><LeaderboardOutlined /></n-icon>
        <span>Liderlik Tablosu</span>
      </div>
    </template>

    <template #header-extra>
      <n-radio-group v-model:value="timeframe" size="small">
        <n-radio-button value="all">Tum Zamanlar</n-radio-button>
        <n-radio-button value="weekly">Haftalik</n-radio-button>
        <n-radio-button value="monthly">Aylik</n-radio-button>
      </n-radio-group>
    </template>

    <n-spin :show="loading">
      <div class="leaderboard-list">
        <div
          v-for="(user, index) in leaderboard"
          :key="user.user_id"
          class="leaderboard-item"
          :class="{ 'top-three': index < 3 }"
          @click="goToProfile(user.user_id)"
        >
          <!-- Rank -->
          <div class="rank" :class="`rank-${index + 1}`">
            <span v-if="index === 0" class="medal">1</span>
            <span v-else-if="index === 1" class="medal">2</span>
            <span v-else-if="index === 2" class="medal">3</span>
            <span v-else>{{ index + 1 }}</span>
          </div>

          <!-- User Info -->
          <div class="user-info">
            <n-avatar :src="user.avatar" size="small" round />
            <div class="user-details">
              <span class="username">{{ user.username }}</span>
              <n-tag :type="getLevelColor(user.level)" size="tiny">
                {{ user.level_name }}
              </n-tag>
            </div>
          </div>

          <!-- Points -->
          <div class="points">
            <span class="points-value">{{ formatNumber(user.points) }}</span>
            <span class="points-label">puan</span>
          </div>
        </div>

        <n-empty v-if="leaderboard.length === 0 && !loading" description="Veri bulunamadi" />
      </div>
    </n-spin>
  </n-card>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NRadioGroup, NRadioButton, NSpin, NAvatar, NTag, NIcon, NEmpty } from 'naive-ui'
import { TrophyIcon } from 'lucide-vue-next'
import { reputationApi } from '@/services/forumAdvanced.js'

const LeaderboardOutlined = TrophyIcon

const router = useRouter()

const props = defineProps({
  limit: {
    type: Number,
    default: 10
  }
})

// State
const leaderboard = ref([])
const loading = ref(false)
const timeframe = ref('all')

// Methods
const fetchLeaderboard = async () => {
  loading.value = true
  try {
    const { data } = await reputationApi.getLeaderboard(timeframe.value, props.limit)
    if (data.success) {
      leaderboard.value = data.leaderboard
    }
  } catch (err) {
    leaderboard.value = []
  } finally {
    loading.value = false
  }
}

const goToProfile = (userId) => {
  router.push(`/profile/${userId}`)
}

const getLevelColor = (level) => {
  if (level >= 7) return 'error'
  if (level >= 5) return 'warning'
  if (level >= 3) return 'success'
  if (level >= 2) return 'info'
  return 'default'
}

const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

// Watch timeframe changes
watch(timeframe, fetchLeaderboard)

// Lifecycle
onMounted(fetchLeaderboard)
</script>

<style scoped>
.forum-leaderboard {
  width: 100%;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.leaderboard-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 200px;
}

.leaderboard-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.leaderboard-item:hover {
  border-color: var(--n-primary-color);
  transform: translateX(4px);
}

.leaderboard-item.top-three {
  border-width: 2px;
}

.leaderboard-item.top-three:nth-child(1) {
  border-color: #FFD700;
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), transparent);
}

.leaderboard-item.top-three:nth-child(2) {
  border-color: #C0C0C0;
  background: linear-gradient(135deg, rgba(192, 192, 192, 0.1), transparent);
}

.leaderboard-item.top-three:nth-child(3) {
  border-color: #CD7F32;
  background: linear-gradient(135deg, rgba(205, 127, 50, 0.1), transparent);
}

.rank {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  border-radius: 50%;
  background: var(--n-color-modal);
}

.rank-1 {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: white;
}

.rank-2 {
  background: linear-gradient(135deg, #C0C0C0, #A0A0A0);
  color: white;
}

.rank-3 {
  background: linear-gradient(135deg, #CD7F32, #8B4513);
  color: white;
}

.medal {
  font-size: 14px;
}

.user-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.username {
  font-weight: 500;
}

.points {
  text-align: right;
}

.points-value {
  font-size: 18px;
  font-weight: bold;
  color: var(--n-primary-color);
}

.points-label {
  display: block;
  font-size: 10px;
  color: var(--n-text-color-3);
  text-transform: uppercase;
}
</style>
