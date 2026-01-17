/*
 * AGTR Merkezi - Main JavaScript v5.2
 * Theme Toggle, Keyboard Shortcuts, Sound Effects, Core Functions
 * Bug fixes: Sound/Theme state persistence, Event dispatch
 */

// ==================== CSRF TOKEN HELPER ====================
const CSRF = {
    getToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    },
    
    getHeaders(extra = {}) {
        return {
            'Content-Type': 'application/json',
            'X-CSRF-Token': this.getToken(),
            ...extra
        };
    }
};

// Override fetch for automatic CSRF token
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    // Only add CSRF for same-origin non-GET requests
    if (options.method && options.method.toUpperCase() !== 'GET') {
        options.headers = options.headers || {};
        if (!options.headers['X-CSRF-Token']) {
            options.headers['X-CSRF-Token'] = CSRF.getToken();
        }
    }
    return originalFetch(url, options);
};

// ==================== THEME MANAGEMENT ====================
const Theme = {
    current: 'dark',
    
    init() {
        const saved = localStorage.getItem('agtr-theme') || 'dark';
        this.set(saved, false);
        
        // Theme toggle buttons
        document.querySelectorAll('.theme-toggle').forEach(btn => {
            btn.addEventListener('click', () => this.toggle());
        });
    },
    
    set(theme, dispatch = true) {
        this.current = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('agtr-theme', theme);
        
        // Update icons - dark mode: show sun, light mode: show moon
        const isDark = theme === 'dark';
        document.querySelectorAll('.icon-sun').forEach(el => el.style.display = isDark ? 'inline' : 'none');
        document.querySelectorAll('.icon-moon').forEach(el => el.style.display = isDark ? 'none' : 'inline');
        
        // Dispatch event for other components
        if (dispatch) {
            window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
        }
    },
    
    toggle() {
        this.set(this.current === 'dark' ? 'light' : 'dark');
        Sound.play('click');
    },
    
    isDark() {
        return this.current === 'dark';
    }
};

// ==================== SOUND EFFECTS (DISABLED) ====================
const Sound = {
    enabled: false,
    
    init() {
        // Ses özelliği devre dışı
        this.enabled = false;
    },
    
    play(name) {
        // Devre dışı
    },
    
    toggle() {
        // Devre dışı
    }
};

