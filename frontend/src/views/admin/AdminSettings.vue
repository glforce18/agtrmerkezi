<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <h1 class="text-2xl font-bold text-text-primary">Sistem Ayarları</h1>
        <router-link to="/admin" class="text-primary text-sm hover:text-primary-light">← Admin Panel</router-link>
      </div>
      <p class="text-text-muted text-sm">Sistem genelinde ayarları yönet</p>
    </div>

    <!-- Settings Sections -->
    <div class="space-y-4">
      <!-- General Settings -->
      <div class="card p-6">
        <h2 class="text-lg font-bold text-text-primary mb-4">Genel Ayarlar</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">Site Adı</label>
            <input v-model="settings.site_name" type="text" class="input" />
          </div>
          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">Site Açıklaması</label>
            <textarea v-model="settings.site_description" class="textarea"></textarea>
          </div>
          <div class="flex items-center gap-3">
            <input v-model="settings.maintenance_mode" type="checkbox" id="maintenance" class="w-4 h-4" />
            <label for="maintenance" class="text-sm text-text-primary cursor-pointer">
              Bakım Modu (Site kullanıcılara kapalı olur)
            </label>
          </div>
        </div>
      </div>

      <!-- Server Settings -->
      <div class="card p-6">
        <h2 class="text-lg font-bold text-text-primary mb-4">Sunucu Ayarları</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">Ana Sunucu IP</label>
            <input v-model="settings.main_server_ip" type="text" class="input" placeholder="185.171.25.137" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-text-primary mb-2">Port Başlangıç</label>
              <input v-model.number="settings.port_start" type="number" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-2">Port Bitiş</label>
              <input v-model.number="settings.port_end" type="number" class="input" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">HLDS Yolu</label>
            <input v-model="settings.hlds_path" type="text" class="input" placeholder="/home/gameservers" />
          </div>
        </div>
      </div>

      <!-- Payment Settings -->
      <div class="card p-6">
        <h2 class="text-lg font-bold text-text-primary mb-4">Ödeme Ayarları</h2>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-text-primary mb-2">Minimum Yükleme (₺)</label>
              <input v-model.number="settings.min_deposit" type="number" step="0.01" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-2">Maksimum Yükleme (₺)</label>
              <input v-model.number="settings.max_deposit" type="number" step="0.01" class="input" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">Armor Dönüşüm Oranı (1₺ = X Armor)</label>
            <input v-model.number="settings.armor_rate" type="number" class="input" />
          </div>
        </div>
      </div>

      <!-- Discount Settings -->
      <div class="card p-6">
        <h2 class="text-lg font-bold text-text-primary mb-4">İndirim Oranları</h2>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">3 Ay (%)</label>
            <input v-model.number="settings.discount_3_month" type="number" step="0.01" class="input" />
          </div>
          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">6 Ay (%)</label>
            <input v-model.number="settings.discount_6_month" type="number" step="0.01" class="input" />
          </div>
          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">12 Ay (%)</label>
            <input v-model.number="settings.discount_12_month" type="number" step="0.01" class="input" />
          </div>
        </div>
      </div>

      <!-- Email Settings -->
      <div class="card p-6">
        <h2 class="text-lg font-bold text-text-primary mb-4">E-posta Ayarları</h2>
        <div class="space-y-4">
          <div class="flex items-center gap-3">
            <input v-model="settings.email_enabled" type="checkbox" id="email_enabled" class="w-4 h-4" />
            <label for="email_enabled" class="text-sm text-text-primary cursor-pointer">
              E-posta Gönderimini Etkinleştir
            </label>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-text-primary mb-2">SMTP Host</label>
              <input v-model="settings.smtp_host" type="text" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-2">SMTP Port</label>
              <input v-model.number="settings.smtp_port" type="number" class="input" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">SMTP Kullanıcı</label>
            <input v-model="settings.smtp_user" type="text" class="input" />
          </div>
          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">Gönderen E-posta</label>
            <input v-model="settings.smtp_from" type="email" class="input" />
          </div>
        </div>
      </div>

      <!-- Save Button -->
      <div class="flex justify-end gap-3">
        <button @click="resetSettings" class="btn btn-secondary">
          🔄 Sıfırla
        </button>
        <button @click="saveSettings" class="btn btn-primary">
          💾 Kaydet
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const settings = ref({
  site_name: 'AGTR Merkezi',
  site_description: 'Half-Life & CS 1.6 Gaming Community Platform',
  maintenance_mode: false,
  main_server_ip: '185.171.25.137',
  port_start: 27018,
  port_end: 27050,
  hlds_path: '/home/gameservers',
  min_deposit: 10,
  max_deposit: 10000,
  armor_rate: 100,
  discount_3_month: 10,
  discount_6_month: 15,
  discount_12_month: 25,
  email_enabled: false,
  smtp_host: 'localhost',
  smtp_port: 587,
  smtp_user: '',
  smtp_from: 'noreply@agtrmerkezi.com'
})

onMounted(() => {
  loadSettings()
})

const loadSettings = async () => {
  try {
    // TODO: Implement settings API
    console.log('Settings loaded')
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}

const saveSettings = async () => {
  try {
    // TODO: Implement settings API
    alert('Ayarlar kaydedildi! (Backend entegrasyonu gerekli)')
    console.log('Settings to save:', settings.value)
  } catch (error) {
    alert('Ayarlar kaydedilemedi: ' + error.message)
  }
}

const resetSettings = () => {
  if (confirm('Tüm ayarları varsayılan değerlere döndürmek istediğinize emin misiniz?')) {
    loadSettings()
  }
}
</script>
