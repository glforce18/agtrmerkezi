<template>
  <div class="profile-customizer">
    <!-- Header -->
    <div class="customizer-header">
      <h3>
        <Palette class="w-5 h-5" />
        Profil Özelleştir
      </h3>
      <p>Profilini kişiselleştir ve öne çık!</p>
    </div>

    <!-- Preview -->
    <div class="preview-section">
      <div
        class="profile-preview"
        :style="previewStyle"
      >
        <div class="preview-banner" :style="bannerStyle">
          <div v-if="customization.banner_pattern" class="banner-pattern" :class="customization.banner_pattern"></div>
        </div>

        <div class="preview-content">
          <div class="preview-avatar" :style="avatarStyle">
            <n-avatar :size="80" :src="user?.avatar" round>
              {{ user?.username?.charAt(0).toUpperCase() }}
            </n-avatar>
            <div v-if="customization.avatar_frame" class="avatar-frame" :class="customization.avatar_frame"></div>
          </div>

          <div class="preview-info">
            <h4 :style="{ color: customization.name_color || 'inherit' }">
              {{ user?.username || 'Kullanıcı Adı' }}
              <span v-if="customization.name_badge" class="name-badge">{{ customization.name_badge }}</span>
            </h4>
            <p :style="{ color: customization.bio_color || 'inherit' }">
              {{ user?.bio || 'Biyografi metni buraya gelecek...' }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="customizer-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <component :is="tab.icon" class="w-4 h-4" />
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="customizer-content">
      <!-- Colors Tab -->
      <div v-if="activeTab === 'colors'" class="tab-panel">
        <div class="option-group">
          <label>Banner Rengi</label>
          <div class="color-palette">
            <button
              v-for="color in bannerColors"
              :key="color"
              class="color-swatch"
              :style="{ background: color }"
              :class="{ active: customization.banner_color === color }"
              @click="customization.banner_color = color"
            ></button>
            <n-color-picker
              v-model:value="customization.banner_color"
              :show-alpha="false"
              size="small"
            >
              <template #label>
                <button class="color-swatch custom">
                  <Plus class="w-4 h-4" />
                </button>
              </template>
            </n-color-picker>
          </div>
        </div>

        <div class="option-group">
          <label>İsim Rengi</label>
          <div class="color-palette">
            <button
              v-for="color in nameColors"
              :key="color"
              class="color-swatch"
              :style="{ background: color }"
              :class="{ active: customization.name_color === color }"
              @click="customization.name_color = color"
            ></button>
            <n-color-picker
              v-model:value="customization.name_color"
              :show-alpha="false"
              size="small"
            >
              <template #label>
                <button class="color-swatch custom">
                  <Plus class="w-4 h-4" />
                </button>
              </template>
            </n-color-picker>
          </div>
        </div>

        <div class="option-group">
          <label>Profil Kartı Arka Planı</label>
          <div class="color-palette">
            <button
              v-for="color in cardColors"
              :key="color"
              class="color-swatch large"
              :style="{ background: color }"
              :class="{ active: customization.card_color === color }"
              @click="customization.card_color = color"
            ></button>
          </div>
        </div>
      </div>

      <!-- Frames Tab -->
      <div v-if="activeTab === 'frames'" class="tab-panel">
        <div class="option-group">
          <label>Avatar Çerçevesi</label>
          <div class="frame-grid">
            <div
              v-for="frame in avatarFrames"
              :key="frame.id"
              class="frame-item"
              :class="{
                active: customization.avatar_frame === frame.id,
                locked: frame.locked
              }"
              @click="!frame.locked && (customization.avatar_frame = frame.id)"
            >
              <div class="frame-preview" :class="frame.id">
                <div class="frame-inner"></div>
              </div>
              <span class="frame-name">{{ frame.name }}</span>
              <Lock v-if="frame.locked" class="w-4 h-4 lock-icon" />
              <span v-if="frame.locked" class="frame-requirement">{{ frame.requirement }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Patterns Tab -->
      <div v-if="activeTab === 'patterns'" class="tab-panel">
        <div class="option-group">
          <label>Banner Deseni</label>
          <div class="pattern-grid">
            <div
              v-for="pattern in bannerPatterns"
              :key="pattern.id"
              class="pattern-item"
              :class="{
                active: customization.banner_pattern === pattern.id,
                locked: pattern.locked
              }"
              @click="!pattern.locked && (customization.banner_pattern = pattern.id)"
            >
              <div class="pattern-preview" :class="pattern.id"></div>
              <span class="pattern-name">{{ pattern.name }}</span>
              <Lock v-if="pattern.locked" class="w-3 h-3 lock-icon" />
            </div>
          </div>
        </div>
      </div>

      <!-- Badges Tab -->
      <div v-if="activeTab === 'badges'" class="tab-panel">
        <div class="option-group">
          <label>İsim Rozeti</label>
          <div class="badge-grid">
            <div
              v-for="badge in nameBadges"
              :key="badge.id"
              class="badge-item"
              :class="{
                active: customization.name_badge === badge.emoji,
                locked: badge.locked
              }"
              @click="!badge.locked && (customization.name_badge = customization.name_badge === badge.emoji ? null : badge.emoji)"
            >
              <span class="badge-emoji">{{ badge.emoji }}</span>
              <span class="badge-name">{{ badge.name }}</span>
              <Lock v-if="badge.locked" class="w-3 h-3 lock-icon" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="customizer-actions">
      <n-button @click="resetToDefault">
        Varsayılana Dön
      </n-button>
      <n-button type="primary" @click="saveCustomization" :loading="saving">
        <template #icon><Save class="w-4 h-4" /></template>
        Kaydet
      </n-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { Palette, Paintbrush, Frame, Sparkles, Award, Save, Plus, Lock } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const props = defineProps({
  user: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['saved'])

const message = useMessage()
const authStore = useAuthStore()

const saving = ref(false)
const activeTab = ref('colors')

// Customization state
const customization = reactive({
  banner_color: '#1e293b',
  banner_pattern: null,
  name_color: null,
  bio_color: null,
  card_color: null,
  avatar_frame: null,
  name_badge: null
})

// Tabs
const tabs = [
  { id: 'colors', label: 'Renkler', icon: Paintbrush },
  { id: 'frames', label: 'Çerçeveler', icon: Frame },
  { id: 'patterns', label: 'Desenler', icon: Sparkles },
  { id: 'badges', label: 'Rozetler', icon: Award }
]

// Color options
const bannerColors = [
  '#1e293b', '#0f172a', '#18181b',
  '#1e3a5f', '#1e3a8a', '#312e81',
  '#4c1d95', '#701a75', '#831843',
  '#7f1d1d', '#78350f', '#365314'
]

const nameColors = [
  '#f97316', '#ef4444', '#ec4899',
  '#8b5cf6', '#3b82f6', '#06b6d4',
  '#22c55e', '#eab308', '#f59e0b',
  '#ffffff', '#94a3b8', '#fbbf24'
]

const cardColors = [
  'rgba(30, 41, 59, 0.9)',
  'rgba(15, 23, 42, 0.9)',
  'rgba(30, 58, 95, 0.9)',
  'rgba(49, 46, 129, 0.9)',
  'rgba(76, 29, 149, 0.9)',
  'rgba(127, 29, 29, 0.9)'
]

// Avatar frames
const avatarFrames = [
  { id: 'none', name: 'Yok', locked: false },
  { id: 'gold', name: 'Altın', locked: false },
  { id: 'diamond', name: 'Elmas', locked: false },
  { id: 'fire', name: 'Ateş', locked: false },
  { id: 'neon', name: 'Neon', locked: true, requirement: 'VIP' },
  { id: 'rainbow', name: 'Gökkuşağı', locked: true, requirement: 'Lvl 50' },
  { id: 'legendary', name: 'Efsanevi', locked: true, requirement: 'Lvl 100' }
]

// Banner patterns
const bannerPatterns = [
  { id: 'none', name: 'Düz', locked: false },
  { id: 'diagonal', name: 'Çapraz Çizgi', locked: false },
  { id: 'dots', name: 'Noktalar', locked: false },
  { id: 'grid', name: 'Izgara', locked: false },
  { id: 'waves', name: 'Dalgalar', locked: true },
  { id: 'circuit', name: 'Devre', locked: true },
  { id: 'gaming', name: 'Gaming', locked: true }
]

// Name badges
const nameBadges = [
  { id: 'none', emoji: null, name: 'Yok', locked: false },
  { id: 'star', emoji: '⭐', name: 'Yıldız', locked: false },
  { id: 'fire', emoji: '🔥', name: 'Ateş', locked: false },
  { id: 'crown', emoji: '👑', name: 'Taç', locked: true },
  { id: 'diamond', emoji: '💎', name: 'Elmas', locked: true },
  { id: 'skull', emoji: '💀', name: 'Kurukafa', locked: false },
  { id: 'bolt', emoji: '⚡', name: 'Şimşek', locked: false },
  { id: 'verified', emoji: '✓', name: 'Onaylı', locked: true }
]

// Computed styles for preview
const previewStyle = computed(() => ({
  background: customization.card_color || 'var(--bg-secondary)'
}))

const bannerStyle = computed(() => ({
  background: customization.banner_color
}))

const avatarStyle = computed(() => ({
  '--frame-color': customization.name_color || '#f97316'
}))

// Methods
const loadCustomization = async () => {
  try {
    const response = await api.get('/profile/customization')
    const data = response.customization || response

    if (data) {
      Object.assign(customization, data)
    }
  } catch (e) {
    // Use defaults
  }
}

const saveCustomization = async () => {
  saving.value = true

  try {
    await api.put('/profile/customization', customization)
    message.success('Profil özelleştirmeleri kaydedildi!')
    emit('saved', { ...customization })
  } catch (e) {
    message.error('Kaydedilemedi: ' + (e.response?.data?.message || 'Bir hata oluştu'))
  } finally {
    saving.value = false
  }
}

const resetToDefault = () => {
  Object.assign(customization, {
    banner_color: '#1e293b',
    banner_pattern: null,
    name_color: null,
    bio_color: null,
    card_color: null,
    avatar_frame: null,
    name_badge: null
  })
}

onMounted(() => {
  loadCustomization()
})
</script>

<style scoped>
.profile-customizer {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
}

.customizer-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.customizer-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 4px;
  font-size: 18px;
  font-weight: 600;
}

