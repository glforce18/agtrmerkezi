/**
 * AGTR Merkezi - Performance Utilities
 * Lazy loading, skeleton screens, optimizasyonlar
 */

// ============================================
// LAZY LOADING - Intersection Observer API
// ============================================

class LazyLoader {
    constructor() {
        this.imageObserver = null;
        this.init();
    }

    init() {
        // Intersection Observer desteği kontrolü
        if ('IntersectionObserver' in window) {
            this.imageObserver = new IntersectionObserver(
                (entries, observer) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const img = entry.target;
                            this.loadImage(img);
                            observer.unobserve(img);
                        }
                    });
                },
                {
                    rootMargin: '50px 0px', // 50px önce yüklemeye başla
                    threshold: 0.01
                }
            );

            // Mevcut lazy image'ları observe et
            this.observeImages();

            // Dinamik içerik için MutationObserver
            this.observeDOMChanges();
        } else {
            // Fallback: Hemen yükle
            this.loadAllImages();
        }
    }

    observeImages() {
        const lazyImages = document.querySelectorAll('img[data-src], img[loading="lazy"]');
        lazyImages.forEach(img => {
            if (img.dataset.src) {
                this.imageObserver.observe(img);
            }
        });
    }

    loadImage(img) {
        const src = img.dataset.src || img.src;
        const srcset = img.dataset.srcset;

        // Skeleton'u kaldır
        img.classList.remove('skeleton');

        // Önce placeholder göster
        if (!img.src || img.src.includes('placeholder')) {
            img.style.opacity = '0';
        }

        // Gerçek resmi yükle
        const tempImg = new Image();
        tempImg.onload = () => {
            img.src = src;
            if (srcset) img.srcset = srcset;

            // Fade-in animasyonu
            img.style.transition = 'opacity 0.3s ease-in-out';
            img.style.opacity = '1';

            img.classList.add('loaded');
            img.removeAttribute('data-src');
            img.removeAttribute('data-srcset');
        };
        tempImg.onerror = () => {
            console.warn('Image failed to load:', src);
            img.src = '/static/images/placeholder.svg';
            img.style.opacity = '1';
        };
        tempImg.src = src;
    }

    loadAllImages() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => this.loadImage(img));
    }

    observeDOMChanges() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) {
                        if (node.tagName === 'IMG' && node.dataset.src) {
                            this.imageObserver.observe(node);
                        }
                        // Alt elementleri kontrol et
                        const imgs = node.querySelectorAll?.('img[data-src]');
                        imgs?.forEach(img => this.imageObserver.observe(img));
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
}

// ============================================
// SKELETON SCREENS
// ============================================

class SkeletonLoader {
    static show(container, type = 'default') {
        const skeletons = {
            'card': `
                <div class="skeleton-card">
                    <div class="skeleton skeleton-image"></div>
                    <div class="skeleton skeleton-title"></div>
                    <div class="skeleton skeleton-text"></div>
                    <div class="skeleton skeleton-text short"></div>
                </div>
            `,
            'list': `
                <div class="skeleton-list">
                    ${Array(5).fill('<div class="skeleton skeleton-list-item"></div>').join('')}
                </div>
            `,
            'table': `
                <div class="skeleton-table">
                    ${Array(8).fill(`
                        <div class="skeleton-row">
                            <div class="skeleton skeleton-cell"></div>
                            <div class="skeleton skeleton-cell"></div>
                            <div class="skeleton skeleton-cell"></div>
                        </div>
                    `).join('')}
                </div>
            `,
            'default': '<div class="skeleton skeleton-block"></div>'
        };

        if (container) {
            container.innerHTML = skeletons[type] || skeletons.default;
            container.classList.add('loading');
        }
    }

    static hide(container) {
        if (container) {
            container.classList.remove('loading');
        }
    }
}

// ============================================
// PERFORMANCE MONITORING
// ============================================

class PerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.init();
    }

    init() {
        // Core Web Vitals
        if ('PerformanceObserver' in window) {
            try {
                // Largest Contentful Paint (LCP)
                const lcpObserver = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    this.metrics.lcp = lastEntry.renderTime || lastEntry.loadTime;
                    console.log('📊 LCP:', this.metrics.lcp.toFixed(2), 'ms');
                });
                lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

                // First Input Delay (FID)
                const fidObserver = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach(entry => {
                        this.metrics.fid = entry.processingStart - entry.startTime;
                        console.log('📊 FID:', this.metrics.fid.toFixed(2), 'ms');
                    });
                });
                fidObserver.observe({ entryTypes: ['first-input'] });

                // Cumulative Layout Shift (CLS)
                let clsValue = 0;
                const clsObserver = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (!entry.hadRecentInput) {
                            clsValue += entry.value;
                            this.metrics.cls = clsValue;
                            console.log('📊 CLS:', this.metrics.cls.toFixed(3));
                        }
                    }
                });
                clsObserver.observe({ entryTypes: ['layout-shift'] });

            } catch (e) {
                console.warn('Performance monitoring not fully supported:', e);
            }
        }

        // Navigation Timing
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    console.log('📊 Page Load Metrics:', {
                        'DNS Lookup': (perfData.domainLookupEnd - perfData.domainLookupStart).toFixed(2) + 'ms',
                        'TCP Connect': (perfData.connectEnd - perfData.connectStart).toFixed(2) + 'ms',
                        'Request': (perfData.responseStart - perfData.requestStart).toFixed(2) + 'ms',
                        'Response': (perfData.responseEnd - perfData.responseStart).toFixed(2) + 'ms',
                        'DOM Processing': (perfData.domComplete - perfData.domLoading).toFixed(2) + 'ms',
                        'Total Load': (perfData.loadEventEnd - perfData.fetchStart).toFixed(2) + 'ms'
                    });
                }
            }, 0);
        });
    }

    getMetrics() {
        return this.metrics;
    }
}

// ============================================
// PREFETCH & PRELOAD
// ============================================

class ResourcePreloader {
    static prefetchPage(url) {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = url;
        document.head.appendChild(link);
    }

    static preloadImage(url) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'image';
        link.href = url;
        document.head.appendChild(link);
    }

    static preloadFont(url) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'font';
        link.type = 'font/woff2';
        link.crossOrigin = 'anonymous';
        link.href = url;
        document.head.appendChild(link);
    }
}

// ============================================
// DEBOUNCE & THROTTLE
// ============================================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============================================
// INITIALIZATION
// ============================================

let lazyLoader, perfMonitor;

document.addEventListener('DOMContentLoaded', () => {
    // Lazy loading başlat
    lazyLoader = new LazyLoader();
    console.log('✅ Lazy loading initialized');

    // Performance monitoring başlat (sadece debug modda)
    if (window.location.hostname === 'localhost' || window.location.search.includes('debug=1')) {
        perfMonitor = new PerformanceMonitor();
        console.log('✅ Performance monitoring enabled');
    }

    // Hover ile prefetch (navigation links)
    document.querySelectorAll('a[href^="/"]').forEach(link => {
        link.addEventListener('mouseenter', debounce(() => {
            const url = link.getAttribute('href');
            if (url && !url.startsWith('#')) {
                ResourcePreloader.prefetchPage(url);
            }
        }, 100), { once: true });
    });
});

// Export
window.LazyLoader = LazyLoader;
window.SkeletonLoader = SkeletonLoader;
window.PerformanceMonitor = PerformanceMonitor;
window.ResourcePreloader = ResourcePreloader;
window.debounce = debounce;
window.throttle = throttle;
