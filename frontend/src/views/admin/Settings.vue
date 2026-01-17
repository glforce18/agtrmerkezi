<template>
  <AdminLayout>
    <div class="admin-settings">
      <!-- Header -->
      <div class="page-header">
        <div class="header-left">
          <h1>Sistem Ayarları</h1>
          <p class="subtitle">Site yapılandırması ve genel ayarlar</p>
        </div>
      </div>

      <!-- Settings Tabs -->
      <div class="settings-layout">
        <aside class="settings-nav">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="nav-item"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            <component :is="tab.icon" :size="18" />
            <span>{{ tab.label }}</span>
          </button>
        </aside>

        <div class="settings-content">
          <!-- General Settings -->
          <div v-show="activeTab === 'general'" class="settings-section">
            <h2>Genel Ayarlar</h2>

            <div class="form-group">
              <label>Site Adı</label>
              <input v-model="settings.site_name" type="text" placeholder="AGTR Merkezi" />
            </div>

            <div class="form-group">
              <label>Site Açıklaması</label>
              <textarea v-model="settings.site_description" rows="2" placeholder="Site açıklaması..."></textarea>
            </div>

            <div class="form-group">
              <label>Logo URL</label>
              <input v-model="settings.logo_url" type="text" placeholder="/static/logo.png" />
            </div>

            <div class="form-group">
              <label>Favicon URL</label>
              <input v-model="settings.favicon_url" type="text" placeholder="/static/favicon.ico" />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Discord Sunucusu</label>
                <input v-model="settings.discord_url" type="text" placeholder="https://discord.gg/..." />
              </div>
              <div class="form-group">
                <label>Destek E-posta</label>
                <input v-model="settings.support_email" type="email" placeholder="destek@site.com" />
              </div>
            </div>

            <div class="toggle-group">
              <label class="toggle-label">
                <span>Bakım Modu</span>
                <span class="toggle-desc">Site bakım modunda olduğunda ziyaretçiler bilgilendirilir</span>
              </label>
              <label class="toggle">
                <input type="checkbox" v-model="settings.maintenance_mode" />
                <span class="toggle-slider"></span>
              </label>
            </div>

            <div class="toggle-group">
              <label class="toggle-label">
                <span>Yeni Kayıt</span>
                <span class="toggle-desc">Yeni kullanıcı kayıtlarına izin ver</span>
              </label>
              <label class="toggle">
                <input type="checkbox" v-model="settings.registration_enabled" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <!-- Payment Settings -->
          <div v-show="activeTab === 'payments'" class="settings-section">
            <h2>Ödeme Ayarları</h2>

            <div class="form-group">
              <label>Banka Hesap Bilgisi</label>
              <textarea v-model="settings.bank_info" rows="4" placeholder="Banka: ...&#10;IBAN: ...&#10;Alıcı: ..."></textarea>
            </div>

            <div class="form-group">
              <label>Papara No</label>
              <input v-model="settings.papara_number" type="text" placeholder="1234567890" />
            </div>

            <div class="form-group">
              <label>Kripto Cüzdan (BTC)</label>
              <input v-model="settings.btc_address" type="text" placeholder="bc1..." />
            </div>

            <div class="form-group">
              <label>Minimum Yükleme Tutarı (₺)</label>
              <input v-model.number="settings.min_deposit" type="number" min="0" step="1" />
            </div>

            <div class="toggle-group">
              <label class="toggle-label">
                <span>Otomatik Onay</span>
                <span class="toggle-desc">Ödemeleri otomatik olarak onayla (dikkatli kullan)</span>
              </label>
              <label class="toggle">
                <input type="checkbox" v-model="settings.auto_approve_payments" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <!-- Server Settings -->
          <div v-show="activeTab === 'servers'" class="settings-section">
            <h2>Sunucu Ayarları</h2>

            <div class="form-row">
              <div class="form-group">
                <label>Varsayılan Slot</label>
                <input v-model.number="settings.default_slots" type="number" min="1" />
              </div>
              <div class="form-group">
                <label>Maksimum Slot</label>
                <input v-model.number="settings.max_slots" type="number" min="1" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Varsayılan RAM (MB)</label>
                <input v-model.number="settings.default_ram" type="number" min="128" step="64" />
              </div>
              <div class="form-group">
                <label>Maksimum RAM (MB)</label>
                <input v-model.number="settings.max_ram" type="number" min="128" step="64" />
              </div>
            </div>

            <div class="form-group">
              <label>Sorgu Aralığı (saniye)</label>
              <input v-model.number="settings.query_interval" type="number" min="30" />
            </div>

            <div class="toggle-group">
              <label class="toggle-label">
                <span>RCON Erişimi</span>
                <span class="toggle-desc">Kullanıcılara RCON erişimi ver</span>
              </label>
              <label class="toggle">
                <input type="checkbox" v-model="settings.rcon_enabled" />
                <span class="toggle-slider"></span>
              </label>
            </div>

            <div class="toggle-group">
              <label class="toggle-label">
                <span>FTP Erişimi</span>
                <span class="toggle-desc">Kullanıcılara FTP erişimi ver</span>
              </label>
              <label class="toggle">
                <input type="checkbox" v-model="settings.ftp_enabled" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <!-- Security Settings -->
          <div v-show="activeTab === 'security'" class="settings-section">
            <h2>Güvenlik Ayarları</h2>

            <div class="form-group">
              <label>Oturum Süresi (dakika)</label>
              <input v-model.number="settings.session_timeout" type="number" min="5" />
            </div>

            <div class="form-group">
              <label>Maksimum Giriş Denemesi</label>
              <input v-model.number="settings.max_login_attempts" type="number" min="1" />
            </div>

            <div class="form-group">
              <label>IP Yasak Süresi (dakika)</label>
              <input v-model.number="settings.ban_duration" type="number" min="1" />
            </div>

            <div class="toggle-group">
              <label class="toggle-label">
                <span>2FA Zorunlu (Admin)</span>
                <span class="toggle-desc">Admin kullanıcılar için 2FA zorunlu olsun</span>
              </label>
              <label class="toggle">
                <input type="checkbox" v-model="settings.require_2fa_admin" />
                <span class="toggle-slider"></span>
              </label>
            </div>

            <div class="toggle-group">
              <label class="toggle-label">
                <span>E-posta Doğrulama</span>
                <span class="toggle-desc">Kayıt sonrası e-posta doğrulaması iste</span>
              </label>
              <label class="toggle">
                <input type="checkbox" v-model="settings.email_verification" />
                <span class="toggle-slider"></span>
              </label>
            </div>

            <div class="toggle-group">
              <label class="toggle-label">
                <span>Captcha</span>
                <span class="toggle-desc">Giriş ve kayıt formlarında captcha göster</span>
              </label>
              <label class="toggle">
                <input type="checkbox" v-model="settings.captcha_enabled" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <!-- Email Settings -->
          <div v-show="activeTab === 'email'" class="settings-section">
            <h2>E-posta Ayarları</h2>

            <div class="form-row">
              <div class="form-group">
                <label>SMTP Sunucu</label>
                <input v-model="settings.smtp_host" type="text" placeholder="smtp.gmail.com" />
              </div>
              <div class="form-group">
                <label>SMTP Port</label>
                <input v-model.number="settings.smtp_port" type="number" placeholder="587" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>SMTP Kullanıcı</label>
                <input v-model="settings.smtp_user" type="text" placeholder="email@domain.com" />
              </div>
              <div class="form-group">
                <label>SMTP Şifre</label>
                <input v-model="settings.smtp_password" type="password" placeholder="••••••••" />
              </div>
            </div>

            <div class="form-group">
              <label>Gönderen Adı</label>
              <input v-model="settings.email_from_name" type="text" placeholder="AGTR Merkezi" />
            </div>

            <div class="toggle-group">
              <label class="toggle-label">
                <span>TLS/SSL</span>
                <span class="toggle-desc">Güvenli bağlantı kullan</span>
              </label>
              <label class="toggle">
                <input type="checkbox" v-model="settings.smtp_tls" />
                <span class="toggle-slider"></span>
              </label>
            </div>

            <button class="btn btn-secondary" @click="testEmail">
              <Mail :size="16" />
              Test E-posta Gönder
            </button>
          </div>

          <!-- Save Button -->
          <div class="settings-footer">
            <button class="btn btn-primary" @click="saveSettings" :disabled="saving">
              <Loader2 v-if="saving" :size="16" class="spin" />
              <Save v-else :size="16" />
              <span>Kaydet</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'
