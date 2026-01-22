<template>
  <AdminLayout>
    <div class="maintenance-page">
      <!-- Header -->
      <div class="page-header">
        <h1>Bakim Modu Yonetimi</h1>
        <p>Sayfalari bakima al veya ac</p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-box">
        <div class="spinner"></div>
        <span>Yukleniyor...</span>
      </div>

      <!-- Features Grid -->
      <div v-else class="features-grid">
        <div
          v-for="item in features"
          :key="item.key"
          class="feature-card"
          :class="{ active: item.is_enabled }"
        >
          <div class="card-header">
            <span class="feature-icon">{{ item.icon }}</span>
            <span class="feature-name">{{ item.name }}</span>
          </div>

          <p class="feature-desc">{{ item.description }}</p>

          <div class="card-footer">
            <span class="status-text" :class="item.is_enabled ? 'maintenance' : 'online'">
              {{ item.is_enabled ? 'BAKIMDA' : 'AKTIF' }}
            </span>
            <button
              class="toggle-btn"
              :class="item.is_enabled ? 'btn-green' : 'btn-orange'"
              @click="toggleMaintenance(item)"
              :disabled="saving === item.key"
            >
              <span v-if="saving === item.key" class="btn-spinner"></span>
              <span v-else>{{ item.is_enabled ? 'Ac' : 'Bakima Al' }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Bulk Actions -->
      <div class="bulk-actions">
        <button class="bulk-btn danger" @click="enableAll" :disabled="bulkSaving">
          Tumunu Bakima Al
        </button>
        <button class="bulk-btn success" @click="disableAll" :disabled="bulkSaving">
          Tumunu Ac
        </button>
      </div>

      <!-- Toast -->
      <div v-if="toast.show" class="toast" :class="toast.type">
        {{ toast.message }}
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const loading = ref(true)
const saving = ref(null)
const bulkSaving = ref(false)
const features = ref([])
const toast = ref({ show: false, message: '', type: 'success' })

const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => toast.value.show = false, 3000)
}

const getHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${authStore.token}`
})

const fetchFeatures = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/maintenance/admin/list', {
      headers: getHeaders()
    })
    const data = await res.json()
    if (res.ok) {
      features.value = data.features || []
    } else {
      showToast(data.detail || 'Veri alinamadi', 'error')
    }
  } catch (e) {
    showToast('Baglanti hatasi', 'error')
  }
  loading.value = false
}

const toggleMaintenance = async (item) => {
  saving.value = item.key
  try {
    const res = await fetch(`/api/maintenance/admin/${item.key}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({
        is_enabled: !item.is_enabled,
        message: !item.is_enabled ? `${item.name} su anda bakimdadir.` : null
      })
    })
    const data = await res.json()
    if (res.ok) {
      showToast(data.message || 'Guncellendi', 'success')
      await fetchFeatures()
    } else {
      showToast(data.detail || 'Hata olustu', 'error')
    }
  } catch (e) {
    showToast('Baglanti hatasi', 'error')
  }
  saving.value = null
}

const enableAll = async () => {
  bulkSaving.value = true
  try {
    const res = await fetch('/api/maintenance/admin/all-on?message=Site%20bakim%20modunda', {
      method: 'POST',
      headers: getHeaders()
    })
    if (res.ok) {
      showToast('Tum ozellikler bakima alindi', 'success')
      await fetchFeatures()
    }
  } catch (e) {
    showToast('Hata olustu', 'error')
  }
  bulkSaving.value = false
}

const disableAll = async () => {
  bulkSaving.value = true
  try {
    const res = await fetch('/api/maintenance/admin/all-off', {
      method: 'POST',
      headers: getHeaders()
    })
    if (res.ok) {
      showToast('Tum bakimlar kapatildi', 'success')
      await fetchFeatures()
    }
  } catch (e) {
    showToast('Hata olustu', 'error')
  }
  bulkSaving.value = false
}

onMounted(() => {
  fetchFeatures()
})
</script>

<style scoped>
.maintenance-page {
  padding: 24px;
  max-width: 1200px;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
}

.page-header p {
  color: #888;
  font-size: 14px;
}

.loading-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  color: #888;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #333;
  border-top-color: #f97316;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.feature-card {
  background: #1a1a1f;
  border: 2px solid #2a2a30;
  border-radius: 16px;
  padding: 20px;
  transition: all 0.2s;
}

.feature-card:hover {
  border-color: #3a3a40;
}

.feature-card.active {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #1a1a1f 0%, rgba(245, 158, 11, 0.05) 100%);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.feature-icon {
  font-size: 28px;
}

.feature-name {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.feature-desc {
  color: #666;
  font-size: 13px;
  margin-bottom: 16px;
  line-height: 1.4;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-text {
  font-size: 12px;
  font-weight: 700;
  padding: 6px 12px;
  border-radius: 6px;
}

.status-text.online {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.status-text.maintenance {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.toggle-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-orange {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: #fff;
}

.btn-orange:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.4);
}

.btn-green {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #fff;
}

.btn-green:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4);
}

.bulk-actions {
  display: flex;
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid #2a2a30;
}

.bulk-btn {
  padding: 14px 28px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.bulk-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.bulk-btn.danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: #fff;
}

.bulk-btn.danger:hover:not(:disabled) {
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.4);
}

.bulk-btn.success {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #fff;
}

.bulk-btn.success:hover:not(:disabled) {
  box-shadow: 0 4px 16px rgba(34, 197, 94, 0.4);
}

.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 16px 24px;
  border-radius: 10px;
  font-weight: 500;
  z-index: 9999;
  animation: slideIn 0.3s ease;
}

.toast.success {
  background: #22c55e;
  color: #fff;
}

.toast.error {
  background: #ef4444;
  color: #fff;
}

@keyframes slideIn {
  from {
    transform: translateX(100px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
