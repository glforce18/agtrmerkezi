/**
 * Game Assets Composable
 * Oyun gorselleri, banner, icon ve animasyonlar icin API
 */

import { ref, computed } from 'vue'
import api from '@/services/api'

// Global cache
const gamesCache = ref(null)
const assetsCache = ref({})
const animationsCache = ref(null)

export function useGameAssets() {
  const loading = ref(false)
  const error = ref(null)

  /**
   * Desteklenen oyun listesini getir
   */
  async function getGames(forceRefresh = false) {
    if (gamesCache.value && !forceRefresh) {
      return gamesCache.value
    }

    loading.value = true
    error.value = null

    try {
      const response = await api.get('/game-assets/games')
      // API servisi direkt data dönüyor, response.data değil
      if (response.success) {
        gamesCache.value = response.games
        return response.games
      }
      return []
    } catch (e) {
      error.value = e.message
      console.error('Failed to fetch games:', e)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Oyuna ait asset'leri getir
   * @param {string} gameSlug - Oyun slug (cs16, halflife, etc.)
   * @param {string} assetType - Asset tipi (banner, hero, logo, icon, etc.)
   * @param {number} limit - Maksimum sonuc
   */
  async function getGameAssets(gameSlug, assetType = null, limit = 20) {
    const cacheKey = `${gameSlug}_${assetType || 'all'}_${limit}`

    if (assetsCache.value[cacheKey]) {
      return assetsCache.value[cacheKey]
    }

    loading.value = true
    error.value = null

    try {
      const params = { limit }
      if (assetType) {
        params.asset_type = assetType
      }

      const response = await api.get(`/game-assets/games/${gameSlug}`, { params })
      // API servisi direkt data dönüyor
      if (response.success) {
        assetsCache.value[cacheKey] = response.assets
        return response.assets
      }
      return []
    } catch (e) {
      error.value = e.message
      console.error(`Failed to fetch assets for ${gameSlug}:`, e)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Oyunun ana banner'ini getir
   * @param {string} gameSlug - Oyun slug
   */
  async function getGameBanner(gameSlug) {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/game-assets/games/${gameSlug}/banner`)
      if (response.success) {
        return response.asset
      }
      return null
    } catch (e) {
      error.value = e.message
      console.error(`Failed to fetch banner for ${gameSlug}:`, e)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Oyuna ait haritalari getir
   * @param {string} gameSlug - Oyun slug
   * @param {string} mapType - Harita tipi (de_, cs_, fy_, etc.)
   * @param {number} limit - Maksimum sonuc
   */
  async function getGameMaps(gameSlug, mapType = null, limit = 20) {
    loading.value = true
    error.value = null

    try {
      const params = { limit }
      if (mapType) {
        params.map_type = mapType
      }

      const response = await api.get(`/game-assets/games/${gameSlug}/maps`, { params })
      if (response.success) {
        return response.maps
      }
      return []
    } catch (e) {
      error.value = e.message
      console.error(`Failed to fetch maps for ${gameSlug}:`, e)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Animasyonlari getir
   * @param {string} category - Kategori (loading, success, error, game, ui)
   * @param {number} limit - Maksimum sonuc
   */
  async function getAnimations(category = null, limit = 20) {
    if (animationsCache.value && !category) {
      return animationsCache.value
    }

    loading.value = true
    error.value = null

    try {
      const params = { limit }
      if (category) {
        params.category = category
      }

      const response = await api.get('/game-assets/animations', { params })
      if (response.success) {
        if (!category) {
          animationsCache.value = response.animations
        }
        return response.animations
      }
      return []
    } catch (e) {
      error.value = e.message
      console.error('Failed to fetch animations:', e)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Tek animasyon detayi getir
   * @param {string} slug - Animasyon slug
   */
  async function getAnimation(slug) {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/game-assets/animations/${slug}`)
      if (response.success) {
        return response.animation
      }
      return null
    } catch (e) {
      error.value = e.message
      console.error(`Failed to fetch animation ${slug}:`, e)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Cache'i temizle
   */
  function clearCache() {
    gamesCache.value = null
    assetsCache.value = {}
    animationsCache.value = null
  }

  return {
    loading,
    error,
    getGames,
    getGameAssets,
    getGameBanner,
    getGameMaps,
    getAnimations,
    getAnimation,
    clearCache
  }
}