// ==================== TOAST NOTIFICATIONS ====================
const Toast = {
    container: null,
    queue: [],
    maxVisible: 5,
    isProcessing: false,
    
    init() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        this.container.innerHTML = '';
        document.body.appendChild(this.container);
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .toast-container {
                position: fixed;
                bottom: 20px;
                right: 20px;
                display: flex;
                flex-direction: column-reverse;
                gap: 10px;
                z-index: 3000;
                max-height: calc(100vh - 40px);
                overflow: hidden;
            }
            .toast {
                display: flex;
                align-items: flex-start;
                gap: 12px;
                padding: 16px;
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
                border-radius: var(--radius-md);
                box-shadow: var(--shadow-lg);
                min-width: 300px;
                max-width: 400px;
                animation: toastIn 0.3s ease;
            }
            .toast-exit {
                animation: toastOut 0.3s ease forwards;
            }
            @keyframes toastIn {
                from { opacity: 0; transform: translateX(100%); }
                to { opacity: 1; transform: translateX(0); }
            }
            @keyframes toastOut {
                from { opacity: 1; transform: translateX(0); }
                to { opacity: 0; transform: translateX(100%); }
            }
            .toast-success { border-left: 4px solid var(--neon-green); }
            .toast-error { border-left: 4px solid var(--neon-red); }
            .toast-warning { border-left: 4px solid var(--neon-yellow); }
            .toast-info { border-left: 4px solid var(--primary); }
            .toast-icon {
                font-size: 20px;
                line-height: 1;
            }
            .toast-content { flex: 1; }
            .toast-title {
                font-weight: 600;
                margin-bottom: 4px;
            }
            .toast-message {
                font-size: 14px;
                color: var(--text-secondary);
            }
            .toast-close {
                background: none;
                border: none;
                color: var(--text-muted);
                cursor: pointer;
                font-size: 18px;
                line-height: 1;
                padding: 0;
            }
            .toast-close:hover {
                color: var(--text-primary);
            }
            .toast-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: var(--primary-color);
                animation: toastProgress linear forwards;
            }
            @keyframes toastProgress {
                from { width: 100%; }
                to { width: 0%; }
            }
        `;
        document.head.appendChild(style);
    },
    
    show(message, type = 'info', title = '', duration = 4000) {
        if (!this.container) this.init();
        
        // Queue if too many visible
        const visibleToasts = this.container.querySelectorAll('.toast:not(.toast-exit)');
        if (visibleToasts.length >= this.maxVisible) {
            this.queue.push({ message, type, title, duration });
            return null;
        }
        
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        
        const titles = {
            success: 'Başarılı',
            error: 'Hata',
            warning: 'Uyarı',
            info: 'Bilgi'
        };
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.position = 'relative';
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <div class="toast-content">
                <div class="toast-title">${title || titles[type]}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">&times;</button>
            ${duration > 0 ? `<div class="toast-progress" style="animation-duration: ${duration}ms;"></div>` : ''}
        `;
        
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.hide(toast);
        });
        
        this.container.appendChild(toast);
        Sound.play('notification');
        
        if (duration > 0) {
            setTimeout(() => this.hide(toast), duration);
        }
        
        return toast;
    },
    
    hide(toast) {
        if (!toast || !toast.parentNode) return;
        toast.classList.add('toast-exit');
        setTimeout(() => {
            toast.remove();
            this.processQueue();
        }, 300);
    },
    
    processQueue() {
        if (this.queue.length === 0) return;
        const visibleToasts = this.container.querySelectorAll('.toast:not(.toast-exit)');
        if (visibleToasts.length < this.maxVisible) {
            const next = this.queue.shift();
            this.show(next.message, next.type, next.title, next.duration);
        }
    },
    
    clearAll() {
        this.queue = [];
        if (this.container) {
            this.container.querySelectorAll('.toast').forEach(t => this.hide(t));
        }
    },
    
    success(message, title) { return this.show(message, 'success', title); },
    error(message, title) { return this.show(message, 'error', title); },
    warning(message, title) { return this.show(message, 'warning', title); },
    info(message, title) { return this.show(message, 'info', title); }
};

// ==================== KEYBOARD SHORTCUTS ====================
const Shortcuts = {
    bindings: {},
    enabled: true,
    
    init() {
        document.addEventListener('keydown', (e) => this.handle(e));
        
        // Default shortcuts
        this.register('ctrl+k', () => GlobalSearch.open(), 'Arama aç');
        this.register('ctrl+/', () => this.showHelp(), 'Kısayolları göster');
        this.register('ctrl+d', () => Theme.toggle(), 'Tema değiştir');
        this.register('ctrl+m', () => Sound.toggle(), 'Ses aç/kapat');
        this.register('escape', () => this.closeModals(), 'Modalları kapat');
        
        // Navigation
        this.register('g+h', () => window.location.href = '/', 'Ana sayfa');
        this.register('g+s', () => window.location.href = '/servers', 'Sunucular');
        this.register('g+f', () => window.location.href = '/forum', 'Forum');
        this.register('g+p', () => window.location.href = '/panel', 'Panel');
    },
    
    register(shortcut, callback, description = '') {
        this.bindings[shortcut.toLowerCase()] = { callback, description };
    },
    
    handle(e) {
        if (!this.enabled) return;
        if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;
        if (e.target.contentEditable === 'true') return;
        
        const keys = [];
        if (e.ctrlKey || e.metaKey) keys.push('ctrl');
        if (e.shiftKey) keys.push('shift');
        if (e.altKey) keys.push('alt');
        
        const key = e.key.toLowerCase();
        if (!['control', 'shift', 'alt', 'meta'].includes(key)) {
            keys.push(key);
        }
        
        const combo = keys.join('+');
        
        if (this.bindings[combo]) {
            e.preventDefault();
            this.bindings[combo].callback();
        }
        
        // Handle sequential shortcuts (g+h style)
        if (this.lastKey && Date.now() - this.lastKeyTime < 500) {
            const seqCombo = `${this.lastKey}+${key}`;
            if (this.bindings[seqCombo]) {
                e.preventDefault();
                this.bindings[seqCombo].callback();
            }
        }
        
        this.lastKey = key;
        this.lastKeyTime = Date.now();
    },
    
    showHelp() {
        let html = '<div class="shortcuts-list">';
        Object.entries(this.bindings).forEach(([key, { description }]) => {
            if (description) {
                html += `
                    <div class="shortcut-item">
                        <kbd>${key.replace(/\+/g, ' + ').toUpperCase()}</kbd>
                        <span>${description}</span>
                    </div>
                `;
            }
        });
        html += '</div>';
        
        Modal.showContent('Klavye Kısayolları', html);
    },
    
    closeModals() {
        // Close search modal
        GlobalSearch.close();
        
        // Close other modals
        document.querySelectorAll('.modal-overlay.active').forEach(modal => {
            Modal.hide(modal.id);
        });
    }
};

