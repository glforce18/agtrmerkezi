/**
 * AGTR Merkezi - Initialization & Global Setup
 * Tüm componentleri başlat ve global helper'ları tanımla
 */

// Global AGTR namespace
window.AGTR = window.AGTR || {};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('%c🎮 AGTR Merkezi v5.5', 'color: #ff6b00; font-size: 16px; font-weight: bold;');
    
    // Initialize components
    initializeAnimations();
    initializeScrollEffects();
    initializeTooltips();
    
    console.log('✅ System initialized');
});

/**
 * Initialize scroll-based animations
 */
function initializeAnimations() {
    const reveals = document.querySelectorAll('.reveal');
    
    if (!reveals.length) return;
    
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    reveals.forEach(reveal => revealObserver.observe(reveal));
}

/**
 * Initialize scroll effects for navbar
 */
function initializeScrollEffects() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;
    
    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        // Hide on scroll down, show on scroll up
        if (currentScroll > lastScroll && currentScroll > 200) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScroll = currentScroll;
    });
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(el => {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const text = e.target.getAttribute('data-tooltip');
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.id = 'active-tooltip';
    
    document.body.appendChild(tooltip);
    
    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.bottom + 8 + 'px';
    
    setTimeout(() => tooltip.classList.add('visible'), 10);
}

function hideTooltip() {
    const tooltip = document.getElementById('active-tooltip');
    if (tooltip) {
        tooltip.classList.remove('visible');
        setTimeout(() => tooltip.remove(), 200);
    }
}

/**
 * Global Search Handler
 */
AGTR.GlobalSearch = {
    open: function() {
        const modal = document.getElementById('search-modal');
        const input = document.getElementById('global-search-input');
        
        if (modal) {
            modal.classList.add('active');
            setTimeout(() => input?.focus(), 100);
        }
    },
    
    close: function() {
        const modal = document.getElementById('search-modal');
        if (modal) {
            modal.classList.remove('active');
        }
    }
};

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+K or Cmd+K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        AGTR.GlobalSearch.open();
    }
    
    // ESC to close modals
    if (e.key === 'Escape') {
        AGTR.GlobalSearch.close();
        // Close other modals too
        document.querySelectorAll('.modal.active, .search-modal.active').forEach(m => {
            m.classList.remove('active');
        });
    }
});

// Click outside search modal to close
document.getElementById('search-modal')?.addEventListener('click', (e) => {
    if (e.target.id === 'search-modal') {
        AGTR.GlobalSearch.close();
    }
});

/**
 * Utility Functions
 */
AGTR.utils = {
    // Format date
    formatDate: function(date) {
        return new Date(date).toLocaleDateString('tr-TR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    
    // Time ago
    timeAgo: function(date) {
        const seconds = Math.floor((new Date() - new Date(date)) / 1000);
        
        const intervals = {
            yıl: 31536000,
            ay: 2592000,
            hafta: 604800,
            gün: 86400,
            saat: 3600,
            dakika: 60
        };
        
        for (const [name, value] of Object.entries(intervals)) {
            const interval = Math.floor(seconds / value);
            if (interval >= 1) {
                return `${interval} ${name} önce`;
            }
        }
        
        return 'Az önce';
    },
    
    // Copy to clipboard
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            AGTR.toast?.show('Kopyalandı!', 'success');
        });
    },
    
    // Debounce function
    debounce: function(func, wait) {
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
};

console.log('✅ AGTR utilities loaded');
