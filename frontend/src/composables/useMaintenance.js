/**
 * Bakım Modu Composable
 * Site özelliklerinin bakım durumunu kontrol eder
 */

import { ref, readonly } from 'vue'

// Global state
const maintenanceStatus = ref({})
const lastFetch = ref(null)
const CACHE_DURATION = 60000 // 1 dakika cache

/**
 * Bakım durumunu fetch et
 */
const fetchMaintenanceStatus = async (force = false) => {
  // Cache kontrolü
  if (!force && lastFetch.value && Date.now() - lastFetch.value < CACHE_DURATION) {
    return maintenanceStatus.value
  }

  try {
    const response = await fetch('/api/maintenance/status')
    if (response.ok) {
      const data = await response.json()
      maintenanceStatus.value = data.maintenance || {}
      lastFetch.value = Date.now()
    }
  } catch (error) {
    console.error('Maintenance status fetch error:', error)
  }

  return maintenanceStatus.value
}

/**
 * Belirli bir özelliğin bakımda olup olmadığını kontrol et
 */
const isInMaintenance = (feature) => {
  return maintenanceStatus.value[feature]?.enabled || false
}

/**
 * Bakım mesajını al
 */
const getMaintenanceMessage = (feature) => {
  return maintenanceStatus.value[feature]?.message || 'Bu özellik şu anda bakımdadır.'
}

/**
 * Tahmini bitiş zamanını al
 */
const getEstimatedEnd = (feature) => {
  const end = maintenanceStatus.value[feature]?.estimated_end
  if (!end) return null
  return new Date(end)
}

/**
 * Bakım durumunu kontrol et ve gerekirse hata fırlat
 */
const checkMaintenance = async (feature, showAlert = true) => {
  await fetchMaintenanceStatus()

  if (isInMaintenance(feature)) {
    const message = getMaintenanceMessage(feature)
    if (showAlert && typeof window !== 'undefined') {
      // Basit alert yerine custom modal/toast kullanılabilir
      alert(`🔧 ${message}`)
    }
    return { inMaintenance: true, message }
  }

  return { inMaintenance: false }
}

/**
 * Feature-specific check fonksiyonları
 */
const checkPaymentsMaintenance = () => checkMaintenance('payments')
const checkServerRentalMaintenance = () => checkMaintenance('server_rental')
const checkShopMaintenance = () => checkMaintenance('shop')
const checkForumMaintenance = () => checkMaintenance('forum')
const checkTournamentsMaintenance = () => checkMaintenance('tournaments')
const checkTransfersMaintenance = () => checkMaintenance('transfers')
const checkRegistrationMaintenance = () => checkMaintenance('registration')
const checkClansMaintenance = () => checkMaintenance('clans')
const checkJackpotMaintenance = () => checkMaintenance('jackpot')
const checkWithdrawalsMaintenance = () => checkMaintenance('withdrawals')

/**
 * Composable export
 */
export function useMaintenance() {
  return {
    // State
    maintenanceStatus: readonly(maintenanceStatus),

    // Methods
    fetchMaintenanceStatus,
    isInMaintenance,
    getMaintenanceMessage,
    getEstimatedEnd,
    checkMaintenance,

    // Feature-specific checks
    checkPaymentsMaintenance,
    checkServerRentalMaintenance,
    checkShopMaintenance,
    checkForumMaintenance,
    checkTournamentsMaintenance,
    checkTransfersMaintenance,
    checkRegistrationMaintenance,
    checkClansMaintenance,
    checkJackpotMaintenance,
    checkWithdrawalsMaintenance
  }
}

// Default export
export default useMaintenance