// ==================== MODAL MANAGEMENT ====================
const Modal = {
    init() {
        // Close on overlay click
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.hide(overlay.id);
                }
            });
        });
        
        // Close buttons
        document.querySelectorAll('[data-modal-close]').forEach(btn => {
            btn.addEventListener('click', () => {
                const modal = btn.closest('.modal-overlay');
                if (modal) this.hide(modal.id);
            });
        });
    },
    
    show(id) {
        const modal = document.getElementById(id);
        if (!modal) return;
        
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        Sound.play('click');
    },
    
    hide(id) {
        const modal = document.getElementById(id);
        if (!modal) return;
        
        modal.classList.remove('active');
        document.body.style.overflow = '';
    },
    
    showContent(title, content) {
        // Create dynamic modal
        let modal = document.getElementById('dynamic-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'dynamic-modal';
            modal.className = 'modal-overlay';
            modal.innerHTML = `
                <div class="modal-container">
                    <div class="modal-header">
                        <h3 class="modal-title"></h3>
                        <button class="modal-close" onclick="Modal.hide('dynamic-modal')">&times;</button>
                    </div>
                    <div class="modal-body"></div>
                </div>
            `;
            document.body.appendChild(modal);
            
            modal.addEventListener('click', (e) => {
                if (e.target === modal) this.hide('dynamic-modal');
            });
        }
        
        modal.querySelector('.modal-title').textContent = title;
        modal.querySelector('.modal-body').innerHTML = content;
        this.show('dynamic-modal');
    }
};

// ==================== GLOBAL SEARCH ====================
const GlobalSearch = {
    isOpen: false,
    searchTimeout: null,
    
    init() {
        const input = document.getElementById('global-search-input');
        if (input) {
            input.addEventListener('input', (e) => {
                clearTimeout(this.searchTimeout);
                const query = e.target.value.trim();
                
                if (query.length < 2) {
                    this.showHint();
                    return;
                }
                
                this.searchTimeout = setTimeout(() => this.search(query), 300);
            });
        }
        
        // Close on outside click
        const modal = document.getElementById('search-modal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) this.close();
            });
        }
    },
    
    toggle() {
        this.isOpen ? this.close() : this.open();
    },
    
    open() {
        const modal = document.getElementById('search-modal');
        if (modal) {
            modal.classList.add('active');
            this.isOpen = true;
            document.getElementById('global-search-input')?.focus();
        }
    },
    
    close() {
        const modal = document.getElementById('search-modal');
        if (modal) {
            modal.classList.remove('active');
            this.isOpen = false;
            
            // Clear input
            const input = document.getElementById('global-search-input');
            if (input) input.value = '';
            
            this.showHint();
        }
    },
    
    showHint() {
        const results = document.getElementById('search-results');
        if (results) {
            results.innerHTML = '<p class="search-hint">Kullanıcı, forum, sunucu ara...</p>';
        }
    },
    
    async search(query) {
        const results = document.getElementById('search-results');
        if (!results) return;
        
        results.innerHTML = '<div class="search-loading"><div class="spinner"></div> Aranıyor...</div>';
        
        try {
            const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            this.render(data);
        } catch (e) {
            results.innerHTML = '<p class="search-error">Arama hatası</p>';
        }
    },
    
    render(data) {
        const results = document.getElementById('search-results');
        if (!results) return;
        
        let html = '';
        const categories = [
            { key: 'users', title: 'Kullanıcılar', icon: '👤' },
            { key: 'forum', title: 'Forum', icon: '💬' },
            { key: 'servers', title: 'Sunucular', icon: '🖥️' },
            { key: 'announcements', title: 'Duyurular', icon: '📢' }
        ];
        
        let hasResults = false;
        
        categories.forEach(cat => {
            if (data[cat.key]?.length > 0) {
                hasResults = true;
                html += `<div class="search-group"><h4>${cat.icon} ${cat.title}</h4>`;
                data[cat.key].forEach(item => {
                    html += `
                        <a href="${item.url}" class="search-item" onclick="GlobalSearch.close()">
                            <div class="search-item-title">${item.title}</div>
                            ${item.subtitle ? `<div class="search-item-subtitle">${item.subtitle}</div>` : ''}
                        </a>
                    `;
                });
                html += '</div>';
            }
        });
        
        results.innerHTML = hasResults ? html : '<p class="search-empty">Sonuç bulunamadı</p>';
    }
};

