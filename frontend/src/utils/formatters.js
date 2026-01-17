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
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}
