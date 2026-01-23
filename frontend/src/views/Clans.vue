<template>
  <div class="clans-page min-h-screen">
    <!-- Maintenance Check -->
    <MaintenanceOverlay feature="clans" />

    <!-- Hero Section -->
    <section class="hero-section py-12 relative overflow-hidden">
      <div class="hero-bg"></div>
      <div class="container-main relative z-10">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div>
            <h1 class="text-3xl md:text-4xl font-bold mb-2 flex items-center gap-3">
              <Shield class="w-10 h-10 text-orange-500" />
              Klanlar
            </h1>
            <p class="text-gray-400">Takımını kur veya bir klana katıl!</p>
          </div>

          <div class="flex gap-3">
            <n-button
              v-if="authStore.isAuthenticated && !clansStore.isInClan"
              type="primary"
              size="large"
              @click="requireSteam(() => showCreateModal = true)"
            >
              <template #icon><Plus class="w-5 h-5" /></template>
              Klan Oluştur
            </n-button>
            <n-button
              v-if="clansStore.myClan"
              size="large"
              @click="goToMyClan"
            >
              <template #icon><Users class="w-5 h-5" /></template>
              Klanım
            </n-button>
          </div>
        </div>
      </div>
    </section>

    <!-- Search & Filters -->
    <section class="py-6 border-b border-gray-800">
      <div class="container-main">
        <div class="flex flex-col md:flex-row gap-4">
          <div class="flex-1">
            <n-input
              v-model:value="searchQuery"
              placeholder="Klan ara..."
              size="large"
              clearable
              :loading="isSearching"
              @input="debouncedSearch"
            >
              <template #prefix>
                <Search class="w-5 h-5 text-gray-400" />
              </template>
            </n-input>
          </div>

          <div class="flex gap-3">
            <n-select
              v-model:value="filterStatus"
              :options="statusOptions"
              placeholder="Durum"
              style="width: 160px"
              clearable
            />
            <n-select
              v-model:value="sortBy"
              :options="sortOptions"
              placeholder="Sıralama"
              style="width: 160px"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- My Clan Section (if member) -->
    <section v-if="clansStore.myClan" class="py-8 bg-gradient-to-r from-orange-500/5 to-transparent">
      <div class="container-main">
        <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
          <Crown class="w-6 h-6 text-yellow-500" />
          Klanım
        </h2>

        <div class="my-clan-card">
          <div class="flex items-center gap-4">
            <div class="clan-logo-large">
              <img v-if="clansStore.myClan.logo_url" :src="clansStore.myClan.logo_url" alt="Klan Logo" />
              <Shield v-else class="w-12 h-12 text-orange-500" />
            </div>

            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <span class="clan-tag">[{{ clansStore.myClan.tag }}]</span>
                <h3 class="text-xl font-bold">{{ clansStore.myClan.name }}</h3>
              </div>
              <p class="text-gray-400 text-sm">{{ clansStore.myClan.description || 'Açıklama yok' }}</p>
            </div>

            <div class="clan-stats-row hidden md:flex">
              <div class="stat-item">
                <Users class="w-5 h-5" />
                <span>{{ clansStore.myClan.member_count }}</span>
              </div>
              <div class="stat-item">
                <Trophy class="w-5 h-5 text-yellow-500" />
                <span>{{ clansStore.myClan.wins || 0 }}</span>
              </div>
              <div class="stat-item">
                <Target class="w-5 h-5 text-blue-500" />
                <span>#{{ clansStore.myClan.rank || '-' }}</span>
              </div>
            </div>

            <n-button type="primary" @click="goToMyClan">
              Yönet
              <template #icon><ArrowRight class="w-4 h-4" /></template>
            </n-button>
          </div>
        </div>
      </div>
    </section>

    <!-- Pending Applications -->
    <section v-if="clansStore.myApplications.length > 0" class="py-6">
      <div class="container-main">
        <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
          <Clock class="w-5 h-5 text-yellow-500" />
          Bekleyen Başvurularım
        </h2>

        <div class="applications-list">
          <div
            v-for="app in clansStore.myApplications"
            :key="app.id"
            class="application-item"
          >
            <div class="flex items-center gap-3">
              <div class="app-clan-logo">
                <Shield class="w-6 h-6" />
              </div>
              <div>
                <h4 class="font-medium">{{ app.clan_name }}</h4>
                <p class="text-sm text-gray-400">{{ formatDate(app.created_at) }}</p>
              </div>
            </div>
            <n-button size="small" quaternary @click="cancelApplication(app.clan_id)">
              İptal
            </n-button>
          </div>
        </div>
      </div>
    </section>

    <!-- Clans List -->
    <section class="py-8">
      <div class="container-main">
        <!-- Loading -->
        <div v-if="clansStore.loading" class="loading-state">
          <n-spin size="large" />
          <p>Klanlar yükleniyor...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredClans.length === 0" class="empty-state">
          <Shield class="w-16 h-16 text-gray-600" />
          <h3 class="text-xl font-semibold mt-4">Klan Bulunamadı</h3>
          <p class="text-gray-400 mt-2">Arama kriterlerinize uygun klan yok.</p>
          <n-button v-if="authStore.isAuthenticated" type="primary" class="mt-4" @click="requireSteam(() => showCreateModal = true)">
            <template #icon><Plus class="w-5 h-5" /></template>
            İlk Klanı Oluştur
          </n-button>
        </div>

        <!-- Clans Grid -->
        <div v-else class="clans-grid">
          <ClanCard
            v-for="clan in filteredClans"
            :key="clan.id"
            :clan="clan"
            @applied="handleApplied"
            @cancelled="handleCancelled"
          />
        </div>

        <!-- Load More -->
        <div v-if="hasMore && !clansStore.loading" class="text-center mt-8">
          <n-button size="large" @click="loadMore" :loading="loadingMore">
            Daha Fazla Yükle
          </n-button>
        </div>
      </div>
    </section>

    <!-- Create Clan Modal -->
    <n-modal v-model:show="showCreateModal" preset="card" title="Yeni Klan Oluştur" style="max-width: 500px">
      <n-form ref="createFormRef" :model="createForm" :rules="createRules">
        <n-form-item label="Klan Adı" path="name">
          <n-input v-model:value="createForm.name" placeholder="En az 3 karakter" maxlength="100" show-count />
        </n-form-item>

        <n-form-item label="Klan Etiketi" path="tag">
          <n-input
            v-model:value="createForm.tag"
            placeholder="2-5 karakter (örn: AGTR)"
            maxlength="5"
            :input-props="{ style: 'text-transform: uppercase' }"
          />
        </n-form-item>

        <n-form-item label="Açıklama" path="description">
          <n-input
            v-model:value="createForm.description"
            type="textarea"
            placeholder="Klanınızı tanıtın..."
            :rows="3"
            maxlength="500"
            show-count
          />
        </n-form-item>

        <n-form-item label="Renk">
          <n-color-picker v-model:value="createForm.color" :swatches="colorSwatches" />
        </n-form-item>

        <div class="flex justify-end gap-3 mt-4">
          <n-button @click="showCreateModal = false">İptal</n-button>
          <n-button type="primary" :loading="creating" @click="handleCreateClan">
            <template #icon><Plus class="w-4 h-4" /></template>
            Oluştur
          </n-button>
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import MaintenanceOverlay from '@/components/MaintenanceOverlay.vue'
import SteamRequiredModal from '@/components/SteamRequiredModal.vue'
import {
  Shield, Plus, Users, Trophy, Target, Crown, Search,
  ArrowRight, Clock
} from 'lucide-vue-next'
import { useClansStore } from '@/stores/clans'
import { useAuthStore } from '@/stores/auth'
import { useRequireSteam } from '@/composables/useRequireSteam'
import ClanCard from '@/components/social/ClanCard.vue'

