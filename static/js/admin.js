/*
 * AGTR Merkezi v5.0 - Admin Utilities
 * DataTables, WYSIWYG Editor, Drag & Drop
 */

// ==================== DATA TABLES WRAPPER ====================
const AGTRTable = {
    defaultConfig: {
        language: {
            search: "Ara:",
            lengthMenu: "_MENU_ kayıt göster",
            info: "_TOTAL_ kayıttan _START_ - _END_ arası",
            infoEmpty: "Kayıt bulunamadı",
            infoFiltered: "(_MAX_ kayıt içinden filtrelendi)",
            zeroRecords: "Eşleşen kayıt bulunamadı",
            emptyTable: "Tabloda veri yok",
            paginate: {
                first: "İlk",
                previous: "‹",
                next: "›",
                last: "Son"
            }
        },
        pageLength: 25,
        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Tümü"]],
        dom: '<"table-header"<"table-search"f><"table-length"l>><"table-wrapper"t><"table-footer"<"table-info"i><"table-pagination"p>>',
        responsive: true,
        autoWidth: false,
        order: [[0, 'desc']],
        drawCallback: function() {
            // After draw, init any tooltips
            if (window.Tooltip) Tooltip.init();
        }
    },
    
    init(selector, customConfig = {}) {
        const config = { ...this.defaultConfig, ...customConfig };
        
        // Check if DataTables is loaded
        if (typeof $.fn.DataTable === 'undefined') {
            console.warn('DataTables not loaded');
            return null;
        }
        
        return $(selector).DataTable(config);
    },
    
    // Server-side processing
    serverSide(selector, apiUrl, columns, customConfig = {}) {
        return this.init(selector, {
            processing: true,
            serverSide: true,
            ajax: {
                url: apiUrl,
                type: 'POST',
                contentType: 'application/json',
                data: (d) => JSON.stringify(d)
            },
            columns: columns,
            ...customConfig
        });
    },
    
    // Refresh table
    refresh(table) {
        if (table) {
            table.ajax.reload(null, false);
        }
    },
    
    // Destroy table
    destroy(table) {
        if (table) {
            table.destroy();
        }
    }
};

