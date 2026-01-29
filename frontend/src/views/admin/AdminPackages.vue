<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <h1 class="text-2xl font-bold text-text-primary">Paket Yönetimi</h1>
        <router-link to="/admin" class="text-primary text-sm hover:text-primary-light">← Admin Panel</router-link>
      </div>
      <p class="text-text-muted text-sm">Sunucu paketlerini görüntüle ve düzenle</p>
    </div>

    <!-- Packages -->
    <div class="card overflow-hidden">
      <div class="p-4 border-b border-dark-border flex items-center justify-between">
        <h2 class="text-lg font-bold text-text-primary">Mevcut Paketler</h2>
        <button @click="showAddPackage = true" class="btn btn-primary text-sm">
          + Yeni Paket
        </button>
      </div>

      <div v-if="loading" class="p-8 text-center text-text-muted">
        <div class="text-3xl mb-2">⏳</div>
        <p class="text-sm">Paketler yükleniyor...</p>
      </div>

      <div v-else-if="packages.length === 0" class="p-8 text-center text-text-muted">
        <div class="text-3xl mb-2">📦</div>
        <p class="text-sm">Henüz paket yok</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Slug</th>
              <th>İsim</th>
              <th>Oyun</th>
              <th>Slot</th>
              <th>Fiyat</th>
              <th>Sıra</th>
              <th>Durum</th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pkg in packages" :key="pkg.id">
              <td class="text-text-muted text-sm">{{ pkg.id }}</td>
              <td class="font-mono text-text-secondary text-sm">{{ pkg.slug }}</td>
              <td class="font-medium text-text-primary">{{ pkg.name }}</td>
              <td class="text-text-secondary text-sm">{{ getGameName(pkg.game_type) }}</td>
              <td class="text-text-primary">{{ pkg.slots }}</td>
              <td class="font-bold text-primary">₺{{ pkg.price_monthly }}/ay</td>
              <td class="text-text-muted text-sm">{{ pkg.display_order }}</td>
              <td>
                <span class="badge text-xs" :class="pkg.is_active ? 'badge-success' : 'badge-neutral'">
                  {{ pkg.is_active ? 'Aktif' : 'Pasif' }}
                </span>
              </td>
              <td>
                <div class="flex gap-2">
                  <button @click="editPackage(pkg)" class="text-status-info hover:text-status-info/80 text-sm">
                    ✏️
                  </button>
                  <button @click="togglePackage(pkg)" class="text-status-warning hover:text-status-warning/80 text-sm">
                    {{ pkg.is_active ? '🔒' : '🔓' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Package Modal -->
    <div v-if="showAddPackage" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="card p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-semibold text-text-primary">Yeni Paket Ekle</h3>
          <button @click="showAddPackage = false" class="text-text-muted hover:text-text-primary">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">Slug (URL-friendly)</label>
            <input v-model="newPackage.slug" type="text" class="input" placeholder="cs16-basic" />
          </div>

          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">İsim</label>
            <input v-model="newPackage.name" type="text" class="input" placeholder="CS 1.6 Başlangıç Paketi" />
          </div>

          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">Oyun Tipi</label>
            <select v-model="newPackage.game_type" class="input">
              <option value="cstrike">Counter-Strike 1.6</option>
              <option value="czero">Condition Zero</option>
              <option value="valve">Half-Life</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">Slot Sayısı</label>
            <input v-model.number="newPackage.slots" type="number" class="input" placeholder="32" />
          </div>

          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">Aylık Fiyat (₺)</label>
            <input v-model.number="newPackage.price_monthly" type="number" step="0.01" class="input" placeholder="50.00" />
          </div>

          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">Açıklama</label>
            <textarea v-model="newPackage.description" class="textarea" placeholder="Paket açıklaması..."></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">Sıra</label>
            <input v-model.number="newPackage.display_order" type="number" class="input" placeholder="0" />
          </div>

          <div class="flex gap-3 pt-4">
            <button @click="showAddPackage = false" class="btn btn-secondary flex-1">
              İptal
            </button>
            <button @click="savePackage" class="btn btn-primary flex-1">
              Kaydet
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'

const loading = ref(true)
const packages = ref([])
const showAddPackage = ref(false)
const newPackage = ref({
  slug: '',
  name: '',
  game_type: 'cstrike',
  slots: 32,
  price_monthly: 50,
  description: '',
  display_order: 0,
  features: []
})

onMounted(() => {
  fetchPackages()
})

const fetchPackages = async () => {
  try {
    loading.value = true
    const response = await apiClient.get('/admin/commerce/packages')
    packages.value = response.data.data?.packages || []
  } catch (error) {
    console.error('Failed to fetch packages:', error)
    packages.value = []
  } finally {
    loading.value = false
  }
}

const getGameName = (gameType) => {
  const names = {
    cstrike: 'CS 1.6',
    czero: 'CZ',
    valve: 'HL'
  }
  return names[gameType] || gameType
}

const editPackage = (pkg) => {
  alert(`Paket düzenleme özelliği yakında eklenecek: ${pkg.name}`)
}

const togglePackage = async (pkg) => {
  if (!confirm(`${pkg.name} paketini ${pkg.is_active ? 'pasifleştirmek' : 'aktifleştirmek'} istediğinize emin misiniz?`)) return

  try {
    await apiClient.put(`/admin/commerce/packages/${pkg.id}`, {
      is_active: !pkg.is_active
    })
    alert('Paket durumu güncellendi!')
    await fetchPackages()
  } catch (error) {
    alert('Paket güncellenemedi: ' + (error.response?.data?.detail || 'Bilinmeyen hata'))
  }
}

const savePackage = async () => {
  if (!newPackage.value.slug || !newPackage.value.name) {
    alert('Lütfen gerekli alanları doldurun')
    return
  }

  try {
    await apiClient.post('/admin/commerce/packages', newPackage.value)
    alert('Paket oluşturuldu!')
    showAddPackage.value = false
    await fetchPackages()

    // Reset form
    newPackage.value = {
      slug: '',
      name: '',
      game_type: 'cstrike',
      slots: 32,
      price_monthly: 50,
      description: '',
      display_order: 0,
      features: []
    }
  } catch (error) {
    alert('Paket oluşturulamadı: ' + (error.response?.data?.detail || 'Bilinmeyen hata'))
  }
}
</script>
