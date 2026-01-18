<template>
  <div class="min-h-screen">
    <div class="container-custom py-8">
      <!-- Back Button & Header -->
      <div class="mb-6">
        <router-link to="/servers" class="inline-flex items-center gap-2 text-gray-400 hover:text-orange-500 transition-colors mb-4">
          <ArrowLeftIcon class="w-4 h-4" />
          Sunuculara Dön
        </router-link>

        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div class="flex items-center gap-4">
            <div class="w-20 h-20 rounded-xl bg-gradient-to-br from-orange-500 to-purple-500 flex items-center justify-center">
              <ServerIcon class="w-10 h-10 text-white" />
            </div>
            <div>
              <h1 class="text-4xl font-display font-bold">
                <span class="text-gradient">{{ server?.name || 'Sunucu' }}</span>
              </h1>
              <p class="text-gray-400">
                {{ server?.ip }}:{{ server?.port }}
              </p>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <div
              :class="[
                'w-3 h-3 rounded-full',
                server?.status === 'running' ? 'status-online' : 'status-offline'
              ]"
            ></div>
            <n-tag :type="server?.status === 'running' ? 'success' : 'error'">
              {{ server?.status === 'running' ? 'Çalışıyor' : 'Durduruldu' }}
            </n-tag>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        <n-button
          type="success"
          :disabled="server?.status === 'running'"
          @click="startServer"
          block
        >
          <template #icon><PlayCircleIcon class="w-4 h-4" /></template>
          Başlat
        </n-button>

        <n-button
          type="error"
          :disabled="server?.status !== 'running'"
          @click="stopServer"
          block
        >
          <template #icon><StopCircleIcon class="w-4 h-4" /></template>
          Durdur
        </n-button>

        <n-button
          type="primary"
          @click="restartServer"
          block
        >
          <template #icon><RefreshCwIcon class="w-4 h-4" /></template>
          Yeniden Başlat
        </n-button>

        <n-button
          quaternary
          @click="reinstallServer"
          block
        >
          <template #icon><DownloadIcon class="w-4 h-4" /></template>
          Yeniden Kur
        </n-button>

        <n-button
          secondary
          @click="copyServerIP"
          block
        >
          <template #icon><CopyIcon class="w-4 h-4" /></template>
          IP Kopyala
        </n-button>
      </div>

      <!-- Performance Stats -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <n-card class="glass-card stat-card">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-400">CPU Kullanımı</span>
            <CpuIcon class="w-5 h-5 text-orange-500" />
          </div>
          <div class="text-2xl font-bold text-orange-500 mb-2">{{ stats.cpu }}%</div>
          <n-progress
            type="line"
            :percentage="stats.cpu"
            :show-indicator="false"
            :height="8"
            :border-radius="4"
            color="linear-gradient(to right, #f97316, #8b5cf6)"
          />
        </n-card>

        <n-card class="glass-card stat-card">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-400">RAM Kullanımı</span>
            <MemoryStickIcon class="w-5 h-5 text-purple-500" />
          </div>
          <div class="text-2xl font-bold text-purple-500 mb-2">{{ stats.ram }}%</div>
          <n-progress
            type="line"
            :percentage="stats.ram"
            :show-indicator="false"
            :height="8"
            :border-radius="4"
            color="linear-gradient(to right, #8b5cf6, #06b6d4)"
          />
        </n-card>

        <n-card class="glass-card stat-card">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-400">Oyuncular</span>
            <UsersIcon class="w-5 h-5 text-cyan-500" />
          </div>
          <div class="text-2xl font-bold text-cyan-500">
            {{ stats.players }}/{{ stats.maxPlayers }}
          </div>
          <div class="text-xs text-gray-500 mt-1">
            %{{ Math.round((stats.players / stats.maxPlayers) * 100) }} dolu
          </div>
        </n-card>

        <n-card class="glass-card stat-card">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-400">Uptime</span>
            <ClockIcon class="w-5 h-5 text-green-500" />
          </div>
          <div class="text-2xl font-bold text-green-500">{{ stats.uptime }}</div>
          <div class="text-xs text-gray-500 mt-1">
            Sorunsuz çalışıyor
          </div>
        </n-card>
      </div>

      <!-- Tabs -->
      <n-tabs v-model:value="activeTab" type="segment" animated class="mb-6">
        <n-tab-pane name="overview" tab="Genel Bakış">
          <template #tab>
            <div class="flex items-center gap-2">
              <LayoutDashboardIcon class="w-4 h-4" />
              <span>Genel Bakış</span>
            </div>
          </template>
        </n-tab-pane>
        <n-tab-pane name="console" tab="Konsol">
          <template #tab>
            <div class="flex items-center gap-2">
              <TerminalIcon class="w-4 h-4" />
              <span>Konsol</span>
            </div>
          </template>
        </n-tab-pane>
        <n-tab-pane name="files" tab="Dosyalar">
          <template #tab>
            <div class="flex items-center gap-2">
              <FolderIcon class="w-4 h-4" />
              <span>Dosyalar</span>
            </div>
          </template>
        </n-tab-pane>
        <n-tab-pane name="plugins" tab="Eklentiler">
          <template #tab>
            <div class="flex items-center gap-2">
              <PuzzleIcon class="w-4 h-4" />
              <span>Eklentiler</span>
            </div>
          </template>
        </n-tab-pane>
        <n-tab-pane name="config" tab="Ayarlar">
          <template #tab>
            <div class="flex items-center gap-2">
              <SettingsIcon class="w-4 h-4" />
              <span>Ayarlar</span>
            </div>
          </template>
        </n-tab-pane>
        <n-tab-pane name="players" tab="Oyuncular">
          <template #tab>
            <div class="flex items-center gap-2">
              <UsersIcon class="w-4 h-4" />
              <span>Oyuncular</span>
            </div>
          </template>
        </n-tab-pane>
        <n-tab-pane name="bans" tab="Banlar">
          <template #tab>
            <div class="flex items-center gap-2">
              <ShieldBanIcon class="w-4 h-4" />
              <span>Banlar</span>
            </div>
          </template>
        </n-tab-pane>
        <n-tab-pane name="tasks" tab="Zamanlanmış">
          <template #tab>
            <div class="flex items-center gap-2">
              <CalendarClockIcon class="w-4 h-4" />
              <span>Zamanlanmış</span>
            </div>
          </template>
        </n-tab-pane>
        <n-tab-pane name="backups" tab="Yedekler">
          <template #tab>
            <div class="flex items-center gap-2">
              <DatabaseBackupIcon class="w-4 h-4" />
              <span>Yedekler</span>
            </div>
          </template>
        </n-tab-pane>
      </n-tabs>

      <!-- Tab Content -->
      <div>
        <!-- Overview Tab -->
        <div v-if="activeTab === 'overview'" class="space-y-6">
          <!-- Performance Chart -->
          <n-card class="glass-card">
            <template #header>
              <span class="font-bold">Performans Grafiği</span>
            </template>
            <div class="h-64">
              <Line :data="chartData" :options="chartOptions" />
            </div>
          </n-card>

          <div class="grid md:grid-cols-2 gap-6">
            <!-- Server Info -->
            <n-card class="glass-card">
              <template #header>
                <div class="flex items-center gap-2">
                  <InfoIcon class="w-5 h-5 text-orange-500" />
                  <span class="font-bold">Sunucu Bilgileri</span>
                </div>
              </template>
              <div class="space-y-3">
                <div class="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  <span class="text-gray-400">Sunucu Adı</span>
                  <span class="font-semibold">{{ server?.name }}</span>
                </div>
                <div class="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  <span class="text-gray-400">IP Adresi</span>
                  <span class="font-mono text-orange-500">{{ server?.ip }}:{{ server?.port }}</span>
                </div>
                <div class="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  <span class="text-gray-400">Mevcut Map</span>
                  <span class="font-mono">{{ server?.current_map || 'de_dust2' }}</span>
                </div>
                <div class="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  <span class="text-gray-400">Oyun Modu</span>
                  <n-tag type="primary" size="small">{{ server?.game_mode || 'Classic' }}</n-tag>
                </div>
                <div class="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  <span class="text-gray-400">Oluşturulma</span>
                  <span class="text-sm">{{ formatDate(server?.created_at) }}</span>
                </div>
              </div>
            </n-card>

            <!-- Recent Activity -->
            <n-card class="glass-card">
              <template #header>
                <div class="flex items-center gap-2">
                  <ActivityIcon class="w-5 h-5 text-purple-500" />
                  <span class="font-bold">Son Aktiviteler</span>
                </div>
              </template>
              <div class="space-y-3">
                <div v-for="activity in recentActivity" :key="activity.id" class="flex items-start gap-3 p-3 bg-white/5 rounded-lg">
                  <div
                    :class="[
                      'w-2 h-2 rounded-full mt-2',
                      activity.type === 'success' ? 'bg-green-500' : activity.type === 'error' ? 'bg-red-500' : 'bg-orange-500'
                    ]"
                  ></div>
                  <div class="flex-1">
                    <p class="text-sm">{{ activity.message }}</p>
                    <span class="text-xs text-gray-500">{{ activity.time }}</span>
                  </div>
                </div>
              </div>
            </n-card>
          </div>
        </div>

        <!-- Console Tab -->
        <div v-if="activeTab === 'console'">
          <n-card class="glass-card">
            <template #header>
              <div class="flex justify-between items-center">
                <div class="flex items-center gap-2">
                  <TerminalIcon class="w-5 h-5 text-orange-500" />
                  <span class="font-bold">Sunucu Konsolu</span>
                </div>
                <div class="flex gap-2">
                  <n-button quaternary size="small" @click="clearConsole">
                    <template #icon><TrashIcon class="w-4 h-4" /></template>
                  </n-button>
                  <n-button quaternary size="small" @click="scrollToBottom">
                    <template #icon><ArrowDownIcon class="w-4 h-4" /></template>
                  </n-button>
                </div>
              </div>
            </template>

            <!-- Console Output -->
            <div
              ref="consoleOutput"
              class="bg-gray-900 rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm text-green-400 mb-4"
            >
              <div v-for="(log, index) in consoleLogs" :key="index" class="mb-1">
                <span class="text-gray-600">[{{ log.time }}]</span>
                <span :class="getLogColor(log.level)"> {{ log.message }}</span>
              </div>
            </div>

            <!-- Console Input -->
            <div class="flex gap-2">
              <n-input
                v-model:value="consoleCommand"
                placeholder="Komut girin..."
                class="font-mono"
                @keyup.enter="sendCommand"
              />
              <n-button type="primary" @click="sendCommand">
                <template #icon><SendIcon class="w-4 h-4" /></template>
                Gönder
              </n-button>
            </div>
          </n-card>
        </div>

        <!-- Files Tab -->
        <div v-if="activeTab === 'files'">
          <n-card class="glass-card">
            <template #header>
              <div class="flex items-center gap-2">
                <FolderIcon class="w-5 h-5 text-orange-500" />
                <span class="font-bold">Dosya Yöneticisi</span>
              </div>
            </template>

            <!-- Breadcrumb -->
            <n-breadcrumb class="mb-4">
              <n-breadcrumb-item @click="navigateToFolder('/')">cstrike</n-breadcrumb-item>
              <n-breadcrumb-item v-for="folder in currentPath.split('/').filter(Boolean)" :key="folder">
                {{ folder }}
              </n-breadcrumb-item>
            </n-breadcrumb>

            <!-- File List -->
            <n-data-table
              :columns="fileColumns"
              :data="files"
              :bordered="false"
              :row-class-name="() => 'hover:bg-white/5'"
            />
          </n-card>
        </div>

        <!-- Config Tab -->
        <div v-if="activeTab === 'config'">
          <n-card class="glass-card">
            <template #header>
              <div class="flex items-center gap-2">
                <SettingsIcon class="w-5 h-5 text-orange-500" />
                <span class="font-bold">Sunucu Ayarları</span>
              </div>
            </template>

            <n-form @submit.prevent="saveConfig" class="space-y-4">
              <n-form-item label="Sunucu Adı">
                <n-input v-model:value="config.hostname" placeholder="My CS 1.6 Server" />
              </n-form-item>

              <n-form-item label="Maksimum Oyuncu">
                <n-input-number v-model:value="config.maxplayers" :min="2" :max="32" style="width: 100%;" />
              </n-form-item>

              <n-form-item label="RCON Şifresi">
                <n-input v-model:value="config.rcon_password" type="password" show-password-on="click" />
              </n-form-item>

              <n-form-item label="Map Rotasyonu">
                <n-input
                  v-model:value="config.mapcycle"
                  type="textarea"
                  placeholder="de_dust2&#10;de_inferno&#10;de_nuke"
                  :rows="5"
                />
              </n-form-item>

              <div class="flex gap-2">
                <n-button type="primary" attr-type="submit">
                  <template #icon><SaveIcon class="w-4 h-4" /></template>
                  Kaydet
                </n-button>
                <n-button quaternary>İptal</n-button>
              </div>
            </n-form>
          </n-card>
        </div>

        <!-- Players Tab -->
        <div v-if="activeTab === 'players'">
          <n-card class="glass-card">
            <template #header>
              <div class="flex items-center gap-2">
                <UsersIcon class="w-5 h-5 text-orange-500" />
                <span class="font-bold">Aktif Oyuncular ({{ onlinePlayers.length }})</span>
              </div>
            </template>

            <n-data-table
              :columns="playerColumns"
              :data="onlinePlayers"
              :bordered="false"
            />
          </n-card>
        </div>

        <!-- Plugins Tab -->
        <div v-if="activeTab === 'plugins'">
          <div class="grid lg:grid-cols-3 gap-6">
            <!-- Installed Plugins -->
            <div class="lg:col-span-2">
              <n-card class="glass-card">
                <template #header>
                  <div class="flex justify-between items-center">
                    <div class="flex items-center gap-2">
                      <PuzzleIcon class="w-5 h-5 text-orange-500" />
                      <span class="font-bold">Yüklü Eklentiler</span>
                    </div>
                    <n-button type="primary" size="small">
                      <template #icon><PlusIcon class="w-4 h-4" /></template>
                      Eklenti Yükle
                    </n-button>
                  </div>
                </template>

                <div class="space-y-3">
                  <div v-for="plugin in installedPlugins" :key="plugin.id"
                       class="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                    <div class="flex items-center gap-3">
                      <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-orange-500 to-purple-500 flex items-center justify-center">
                        <PuzzleIcon class="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h4 class="font-bold">{{ plugin.name }}</h4>
                        <p class="text-sm text-gray-400">{{ plugin.version }} · {{ plugin.author }}</p>
                      </div>
                    </div>
                    <div class="flex items-center gap-2">
                      <n-tag :type="plugin.enabled ? 'success' : 'error'" size="small">
                        {{ plugin.enabled ? 'Aktif' : 'Pasif' }}
                      </n-tag>
                      <n-button quaternary size="tiny" @click="togglePlugin(plugin)">
                        <template #icon><SettingsIcon class="w-3 h-3" /></template>
                      </n-button>
                      <n-button quaternary size="tiny" type="error" @click="removePlugin(plugin)">
                        <template #icon><TrashIcon class="w-3 h-3" /></template>
                      </n-button>
                    </div>
                  </div>
                </div>
              </n-card>
            </div>

            <!-- Popular Plugins -->
            <div>
              <n-card class="glass-card">
                <template #header>
                  <div class="flex items-center gap-2">
                    <StarIcon class="w-5 h-5 text-yellow-500" />
                    <span class="font-bold">Popüler Eklentiler</span>
                  </div>
                </template>
                <div class="space-y-3">
                  <div v-for="plugin in popularPlugins" :key="plugin.id"
                       class="p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer">
                    <div class="flex items-center justify-between mb-2">
                      <h4 class="font-semibold text-sm">{{ plugin.name }}</h4>
                      <span class="text-xs text-yellow-500">{{ plugin.downloads }}</span>
                    </div>
                    <p class="text-xs text-gray-400 mb-2">{{ plugin.description }}</p>
                    <n-button size="tiny" block @click="installPlugin(plugin)">
                      <template #icon><DownloadIcon class="w-3 h-3" /></template>
                      Yükle
                    </n-button>
                  </div>
                </div>
              </n-card>
            </div>
          </div>
        </div>

        <!-- Bans Tab -->
        <div v-if="activeTab === 'bans'">
          <n-card class="glass-card">
            <template #header>
              <div class="flex justify-between items-center">
                <div class="flex items-center gap-2">
                  <ShieldBanIcon class="w-5 h-5 text-red-500" />
                  <span class="font-bold">Ban Listesi</span>
                </div>
                <n-button type="error" size="small" @click="showBanModal = true">
                  <template #icon><PlusIcon class="w-4 h-4" /></template>
                  Yeni Ban
                </n-button>
              </div>
            </template>

            <n-data-table
              :columns="banColumns"
              :data="banList"
              :bordered="false"
            />
          </n-card>
        </div>

        <!-- Scheduled Tasks Tab -->
        <div v-if="activeTab === 'tasks'">
          <div class="grid lg:grid-cols-2 gap-6">
            <n-card class="glass-card">
              <template #header>
                <div class="flex justify-between items-center">
                  <div class="flex items-center gap-2">
                    <CalendarClockIcon class="w-5 h-5 text-orange-500" />
                    <span class="font-bold">Zamanlanmış Görevler</span>
                  </div>
                  <n-button type="primary" size="small" @click="showTaskModal = true">
                    <template #icon><PlusIcon class="w-4 h-4" /></template>
                    Yeni Görev
                  </n-button>
                </div>
              </template>

              <div class="space-y-3">
                <div v-for="task in scheduledTasks" :key="task.id"
                     class="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div class="flex items-center gap-3">
                    <div :class="['w-10 h-10 rounded-lg flex items-center justify-center',
                                 task.type === 'restart' ? 'bg-yellow-500/20 text-yellow-500' :
                                 task.type === 'backup' ? 'bg-cyan-500/20 text-cyan-500' :
                                 'bg-orange-500/20 text-orange-500']">
                      <RefreshCwIcon v-if="task.type === 'restart'" class="w-5 h-5" />
                      <DatabaseBackupIcon v-else-if="task.type === 'backup'" class="w-5 h-5" />
                      <TerminalIcon v-else class="w-5 h-5" />
                    </div>
                    <div>
                      <h4 class="font-bold">{{ task.name }}</h4>
                      <p class="text-sm text-gray-400">{{ task.schedule }}</p>
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <n-switch v-model:value="task.enabled" size="small" @update:value="toggleTask(task)" />
                    <n-button quaternary size="tiny" @click="editTask(task)">
                      <template #icon><EditIcon class="w-3 h-3" /></template>
                    </n-button>
                    <n-button quaternary size="tiny" type="error" @click="deleteTask(task)">
                      <template #icon><TrashIcon class="w-3 h-3" /></template>
                    </n-button>
                  </div>
                </div>
              </div>
            </n-card>

            <!-- Quick Task Templates -->
            <n-card class="glass-card">
              <template #header>
                <div class="flex items-center gap-2">
                  <ZapIcon class="w-5 h-5 text-yellow-500" />
                  <span class="font-bold">Hızlı Görev Şablonları</span>
                </div>
              </template>
              <div class="space-y-3">
                <button class="w-full p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors text-left"
                        @click="createQuickTask('daily-restart')">
                  <div class="flex items-center gap-3">
                    <RefreshCwIcon class="w-5 h-5 text-yellow-500" />
                    <div>
                      <h4 class="font-semibold">Günlük Yeniden Başlatma</h4>
                      <p class="text-sm text-gray-400">Her gün 04:00'da sunucuyu yeniden başlat</p>
                    </div>
                  </div>
                </button>
                <button class="w-full p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors text-left"
                        @click="createQuickTask('hourly-backup')">
                  <div class="flex items-center gap-3">
                    <DatabaseBackupIcon class="w-5 h-5 text-cyan-500" />
                    <div>
                      <h4 class="font-semibold">Saatlik Yedekleme</h4>
                      <p class="text-sm text-gray-400">Her saat başı otomatik yedek al</p>
                    </div>
                  </div>
                </button>
                <button class="w-full p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors text-left"
                        @click="createQuickTask('map-rotation')">
                  <div class="flex items-center gap-3">
                    <MapIcon class="w-5 h-5 text-green-500" />
                    <div>
                      <h4 class="font-semibold">Map Rotasyonu</h4>
                      <p class="text-sm text-gray-400">Her 30 dakikada map değiştir</p>
                    </div>
                  </div>
                </button>
              </div>
            </n-card>
          </div>
        </div>

        <!-- Backups Tab -->
        <div v-if="activeTab === 'backups'">
          <div class="grid lg:grid-cols-3 gap-6">
            <div class="lg:col-span-2">
              <n-card class="glass-card">
                <template #header>
                  <div class="flex justify-between items-center">
                    <div class="flex items-center gap-2">
                      <DatabaseBackupIcon class="w-5 h-5 text-orange-500" />
                      <span class="font-bold">Yedekler</span>
                    </div>
                    <n-button type="primary" size="small" @click="createBackup">
                      <template #icon><PlusIcon class="w-4 h-4" /></template>
                      Yeni Yedek
                    </n-button>
                  </div>
                </template>

                <div class="space-y-3">
                  <div v-for="backup in backups" :key="backup.id"
                       class="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                    <div class="flex items-center gap-3">
                      <div class="w-12 h-12 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                        <DatabaseBackupIcon class="w-6 h-6 text-cyan-500" />
                      </div>
                      <div>
                        <h4 class="font-bold">{{ backup.name }}</h4>
                        <p class="text-sm text-gray-400">{{ backup.date }} · {{ backup.size }}</p>
                      </div>
                    </div>
                    <div class="flex items-center gap-2">
                      <n-tag :type="backup.type === 'auto' ? 'info' : 'primary'" size="small">
                        {{ backup.type === 'auto' ? 'Otomatik' : 'Manuel' }}
                      </n-tag>
                      <n-button type="success" size="tiny" @click="restoreBackup(backup)">
                        <template #icon><RefreshCwIcon class="w-3 h-3" /></template>
                        Geri Yükle
                      </n-button>
                      <n-button quaternary size="tiny" @click="downloadBackup(backup)">
                        <template #icon><DownloadIcon class="w-3 h-3" /></template>
                      </n-button>
                      <n-button quaternary size="tiny" type="error" @click="deleteBackup(backup)">
                        <template #icon><TrashIcon class="w-3 h-3" /></template>
                      </n-button>
                    </div>
                  </div>
                </div>
              </n-card>
            </div>

            <!-- Backup Settings -->
            <n-card class="glass-card">
              <template #header>
                <div class="flex items-center gap-2">
                  <SettingsIcon class="w-5 h-5 text-orange-500" />
                  <span class="font-bold">Yedekleme Ayarları</span>
                </div>
              </template>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <div>
                    <span class="font-semibold">Otomatik Yedekleme</span>
                    <p class="text-xs text-gray-400">Düzenli aralıklarla yedek al</p>
                  </div>
                  <n-switch v-model:value="backupSettings.autoBackup" />
                </div>

                <n-form-item label="Yedekleme Sıklığı">
                  <n-select
                    v-model:value="backupSettings.frequency"
                    :options="frequencyOptions"
                  />
                </n-form-item>

                <n-form-item label="Maksimum Yedek Sayısı">
                  <n-input-number
                    v-model:value="backupSettings.maxBackups"
                    :min="1"
                    :max="50"
                    style="width: 100%;"
                  />
                </n-form-item>

                <n-button type="primary" block @click="saveBackupSettings">
                  <template #icon><SaveIcon class="w-4 h-4" /></template>
                  Ayarları Kaydet
                </n-button>
              </div>
            </n-card>
          </div>
        </div>
      </div>
    </div>

    <!-- Ban Modal -->
    <n-modal v-model:show="showBanModal" preset="card" title="Yeni Ban Ekle" style="width: 500px;">
      <n-form class="space-y-4">
        <n-form-item label="Oyuncu Adı">
          <n-input v-model:value="newBan.playerName" placeholder="Oyuncu adı" />
        </n-form-item>
        <n-form-item label="Steam ID">
          <n-input v-model:value="newBan.steamId" placeholder="STEAM_0:X:XXXXXXXX" />
        </n-form-item>
        <n-form-item label="Sebep">
          <n-input v-model:value="newBan.reason" placeholder="Ban sebebi" />
        </n-form-item>
        <n-form-item label="Süre">
          <n-select
            v-model:value="newBan.duration"
            :options="banDurationOptions"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="flex gap-2 justify-end">
          <n-button quaternary @click="showBanModal = false">İptal</n-button>
          <n-button type="error" @click="addBan">
            <template #icon><ShieldBanIcon class="w-4 h-4" /></template>
            Banla
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- Task Modal -->
    <n-modal v-model:show="showTaskModal" preset="card" title="Yeni Zamanlanmış Görev" style="width: 500px;">
      <n-form class="space-y-4">
        <n-form-item label="Görev Adı">
          <n-input v-model:value="newTask.name" placeholder="Görev adı" />
        </n-form-item>
        <n-form-item label="Görev Tipi">
          <n-select
            v-model:value="newTask.type"
            :options="taskTypeOptions"
          />
        </n-form-item>
        <n-form-item label="Zamanlama">
          <n-input v-model:value="newTask.schedule" placeholder="Her gün 04:00" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="flex gap-2 justify-end">
          <n-button quaternary @click="showTaskModal = false">İptal</n-button>
          <n-button type="primary" @click="addTask">
            <template #icon><PlusIcon class="w-4 h-4" /></template>
            Ekle
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import { NButton, NTag, NAvatar } from 'naive-ui'
import {
  ServerIcon,
  ArrowLeftIcon,
  PlayCircleIcon,
  StopCircleIcon,
  RefreshCwIcon,
  DownloadIcon,
  CopyIcon,
  CpuIcon,
  MemoryStickIcon,
  UsersIcon,
  ClockIcon,
  LayoutDashboardIcon,
  TerminalIcon,
  FolderIcon,
  SettingsIcon,
  InfoIcon,
  ActivityIcon,
  TrashIcon,
  ArrowDownIcon,
  SendIcon,
  FileIcon,
  EditIcon,
  SaveIcon,
  UserIcon,
  XCircleIcon,
  MapIcon,
  PuzzleIcon,
  StarIcon,
  PlusIcon,
  ShieldBan as ShieldBanIcon,
  CalendarClock as CalendarClockIcon,
  DatabaseBackup as DatabaseBackupIcon,
  ZapIcon
} from 'lucide-vue-next'
import { serversAPI } from '@/api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