const router = useRouter()
const message = useMessage()
const clansStore = useClansStore()
const authStore = useAuthStore()
const { hasSteam, showSteamModal, requireSteam, connectSteam, closeModal } = useRequireSteam()

// Search & Filter
const searchQuery = ref('')
const filterStatus = ref(null)
const sortBy = ref('points')
const isSearching = ref(false) // Loading indicator for debounced search

const statusOptions = [
  { label: 'Tümü', value: null },
  { label: 'Üye Alıyor', value: 'recruiting' },
  { label: 'Kapalı', value: 'closed' }
]

const sortOptions = [
  { label: 'Puan', value: 'points' },
  { label: 'Üye Sayısı', value: 'members' },
  { label: 'Galibiyetler', value: 'wins' },
  { label: 'En Yeni', value: 'newest' }
]

// Create Modal
const showCreateModal = ref(false)
const creating = ref(false)
const createFormRef = ref(null)
const createForm = ref({
  name: '',
  tag: '',
  description: '',
  color: '#f97316'
})

const createRules = {
  name: [
    { required: true, message: 'Klan adı gerekli', trigger: 'blur' },
    { min: 3, message: 'En az 3 karakter', trigger: 'blur' }
  ],
  tag: [
    { required: true, message: 'Klan etiketi gerekli', trigger: 'blur' },
    { min: 2, max: 5, message: '2-5 karakter arası', trigger: 'blur' }
  ]
}

