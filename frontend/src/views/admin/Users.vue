<template>
  <AdminLayout>
    <div class="p-6">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl font-bold">Kullanıcı Yönetimi</h1>
          <p class="text-gray-500 dark:text-gray-400 mt-1">Toplam {{ totalUsers }} kullanıcı</p>
        </div>
        <n-button @click="exportUsers" :loading="exporting">
          <template #icon><n-icon><Download /></n-icon></template>
          Dışa Aktar
        </n-button>
      </div>

      <!-- Filters -->
      <n-card class="mb-6">
        <div class="flex flex-col md:flex-row gap-4">
          <n-input
            v-model:value="searchQuery"
            placeholder="Kullanıcı ara..."
            clearable
            @update:value="debouncedSearch"
            class="md:flex-1"
          >
            <template #prefix><n-icon><Search /></n-icon></template>
          </n-input>
          <n-select
            v-model:value="filterRole"
            :options="roleOptions"
            placeholder="Tüm Roller"
            clearable
            class="md:w-48"
            @update:value="fetchUsers"
          />
          <n-select
            v-model:value="filterStatus"
            :options="statusOptions"
            placeholder="Tüm Durumlar"
            clearable
            class="md:w-48"
            @update:value="fetchUsers"
          />
        </div>
      </n-card>

      <!-- Users Table -->
      <n-card>
        <n-data-table
          :columns="columns"
          :data="users"
          :loading="loading"
          :pagination="pagination"
          :row-key="row => row.id"
          striped
          @update:page="handlePageChange"
        />
      </n-card>

      <!-- User Edit Modal -->
      <n-modal
        v-model:show="showModal"
        preset="card"
        :title="editMode ? 'Kullanıcı Düzenle' : 'Kullanıcı Detayı'"
        style="width: 600px; max-width: 95vw;"
        :mask-closable="false"
      >
        <template v-if="selectedUser">
          <!-- User Header -->
          <div class="flex items-center gap-4 mb-6 pb-6 border-b border-gray-200 dark:border-gray-700">
            <n-avatar
              :size="72"
              round
              :src="`https://api.dicebear.com/7.x/initials/svg?seed=${selectedUser.username}`"
            />
            <div>
              <h3 class="text-xl font-semibold">{{ selectedUser.username }}</h3>
              <n-tag :type="getRoleType(selectedUser.role)" size="small" class="mt-1">
                {{ getRoleLabel(selectedUser.role) }}
              </n-tag>
            </div>
          </div>

          <!-- User Info Grid -->
          <n-grid :cols="2" :x-gap="16" :y-gap="16" class="mb-6">
            <n-gi>
              <n-statistic label="E-posta">
                <template #prefix><n-icon><Mail /></n-icon></template>
                {{ selectedUser.email }}
              </n-statistic>
            </n-gi>
            <n-gi>
              <n-statistic label="Kayıt Tarihi">
                <template #prefix><n-icon><Calendar /></n-icon></template>
                {{ formatDate(selectedUser.created_at) }}
              </n-statistic>
            </n-gi>
            <n-gi>
              <n-statistic label="TL Bakiye" :value="editMode ? undefined : selectedUser.balance || 0">
                <template #prefix><n-icon><Wallet /></n-icon></template>
                <template v-if="!editMode">{{ formatCurrency(selectedUser.balance || 0) }}</template>
                <n-input-number
                  v-else
                  v-model:value="editForm.balance"
                  :precision="2"
                  :min="0"
                  class="w-full"
                />
              </n-statistic>
            </n-gi>
            <n-gi>
              <n-statistic label="Armor Bakiye" :value="editMode ? undefined : selectedUser.balance_coin || 0">
                <template #prefix><n-icon><Shield /></n-icon></template>
                <template v-if="!editMode">{{ formatNumber(selectedUser.balance_coin || 0) }}</template>
                <n-input-number
                  v-else
                  v-model:value="editForm.balance_coin"
                  :precision="0"
                  :min="0"
                  class="w-full"
                />
              </n-statistic>
            </n-gi>
          </n-grid>

          <!-- Edit Form -->
          <div v-if="editMode" class="space-y-4">
            <n-divider>Düzenleme</n-divider>
            <n-form-item label="Rol">
              <n-select
                v-model:value="editForm.role"
                :options="allRoleOptions"
              />
            </n-form-item>
            <n-form-item label="Durum">
              <n-select
                v-model:value="editForm.status"
                :options="allStatusOptions"
              />
            </n-form-item>
          </div>
        </template>

        <template #footer>
          <div class="flex justify-end gap-3">
            <n-button @click="closeModal">İptal</n-button>
            <n-button v-if="!editMode" type="primary" @click="editMode = true">
              <template #icon><n-icon><Edit2 /></n-icon></template>
              Düzenle
            </n-button>
            <n-button v-else type="primary" :loading="saving" @click="saveUser">
              <template #icon><n-icon><Save /></n-icon></template>
              Kaydet
            </n-button>
          </div>
        </template>
      </n-modal>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, computed, h, onMounted } from 'vue'
