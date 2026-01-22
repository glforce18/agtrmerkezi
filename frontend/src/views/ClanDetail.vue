<template>
  <div class="clan-detail-page min-h-screen">
    <!-- Loading -->
    <div v-if="loading" class="loading-overlay">
      <n-spin size="large" />
    </div>

    <!-- Not Found -->
    <div v-else-if="!clan" class="not-found">
      <Shield class="w-20 h-20 text-gray-600" />
      <h2 class="text-2xl font-bold mt-4">Klan Bulunamadı</h2>
      <p class="text-gray-400 mt-2">Bu klan mevcut değil veya silinmiş olabilir.</p>
      <router-link to="/clans">
        <n-button type="primary" class="mt-4">Klanlara Dön</n-button>
      </router-link>
    </div>

    <!-- Clan Content -->
    <template v-else>
      <!-- Hero Banner -->
      <section class="hero-banner" :style="bannerStyle">
        <div class="banner-overlay"></div>
        <div class="container-main relative z-10">
          <div class="hero-content">
            <!-- Clan Logo -->
            <div class="clan-logo-container">
              <img v-if="clan.logo_url" :src="clan.logo_url" :alt="clan.name" class="clan-logo" />
              <div v-else class="clan-logo-placeholder">
                <span>{{ clan.name?.charAt(0).toUpperCase() }}</span>
              </div>
            </div>

            <!-- Clan Info -->
            <div class="clan-info">
              <div class="clan-tag-badge">[{{ clan.tag }}]</div>
              <h1 class="clan-name">{{ clan.name }}</h1>
              <p v-if="clan.description" class="clan-description">{{ clan.description }}</p>

              <!-- Status & Stats -->
              <div class="clan-meta">
                <span v-if="clan.is_recruiting" class="status-badge recruiting">
                  <UserPlus class="w-4 h-4" /> Üye Alıyor
                </span>
                <span v-else class="status-badge closed">
                  <Lock class="w-4 h-4" /> Kapalı
                </span>

                <div class="meta-stats">
                  <span><Users class="w-4 h-4" /> {{ clan.member_count || 0 }} Üye</span>
                  <span><Trophy class="w-4 h-4" /> {{ clan.wins || 0 }} Galibiyet</span>
                  <span><Target class="w-4 h-4" /> #{{ clan.rank || '-' }}</span>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="hero-actions">
              <template v-if="isMember">
                <n-button v-if="isLeader" type="primary" @click="showSettings = true">
                  <template #icon><Settings class="w-5 h-5" /></template>
                  Ayarlar
                </n-button>
                <n-button type="error" ghost @click="handleLeaveClan">
                  <template #icon><LogOut class="w-5 h-5" /></template>
                  Ayrıl
                </n-button>
              </template>

              <template v-else-if="authStore.isAuthenticated && !clansStore.isInClan">
                <n-button v-if="clan.is_recruiting && !hasApplied" type="primary" @click="requireSteam(handleApply)">
                  <template #icon><UserPlus class="w-5 h-5" /></template>
                  Başvur
                </n-button>
                <n-button v-else-if="hasApplied" disabled>
                  <template #icon><Clock class="w-5 h-5" /></template>
                  Başvuru Bekliyor
                </n-button>
              </template>
            </div>
          </div>
        </div>
      </section>

      <!-- Content Tabs -->
      <section class="py-8">
        <div class="container-main">
          <n-tabs v-model:value="activeTab" type="line" animated>
            <!-- Members Tab -->
            <n-tab-pane name="members" tab="Üyeler">
              <div class="members-grid">
                <div
                  v-for="member in members"
                  :key="member.user_id"
                  class="member-card"
                  :class="{ 'leader': member.role === 'owner', 'officer': member.role === 'admin' }"
                >
                  <router-link :to="`/profile/${member.user_id}`" class="member-link">
                    <n-avatar :size="56" :src="member.avatar_url" round>
                      {{ member.username?.charAt(0).toUpperCase() }}
                    </n-avatar>
                    <div class="member-info">
                      <h4 class="member-name">{{ member.username }}</h4>
                      <span class="member-role" :class="member.role">
                        <Crown v-if="member.role === 'owner'" class="w-3 h-3" />
                        <Shield v-else-if="member.role === 'admin'" class="w-3 h-3" />
                        {{ getRoleLabel(member.role) }}
                      </span>
                    </div>
                  </router-link>

                  <!-- Member Actions (for officers) -->
                  <div v-if="canManageMembers && member.user_id !== authStore.user?.id" class="member-actions">
                    <n-dropdown :options="getMemberActions(member)" @select="(key) => handleMemberAction(key, member)">
                      <n-button size="small" quaternary>
                        <template #icon><MoreVertical class="w-4 h-4" /></template>
                      </n-button>
                    </n-dropdown>
                  </div>
                </div>
              </div>
            </n-tab-pane>

            <!-- Applications Tab (for officers) -->
            <n-tab-pane v-if="canManageMembers" name="applications" :tab="`Başvurular (${applications.length})`">
              <div v-if="applications.length === 0" class="empty-state">
                <UserPlus class="w-12 h-12" />
                <p>Bekleyen başvuru yok</p>
              </div>

              <div v-else class="applications-list">
                <div v-for="app in applications" :key="app.id" class="application-card">
                  <router-link :to="`/profile/${app.user_id}`" class="applicant-info">
                    <n-avatar :size="48" :src="app.avatar_url" round>
                      {{ app.username?.charAt(0).toUpperCase() }}
                    </n-avatar>
                    <div>
                      <h4>{{ app.username }}</h4>
                      <p class="text-sm text-gray-400">{{ formatDate(app.created_at) }}</p>
                    </div>
                  </router-link>

                  <p v-if="app.message" class="application-message">{{ app.message }}</p>

                  <div class="application-actions">
                    <n-button type="primary" size="small" @click="acceptApplication(app.id)">
                      <template #icon><Check class="w-4 h-4" /></template>
                      Kabul Et
                    </n-button>
                    <n-button type="error" size="small" ghost @click="rejectApplication(app.id)">
                      <template #icon><X class="w-4 h-4" /></template>
                      Reddet
                    </n-button>
                  </div>
                </div>
              </div>
            </n-tab-pane>

            <!-- Stats Tab -->
            <n-tab-pane name="stats" tab="İstatistikler">
              <div class="stats-grid">
                <div class="stat-card">
                  <Trophy class="w-8 h-8 text-yellow-500" />
                  <div class="stat-value">{{ clan.wins || 0 }}</div>
                  <div class="stat-label">Galibiyet</div>
                </div>
                <div class="stat-card">
                  <Target class="w-8 h-8 text-red-500" />
                  <div class="stat-value">{{ clan.losses || 0 }}</div>
                  <div class="stat-label">Mağlubiyet</div>
                </div>
                <div class="stat-card">
                  <TrendingUp class="w-8 h-8 text-green-500" />
                  <div class="stat-value">{{ clan.points || 0 }}</div>
                  <div class="stat-label">Puan</div>
                </div>
                <div class="stat-card">
                  <Users class="w-8 h-8 text-blue-500" />
                  <div class="stat-value">{{ clan.member_count || 0 }}</div>
                  <div class="stat-label">Üye</div>
                </div>
              </div>
            </n-tab-pane>
          </n-tabs>
        </div>
      </section>
    </template>

    <!-- Settings Modal -->
    <n-modal v-model:show="showSettings" preset="card" title="Klan Ayarları" style="max-width: 600px">
      <n-form :model="settingsForm">
        <n-form-item label="Klan Adı">
          <n-input v-model:value="settingsForm.name" />
        </n-form-item>
        <n-form-item label="Klan Etiketi">
          <n-input v-model:value="settingsForm.tag" :maxlength="5" />
        </n-form-item>
        <n-form-item label="Açıklama">
          <n-input v-model:value="settingsForm.description" type="textarea" :rows="3" />
        </n-form-item>
        <n-form-item label="Üye Alımı">
          <n-switch v-model:value="settingsForm.is_recruiting" />
        </n-form-item>

        <div class="flex justify-end gap-3 mt-4">
          <n-button @click="showSettings = false">İptal</n-button>
          <n-button type="primary" :loading="savingSettings" @click="saveSettings">Kaydet</n-button>
        </div>
      </n-form>
    </n-modal>

    <!-- Steam Required Modal -->
    <SteamRequiredModal
      :show="showSteamModal"
      @close="closeModal"
      @connect="connectSteam"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import SteamRequiredModal from '@/components/SteamRequiredModal.vue'
