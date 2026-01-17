/**
 * AGTR Merkezi - UI Components JavaScript
 * Scroll Animations, Counter, Lazy Loading
 * Note: Toast and Modal are in main.js
 */

// ==================== SCROLL ANIMATIONS ====================

class ScrollAnimations {
    constructor() {
        this.elements = document.querySelectorAll('.reveal');
        this.observer = null;
        this.init();
    }

    init() {
        if (!this.elements.length) return;

        const options = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                }
            });
        }, options);

        this.elements.forEach(el => this.observer.observe(el));
    }

    refresh() {
        this.elements = document.querySelectorAll('.reveal');
        this.elements.forEach(el => {
            if (!el.classList.contains('active')) {
                this.observer.observe(el);
            }
        });
    }
}

// ==================== COUNTER ANIMATION ====================

class CounterAnimation {
    static animate(element, duration = 2000) {
        const target = parseInt(element.dataset.target || element.textContent);
        if (isNaN(target)) return;

        const start = 0;
        const increment = target / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 16);
    }

    static init() {
        const counters = document.querySelectorAll('[data-counter], .counter');
        if (!counters.length) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.dataset.animated) {
                    this.animate(entry.target);
                    entry.target.dataset.animated = 'true';
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(counter => observer.observe(counter));
    }
}

// ==================== DROPDOWN ====================

class Dropdown {
    static init() {
        const dropdowns = document.querySelectorAll('.dropdown');
        if (!dropdowns.length) return;

        dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            const menu = dropdown.querySelector('.dropdown-menu');

            if (toggle && menu) {
                toggle.addEventListener('click', (e) => {
                    e.stopPropagation();
                    menu.classList.toggle('show');
                });

                document.addEventListener('click', () => {
                    menu.classList.remove('show');
                });
            }
        });
    }
}

// ==================== LAZY LOADING IMAGES ====================

class LazyLoader {
    static init() {
        const images = document.querySelectorAll('img[data-src]');
        if (!images.length) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });

        images.forEach(img => observer.observe(img));
    }
}

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', () => {
    try {
        // Initialize all components
        new ScrollAnimations();
        CounterAnimation.init();
        Dropdown.init();
        LazyLoader.init();

        // Expose to window for external use
        window.AGTR = window.AGTR || {};
        window.AGTR.CounterAnimation = CounterAnimation;
        window.AGTR.ScrollAnimations = ScrollAnimations;

        console.log('✅ Components initialized');
    } catch (error) {
        console.error('Component initialization error:', error);
    }
});
