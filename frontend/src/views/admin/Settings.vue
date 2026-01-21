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

          <!-- Branding Settings -->
          <div v-show="activeTab === 'branding'" class="settings-section branding-section">
            <h2>Marka & Logo Ayarları</h2>
            <p class="section-desc">Site logolarını ve marka görünümünü buradan yönetin</p>

            <!-- Live Preview -->
            <div class="brand-preview-card">
              <div class="preview-header">
                <span class="preview-badge">Canlı Önizleme</span>
              </div>
              <div class="preview-navbar">
                <div class="preview-logo-area">
                  <img
                    v-if="settings.logo_url"
                    :src="settings.logo_url"
                    :style="{ height: (settings.logo_height || 36) + 'px', maxHeight: '40px' }"
                    alt="Logo"
                    @error="$event.target.style.display='none'"
                  />
                  <div v-if="settings.show_logo_text" class="preview-text-logo">
                    <span class="main-text" :style="{ color: settings.primary_color }">{{ settings.logo_text || 'AGTR' }}</span>
                    <span class="sub-text">{{ settings.logo_subtitle || 'MERKEZİ' }}</span>
                  </div>
                </div>
                <div class="preview-nav-links">
                  <span>Ana Sayfa</span>
                  <span>Sunucular</span>
                  <span>Forum</span>
                </div>
              </div>
            </div>

            <!-- Logo Cards Grid -->
            <div class="brand-cards-grid">
              <!-- Main Logo -->
              <div class="brand-card">
                <div class="brand-card-header">
                  <div class="brand-card-icon primary">
                    <Image :size="20" />
                  </div>
                  <div>
                    <h4>Ana Logo</h4>
                    <span>Navbar'da görünür</span>
                  </div>
                </div>
                <div
                  class="brand-upload-zone"
                  :class="{ 'has-image': settings.logo_url }"
                  @click="uploadLogo('logo')"
                  @dragover.prevent
                  @drop.prevent="handleLogoDrop($event, 'logo')"
                >
                  <img v-if="settings.logo_url" :src="settings.logo_url" alt="Logo" />
                  <div v-else class="upload-placeholder">
                    <Upload :size="24" />
                    <span>Tıkla veya sürükle</span>
                  </div>
                  <div class="upload-overlay">
                    <Upload :size="20" />
                    <span>Değiştir</span>
                  </div>
                </div>
                <div class="brand-card-footer">
                  <input v-model="settings.logo_url" type="text" placeholder="Logo URL" class="brand-url-input" />
                  <div class="brand-size-inputs">
                    <input v-model="settings.logo_width" type="text" placeholder="Genişlik" />
                    <span>×</span>
                    <input v-model="settings.logo_height" type="text" placeholder="Yükseklik" />
                  </div>
                </div>
              </div>

              <!-- Dark Theme Logo -->
              <div class="brand-card">
                <div class="brand-card-header">
                  <div class="brand-card-icon dark">
                    <Moon :size="20" />
                  </div>
                  <div>
                    <h4>Koyu Tema Logosu</h4>
                    <span>Dark mode için</span>
                  </div>
                </div>
                <div
                  class="brand-upload-zone dark-zone"
                  :class="{ 'has-image': settings.logo_dark_url }"
                  @click="uploadLogo('logo_dark')"
                >
                  <img v-if="settings.logo_dark_url" :src="settings.logo_dark_url" alt="Dark Logo" />
                  <div v-else class="upload-placeholder">
                    <Upload :size="24" />
                    <span>Opsiyonel</span>
                  </div>
                  <div class="upload-overlay">
                    <Upload :size="20" />
                    <span>Değiştir</span>
                  </div>
                </div>
                <div class="brand-card-footer">
                  <input v-model="settings.logo_dark_url" type="text" placeholder="Koyu tema logo URL" class="brand-url-input" />
                </div>
              </div>

              <!-- Mobile Logo -->
              <div class="brand-card">
                <div class="brand-card-header">
                  <div class="brand-card-icon mobile">
                    <Smartphone :size="20" />
                  </div>
                  <div>
                    <h4>Mobil Logo</h4>
                    <span>Küçük ekranlar için</span>
                  </div>
                </div>
                <div
                  class="brand-upload-zone"
                  :class="{ 'has-image': settings.logo_mobile_url }"
                  @click="uploadLogo('logo_mobile')"
                >
                  <img v-if="settings.logo_mobile_url" :src="settings.logo_mobile_url" alt="Mobile Logo" />
                  <div v-else class="upload-placeholder">
                    <Upload :size="24" />
                    <span>Opsiyonel</span>
                  </div>
                  <div class="upload-overlay">
                    <Upload :size="20" />
                    <span>Değiştir</span>
                  </div>
                </div>
                <div class="brand-card-footer">
                  <input v-model="settings.logo_mobile_url" type="text" placeholder="Mobil logo URL" class="brand-url-input" />
                </div>
              </div>

              <!-- Favicon -->
              <div class="brand-card">
                <div class="brand-card-header">
                  <div class="brand-card-icon favicon">
                    <Star :size="20" />
                  </div>
                  <div>
                    <h4>Favicon</h4>
                    <span>Tarayıcı sekmesi ikonu</span>
                  </div>
                </div>
                <div
                  class="brand-upload-zone favicon-zone"
                  :class="{ 'has-image': settings.favicon_url }"
                  @click="uploadLogo('favicon')"
                >
                  <img v-if="settings.favicon_url" :src="settings.favicon_url" alt="Favicon" />
                  <div v-else class="upload-placeholder">
                    <Upload :size="24" />
                    <span>32x32 px</span>
                  </div>
                  <div class="upload-overlay">
                    <Upload :size="20" />
                    <span>Değiştir</span>
                  </div>
                </div>
                <div class="brand-card-footer">
                  <input v-model="settings.favicon_url" type="text" placeholder="Favicon URL" class="brand-url-input" />
                </div>
              </div>

              <!-- Footer Logo -->
              <div class="brand-card wide">
                <div class="brand-card-header">
                  <div class="brand-card-icon footer">
                    <Layout :size="20" />
                  </div>
                  <div>
                    <h4>Footer Logo</h4>
                    <span>Sayfa altında görünür</span>
                  </div>
                </div>
                <div
                  class="brand-upload-zone footer-zone"
                  :class="{ 'has-image': settings.footer_logo_url }"
                  @click="uploadLogo('footer_logo')"
                >
                  <img v-if="settings.footer_logo_url" :src="settings.footer_logo_url" alt="Footer Logo" />
                  <div v-else class="upload-placeholder">
                    <Upload :size="24" />
                    <span>Opsiyonel - Ana logo kullanılır</span>
                  </div>
                  <div class="upload-overlay">
                    <Upload :size="20" />
                    <span>Değiştir</span>
                  </div>
                </div>
                <div class="brand-card-footer">
                  <input v-model="settings.footer_logo_url" type="text" placeholder="Footer logo URL" class="brand-url-input" />
                  <div class="brand-size-inputs">
                    <input v-model="settings.footer_logo_width" type="text" placeholder="Genişlik" />
                    <span>×</span>
                    <input v-model="settings.footer_logo_height" type="text" placeholder="Yükseklik" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Text Logo Section -->
            <div class="brand-text-section">
              <div class="section-header">
                <div>
                  <h3>Yazılı Logo</h3>
                  <p>Logo yerine veya yanında metin göster</p>
                </div>
                <label class="toggle">
                  <input type="checkbox" v-model="settings.show_logo_text" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
              <div v-if="settings.show_logo_text" class="text-logo-config">
                <div class="text-logo-preview" :style="{ '--primary': settings.primary_color }">
                  <span class="main">{{ settings.logo_text || 'AGTR' }}</span>
                  <span class="sub">{{ settings.logo_subtitle || 'MERKEZİ' }}</span>
                </div>
                <div class="text-logo-inputs">
                  <div class="form-group">
                    <label>Ana Yazı</label>
                    <input v-model="settings.logo_text" type="text" placeholder="AGTR" />
                  </div>
                  <div class="form-group">
                    <label>Alt Yazı</label>
                    <input v-model="settings.logo_subtitle" type="text" placeholder="MERKEZİ" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Colors Section -->
            <div class="brand-colors-section">
              <h3>Marka Renkleri</h3>
              <p>Sitenin ana renk şemasını belirleyin</p>
              <div class="color-cards">
                <div class="color-card">
                  <div class="color-preview" :style="{ backgroundColor: settings.primary_color }"></div>
                  <div class="color-info">
                    <label>Ana Renk (Primary)</label>
                    <div class="color-input-group">
                      <input type="color" v-model="settings.primary_color" />
                      <input type="text" v-model="settings.primary_color" placeholder="#f97316" />
                    </div>
                  </div>
                </div>
                <div class="color-card">
                  <div class="color-preview" :style="{ backgroundColor: settings.secondary_color }"></div>
                  <div class="color-info">
                    <label>İkincil Renk (Secondary)</label>
                    <div class="color-input-group">
                      <input type="color" v-model="settings.secondary_color" />
                      <input type="text" v-model="settings.secondary_color" placeholder="#3b82f6" />
                    </div>
                  </div>
                </div>
              </div>
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
  Loader2,
  Palette,
  Upload,
  Image,
  Eye,
  Trash2,
  Moon,
  Smartphone,
  Star,
  Layout
} from 'lucide-vue-next'

