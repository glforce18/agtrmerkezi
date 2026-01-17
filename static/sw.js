// AGTR Service Worker v5.3 - PWA Offline Support
const CACHE_NAME = 'agtr-v53';
const OFFLINE_URL = '/offline.html';

// Önbelleğe alınacak dosyalar
const PRECACHE_URLS = [
    '/',
    '/static/css/theme.css',
    '/static/css/animations.css',
    '/static/js/main.js',
    '/static/images/logo.svg',
    '/static/images/favicon.svg',
    '/static/images/default-avatar.svg'
];

// Install - Precache
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

// Activate - Eski cache'leri temizle
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(name => name !== CACHE_NAME)
                    .map(name => caches.delete(name))
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch - Network first, cache fallback
self.addEventListener('fetch', (event) => {
    // API ve WebSocket isteklerini cache'leme
    if (event.request.url.includes('/api/') || 
        event.request.url.includes('/ws/') ||
        event.request.method !== 'GET') {
        return;
    }
    
    event.respondWith(
        fetch(event.request)
            .then(response => {
                // Başarılı yanıtları cache'le
                if (response.status === 200) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            })
            .catch(() => {
                // Offline - cache'den getir
                return caches.match(event.request)
                    .then(cachedResponse => {
                        if (cachedResponse) {
                            return cachedResponse;
                        }
                        // HTML istekleri için offline sayfası
                        if (event.request.headers.get('accept').includes('text/html')) {
                            return caches.match(OFFLINE_URL);
                        }
                        return new Response('Offline', { status: 503 });
                    });
            })
    );
});
