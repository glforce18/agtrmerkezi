<template>
  <div class="min-h-screen user-profile-page">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-gradient"></div>
      <div class="hero-pattern"></div>
    </div>

    <div class="container-custom relative -mt-20 pb-6">
      <!-- Loading State -->
      <div v-if="loading" class="glass-card rounded-2xl p-8 text-center">
        <n-spin size="large" />
        <p class="mt-4 text-gray-400">Profil yukleniyor...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="glass-card rounded-2xl p-8 text-center">
        <XCircleIcon class="w-16 h-16 mx-auto text-red-500 mb-4" />
        <h2 class="text-xl font-bold mb-2">Kullanici Bulunamadi</h2>
        <p class="text-gray-400 mb-4">{{ error }}</p>
        <n-button type="primary" @click="$router.push('/forum')">
          Forum'a Don
        </n-button>
      </div>

      <!-- Profile Content -->
      <template v-else-if="profile">
        <!-- Profile Header Card -->
        <div class="glass-card-hero rounded-2xl p-6 mb-6">
          <div class="flex flex-col lg:flex-row items-start lg:items-center gap-6">
            <!-- Avatar -->
            <div class="relative">
              <div class="avatar-container">
                <n-avatar
                  round
                  :size="120"
                  :src="profile.avatar || '/default-avatar.png'"
                  class="avatar-main"
                />
                <div v-if="profile.is_online" class="status-dot status-dot--online"></div>
              </div>
              <!-- Level Badge -->
              <div class="level-badge-floating">
                <ZapIcon class="w-4 h-4" />
                <span>{{ profile.level || 1 }}</span>
              </div>
            </div>

            <!-- User Info -->
            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap items-center gap-3 mb-3">
                <h1 class="text-2xl md:text-3xl font-bold text-white">
                  {{ profile.username }}
                </h1>

                <!-- Verification Badge -->
                <div v-if="profile.verified" class="verification-badge">
                  <CheckCircleIcon class="w-4 h-4" />
                  <span>Dogrulanmis</span>
                </div>

                <!-- Role Badge -->
                <div class="role-badge" :class="`role-badge--${profile.role}`">
                  <CrownIcon class="w-3.5 h-3.5" />
                  <span>{{ getRoleLabel(profile.role) }}</span>
                </div>
              </div>

              <!-- Bio -->
              <p v-if="profile.bio" class="text-gray-400 mb-4">
                {{ profile.bio }}
              </p>

              <!-- User Stats Row -->
              <div class="stats-row">
                <div class="stat-card">
                  <div class="stat-icon stat-icon-orange">
                    <ServerIcon class="w-5 h-5" />
                  </div>
                  <div class="stat-content">
                    <span class="stat-value">{{ profile.servers_count || 0 }}</span>
                    <span class="stat-label">Sunucu</span>
                  </div>
                </div>

                <div class="stat-card">
                  <div class="stat-icon stat-icon-blue">
                    <MessageSquareIcon class="w-5 h-5" />
                  </div>
                  <div class="stat-content">
                    <span class="stat-value">{{ profile.forum_posts || 0 }}</span>
                    <span class="stat-label">Forum Gonderi</span>
                  </div>
                </div>

                <div class="stat-card">
                  <div class="stat-icon stat-icon-green">
                    <CalendarIcon class="w-5 h-5" />
                  </div>
                  <div class="stat-content">
                    <span class="stat-value">{{ formatMemberSince(profile.created_at) }}</span>
                    <span class="stat-label">Uyelik</span>
                  </div>
                </div>

                <div class="stat-card">
                  <div class="stat-icon stat-icon-purple">
                    <TrophyIcon class="w-5 h-5" />
                  </div>
                  <div class="stat-content">
                    <span class="stat-value">{{ profile.achievements_count || 0 }}</span>
                    <span class="stat-label">Basari</span>
                  </div>
                </div>
              </div>

              <!-- Steam Profile Section - All Formats -->
              <div v-if="profile.steam_id || profile.steam_ids?.steam64" class="steam-section mt-4">
                <div class="steam-header">
                  <div class="steam-icon-large">
                    <svg viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
                      <path d="M12 2C6.48 2 2 6.48 2 12c0 5.17 3.95 9.42 9 9.95v-2.02c-3.94-.49-7-3.86-7-7.93 0-4.42 3.58-8 8-8s8 3.58 8 8c0 .88-.14 1.73-.41 2.52l1.77.71c.41-1.01.64-2.1.64-3.23 0-5.52-4.48-10-10-10zm-1.5 11.5l-2.47-.99c.13 1.67 1.52 3 3.22 3 1.79 0 3.25-1.46 3.25-3.25s-1.46-3.25-3.25-3.25c-.67 0-1.29.2-1.81.55l2.56 1.03c.81.32 1.2 1.24.88 2.05-.32.8-1.24 1.19-2.05.87l-.33-.01z"/>
                    </svg>
                  </div>
                  <div>
                    <h4 class="text-white font-medium">Steam Hesabi</h4>
                    <a
                      :href="profile.steam_ids?.profile_url || getSteamProfileUrl(profile.steam_id)"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="steam-profile-link"
                    >
                      <ExternalLinkIcon class="w-3 h-3" />
                      Profili Görüntüle
                    </a>
                  </div>
                </div>

                <div class="steam-ids-grid">
                  <!-- Steam2 ID (STEAM_0:X:Y) - Oyunlarda kullanılan -->
                  <div v-if="profile.steam_ids?.steam2" class="steam-id-item">
                    <span class="steam-id-label">Steam ID (Oyun)</span>
                    <div class="steam-id-value-wrapper">
                      <code class="steam-id-value">{{ profile.steam_ids.steam2 }}</code>
                      <button @click="copyToClipboard(profile.steam_ids.steam2)" class="copy-btn" title="Kopyala">
                        <CopyIcon class="w-3 h-3" />
                      </button>
                    </div>
                  </div>

                  <!-- Steam64 ID -->
                  <div v-if="profile.steam_ids?.steam64" class="steam-id-item">
                    <span class="steam-id-label">Steam64 ID</span>
                    <div class="steam-id-value-wrapper">
                      <code class="steam-id-value">{{ profile.steam_ids.steam64 }}</code>
                      <button @click="copyToClipboard(profile.steam_ids.steam64)" class="copy-btn" title="Kopyala">
                        <CopyIcon class="w-3 h-3" />
                      </button>
                    </div>
                  </div>

                  <!-- Steam3 ID [U:1:X] -->
                  <div v-if="profile.steam_ids?.steam3" class="steam-id-item">
                    <span class="steam-id-label">Steam3 ID</span>
                    <div class="steam-id-value-wrapper">
                      <code class="steam-id-value">{{ profile.steam_ids.steam3 }}</code>
                      <button @click="copyToClipboard(profile.steam_ids.steam3)" class="copy-btn" title="Kopyala">
                        <CopyIcon class="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Forum Activity -->
        <div v-if="profile.recent_topics?.length" class="glass-card rounded-2xl p-6">
          <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
            <MessageSquareIcon class="w-5 h-5 text-orange-500" />
            Son Forum Aktivitesi
          </h3>
          <div class="space-y-3">
            <router-link
              v-for="topic in profile.recent_topics"
              :key="topic.id"
              :to="`/forum/topic/${topic.id}`"
              class="activity-item"
            >
              <div class="activity-content">
                <h4 class="activity-title">{{ topic.title }}</h4>
                <p class="activity-meta">
                  {{ formatDate(topic.created_at) }} - {{ topic.replies_count || 0 }} yanit
                </p>
              </div>
              <ChevronRightIcon class="w-5 h-5 text-gray-500" />
            </router-link>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  ZapIcon,
  CheckCircleIcon,
  CrownIcon,
  ServerIcon,
  MessageSquareIcon,
  CalendarIcon,
  TrophyIcon,
  ExternalLinkIcon,
  XCircleIcon,
  ChevronRightIcon,
  CopyIcon
} from 'lucide-vue-next'

