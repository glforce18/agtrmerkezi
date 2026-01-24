/**
 * AGTR Merkezi - Cookie Yönetim Composable
 * KVKK/GDPR uyumlu cookie yönetimi
 */

import { ref, computed, watch } from 'vue'

// Cookie kategorileri
export const COOKIE_CATEGORIES = {
  NECESSARY: 'necessary',      // Zorunlu (oturum, CSRF)
  PREFERENCES: 'preferences',  // Tercihler (tema, dil)
  ANALYTICS: 'analytics',      // Analitik (ziyaretçi istatistikleri)
  MARKETING: 'marketing'       // Pazarlama (reklam)
}

// Cookie isimleri
export const COOKIE_NAMES = {
  CONSENT: 'agtr_cookie_consent',
  THEME: 'agtr_theme',
  LANGUAGE: 'agtr_language',
  LAST_SERVER: 'agtr_last_server',
  REMEMBER_ME: 'agtr_remember_me',
  SIDEBAR_STATE: 'agtr_sidebar',
  VOLUME: 'agtr_volume'
}

// Cookie ayarları
const COOKIE_DEFAULTS = {
  path: '/',
  secure: true,
  sameSite: 'Lax'
}

// Consent state
const consentGiven = ref(false)
const consentCategories = ref({
  [COOKIE_CATEGORIES.NECESSARY]: true,    // Her zaman true
  [COOKIE_CATEGORIES.PREFERENCES]: false,
  [COOKIE_CATEGORIES.ANALYTICS]: false,
  [COOKIE_CATEGORIES.MARKETING]: false
})

// Banner visibility
const showBanner = ref(false)

/**
 * Cookie okuma
 */
function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    return decodeURIComponent(parts.pop().split(';').shift())
  }
  return null
}

/**
 * Cookie yazma
 */
function setCookie(name, value, options = {}) {
  const opts = { ...COOKIE_DEFAULTS, ...options }

  let cookieString = `${name}=${encodeURIComponent(value)}`

  if (opts.maxAge) {
    cookieString += `; max-age=${opts.maxAge}`
  } else if (opts.expires) {
    cookieString += `; expires=${opts.expires.toUTCString()}`
  }

  if (opts.path) {
    cookieString += `; path=${opts.path}`
  }

  if (opts.domain) {
    cookieString += `; domain=${opts.domain}`
  }

  if (opts.secure) {
    cookieString += '; secure'
  }

  if (opts.sameSite) {
    cookieString += `; samesite=${opts.sameSite}`
  }

  document.cookie = cookieString
}

/**
 * Cookie silme
 */
function deleteCookie(name, options = {}) {
  const opts = { ...COOKIE_DEFAULTS, ...options }
  document.cookie = `${name}=; max-age=0; path=${opts.path}`
}

/**
 * Consent durumunu yükle
 */
function loadConsent() {
  const saved = getCookie(COOKIE_NAMES.CONSENT)

  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      consentGiven.value = true
      consentCategories.value = {
        ...consentCategories.value,
        ...parsed
      }
      showBanner.value = false
    } catch {
      showBanner.value = true
    }
  } else {
    showBanner.value = true
  }
}

/**
 * Consent kaydet
 */
function saveConsent(categories) {
  consentCategories.value = {
    [COOKIE_CATEGORIES.NECESSARY]: true, // Her zaman true
    ...categories
  }
  consentGiven.value = true
  showBanner.value = false

  // Consent cookie'sini kaydet (1 yıl)
  setCookie(COOKIE_NAMES.CONSENT, JSON.stringify(consentCategories.value), {
    maxAge: 365 * 24 * 60 * 60
  })
}

/**
 * Tümünü kabul et
 */
function acceptAll() {
  saveConsent({
    [COOKIE_CATEGORIES.NECESSARY]: true,
    [COOKIE_CATEGORIES.PREFERENCES]: true,
    [COOKIE_CATEGORIES.ANALYTICS]: true,
    [COOKIE_CATEGORIES.MARKETING]: true
  })
}

/**
 * Sadece zorunlu
 */
function acceptNecessaryOnly() {
  saveConsent({
    [COOKIE_CATEGORIES.NECESSARY]: true,
    [COOKIE_CATEGORIES.PREFERENCES]: false,
    [COOKIE_CATEGORIES.ANALYTICS]: false,
    [COOKIE_CATEGORIES.MARKETING]: false
  })
}

/**
 * Kategori izni kontrol
 */
function hasConsent(category) {
  if (category === COOKIE_CATEGORIES.NECESSARY) {
    return true
  }
  return consentCategories.value[category] === true
}

/**
 * Tercih cookie'si kaydet (tema, dil vb.)
 */