import {
  Shield, Users, Trophy, Target, Crown, UserPlus, Lock,
  Settings, LogOut, Clock, Check, X, MoreVertical, TrendingUp
} from 'lucide-vue-next'
import { useClansStore, ClanRole } from '@/stores/clans'
import { useAuthStore } from '@/stores/auth'
import { useRequireSteam } from '@/composables/useRequireSteam'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const clansStore = useClansStore()
const authStore = useAuthStore()
const { hasSteam, showSteamModal, requireSteam, connectSteam, closeModal } = useRequireSteam()

// State
const loading = ref(true)
const activeTab = ref('members')
const showSettings = ref(false)
const savingSettings = ref(false)

const clan = ref(null)
const members = ref([])
const applications = ref([])

const settingsForm = ref({
  name: '',
  tag: '',
  description: '',
  is_recruiting: true
})

// Computed
const bannerStyle = computed(() => ({
  background: clan.value?.banner_url
    ? `url(${clan.value.banner_url}) center/cover`
    : `linear-gradient(135deg, ${clan.value?.color || '#f97316'}20 0%, transparent 50%)`
}))

const isMember = computed(() => {
  return clansStore.myClan?.id === clan.value?.id
})

const isLeader = computed(() => {
  return isMember.value && clansStore.myRole === ClanRole.LEADER
})