const route = useRoute()
const router = useRouter()
const serverId = route.params.id

const server = ref(null)
const activeTab = ref('overview')
const consoleOutput = ref(null)
const consoleCommand = ref('')

const stats = reactive({
  cpu: 45,
  ram: 62,
  players: 12,
  maxPlayers: 32,
  uptime: '3d 12h'
})

const consoleLogs = ref([
  { time: '14:32:01', level: 'info', message: 'Server started successfully' },
  { time: '14:32:15', level: 'info', message: 'Map loaded: de_dust2' },
  { time: '14:32:45', level: 'success', message: 'Player connected: PlayerName' },
])

const currentPath = ref('/')
const files = ref([
  { name: 'addons', type: 'folder', size: '-', modified: '2 hours ago' },
  { name: 'maps', type: 'folder', size: '-', modified: '1 day ago' },
  { name: 'server.cfg', type: 'file', size: '4.2 KB', modified: '5 minutes ago' },
  { name: 'mapcycle.txt', type: 'file', size: '892 B', modified: '1 hour ago' },
])

const fileColumns = [
  {
    title: 'Ad',
    key: 'name',
    render: (row) => {
      return h('div', { class: 'flex items-center gap-2' }, [
        row.type === 'folder'
          ? h(FolderIcon, { class: 'w-4 h-4 text-orange-500' })
          : h(FileIcon, { class: 'w-4 h-4 text-gray-400' }),
        h('span', {}, row.name)
      ])
    }
  },
  { title: 'Boyut', key: 'size' },
  { title: 'Değiştirme', key: 'modified' },
  {
    title: 'İşlemler',
    key: 'actions',
    width: 120,
    render: () => {
      return h('div', { class: 'flex gap-1' }, [
        h(NButton, { quaternary: true, size: 'tiny' }, { icon: () => h(DownloadIcon, { class: 'w-3 h-3' }) }),
        h(NButton, { quaternary: true, size: 'tiny' }, { icon: () => h(EditIcon, { class: 'w-3 h-3' }) }),
        h(NButton, { quaternary: true, size: 'tiny', type: 'error' }, { icon: () => h(TrashIcon, { class: 'w-3 h-3' }) })
      ])
    }
  }
]