.customizer-header p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
}

/* Preview */
.preview-section {
  padding: 20px;
  background: var(--bg-tertiary);
}

.profile-preview {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.preview-banner {
  position: relative;
  height: 80px;
  overflow: hidden;
}

.banner-pattern {
  position: absolute;
  inset: 0;
  opacity: 0.3;
}

.banner-pattern.diagonal {
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 10px,
    rgba(255, 255, 255, 0.1) 10px,
    rgba(255, 255, 255, 0.1) 20px
  );
}

.banner-pattern.dots {
  background-image: radial-gradient(circle, rgba(255, 255, 255, 0.2) 1px, transparent 1px);
  background-size: 20px 20px;
}

.banner-pattern.grid {
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
  background-size: 20px 20px;
}

.preview-content {
  padding: 0 20px 20px;
}

.preview-avatar {
  position: relative;
  width: 80px;
  margin: -40px auto 12px;
}

.avatar-frame {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  pointer-events: none;
}

.avatar-frame.gold {
  border: 3px solid #fbbf24;
  box-shadow: 0 0 10px rgba(251, 191, 36, 0.5);
}

.avatar-frame.diamond {
  border: 3px solid #06b6d4;
  box-shadow: 0 0 10px rgba(6, 182, 212, 0.5);
}

.avatar-frame.fire {
  border: 3px solid #ef4444;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
  animation: pulse 2s infinite;
}