import {
  NButton, NCard, NInput, NSelect, NDataTable, NModal, NAvatar,
  NTag, NGrid, NGi, NStatistic, NFormItem, NInputNumber, NDivider,
  NIcon, NSpace, NPopconfirm, useMessage
} from 'naive-ui'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'
import {
  Search, Download, Eye, Edit2, Ban, UserCheck, Mail, Calendar,
  Wallet, Shield, Save
} from 'lucide-vue-next'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

const message = useMessage()
const authStore = useAuthStore()

// State
const loading = ref(false)
const saving = ref(false)
const exporting = ref(false)
const users = ref([])
const totalUsers = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const searchQuery = ref('')
const filterRole = ref(null)
const filterStatus = ref(null)

const showModal = ref(false)
const editMode = ref(false)
const selectedUser = ref(null)
const editForm = reactive({
  role: '',
  status: '',
  balance: 0,
  balance_coin: 0
})

let searchTimeout = null

// Options
const roleOptions = [
  { label: 'Admin', value: 'admin' },
  { label: 'Moderatör', value: 'moderator' },
  { label: 'Kullanıcı', value: 'user' }
]

const allRoleOptions = [
  { label: 'Kullanıcı', value: 'user' },
  { label: 'Moderatör', value: 'moderator' },
  { label: 'Admin', value: 'admin' },
  { label: 'Süper Admin', value: 'superadmin' }
]

const statusOptions = [
  { label: 'Aktif', value: 'active' },
  { label: 'Yasaklı', value: 'banned' },
  { label: 'Pasif', value: 'inactive' }
]

const allStatusOptions = [
  { label: 'Aktif', value: 'active' },
  { label: 'Pasif', value: 'inactive' },
  { label: 'Yasaklı', value: 'banned' }
]

// Pagination
const pagination = computed(() => ({
  page: currentPage.value,
  pageSize: pageSize.value,
  pageCount: Math.ceil(totalUsers.value / pageSize.value),
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  itemCount: totalUsers.value,
  prefix: ({ itemCount }) => `Toplam ${itemCount} kullanıcı`
}))

// Table columns
const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 80,
    render: (row) => h('span', { class: 'font-mono text-gray-500' }, `#${row.id}`)
  },
  {
    title: 'Kullanıcı',
    key: 'username',
    render: (row) => h('div', { class: 'flex items-center gap-3' }, [
      h(NAvatar, {
        size: 36,
        round: true,
        src: `https://api.dicebear.com/7.x/initials/svg?seed=${row.username}`
      }),
      h('div', {}, [
        h('div', { class: 'font-medium' }, row.username),
        h('div', { class: 'text-xs text-gray-500' }, row.email)
      ])
    ])
  },
  {
    title: 'Bakiye',
    key: 'balance',
    render: (row) => h('div', {}, [
      h('div', { class: 'text-green-500 font-medium' }, `${formatCurrency(row.balance || 0)} TL`),
      h('div', { class: 'text-xs text-orange-500' }, `${formatNumber(row.balance_coin || 0)} Armor`)
    ])
  },
  {
    title: 'Rol',
    key: 'role',
    width: 120,
    render: (row) => h(NTag, {
      type: getRoleType(row.role),
      size: 'small',
      round: true
    }, { default: () => getRoleLabel(row.role) })
  },
  {
    title: 'Durum',
    key: 'status',
    width: 100,
    render: (row) => h(NTag, {
      type: getStatusType(row.status),
      size: 'small',
      round: true
    }, { default: () => getStatusLabel(row.status) })
  },
  {
    title: 'Kayıt',
    key: 'created_at',
    width: 140,
    render: (row) => h('span', { class: 'text-gray-500 text-sm' }, formatDate(row.created_at))
  },
  {
    title: 'İşlemler',
    key: 'actions',
    width: 150,
    render: (row) => h(NSpace, { size: 'small' }, {
      default: () => [
        h(NButton, {
          size: 'small',
          quaternary: true,
          circle: true,
          onClick: () => viewUser(row)
        }, { icon: () => h(NIcon, null, { default: () => h(Eye) }) }),
        h(NButton, {
          size: 'small',
          quaternary: true,
          circle: true,
          onClick: () => openEditUser(row)
        }, { icon: () => h(NIcon, null, { default: () => h(Edit2) }) }),
        row.status !== 'banned'
          ? h(NPopconfirm, {
              onPositiveClick: () => banUser(row)
            }, {
              trigger: () => h(NButton, {
                size: 'small',
                quaternary: true,
                circle: true,
                type: 'error'
              }, { icon: () => h(NIcon, null, { default: () => h(Ban) }) }),
              default: () => `${row.username} kullanıcısını yasaklamak istediğinize emin misiniz?`
            })
          : h(NPopconfirm, {
              onPositiveClick: () => unbanUser(row)
            }, {
              trigger: () => h(NButton, {
                size: 'small',
                quaternary: true,
                circle: true,
                type: 'success'
              }, { icon: () => h(NIcon, null, { default: () => h(UserCheck) }) }),
              default: () => `${row.username} kullanıcısının yasağını kaldırmak istediğinize emin misiniz?`
            })
      ]
    })
  }
]

