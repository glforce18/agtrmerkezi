/**
 * Analytics Service
 * Google Analytics 4 + Custom Event Tracking for AGTR Merkezi
 *
 * Setup:
 * 1. Add your GA4 Measurement ID to .env: VITE_GA_MEASUREMENT_ID=G-XXXXXXXXXX
 * 2. The script will be loaded automatically
 */

const isDev = import.meta.env.DEV
const GA_MEASUREMENT_ID = import.meta.env.VITE_GA_MEASUREMENT_ID || ''

// Event categories
export const EventCategory = {
  USER: 'user',
  SERVER: 'server',
  FORUM: 'forum',
  SHOP: 'shop',
  GAME: 'game',
  NAVIGATION: 'navigation',
  ENGAGEMENT: 'engagement'
}

/**
 * Load Google Analytics script
 */
const loadGoogleAnalytics = () => {
  if (!GA_MEASUREMENT_ID || isDev) {
    if (isDev) console.log('%c[Analytics] Skipped in development', 'color: #6b7280')
    return false
  }

  // Check if already loaded
  if (window.gtag) return true

  // Create script elements
  const script1 = document.createElement('script')
  script1.async = true
  script1.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`

  const script2 = document.createElement('script')
  script2.innerHTML = `
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '${GA_MEASUREMENT_ID}', {
      send_page_view: false,
      cookie_flags: 'SameSite=None;Secure'
    });
  `

  document.head.appendChild(script1)
  document.head.appendChild(script2)

  return true
}

/**
 * Track page view
 */
export const trackPageView = (path, title) => {
  if (isDev) {
    console.log('%c[Analytics] Page View:', 'color: #3b82f6', { path, title })
    return
  }

  if (window.gtag) {
    window.gtag('event', 'page_view', {
      page_path: path,
      page_title: title,
      page_location: window.location.href
    })
  }
}

/**
 * Track custom event
 */
export const trackEvent = (eventName, category = EventCategory.ENGAGEMENT, params = {}) => {
  const eventData = {
    event_category: category,
    ...params
  }

  if (isDev) {
    console.log('%c[Analytics] Event:', 'color: #22c55e', eventName, eventData)
    return
  }

  if (window.gtag) {
    window.gtag('event', eventName, eventData)
  }
}

/**
 * Track user login
 */
export const trackLogin = (method = 'email') => {
  trackEvent('login', EventCategory.USER, { method })
}

/**
 * Track user registration
 */
export const trackRegister = (method = 'email') => {
  trackEvent('sign_up', EventCategory.USER, { method })
}

/**
 * Track server actions
 */
export const trackServerAction = (action, serverId, serverName) => {
  trackEvent(`server_${action}`, EventCategory.SERVER, {
    server_id: serverId,
    server_name: serverName
  })
}

/**
 * Track forum actions
 */
export const trackForumAction = (action, topicId, categoryId) => {
  trackEvent(`forum_${action}`, EventCategory.FORUM, {
    topic_id: topicId,
    category_id: categoryId
  })
}

/**
 * Track shop/purchase events
 */
export const trackPurchase = (itemId, itemName, value, currency = 'TRY') => {
  trackEvent('purchase', EventCategory.SHOP, {
    item_id: itemId,
    item_name: itemName,
    value,
    currency
  })
}

/**
 * Track shop view
 */
export const trackViewItem = (itemId, itemName, price) => {
  trackEvent('view_item', EventCategory.SHOP, {
    item_id: itemId,
    item_name: itemName,
    price
  })
}

/**
 * Track search
 */
export const trackSearch = (searchTerm, resultsCount) => {
  trackEvent('search', EventCategory.NAVIGATION, {
    search_term: searchTerm,
    results_count: resultsCount
  })
}

/**
 * Track game connection
 */
export const trackGameConnect = (serverAddress, gameType) => {
  trackEvent('game_connect', EventCategory.GAME, {
    server_address: serverAddress,
    game_type: gameType
  })
}

/**
 * Track achievement unlock
 */
export const trackAchievement = (achievementId, achievementName) => {
  trackEvent('unlock_achievement', EventCategory.GAME, {
    achievement_id: achievementId,
    achievement_name: achievementName
  })
}

/**
 * Track level up
 */
export const trackLevelUp = (level, character = 'user') => {
  trackEvent('level_up', EventCategory.GAME, {
    level,
    character
  })
}

/**
 * Track engagement time
 */
let engagementStartTime = null

export const startEngagementTracking = () => {
  engagementStartTime = Date.now()
}

export const endEngagementTracking = (pageName) => {
  if (!engagementStartTime) return

  const duration = Math.round((Date.now() - engagementStartTime) / 1000)
  engagementStartTime = null

  if (duration > 5) { // Only track if more than 5 seconds
    trackEvent('engagement', EventCategory.ENGAGEMENT, {
      page_name: pageName,
      engagement_time_sec: duration
    })
  }
}

/**
 * Set user properties
 */
export const setUserProperties = (userId, properties = {}) => {
  if (isDev) {
    console.log('%c[Analytics] User Properties:', 'color: #8b5cf6', { userId, properties })
    return
  }

  if (window.gtag) {
    window.gtag('set', 'user_properties', {
      user_id: userId,
      ...properties
    })
  }
}

/**
 * Initialize analytics with router
 */
export const initAnalytics = (router) => {
  const loaded = loadGoogleAnalytics()

  // Track page views on route change
  router.afterEach((to, from) => {
    // End engagement tracking for previous page
    if (from.name) {
      endEngagementTracking(from.name)
    }

    // Start engagement tracking for new page
    startEngagementTracking()

    // Track page view
    trackPageView(to.path, to.meta?.title || to.name || 'AGTR Merkezi')
  })

  if (isDev) {
    console.log('%c[Analytics] Initialized', 'color: #22c55e', { loaded, measurementId: GA_MEASUREMENT_ID || 'Not set' })
  }
}

export default {
  init: initAnalytics,
  trackPageView,
  trackEvent,
  trackLogin,
  trackRegister,
  trackServerAction,
  trackForumAction,
  trackPurchase,
  trackViewItem,
  trackSearch,
  trackGameConnect,
  trackAchievement,
  trackLevelUp,
  setUserProperties,
  EventCategory
}