.avatar-frame.neon {
  border: 3px solid var(--frame-color);
  box-shadow: 0 0 15px var(--frame-color);
}

.avatar-frame.rainbow {
  background: linear-gradient(45deg, #f97316, #ec4899, #8b5cf6, #3b82f6, #22c55e);
  padding: 3px;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: exclude;
  mask-composite: exclude;
}

.preview-info {
  text-align: center;
}

.preview-info h4 {
  margin: 0 0 4px;
  font-size: 18px;
  font-weight: 600;
}

.name-badge {
  margin-left: 4px;
}

.preview-info p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
}

/* Tabs */
.customizer-tabs {
  display: flex;
  padding: 8px 20px;
  gap: 8px;
  border-bottom: 1px solid var(--border-color);
  overflow-x: auto;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.tab-btn:hover {
  background: var(--bg-secondary);
}

.tab-btn.active {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

/* Content */
.customizer-content {
  padding: 20px;
  min-height: 200px;
}

.tab-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-group label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.color-palette {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.color-swatch {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.color-swatch:hover {
  transform: scale(1.1);
}

.color-swatch.active {
  border-color: white;
  box-shadow: 0 0 0 2px #f97316;
}

.color-swatch.large {
  width: 60px;
  height: 36px;
}

.color-swatch.custom {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 2px dashed var(--border-color);
  color: var(--text-tertiary);
}

/* Frames Grid */
.frame-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
}

.frame-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: var(--bg-tertiary);
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.frame-item:hover:not(.locked) {
  background: var(--bg-secondary);
}

.frame-item.active {
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.1);
}

.frame-item.locked {
  opacity: 0.5;
  cursor: not-allowed;
}

.frame-preview {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: var(--bg-secondary);
}

.frame-preview.gold {
  border: 3px solid #fbbf24;
  box-shadow: 0 0 8px rgba(251, 191, 36, 0.5);
}

.frame-preview.diamond {
  border: 3px solid #06b6d4;
  box-shadow: 0 0 8px rgba(6, 182, 212, 0.5);
}

.frame-preview.fire {
  border: 3px solid #ef4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
}

.frame-preview.neon {
  border: 3px solid #f97316;
  box-shadow: 0 0 12px #f97316;
}

.frame-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--bg-primary);
}