const authStore = useAuthStore()
const activeTab = ref('general')
const saving = ref(false)

// Get CSRF token from cookie
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
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken
  }
  return headers
}

const tabs = [
  { id: 'general', label: 'Genel', icon: Settings },
  { id: 'branding', label: 'Marka/Logo', icon: Palette },
  { id: 'payments', label: 'Ödemeler', icon: CreditCard },
  { id: 'servers', label: 'Sunucular', icon: Server },
  { id: 'security', label: 'Güvenlik', icon: Shield },
  { id: 'email', label: 'E-posta', icon: Mail }
]

const settings = reactive({
  // General
  site_name: 'AGTR Merkezi',
  site_description: '',
  discord_url: '',
  support_email: '',
  maintenance_mode: false,
  registration_enabled: true,

  // Branding
  logo_url: '/logo-navbar.png',
  logo_dark_url: '',
  logo_mobile_url: '',
  logo_width: 'auto',
  logo_height: '36',
  logo_text: 'AGTR',
  logo_subtitle: 'MERKEZİ',
  show_logo_text: false,
  footer_logo_url: '',
  footer_logo_width: 'auto',
  footer_logo_height: '48',
  favicon_url: '/favicon.ico',
  primary_color: '#f97316',
  secondary_color: '#3b82f6',

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

// Logo upload handler
const uploadLogo = async (type) => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = type === 'favicon' ? '.ico,.png,.svg' : 'image/*'

  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    // Map type to category for the API
    const categoryMap = {
      'logo': 'logos',
      'logo_dark': 'logos',
      'logo_mobile': 'logos',
      'footer_logo': 'logos',
      'favicon': 'icons'
    }
    formData.append('category', categoryMap[type] || 'general')

    try {
      const response = await fetch('/api/admin/media/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authStore.token}`
        },
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        const url = data.file_path || data.url
        // Update the corresponding setting
        if (type === 'logo') settings.logo_url = url
        else if (type === 'logo_dark') settings.logo_dark_url = url
        else if (type === 'logo_mobile') settings.logo_mobile_url = url
        else if (type === 'footer_logo') settings.footer_logo_url = url
        else if (type === 'favicon') settings.favicon_url = url

        alert('Yükleme başarılı!')
      } else {
        const errorData = await response.json().catch(() => ({}))
        alert(errorData.detail || 'Yükleme başarısız')
      }
    } catch (error) {
      console.error('Upload error:', error)
      alert('Yükleme sırasında hata oluştu')
    }
  }

  input.click()
}

