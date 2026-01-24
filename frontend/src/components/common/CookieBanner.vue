<template>
  <Teleport to="body">
    <Transition name="cookie-slide">
      <div v-if="showBanner" class="cookie-banner-overlay">
        <div class="cookie-banner" :class="{ 'show-details': showDetails }">
          <!-- Ana Banner -->
          <div class="cookie-main">
            <div class="cookie-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <circle cx="8" cy="9" r="1" fill="currentColor"/>
                <circle cx="15" cy="8" r="1" fill="currentColor"/>
                <circle cx="10" cy="14" r="1" fill="currentColor"/>
                <circle cx="16" cy="13" r="1" fill="currentColor"/>
                <circle cx="12" cy="11" r="1" fill="currentColor"/>
              </svg>
            </div>

            <div class="cookie-content">
              <h3>Cerez Politikasi</h3>
              <p>
                Bu web sitesi, deneyiminizi iyilestirmek icin cerezler kullanmaktadir.
                Zorunlu cerezler site islevleri icin gereklidir.
                <button class="link-btn" @click="showDetails = true">Detayli bilgi</button>
              </p>
            </div>

            <div class="cookie-actions">
              <button class="btn btn-ghost" @click="handleNecessaryOnly">
                Sadece Zorunlu
              </button>
              <button class="btn btn-ghost" @click="showDetails = true">
                Ayarlar
              </button>
              <button class="btn btn-primary" @click="handleAcceptAll">
                Tumunu Kabul Et
              </button>
            </div>
          </div>

          <!-- Detayli Ayarlar -->
          <Transition name="details-slide">
            <div v-if="showDetails" class="cookie-details">
              <div class="details-header">
                <h4>Cerez Tercihleriniz</h4>
                <button class="close-btn" @click="showDetails = false">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>

              <div class="cookie-categories">
                <!-- Zorunlu Cerezler -->
                <div class="category">
                  <div class="category-header">
                    <div class="category-info">
                      <span class="category-name">Zorunlu Cerezler</span>
                      <span class="category-badge required">Gerekli</span>
                    </div>
                    <label class="toggle disabled">
                      <input type="checkbox" checked disabled />
                      <span class="slider"></span>
                    </label>
                  </div>
                  <p class="category-desc">
                    Bu cerezler sitenin duzgun calismasi icin gereklidir. Oturum yonetimi,
                    guvenlik (CSRF korumasi) ve temel site islevleri icin kullanilir.
                  </p>
                </div>

                <!-- Tercih Cerezleri -->
                <div class="category">
                  <div class="category-header">
                    <div class="category-info">
                      <span class="category-name">Tercih Cerezleri</span>
                    </div>
                    <label class="toggle">
                      <input
                        type="checkbox"
                        v-model="preferences.preferences"
                      />
                      <span class="slider"></span>
                    </label>
                  </div>
                  <p class="category-desc">
                    Tema tercihi (karanlik/acik mod), dil secimi ve diger kisisellestirilmis
                    ayarlarinizi hatirlamak icin kullanilir.
                  </p>
                </div>

                <!-- Analitik Cerezleri -->
                <div class="category">
                  <div class="category-header">
                    <div class="category-info">
                      <span class="category-name">Analitik Cerezleri</span>
                    </div>
                    <label class="toggle">
                      <input
                        type="checkbox"
                        v-model="preferences.analytics"
                      />
                      <span class="slider"></span>
                    </label>
                  </div>
                  <p class="category-desc">
                    Ziyaretci istatistiklerini toplamak ve site performansini olcmek icin
                    kullanilir. Kisisel bilgi icermez.
                  </p>
                </div>

                <!-- Pazarlama Cerezleri -->
                <div class="category">
                  <div class="category-header">
                    <div class="category-info">
                      <span class="category-name">Pazarlama Cerezleri</span>
                    </div>
                    <label class="toggle">
                      <input
                        type="checkbox"
                        v-model="preferences.marketing"
                      />
                      <span class="slider"></span>
                    </label>
                  </div>
                  <p class="category-desc">
                    Ilgi alanlariniza gore kisisellestirilmis icerik ve reklamlar
                    gostermek icin kullanilir.
                  </p>
                </div>
              </div>

              <div class="details-footer">
                <router-link to="/gizlilik-politikasi" class="privacy-link">
                  Gizlilik Politikasi
                </router-link>
                <div class="details-actions">
                  <button class="btn btn-ghost" @click="handleNecessaryOnly">
                    Sadece Zorunlu
                  </button>
                  <button class="btn btn-primary" @click="handleSavePreferences">
                    Tercihleri Kaydet
                  </button>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useCookies, COOKIE_CATEGORIES } from '@/composables/useCookies'

