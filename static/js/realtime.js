/*
 * AGTR Merkezi - Real-time Module v3.1
 * WebSocket connections, Live stats, Server monitoring
 * Auto-reconnect with exponential backoff
 */

// ==================== WEBSOCKET MANAGER ====================
const WebSocketManager = {
    connections: {},
    reconnectAttempts: {},
    maxReconnectAttempts: 10,
    baseReconnectDelay: 1000,
    maxReconnectDelay: 30000,
    
    getReconnectDelay(attempt) {
        // Exponential backoff with jitter
        const delay = Math.min(
            this.baseReconnectDelay * Math.pow(2, attempt),
            this.maxReconnectDelay
        );
        // Add random jitter (±20%)
        const jitter = delay * 0.2 * (Math.random() - 0.5);
        return Math.floor(delay + jitter);
    },
    
    connect(endpoint, handlers = {}) {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url = `${wsProtocol}//${window.location.host}/ws/${endpoint}`;
        
        if (this.connections[endpoint]) {
            this.connections[endpoint].close();
        }
        
        const ws = new WebSocket(url);
        
        ws.onopen = () => {
            console.log(`[WS] Connected: ${endpoint}`);
            this.reconnectAttempts[endpoint] = 0;
            if (handlers.onOpen) handlers.onOpen();
            // Dispatch connected event
            window.dispatchEvent(new CustomEvent('ws:connected', { detail: { endpoint } }));
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (handlers.onMessage) handlers.onMessage(data);
            } catch (e) {
                console.error('[WS] Parse error:', e);
            }
        };
        
        ws.onerror = (error) => {
            console.error(`[WS] Error: ${endpoint}`, error);
            if (handlers.onError) handlers.onError(error);
        };
        
        ws.onclose = (event) => {
            console.log(`[WS] Disconnected: ${endpoint} (code: ${event.code})`);
            if (handlers.onClose) handlers.onClose();
            
            // Dispatch disconnected event
            window.dispatchEvent(new CustomEvent('ws:disconnected', { detail: { endpoint } }));
            
            // Auto reconnect with exponential backoff
            if (this.reconnectAttempts[endpoint] < this.maxReconnectAttempts) {
                const attempt = this.reconnectAttempts[endpoint]++;
                const delay = this.getReconnectDelay(attempt);
                console.log(`[WS] Reconnecting: ${endpoint} in ${delay}ms (attempt ${attempt + 1}/${this.maxReconnectAttempts})`);
                setTimeout(() => {
                    this.connect(endpoint, handlers);
                }, delay);
            } else {
                console.warn(`[WS] Max reconnect attempts reached: ${endpoint}`);
                window.dispatchEvent(new CustomEvent('ws:failed', { detail: { endpoint } }));
            }
        };
        
        this.connections[endpoint] = ws;
        return ws;
    },
    
    send(endpoint, data) {
        const ws = this.connections[endpoint];
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(data));
            return true;
        }
        return false;
    },
    
    disconnect(endpoint) {
        const ws = this.connections[endpoint];
        if (ws) {
            this.reconnectAttempts[endpoint] = this.maxReconnectAttempts; // Prevent reconnect
            ws.close();
            delete this.connections[endpoint];
        }
    },
    
    disconnectAll() {
        Object.keys(this.connections).forEach(endpoint => {
            this.disconnect(endpoint);
        });
    }
};