// ==================== WYSIWYG EDITOR ====================
const AGTREditor = {
    instances: {},
    
    init(selector, config = {}) {
        const defaultConfig = {
            modules: {
                toolbar: [
                    [{ 'header': [1, 2, 3, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    [{ 'color': [] }, { 'background': [] }],
                    [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                    [{ 'align': [] }],
                    ['link', 'image', 'code-block'],
                    ['clean']
                ]
            },
            theme: 'snow',
            placeholder: 'İçerik yazın...'
        };
        
        const mergedConfig = { ...defaultConfig, ...config };
        
        // Check if Quill is loaded
        if (typeof Quill === 'undefined') {
            console.warn('Quill not loaded, using textarea fallback');
            return null;
        }
        
        const element = document.querySelector(selector);
        if (!element) return null;
        
        const quill = new Quill(selector, mergedConfig);
        this.instances[selector] = quill;
        
        return quill;
    },
    
    // Get HTML content
    getContent(selector) {
        const quill = this.instances[selector];
        if (quill) {
            return quill.root.innerHTML;
        }
        return '';
    },
    
    // Set HTML content
    setContent(selector, html) {
        const quill = this.instances[selector];
        if (quill) {
            quill.root.innerHTML = html;
        }
    },
    
    // Get plain text
    getText(selector) {
        const quill = this.instances[selector];
        if (quill) {
            return quill.getText();
        }
        return '';
    },
    
    // Destroy editor
    destroy(selector) {
        if (this.instances[selector]) {
            delete this.instances[selector];
        }
    }
};

// ==================== DRAG & DROP SORTING ====================
const AGTRSortable = {
    instances: {},
    
    init(selector, options = {}) {
        // Check if Sortable is loaded
        if (typeof Sortable === 'undefined') {
            console.warn('SortableJS not loaded');
            return null;
        }
        
        const element = document.querySelector(selector);
        if (!element) return null;
        
        const defaultOptions = {
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            handle: '.drag-handle',
            onEnd: (evt) => {
                this.onSortEnd(evt, options.onSort);
            }
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        const sortable = Sortable.create(element, mergedOptions);
        
        this.instances[selector] = sortable;
        return sortable;
    },
    
    onSortEnd(evt, callback) {
        const items = Array.from(evt.to.children).map((el, index) => ({
            id: el.dataset.id,
            order: index + 1
        }));
        
        if (callback) {
            callback(items, evt);
        }
    },
    
    // Get current order
    getOrder(selector) {
        const sortable = this.instances[selector];
        if (sortable) {
            return sortable.toArray();
        }
        return [];
    },
    
    // Set order
    setOrder(selector, order) {
        const sortable = this.instances[selector];
        if (sortable) {
            sortable.sort(order);
        }
    },
    
    // Destroy
    destroy(selector) {
        const sortable = this.instances[selector];
        if (sortable) {
            sortable.destroy();
            delete this.instances[selector];
        }
    }
};

// ==================== SKELETON LOADING ====================
const Skeleton = {
    show(container, type = 'list', count = 5) {
        const element = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
        
        if (!element) return;
        
        let html = '';
        
        switch (type) {
            case 'list':
                for (let i = 0; i < count; i++) {
                    html += `
                        <div class="skeleton-item">
                            <div class="skeleton skeleton-avatar"></div>
                            <div class="skeleton-content">
                                <div class="skeleton skeleton-title"></div>
                                <div class="skeleton skeleton-text"></div>
                            </div>
                        </div>
                    `;
                }
                break;
                
            case 'table':
                html = '<div class="skeleton-table">';
                for (let i = 0; i < count; i++) {
                    html += `
                        <div class="skeleton-row">
                            <div class="skeleton skeleton-cell" style="width: 50px;"></div>
                            <div class="skeleton skeleton-cell" style="width: 150px;"></div>
                            <div class="skeleton skeleton-cell" style="width: 200px;"></div>
                            <div class="skeleton skeleton-cell" style="width: 100px;"></div>
                        </div>
                    `;
                }
                html += '</div>';
                break;
                
            case 'card':
                for (let i = 0; i < count; i++) {
                    html += `
                        <div class="skeleton-card">
                            <div class="skeleton skeleton-image"></div>
                            <div class="skeleton skeleton-title"></div>
                            <div class="skeleton skeleton-text"></div>
                            <div class="skeleton skeleton-text short"></div>
                        </div>
                    `;
                }
                break;
                
            case 'stats':
                for (let i = 0; i < count; i++) {
                    html += `
                        <div class="skeleton-stat">
                            <div class="skeleton skeleton-icon"></div>
                            <div class="skeleton skeleton-number"></div>
                            <div class="skeleton skeleton-label"></div>
                        </div>
                    `;
                }
                break;
        }
        
        element.innerHTML = html;
    },
    
    hide(container) {
        const element = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
        
        if (element) {
            element.innerHTML = '';
        }
    }
};

// Add skeleton styles
const skeletonStyles = document.createElement('style');
skeletonStyles.textContent = `
    .skeleton {
        background: linear-gradient(90deg, #2a2a4a 25%, #3a3a5a 50%, #2a2a4a 75%);
        background-size: 200% 100%;
        animation: skeletonShimmer 1.5s infinite;
        border-radius: 4px;
    }
    
    @keyframes skeletonShimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    .skeleton-item {
        display: flex;
        gap: 16px;
        padding: 16px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .skeleton-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    
    .skeleton-content {
        flex: 1;
    }
    
    .skeleton-title {
        height: 20px;
        width: 60%;
        margin-bottom: 8px;
    }
    
    .skeleton-text {
        height: 14px;
        width: 100%;
    }
    
    .skeleton-text.short {
        width: 40%;
    }
    
    .skeleton-row {
        display: flex;
        gap: 16px;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .skeleton-cell {
        height: 16px;
    }
    
    .skeleton-card {
        padding: 20px;
        background: var(--bg-card);
        border-radius: 12px;
        margin-bottom: 16px;
    }
    
    .skeleton-image {
        height: 150px;
        margin-bottom: 16px;
        border-radius: 8px;
    }
    
    .skeleton-stat {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        padding: 20px;
    }
    
    .skeleton-icon {
        width: 48px;
        height: 48px;
        border-radius: 50%;
    }
    
    .skeleton-number {
        width: 80px;
        height: 32px;
    }
    
    .skeleton-label {
        width: 100px;
        height: 14px;
    }
    
    /* Sortable styles */
    .sortable-ghost {
        opacity: 0.4;
        background: var(--neon-green);
    }
    
    .sortable-chosen {
        background: rgba(255, 107, 0, 0.1);
    }
    
    .sortable-drag {
        background: var(--bg-card);
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    
    .drag-handle {
        cursor: grab;
        padding: 8px;
        color: var(--text-secondary);
    }
    
    .drag-handle:active {
        cursor: grabbing;
    }
`;
document.head.appendChild(skeletonStyles);

// ==================== ACTIVITY TIMELINE ====================
const Timeline = {
    render(container, activities) {
        const element = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
        
        if (!element || !activities.length) return;
        
        const icons = {
            login: '🔐',
            logout: '🚪',
            purchase: '💰',
            server_create: '🖥️',
            server_delete: '🗑️',
            profile_update: '👤',
            password_change: '🔑',
            ticket_create: '📝',
            post_create: '💬',
            default: '📌'
        };
        
        const html = activities.map(activity => `
            <div class="timeline-item">
                <div class="timeline-icon">${icons[activity.type] || icons.default}</div>
                <div class="timeline-content">
                    <div class="timeline-title">${activity.title}</div>
                    <div class="timeline-description">${activity.description || ''}</div>
                    <div class="timeline-time">${this.formatTime(activity.timestamp)}</div>
                </div>
            </div>
        `).join('');
        
        element.innerHTML = `<div class="timeline">${html}</div>`;
    },
    
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        // Less than 1 minute
        if (diff < 60000) return 'Az önce';
        
        // Less than 1 hour
        if (diff < 3600000) {
            const mins = Math.floor(diff / 60000);
            return `${mins} dakika önce`;
        }
        
        // Less than 24 hours
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours} saat önce`;
        }
        
        // Less than 7 days
        if (diff < 604800000) {
            const days = Math.floor(diff / 86400000);
            return `${days} gün önce`;
        }
        
        // Otherwise show date
        return date.toLocaleDateString('tr-TR', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    }
};

// Add timeline styles
const timelineStyles = document.createElement('style');
timelineStyles.textContent = `
    .timeline {
        position: relative;
        padding-left: 30px;
    }
    
    .timeline::before {
        content: '';
        position: absolute;
        left: 12px;
        top: 0;
        bottom: 0;
        width: 2px;
        background: linear-gradient(to bottom, #ff6b00, #ff6b0033);
    }
    
    .timeline-item {
        position: relative;
        padding: 16px 0;
        display: flex;
        gap: 16px;
    }
    
    .timeline-icon {
        position: absolute;
        left: -30px;
        width: 24px;
        height: 24px;
        background: var(--bg-primary);
        border: 2px solid #ff6b00;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
    }
    
    .timeline-content {
        flex: 1;
        background: var(--bg-card);
        padding: 16px;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .timeline-title {
        font-weight: 600;
        margin-bottom: 4px;
    }
    
    .timeline-description {
        color: var(--text-secondary);
        font-size: 14px;
        margin-bottom: 8px;
    }
    
    .timeline-time {
        font-size: 12px;
        color: #ff6b00;
    }
`;
document.head.appendChild(timelineStyles);

// Export
window.AGTRTable = AGTRTable;
window.AGTREditor = AGTREditor;
window.AGTRSortable = AGTRSortable;
window.Skeleton = Skeleton;
window.Timeline = Timeline;
