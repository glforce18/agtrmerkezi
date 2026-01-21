/**
 * AGTR Merkezi - SEO Utilities
 * Meta tag management for better SEO
 */

/**
 * Default meta values
 */
const defaults = {
  title: 'AGTR Merkezi',
  description: 'CS 1.6 ve Half-Life oyun sunuculari icin en iyi topluluk platformu',
  keywords: 'cs 1.6, half-life, game server, oyun sunucusu, agtr, counter-strike',
  image: '/og-image.png',
  url: typeof window !== 'undefined' ? window.location.origin : ''
}

/**
 * Update document title
 * @param {string} title - Page title
 * @param {boolean} includeSiteName - Include site name suffix
 */
export function setTitle(title, includeSiteName = true) {
  if (!title) {
    document.title = defaults.title
    return
  }

  document.title = includeSiteName
    ? `${title} | ${defaults.title}`
    : title
}

/**
 * Update meta tag
 * @param {string} name - Meta name or property
 * @param {string} content - Meta content
 * @param {boolean} isProperty - Use property instead of name
 */
export function setMeta(name, content, isProperty = false) {
  if (!content) return

  const attr = isProperty ? 'property' : 'name'
  let meta = document.querySelector(`meta[${attr}="${name}"]`)

  if (!meta) {
    meta = document.createElement('meta')
    meta.setAttribute(attr, name)
    document.head.appendChild(meta)
  }

  meta.setAttribute('content', content)
}

/**
 * Set multiple meta tags at once
 * @param {Object} tags - Object with meta tags
 */
export function setMetaTags(tags) {
  Object.entries(tags).forEach(([name, content]) => {
    const isProperty = name.startsWith('og:') || name.startsWith('twitter:')
    setMeta(name, content, isProperty)
  })
}

/**
 * Set Open Graph tags for social sharing
 * @param {Object} options - OG options
 */
export function setOpenGraph({ title, description, image, url, type = 'website' }) {
  setMeta('og:type', type, true)
  setMeta('og:title', title || defaults.title, true)
  setMeta('og:description', description || defaults.description, true)
  setMeta('og:image', image || defaults.image, true)
  setMeta('og:url', url || (typeof window !== 'undefined' ? window.location.href : ''), true)
  setMeta('og:site_name', defaults.title, true)
}

/**
 * Set Twitter Card tags
 * @param {Object} options - Twitter card options
 */
export function setTwitterCard({ title, description, image, card = 'summary_large_image' }) {
  setMeta('twitter:card', card, true)
  setMeta('twitter:title', title || defaults.title, true)
  setMeta('twitter:description', description || defaults.description, true)
  setMeta('twitter:image', image || defaults.image, true)
}

/**
 * Set canonical URL
 * @param {string} url - Canonical URL
 */
export function setCanonical(url) {
  let link = document.querySelector('link[rel="canonical"]')

  if (!link) {
    link = document.createElement('link')
    link.setAttribute('rel', 'canonical')
    document.head.appendChild(link)
  }

  link.setAttribute('href', url || (typeof window !== 'undefined' ? window.location.href : ''))
}

/**
 * Set robots meta
 * @param {string} content - Robots content (index, follow, etc.)
 */
export function setRobots(content = 'index, follow') {
  setMeta('robots', content)
}

/**
 * Set structured data (JSON-LD)
 * @param {Object} data - Structured data object
 */
export function setStructuredData(data) {
  let script = document.querySelector('script[type="application/ld+json"]')

  if (!script) {
    script = document.createElement('script')
    script.setAttribute('type', 'application/ld+json')
    document.head.appendChild(script)
  }

  script.textContent = JSON.stringify(data)
}

/**
 * Set page SEO - combines all methods
 * @param {Object} options - SEO options
 */
export function setPageSEO({
  title,
  description,
  keywords,
  image,
  url,
  type = 'website',
  robots = 'index, follow',
  structuredData = null
}) {
  // Title
  setTitle(title)

  // Basic meta tags
  setMeta('description', description || defaults.description)
  setMeta('keywords', keywords || defaults.keywords)

  // Open Graph
  setOpenGraph({ title, description, image, url, type })

  // Twitter Card
  setTwitterCard({ title, description, image })

  // Canonical
  setCanonical(url)

  // Robots
  setRobots(robots)

  // Structured Data
  if (structuredData) {
    setStructuredData(structuredData)
  }
}

/**
 * Pre-defined page SEO configurations
 */
export const pageSEO = {
  home: {
    title: null,
    description: 'CS 1.6 ve Half-Life oyun sunuculari icin en iyi topluluk platformu. Sunucu kirala, topluluga katil!',
    keywords: 'cs 1.6, half-life, game server, oyun sunucusu, agtr, counter-strike, gaming community'
  },

  forum: {
    title: 'Forum',
    description: 'AGTR topluluk forumu. Oyun stratejileri, sunucu ayarlari ve daha fazlasi hakkinda tartis.',
    keywords: 'forum, cs 1.6 forum, oyun forumu, gaming forum'
  },

  servers: {
    title: 'Sunucular',
    description: 'Aktif CS 1.6 ve Half-Life sunuculari. Hemen baglan ve oynamaya basla!',
    keywords: 'cs 1.6 servers, game servers, oyun sunuculari, server list'
  },

  shop: {
    title: 'Magaza',
    description: 'VIP paketler, sunucu kiralama ve daha fazlasi. En uygun fiyatlarla hemen satin al!',
    keywords: 'vip, sunucu kiralama, game hosting, oyun sunucusu'
  },

  leaderboard: {
    title: 'Lider Tablosu',
    description: 'En iyi oyuncular, en cok puan toplayanlar. Siralamalari incele!',
    keywords: 'leaderboard, ranking, top players, en iyi oyuncular'
  },

  jackpot: {
    title: 'Jackpot',
    description: 'Sansini dene, buyuk odullar kazan! AGTR Jackpot sistemi.',
    keywords: 'jackpot, odul, gaming lottery, oyun piyangosu'
  }
}

export default {
  setTitle,
  setMeta,
  setMetaTags,
  setOpenGraph,
  setTwitterCard,
  setCanonical,
  setRobots,
  setStructuredData,
  setPageSEO,
  pageSEO
}