// ==================== SERVER STATS ====================
const ServerStats = {
    widgets: {},
    updateInterval: null,
    
    init() {
        // Find all server stat widgets
        document.querySelectorAll('[data-server-stats]').forEach(widget => {
            const serverId = widget.getAttribute('data-server-stats');
            this.widgets[serverId] = widget;
        });
        
        // Connect to WebSocket for real-time updates
        WebSocketManager.connect('server-stats', {
            onMessage: (data) => this.handleUpdate(data)
        });
        
        // Fallback: Poll every 30 seconds if WebSocket fails
        this.startPolling();
    },
    
    handleUpdate(data) {
        const { server_id, stats } = data;
        const widget = this.widgets[server_id];
        
        if (!widget) return;
        
        // Update player count
        const playerEl = widget.querySelector('[data-stat="players"]');
        if (playerEl) {
            const current = parseInt(playerEl.textContent) || 0;
            const newValue = stats.players || 0;
            this.animateValue(playerEl, current, newValue);
        }
        
        // Update CPU
        const cpuEl = widget.querySelector('[data-stat="cpu"]');
        if (cpuEl) {
            cpuEl.textContent = `${stats.cpu || 0}%`;
            this.updateProgressBar(widget, 'cpu', stats.cpu);
        }
        
        // Update RAM
        const ramEl = widget.querySelector('[data-stat="ram"]');
        if (ramEl) {
            ramEl.textContent = `${stats.ram || 0}%`;
            this.updateProgressBar(widget, 'ram', stats.ram);
        }
        
        // Update status
        const statusEl = widget.querySelector('[data-stat="status"]');
        if (statusEl) {
            statusEl.className = `server-status ${stats.status}`;
            statusEl.textContent = this.getStatusText(stats.status);
        }
        
        // Update uptime
        const uptimeEl = widget.querySelector('[data-stat="uptime"]');
        if (uptimeEl && stats.uptime) {
            uptimeEl.textContent = this.formatUptime(stats.uptime);
        }
        
        // Update map
        const mapEl = widget.querySelector('[data-stat="map"]');
        if (mapEl) {
            mapEl.textContent = stats.map || '-';
        }
    },
    
    animateValue(el, start, end) {
        const duration = 500;
        const startTime = performance.now();
        
        const update = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(start + (end - start) * progress);
            el.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        };
        
        requestAnimationFrame(update);
    },
    
    updateProgressBar(widget, type, value) {
        const bar = widget.querySelector(`[data-progress="${type}"]`);
        if (bar) {
            bar.style.width = `${value}%`;
            
            // Color based on value
            if (value > 80) {
                bar.classList.add('red');
                bar.classList.remove('green', 'blue');
            } else if (value > 50) {
                bar.classList.add('blue');
                bar.classList.remove('green', 'red');
            } else {
                bar.classList.add('green');
                bar.classList.remove('blue', 'red');
            }
        }
    },
    
    getStatusText(status) {
        const texts = {
            online: 'Çevrimiçi',
            offline: 'Çevrimdışı',
            starting: 'Başlatılıyor',
            stopping: 'Durduruluyor',
            restarting: 'Yeniden Başlatılıyor'
        };
        return texts[status] || status;
    },
    
    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (days > 0) return `${days}g ${hours}s`;
        if (hours > 0) return `${hours}s ${minutes}d`;
        return `${minutes}d`;
    },
    
    startPolling() {
        if (this.updateInterval) clearInterval(this.updateInterval);
        
        this.updateInterval = setInterval(() => {
            Object.keys(this.widgets).forEach(serverId => {
                this.fetchStats(serverId);
            });
        }, 30000);
    },
    
    async fetchStats(serverId) {
        try {
            const response = await fetch(`/api/servers/${serverId}/stats`);
            if (response.ok) {
                const stats = await response.json();
                this.handleUpdate({ server_id: serverId, stats });
            }
        } catch (e) {
            console.error(`Failed to fetch stats for server ${serverId}:`, e);
        }
    },
    
    destroy() {
        WebSocketManager.disconnect('server-stats');
        if (this.updateInterval) clearInterval(this.updateInterval);
    }
};