const colorSwatches = [
  '#f97316', '#ef4444', '#22c55e', '#3b82f6',
  '#8b5cf6', '#ec4899', '#06b6d4', '#eab308'
]

// Pagination
const loadingMore = ref(false)
const hasMore = ref(true)
const page = ref(1)

// Computed
const filteredClans = computed(() => {
  let clans = [...clansStore.clans]

  // Filter by search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    clans = clans.filter(c =>
      c.name.toLowerCase().includes(query) ||
      c.tag.toLowerCase().includes(query)
    )
  }

  // Filter by status
  if (filterStatus.value) {
    clans = clans.filter(c => c.status === filterStatus.value)
  }

  // Sort
  switch (sortBy.value) {
    case 'members':
      clans.sort((a, b) => (b.member_count || 0) - (a.member_count || 0))
      break
    case 'wins':
      clans.sort((a, b) => (b.wins || 0) - (a.wins || 0))
      break
    case 'newest':
      clans.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      break
    default:
      clans.sort((a, b) => (b.points || 0) - (a.points || 0))
  }

  return clans
})

// Methods
let searchTimeout = null
const debouncedSearch = () => {
  // Show loading indicator while debouncing
  isSearching.value = true

  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    // Search is handled by computed, just turn off loading
    isSearching.value = false
    searchTimeout = null
  }, 300)
}

const goToMyClan = () => {
  if (clansStore.myClan) {
    router.push(`/clans/${clansStore.myClan.id}`)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('tr-TR')
}

const handleCreateClan = async () => {
  try {
    await createFormRef.value?.validate()

    creating.value = true
    const result = await clansStore.createClan({
      ...createForm.value,
      tag: createForm.value.tag.toUpperCase()
    })

    if (result.success) {
      message.success('Klan başarıyla oluşturuldu!')
      showCreateModal.value = false
      createForm.value = { name: '', tag: '', description: '', color: '#f97316' }

      if (result.clan_id) {
        router.push(`/clans/${result.clan_id}`)
      }
    } else {
      message.error(result.message || 'Klan oluşturulamadı')
    }
  } catch (e) {
    // Validation error
  } finally {
    creating.value = false
  }
}

const handleApplied = (clan) => {
  message.success(`${clan.name} klanına başvurunuz gönderildi`)
}

const handleCancelled = (clan) => {
  message.info(`${clan.name} klanına başvurunuz iptal edildi`)
}

const cancelApplication = async (clanId) => {
  const result = await clansStore.cancelApplication(clanId)
  if (result.success) {
    message.success('Başvuru iptal edildi')
  } else {
    message.error(result.message)
  }
}

const loadMore = async () => {
  loadingMore.value = true
  page.value++
  await clansStore.fetchClans({ page: page.value, append: true })
  loadingMore.value = false
}

// Initialize
onMounted(async () => {
  await clansStore.fetchClans()
  if (authStore.isAuthenticated) {
    await clansStore.fetchMyClan()
    await clansStore.fetchMyApplications()
  }
})

// Cleanup on unmount
onUnmounted(() => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
    searchTimeout = null
  }
})
</script>

<style scoped>
.clans-page {
  background: linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
}

.hero-section {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, transparent 50%);
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23f97316' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.container-main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* My Clan Card */
.my-clan-card {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(0, 0, 0, 0.2) 100%);
  border: 1px solid rgba(249, 115, 22, 0.3);
  border-radius: 16px;
  padding: 24px;
}

.clan-logo-large {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(249, 115, 22, 0.1);
  border-radius: 16px;
  border: 2px solid rgba(249, 115, 22, 0.3);
}

.clan-logo-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 14px;
}

.clan-tag {
  color: #f97316;
  font-weight: 700;
  font-family: monospace;
}

.clan-stats-row {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
}

.stat-item span {
  font-weight: 600;
  color: var(--text-primary);
}

/* Applications */
.applications-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.application-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.app-clan-logo {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 10px;
  color: var(--text-tertiary);
}

/* Loading & Empty States */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  color: var(--text-tertiary);
}

/* Clans Grid */
.clans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

@media (max-width: 768px) {
  .clans-grid {
    grid-template-columns: 1fr;
  }

  .clan-stats-row {
    display: none;
  }
}
</style>
