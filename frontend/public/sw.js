/**
 * AGTR Merkezi - Service Worker
 * Offline support and caching strategy
 */

const CACHE_VERSION = 19
const CACHE_NAME = `agtr-v${CACHE_VERSION}`
const STATIC_CACHE = `agtr-static-v${CACHE_VERSION}`
const DYNAMIC_CACHE = `agtr-dynamic-v${CACHE_VERSION}`
const API_CACHE = `agtr-api-v${CACHE_VERSION}`

// Static assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.ico',
  '/logo-navbar.png'
]

// API routes to use network-first strategy
const API_ROUTES = ['/api/']

// API endpoints that can be cached for offline access (read-only, public data)
// IMPORTANT: Use $ to match exact endpoints, avoid caching dynamic data
const CACHEABLE_API_PATTERNS = [
  /\/api\/public\/settings$/,
  /\/api\/forum\/categories$/,  // Only cache category list, NOT category/{id}/topics
  /\/api\/packages$/,
  /\/api\/announcements$/,
  /\/api\/servers$/,
  /\/api\/forum\/trending$/,
  /\/api\/health$/
]

// API endpoints that should NEVER be cached (always fetch fresh)
const NEVER_CACHE_PATTERNS = [
  /\/api\/forum\/categories\/[^/]+\/topics/,  // Category topics - always fresh
  /\/api\/forum\/topics\/\d+$/,               // Single topic - always fresh
  /\/api\/auth\//,                            // Auth endpoints
  /\/api\/user\//,                            // User data
  /\/api\/wallet\//                           // Wallet data
]

// Cache TTL for different API types (in seconds)
const API_CACHE_TTL = {
  default: 60,  // 1 minute
  settings: 300,  // 5 minutes
  categories: 300,  // 5 minutes
  static: 3600  // 1 hour
}

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Caching static assets')
        return cache.addAll(STATIC_ASSETS)
      })
      .then(() => self.skipWaiting())
  )
})

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  const currentCaches = [STATIC_CACHE, DYNAMIC_CACHE, API_CACHE]
  event.waitUntil(
    caches.keys()
      .then((keys) => {
        return Promise.all(
          keys
            .filter((key) => key.startsWith('agtr-') && !currentCaches.includes(key))
            .map((key) => {
              console.log('[SW] Removing old cache:', key)
              return caches.delete(key)
            })
        )
      })
      .then(() => self.clients.claim())
  )
})

// Fetch event - caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // Skip non-GET requests
  if (request.method !== 'GET') return

  // Skip chrome-extension and other non-http(s) requests
  if (!url.protocol.startsWith('http')) return

  // API requests: Check if cacheable, use appropriate strategy
  if (API_ROUTES.some(route => url.pathname.startsWith(route))) {
    // Check if this endpoint should NEVER be cached
    const shouldNeverCache = NEVER_CACHE_PATTERNS.some(pattern => pattern.test(url.pathname))
    if (shouldNeverCache) {
      // Always fetch fresh data for dynamic endpoints
      event.respondWith(networkOnly(request))
      return
    }

    const isCacheable = CACHEABLE_API_PATTERNS.some(pattern => pattern.test(url.pathname))
    if (isCacheable) {
      // Cacheable API: stale-while-revalidate for fast offline access
      event.respondWith(staleWhileRevalidateApi(request))
    } else {
      // Non-cacheable API: network first
      event.respondWith(networkFirst(request))
    }
    return
  }

  // Static assets: Cache first, fallback to network
  if (isStaticAsset(url.pathname)) {
    event.respondWith(cacheFirst(request))
    return
  }

  // HTML pages: Network first with offline fallback
  if (request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(networkFirstWithOffline(request))
    return
  }

  // Default: Stale-while-revalidate
  event.respondWith(staleWhileRevalidate(request))
})

// Check if URL is a static asset
function isStaticAsset(pathname) {
  const staticExtensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf']
  return staticExtensions.some(ext => pathname.endsWith(ext))
}

