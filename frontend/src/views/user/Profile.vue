<template>
  <div class="min-h-screen bg-gradient-to-b from-dark-bg via-dark-card to-dark-bg py-8">
    <div class="container mx-auto px-4">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-20">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/20 mb-4">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
        <p class="text-text-secondary">Profil yükleniyor...</p>
      </div>

      <div v-else-if="user" class="max-w-6xl mx-auto space-y-6">
        <!-- Hero Section -->
        <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary/20 via-dark-card to-dark-elevated border border-primary/30 shadow-2xl">
          <!-- Background Pattern -->
          <div class="absolute inset-0 opacity-5">
            <div class="absolute inset-0" style="background-image: radial-gradient(circle at 2px 2px, white 1px, transparent 0); background-size: 40px 40px;"></div>
          </div>

          <div class="relative p-8">
            <div class="flex flex-col md:flex-row items-center md:items-start gap-6">
              <!-- Avatar -->
              <div class="relative group">
                <div class="w-32 h-32 rounded-2xl bg-gradient-to-br from-primary to-orange-600 p-1 shadow-2xl shadow-primary/50">
                  <div class="w-full h-full rounded-xl overflow-hidden bg-dark-elevated">
                    <img v-if="user.avatar" :src="user.avatar" :alt="user.username" class="w-full h-full object-cover" />
                    <div v-else class="w-full h-full flex items-center justify-center">
                      <span class="text-white text-4xl font-bold">{{ getInitials(user.username) }}</span>
                    </div>
                  </div>
                </div>
                <!-- Status Indicator -->
                <div class="absolute bottom-2 right-2 w-6 h-6 rounded-full bg-green-500 border-4 border-dark-card"></div>
              </div>

              <!-- User Info -->
              <div class="flex-1 text-center md:text-left">
                <div class="flex flex-col md:flex-row md:items-center gap-3 mb-3">
                  <h1 class="text-4xl font-bold text-white">{{ user.username }}</h1>
                  <span class="inline-flex items-center px-3 py-1 rounded-lg text-sm font-semibold" :class="getRoleBadgeClass(user.role)">
                    <span class="mr-1">{{ getRoleIcon(user.role) }}</span>
                    {{ getRoleText(user.role) }}
                  </span>
                </div>

                <div class="flex flex-wrap items-center justify-center md:justify-start gap-4 text-sm text-text-secondary mb-4">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                    <span>Üyelik: {{ formatDate(user.created_at) }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span>Son giriş: {{ formatRelativeTime(user.last_login) }}</span>
                  </div>
                  <div v-if="user.steam_id" class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2a10 10 0 0 0-10 10 10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2zm0 18a8 8 0 0 1-8-8 8 8 0 0 1 8-8 8 8 0 0 1 8 8 8 8 0 0 1-8 8z"/>
                    </svg>
                    <span class="text-blue-400">Steam Bağlı</span>
                  </div>
                </div>

                <div class="flex flex-wrap gap-3 justify-center md:justify-start">
                  <button @click="showEditModal = true" class="btn btn-primary">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                    Profili Düzenle
                  </button>
                  <router-link to="/wallet" class="btn btn-secondary">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
                    </svg>
                    Cüzdanım
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <!-- Wallet Balance -->
          <div class="card group hover:border-amber-500/50 transition-all duration-300">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center shadow-lg shadow-amber-500/30 group-hover:scale-110 transition-transform">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div class="flex-1">
                <div class="text-xs text-text-muted mb-1">TL Bakiye</div>
                <div class="text-2xl font-bold text-amber-400">{{ formatBalance(user.balance) }}₺</div>
              </div>
            </div>
          </div>

          <!-- Armor Coins -->
          <div class="card group hover:border-primary/50 transition-all duration-300">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary to-orange-600 flex items-center justify-center shadow-lg shadow-primary/30 group-hover:scale-110 transition-transform">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                </svg>
              </div>
              <div class="flex-1">
                <div class="text-xs text-text-muted mb-1">Armor Coin</div>
                <div class="text-2xl font-bold text-primary">{{ formatArmorBalance(user.balance_coin) }}</div>
              </div>
            </div>
          </div>

          <!-- Active Servers -->
          <div class="card group hover:border-green-500/50 transition-all duration-300">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center shadow-lg shadow-green-500/30 group-hover:scale-110 transition-transform">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"/>
                </svg>
              </div>
              <div class="flex-1">
                <div class="text-xs text-text-muted mb-1">Aktif Sunucu</div>
                <div class="text-2xl font-bold text-white">{{ user.server_count || 0 }}</div>
              </div>
            </div>
          </div>

          <!-- Total Spent -->
          <div class="card group hover:border-purple-500/50 transition-all duration-300">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/30 group-hover:scale-110 transition-transform">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
                </svg>
              </div>
              <div class="flex-1">
                <div class="text-xs text-text-muted mb-1">Toplam Harcama</div>
                <div class="text-2xl font-bold text-purple-400">₺{{ formatMoney(user.total_spent) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Left Column - Account Info & Stats -->
          <div class="lg:col-span-2 space-y-6">
            <!-- Gaming Stats -->
            <div class="card">
              <div class="flex items-center justify-between mb-6">
                <h2 class="text-2xl font-bold text-white flex items-center gap-2">
                  <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                  </svg>
                  Oyun İstatistikleri
                </h2>
              </div>

              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-dark-elevated rounded-xl p-4 border border-dark-border hover:border-primary/30 transition-colors">
                  <div class="text-text-muted text-xs mb-1">ELO Rating</div>
                  <div class="text-2xl font-bold text-primary">{{ user.elo || 1500 }}</div>
                  <div class="text-xs text-green-500 mt-1">+12 bu ay</div>
                </div>

                <div class="bg-dark-elevated rounded-xl p-4 border border-dark-border hover:border-primary/30 transition-colors">
                  <div class="text-text-muted text-xs mb-1">Kazanma Oranı</div>
                  <div class="text-2xl font-bold text-green-400">{{ user.win_rate || 52 }}%</div>
                  <div class="text-xs text-text-muted mt-1">{{ user.wins || 0 }}W / {{ user.losses || 0 }}L</div>
                </div>

                <div class="bg-dark-elevated rounded-xl p-4 border border-dark-border hover:border-primary/30 transition-colors">
                  <div class="text-text-muted text-xs mb-1">K/D Oranı</div>
                  <div class="text-2xl font-bold text-blue-400">{{ user.kd_ratio || 1.2 }}</div>
                  <div class="text-xs text-text-muted mt-1">{{ user.kills || 0 }} / {{ user.deaths || 0 }}</div>
                </div>

                <div class="bg-dark-elevated rounded-xl p-4 border border-dark-border hover:border-primary/30 transition-colors">
                  <div class="text-text-muted text-xs mb-1">Toplam Oyun</div>
                  <div class="text-2xl font-bold text-amber-400">{{ user.total_matches || 0 }}</div>
                  <div class="text-xs text-text-muted mt-1">{{ user.playtime_hours || 0 }} saat</div>
                </div>
              </div>
            </div>

            <!-- Community Stats -->
            <div class="card">
              <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                </svg>
                Topluluk Aktivitesi
              </h2>

              <div class="grid grid-cols-3 gap-4">
                <div class="text-center p-4 bg-dark-elevated rounded-xl border border-dark-border">
                  <div class="text-3xl font-bold text-primary mb-1">{{ user.post_count || 0 }}</div>
                  <div class="text-xs text-text-muted">Forum Mesajı</div>
                </div>

                <div class="text-center p-4 bg-dark-elevated rounded-xl border border-dark-border">
                  <div class="text-3xl font-bold text-amber-400 mb-1">{{ user.reputation || 0 }}</div>
                  <div class="text-xs text-text-muted">İtibar Puanı</div>
                </div>

                <div class="text-center p-4 bg-dark-elevated rounded-xl border border-dark-border">
                  <div class="text-3xl font-bold text-green-400 mb-1">{{ user.helpful_count || 0 }}</div>
                  <div class="text-xs text-text-muted">Yardımcı Cevap</div>
                </div>
              </div>
            </div>

            <!-- Recent Activity -->
            <div class="card">
              <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                Son Aktiviteler
              </h2>

              <div v-if="activities.length" class="space-y-3">
                <div v-for="activity in activities" :key="activity.id" class="flex items-start gap-4 p-4 bg-dark-elevated rounded-xl border border-dark-border hover:border-primary/30 transition-colors">
                  <div class="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center text-xl flex-shrink-0">
                    {{ getActivityIcon(activity.type) }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-white mb-1">{{ activity.description }}</div>
                    <div class="text-xs text-text-muted">{{ formatRelativeTime(activity.created_at) }}</div>
                  </div>
                </div>
              </div>

              <div v-else class="text-center py-12">
                <div class="text-6xl mb-4 opacity-20">📊</div>
                <p class="text-text-muted">Henüz aktivite bulunmuyor</p>
              </div>
            </div>
          </div>

          <!-- Right Column - Account Details -->
          <div class="space-y-6">
            <!-- Account Info -->
            <div class="card">
              <h2 class="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
                Hesap Bilgileri
              </h2>

              <div class="space-y-4">
                <div class="pb-4 border-b border-dark-border">
                  <label class="block text-text-muted text-xs mb-1">Kullanıcı Adı</label>
                  <div class="text-white font-semibold">{{ user.username }}</div>
                </div>

                <div v-if="user.email" class="pb-4 border-b border-dark-border">
                  <label class="block text-text-muted text-xs mb-1">E-posta</label>
                  <div class="text-white">{{ user.email }}</div>
                </div>

                <div v-if="user.steam_id" class="pb-4 border-b border-dark-border">
                  <label class="block text-text-muted text-xs mb-1">Steam ID</label>
                  <div class="text-white font-mono text-sm">{{ user.steam_id }}</div>
                </div>

                <div class="pb-4 border-b border-dark-border">
                  <label class="block text-text-muted text-xs mb-1">Hesap Durumu</label>
                  <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-green-500"></span>
                    <span class="text-white">Aktif</span>
                  </div>
                </div>

                <div>
                  <label class="block text-text-muted text-xs mb-1">Üyelik Tarihi</label>
                  <div class="text-white">{{ formatFullDate(user.created_at) }}</div>
                </div>
              </div>
            </div>

            <!-- Security -->
            <div class="card">
              <h2 class="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                Güvenlik
              </h2>

              <div class="space-y-4">
                <!-- Steam Connection -->
                <div class="p-4 rounded-xl border" :class="user.steam_id ? 'bg-green-500/10 border-green-500/30' : 'bg-dark-elevated border-dark-border'">
                  <div class="flex items-center justify-between mb-2">
                    <div class="flex items-center gap-2">
                      <svg class="w-5 h-5" :class="user.steam_id ? 'text-blue-400' : 'text-text-muted'" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2a10 10 0 0 0-10 10 10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2zm0 18a8 8 0 0 1-8-8 8 8 0 0 1 8-8 8 8 0 0 1 8 8 8 8 0 0 1-8 8z"/>
                      </svg>
                      <span class="text-white font-semibold">Steam</span>
                    </div>
                    <span v-if="user.steam_id" class="text-xs text-green-500 font-semibold">✓ Bağlı</span>
                    <span v-else class="text-xs text-text-muted">Bağlı değil</span>
                  </div>
                  <div v-if="!user.steam_id" class="text-xs text-text-muted">
                    Steam hesabınızı bağlayarak giriş yapabilirsiniz
                  </div>
                </div>

                <!-- 2FA -->
                <div class="p-4 rounded-xl bg-dark-elevated border border-dark-border">
                  <div class="flex items-center justify-between mb-2">
                    <div class="flex items-center gap-2">
                      <svg class="w-5 h-5 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4"/>
                      </svg>
                      <span class="text-white font-semibold">2FA</span>
                    </div>
                    <span class="text-xs text-text-muted">Kapalı</span>
                  </div>
                  <div class="text-xs text-text-muted mb-3">
                    İki faktörlü kimlik doğrulama ile hesabınızı koruyun
                  </div>
                  <button class="w-full btn btn-secondary text-sm py-2">
                    Etkinleştir
                  </button>
                </div>
              </div>
            </div>

            <!-- Quick Links -->
            <div class="card">
              <h2 class="text-xl font-bold text-white mb-4">Hızlı Erişim</h2>
              <div class="space-y-2">
                <router-link to="/servers/my" class="flex items-center gap-3 p-3 rounded-lg bg-dark-elevated border border-dark-border hover:border-primary/50 transition-colors group">
                  <svg class="w-5 h-5 text-text-muted group-hover:text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"/>
                  </svg>
                  <span class="text-white group-hover:text-primary transition-colors">Sunucularım</span>
                </router-link>

                <router-link to="/wallet" class="flex items-center gap-3 p-3 rounded-lg bg-dark-elevated border border-dark-border hover:border-primary/50 transition-colors group">
                  <svg class="w-5 h-5 text-text-muted group-hover:text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
                  </svg>
                  <span class="text-white group-hover:text-primary transition-colors">Cüzdan</span>
                </router-link>

                <router-link to="/forum" class="flex items-center gap-3 p-3 rounded-lg bg-dark-elevated border border-dark-border hover:border-primary/50 transition-colors group">
                  <svg class="w-5 h-5 text-text-muted group-hover:text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"/>
                  </svg>
                  <span class="text-white group-hover:text-primary transition-colors">Forum</span>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 px-4">
      <div class="card max-w-md w-full">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold text-white">Profili Düzenle</h2>
          <button @click="showEditModal = false" class="text-text-muted hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <form @submit.prevent="handleUpdateProfile" class="space-y-4">
          <div v-if="user.steam_id" class="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 mb-4">
            <div class="flex items-center gap-2 text-blue-400 text-sm">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2a10 10 0 0 0-10 10 10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2zm0 18a8 8 0 0 1-8-8 8 8 0 0 1 8-8 8 8 0 0 1 8 8 8 8 0 0 1-8 8z"/>
              </svg>
              <span>Bu hesap Steam ile bağlı - E-posta gereksiz</span>
            </div>
          </div>

          <div v-if="user.email">
            <label class="block text-text-muted text-sm mb-2">E-posta</label>
            <input v-model="editForm.email" type="email" class="input" required />
          </div>

          <div>
            <label class="block text-text-muted text-sm mb-2">İmza</label>
            <textarea
              v-model="editForm.signature"
              rows="3"
              class="input"
              placeholder="Forum mesajlarınızda görünecek imza..."
              maxlength="200"
            ></textarea>
            <p class="text-text-muted text-xs mt-1">{{ editForm.signature?.length || 0 }}/200</p>
          </div>

          <div v-if="editError" class="alert alert-danger">
            {{ editError }}
          </div>

          <div class="flex gap-3 pt-4">
            <button type="button" @click="showEditModal = false" class="flex-1 btn btn-secondary">
              İptal
            </button>
            <button type="submit" :disabled="editLoading" class="flex-1 btn btn-primary" :class="{ 'opacity-50 cursor-not-allowed': editLoading }">
              {{ editLoading ? 'Kaydediliyor...' : 'Kaydet' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import authAPI from '@/api/auth'

const authStore = useAuthStore()

const loading = ref(true)
const user = ref(null)
const activities = ref([])

const showEditModal = ref(false)
const editForm = ref({
  email: '',
  signature: ''
})
const editLoading = ref(false)
const editError = ref(null)

onMounted(async () => {
  await fetchProfile()
})

const fetchProfile = async () => {
  try {
    const response = await authAPI.getMe()
    user.value = response.data
    editForm.value = {
      email: user.value.email || '',
      signature: user.value.signature || ''
    }

    // Fetch activities
    // TODO: Add activities API endpoint
  } catch (error) {
    console.error('Failed to fetch profile:', error)
  } finally {
    loading.value = false
  }
}

const handleUpdateProfile = async () => {
  editLoading.value = true
  editError.value = null

  try {
    await authAPI.updateProfile(editForm.value)
    await fetchProfile()
    showEditModal.value = false
  } catch (error) {
    editError.value = error.response?.data?.detail || 'Profil güncellenemedi'
  } finally {
    editLoading.value = false
  }
}

const getInitials = (username) => {
  if (!username) return '?'
  return username.substring(0, 2).toUpperCase()
}

const getRoleText = (role) => {
  const roles = {
    admin: 'Yönetici',
    moderator: 'Moderatör',
    user: 'Kullanıcı'
  }
  return roles[role] || 'Kullanıcı'
}

const getRoleIcon = (role) => {
  const icons = {
    admin: '👑',
    moderator: '⭐',
    user: '👤'
  }
  return icons[role] || '👤'
}

const getRoleBadgeClass = (role) => {
  const classes = {
    admin: 'bg-gradient-to-r from-amber-500 to-amber-600 text-white shadow-lg shadow-amber-500/30',
    moderator: 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/30',
    user: 'bg-dark-elevated text-text-secondary border border-dark-border'
  }
  return classes[role] || classes.user
}

const formatDate = (dateString) => {
  if (!dateString) return 'Bilinmiyor'

  const date = new Date(dateString)
  return date.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const formatFullDate = (dateString) => {
  if (!dateString) return 'Bilinmiyor'

  const date = new Date(dateString)
  return date.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatRelativeTime = (dateString) => {
  if (!dateString) return 'Bilinmiyor'

  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Şimdi'
  if (diffMins < 60) return `${diffMins} dakika önce`
  if (diffHours < 24) return `${diffHours} saat önce`
  if (diffDays === 1) return 'Dün'
  if (diffDays < 7) return `${diffDays} gün önce`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} hafta önce`

  return formatDate(dateString)
}

const formatMoney = (amount) => {
  if (!amount) return '0'
  return new Intl.NumberFormat('tr-TR').format(amount)
}

const formatBalance = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

const formatArmorBalance = (amount) => {
  if (!amount) return '0'
  const num = parseFloat(amount)
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toFixed(0)
}

const getActivityIcon = (type) => {
  const icons = {
    server_created: '🖥️',
    server_deleted: '🗑️',
    payment: '💳',
    forum_post: '💬',
    profile_update: '👤',
    login: '🔑',
    wallet_deposit: '💰',
    wallet_withdraw: '📤'
  }
  return icons[type] || '📝'
}
</script>

<style scoped>
/* Additional custom styles if needed */
</style>
