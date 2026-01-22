import { ref, computed, onMounted } from 'vue'

const STREAK_KEY = 'agtr-daily-streak'
const LAST_LOGIN_KEY = 'agtr-last-login-date'

export function useStreak() {
  const streak = ref(0)
  const lastLoginDate = ref(null)
  const streakBonus = ref(0)
  const showStreakPopup = ref(false)

  // Get today's date as YYYY-MM-DD
  const getToday = () => {
    return new Date().toISOString().split('T')[0]
  }

  // Get yesterday's date as YYYY-MM-DD
  const getYesterday = () => {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    return yesterday.toISOString().split('T')[0]
  }

  // Calculate bonus based on streak
  const calculateBonus = (streakCount) => {
    if (streakCount >= 30) return 50
    if (streakCount >= 14) return 25
    if (streakCount >= 7) return 15
    if (streakCount >= 3) return 5
    return 0
  }

  // Initialize streak from localStorage
  const initStreak = () => {
    const savedStreak = localStorage.getItem(STREAK_KEY)
    const savedLastLogin = localStorage.getItem(LAST_LOGIN_KEY)
    const today = getToday()
    const yesterday = getYesterday()

    if (savedLastLogin === today) {
      // Already logged in today, just restore streak
      streak.value = parseInt(savedStreak) || 1
    } else if (savedLastLogin === yesterday) {
      // Logged in yesterday, continue streak
      streak.value = (parseInt(savedStreak) || 0) + 1
      localStorage.setItem(STREAK_KEY, streak.value)
      localStorage.setItem(LAST_LOGIN_KEY, today)
      showStreakPopup.value = true
    } else {
      // Streak broken, start fresh
      streak.value = 1
      localStorage.setItem(STREAK_KEY, 1)
      localStorage.setItem(LAST_LOGIN_KEY, today)
      if (savedLastLogin) {
        // Only show popup if there was a previous streak
        showStreakPopup.value = true
      }
    }

    lastLoginDate.value = today
    streakBonus.value = calculateBonus(streak.value)
  }

  // Check if streak is at risk (hasn't logged in today)
  const isStreakAtRisk = computed(() => {
    const today = getToday()
    return lastLoginDate.value !== today
  })

  // Get streak tier for styling
  const streakTier = computed(() => {
    if (streak.value >= 30) return 'legendary'
    if (streak.value >= 14) return 'epic'
    if (streak.value >= 7) return 'rare'
    if (streak.value >= 3) return 'common'
    return 'starter'
  })

  // Get next milestone
  const nextMilestone = computed(() => {
    if (streak.value < 3) return { target: 3, label: '3 Gün' }
    if (streak.value < 7) return { target: 7, label: '1 Hafta' }
    if (streak.value < 14) return { target: 14, label: '2 Hafta' }
    if (streak.value < 30) return { target: 30, label: '1 Ay' }
    return { target: streak.value + 30, label: 'Devam Et!' }
  })

  // Hide popup
  const hideStreakPopup = () => {
    showStreakPopup.value = false
  }

  onMounted(() => {
    initStreak()
  })

  return {
    streak,
    streakBonus,
    streakTier,
    nextMilestone,
    isStreakAtRisk,
    showStreakPopup,
    hideStreakPopup,
    initStreak
  }
}