const route = useRoute()

const loading = ref(true)
const error = ref(null)
const profile = ref(null)

// Fetch user profile by username
async function fetchProfile() {
  loading.value = true
  error.value = null

  try {
    const username = route.params.username
    const response = await fetch(`/api/user/profile/${encodeURIComponent(username)}`)

    if (!response.ok) {
      if (response.status === 404) {
        error.value = 'Bu kullanici bulunamadi.'
      } else {
        error.value = 'Profil yuklenirken bir hata olustu.'
      }
      return
    }

    profile.value = await response.json()
  } catch (err) {
    console.error('Profile fetch error:', err)
    error.value = 'Profil yuklenirken bir hata olustu.'
  } finally {
    loading.value = false
  }
}

// Role label
const getRoleLabel = (role) => {
  const roles = {
    user: 'Uye',
    moderator: 'Moderator',
    admin: 'Admin',
    superadmin: 'Super Admin',
    vip: 'VIP'
  }
  return roles[role] || 'Uye'
}

// Format member since
const formatMemberSince = (timestamp) => {
  if (!timestamp) return 'Yeni'
  const date = new Date(timestamp)
  const now = new Date()
  const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
  if (diffDays < 30) return `${diffDays} gun`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} ay`
  return `${Math.floor(diffDays / 365)} yil`
}

// Format date
const formatDate = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

// Steam profile URL
const getSteamProfileUrl = (steamId) => {
  if (!steamId) return '#'
  if (steamId.startsWith('STEAM_')) {
    const parts = steamId.replace('STEAM_', '').split(':')
    if (parts.length === 3) {
      const Y = parseInt(parts[1])
      const Z = parseInt(parts[2])
      const steamId64 = BigInt('76561197960265728') + BigInt(Z * 2) + BigInt(Y)
      return `https://steamcommunity.com/profiles/${steamId64}`
    }
  }
  if (/^\d{17}$/.test(steamId)) {
    return `https://steamcommunity.com/profiles/${steamId}`
  }
  return `https://steamcommunity.com/id/${steamId}`
}

