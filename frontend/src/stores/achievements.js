/**
 * Achievements Store - Başarım Sistemi
 * Track player achievements, progress, and rewards
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { trackAchievement } from '@/services/analytics'

// Achievement Categories
export const AchievementCategory = {
  GAMEPLAY: 'gameplay',
  SOCIAL: 'social',
  FORUM: 'forum',
  COLLECTION: 'collection',
  SPECIAL: 'special'
}

// Achievement Rarity
export const AchievementRarity = {
  COMMON: { name: 'Yaygın', color: '#9ca3af', points: 10 },
  UNCOMMON: { name: 'Sık Olmayan', color: '#22c55e', points: 25 },
  RARE: { name: 'Nadir', color: '#3b82f6', points: 50 },
  EPIC: { name: 'Epik', color: '#8b5cf6', points: 100 },
  LEGENDARY: { name: 'Efsanevi', color: '#f97316', points: 250 }
}

// Predefined achievements (can be extended from backend)
const ACHIEVEMENT_DEFINITIONS = [
  // Gameplay
  { id: 'first_blood', name: 'İlk Kan', description: 'İlk oyuncuyu öldür', icon: '🎯', category: AchievementCategory.GAMEPLAY, rarity: 'COMMON', maxProgress: 1 },
  { id: 'headshot_master', name: 'Headshot Ustası', description: '100 headshot yap', icon: '🎯', category: AchievementCategory.GAMEPLAY, rarity: 'RARE', maxProgress: 100 },
  { id: 'killstreak_5', name: 'Öldürme Serisi', description: 'Ölmeden 5 kişi öldür', icon: '🔥', category: AchievementCategory.GAMEPLAY, rarity: 'UNCOMMON', maxProgress: 1 },
  { id: 'killstreak_10', name: 'Durdurulamaz', description: 'Ölmeden 10 kişi öldür', icon: '💀', category: AchievementCategory.GAMEPLAY, rarity: 'EPIC', maxProgress: 1 },
  { id: 'play_100_hours', name: 'Veteran', description: '100 saat oyna', icon: '⏰', category: AchievementCategory.GAMEPLAY, rarity: 'EPIC', maxProgress: 100 },
  { id: 'win_100_matches', name: 'Zafer Lordu', description: '100 maç kazan', icon: '🏆', category: AchievementCategory.GAMEPLAY, rarity: 'LEGENDARY', maxProgress: 100 },

  // Social
  { id: 'first_friend', name: 'İlk Arkadaş', description: 'İlk arkadaşını ekle', icon: '👥', category: AchievementCategory.SOCIAL, rarity: 'COMMON', maxProgress: 1 },
  { id: 'social_butterfly', name: 'Sosyal Kelebek', description: '50 arkadaş edin', icon: '🦋', category: AchievementCategory.SOCIAL, rarity: 'RARE', maxProgress: 50 },
  { id: 'team_player', name: 'Takım Oyuncusu', description: 'Bir klana katıl', icon: '🤝', category: AchievementCategory.SOCIAL, rarity: 'UNCOMMON', maxProgress: 1 },

  // Forum
  { id: 'first_post', name: 'İlk Gönderi', description: 'İlk forum gönderini paylaş', icon: '📝', category: AchievementCategory.FORUM, rarity: 'COMMON', maxProgress: 1 },
  { id: 'popular_post', name: 'Popüler Gönderi', description: '50 beğeni al', icon: '❤️', category: AchievementCategory.FORUM, rarity: 'RARE', maxProgress: 50 },
  { id: 'forum_veteran', name: 'Forum Kıdemi', description: '100 gönderi paylaş', icon: '💬', category: AchievementCategory.FORUM, rarity: 'EPIC', maxProgress: 100 },

  // Collection
  { id: 'first_purchase', name: 'İlk Alışveriş', description: 'Mağazadan ilk ürünü al', icon: '🛒', category: AchievementCategory.COLLECTION, rarity: 'COMMON', maxProgress: 1 },
  { id: 'vip_member', name: 'VIP Üye', description: 'VIP üyelik satın al', icon: '⭐', category: AchievementCategory.COLLECTION, rarity: 'UNCOMMON', maxProgress: 1 },
  { id: 'big_spender', name: 'Büyük Harcamacı', description: '1000 TL harca', icon: '💎', category: AchievementCategory.COLLECTION, rarity: 'LEGENDARY', maxProgress: 1000 },

  // Special
  { id: 'early_adopter', name: 'Erken Kuş', description: 'Beta döneminde kayıt ol', icon: '🐦', category: AchievementCategory.SPECIAL, rarity: 'LEGENDARY', maxProgress: 1 },
  { id: 'anniversary', name: 'Yıl Dönümü', description: '1 yıldır üye ol', icon: '🎂', category: AchievementCategory.SPECIAL, rarity: 'EPIC', maxProgress: 1 },
  { id: 'daily_streak_7', name: 'Haftalık Seri', description: '7 gün üst üste giriş yap', icon: '🔥', category: AchievementCategory.SPECIAL, rarity: 'UNCOMMON', maxProgress: 7 },
  { id: 'daily_streak_30', name: 'Aylık Seri', description: '30 gün üst üste giriş yap', icon: '🔥', category: AchievementCategory.SPECIAL, rarity: 'RARE', maxProgress: 30 }
]

export const useAchievementsStore = defineStore('achievements', () => {
  // State
  const achievements = ref([]) // All available achievements
  const userAchievements = ref([]) // User's unlocked achievements
  const userProgress = ref({}) // Progress for each achievement
  const loading = ref(false)
  const error = ref(null)

  // Recently unlocked (for notifications)
  const recentlyUnlocked = ref([])

  // Computed
  const totalPoints = computed(() => {
    return userAchievements.value.reduce((sum, ua) => {
      const def = getAchievementDef(ua.achievement_id)
      return sum + (AchievementRarity[def?.rarity]?.points || 0)
    }, 0)
  })

  const unlockedCount = computed(() => userAchievements.value.length)

  const totalCount = computed(() => achievements.value.length)

  const completionPercent = computed(() => {
    if (totalCount.value === 0) return 0
    return Math.round((unlockedCount.value / totalCount.value) * 100)
  })

  const achievementsByCategory = computed(() => {
    const grouped = {}
    for (const category of Object.values(AchievementCategory)) {
      grouped[category] = achievements.value.filter(a => a.category === category)
    }
    return grouped
  })

  // Helper functions
  const getAchievementDef = (id) => {
    return achievements.value.find(a => a.id === id) ||
           ACHIEVEMENT_DEFINITIONS.find(a => a.id === id)
  }

  const isUnlocked = (achievementId) => {
    return userAchievements.value.some(ua => ua.achievement_id === achievementId)
  }

  const getProgress = (achievementId) => {
    return userProgress.value[achievementId] || 0
  }

  const getProgressPercent = (achievementId) => {
    const def = getAchievementDef(achievementId)
    if (!def || !def.maxProgress) return 0
    const progress = getProgress(achievementId)
    return Math.min(100, Math.round((progress / def.maxProgress) * 100))
  }

  // Actions
  const fetchAchievements = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/achievements')
      achievements.value = response.achievements || response || ACHIEVEMENT_DEFINITIONS
    } catch (e) {
      console.error('Failed to fetch achievements:', e)
      // Fall back to predefined
      achievements.value = ACHIEVEMENT_DEFINITIONS
    } finally {
      loading.value = false
    }
  }

  const fetchUserAchievements = async () => {
    try {
      const response = await api.get('/achievements/me')
      userAchievements.value = response.unlocked || response.achievements || []
      userProgress.value = response.progress || {}
    } catch (e) {
      console.error('Failed to fetch user achievements:', e)
      userAchievements.value = []
      userProgress.value = {}
    }
  }

  const updateProgress = async (achievementId, progress) => {
    const def = getAchievementDef(achievementId)
    if (!def) return

    // Update local progress
    userProgress.value[achievementId] = progress

    // Check if achievement should be unlocked
    if (progress >= def.maxProgress && !isUnlocked(achievementId)) {
      await unlockAchievement(achievementId)
    }

    // Sync with backend
    try {
      await api.post('/achievements/progress', { achievement_id: achievementId, progress })
    } catch (e) {
      console.error('Failed to update progress:', e)
    }
  }

  const unlockAchievement = async (achievementId) => {
    const def = getAchievementDef(achievementId)
    if (!def || isUnlocked(achievementId)) return

    // Add to unlocked
    const unlockData = {
      achievement_id: achievementId,
      unlocked_at: new Date().toISOString()
    }
    userAchievements.value.push(unlockData)

    // Add to recently unlocked for notification
    recentlyUnlocked.value.push({
      ...def,
      ...unlockData
    })

    // Track in analytics
    trackAchievement(achievementId, def.name)

    // Sync with backend
    try {
      await api.post('/achievements/unlock', { achievement_id: achievementId })
    } catch (e) {
      console.error('Failed to sync achievement unlock:', e)
    }
  }

  const clearRecentlyUnlocked = () => {
    recentlyUnlocked.value = []
  }

  const popRecentlyUnlocked = () => {
    return recentlyUnlocked.value.shift()
  }

  // Initialize
  const init = async () => {
    await Promise.all([
      fetchAchievements(),
      fetchUserAchievements()
    ])
  }

  // Reset
  const reset = () => {
    userAchievements.value = []
    userProgress.value = {}
    recentlyUnlocked.value = []
  }

  return {
    // State
    achievements,
    userAchievements,
    userProgress,
    loading,
    error,
    recentlyUnlocked,

    // Computed
    totalPoints,
    unlockedCount,
    totalCount,
    completionPercent,
    achievementsByCategory,

    // Methods
    getAchievementDef,
    isUnlocked,
    getProgress,
    getProgressPercent,
    fetchAchievements,
    fetchUserAchievements,
    updateProgress,
    unlockAchievement,
    clearRecentlyUnlocked,
    popRecentlyUnlocked,
    init,
    reset,

    // Constants
    AchievementCategory,
    AchievementRarity
  }
})
