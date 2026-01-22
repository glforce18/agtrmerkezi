<template>
  <div class="clan-card" :class="[clan.status]">
    <!-- Banner/Logo -->
    <div class="clan-banner">
      <img v-if="clan.banner_url" :src="clan.banner_url" :alt="clan.name" class="banner-img" />
      <div v-else class="banner-placeholder">
        <Shield class="w-10 h-10" />
      </div>

      <!-- Clan Tag -->
      <div class="clan-tag">[{{ clan.tag }}]</div>

      <!-- Status Badge -->
      <div
        v-if="clan.status === 'recruiting'"
        class="status-badge recruiting"
      >
        <UserPlus class="w-3 h-3" />
        Üye Alıyor
      </div>
    </div>

    <!-- Logo -->
    <div class="clan-logo">
      <img v-if="clan.logo_url" :src="clan.logo_url" :alt="clan.name" />
      <div v-else class="logo-placeholder">
        <span>{{ clan.name.charAt(0).toUpperCase() }}</span>
      </div>
    </div>

    <!-- Content -->
    <div class="clan-content">
      <h3 class="clan-name">{{ clan.name }}</h3>

      <p v-if="clan.description" class="clan-description">
        {{ truncatedDescription }}
      </p>

      <!-- Stats -->
      <div class="clan-stats">
        <div class="stat">
          <Users class="w-4 h-4" />
          <span>{{ clan.member_count || 0 }}</span>
          <span class="stat-label">Üye</span>
        </div>
        <div class="stat">
          <Trophy class="w-4 h-4" />
          <span>{{ clan.wins || 0 }}</span>
          <span class="stat-label">Galibiyet</span>
        </div>
        <div class="stat">
          <Target class="w-4 h-4" />
          <span>{{ clan.rank || '-' }}</span>
          <span class="stat-label">Sıralama</span>
        </div>
      </div>

      <!-- Leader -->
      <div class="clan-leader">
        <n-avatar :size="24" :src="clan.leader?.avatar" round>
          {{ clan.leader?.username?.charAt(0).toUpperCase() }}
        </n-avatar>
        <span>{{ clan.leader?.username || 'Bilinmiyor' }}</span>
        <Crown class="w-3 h-3 text-yellow-500" />
      </div>
    </div>

    <!-- Footer -->
    <div class="clan-footer">
      <router-link :to="`/clans/${clan.id}`" class="view-btn">
        Detaylar
      </router-link>

      <n-button
        v-if="canApply"
        size="small"
        type="primary"
        @click.stop.prevent="handleApply"
        :loading="applying"
      >
        <template #icon><UserPlus class="w-4 h-4" /></template>
        Başvur
      </n-button>

      <n-button
        v-else-if="isMember"
        size="small"
        disabled
      >
        <template #icon><Check class="w-4 h-4" /></template>
        Üyesin
      </n-button>

      <n-button
        v-else-if="hasApplied"
        size="small"
        @click.stop.prevent="handleCancelApplication"
      >
        Bekliyor
      </n-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { Shield, Users, Trophy, Target, Crown, UserPlus, Check } from 'lucide-vue-next'
import { useClansStore, ClanStatus } from '@/stores/clans'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  clan: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['applied', 'cancelled'])

const message = useMessage()
const clansStore = useClansStore()
const authStore = useAuthStore()

const applying = ref(false)

// Computed
const truncatedDescription = computed(() => {
  if (!props.clan.description) return ''
  return props.clan.description.length > 80
    ? props.clan.description.substring(0, 80) + '...'
    : props.clan.description
})

const isMember = computed(() => {
  return clansStore.myClan?.id === props.clan.id
})

const hasApplied = computed(() => {
  return props.clan.has_applied
})

const canApply = computed(() => {
  return authStore.isAuthenticated &&
         !isMember.value &&
         !hasApplied.value &&
         props.clan.status === ClanStatus.RECRUITING &&
         !clansStore.isInClan
})

// Methods
const handleApply = async () => {
  applying.value = true
  const result = await clansStore.applyToClan(props.clan.id)
  applying.value = false

  if (result.success) {
    message.success(result.message)
    emit('applied', props.clan)
  } else {
    message.error(result.message)
  }
}

const handleCancelApplication = async () => {
  const result = await clansStore.cancelApplication(props.clan.id)

  if (result.success) {
    message.success(result.message)
    emit('cancelled', props.clan)
  } else {
    message.error(result.message)
  }
}
</script>

<style scoped>
.clan-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.clan-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

.clan-card.recruiting {
  border-color: rgba(34, 197, 94, 0.3);
}

.clan-banner {
  position: relative;
  height: 80px;
  overflow: hidden;
}

.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  color: var(--text-tertiary);
}

.clan-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 4px 10px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  color: #f97316;
  font-family: monospace;
}

.status-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.recruiting {
  background: rgba(34, 197, 94, 0.9);
  color: white;
}

.clan-logo {
  width: 64px;
  height: 64px;
  margin: -32px auto 0;
  position: relative;
  z-index: 1;
}

.clan-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 16px;
  border: 3px solid var(--bg-secondary);
}

.logo-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f97316, #fb923c);
  border-radius: 16px;
  border: 3px solid var(--bg-secondary);
  font-size: 28px;
  font-weight: 700;
  color: white;
}

.clan-content {
  padding: 12px 16px 16px;
  text-align: center;
}

.clan-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 6px;
}

.clan-description {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 16px;
  line-height: 1.4;
}

.clan-stats {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 16px;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat svg {
  color: var(--text-tertiary);
}

.stat span:first-of-type {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 11px;
  color: var(--text-tertiary);
}

.clan-leader {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.clan-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border-top: 1px solid var(--border-color);
}

.view-btn {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s;
}

.view-btn:hover {
  color: #f97316;
}
</style>
