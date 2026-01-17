<template>
  <AdminLayout>
    <div class="theme-management">
      <!-- Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Tema Ayarlari</h1>
          <p class="page-desc">Site renkleri, fontlar ve gorunumu ozelllestirin</p>
        </div>
        <button class="btn-primary" @click="saveTheme">
          <Save :size="18" />
          Kaydet
        </button>
      </div>

      <div class="theme-grid">
        <!-- Color Settings -->
        <div class="theme-section">
          <h2>Renkler</h2>
          <div class="color-grid">
            <div class="color-item">
              <label>Ana Renk (Primary)</label>
              <div class="color-input">
                <input type="color" v-model="theme.primaryColor" />
                <input type="text" v-model="theme.primaryColor" />
              </div>
            </div>
            <div class="color-item">
              <label>Ikincil Renk (Secondary)</label>
              <div class="color-input">
                <input type="color" v-model="theme.secondaryColor" />
                <input type="text" v-model="theme.secondaryColor" />
              </div>
            </div>
            <div class="color-item">
              <label>Aksent Rengi</label>
              <div class="color-input">
                <input type="color" v-model="theme.accentColor" />
                <input type="text" v-model="theme.accentColor" />
              </div>
            </div>
            <div class="color-item">
              <label>Basari Rengi</label>
              <div class="color-input">
                <input type="color" v-model="theme.successColor" />
                <input type="text" v-model="theme.successColor" />
              </div>
            </div>
            <div class="color-item">
              <label>Hata Rengi</label>
              <div class="color-input">
                <input type="color" v-model="theme.errorColor" />
                <input type="text" v-model="theme.errorColor" />
              </div>
            </div>
            <div class="color-item">
              <label>Uyari Rengi</label>
              <div class="color-input">
                <input type="color" v-model="theme.warningColor" />
                <input type="text" v-model="theme.warningColor" />
              </div>
            </div>
          </div>
        </div>

        <!-- Dark Theme Colors -->
        <div class="theme-section">
          <h2>Karanlik Tema</h2>
          <div class="color-grid">
            <div class="color-item">
              <label>Arkaplan (Primary)</label>
              <div class="color-input">
                <input type="color" v-model="theme.dark.bgPrimary" />
                <input type="text" v-model="theme.dark.bgPrimary" />
              </div>
            </div>
            <div class="color-item">
              <label>Arkaplan (Secondary)</label>
              <div class="color-input">
                <input type="color" v-model="theme.dark.bgSecondary" />
                <input type="text" v-model="theme.dark.bgSecondary" />
              </div>
            </div>
            <div class="color-item">
              <label>Yazi Rengi</label>
              <div class="color-input">
                <input type="color" v-model="theme.dark.textPrimary" />
                <input type="text" v-model="theme.dark.textPrimary" />
              </div>
            </div>
            <div class="color-item">
              <label>Border Rengi</label>
              <div class="color-input">
                <input type="color" v-model="theme.dark.borderColor" />
                <input type="text" v-model="theme.dark.borderColor" />
              </div>
            </div>
          </div>
        </div>

        <!-- Light Theme Colors -->
        <div class="theme-section">
          <h2>Acik Tema</h2>
          <div class="color-grid">
            <div class="color-item">
              <label>Arkaplan (Primary)</label>
              <div class="color-input">
                <input type="color" v-model="theme.light.bgPrimary" />
                <input type="text" v-model="theme.light.bgPrimary" />
              </div>
            </div>
            <div class="color-item">
              <label>Arkaplan (Secondary)</label>
              <div class="color-input">
                <input type="color" v-model="theme.light.bgSecondary" />
                <input type="text" v-model="theme.light.bgSecondary" />
              </div>
            </div>
            <div class="color-item">
              <label>Yazi Rengi</label>
              <div class="color-input">
                <input type="color" v-model="theme.light.textPrimary" />
                <input type="text" v-model="theme.light.textPrimary" />
              </div>
            </div>
            <div class="color-item">
              <label>Border Rengi</label>
              <div class="color-input">
                <input type="color" v-model="theme.light.borderColor" />
                <input type="text" v-model="theme.light.borderColor" />
              </div>
            </div>
          </div>
        </div>

        <!-- Preview -->
        <div class="theme-section preview-section">
          <h2>Onizleme</h2>
          <div class="preview-container" :style="previewStyle">
            <div class="preview-card">
              <h3>Ornek Kart</h3>
              <p>Bu bir ornek metin. Tema ayarlarinizin nasil gorunecegini buradan gorebilirsiniz.</p>
              <div class="preview-buttons">
                <button class="preview-btn primary">Ana Buton</button>
                <button class="preview-btn secondary">Ikincil Buton</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Typography -->
        <div class="theme-section">
          <h2>Tipografi</h2>
          <div class="typography-settings">
            <div class="form-group">
              <label>Ana Font</label>
              <select v-model="theme.fontPrimary">
                <option value="Inter">Inter</option>
                <option value="Roboto">Roboto</option>
                <option value="Poppins">Poppins</option>
                <option value="Nunito">Nunito</option>
                <option value="Open Sans">Open Sans</option>
              </select>
            </div>
            <div class="form-group">
              <label>Baslik Fontu</label>
              <select v-model="theme.fontDisplay">
                <option value="Orbitron">Orbitron</option>
                <option value="Rajdhani">Rajdhani</option>
                <option value="Audiowide">Audiowide</option>
                <option value="Quantico">Quantico</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Border Radius -->
        <div class="theme-section">
          <h2>Border Radius</h2>
          <div class="radius-settings">
            <div class="radius-item">
              <label>Small</label>
              <input type="range" v-model="theme.radiusSmall" min="0" max="20" />
              <span>{{ theme.radiusSmall }}px</span>
            </div>
            <div class="radius-item">
              <label>Medium</label>
              <input type="range" v-model="theme.radiusMedium" min="0" max="30" />
              <span>{{ theme.radiusMedium }}px</span>
            </div>
            <div class="radius-item">
              <label>Large</label>
              <input type="range" v-model="theme.radiusLarge" min="0" max="40" />
              <span>{{ theme.radiusLarge }}px</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Reset Button -->
      <div class="reset-section">
        <button class="btn-danger" @click="resetTheme">
          <RotateCcw :size="18" />
          Varsayilana Sifirla
        </button>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { Save, RotateCcw } from 'lucide-vue-next'

