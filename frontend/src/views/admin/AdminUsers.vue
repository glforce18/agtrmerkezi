<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <h1 class="text-2xl font-bold text-text-primary">Kullanıcı Yönetimi</h1>
        <router-link to="/admin" class="text-primary text-sm hover:text-primary-light">← Admin Panel</router-link>
      </div>
      <p class="text-text-muted text-sm">Tüm kullanıcıları görüntüle ve yönet</p>
    </div>

    <!-- Filters -->
    <div class="card p-4 mb-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
        <input
          v-model="search"
          type="text"
          placeholder="Kullanıcı ara..."
          class="input"
        />
        <select v-model="filterRole" class="input">
          <option value="">Tüm Roller</option>
          <option value="user">Kullanıcı</option>
          <option value="admin">Admin</option>
          <option value="superadmin">Superadmin</option>
        </select>
        <select v-model="filterStatus" class="input">
          <option value="">Tüm Durumlar</option>
          <option value="active">Aktif</option>
          <option value="banned">Yasaklı</option>
        </select>
        <button @click="fetchUsers" class="btn btn-primary">
          🔍 Ara
        </button>
      </div>
    </div>

    <!-- Users Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-text-muted">
        <div class="text-3xl mb-2">⏳</div>
        <p class="text-sm">Kullanıcılar yükleniyor...</p>
      </div>

      <div v-else-if="users.length === 0" class="p-8 text-center text-text-muted">
        <div class="text-3xl mb-2">👤</div>
        <p class="text-sm">Kullanıcı bulunamadı</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Kullanıcı Adı</th>
              <th>Email</th>
              <th>Rol</th>
              <th>Bakiye</th>
              <th>Kayıt Tarihi</th>
              <th>Durum</th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td class="text-text-muted text-sm">{{ user.id }}</td>
              <td class="font-medium text-text-primary">{{ user.username }}</td>
              <td class="text-text-secondary text-sm">{{ user.email || 'N/A' }}</td>
              <td>
                <span class="badge" :class="getRoleBadge(user.role)">
                  {{ getRoleText(user.role) }}
                </span>
              </td>
              <td class="text-text-primary font-medium">₺{{ (user.balance || 0).toFixed(2) }}</td>
              <td class="text-text-muted text-sm">{{ formatDate(user.created_at) }}</td>
              <td>
                <span class="badge" :class="user.is_banned ? 'badge-error' : 'badge-success'">
                  {{ user.is_banned ? 'Yasaklı' : 'Aktif' }}
                </span>
              </td>
              <td>
                <div class="flex gap-2">
                  <button @click="viewUser(user)" class="text-primary hover:text-primary-light text-sm">
                    👁️
                  </button>
                  <button @click="editUser(user)" class="text-status-info hover:text-status-info/80 text-sm">
                    ✏️
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
            Toplam {{ total }} kullanıcı
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

const loading = ref(true)
const users = ref([])
const total = ref(0)
const page = ref(1)
const perPage = ref(20)
const totalPages = ref(0)

const search = ref('')
const filterRole = ref('')
const filterStatus = ref('')

onMounted(() => {
  fetchUsers()
})

watch(page, () => {
  fetchUsers()
})

const fetchUsers = async () => {
  try {
    loading.value = true
    const params = {
      page: page.value,
      per_page: perPage.value
    }

    if (search.value) params.search = search.value
    if (filterRole.value) params.role = filterRole.value
    if (filterStatus.value) params.status = filterStatus.value

    const response = await apiClient.get('/admin/users', { params })
    users.value = response.data.data || []
    total.value = response.data.pagination?.total || 0
    totalPages.value = response.data.pagination?.pages || Math.ceil(total.value / perPage.value)
  } catch (error) {
    console.error('Failed to fetch users:', error)
    users.value = []
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const getRoleBadge = (role) => {
  const badges = {
    superadmin: 'badge-error',
    admin: 'badge-warning',
    user: 'badge-neutral'
  }
  return badges[role?.toLowerCase()] || 'badge-neutral'
}

const getRoleText = (role) => {
  const texts = {
    superadmin: 'Superadmin',
    admin: 'Admin',
    user: 'Kullanıcı'
  }
  return texts[role?.toLowerCase()] || role
}

const viewUser = (user) => {
  alert(`Kullanıcı Detayı: ${user.username}\nID: ${user.id}\nEmail: ${user.email || 'N/A'}`)
}

const editUser = (user) => {
  alert(`Kullanıcı düzenleme özelliği yakında eklenecek: ${user.username}`)
}
</script>
