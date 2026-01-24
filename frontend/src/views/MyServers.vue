<template>
  <div class="min-h-screen server-panel">
    <!-- Animated Background -->
    <div class="panel-bg">
      <div class="bg-gradient"></div>
      <div class="bg-grid"></div>
    </div>

    <div class="container mx-auto max-w-7xl px-4 py-8 relative z-10">
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 class="text-3xl md:text-4xl font-bold text-white flex items-center gap-3">
            <div class="p-3 bg-orange-500/20 rounded-xl">
              <svg class="w-8 h-8 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
              </svg>
            </div>
            Sunucu Paneli
          </h1>
          <p class="text-gray-400 mt-2">Sunucularınızı tam kontrol ile yönetin</p>
        </div>
        <button
          @click="goToShop"
          class="btn-primary flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          Sunucu Kirala
        </button>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div class="stat-card">
          <div class="stat-icon bg-orange-500/20 text-orange-500">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2" />
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-white">{{ servers.length }}</div>
            <div class="text-sm text-gray-400">Toplam Sunucu</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon bg-green-500/20 text-green-500">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z" />
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-white">{{ runningCount }}</div>
            <div class="text-sm text-gray-400">Çalışıyor</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon bg-blue-500/20 text-blue-500">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-white">{{ totalPlayers }}</div>
            <div class="text-sm text-gray-400">Aktif Oyuncu</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon bg-purple-500/20 text-purple-500">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-white">{{ totalAdmins }}</div>
            <div class="text-sm text-gray-400">Toplam Admin</div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20">
        <div class="loading-spinner"></div>
        <p class="mt-4 text-gray-400">Sunucular yükleniyor...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="glass-card p-8 text-center">
        <div class="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-white mb-2">Bir Hata Oluştu</h3>
        <p class="text-gray-400 mb-4">{{ error }}</p>
        <button @click="fetchServers" class="btn-primary">Tekrar Dene</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="servers.length === 0" class="glass-card p-12 text-center">
        <div class="w-20 h-20 bg-gray-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-10 h-10 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2" />
          </svg>
        </div>
        <h3 class="text-2xl font-bold text-white mb-2">Henüz Sunucunuz Yok</h3>
        <p class="text-gray-400 mb-6 max-w-md mx-auto">
          Premium paketlerimizden birini satın alarak kendi sunucunuza sahip olun!
        </p>
        <button @click="goToShop" class="btn-primary">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          Sunucu Kirala
        </button>
      </div>

      <!-- Server List -->
      <div v-else class="space-y-4">
        <div
          v-for="server in servers"
          :key="server.id"
          class="server-card"
          :class="{ 'server-card-online': server.status === 'running' }"
        >
          <!-- Server Header -->
          <div class="p-5 border-b border-white/5">
            <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <!-- Server Info -->
              <div class="flex items-start gap-4">
                <div class="server-status-indicator" :class="getStatusClass(server.status)">
                  <span class="status-dot"></span>
                </div>
                <div>
                  <div class="flex flex-wrap items-center gap-2 mb-1">
                    <h3 class="text-lg font-bold text-white">{{ server.name }}</h3>
                    <span class="tag tag-orange">{{ server.unique_code }}</span>
                    <span class="tag" :class="getGameTagClass(server.game_type)">
                      {{ server.game_type }}
                    </span>
                  </div>
                  <div class="flex flex-wrap items-center gap-4 text-sm text-gray-400">
                    <span class="flex items-center gap-1">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                      </svg>
                      {{ server.ip_address }}:{{ server.port }}
                    </span>
                    <span class="flex items-center gap-1">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197" />
                      </svg>
                      {{ server.current_players || 0 }}/{{ server.max_players }}
                    </span>
                    <span v-if="server.current_map" class="flex items-center gap-1">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                      </svg>
                      {{ server.current_map }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex items-center gap-2">
                <button
                  v-if="server.status !== 'running'"
                  @click="controlServer(server.id, 'start')"
                  :disabled="serverLoading[server.id]"
                  class="btn-success"
                >
                  <svg v-if="!serverLoading[server.id]" class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  </svg>
                  <span v-if="serverLoading[server.id]" class="btn-spinner"></span>
                  Başlat
                </button>
                <button
                  v-else
                  @click="controlServer(server.id, 'stop')"
                  :disabled="serverLoading[server.id]"
                  class="btn-danger"
                >
                  <svg v-if="!serverLoading[server.id]" class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                  </svg>
                  <span v-if="serverLoading[server.id]" class="btn-spinner"></span>
                  Durdur
                </button>
                <button
                  @click="controlServer(server.id, 'restart')"
                  :disabled="serverLoading[server.id] || server.status !== 'running'"
                  class="btn-warning"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
                <button @click="openManageModal(server)" class="btn-secondary">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Yönet
                </button>
              </div>
            </div>
          </div>

          <!-- Quick Actions Bar -->
          <div class="px-5 py-3 flex flex-wrap items-center gap-2 bg-white/[0.02]">
            <button @click="openTab(server, 'console')" class="quick-action">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Konsol
            </button>
            <button @click="openTab(server, 'players')" class="quick-action">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197" />
              </svg>
              Oyuncular
            </button>
            <button @click="openTab(server, 'admins')" class="quick-action">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Adminler
            </button>
            <button @click="openTab(server, 'config')" class="quick-action">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Config
            </button>
            <button @click="openTab(server, 'maps')" class="quick-action">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              Haritalar
            </button>
            <button @click="copyConnect(server)" class="quick-action">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
              </svg>
              Bağlantı Kopyala
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Server Management Modal -->
    <Teleport to="body">
      <div v-if="showManageModal" class="modal-overlay" @click.self="showManageModal = false">
        <div class="modal-container">
          <!-- Modal Header -->
          <div class="modal-header">
            <div class="flex items-center gap-3">
              <div class="w-3 h-3 rounded-full" :class="selectedServer?.status === 'running' ? 'bg-green-500' : 'bg-red-500'"></div>
              <h2 class="text-xl font-bold text-white">{{ selectedServer?.name }}</h2>
              <span class="tag tag-orange text-xs">{{ selectedServer?.unique_code }}</span>
            </div>
            <button @click="showManageModal = false" class="modal-close">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Tabs -->
          <div class="modal-tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              class="modal-tab"
              :class="{ active: activeTab === tab.id }"
            >
              <span v-html="tab.icon"></span>
              {{ tab.name }}
            </button>
          </div>

          <!-- Tab Content -->
          <div class="modal-content">
            <!-- Console Tab -->
            <div v-if="activeTab === 'console'" class="tab-content">
              <div class="console-container">
                <div class="console-output" ref="consoleOutput">
                  <div v-if="consoleHistory.length === 0" class="text-gray-500 text-center py-8">
                    Henüz komut geçmişi yok. Bir komut gönderin.
                  </div>
                  <div
                    v-for="(entry, i) in consoleHistory"
                    :key="i"
                    class="console-entry"
                  >
                    <div class="console-command">
                      <span class="text-gray-500">{{ entry.time }}</span>
                      <span class="text-orange-400 mx-2">›</span>
                      <span class="text-yellow-400">{{ entry.command }}</span>
                    </div>
                    <pre v-if="entry.response" class="console-response">{{ entry.response }}</pre>
                  </div>
                </div>
                <div class="console-input">
                  <input
                    v-model="rconCommand"
                    @keyup.enter="sendRcon"
                    placeholder="RCON komutu girin..."
                    :disabled="rconLoading"
                    class="console-input-field"
                  />
                  <button @click="sendRcon" :disabled="rconLoading" class="btn-primary">
                    <span v-if="rconLoading" class="btn-spinner"></span>
                    <span v-else>Gönder</span>
                  </button>
                </div>
                <div class="quick-commands">
                  <span class="text-gray-500 text-sm">Hızlı:</span>
                  <button @click="quickRcon('status')" class="quick-cmd">status</button>
                  <button @click="quickRcon('users')" class="quick-cmd">users</button>
                  <button @click="quickRcon('stats')" class="quick-cmd">stats</button>
                  <button @click="quickRcon('sv_restart 1')" class="quick-cmd">restart round</button>
                  <button @click="quickRcon('mp_timelimit')" class="quick-cmd">timelimit</button>
                </div>
              </div>
            </div>

            <!-- Players Tab -->
            <div v-if="activeTab === 'players'" class="tab-content">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold text-white">Aktif Oyuncular</h3>
                <button @click="fetchPlayers" :disabled="playersLoading" class="btn-secondary btn-sm">
                  <svg class="w-4 h-4" :class="{ 'animate-spin': playersLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Yenile
                </button>
              </div>
              <div v-if="players.length === 0" class="empty-state-sm">
                <p>Sunucuda aktif oyuncu yok</p>
              </div>
              <div v-else class="players-table">
                <table>
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>İsim</th>
                      <th>Steam ID</th>
                      <th>Ping</th>
                      <th>Süre</th>
                      <th>İşlem</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="player in players" :key="player.slot">
                      <td>{{ player.slot }}</td>
                      <td>{{ player.name }}</td>
                      <td class="font-mono text-xs">{{ player.steam_id }}</td>
                      <td>{{ player.ping }}ms</td>
                      <td>{{ player.time }}</td>
                      <td>
                        <div class="flex gap-1">
                          <button @click="kickPlayer(player)" class="btn-warning btn-xs">Kick</button>
                          <button @click="banPlayer(player)" class="btn-danger btn-xs">Ban</button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Admins Tab -->
            <div v-if="activeTab === 'admins'" class="tab-content">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold text-white">Sunucu Adminleri</h3>
                <button @click="showAddAdminModal = true" class="btn-primary btn-sm">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Admin Ekle
                </button>
              </div>
              <div v-if="admins.length === 0" class="empty-state-sm">
                <p>Henüz admin eklenmemiş</p>
              </div>
              <div v-else class="admins-grid">
                <div v-for="admin in admins" :key="admin.id" class="admin-card">
                  <div class="flex items-center justify-between">
                    <div>
                      <div class="font-semibold text-white">{{ admin.name || 'İsimsiz' }}</div>
                      <div class="text-sm text-gray-400 font-mono">{{ admin.steam_id }}</div>
                      <div class="text-xs text-orange-400 mt-1">{{ admin.flags }}</div>
                    </div>
                    <button @click="removeAdmin(admin.id)" class="btn-danger btn-xs">Sil</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Config Tab -->
            <div v-if="activeTab === 'config'" class="tab-content">
              <div class="flex gap-2 mb-4">
                <button
                  v-for="file in configFiles"
                  :key="file"
                  @click="loadConfig(file)"
                  class="btn-secondary btn-sm"
                  :class="{ 'btn-primary': selectedConfigFile === file }"
                >
                  {{ file }}
                </button>
              </div>
              <div class="config-editor">
                <textarea
                  v-model="configContent"
                  :disabled="configLoading"
                  class="config-textarea"
                  placeholder="Config içeriği yükleniyor..."
                ></textarea>
              </div>
              <div class="flex justify-end gap-2 mt-4">
                <button @click="loadConfig(selectedConfigFile)" class="btn-secondary">Yenile</button>
                <button @click="saveConfig" :disabled="configSaving" class="btn-primary">
                  <span v-if="configSaving" class="btn-spinner"></span>
                  Kaydet
                </button>
              </div>
            </div>

            <!-- Maps Tab -->
            <div v-if="activeTab === 'maps'" class="tab-content">
              <h3 class="text-lg font-semibold text-white mb-4">Harita Değiştir</h3>
              <div v-if="maps.length === 0" class="empty-state-sm">
                <p>Harita listesi yüklenemedi</p>
              </div>
              <div v-else class="maps-grid">
                <button
                  v-for="map in maps"
                  :key="map"
                  @click="changeMap(map)"
                  class="map-card"
                  :class="{ 'map-card-active': selectedServer?.current_map === map }"
                >
                  <svg class="w-8 h-8 text-orange-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                  </svg>
                  <span class="text-sm">{{ map }}</span>
                  <span v-if="selectedServer?.current_map === map" class="text-xs text-green-400 mt-1">Aktif</span>
                </button>
              </div>
            </div>

            <!-- Stats Tab -->
            <div v-if="activeTab === 'stats'" class="tab-content">
              <h3 class="text-lg font-semibold text-white mb-4">Sunucu İstatistikleri</h3>
              <div class="stats-grid">
                <div class="stats-item">
                  <div class="stats-value">{{ serverStats?.uptime || '0s' }}</div>
                  <div class="stats-label">Uptime</div>
                </div>
                <div class="stats-item">
                  <div class="stats-value">{{ serverStats?.avg_players?.toFixed(1) || 0 }}</div>
                  <div class="stats-label">Ort. Oyuncu (24s)</div>
                </div>
                <div class="stats-item">
                  <div class="stats-value">{{ serverStats?.max_players || 0 }}</div>
                  <div class="stats-label">Max Oyuncu (24s)</div>
                </div>
                <div class="stats-item">
                  <div class="stats-value">{{ serverStats?.crash_count || 0 }}</div>
                  <div class="stats-label">Çökme Sayısı</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Add Admin Modal -->
    <Teleport to="body">
      <div v-if="showAddAdminModal" class="modal-overlay" @click.self="showAddAdminModal = false">
        <div class="modal-container modal-sm">
          <div class="modal-header">
            <h2 class="text-xl font-bold text-white">Admin Ekle</h2>
            <button @click="showAddAdminModal = false" class="modal-close">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="modal-content">
            <div class="space-y-4">
              <div>
                <label class="form-label">Steam ID *</label>
                <input v-model="newAdmin.steam_id" class="form-input" placeholder="STEAM_0:0:123456" />
              </div>
              <div>
                <label class="form-label">İsim</label>
                <input v-model="newAdmin.name" class="form-input" placeholder="Admin ismi (opsiyonel)" />
              </div>
              <div>
                <label class="form-label">Yetkiler</label>
                <input v-model="newAdmin.flags" class="form-input" placeholder="abcdefghijklmnopqrstu" />
                <p class="text-xs text-gray-500 mt-1">a=immunity, b=reservation, c=kick, d=ban, e=slay, f=map, u=menu</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="showAddAdminModal = false" class="btn-secondary">İptal</button>
            <button @click="addAdmin" :disabled="addingAdmin" class="btn-primary">
              <span v-if="addingAdmin" class="btn-spinner"></span>
              Ekle
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Toast Notifications -->
    <Teleport to="body">
      <div class="toast-container">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="toast"
          :class="'toast-' + toast.type"
        >
          {{ toast.message }}
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/client'

const router = useRouter()

// State
const loading = ref(true)
const error = ref(null)
const servers = ref([])
const serverLoading = ref({})

// Modals
const showManageModal = ref(false)
const showAddAdminModal = ref(false)
const selectedServer = ref(null)
const activeTab = ref('console')

// Console
const consoleOutput = ref(null)
const consoleHistory = ref([])
const rconCommand = ref('')
const rconLoading = ref(false)

// Players
const players = ref([])
const playersLoading = ref(false)

// Admins
const admins = ref([])
const newAdmin = ref({ steam_id: '', name: '', flags: 'abcdefghijklmnopqrstu' })
const addingAdmin = ref(false)

// Config
const configFiles = ['server.cfg', 'mapcycle.txt', 'motd.txt']
const selectedConfigFile = ref('server.cfg')
const configContent = ref('')
const configLoading = ref(false)
const configSaving = ref(false)

// Maps
const maps = ref([])

// Stats
const serverStats = ref(null)

// Toasts
const toasts = ref([])

// Tabs config
const tabs = [
  { id: 'console', name: 'Konsol', icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>' },
  { id: 'players', name: 'Oyuncular', icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197"/></svg>' },
  { id: 'admins', name: 'Adminler', icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>' },
  { id: 'config', name: 'Config', icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>' },
  { id: 'maps', name: 'Haritalar', icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/></svg>' },
  { id: 'stats', name: 'İstatistik', icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>' }
]

// Computed
const runningCount = computed(() => servers.value.filter(s => s.status === 'running').length)
const totalPlayers = computed(() => servers.value.reduce((sum, s) => sum + (s.current_players || 0), 0))
const totalAdmins = computed(() => admins.value.length)

// Navigation
function goToShop() {
  router.push('/shop')
}

// Toast helper
function showToast(message, type = 'info') {
  const id = Date.now()
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 3000)
}

// Status helpers
function getStatusClass(status) {
  switch(status) {
    case 'running': return 'status-online'
    case 'stopped': return 'status-offline'
    case 'creating': return 'status-pending'
    default: return 'status-offline'
  }
}

function getGameTagClass(gameType) {
  switch(gameType) {
    case 'AG': return 'tag-green'
    case 'CS16': return 'tag-blue'
    case 'HLDM': return 'tag-purple'
    default: return 'tag-gray'
  }
}

// API calls
async function fetchServers() {
  loading.value = true
  error.value = null
  try {
    const response = await apiClient.get('/v2/servers/my')
    servers.value = response.data || []
  } catch (err) {
    console.error('Fetch servers error:', err)
    error.value = err.response?.data?.detail || 'Sunucular yüklenemedi'
  } finally {
    loading.value = false
  }
}

async function controlServer(id, action) {
  serverLoading.value[id] = true
  try {
    await apiClient.post(`/v2/servers/${id}/${action}`)
    showToast(`Sunucu ${action === 'start' ? 'başlatılıyor' : action === 'stop' ? 'durduruluyor' : 'yeniden başlatılıyor'}...`, 'success')
    setTimeout(fetchServers, 2000)
  } catch (err) {
    showToast(err.response?.data?.detail || 'İşlem başarısız', 'error')
  } finally {
    serverLoading.value[id] = false
  }
}

function openManageModal(server) {
  selectedServer.value = server
  activeTab.value = 'console'
  showManageModal.value = true
  loadConsoleHistory()
  fetchAdmins()
  fetchMaps()
  fetchStats()
}

function openTab(server, tab) {
  selectedServer.value = server
  activeTab.value = tab
  showManageModal.value = true

  if (tab === 'console') loadConsoleHistory()
  if (tab === 'players') fetchPlayers()
  if (tab === 'admins') fetchAdmins()
  if (tab === 'config') loadConfig('server.cfg')
  if (tab === 'maps') fetchMaps()
  if (tab === 'stats') fetchStats()
}

// Console
async function loadConsoleHistory() {
  if (!selectedServer.value) return
  try {
    const response = await apiClient.get(`/v2/servers/${selectedServer.value.id}/rcon/history?limit=20`)
    consoleHistory.value = (response.data.history || []).map(h => ({
      time: new Date(h.created_at).toLocaleTimeString('tr-TR'),
      command: h.command,
      response: h.response
    }))
  } catch (err) {
    console.error('Console history error:', err)
  }
}

async function sendRcon() {
  if (!rconCommand.value.trim() || !selectedServer.value) return
  rconLoading.value = true
  try {
    const response = await apiClient.post(`/v2/servers/${selectedServer.value.id}/rcon`, {
      command: rconCommand.value
    })
    consoleHistory.value.push({
      time: new Date().toLocaleTimeString('tr-TR'),
      command: rconCommand.value,
      response: response.data.response
    })
    rconCommand.value = ''
    await nextTick()
    if (consoleOutput.value) {
      consoleOutput.value.scrollTop = consoleOutput.value.scrollHeight
    }
  } catch (err) {
    showToast(err.response?.data?.detail || 'Komut gönderilemedi', 'error')
  } finally {
    rconLoading.value = false
  }
}

function quickRcon(cmd) {
  rconCommand.value = cmd
  sendRcon()
}

// Players
async function fetchPlayers() {
  if (!selectedServer.value) return
  playersLoading.value = true
  try {
    const response = await apiClient.get(`/v2/servers/${selectedServer.value.id}/players`)
    players.value = response.data.players || []
  } catch (err) {
    console.error('Players error:', err)
  } finally {
    playersLoading.value = false
  }
}

async function kickPlayer(player) {
  try {
    await apiClient.post(`/v2/servers/${selectedServer.value.id}/players/${player.slot}/kick`, {
      reason: 'Kicked by admin'
    })
    showToast('Oyuncu atıldı', 'success')
    fetchPlayers()
  } catch (err) {
    showToast('Kick başarısız', 'error')
  }
}

async function banPlayer(player) {
  try {
    await apiClient.post(`/v2/servers/${selectedServer.value.id}/players/ban`, {
      steam_id: player.steam_id,
      name: player.name,
      reason: 'Banned by admin',
      duration_minutes: 0
    })
    showToast('Oyuncu banlandı', 'success')
    fetchPlayers()
  } catch (err) {
    showToast('Ban başarısız', 'error')
  }
}

// Admins
async function fetchAdmins() {
  if (!selectedServer.value) return
  try {
    const response = await apiClient.get(`/v2/servers/${selectedServer.value.id}/admins`)
    admins.value = response.data.admins || []
  } catch (err) {
    console.error('Admins error:', err)
  }
}

async function addAdmin() {
  if (!newAdmin.value.steam_id) {
    showToast('Steam ID gerekli', 'error')
    return
  }
  addingAdmin.value = true
  try {
    await apiClient.post(`/v2/servers/${selectedServer.value.id}/admins`, newAdmin.value)
    showToast('Admin eklendi', 'success')
    showAddAdminModal.value = false
    newAdmin.value = { steam_id: '', name: '', flags: 'abcdefghijklmnopqrstu' }
    fetchAdmins()
  } catch (err) {
    showToast(err.response?.data?.detail || 'Admin eklenemedi', 'error')
  } finally {
    addingAdmin.value = false
  }
}

async function removeAdmin(adminId) {
  try {
    await apiClient.delete(`/v2/servers/${selectedServer.value.id}/admins/${adminId}`)
    showToast('Admin silindi', 'success')
    fetchAdmins()
  } catch (err) {
    showToast('Silme başarısız', 'error')
  }
}

// Config
async function loadConfig(filename) {
  if (!selectedServer.value) return
  selectedConfigFile.value = filename
  configLoading.value = true
  try {
    const response = await apiClient.get(`/v2/servers/${selectedServer.value.id}/config?filename=${filename}`)
    configContent.value = response.data.content || ''
  } catch (err) {
    configContent.value = '// Config yüklenemedi'
  } finally {
    configLoading.value = false
  }
}

async function saveConfig() {
  if (!selectedServer.value) return
  configSaving.value = true
  try {
    await apiClient.put(`/v2/servers/${selectedServer.value.id}/config?filename=${selectedConfigFile.value}`, {
      content: configContent.value
    })
    showToast('Config kaydedildi', 'success')
  } catch (err) {
    showToast('Kaydetme başarısız', 'error')
  } finally {
    configSaving.value = false
  }
}

// Maps
async function fetchMaps() {
  if (!selectedServer.value) return
  try {
    const response = await apiClient.get(`/v2/servers/${selectedServer.value.id}/maps`)
    maps.value = response.data.maps || []
  } catch (err) {
    console.error('Maps error:', err)
  }
}

async function changeMap(mapName) {
  try {
    await apiClient.post(`/v2/servers/${selectedServer.value.id}/maps/change`, {
      map_name: mapName
    })
    showToast(`Harita değiştiriliyor: ${mapName}`, 'success')
  } catch (err) {
    showToast('Harita değiştirilemedi', 'error')
  }
}

// Stats
async function fetchStats() {
  if (!selectedServer.value) return
  try {
    const response = await apiClient.get(`/v2/servers/${selectedServer.value.id}/stats`)
    serverStats.value = response.data
  } catch (err) {
    console.error('Stats error:', err)
  }
}

// Utilities
function copyConnect(server) {
  const text = `connect ${server.ip_address}:${server.port}`
  navigator.clipboard.writeText(text)
  showToast('Bağlantı kopyalandı!', 'success')
}

// Init
onMounted(() => {
  fetchServers()
})
</script>

<style scoped>
/* Base */
.server-panel {
  min-height: 100vh;
  background: #0a0a0a;
  position: relative;
}

.panel-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.bg-gradient {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 30% 20%, rgba(249, 115, 22, 0.08) 0%, transparent 50%),
              radial-gradient(circle at 70% 80%, rgba(59, 130, 246, 0.05) 0%, transparent 50%);
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 50px 50px;
}

/* Cards */
.glass-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  border-color: rgba(249, 115, 22, 0.3);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.server-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.server-card:hover {
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.server-card-online {
  border-color: rgba(34, 197, 94, 0.3);
}

/* Status */
.server-status-indicator {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-online {
  background: rgba(34, 197, 94, 0.2);
}

.status-offline {
  background: rgba(239, 68, 68, 0.2);
}

.status-pending {
  background: rgba(234, 179, 8, 0.2);
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-online .status-dot { background: #22c55e; }
.status-offline .status-dot { background: #ef4444; }
.status-pending .status-dot { background: #eab308; }

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.9); }
}

/* Tags */
.tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.tag-orange { background: rgba(249, 115, 22, 0.2); color: #f97316; }
.tag-green { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
.tag-blue { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
.tag-purple { background: rgba(168, 85, 247, 0.2); color: #a855f7; }
.tag-gray { background: rgba(156, 163, 175, 0.2); color: #9ca3af; }

/* Buttons */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white;
  font-weight: 600;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-weight: 500;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover { background: rgba(255, 255, 255, 0.15); }

.btn-success {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  font-weight: 500;
  border-radius: 8px;
  border: 1px solid rgba(34, 197, 94, 0.3);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-success:hover { background: rgba(34, 197, 94, 0.3); }
.btn-success:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-danger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  font-weight: 500;
  border-radius: 8px;
  border: 1px solid rgba(239, 68, 68, 0.3);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-danger:hover { background: rgba(239, 68, 68, 0.3); }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-warning {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  background: rgba(234, 179, 8, 0.2);
  color: #eab308;
  font-weight: 500;
  border-radius: 8px;
  border: 1px solid rgba(234, 179, 8, 0.3);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-warning:hover { background: rgba(234, 179, 8, 0.3); }
.btn-warning:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-sm { padding: 6px 12px; font-size: 14px; }
.btn-xs { padding: 4px 8px; font-size: 12px; }

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Quick Actions */
.quick-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  color: #9ca3af;
  font-size: 13px;
  border-radius: 6px;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-action:hover {
  color: #f97316;
  background: rgba(249, 115, 22, 0.1);
}

/* Loading */
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(249, 115, 22, 0.2);
  border-top-color: #f97316;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: #141414;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-sm {
  max-width: 500px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.modal-close {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.modal-tabs {
  display: flex;
  gap: 4px;
  padding: 12px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  overflow-x: auto;
}

.modal-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #9ca3af;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.modal-tab:hover {
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

.modal-tab.active {
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
}

.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

/* Console */
.console-container {
  background: #0a0a0a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
}

.console-output {
  height: 300px;
  overflow-y: auto;
  padding: 16px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.console-entry {
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.console-command {
  display: flex;
  align-items: center;
}

.console-response {
  margin-top: 4px;
  padding-left: 20px;
  color: #9ca3af;
  white-space: pre-wrap;
  font-size: 12px;
}

.console-input {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
}

.console-input-field {
  flex: 1;
  padding: 10px 14px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: white;
  font-family: inherit;
  font-size: 14px;
  outline: none;
}

.console-input-field:focus {
  border-color: #f97316;
}

.quick-commands {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  flex-wrap: wrap;
}

.quick-cmd {
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #9ca3af;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-cmd:hover {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
  color: #f97316;
}

/* Players Table */
.players-table {
  overflow-x: auto;
}

.players-table table {
  width: 100%;
  border-collapse: collapse;
}

.players-table th,
.players-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.players-table th {
  color: #9ca3af;
  font-weight: 500;
  font-size: 13px;
}

.players-table td {
  color: white;
  font-size: 14px;
}

/* Admins Grid */
.admins-grid {
  display: grid;
  gap: 12px;
}

.admin-card {
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
}

/* Config Editor */
.config-textarea {
  width: 100%;
  height: 400px;
  padding: 16px;
  background: #0a0a0a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #e5e5e5;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  resize: vertical;
  outline: none;
}

.config-textarea:focus {
  border-color: #f97316;
}

/* Maps Grid */
.maps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.map-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.map-card:hover {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
}

.map-card-active {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}

.stats-item {
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  text-align: center;
}

.stats-value {
  font-size: 28px;
  font-weight: bold;
  color: white;
}

.stats-label {
  font-size: 13px;
  color: #9ca3af;
  margin-top: 4px;
}

/* Form */
.form-label {
  display: block;
  color: #9ca3af;
  font-size: 14px;
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: white;
  font-size: 14px;
  outline: none;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: #f97316;
  background: rgba(255, 255, 255, 0.08);
}

/* Empty State */
.empty-state-sm {
  padding: 40px;
  text-align: center;
  color: #6b7280;
}

/* Toast */
.toast-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toast {
  padding: 12px 20px;
  border-radius: 10px;
  color: white;
  font-size: 14px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast-success { background: #22c55e; }
.toast-error { background: #ef4444; }
.toast-info { background: #3b82f6; }

/* Scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