// ==================== NOTIFICATIONS ====================
const Notifications = {
    count: 0,
    
    init() {
        this.load();
        setInterval(() => this.load(), 60000);
    },
    
    async load() {
        try {
            const res = await fetch('/api/notifications/count');
            const data = await res.json();
            this.count = data.count || 0;
            this.updateBadge();
        } catch (e) {}
    },
    
    updateBadge() {
        document.querySelectorAll('.notif-badge').forEach(badge => {
            badge.textContent = this.count;
            badge.style.display = this.count > 0 ? 'flex' : 'none';
        });
    }
};

// ==================== NAVBAR SCROLL EFFECT ====================
const Navbar = {
    init() {
        const navbar = document.getElementById('navbar');
        if (!navbar) return;
        
        let lastScroll = 0;
        
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll > 100) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
            
            lastScroll = currentScroll;
        });
    }
};

// ==================== RIPPLE EFFECT ====================
const Ripple = {
    init() {
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const rect = btn.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const ripple = document.createElement('span');
                ripple.className = 'ripple';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                
                btn.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            });
        });
    }
};

// ==================== CLIPBOARD ====================
const Clipboard = {
    init() {
        document.querySelectorAll('[data-copy]').forEach(btn => {
            btn.addEventListener('click', () => {
                const text = btn.getAttribute('data-copy');
                this.copy(text);
            });
        });
    },
    
    async copy(text) {
        try {
            await navigator.clipboard.writeText(text);
            Toast.success('Kopyalandı!');
            Sound.play('success');
        } catch (e) {
            // Fallback
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            textarea.remove();
            Toast.success('Kopyalandı!');
        }
    }
};

// ==================== TOOLTIP ====================
const Tooltip = {
    init() {
        document.querySelectorAll('[data-tooltip]').forEach(el => {
            el.addEventListener('mouseenter', (e) => this.show(e.target));
            el.addEventListener('mouseleave', () => this.hide());
        });
    },
    
    show(el) {
        const text = el.getAttribute('data-tooltip');
        if (!text) return;
        
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        document.body.appendChild(tooltip);
        
        const rect = el.getBoundingClientRect();
        tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
        
        this.current = tooltip;
    },
    
    hide() {
        if (this.current) {
            this.current.remove();
            this.current = null;
        }
    }
};

// ==================== LAZY LOAD ====================
const LazyLoad = {
    init() {
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                        }
                        observer.unobserve(img);
                    }
                });
            });
            
            document.querySelectorAll('img[data-src]').forEach(img => {
                observer.observe(img);
            });
        }
    }
};

// ==================== API HELPERS ====================
const API = {
    baseURL: '/api',
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Bir hata oluştu');
            }
            
            return data;
        } catch (error) {
            Toast.error(error.message);
            throw error;
        }
    },
    
    get(endpoint) {
        return this.request(endpoint);
    },
    
    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
};