// Copy to clipboard
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    window.$message?.success('Kopyalandi!')
  } catch (err) {
    // Fallback
    const textarea = document.createElement('textarea')
    textarea.value = text
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    window.$message?.success('Kopyalandi!')
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.user-profile-page {
  background: var(--bg-primary, #0b0f14);
  min-height: 100vh;
}

.hero-section {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.hero-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
}

.hero-pattern {
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.container-custom {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 16px;
}

.glass-card {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(11, 15, 20, 0.95) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.glass-card-hero {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(11, 15, 20, 0.98) 100%);
  border: 1px solid rgba(249, 115, 22, 0.2);
  backdrop-filter: blur(10px);
}

.avatar-container {
  position: relative;
}

.avatar-main {
  border: 3px solid rgba(249, 115, 22, 0.3);
}

.status-dot {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 3px solid rgba(15, 23, 42, 0.95);
}

.status-dot--online {
  background: #22c55e;
}

.level-badge-floating {
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
}

.verification-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 20px;
  color: #22c55e;
  font-size: 12px;
  font-weight: 500;
}

.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge--user {
  background: rgba(156, 163, 175, 0.15);
  border: 1px solid rgba(156, 163, 175, 0.3);
  color: #9ca3af;
}

.role-badge--vip {
  background: rgba(234, 179, 8, 0.15);
  border: 1px solid rgba(234, 179, 8, 0.3);
  color: #eab308;
}

.role-badge--moderator {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #3b82f6;
}

.role-badge--admin {
  background: rgba(139, 92, 246, 0.15);
  border: 1px solid rgba(139, 92, 246, 0.3);
  color: #8b5cf6;
}

.role-badge--superadmin {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.stats-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
}

.stat-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
}

.stat-icon-orange {
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
}

.stat-icon-blue {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.stat-icon-green {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.stat-icon-purple {
  background: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 16px;
  font-weight: 700;
  color: white;
}

.stat-label {
  font-size: 11px;
  color: #9ca3af;
}

/* Steam Section */
.steam-section {
  padding: 16px;
  background: linear-gradient(135deg, rgba(27, 40, 56, 0.6), rgba(23, 32, 42, 0.6));
  border: 1px solid rgba(102, 192, 244, 0.2);
  border-radius: 12px;
}

.steam-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(102, 192, 244, 0.1);
}

.steam-icon-large {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1b2838, #2a475e);
  border-radius: 12px;
  color: #66c0f4;
}

.steam-profile-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 12px;
  color: #66c0f4;
  background: rgba(102, 192, 244, 0.1);
  border: 1px solid rgba(102, 192, 244, 0.2);
  border-radius: 6px;
  text-decoration: none;
  transition: all 0.2s ease;
  width: fit-content;
  margin-top: 4px;
}

.steam-profile-link:hover {
  background: rgba(102, 192, 244, 0.2);
  border-color: rgba(102, 192, 244, 0.4);
  color: #9dd5fa;
}

.steam-ids-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.steam-id-item {
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(102, 192, 244, 0.1);
  border-radius: 8px;
}

.steam-id-label {
  display: block;
  font-size: 11px;
  color: #66c0f4;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.steam-id-value-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.steam-id-value {
  flex: 1;
  font-size: 13px;
  color: #e2e8f0;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  background: transparent;
  word-break: break-all;
}

.copy-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: rgba(102, 192, 244, 0.1);
  border: 1px solid rgba(102, 192, 244, 0.2);
  border-radius: 4px;
  color: #66c0f4;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.copy-btn:hover {
  background: rgba(102, 192, 244, 0.2);
  border-color: rgba(102, 192, 244, 0.4);
}

/* Activity Items */
.activity-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.activity-item:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(249, 115, 22, 0.3);
}

.activity-title {
  font-size: 14px;
  font-weight: 500;
  color: white;
  margin-bottom: 2px;
}

.activity-meta {
  font-size: 12px;
  color: #9ca3af;
}
</style>