// Drag and drop handler for logos
const handleLogoDrop = async (event, type) => {
  const files = event.dataTransfer.files
  if (!files || files.length === 0) return

  const file = files[0]
  if (!file.type.startsWith('image/')) {
    alert('Lütfen sadece resim dosyası yükleyin')
    return
  }

  const formData = new FormData()
  formData.append('file', file)

  const categoryMap = {
    'logo': 'logos',
    'logo_dark': 'logos',
    'logo_mobile': 'logos',
    'footer_logo': 'logos',
    'favicon': 'icons'
  }
  formData.append('category', categoryMap[type] || 'general')

  try {
    const response = await fetch('/api/admin/media/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      },
      body: formData
    })

    if (response.ok) {
      const data = await response.json()
      const url = data.file_path || data.url
      if (type === 'logo') settings.logo_url = url
      else if (type === 'logo_dark') settings.logo_dark_url = url
      else if (type === 'logo_mobile') settings.logo_mobile_url = url
      else if (type === 'footer_logo') settings.footer_logo_url = url
      else if (type === 'favicon') settings.favicon_url = url

      alert('Yükleme başarılı!')
    } else {
      const errorData = await response.json().catch(() => ({}))
      alert(errorData.detail || 'Yükleme başarısız')
    }
  } catch (error) {
    console.error('Upload error:', error)
    alert('Yükleme sırasında hata oluştu')
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

/* Branding Styles */
.settings-section h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 24px 0 16px;
}