const isOfficer = computed(() => {
  return isMember.value && (clansStore.myRole === ClanRole.LEADER || clansStore.myRole === ClanRole.OFFICER)
})

const canManageMembers = computed(() => isOfficer.value)

const hasApplied = computed(() => {
  return clan.value?.has_applied || false
})

// Methods
const fetchClanData = async () => {
  loading.value = true

  const clanId = route.params.id
  const clanData = await clansStore.fetchClan(clanId)

  if (clanData) {
    clan.value = clanData
    members.value = clanData.members || []

    settingsForm.value = {
      name: clanData.name,
      tag: clanData.tag,
      description: clanData.description || '',
      is_recruiting: clanData.is_recruiting
    }

    if (isOfficer.value) {
      await fetchApplications()
    }
  }

  loading.value = false
}

const fetchApplications = async () => {
  try {
    const response = await clansStore.fetchApplications()
    applications.value = response || []
  } catch (e) {
    console.error('Failed to fetch applications:', e)
  }
}

const getRoleLabel = (role) => {
  const labels = {
    owner: 'Lider',
    admin: 'Subay',
    member: 'Üye'
  }
  return labels[role] || role
}

const getMemberActions = (member) => {
  const actions = []

  if (member.role === 'member' && isLeader.value) {
    actions.push({ label: 'Subay Yap', key: 'promote' })
  }
  if (member.role === 'admin' && isLeader.value) {
    actions.push({ label: 'Üye Yap', key: 'demote' })
  }
  if (isLeader.value && member.role !== 'owner') {
    actions.push({ label: 'Liderliği Devret', key: 'transfer' })
  }
  if (isOfficer.value && member.role !== 'owner') {
    actions.push({ type: 'divider' })
    actions.push({ label: 'Klandan Çıkar', key: 'kick' })
  }

  return actions
}

const handleMemberAction = async (key, member) => {
  switch (key) {
    case 'promote':
      const promoteResult = await clansStore.promoteToOfficer(member.user_id)
      if (promoteResult.success) {
        message.success(promoteResult.message)
        member.role = 'admin'
      } else {
        message.error(promoteResult.message)
      }
      break

    case 'demote':
      const demoteResult = await clansStore.demoteToMember(member.user_id)
      if (demoteResult.success) {
        message.success(demoteResult.message)
        member.role = 'member'
      } else {
        message.error(demoteResult.message)
      }
      break

    case 'transfer':
      dialog.warning({
        title: 'Liderliği Devret',
        content: `Liderliği ${member.username} kullanıcısına devretmek istediğinize emin misiniz?`,
        positiveText: 'Evet, Devret',
        negativeText: 'İptal',
        onPositiveClick: async () => {
          const result = await clansStore.transferLeadership(member.user_id)
          if (result.success) {
            message.success(result.message)
            await fetchClanData()
          } else {
            message.error(result.message)
          }
        }
      })
      break

    case 'kick':
      dialog.error({
        title: 'Üyeyi Çıkar',
        content: `${member.username} kullanıcısını klandan çıkarmak istediğinize emin misiniz?`,
        positiveText: 'Evet, Çıkar',
        negativeText: 'İptal',
        onPositiveClick: async () => {
          const result = await clansStore.kickMember(member.user_id)
          if (result.success) {
            message.success(result.message)
            members.value = members.value.filter(m => m.user_id !== member.user_id)
          } else {
            message.error(result.message)
          }
        }
      })
      break
  }
}

