<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <h1 class="text-2xl font-bold text-text-primary">Sunucu Yönetimi</h1>
        <router-link to="/admin" class="text-primary text-sm hover:text-primary-light">← Admin Panel</router-link>
      </div>
      <p class="text-text-muted text-sm">Tüm sunucuları görüntüle ve yönet</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
      <div class="card p-4">
        <div class="text-text-muted text-xs mb-1">Toplam Sunucu</div>
        <div class="text-2xl font-bold text-text-primary">{{ stats.total || 0 }}</div>
      </div>
      <div class="card p-4">
        <div class="text-text-muted text-xs mb-1">Aktif</div>
        <div class="text-2xl font-bold text-status-success">{{ stats.running || 0 }}</div>
      </div>
      <div class="card p-4">
        <div class="text-text-muted text-xs mb-1">Kapalı</div>
        <div class="text-2xl font-bold text-text-muted">{{ stats.stopped || 0 }}</div>
      </div>
      <div class="card p-4">
        <div class="text-text-muted text-xs mb-1">Beklemede</div>
        <div class="text-2xl font-bold text-status-warning">{{ stats.pending || 0 }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4 mb-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
        <input
          v-model="search"
          type="text"
          placeholder="Sunucu ara..."
          class="input"
        />
        <select v-model="filterStatus" class="input">
          <option value="">Tüm Durumlar</option>
          <option value="running">Aktif</option>
          <option value="stopped">Kapalı</option>
          <option value="pending">Beklemede</option>
          <option value="suspended">Askıda</option>
        </select>
        <select v-model="filterGame" class="input">
          <option value="">Tüm Oyunlar</option>
          <option value="cstrike">Counter-Strike 1.6</option>
          <option value="czero">Condition Zero</option>
          <option value="valve">Half-Life</option>
        </select>
        <button @click="fetchServers" class="btn btn-primary">
          🔍 Ara
        </button>
      </div>
    </div>

    <!-- Servers Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-text-muted">
        <div class="text-3xl mb-2">⏳</div>
        <p class="text-sm">Sunucular yükleniyor...</p>
      </div>

      <div v-else-if="servers.length === 0" class="p-8 text-center text-text-muted">
        <div class="text-3xl mb-2">🖥️</div>
        <p class="text-sm">Sunucu bulunamadı</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Sunucu Adı</th>
              <th>Sahibi</th>
              <th>IP:Port</th>
              <th>Oyun</th>
              <th>Durum</th>
              <th>Oyuncular</th>
              <th>Bitiş Tarihi</th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="server in servers" :key="server.id">
              <td class="text-text-muted text-sm">{{ server.id }}</td>
              <td class="font-medium text-text-primary">{{ server.name }}</td>
              <td class="text-text-secondary text-sm">{{ server.owner_username || 'N/A' }}</td>
              <td class="text-text-muted text-sm font-mono">{{ server.ip_address }}:{{ server.port }}</td>
              <td class="text-text-secondary text-sm">{{ getGameName(server.game_type) }}</td>
              <td>
                <span class="badge text-xs" :class="getStatusBadge(server.status)">
                  {{ getStatusText(server.status) }}
                </span>
              </td>
              <td class="text-text-primary text-sm">{{ server.current_players || 0 }}/{{ server.slots }}</td>
              <td class="text-text-muted text-sm">{{ formatDate(server.expires_at) }}</td>
              <td>
                <div class="flex gap-2">
                  <button @click="viewServer(server)" class="text-primary hover:text-primary-light text-sm">
                    👁️
                  </button>
                  <button
                    v-if="server.status?.toLowerCase() === 'stopped'"
                    @click="startServer(server)"
                    class="text-status-success hover:text-status-success/80 text-sm"
                  >
                    ▶️
                  </button>
                  <button
                    v-if="server.status?.toLowerCase() === 'running'"
                    @click="stopServer(server)"
                    class="text-status-error hover:text-status-error/80 text-sm"
                  >
                    ⏹️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="border-t border-dark-border p-4">
        <div class="flex items-center justify-between">
          <div class="text-sm text-text-muted">
            Toplam {{ total }} sunucu
          </div>
          <div class="flex gap-2">
            <button
              @click="page--"
              :disabled="page === 1"
              class="pagination-btn"
            >
              ← Önceki
            </button>
            <span class="px-3 py-1.5 text-sm text-text-secondary">
              Sayfa {{ page }} / {{ totalPages }}
            </span>
            <button
              @click="page++"
              :disabled="page === totalPages"
              class="pagination-btn"
            >
              Sonraki →
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import apiClient from '@/api/client'
import { getStatusBadge, getStatusText, getGameName, formatDate } from '@/utils/helpers'

const loading = ref(true)
const servers = ref([])
const stats = ref({})
const total = ref(0)
const page = ref(1)
const perPage = ref(20)
const totalPages = ref(0)

const search = ref('')
const filterStatus = ref('')
const filterGame = ref('')

onMounted(() => {
  fetchStats()
  fetchServers()
})

watch(page, () => {
  fetchServers()
})

const fetchStats = async () => {
  try {
    const response = await apiClient.get('/admin/servers/stats')
    stats.value = response.data || {}
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const fetchServers = async () => {
  try {
    loading.value = true
    const params = {
      page: page.value,
      per_page: perPage.value
    }

    if (search.value) params.search = search.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterGame.value) params.game_type = filterGame.value

    const response = await apiClient.get('/admin/servers', { params })
    servers.value = response.data.data || []
    total.value = response.data.pagination?.total || 0
    totalPages.value = response.data.pagination?.pages || Math.ceil(total.value / perPage.value)
  } catch (error) {
    console.error('Failed to fetch servers:', error)
    servers.value = []
  } finally {
    loading.value = false
  }
}

const viewServer = (server) => {
  window.open(`/servers/${server.id}`, '_blank')
}

const startServer = async (server) => {
  if (!confirm(`${server.name} sunucusunu başlatmak istediğinize emin misiniz?`)) return

  try {
    await apiClient.post(`/servers/${server.id}/start`)
    alert('Sunucu başlatılıyor...')
    await fetchServers()
  } catch (error) {
    alert('Sunucu başlatılamadı: ' + (error.response?.data?.detail || 'Bilinmeyen hata'))
  }
}

const stopServer = async (server) => {
  if (!confirm(`${server.name} sunucusunu durdurmak istediğinize emin misiniz?`)) return

  try {
    await apiClient.post(`/servers/${server.id}/stop`)
    alert('Sunucu durduruluyor...')
    await fetchServers()
  } catch (error) {
    alert('Sunucu durdurulamadı: ' + (error.response?.data?.detail || 'Bilinmeyen hata'))
  }
}
</script>
