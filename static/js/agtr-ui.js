/**
 * AGTR v6.0 - Toast & Modal Standart Sistemi
 * Dosya: static/js/agtr-ui.js
 * 
 * Tüm sayfalarda tutarlı toast bildirimleri ve modal işlemleri
 * Base template'e dahil edilmeli
 */

(function(window) {
    'use strict';

    // ============================================
    // TOAST NOTIFICATION SYSTEM
    // ============================================
    
    const TOAST_CONFIG = {
        maxToasts: 5,
        defaultDuration: 4000,
        position: 'top-right', // top-right, top-left, bottom-right, bottom-left, top-center, bottom-center
        showProgress: true,
        pauseOnHover: true,
        closeOnClick: true
    };

    const TOAST_TYPES = {
        success: {
            icon: 'fas fa-check-circle',
            bgClass: 'bg-success',
            title: 'Başarılı'
        },
        error: {
            icon: 'fas fa-times-circle',
            bgClass: 'bg-danger',
            title: 'Hata'
        },
        warning: {
            icon: 'fas fa-exclamation-triangle',
            bgClass: 'bg-warning',
            title: 'Uyarı'
        },
        info: {
            icon: 'fas fa-info-circle',
            bgClass: 'bg-info',
            title: 'Bilgi'
        }
    };

    let toastContainer = null;
    let activeToasts = [];

    function initToastContainer() {
        if (toastContainer) return toastContainer;

        toastContainer = document.createElement('div');
        toastContainer.id = 'agtr-toast-container';
        toastContainer.className = 'agtr-toast-container';
        
        // Position based on config
        const positionClasses = {
            'top-right': 'top-0 end-0',
            'top-left': 'top-0 start-0',
            'bottom-right': 'bottom-0 end-0',
            'bottom-left': 'bottom-0 start-0',
            'top-center': 'top-0 start-50 translate-middle-x',
            'bottom-center': 'bottom-0 start-50 translate-middle-x'
        };
        
        toastContainer.className = `agtr-toast-container position-fixed p-3 ${positionClasses[TOAST_CONFIG.position]}`;
        toastContainer.style.zIndex = '9999';
        toastContainer.style.maxWidth = '380px';
        toastContainer.style.width = '100%';
        
        document.body.appendChild(toastContainer);
        return toastContainer;
    }

    function showToast(message, type = 'info', options = {}) {
        const container = initToastContainer();
        const typeConfig = TOAST_TYPES[type] || TOAST_TYPES.info;
        const duration = options.duration || TOAST_CONFIG.defaultDuration;
        const title = options.title || typeConfig.title;

        // Max toast limit
        while (activeToasts.length >= TOAST_CONFIG.maxToasts) {
            const oldestToast = activeToasts.shift();
            if (oldestToast && oldestToast.element) {
                removeToast(oldestToast.element);
            }
        }

        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toastEl = document.createElement('div');
        toastEl.id = toastId;
        toastEl.className = 'toast show border-0 shadow-lg mb-2';
        toastEl.setAttribute('role', 'alert');
        toastEl.style.animation = 'slideInRight 0.3s ease-out';
        
        toastEl.innerHTML = `
            <div class="toast-header ${typeConfig.bgClass} text-white border-0">
                <i class="${typeConfig.icon} me-2"></i>
                <strong class="me-auto">${title}</strong>
                <small class="text-white-50">şimdi</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${escapeHtml(message)}
                ${TOAST_CONFIG.showProgress ? '<div class="toast-progress"><div class="toast-progress-bar"></div></div>' : ''}
            </div>
        `;

        container.appendChild(toastEl);

        // Track active toast
        const toastData = { id: toastId, element: toastEl, timeout: null };
        activeToasts.push(toastData);

        // Progress bar animation
        if (TOAST_CONFIG.showProgress) {
            const progressBar = toastEl.querySelector('.toast-progress-bar');
            if (progressBar) {
                progressBar.style.animation = `progressShrink ${duration}ms linear forwards`;
            }
        }

        // Close button
        const closeBtn = toastEl.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => removeToast(toastEl));
        }

        // Click to close
        if (TOAST_CONFIG.closeOnClick) {
            toastEl.addEventListener('click', (e) => {
                if (e.target !== closeBtn) {
                    removeToast(toastEl);
                }
            });
        }

        // Pause on hover
        if (TOAST_CONFIG.pauseOnHover) {
            toastEl.addEventListener('mouseenter', () => {
                if (toastData.timeout) {
                    clearTimeout(toastData.timeout);
                    toastData.timeout = null;
                }
                const progressBar = toastEl.querySelector('.toast-progress-bar');
                if (progressBar) {
                    progressBar.style.animationPlayState = 'paused';
                }
            });
            
            toastEl.addEventListener('mouseleave', () => {
                const progressBar = toastEl.querySelector('.toast-progress-bar');
                if (progressBar) {
                    progressBar.style.animationPlayState = 'running';
                }
                toastData.timeout = setTimeout(() => removeToast(toastEl), duration / 2);
            });
        }

        // Auto dismiss
        toastData.timeout = setTimeout(() => removeToast(toastEl), duration);

        return toastId;
    }

    function removeToast(toastEl) {
        if (!toastEl || !toastEl.parentNode) return;
        
        toastEl.style.animation = 'slideOutRight 0.3s ease-in forwards';
        
        setTimeout(() => {
            if (toastEl.parentNode) {
                toastEl.parentNode.removeChild(toastEl);
            }
            activeToasts = activeToasts.filter(t => t.element !== toastEl);
        }, 300);
    }

    function clearAllToasts() {
        activeToasts.forEach(toast => {
            if (toast.timeout) clearTimeout(toast.timeout);
            if (toast.element) removeToast(toast.element);
        });
        activeToasts = [];
    }


    // ============================================
    // MODAL SYSTEM
    // ============================================

    const MODAL_DEFAULTS = {
        size: 'md', // sm, md, lg, xl
        centered: true,
        backdrop: true,
        keyboard: true,
        focus: true
    };

    /**
     * Confirmation modal - Silme/Onay işlemleri için
     */
    function showConfirmModal(options = {}) {
        return new Promise((resolve) => {
            const {
                title = 'Emin misiniz?',
                message = 'Bu işlem geri alınamaz.',
                confirmText = 'Onayla',
                cancelText = 'İptal',
                confirmClass = 'btn-danger',
                icon = 'fas fa-exclamation-triangle',
                iconColor = 'text-warning'
            } = options;

            // Remove existing modal if any
            const existingModal = document.getElementById('agtr-confirm-modal');
            if (existingModal) {
                existingModal.remove();
            }

            const modalHtml = `
                <div class="modal fade" id="agtr-confirm-modal" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered modal-sm">
                        <div class="modal-content border-0 shadow">
                            <div class="modal-body text-center py-4">
                                <div class="mb-3">
                                    <i class="${icon} ${iconColor} fa-3x"></i>
                                </div>
                                <h5 class="mb-2">${escapeHtml(title)}</h5>
                                <p class="text-muted mb-0">${escapeHtml(message)}</p>
                            </div>
                            <div class="modal-footer border-0 justify-content-center pt-0">
                                <button type="button" class="btn btn-light" data-action="cancel">${escapeHtml(cancelText)}</button>
                                <button type="button" class="btn ${confirmClass}" data-action="confirm">
                                    ${escapeHtml(confirmText)}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            const modalEl = document.getElementById('agtr-confirm-modal');
            const modal = new bootstrap.Modal(modalEl);

            // Button handlers
            modalEl.querySelector('[data-action="confirm"]').addEventListener('click', () => {
                modal.hide();
                resolve(true);
            });

            modalEl.querySelector('[data-action="cancel"]').addEventListener('click', () => {
                modal.hide();
                resolve(false);
            });

            // Cleanup on hide
            modalEl.addEventListener('hidden.bs.modal', () => {
                modalEl.remove();
            });

            modal.show();
        });
    }

    /**
     * Alert modal - Bilgi mesajları için
     */
    function showAlertModal(options = {}) {
        return new Promise((resolve) => {
            const {
                title = 'Bilgi',
                message = '',
                buttonText = 'Tamam',
                icon = 'fas fa-info-circle',
                iconColor = 'text-primary'
            } = options;

            const existingModal = document.getElementById('agtr-alert-modal');
            if (existingModal) existingModal.remove();

            const modalHtml = `
                <div class="modal fade" id="agtr-alert-modal" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered modal-sm">
                        <div class="modal-content border-0 shadow">
                            <div class="modal-body text-center py-4">
                                <div class="mb-3">
                                    <i class="${icon} ${iconColor} fa-3x"></i>
                                </div>
                                <h5 class="mb-2">${escapeHtml(title)}</h5>
                                <p class="text-muted mb-0">${escapeHtml(message)}</p>
                            </div>
                            <div class="modal-footer border-0 justify-content-center pt-0">
                                <button type="button" class="btn btn-primary" data-action="ok">${escapeHtml(buttonText)}</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            const modalEl = document.getElementById('agtr-alert-modal');
            const modal = new bootstrap.Modal(modalEl);

            modalEl.querySelector('[data-action="ok"]').addEventListener('click', () => {
                modal.hide();
                resolve(true);
            });

            modalEl.addEventListener('hidden.bs.modal', () => {
                modalEl.remove();
            });

            modal.show();
        });
    }

    /**
     * Prompt modal - Kullanıcıdan input almak için
     */
    function showPromptModal(options = {}) {
        return new Promise((resolve) => {
            const {
                title = 'Değer Girin',
                message = '',
                placeholder = '',
                defaultValue = '',
                confirmText = 'Tamam',
                cancelText = 'İptal',
                inputType = 'text'
            } = options;

            const existingModal = document.getElementById('agtr-prompt-modal');
            if (existingModal) existingModal.remove();

            const modalHtml = `
                <div class="modal fade" id="agtr-prompt-modal" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content border-0 shadow">
                            <div class="modal-header border-0 pb-0">
                                <h5 class="modal-title">${escapeHtml(title)}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                ${message ? '<p class="text-muted">' + escapeHtml(message) + '</p>' : ''}
                                <input type="${inputType}" class="form-control" id="agtr-prompt-input" 
                                       placeholder="${escapeHtml(placeholder)}" value="${escapeHtml(defaultValue)}">
                            </div>
                            <div class="modal-footer border-0 pt-0">
                                <button type="button" class="btn btn-light" data-action="cancel">${escapeHtml(cancelText)}</button>
                                <button type="button" class="btn btn-primary" data-action="confirm">${escapeHtml(confirmText)}</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            const modalEl = document.getElementById('agtr-prompt-modal');
            const modal = new bootstrap.Modal(modalEl);
            const input = modalEl.querySelector('#agtr-prompt-input');

            modalEl.querySelector('[data-action="confirm"]').addEventListener('click', () => {
                modal.hide();
                resolve(input.value);
            });

            modalEl.querySelector('[data-action="cancel"]').addEventListener('click', () => {
                modal.hide();
                resolve(null);
            });

            // Enter key submit
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    modal.hide();
                    resolve(input.value);
                }
            });

            modalEl.addEventListener('hidden.bs.modal', () => {
                modalEl.remove();
            });

            modalEl.addEventListener('shown.bs.modal', () => {
                input.focus();
                input.select();
            });

            modal.show();
        });
    }


    // ============================================
    // LOADING OVERLAY
    // ============================================

    let loadingOverlay = null;

    function showLoading(message = 'Yükleniyor...') {
        if (loadingOverlay) return;

        loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'agtr-loading-overlay';
        loadingOverlay.className = 'agtr-loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="agtr-loading-content">
                <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Yükleniyor...</span>
                </div>
                <p class="mb-0 text-muted">${escapeHtml(message)}</p>
            </div>
        `;
        
        document.body.appendChild(loadingOverlay);
        document.body.style.overflow = 'hidden';
        
        // Fade in
        requestAnimationFrame(() => {
            loadingOverlay.classList.add('show');
        });
    }

    function hideLoading() {
        if (!loadingOverlay) return;
        
        loadingOverlay.classList.remove('show');
        
        setTimeout(() => {
            if (loadingOverlay && loadingOverlay.parentNode) {
                loadingOverlay.parentNode.removeChild(loadingOverlay);
            }
            loadingOverlay = null;
            document.body.style.overflow = '';
        }, 300);
    }


    // ============================================
    // UTILITY FUNCTIONS
    // ============================================

    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * API fetch wrapper with error handling
     */
    async function apiFetch(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, mergedOptions);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.message || 'API hatası');
            }

            return { success: true, data, response };
        } catch (error) {
            return { success: false, error: error.message, response: null };
        }
    }

    /**
     * Form serialize helper
     */
    function serializeForm(formEl) {
        const formData = new FormData(formEl);
        const data = {};
        formData.forEach((value, key) => {
            if (data[key]) {
                if (!Array.isArray(data[key])) {
                    data[key] = [data[key]];
                }
                data[key].push(value);
            } else {
                data[key] = value;
            }
        });
        return data;
    }


    // ============================================
    // EXPORT TO GLOBAL
    // ============================================

    window.AGTR = window.AGTR || {};
    
    // Toast functions
    window.AGTR.toast = showToast;
    window.AGTR.clearToasts = clearAllToasts;
    
    // For backward compatibility - global showToast
    window.showToast = showToast;

    // Modal functions
    window.AGTR.confirm = showConfirmModal;
    window.AGTR.alert = showAlertModal;
    window.AGTR.prompt = showPromptModal;

    // Loading
    window.AGTR.showLoading = showLoading;
    window.AGTR.hideLoading = hideLoading;

    // Utilities
    window.AGTR.fetch = apiFetch;
    window.AGTR.serializeForm = serializeForm;
    window.AGTR.escapeHtml = escapeHtml;

})(window);