const theme = reactive({
  primaryColor: '#f97316',
  secondaryColor: '#8b5cf6',
  accentColor: '#06b6d4',
  successColor: '#10b981',
  errorColor: '#ef4444',
  warningColor: '#f59e0b',
  dark: {
    bgPrimary: '#0f172a',
    bgSecondary: '#1e293b',
    textPrimary: '#f8fafc',
    borderColor: '#475569'
  },
  light: {
    bgPrimary: '#ffffff',
    bgSecondary: '#f1f5f9',
    textPrimary: '#0f172a',
    borderColor: '#e2e8f0'
  },
  fontPrimary: 'Inter',
  fontDisplay: 'Orbitron',
  radiusSmall: 8,
  radiusMedium: 12,
  radiusLarge: 16
})

const previewStyle = computed(() => ({
  '--preview-bg': theme.dark.bgSecondary,
  '--preview-text': theme.dark.textPrimary,
  '--preview-border': theme.dark.borderColor,
  '--preview-primary': theme.primaryColor,
  '--preview-secondary': theme.secondaryColor,
  '--preview-radius': theme.radiusMedium + 'px'
}))

const saveTheme = async () => {
  try {
    const response = await fetch('/api/admin/theme', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(theme)
    })

    if (response.ok) {
      alert('Tema ayarlari kaydedildi!')
      // Apply theme changes
      applyTheme()
    }
  } catch (e) {
    console.error('Save error:', e)
  }
}

const resetTheme = () => {
  if (!confirm('Tema ayarlarini varsayilana sifirlamak istediginize emin misiniz?')) return

  Object.assign(theme, {
    primaryColor: '#f97316',
    secondaryColor: '#8b5cf6',
    accentColor: '#06b6d4',
    successColor: '#10b981',
    errorColor: '#ef4444',
    warningColor: '#f59e0b',
    dark: {
      bgPrimary: '#0f172a',
      bgSecondary: '#1e293b',
      textPrimary: '#f8fafc',
      borderColor: '#475569'
    },
    light: {
      bgPrimary: '#ffffff',
      bgSecondary: '#f1f5f9',
      textPrimary: '#0f172a',
      borderColor: '#e2e8f0'
    },
    fontPrimary: 'Inter',
    fontDisplay: 'Orbitron',
    radiusSmall: 8,
    radiusMedium: 12,
    radiusLarge: 16
  })
}

const applyTheme = () => {
  const root = document.documentElement
  root.style.setProperty('--primary-color', theme.primaryColor)
  root.style.setProperty('--secondary-color', theme.secondaryColor)
  root.style.setProperty('--accent-color', theme.accentColor)
}
</script>

<style scoped>
.theme-management {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.page-desc {
  color: var(--text-secondary);
  font-size: 14px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--gradient-primary);
  border: none;
  border-radius: 10px;
  color: var(--bg-primary);
  font-weight: 600;
  cursor: pointer;
}

.btn-danger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 10px;
  color: #ef4444;
  font-weight: 500;
  cursor: pointer;
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.theme-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
}

.theme-section h2 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.color-item label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.color-input {
  display: flex;
  gap: 8px;
}

.color-input input[type="color"] {
  width: 48px;
  height: 40px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  padding: 0;
}

.color-input input[type="text"] {
  flex: 1;
  padding: 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-family: monospace;
  font-size: 13px;
}

/* Preview */
.preview-section {
  grid-column: span 2;
}

.preview-container {
  background: var(--preview-bg);
  border-radius: var(--preview-radius);
  padding: 24px;
  border: 1px solid var(--preview-border);
}

.preview-card {
  background: var(--bg-tertiary);
  border-radius: var(--preview-radius);
  padding: 20px;
  border: 1px solid var(--preview-border);
}

.preview-card h3 {
  color: var(--preview-text);
  margin-bottom: 12px;
}

.preview-card p {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 16px;
}

.preview-buttons {
  display: flex;
  gap: 12px;
}

.preview-btn {
  padding: 10px 20px;
  border-radius: var(--preview-radius);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.preview-btn.primary {
  background: var(--preview-primary);
  border: none;
  color: var(--bg-primary);
}

.preview-btn.secondary {
  background: transparent;
  border: 1px solid var(--preview-border);
  color: var(--preview-text);
}

/* Typography */
.typography-settings {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.form-group select {
  width: 100%;
  padding: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
}

/* Radius */
.radius-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.radius-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.radius-item label {
  width: 80px;
  font-size: 13px;
  color: var(--text-secondary);
}

.radius-item input[type="range"] {
  flex: 1;
  accent-color: var(--primary-color);
}

.radius-item span {
  width: 50px;
  font-size: 13px;
  color: var(--text-primary);
  font-family: monospace;
}

.reset-section {
  text-align: center;
}

@media (max-width: 1024px) {
  .theme-grid {
    grid-template-columns: 1fr;
  }

  .preview-section {
    grid-column: span 1;
  }
}
</style>