function setPreferenceCookie(name, value, maxAgeDays = 365) {
  if (!hasConsent(COOKIE_CATEGORIES.PREFERENCES)) {
    // Consent yoksa localStorage'a kaydet
    localStorage.setItem(name, value)
    return
  }

  setCookie(name, value, {
    maxAge: maxAgeDays * 24 * 60 * 60
  })
}

/**
 * Tercih cookie'si oku
 */
function getPreferenceCookie(name) {
  // Önce cookie'den, yoksa localStorage'dan
  return getCookie(name) || localStorage.getItem(name)
}

/**
 * Tema tercihini kaydet
 */
function setThemePreference(theme) {
  setPreferenceCookie(COOKIE_NAMES.THEME, theme)
}

/**
 * Tema tercihini oku
 */
function getThemePreference() {
  return getPreferenceCookie(COOKIE_NAMES.THEME)
}

/**
 * Dil tercihini kaydet
 */
function setLanguagePreference(lang) {
  setPreferenceCookie(COOKIE_NAMES.LANGUAGE, lang)
}

/**
 * Dil tercihini oku
 */
function getLanguagePreference() {
  return getPreferenceCookie(COOKIE_NAMES.LANGUAGE) || 'tr'
}

/**
 * Son görüntülenen sunucuyu kaydet
 */
function setLastServer(serverId) {
  setPreferenceCookie(COOKIE_NAMES.LAST_SERVER, serverId, 30)
}

/**
 * Son görüntülenen sunucuyu oku
 */
function getLastServer() {
  return getPreferenceCookie(COOKIE_NAMES.LAST_SERVER)
}

/**
 * Beni hatırla tercihini kaydet
 */
function setRememberMe(value) {
  if (value) {
    setPreferenceCookie(COOKIE_NAMES.REMEMBER_ME, 'true', 30)
  } else {
    deleteCookie(COOKIE_NAMES.REMEMBER_ME)
    localStorage.removeItem(COOKIE_NAMES.REMEMBER_ME)
  }
}

/**
 * Beni hatırla tercihini oku
 */
function getRememberMe() {
  return getPreferenceCookie(COOKIE_NAMES.REMEMBER_ME) === 'true'
}

/**
 * Sidebar durumunu kaydet
 */
function setSidebarState(collapsed) {
  setPreferenceCookie(COOKIE_NAMES.SIDEBAR_STATE, collapsed ? 'collapsed' : 'expanded', 365)
}

/**
 * Sidebar durumunu oku
 */
function getSidebarState() {
  return getPreferenceCookie(COOKIE_NAMES.SIDEBAR_STATE) === 'collapsed'
}

/**
 * Ses seviyesini kaydet
 */
function setVolumePreference(volume) {
  setPreferenceCookie(COOKIE_NAMES.VOLUME, String(volume), 365)
}

/**
 * Ses seviyesini oku
 */
function getVolumePreference() {
  const vol = getPreferenceCookie(COOKIE_NAMES.VOLUME)
  return vol !== null ? parseFloat(vol) : 0.5
}

/**
 * Tüm cookie'leri temizle (zorunlu hariç)
 */
function clearAllCookies() {
  Object.values(COOKIE_NAMES).forEach(name => {
    if (name !== COOKIE_NAMES.CONSENT) {
      deleteCookie(name)
      localStorage.removeItem(name)
    }
  })
}

/**
 * Cookie consent'i sıfırla
 */
function resetConsent() {
  deleteCookie(COOKIE_NAMES.CONSENT)
  consentGiven.value = false
  consentCategories.value = {
    [COOKIE_CATEGORIES.NECESSARY]: true,
    [COOKIE_CATEGORIES.PREFERENCES]: false,
    [COOKIE_CATEGORIES.ANALYTICS]: false,
    [COOKIE_CATEGORIES.MARKETING]: false
  }
  showBanner.value = true
}

// Composable export
export function useCookies() {
  // İlk yüklemede consent durumunu kontrol et
  if (typeof window !== 'undefined' && !consentGiven.value) {
    loadConsent()
  }

  return {
    // State
    consentGiven,
    consentCategories,
    showBanner,

    // Consent yönetimi
    acceptAll,
    acceptNecessaryOnly,
    saveConsent,
    hasConsent,
    resetConsent,

    // Cookie işlemleri
    getCookie,
    setCookie,
    deleteCookie,

    // Tercih cookie'leri
    setPreferenceCookie,
    getPreferenceCookie,

    // Tema
    setThemePreference,
    getThemePreference,

    // Dil
    setLanguagePreference,
    getLanguagePreference,

    // Son sunucu
    setLastServer,
    getLastServer,

    // Beni hatırla
    setRememberMe,
    getRememberMe,

    // Sidebar
    setSidebarState,
    getSidebarState,

    // Ses
    setVolumePreference,
    getVolumePreference,

    // Temizlik
    clearAllCookies,

    // Sabitler
    COOKIE_CATEGORIES,
    COOKIE_NAMES
  }
}

export default useCookies