// CSRF Token
const getCsrfToken = () => {
  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'csrf_token') return value
  }
  return null
}

const getHeaders = () => {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authStore.token}`
  }
  const csrfToken = getCsrfToken()
  if (csrfToken) headers['X-CSRF-Token'] = csrfToken
  return headers
}

// Helpers
const getRoleLabel = (role) => {
  const r = typeof role === 'string' ? role : role?.value || 'user'
  const labels = { admin: 'Admin', moderator: 'Moderatör', user: 'Kullanıcı', superadmin: 'Süper Admin' }
  return labels[r] || r
}

const getRoleType = (role) => {
  const r = typeof role === 'string' ? role : role?.value || 'user'
  const types = { admin: 'error', moderator: 'warning', user: 'info', superadmin: 'error' }
  return types[r] || 'default'
}

const getStatusLabel = (status) => {
  const labels = { active: 'Aktif', inactive: 'Pasif', banned: 'Yasaklı' }
  return labels[status] || status
}

const getStatusType = (status) => {
  const types = { active: 'success', inactive: 'default', banned: 'error' }
  return types[status] || 'default'
}

const formatDate = (date) => {
  if (!date) return '-'
  return format(new Date(date), 'dd MMM yyyy', { locale: tr })
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value)
}

const formatNumber = (value) => {
  return new Intl.NumberFormat('tr-TR').format(value)
}

// API Calls
const fetchUsers = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      per_page: pageSize.value
    })
    if (searchQuery.value) params.append('search', searchQuery.value)
    if (filterRole.value) params.append('role', filterRole.value)
    if (filterStatus.value) params.append('status', filterStatus.value)

    const response = await fetch(`/api/admin/users?${params}`, { headers: getHeaders() })
    if (response.ok) {
      const data = await response.json()
      users.value = data.users || []
      totalUsers.value = data.pagination?.total || 0
    } else {
      message.error('Kullanıcılar yüklenemedi')
    }
  } catch (error) {
    console.error('Fetch users error:', error)
    message.error('Bağlantı hatası')
  } finally {
    loading.value = false
  }
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchUsers()
  }, 300)
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchUsers()
}

const viewUser = (user) => {
  selectedUser.value = { ...user }
  editMode.value = false
  showModal.value = true
  resetEditForm(user)
}

const openEditUser = (user) => {
  selectedUser.value = { ...user }
  editMode.value = true
  showModal.value = true
  resetEditForm(user)
}

const resetEditForm = (user) => {
  const role = typeof user.role === 'string' ? user.role : user.role?.value || 'user'
  editForm.role = role
  editForm.status = user.status || 'active'
  editForm.balance = user.balance || 0
  editForm.balance_coin = user.balance_coin || 0
}

const closeModal = () => {
  showModal.value = false
  selectedUser.value = null
  editMode.value = false
}

const saveUser = async () => {
  saving.value = true
  try {
    const response = await fetch(`/api/admin/users/${selectedUser.value.id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({
        role: editForm.role,
        status: editForm.status,
        balance: editForm.balance,
        balance_coin: editForm.balance_coin
      })
    })

    if (response.ok) {
      message.success('Kullanıcı başarıyla güncellendi')

      // Update local data
      const index = users.value.findIndex(u => u.id === selectedUser.value.id)
      if (index !== -1) {
        users.value[index] = {
          ...users.value[index],
          role: editForm.role,
          status: editForm.status,
          balance: editForm.balance,
          balance_coin: editForm.balance_coin
        }
      }

      // If editing current user, update auth store
      if (authStore.user?.id === selectedUser.value.id) {
        authStore.updateBalance(editForm.balance, editForm.balance_coin)
      }

      closeModal()
    } else {
      const error = await response.json()
      message.error(error.detail || 'Güncelleme başarısız')
    }
  } catch (error) {
    console.error('Save user error:', error)
    message.error('Bağlantı hatası')
  } finally {
    saving.value = false
  }
}

const banUser = async (user) => {
  try {
    const response = await fetch(`/api/admin/users/${user.id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({ status: 'banned' })
    })
    if (response.ok) {
      user.status = 'banned'
      message.success(`${user.username} yasaklandı`)
    } else {
      message.error('İşlem başarısız')
    }
  } catch (error) {
    message.error('Bağlantı hatası')
  }
}

const unbanUser = async (user) => {
  try {
    const response = await fetch(`/api/admin/users/${user.id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({ status: 'active' })
    })
    if (response.ok) {
      user.status = 'active'
      message.success(`${user.username} yasağı kaldırıldı`)
    } else {
      message.error('İşlem başarısız')
    }
  } catch (error) {
    message.error('Bağlantı hatası')
  }
}

const exportUsers = async () => {
  exporting.value = true
  try {
    window.open(`/api/admin/users/export?format=csv&token=${authStore.token}`, '_blank')
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.space-y-4 > * + * {
  margin-top: 1rem;
}
</style>
