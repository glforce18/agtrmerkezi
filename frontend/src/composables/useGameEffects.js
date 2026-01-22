import { ref, readonly } from 'vue'

// Global refs for game effect components
const achievementRef = ref(null)
const killFeedRef = ref(null)
const xpGainRef = ref(null)
const levelUpRef = ref(null)

// Singleton state
const isInitialized = ref(false)

/**
 * useGameEffects composable
 * Provides methods to show game-themed effects like achievements, XP gains, kill feeds, and level ups
 */
export function useGameEffects() {
  /**
   * Initialize component refs (called from App.vue)
   */
  const init = (refs) => {
    if (refs.achievement) achievementRef.value = refs.achievement
    if (refs.killFeed) killFeedRef.value = refs.killFeed
    if (refs.xpGain) xpGainRef.value = refs.xpGain
    if (refs.levelUp) levelUpRef.value = refs.levelUp
    isInitialized.value = true
  }

  /**
   * Show achievement popup
   * @param {Object} data - Achievement data
   * @param {string} data.title - Achievement title
   * @param {string} [data.description] - Achievement description
   * @param {string} [data.gameIcon] - Game icon name (from icons.svg)
   * @param {Object} [data.icon] - Lucide icon component
   * @param {string} [data.color] - Icon color
   * @param {string} [data.type] - 'default' | 'epic' | 'legendary'
   * @param {string} [data.reward] - Reward text
   * @param {number} [data.duration] - Duration in ms (default: 4000)
   */
  const showAchievement = (data) => {
    if (achievementRef.value?.show) {
      achievementRef.value.show(data)
    } else {
      console.warn('[useGameEffects] Achievement component not initialized')
    }
  }

  /**
   * Add kill to kill feed
   * @param {Object} data - Kill data
   * @param {string} data.killer - Killer name
   * @param {string} data.victim - Victim name
   * @param {string} [data.weapon] - Weapon name for icon (ak47, awp, m4a1, deagle, knife, crowbar, gauss, crossbow)
   * @param {string} [data.weaponImage] - Custom weapon image URL
   * @param {string} [data.weaponName] - Weapon display name
   * @param {boolean} [data.headshot] - Is headshot
   * @param {string} [data.killerColor] - Killer name color
   * @param {string} [data.victimColor] - Victim name color
   * @param {number} [data.duration] - Duration in ms (default: 4000)
   */
  const addKill = (data) => {
    if (killFeedRef.value?.addKill) {
      killFeedRef.value.addKill(data)
    } else {
      console.warn('[useGameEffects] KillFeed component not initialized')
    }
  }

  /**
   * Show XP gain floating text
   * @param {number} amount - XP amount
   * @param {Object} [options] - Options
   * @param {string} [options.label] - Label text (default: 'XP')
   * @param {string} [options.type] - 'default' | 'bonus' | 'critical' | 'armor' | 'money'
   * @param {number} [options.x] - X position
   * @param {number} [options.y] - Y position
   * @param {number} [options.duration] - Duration in ms (default: 1500)
   */
  const showXP = (amount, options = {}) => {
    if (xpGainRef.value?.show) {
      xpGainRef.value.show(amount, options)
    } else {
      console.warn('[useGameEffects] XPGain component not initialized')
    }
  }

  /**
   * Show XP gain at specific element
   * @param {HTMLElement} element - Target element
   * @param {number} amount - XP amount
   * @param {Object} [options] - Options (same as showXP)
   */
  const showXPAtElement = (element, amount, options = {}) => {
    if (xpGainRef.value?.showAtElement) {
      xpGainRef.value.showAtElement(element, amount, options)
    } else {
      console.warn('[useGameEffects] XPGain component not initialized')
    }
  }

  /**
   * Show level up celebration
   * @param {Object} data - Level up data
   * @param {number} data.level - New level number
   * @param {string} [data.title] - Rank title
   * @param {Array} [data.rewards] - Array of reward objects { icon, text, color }
   * @param {number} [data.duration] - Auto-hide duration in ms (optional)
   */
  const showLevelUp = (data) => {
    if (levelUpRef.value?.show) {
      levelUpRef.value.show(data)
    } else {
      console.warn('[useGameEffects] LevelUp component not initialized')
    }
  }

  /**
   * Hide level up overlay
   */
  const hideLevelUp = () => {
    if (levelUpRef.value?.hide) {
      levelUpRef.value.hide()
    }
  }

  /**
   * Clear kill feed
   */
  const clearKillFeed = () => {
    if (killFeedRef.value?.clear) {
      killFeedRef.value.clear()
    }
  }

  // Convenience methods for common achievements
  const achievements = {
    firstWin: () => showAchievement({
      title: 'Ilk Zafer!',
      description: 'Ilk oyununu kazandin',
      gameIcon: 'achievement-first-win',
      color: '#22c55e',
      reward: '+100 XP'
    }),
    headshot: () => showAchievement({
      title: 'Headshot Ustasi',
      description: '10 headshot yaptin',
      gameIcon: 'kill-headshot',
      color: '#ef4444',
      type: 'epic'
    }),
    killStreak: (count) => showAchievement({
      title: `${count} Kill Streak!`,
      description: `Ard arda ${count} kill aldin`,
      gameIcon: 'kill-streak',
      color: '#f97316',
      type: 'legendary'
    }),
    levelUp: (level) => showAchievement({
      title: `Level ${level}!`,
      description: 'Yeni seviyeye ulastin',
      gameIcon: 'level-up',
      color: '#8b5cf6',
      reward: '+500 XP'
    }),
    dailyLogin: () => showAchievement({
      title: 'Gunluk Giris',
      description: 'Bugun giris yaptin',
      gameIcon: 'achievement-streak',
      color: '#06b6d4',
      reward: '+50 XP'
    }),
    purchase: () => showAchievement({
      title: 'Satin Alma Basarili!',
      description: 'Paketin aktif edildi',
      gameIcon: 'hud-money',
      color: '#22c55e',
      type: 'epic'
    })
  }

  return {
    // Initialization
    init,
    isInitialized: readonly(isInitialized),

    // Main methods
    showAchievement,
    addKill,
    showXP,
    showXPAtElement,
    showLevelUp,
    hideLevelUp,
    clearKillFeed,

    // Convenience achievements
    achievements,

    // Refs for direct access
    achievementRef: readonly(achievementRef),
    killFeedRef: readonly(killFeedRef),
    xpGainRef: readonly(xpGainRef),
    levelUpRef: readonly(levelUpRef)
  }
}

export default useGameEffects