// ==================== DASHBOARD STATS ====================
const DashboardStats = {
    init() {
        WebSocketManager.connect('dashboard', {
            onMessage: (data) => this.handleUpdate(data)
        });
    },
    
    handleUpdate(data) {
        // Total servers online
        this.updateStat('total-online', data.total_online);
        
        // Total players
        this.updateStat('total-players', data.total_players);
        
        // Today's revenue
        this.updateStat('today-revenue', data.today_revenue, '₺');
        
        // Active users
        this.updateStat('active-users', data.active_users);
        
        // Server health
        if (data.server_health) {
            this.updateHealthChart(data.server_health);
        }
    },
    
    updateStat(id, value, prefix = '') {
        const el = document.querySelector(`[data-dashboard="${id}"]`);
        if (el) {
            const current = parseInt(el.textContent.replace(/[^\d]/g, '')) || 0;
            this.animateValue(el, current, value, prefix);
        }
    },
    
    animateValue(el, start, end, prefix = '') {
        const duration = 1000;
        const startTime = performance.now();
        
        const update = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            
            const current = Math.floor(start + (end - start) * eased);
            el.textContent = prefix + current.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        };
        
        requestAnimationFrame(update);
    },
    
    updateHealthChart(health) {
        // Update health indicators
        Object.entries(health).forEach(([server, status]) => {
            const indicator = document.querySelector(`[data-health="${server}"]`);
            if (indicator) {
                indicator.className = `health-indicator ${status}`;
            }
        });
    }
};

// ==================== NOTIFICATIONS ====================
const RealtimeNotifications = {
    init() {
        WebSocketManager.connect('notifications', {
            onMessage: (data) => this.handleNotification(data)
        });
    },
    
    handleNotification(data) {
        const { type, title, message, link } = data;
        
        // Show toast
        if (window.Toast) {
            window.Toast[type]?.(message, title);
        }
        
        // Update notification badge
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            const count = parseInt(badge.textContent) || 0;
            badge.textContent = count + 1;
            badge.classList.add('has-notifications');
        }
        
        // Browser notification (if permitted)
        if (Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/images/logo.png'
            });
        }
    },
    
    requestPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
};

// ==================== CHAT / MESSAGING ====================
const RealtimeChat = {
    currentRoom: null,
    
    joinRoom(roomId) {
        if (this.currentRoom) {
            WebSocketManager.send('chat', { action: 'leave', room: this.currentRoom });
        }
        
        this.currentRoom = roomId;
        
        WebSocketManager.connect('chat', {
            onOpen: () => {
                WebSocketManager.send('chat', { action: 'join', room: roomId });
            },
            onMessage: (data) => this.handleMessage(data)
        });
    },
    
    sendMessage(message) {
        if (!this.currentRoom) return;
        
        WebSocketManager.send('chat', {
            action: 'message',
            room: this.currentRoom,
            message
        });
    },
    
    handleMessage(data) {
        const { type, message, user, timestamp } = data;
        
        const chatContainer = document.querySelector('.chat-messages');
        if (!chatContainer) return;
        
        const msgEl = document.createElement('div');
        msgEl.className = `chat-message ${type}`;
        msgEl.innerHTML = `
            <span class="chat-user">${user}</span>
            <span class="chat-text">${this.escapeHtml(message)}</span>
            <span class="chat-time">${new Date(timestamp).toLocaleTimeString()}</span>
        `;
        
        chatContainer.appendChild(msgEl);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    },
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    leaveRoom() {
        if (this.currentRoom) {
            WebSocketManager.send('chat', { action: 'leave', room: this.currentRoom });
            this.currentRoom = null;
        }
        WebSocketManager.disconnect('chat');
    }
};