const {
  showBanner,
  acceptAll,
  acceptNecessaryOnly,
  saveConsent
} = useCookies()

const showDetails = ref(false)

const preferences = reactive({
  preferences: false,
  analytics: false,
  marketing: false
})

function handleAcceptAll() {
  acceptAll()
  showDetails.value = false
}

function handleNecessaryOnly() {
  acceptNecessaryOnly()
  showDetails.value = false
}

function handleSavePreferences() {
  saveConsent({
    [COOKIE_CATEGORIES.NECESSARY]: true,
    [COOKIE_CATEGORIES.PREFERENCES]: preferences.preferences,
    [COOKIE_CATEGORIES.ANALYTICS]: preferences.analytics,
    [COOKIE_CATEGORIES.MARKETING]: preferences.marketing
  })
  showDetails.value = false
}
</script>

<style scoped>
.cookie-banner-overlay {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  padding: 16px;
  pointer-events: none;
}

.cookie-banner {
  max-width: 900px;
  margin: 0 auto;
  background: var(--card-bg, rgba(30, 30, 35, 0.98));
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  border-radius: 16px;
  box-shadow: 0 -4px 30px rgba(0, 0, 0, 0.3);
  pointer-events: auto;
  overflow: hidden;
}

.cookie-main {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
}

.cookie-icon {
  flex-shrink: 0;
  color: #f97316;
}

.cookie-content {
  flex: 1;
}

.cookie-content h3 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary, #fff);
  margin: 0 0 4px 0;
}

.cookie-content p {
  font-size: 14px;
  color: var(--text-secondary, #9ca3af);
  margin: 0;
  line-height: 1.5;
}

.link-btn {
  background: none;
  border: none;
  color: #f97316;
  cursor: pointer;
  text-decoration: underline;
  font-size: 14px;
  padding: 0;
}

.link-btn:hover {
  color: #fb923c;
}

.cookie-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-primary {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: #fff;
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #fb923c, #f97316);
  transform: translateY(-1px);
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary, #9ca3af);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary, #fff);
  border-color: rgba(255, 255, 255, 0.2);
}

/* Detayli Ayarlar */
.cookie-details {
  border-top: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  padding: 20px 24px;
  background: rgba(0, 0, 0, 0.2);
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.details-header h4 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary, #fff);
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary, #9ca3af);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary, #fff);
}

.cookie-categories {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.08));
  border-radius: 12px;
  padding: 16px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.category-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #fff);
}

.category-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.category-badge.required {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.category-desc {
  font-size: 13px;
  color: var(--text-secondary, #9ca3af);
  margin: 0;
  line-height: 1.5;
}

/* Toggle Switch */
.toggle {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.toggle.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  transition: 0.3s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  border-radius: 50%;
  transition: 0.3s;
}

.toggle input:checked + .slider {
  background: linear-gradient(135deg, #f97316, #ea580c);
}

.toggle input:checked + .slider:before {
  transform: translateX(20px);
}

.toggle.disabled .slider {
  cursor: not-allowed;
}

/* Footer */
.details-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color, rgba(255, 255, 255, 0.08));
}

.privacy-link {
  color: #f97316;
  font-size: 14px;
  text-decoration: none;
}

.privacy-link:hover {
  text-decoration: underline;
}

.details-actions {
  display: flex;
  gap: 8px;
}

/* Animations */
.cookie-slide-enter-active {
  animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.cookie-slide-leave-active {
  animation: slideDown 0.3s cubic-bezier(0.7, 0, 0.84, 0);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(100%);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideDown {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(100%);
  }
}

.details-slide-enter-active {
  animation: expandDown 0.3s ease-out;
}

.details-slide-leave-active {
  animation: collapseUp 0.2s ease-in;
}

@keyframes expandDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 500px;
  }
}

@keyframes collapseUp {
  from {
    opacity: 1;
    max-height: 500px;
  }
  to {
    opacity: 0;
    max-height: 0;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .cookie-banner-overlay {
    padding: 8px;
  }

  .cookie-main {
    flex-direction: column;
    text-align: center;
    padding: 16px;
  }

  .cookie-actions {
    flex-direction: column;
    width: 100%;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .details-footer {
    flex-direction: column;
    gap: 16px;
  }

  .details-actions {
    width: 100%;
    flex-direction: column;
  }
}
</style>