import {
  Settings,
  CreditCard,
  Server,
  Shield,
  Mail,
  Save,
  Loader2
} from 'lucide-vue-next'

const authStore = useAuthStore()
const activeTab = ref('general')
const saving = ref(false)

const getHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${authStore.token}`
})

const tabs = [
  { id: 'general', label: 'Genel', icon: Settings },
  { id: 'payments', label: 'Ödemeler', icon: CreditCard },
  { id: 'servers', label: 'Sunucular', icon: Server },
  { id: 'security', label: 'Güvenlik', icon: Shield },
  { id: 'email', label: 'E-posta', icon: Mail }
]

const settings = reactive({
  // General
  site_name: 'AGTR Merkezi',
  site_description: '',
  logo_url: '',
  favicon_url: '',
  discord_url: '',
  support_email: '',
  maintenance_mode: false,
  registration_enabled: true,

  // Payments
  bank_info: '',
  papara_number: '',
  btc_address: '',
  min_deposit: 10,
  auto_approve_payments: false,

  // Servers
  default_slots: 12,
  max_slots: 32,
  default_ram: 512,
  max_ram: 2048,
  query_interval: 60,
  rcon_enabled: true,
  ftp_enabled: true,

  // Security
  session_timeout: 60,
  max_login_attempts: 5,
  ban_duration: 30,
  require_2fa_admin: false,
  email_verification: true,
  captcha_enabled: false,

  // Email
  smtp_host: '',
  smtp_port: 587,
  smtp_user: '',
  smtp_password: '',
  email_from_name: '',
  smtp_tls: true
})

const fetchSettings = async () => {
  try {
    const response = await fetch('/api/admin/settings', {
      headers: getHeaders()
    })
    if (response.ok) {
      const data = await response.json()
      Object.assign(settings, data)
    }
  } catch (error) {
    console.error('Fetch settings error:', error)
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    const response = await fetch('/api/admin/settings', {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(settings)
    })

    if (response.ok) {
      alert('Ayarlar kaydedildi')
    } else {
      const data = await response.json()
      alert(data.detail || 'Kaydetme başarısız')
    }
  } catch (error) {
    console.error('Save settings error:', error)
    alert('Bir hata oluştu')
  }
  saving.value = false
}

const testEmail = async () => {
  try {
    const response = await fetch('/api/admin/settings/test-email', {
      method: 'POST',
      headers: getHeaders()
    })

    if (response.ok) {
      alert('Test e-postası gönderildi')
    } else {
      alert('E-posta gönderilemedi')
    }
  } catch (error) {
    console.error('Test email error:', error)
    alert('Bir hata oluştu')
  }
}

onMounted(() => {
  fetchSettings()
})
</script>

<style scoped>
.admin-settings {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.subtitle {
  color: var(--text-secondary);
  margin: 4px 0 0;
}

.settings-layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 32px;
}

/* Navigation */
.settings-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: none;
  border: none;
  border-radius: 10px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.nav-item:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.nav-item.active {
  background: rgba(255, 107, 0, 0.15);
  color: var(--primary-color);
}

/* Content */
.settings-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 32px;
}

.settings-section h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

/* Form */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
}

.form-group textarea {
  resize: vertical;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

/* Toggle Group */
.toggle-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color);
}

.toggle-group:last-of-type {
  border-bottom: none;
}

.toggle-label {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.toggle-label span:first-child {
  font-weight: 500;
  color: var(--text-primary);
}

.toggle-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.toggle {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
  flex-shrink: 0;
}

.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background: var(--bg-tertiary);
  border-radius: 26px;
  transition: 0.3s;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  left: 3px;
  bottom: 3px;
  background: white;
  border-radius: 50%;
  transition: 0.3s;
}

.toggle input:checked + .toggle-slider {
  background: var(--primary-color);
}

.toggle input:checked + .toggle-slider::before {
  transform: translateX(22px);
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: var(--primary-color);
  color: var(--bg-primary);
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn:hover {
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Footer */
.settings-footer {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .settings-layout {
    grid-template-columns: 1fr;
  }

  .settings-nav {
    flex-direction: row;
    overflow-x: auto;
    padding-bottom: 8px;
  }

  .nav-item {
    white-space: nowrap;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
