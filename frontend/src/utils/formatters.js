export function formatDate(date, format = 'long') {
  const d = new Date(date)

  if (format === 'relative') {
    return getRelativeTime(d)
  }

  const options = format === 'short'
    ? { year: 'numeric', month: 'short', day: 'numeric' }
    : { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }

  return d.toLocaleDateString('tr-TR', options)
}

export function getRelativeTime(date) {
  const now = new Date()
  const diff = now - new Date(date)
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 7) {
    return formatDate(date, 'short')
  } else if (days > 0) {
    return `${days} gün önce`
  } else if (hours > 0) {
    return `${hours} saat önce`
  } else if (minutes > 0) {
    return `${minutes} dakika önce`
  } else {
    return 'Az önce'
  }
}

export function formatNumber(num) {
  return new Intl.NumberFormat('tr-TR').format(num)
}

export function formatCurrency(amount) {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY'
  }).format(amount)
}

export function truncate(text, length = 100) {
  if (!text) return ''
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

/**
 * Format Armor currency
 */
export function formatArmor(value) {
  if (value === null || value === undefined) return '0'
  return formatNumber(value)
}

/**
 * Format file size
 */
export function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return '0 B'

  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  const size = bytes / Math.pow(1024, i)

  return `${size.toFixed(i > 0 ? 1 : 0)} ${units[i]}`
}

/**
 * Format duration (seconds to HH:MM:SS)
 */
export function formatDuration(seconds) {
  if (!seconds || seconds < 0) return '00:00'

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

/**
 * Format uptime (seconds to human readable)
 */
export function formatUptime(seconds) {
  if (!seconds || seconds < 0) return '0 saniye'

  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  const parts = []
  if (days > 0) parts.push(`${days} gun`)
  if (hours > 0) parts.push(`${hours} saat`)
  if (minutes > 0 && days === 0) parts.push(`${minutes} dakika`)

  return parts.join(' ') || '0 dakika'
}

/**
 * Format percentage
 */
export function formatPercentage(value, decimals = 0) {
  if (value === null || value === undefined) return '0%'
  const percentage = value <= 1 && value >= 0 ? value * 100 : value
  return `${percentage.toFixed(decimals)}%`
}

/**
 * Format player count
 */
export function formatPlayerCount(current, max) {
  return `${current || 0}/${max || 0}`
}

/**
 * Format server address
 */
export function formatServerAddress(ip, port) {
  if (!ip) return ''
  return port ? `${ip}:${port}` : ip
}

/**
 * Format status text (Turkish)
 */
export function formatStatus(status) {
  const statusMap = {
    active: 'Aktif',
    inactive: 'Pasif',
    pending: 'Bekliyor',
    completed: 'Tamamlandı',
    failed: 'Başarısız',
    banned: 'Yasaklı',
    online: 'Çevrimiçi',
    offline: 'Çevrimdışı',
    starting: 'Başlatılıyor',
    stopping: 'Durduruluyor',
    running: 'Çalışıyor',
    stopped: 'Durduruldu',
    error: 'Hata'
  }
  return statusMap[status?.toLowerCase()] || status || ''
}

/**
 * Format role text (Turkish)
 */
export function formatRole(role) {
  const roleMap = {
    user: 'Kullanıcı',
    admin: 'Yönetici',
    moderatör: 'Moderatör',
    vip: 'VIP',
    premium: 'Premium'
  }
  return roleMap[role?.toLowerCase()] || role || ''
}

/**
 * Format username for display
 */
export function formatUsername(username) {
  if (!username) return ''
  return username.charAt(0).toUpperCase() + username.slice(1)
}