.logo-preview-section {
  margin-bottom: 24px;
}

.logo-preview-section > label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.logo-preview-box {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80px;
  padding: 20px;
  background: var(--bg-tertiary);
  border: 2px dashed var(--border-color);
  border-radius: 12px;
}

.logo-preview-box img {
  object-fit: contain;
}

.logo-preview-box .no-logo {
  color: var(--text-secondary);
  font-size: 14px;
}

.input-with-action {
  display: flex;
  gap: 8px;
}

.input-with-action input {
  flex: 1;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.input-hint {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 6px;
}

.size-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.size-input input {
  flex: 1;
  width: auto;
}

.size-input .unit {
  color: var(--text-secondary);
  font-size: 13px;
}

.color-input {
  display: flex;
  gap: 12px;
  align-items: center;
}

.color-input input[type="color"] {
  width: 50px;
  height: 44px;
  padding: 4px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  cursor: pointer;
  background: var(--bg-tertiary);
}

.color-input input[type="text"] {
  flex: 1;
}

.divider {
  height: 1px;
  background: var(--border-color);
  margin: 24px 0;
}

.inline {
  display: inline-block;
  vertical-align: middle;
}

.mr-1 {
  margin-right: 4px;
}

/* New Branding Section Styles */
.branding-section .section-desc {
  color: var(--text-secondary);
  margin: -16px 0 24px;
  font-size: 14px;
}

.brand-preview-card {
  background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-primary) 100%);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 32px;
}

.preview-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.preview-badge {
  background: rgba(249, 115, 22, 0.15);
  color: var(--primary-color);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.preview-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: var(--bg-secondary);
}

.preview-logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.preview-logo-area img {
  max-height: 40px;
  object-fit: contain;
}

.preview-text-logo {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.preview-text-logo .main-text {
  font-weight: 800;
  font-size: 18px;
}

.preview-text-logo .sub-text {
  font-weight: 500;
  font-size: 14px;
  color: var(--text-secondary);
}

.preview-nav-links {
  display: flex;
  gap: 24px;
  color: var(--text-secondary);
  font-size: 14px;
}

/* Brand Cards Grid */
.brand-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.brand-card {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
}

.brand-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 20px rgba(249, 115, 22, 0.1);
}