.frame-name {
  font-size: 12px;
  color: var(--text-secondary);
}

.lock-icon {
  position: absolute;
  top: 8px;
  right: 8px;
  color: var(--text-tertiary);
}

.frame-requirement {
  font-size: 10px;
  color: #f97316;
}

/* Patterns Grid */
.pattern-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 12px;
}

.pattern-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--bg-tertiary);
  border: 2px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.pattern-item:hover:not(.locked) {
  background: var(--bg-secondary);
}

.pattern-item.active {
  border-color: #f97316;
}

.pattern-item.locked {
  opacity: 0.5;
  cursor: not-allowed;
}

.pattern-preview {
  width: 100%;
  height: 40px;
  border-radius: 6px;
  background: #1e293b;
}

.pattern-preview.diagonal {
  background: repeating-linear-gradient(
    45deg,
    #1e293b,
    #1e293b 5px,
    #334155 5px,
    #334155 10px
  );
}

.pattern-preview.dots {
  background-color: #1e293b;
  background-image: radial-gradient(#334155 2px, transparent 2px);
  background-size: 10px 10px;
}

.pattern-preview.grid {
  background-color: #1e293b;
  background-image:
    linear-gradient(#334155 1px, transparent 1px),
    linear-gradient(90deg, #334155 1px, transparent 1px);
  background-size: 10px 10px;
}

.pattern-name {
  font-size: 11px;
  color: var(--text-secondary);
}

/* Badges Grid */
.badge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
  gap: 12px;
}

.badge-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 12px;
  background: var(--bg-tertiary);
  border: 2px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.badge-item:hover:not(.locked) {
  background: var(--bg-secondary);
}

.badge-item.active {
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.1);
}

.badge-item.locked {
  opacity: 0.5;
  cursor: not-allowed;
}

.badge-emoji {
  font-size: 24px;
}

.badge-name {
  font-size: 11px;
  color: var(--text-secondary);
}

/* Actions */
.customizer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}

/* Animations */
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.5); }
  50% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.8); }
}
</style>