const config = reactive({
  hostname: 'My CS 1.6 Server',
  maxplayers: 32,
  rcon_password: '',
  mapcycle: 'de_dust2\nde_inferno\nde_nuke'
})

const onlinePlayers = ref([
  { id: 1, name: 'Player1', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=1', score: 25, ping: 45, duration: '12:34' },
  { id: 2, name: 'Player2', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=2', score: 18, ping: 67, duration: '08:12' },
])

const playerColumns = [
  {
    title: 'Oyuncu',
    key: 'name',
    render: (row) => {
      return h('div', { class: 'flex items-center gap-3' }, [
        h(NAvatar, { round: true, size: 32, src: row.avatar }),
        h('span', { class: 'font-semibold' }, row.name)
      ])
    }
  },
  {
    title: 'Skor',
    key: 'score',
    render: (row) => h(NTag, { type: 'primary', size: 'small' }, { default: () => row.score })
  },
  {
    title: 'Ping',
    key: 'ping',
    render: (row) => `${row.ping}ms`
  },
  { title: 'Süre', key: 'duration' },
  {
    title: 'İşlemler',
    key: 'actions',
    width: 100,
    render: () => {
      return h('div', { class: 'flex gap-1' }, [
        h(NButton, { quaternary: true, size: 'tiny' }, { icon: () => h(UserIcon, { class: 'w-3 h-3' }) }),
        h(NButton, { quaternary: true, size: 'tiny', type: 'error' }, { icon: () => h(XCircleIcon, { class: 'w-3 h-3' }) })
      ])
    }
  }
]

const recentActivity = ref([
  { id: 1, type: 'success', message: 'Server started successfully', time: '5 minutes ago' },
  { id: 2, type: 'info', message: 'Map changed to de_dust2', time: '15 minutes ago' },
  { id: 3, type: 'error', message: 'Player kicked for high ping', time: '1 hour ago' },
])

// Plugins Data
const installedPlugins = ref([
  { id: 1, name: 'AMX Mod X', version: '1.10.0', author: 'AMXX Team', enabled: true },
  { id: 2, name: 'ReHLDS', version: '3.12.0', author: 'ReHLDS Team', enabled: true },
  { id: 3, name: 'ReGameDLL', version: '5.21.0', author: 'ReGameDLL Team', enabled: true },
  { id: 4, name: 'MetaMod-R', version: '1.3.0', author: 'MetaMod Team', enabled: false },
])

const popularPlugins = ref([
  { id: 1, name: 'Knife Arena', description: 'Bıçak dövüşü modu', downloads: '25K+' },
  { id: 2, name: 'GunGame', description: 'Silah yarışması modu', downloads: '18K+' },
  { id: 3, name: 'Zombie Plague', description: 'Zombi salgını modu', downloads: '45K+' },
])

// Ban Data
const showBanModal = ref(false)
const banList = ref([
  { id: 1, playerName: 'Cheater123', steamId: 'STEAM_0:1:12345678', reason: 'Aimbot', permanent: true, duration: '-', bannedBy: 'Admin' },
  { id: 2, playerName: 'Toxic_Player', steamId: 'STEAM_0:0:87654321', reason: 'Hakaret', permanent: false, duration: '7 gün', bannedBy: 'Moderator' },
])

const newBan = reactive({
  playerName: '',
  steamId: '',
  reason: '',
  duration: 'permanent'
})

const banDurationOptions = [
  { label: 'Kalıcı', value: 'permanent' },
  { label: '1 Gün', value: '1d' },
  { label: '7 Gün', value: '7d' },
  { label: '30 Gün', value: '30d' }
]

const banColumns = [
  { title: 'Oyuncu', key: 'playerName' },
  {
    title: 'Steam ID',
    key: 'steamId',
    render: (row) => h('span', { class: 'font-mono text-sm' }, row.steamId)
  },
  { title: 'Sebep', key: 'reason' },
  {
    title: 'Süre',
    key: 'duration',
    render: (row) => h(NTag, { type: row.permanent ? 'error' : 'warning', size: 'small' }, { default: () => row.permanent ? 'Kalıcı' : row.duration })
  },
  { title: 'Banlayan', key: 'bannedBy' },
  {
    title: 'İşlemler',
    key: 'actions',
    width: 100,
    render: (row) => h(NButton, { type: 'success', size: 'tiny', onClick: () => unbanPlayer(row) }, { default: () => 'Kaldır' })
  }
]

// Scheduled Tasks Data
const showTaskModal = ref(false)
const scheduledTasks = ref([
  { id: 1, name: 'Günlük Restart', type: 'restart', schedule: 'Her gün 04:00', enabled: true },
  { id: 2, name: 'Saatlik Yedek', type: 'backup', schedule: 'Her saat başı', enabled: true },
  { id: 3, name: 'Haftalık Temizlik', type: 'command', schedule: 'Her Pazar 03:00', enabled: false },
])

const newTask = reactive({
  name: '',
  type: 'restart',
  schedule: ''
})

const taskTypeOptions = [
  { label: 'Yeniden Başlatma', value: 'restart' },
  { label: 'Yedekleme', value: 'backup' },
  { label: 'Komut', value: 'command' }
]

// Backup Data
const backups = ref([
  { id: 1, name: 'backup_2026-01-17_04-00', date: '17 Ocak 2026, 04:00', size: '156 MB', type: 'auto' },
  { id: 2, name: 'backup_2026-01-16_04-00', date: '16 Ocak 2026, 04:00', size: '154 MB', type: 'auto' },
  { id: 3, name: 'manual_backup_v2', date: '15 Ocak 2026, 18:30', size: '158 MB', type: 'manual' },
])

const backupSettings = reactive({
  autoBackup: true,
  frequency: 'daily',
  maxBackups: 10
})

const frequencyOptions = [
  { label: 'Saatlik', value: 'hourly' },
  { label: 'Günlük', value: 'daily' },
  { label: 'Haftalık', value: 'weekly' }
]

const chartData = computed(() => ({
  labels: ['15:00', '15:05', '15:10', '15:15', '15:20', '15:25', '15:30'],
  datasets: [
    {
      label: 'CPU %',
      data: [45, 52, 38, 65, 45, 48, 55],
      borderColor: '#f97316',
      backgroundColor: 'rgba(249, 115, 22, 0.1)',
      fill: true,
      tension: 0.4
    },
    {
      label: 'RAM %',
      data: [62, 65, 58, 70, 62, 64, 68],
      borderColor: '#8b5cf6',
      backgroundColor: 'rgba(139, 92, 246, 0.1)',
      fill: true,
      tension: 0.4
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: '#94a3b8' }
    }
  },
  scales: {
    y: {
      grid: { color: 'rgba(148, 163, 184, 0.1)' },
      ticks: { color: '#94a3b8' }
    },
    x: {
      grid: { color: 'rgba(148, 163, 184, 0.1)' },
      ticks: { color: '#94a3b8' }
    }
  }
}

onMounted(async () => {
  try {
    const data = await serversAPI.getOne(serverId)
    server.value = data
  } catch (err) {
    window.$message?.error('Sunucu yüklenemedi')
  }
})

const startServer = async () => {
  try {
    await serversAPI.start(serverId)
    if (server.value) server.value.status = 'running'
    window.$message?.success('Sunucu başlatıldı')
  } catch (err) {
    window.$message?.error('Sunucu başlatılamadı')
  }
}

const stopServer = async () => {
  try {
    await serversAPI.stop(serverId)
    if (server.value) server.value.status = 'stopped'
    window.$message?.success('Sunucu durduruldu')
  } catch (err) {
    window.$message?.error('Sunucu durdurulamadı')
  }
}

const restartServer = async () => {
  try {
    await serversAPI.restart(serverId)
    window.$message?.success('Sunucu yeniden başlatılıyor')
  } catch (err) {
    window.$message?.error('Sunucu yeniden başlatılamadı')
  }
}

const reinstallServer = async () => {
  window.$dialog?.warning({
    title: 'Yeniden Kur',
    content: 'Sunucuyu yeniden kurmak istediğinizden emin misiniz? Bu işlem geri alınamaz.',
    positiveText: 'Evet, Yeniden Kur',
    negativeText: 'İptal',
    onPositiveClick: () => {
      window.$message?.info('Sunucu yeniden kuruluyor...')
    }
  })
}

const copyServerIP = () => {
  if (server.value) {
    navigator.clipboard.writeText(`${server.value.ip}:${server.value.port}`)
    window.$message?.success('IP adresi kopyalandı')
  }
}

const sendCommand = () => {
  if (consoleCommand.value.trim()) {
    consoleLogs.value.push({
      time: new Date().toLocaleTimeString(),
      level: 'command',
      message: `> ${consoleCommand.value}`
    })
    consoleCommand.value = ''
    scrollToBottom()
  }
}

const clearConsole = () => {
  consoleLogs.value = []
  window.$message?.success('Konsol temizlendi')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (consoleOutput.value) {
      consoleOutput.value.scrollTop = consoleOutput.value.scrollHeight
    }
  })
}

const getLogColor = (level) => {
  switch (level) {
    case 'error': return 'text-red-500'
    case 'success': return 'text-green-500'
    case 'command': return 'text-orange-500'
    default: return 'text-green-400'
  }
}

const navigateToFolder = (path) => {
  currentPath.value = path
}

const saveConfig = async () => {
  window.$message?.success('Ayarlar kaydedildi')
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('tr-TR')
}

// Plugin Methods
const togglePlugin = (plugin) => {
  plugin.enabled = !plugin.enabled
  window.$message?.success(plugin.enabled ? 'Eklenti aktif edildi' : 'Eklenti devre dışı bırakıldı')
}

const removePlugin = (plugin) => {
  window.$dialog?.warning({
    title: 'Eklenti Sil',
    content: `"${plugin.name}" eklentisini silmek istediğinizden emin misiniz?`,
    positiveText: 'Sil',
    negativeText: 'İptal',
    onPositiveClick: () => {
      installedPlugins.value = installedPlugins.value.filter(p => p.id !== plugin.id)
      window.$message?.success('Eklenti silindi')
    }
  })
}

const installPlugin = (plugin) => {
  installedPlugins.value.push({
    id: Date.now(),
    name: plugin.name,
    version: '1.0.0',
    author: 'Unknown',
    enabled: true
  })
  window.$message?.success(`${plugin.name} yüklendi`)
}

// Ban Methods
const unbanPlayer = (ban) => {
  banList.value = banList.value.filter(b => b.id !== ban.id)
  window.$message?.success('Ban kaldırıldı')
}

const addBan = () => {
  if (!newBan.playerName || !newBan.steamId || !newBan.reason) {
    window.$message?.warning('Lütfen tüm alanları doldurun')
    return
  }
  banList.value.push({
    id: Date.now(),
    playerName: newBan.playerName,
    steamId: newBan.steamId,
    reason: newBan.reason,
    permanent: newBan.duration === 'permanent',
    duration: newBan.duration === 'permanent' ? '-' : newBan.duration,
    bannedBy: 'You'
  })
  showBanModal.value = false
  newBan.playerName = ''
  newBan.steamId = ''
  newBan.reason = ''
  newBan.duration = 'permanent'
  window.$message?.success('Ban eklendi')
}

// Task Methods
const toggleTask = (task) => {
  window.$message?.success(task.enabled ? 'Görev aktif edildi' : 'Görev devre dışı bırakıldı')
}

const editTask = (task) => {
  window.$message?.info('Düzenleme modal\'ı açılacak')
}

const deleteTask = (task) => {
  scheduledTasks.value = scheduledTasks.value.filter(t => t.id !== task.id)
  window.$message?.success('Görev silindi')
}

const addTask = () => {
  if (!newTask.name || !newTask.schedule) {
    window.$message?.warning('Lütfen tüm alanları doldurun')
    return
  }
  scheduledTasks.value.push({
    id: Date.now(),
    name: newTask.name,
    type: newTask.type,
    schedule: newTask.schedule,
    enabled: true
  })
  showTaskModal.value = false
  newTask.name = ''
  newTask.type = 'restart'
  newTask.schedule = ''
  window.$message?.success('Görev eklendi')
}

const createQuickTask = (type) => {
  const templates = {
    'daily-restart': { name: 'Günlük Restart', type: 'restart', schedule: 'Her gün 04:00', enabled: true },
    'hourly-backup': { name: 'Saatlik Yedek', type: 'backup', schedule: 'Her saat başı', enabled: true },
    'map-rotation': { name: 'Map Rotasyonu', type: 'command', schedule: 'Her 30 dakika', enabled: true }
  }
  scheduledTasks.value.push({ id: Date.now(), ...templates[type] })
  window.$message?.success('Görev eklendi')
}

// Backup Methods
const createBackup = () => {
  const now = new Date()
  backups.value.unshift({
    id: Date.now(),
    name: `manual_backup_${now.toISOString().split('T')[0]}`,
    date: now.toLocaleString('tr-TR'),
    size: '~160 MB',
    type: 'manual'
  })
  window.$message?.success('Yedek oluşturuluyor...')
}

const restoreBackup = (backup) => {
  window.$dialog?.warning({
    title: 'Yedeği Geri Yükle',
    content: `"${backup.name}" yedeğini geri yüklemek istediğinizden emin misiniz?`,
    positiveText: 'Geri Yükle',
    negativeText: 'İptal',
    onPositiveClick: () => {
      window.$message?.success('Yedek geri yükleniyor...')
    }
  })
}

const downloadBackup = (backup) => {
  window.$message?.info(`${backup.name} indiriliyor...`)
}

const deleteBackup = (backup) => {
  backups.value = backups.value.filter(b => b.id !== backup.id)
  window.$message?.success('Yedek silindi')
}

const saveBackupSettings = () => {
  window.$message?.success('Yedekleme ayarları kaydedildi')
}
</script>

<style scoped>
.text-gradient {
  background: linear-gradient(to right, #f97316, #8b5cf6, #06b6d4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.glass-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-card {
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: rgba(249, 115, 22, 0.3);
}

.status-online {
  background-color: #22c55e;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
  animation: pulse-glow 2s ease-in-out infinite;
}

.status-offline {
  background-color: #ef4444;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.8);
  }
}

/* Custom scrollbar for console */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.5);
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(249, 115, 22, 0.5);
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(249, 115, 22, 0.8);
}
</style>