// ==================== WORLD MAP (Players Location) ====================
const WorldMap = {
    map: null,
    markers: [],
    
    init(containerId = 'world-map') {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Using Leaflet.js for map
        if (typeof L === 'undefined') {
            console.warn('Leaflet.js not loaded');
            return;
        }
        
        this.map = L.map(containerId).setView([39.9, 32.85], 3);
        
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(this.map);
        
        // Connect to WebSocket for player locations
        WebSocketManager.connect('player-locations', {
            onMessage: (data) => this.updateMarkers(data)
        });
    },
    
    updateMarkers(data) {
        // Clear existing markers
        this.markers.forEach(marker => this.map.removeLayer(marker));
        this.markers = [];
        
        // Add new markers
        data.locations.forEach(loc => {
            const marker = L.circleMarker([loc.lat, loc.lng], {
                radius: 6,
                fillColor: '#00ff88',
                color: '#00ff88',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(this.map);
            
            marker.bindPopup(`
                <strong>${loc.country}</strong><br>
                ${loc.players} oyuncu
            `);
            
            this.markers.push(marker);
        });
    }
};

// ==================== ACTIVITY FEED ====================
const ActivityFeed = {
    container: null,
    maxItems: 20,
    
    init() {
        this.container = document.querySelector('.activity-feed');
        if (!this.container) return;
        
        WebSocketManager.connect('activity', {
            onMessage: (data) => this.addItem(data)
        });
    },
    
    addItem(data) {
        const { type, message, timestamp, icon } = data;
        
        const item = document.createElement('div');
        item.className = `activity-item activity-${type} slide-up`;
        item.innerHTML = `
            <span class="activity-icon">${icon || '📌'}</span>
            <div class="activity-content">
                <span class="activity-message">${message}</span>
                <span class="activity-time">${this.formatTime(timestamp)}</span>
            </div>
        `;
        
        this.container.insertBefore(item, this.container.firstChild);
        
        // Remove old items
        while (this.container.children.length > this.maxItems) {
            this.container.lastChild.remove();
        }
    },
    
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = (now - date) / 1000;
        
        if (diff < 60) return 'Az önce';
        if (diff < 3600) return `${Math.floor(diff / 60)} dk önce`;
        if (diff < 86400) return `${Math.floor(diff / 3600)} saat önce`;
        return date.toLocaleDateString();
    }
};

// ==================== LEADERBOARD ====================
const Leaderboard = {
    container: null,
    currentType: 'kills',
    
    init() {
        this.container = document.querySelector('.leaderboard-list');
        if (!this.container) return;
        
        // Tab switching
        document.querySelectorAll('[data-leaderboard-type]').forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchType(tab.getAttribute('data-leaderboard-type'));
            });
        });
        
        // Connect to WebSocket
        WebSocketManager.connect('leaderboard', {
            onMessage: (data) => this.update(data)
        });
    },
    
    switchType(type) {
        this.currentType = type;
        
        document.querySelectorAll('[data-leaderboard-type]').forEach(tab => {
            tab.classList.toggle('active', tab.getAttribute('data-leaderboard-type') === type);
        });
        
        WebSocketManager.send('leaderboard', { type });
    },
    
    update(data) {
        if (data.type !== this.currentType) return;
        
        this.container.innerHTML = data.players.map((player, index) => `
            <div class="leaderboard-item">
                <span class="leaderboard-rank ${this.getRankClass(index)}">${index + 1}</span>
                <img src="${player.avatar || '/static/images/default-avatar.png'}" class="leaderboard-avatar" alt="">
                <div class="leaderboard-info">
                    <span class="leaderboard-name">${player.name}</span>
                    <span class="leaderboard-stats">${player.server}</span>
                </div>
                <span class="leaderboard-score">${player.score.toLocaleString()}</span>
            </div>
        `).join('');
    },
    
    getRankClass(index) {
        if (index === 0) return 'gold';
        if (index === 1) return 'silver';
        if (index === 2) return 'bronze';
        return '';
    }
};

// ==================== INITIALIZE ====================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize based on page content
    if (document.querySelector('[data-server-stats]')) {
        ServerStats.init();
    }
    
    if (document.querySelector('[data-dashboard]')) {
        DashboardStats.init();
    }
    
    if (document.querySelector('.notification-badge')) {
        RealtimeNotifications.init();
        RealtimeNotifications.requestPermission();
    }
    
    if (document.querySelector('.activity-feed')) {
        ActivityFeed.init();
    }
    
    if (document.querySelector('.leaderboard-list')) {
        Leaderboard.init();
    }
    
    if (document.getElementById('world-map')) {
        WorldMap.init();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    WebSocketManager.disconnectAll();
});

// Export
window.Realtime = {
    WebSocketManager,
    ServerStats,
    DashboardStats,
    RealtimeChat,
    WorldMap
};