// Cache first strategy
async function cacheFirst(request) {
  const cached = await caches.match(request)
  if (cached) return cached

  try {
    const response = await fetch(request)
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE)
      cache.put(request, response.clone())
    }
    return response
  } catch (error) {
    console.log('[SW] Cache first failed:', error)
    return new Response('Offline', { status: 503 })
  }
}

// Network only strategy - always fetch fresh, never cache
async function networkOnly(request) {
  try {
    const response = await fetch(request)
    return response
  } catch (error) {
    console.log('[SW] Network only failed:', error)
    return new Response(JSON.stringify({ error: 'Network error', offline: true }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

// Network first strategy
async function networkFirst(request) {
  try {
    const response = await fetch(request)
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE)
      cache.put(request, response.clone())
    }
    return response
  } catch (error) {
    const cached = await caches.match(request)
    if (cached) return cached
    return new Response(JSON.stringify({ error: 'Offline' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

// Network first with offline page fallback
async function networkFirstWithOffline(request) {
  try {
    const response = await fetch(request)
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE)
      cache.put(request, response.clone())
    }
    return response
  } catch (error) {
    const cached = await caches.match(request)
    if (cached) return cached

    // Return cached index.html for SPA routing
    const indexCached = await caches.match('/')
    if (indexCached) return indexCached

    return new Response('Offline', { status: 503 })
  }
}

// Stale-while-revalidate strategy
async function staleWhileRevalidate(request) {
  const cached = await caches.match(request)

  const fetchPromise = fetch(request)
    .then((response) => {
      if (response.ok) {
        const cache = caches.open(DYNAMIC_CACHE)
        cache.then(c => c.put(request, response.clone()))
      }
      return response
    })
    .catch(() => null)

  return cached || fetchPromise
}

// Stale-while-revalidate for API requests with metadata
async function staleWhileRevalidateApi(request) {
  const cache = await caches.open(API_CACHE)
  const cached = await cache.match(request)

  // Start network fetch in background
  const fetchPromise = fetch(request)
    .then(async (response) => {
      if (response.ok) {
        // Clone response and add timestamp metadata
        const responseToCache = response.clone()
        const headers = new Headers(responseToCache.headers)
        headers.set('sw-cached-at', Date.now().toString())

        const body = await responseToCache.blob()
        const newResponse = new Response(body, {
          status: responseToCache.status,
          statusText: responseToCache.statusText,
          headers: headers
        })

        cache.put(request, newResponse)
      }
      return response
    })
    .catch((error) => {
      console.log('[SW] API fetch failed, using cache:', error)
      return null
    })

  // If we have cached response, return it immediately
  if (cached) {
    // Check if cache is stale (optional: could add TTL check here)
    return cached
  }

  // No cache, wait for network
  const networkResponse = await fetchPromise
  if (networkResponse) {
    return networkResponse
  }

  // Both cache and network failed
  return new Response(JSON.stringify({ error: 'Offline', offline: true }), {
    status: 503,
    headers: { 'Content-Type': 'application/json' }
  })
}

// Push notification handler
self.addEventListener('push', (event) => {
  if (!event.data) return

  const data = event.data.json()

  const options = {
    body: data.body || '',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/'
    },
    actions: data.actions || []
  }

  event.waitUntil(
    self.registration.showNotification(data.title || 'AGTR Merkezi', options)
  )
})

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close()

  const url = event.notification.data?.url || '/'

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Check if there's already a window open
        for (const client of clientList) {
          if (client.url === url && 'focus' in client) {
            return client.focus()
          }
        }
        // Open new window
        if (clients.openWindow) {
          return clients.openWindow(url)
        }
      })
  )
})

// Background sync handler
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-pending-actions') {
    event.waitUntil(syncPendingActions())
  }
})

async function syncPendingActions() {
  // Get pending actions from IndexedDB and sync them
  console.log('[SW] Syncing pending actions...')
}
