/**
 * AGTR Merkezi - Utils Index
 * Tüm utility fonksiyonlarını tek noktadan export eder
 */

export * from './http'

// Format utilities
export function formatCurrency(value, currency = 'TL') {
  return new Intl.NumberFormat('tr-TR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value) + (currency ? ` ${currency}` : '')
}

export function formatNumber(value) {
  return new Intl.NumberFormat('tr-TR').format(value)
}

export function formatDate(date, options = {}) {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString('tr-TR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options
  })
}

export function formatDateTime(date) {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleString('tr-TR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function formatRelativeTime(date) {
  if (!date) return '-'
  const d = new Date(date)
  const now = new Date()
  const diff = now - d

  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 7) return formatDate(date)
  if (days > 0) return `${days} gün önce`
  if (hours > 0) return `${hours} saat önce`
  if (minutes > 0) return `${minutes} dakika önce`
  return 'Az önce'
}

// Validation utilities
export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

export function isValidUsername(username) {
  return /^[a-zA-Z0-9_]{3,20}$/.test(username)
}

// String utilities
export function truncate(str, length = 50) {
  if (!str) return ''
  if (str.length <= length) return str
  return str.substring(0, length) + '...'
}

export function slugify(str) {
  const trMap = {
    'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
    'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
  }

  let slug = str.toLowerCase()
  for (const [tr, en] of Object.entries(trMap)) {
    slug = slug.replace(new RegExp(tr, 'g'), en)
  }

  return slug
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '')
}