const handleApply = async () => {
  const result = await clansStore.applyToClan(clan.value.id)
  if (result.success) {
    message.success(result.message)
    clan.value.has_applied = true
  } else {
    message.error(result.message)
  }
}

const handleLeaveClan = () => {
  dialog.warning({
    title: 'Klandan Ayrıl',
    content: 'Klandan ayrılmak istediğinize emin misiniz?',
    positiveText: 'Evet, Ayrıl',
    negativeText: 'İptal',
    onPositiveClick: async () => {
      const result = await clansStore.leaveClan()
      if (result.success) {
        message.success(result.message)
        router.push('/clans')
      } else {
        message.error(result.message)
      }
    }
  })
}

const acceptApplication = async (appId) => {
  const result = await clansStore.acceptApplication(appId)
  if (result.success) {
    message.success(result.message)
    applications.value = applications.value.filter(a => a.id !== appId)
    await fetchClanData()
  } else {
    message.error(result.message)
  }
}

const rejectApplication = async (appId) => {
  const result = await clansStore.rejectApplication(appId)
  if (result.success) {
    message.info(result.message)
    applications.value = applications.value.filter(a => a.id !== appId)
  } else {
    message.error(result.message)
  }
}

const saveSettings = async () => {
  savingSettings.value = true
  const result = await clansStore.updateClan(clan.value.id, settingsForm.value)

  if (result.success) {
    message.success(result.message)
    showSettings.value = false
    clan.value = { ...clan.value, ...settingsForm.value }
  } else {
    message.error(result.message)
  }
  savingSettings.value = false
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('tr-TR')
}

// Watch route changes
watch(() => route.params.id, () => {
  if (route.params.id) {
    fetchClanData()
  }
})

onMounted(() => {
  fetchClanData()
})
</script>

<style scoped>
.clan-detail-page {
  background: var(--bg-primary);
}

.loading-overlay,
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  color: var(--text-tertiary);
}

.container-main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* Hero Banner */
.hero-banner {
  position: relative;
  padding: 60px 0;
  min-height: 300px;
}

.banner-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent 0%, var(--bg-primary) 100%);
}

.hero-content {
  display: flex;
  align-items: flex-end;
  gap: 24px;
  flex-wrap: wrap;
}

.clan-logo-container {
  flex-shrink: 0;
}

.clan-logo,
.clan-logo-placeholder {
  width: 120px;
  height: 120px;
  border-radius: 24px;
  border: 4px solid var(--bg-primary);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.clan-logo {
  object-fit: cover;
}

.clan-logo-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f97316, #ea580c);
  font-size: 48px;
  font-weight: 800;
  color: white;
}

.clan-info {
  flex: 1;
  min-width: 250px;
}

.clan-tag-badge {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(249, 115, 22, 0.2);
  border-radius: 6px;
  font-family: monospace;
  font-weight: 700;
  color: #f97316;
  margin-bottom: 8px;
}

.clan-name {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0 0 8px;
}

.clan-description {
  color: var(--text-secondary);
  margin-bottom: 16px;
  max-width: 500px;
}

.clan-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
}

.status-badge.recruiting {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.status-badge.closed {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.meta-stats {
  display: flex;
  gap: 16px;
  color: var(--text-secondary);
  font-size: 14px;
}

.meta-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.hero-actions {
  display: flex;
  gap: 12px;
}

/* Members Grid */
.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.member-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  transition: all 0.2s;
}

.member-card:hover {
  border-color: var(--border-hover);
}

.member-card.leader {
  border-color: rgba(251, 191, 36, 0.3);
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.05) 0%, transparent 50%);
}

.member-card.officer {
  border-color: rgba(59, 130, 246, 0.3);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, transparent 50%);
}

.member-link {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: inherit;
}

.member-name {
  font-weight: 600;
  margin: 0 0 4px;
}

.member-role {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.member-role.owner {
  color: #fbbf24;
}

.member-role.admin {
  color: #3b82f6;
}

/* Applications */
.applications-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.application-card {
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.applicant-info {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: inherit;
  margin-bottom: 12px;
}

.application-message {
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.application-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 800;
  margin: 12px 0 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-tertiary);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-tertiary);
}

@media (max-width: 768px) {
  .hero-content {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .clan-name {
    font-size: 1.75rem;
  }

  .clan-meta {
    justify-content: center;
  }

  .hero-actions {
    width: 100%;
    justify-content: center;
  }
}
</style>