// ==================== FORM VALIDATOR ====================
const FormValidator = {
    init() {
        document.querySelectorAll('form[data-validate]').forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validate(form)) {
                    e.preventDefault();
                }
            });
        });
    },
    
    validate(form) {
        let isValid = true;
        
        // Clear previous errors
        form.querySelectorAll('.form-error').forEach(el => el.remove());
        form.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
        
        // Required fields
        form.querySelectorAll('[required]').forEach(input => {
            if (!input.value.trim()) {
                this.showError(input, 'Bu alan zorunludur');
                isValid = false;
            }
        });
        
        // Email validation
        form.querySelectorAll('[type="email"]').forEach(input => {
            if (input.value && !this.isEmail(input.value)) {
                this.showError(input, 'Geçerli bir e-posta girin');
                isValid = false;
            }
        });
        
        // Min length
        form.querySelectorAll('[minlength]').forEach(input => {
            const min = parseInt(input.getAttribute('minlength'));
            if (input.value.length < min) {
                this.showError(input, `En az ${min} karakter olmalı`);
                isValid = false;
            }
        });
        
        // Password match
        const password = form.querySelector('[name="password"]');
        const confirm = form.querySelector('[name="password_confirm"]');
        if (password && confirm && password.value !== confirm.value) {
            this.showError(confirm, 'Şifreler eşleşmiyor');
            isValid = false;
        }
        
        return isValid;
    },
    
    showError(input, message) {
        input.classList.add('error');
        const error = document.createElement('span');
        error.className = 'form-error';
        error.textContent = message;
        input.parentNode.appendChild(error);
    },
    
    isEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }
};

// ==================== COUNTER ANIMATION ====================
const Counter = {
    init() {
        const counters = document.querySelectorAll('[data-counter]');
        if (!counters.length) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animate(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });
        
        counters.forEach(counter => observer.observe(counter));
    },
    
    animate(el) {
        const target = parseInt(el.textContent) || 0;
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const update = () => {
            current += step;
            if (current < target) {
                el.textContent = Math.floor(current).toLocaleString();
                requestAnimationFrame(update);
            } else {
                el.textContent = target.toLocaleString();
            }
        };
        
        update();
    }
};

// ==================== SCROLL REVEAL ====================
const ScrollReveal = {
    init() {
        const elements = document.querySelectorAll('[data-reveal]');
        if (!elements.length) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        elements.forEach(el => observer.observe(el));
    }
};

// ==================== FLOATING ACTION BUTTON ====================
const FAB = {
    init() {
        // Scroll to top button
        const scrollBtn = document.getElementById('scroll-top-btn');
        if (scrollBtn) {
            window.addEventListener('scroll', () => {
                if (window.pageYOffset > 500) {
                    scrollBtn.classList.add('visible');
                } else {
                    scrollBtn.classList.remove('visible');
                }
            });
            
            scrollBtn.addEventListener('click', () => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
    }
};

// ==================== TYPEWRITER EFFECT ====================
const Typewriter = {
    init() {
        document.querySelectorAll('[data-typewriter]').forEach(el => {
            const text = el.getAttribute('data-typewriter') || el.textContent;
            el.textContent = '';
            this.type(el, text, 0);
        });
    },
    
    type(el, text, index) {
        if (index < text.length) {
            el.textContent += text.charAt(index);
            setTimeout(() => this.type(el, text, index + 1), 50);
        }
    }
};

// ==================== INITIALIZE ====================
document.addEventListener('DOMContentLoaded', () => {
    // Core
    Theme.init();
    Toast.init();
    Sound.init();
    Modal.init();
    Shortcuts.init();
    GlobalSearch.init();
    Notifications.init();
    
    // UI Enhancements
    Navbar.init();
    Ripple.init();
    Clipboard.init();
    Tooltip.init();
    LazyLoad.init();
    FormValidator.init();
    Counter.init();
    ScrollReveal.init();
    FAB.init();
    Typewriter.init();
    
    console.log('%c🎮 AGTR Merkezi v5.1 Part3', 'color: #ff6b00; font-size: 20px; font-weight: bold;');
    console.log('%cHalf-Life & CS 1.6 Gaming Platform', 'color: #a0a0b0;');
});

// ==================== PAGINATION HELPER ====================
const Pagination = {
    render(container, currentPage, totalPages, onPageChange) {
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        let html = '<div class="pagination">';
        
        // Previous button
        html += `<button class="pagination-btn" ${currentPage === 1 ? 'disabled' : ''} onclick="Pagination.goTo(${currentPage - 1})">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M15 18l-6-6 6-6"/>
            </svg>
        </button>`;
        
        // Page numbers
        const delta = 2;
        const range = [];
        const rangeWithDots = [];
        
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - delta && i <= currentPage + delta)) {
                range.push(i);
            }
        }
        
        let l;
        for (let i of range) {
            if (l) {
                if (i - l === 2) {
                    rangeWithDots.push(l + 1);
                } else if (i - l !== 1) {
                    rangeWithDots.push('...');
                }
            }
            rangeWithDots.push(i);
            l = i;
        }
        
        for (let i of rangeWithDots) {
            if (i === '...') {
                html += '<span class="pagination-ellipsis">...</span>';
            } else {
                html += `<button class="pagination-btn ${i === currentPage ? 'active' : ''}" onclick="Pagination.goTo(${i})">${i}</button>`;
            }
        }
        
        // Next button
        html += `<button class="pagination-btn" ${currentPage === totalPages ? 'disabled' : ''} onclick="Pagination.goTo(${currentPage + 1})">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 18l6-6-6-6"/>
            </svg>
        </button>`;
        
        html += '</div>';
        container.innerHTML = html;
        
        // Store callback
        this._onPageChange = onPageChange;
    },
    
    goTo(page) {
        if (this._onPageChange) {
            this._onPageChange(page);
        }
    }
};