.brand-card.wide {
  grid-column: span 2;
}

.brand-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.brand-card-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-card-icon.primary {
  background: rgba(249, 115, 22, 0.15);
  color: var(--primary-color);
}

.brand-card-icon.dark {
  background: rgba(99, 102, 241, 0.15);
  color: #818cf8;
}

.brand-card-icon.mobile {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.brand-card-icon.favicon {
  background: rgba(234, 179, 8, 0.15);
  color: #eab308;
}

.brand-card-icon.footer {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.brand-card-header h4 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.brand-card-header span {
  font-size: 12px;
  color: var(--text-secondary);
}

.brand-upload-zone {
  position: relative;
  height: 120px;
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  background: var(--bg-secondary);
}

.brand-upload-zone.dark-zone {
  background: #1a1a2e;
}

.brand-upload-zone.favicon-zone {
  height: 80px;
  width: 80px;
  margin: 0 auto;
}

.brand-upload-zone.footer-zone {
  height: 100px;
}

.brand-upload-zone:hover {
  border-color: var(--primary-color);
  background: rgba(249, 115, 22, 0.05);
}

.brand-upload-zone.has-image img {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
}

.upload-placeholder span {
  font-size: 12px;
}

.upload-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: white;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.upload-overlay span {
  font-size: 12px;
  font-weight: 500;
}

.brand-upload-zone:hover .upload-overlay {
  opacity: 1;
}

.brand-card-footer {
  margin-top: 16px;
}

.brand-url-input {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  margin-bottom: 10px;
}

.brand-url-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.brand-size-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-size-inputs input {
  flex: 1;
  padding: 8px 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 12px;
  text-align: center;
}

.brand-size-inputs input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.brand-size-inputs span {
  color: var(--text-secondary);
  font-size: 14px;
}

/* Text Logo Section */
.brand-text-section {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
}

.brand-text-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand-text-section .section-header h3 {
  margin: 0 0 4px;
  font-size: 16px;
}

.brand-text-section .section-header p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.text-logo-config {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.text-logo-preview {
  background: var(--bg-secondary);
  padding: 16px 24px;
  border-radius: 12px;
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 20px;
}

.text-logo-preview .main {
  font-weight: 800;
  font-size: 24px;
  color: var(--primary, #f97316);
}

.text-logo-preview .sub {
  font-weight: 600;
  font-size: 16px;
  color: var(--text-secondary);
}

.text-logo-inputs {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

/* Brand Colors Section */
.brand-colors-section {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
}

.brand-colors-section h3 {
  margin: 0 0 4px;
  font-size: 16px;
}

.brand-colors-section > p {
  margin: 0 0 20px;
  font-size: 13px;
  color: var(--text-secondary);
}

.color-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.color-card {
  display: flex;
  gap: 16px;
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.color-preview {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.color-info {
  flex: 1;
}

.color-info label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.color-input-group {
  display: flex;
  gap: 8px;
}

.color-input-group input[type="color"] {
  width: 40px;
  height: 36px;
  padding: 2px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  background: var(--bg-tertiary);
}

.color-input-group input[type="text"] {
  flex: 1;
  padding: 8px 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 13px;
  font-family: monospace;
}

.color-input-group input[type="text"]:focus {
  outline: none;
  border-color: var(--primary-color);
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

  /* Branding responsive */
  .brand-cards-grid {
    grid-template-columns: 1fr;
  }

  .brand-card.wide {
    grid-column: span 1;
  }

  .preview-navbar {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }

  .preview-nav-links {
    gap: 16px;
    font-size: 12px;
  }

  .text-logo-inputs {
    grid-template-columns: 1fr;
  }

  .color-cards {
    grid-template-columns: 1fr;
  }
}
</style>