// ==================== LOADING HELPER ====================
const Loading = {
    overlay: null,
    textEl: null,
    
    init() {
        this.overlay = document.getElementById('loadingOverlay');
        this.textEl = document.getElementById('loadingText');
    },
    
    show(text = 'Yükleniyor...') {
        if (!this.overlay) this.init();
        if (this.overlay) {
            if (this.textEl) this.textEl.textContent = text;
            this.overlay.classList.add('active');
        }
    },
    
    hide() {
        if (!this.overlay) this.init();
        if (this.overlay) {
            this.overlay.classList.remove('active');
        }
    },
    
    // Button loading state
    setButtonLoading(btn, loading = true) {
        if (!btn) return;
        if (loading) {
            btn.dataset.originalText = btn.innerHTML;
            btn.classList.add('loading');
            btn.disabled = true;
        } else {
            btn.classList.remove('loading');
            btn.innerHTML = btn.dataset.originalText || btn.innerHTML;
            btn.disabled = false;
        }
    },
    
    // Async wrapper
    async wrap(promise, text = 'Yükleniyor...') {
        this.show(text);
        try {
            return await promise;
        } finally {
            this.hide();
        }
    }
};

// ==================== SKELETON HELPER ====================
const Skeleton = {
    // Create skeleton for table
    table(rows = 5, cols = 4) {
        let html = '<table class="table"><tbody>';
        for (let i = 0; i < rows; i++) {
            html += '<tr>';
            for (let j = 0; j < cols; j++) {
                html += `<td><div class="skeleton skeleton-text" style="width: ${60 + Math.random() * 40}%"></div></td>`;
            }
            html += '</tr>';
        }
        html += '</tbody></table>';
        return html;
    },
    
    // Create skeleton for cards
    cards(count = 3) {
        let html = '<div class="grid grid-3">';
        for (let i = 0; i < count; i++) {
            html += `
                <div class="card">
                    <div class="skeleton skeleton-card" style="height: 150px; margin-bottom: 16px;"></div>
                    <div class="skeleton skeleton-title"></div>
                    <div class="skeleton skeleton-text"></div>
                    <div class="skeleton skeleton-text"></div>
                </div>
            `;
        }
        html += '</div>';
        return html;
    },
    
    // Create skeleton for list
    list(count = 5) {
        let html = '';
        for (let i = 0; i < count; i++) {
            html += `
                <div style="display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--border-color);">
                    <div class="skeleton skeleton-avatar"></div>
                    <div style="flex: 1;">
                        <div class="skeleton skeleton-text" style="width: 40%;"></div>
                        <div class="skeleton skeleton-text" style="width: 70%;"></div>
                    </div>
                </div>
            `;
        }
        return html;
    }
};

// ==================== GLOBAL EXPORTS ====================
window.AGTR = {
    Theme,
    Sound,
    Toast,
    Shortcuts,
    Modal,
    GlobalSearch,
    Notifications,
    API,
    Clipboard,
    Pagination,
    Loading,
    Skeleton
};
