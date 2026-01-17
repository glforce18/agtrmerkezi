<template>
  <div class="min-h-screen ">
    <div class="container-custom py-8">
      <!-- Back Button & Header -->
      <div class="mb-6 animate-slide-down">
        <router-link to="/servers" class="inline-flex items-center gap-2 opacity-60 hover:text-primary transition-colors mb-4">
          <ArrowLeftIcon class="w-4 h-4" />
          Sunuculara Dön
        </router-link>

        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div class="flex items-center gap-4">
            <div class="w-20 h-20 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <ServerIcon class="w-10 h-10 text-white" />
            </div>
            <div>
              <h1 class="text-4xl font-display font-bold">
                <span class="neon-text">{{ server?.name || 'Sunucu' }}</span>
              </h1>
              <p class="opacity-60">
                {{ server?.ip }}:{{ server?.port }}
              </p>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <div
              :class="[
                'w-3 h-3 rounded-full',
                server?.status === 'active' ? 'status-online' : 'status-offline'
              ]"
            ></div>
            <span
              :class="[
                'badge',
                server?.status === 'active' ? 'badge-success' : 'badge-error'
              ]"
            >
              {{ server?.status === 'active' ? 'Aktif' : 'Pasif' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6 animate-slide-up">
        <BaseButton
          variant="success"
          size="sm"
          block
          :disabled="server?.status === 'active'"
          @click="startServer"
        >
          <PlayCircleIcon class="w-4 h-4 mr-1" />
          Başlat
        </BaseButton>

        <BaseButton
          variant="error"
          size="sm"
          block
          :disabled="server?.status !== 'active'"
          @click="stopServer"
        >
          <StopCircleIcon class="w-4 h-4 mr-1" />
          Durdur
        </BaseButton>

        <BaseButton
          variant="primary"
          size="sm"
          block
          @click="restartServer"
        >
          <RefreshCwIcon class="w-4 h-4 mr-1" />
          Yeniden Başlat
        </BaseButton>

        <BaseButton
          variant="ghost"
          size="sm"
          block
          @click="reinstallServer"
        >
          <DownloadIcon class="w-4 h-4 mr-1" />
          Yeniden Kur
        </BaseButton>

        <BaseButton
          variant="outline"
          size="sm"
          block
          @click="copyServerIP"
        >
          <CopyIcon class="w-4 h-4 mr-1" />
          IP Kopyala
        </BaseButton>
      </div>

      <!-- Performance Stats -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6 animate-slide-up" style="animation-delay: 0.1s">
        <BaseCard variant="glass" class="card-hover">
          <div class="p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm opacity-60">CPU Kullanımı</span>
              <CpuIcon class="w-5 h-5 text-primary" />
            </div>
            <div class="text-2xl font-bold text-primary mb-2">{{ stats.cpu }}%</div>
            <div class="w-full bg-base-200/50 rounded-full h-2">
              <div
                class="bg-gradient-to-r from-primary to-secondary h-full rounded-full transition-all"
                :style="{ width: `${stats.cpu}%` }"
              ></div>
            </div>
          </div>
        </BaseCard>

        <BaseCard variant="glass" class="card-hover">
          <div class="p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm opacity-60">RAM Kullanımı</span>
              <MemoryStickIcon class="w-5 h-5 text-secondary" />
            </div>
            <div class="text-2xl font-bold text-secondary mb-2">{{ stats.ram }}%</div>
            <div class="w-full bg-base-200/50 rounded-full h-2">
              <div
                class="bg-gradient-to-r from-secondary to-accent h-full rounded-full transition-all"
                :style="{ width: `${stats.ram}%` }"
              ></div>
            </div>
          </div>
        </BaseCard>

        <BaseCard variant="glass" class="card-hover">
          <div class="p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm opacity-60">Oyuncular</span>
              <UsersIcon class="w-5 h-5 text-accent" />
            </div>
            <div class="text-2xl font-bold text-accent">
              {{ stats.players }}/{{ stats.maxPlayers }}
            </div>
            <div class="text-xs opacity-50 mt-1">
              %{{ Math.round((stats.players / stats.maxPlayers) * 100) }} dolu
            </div>
          </div>
        </BaseCard>

        <BaseCard variant="glass" class="card-hover">
          <div class="p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm opacity-60">Uptime</span>
              <ClockIcon class="w-5 h-5 text-success" />
            </div>
            <div class="text-2xl font-bold text-success">{{ stats.uptime }}</div>
            <div class="text-xs opacity-50 mt-1">
              Sorunsuz çalışıyor
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- Tabs -->
      <div class="mb-6 animate-slide-up" style="animation-delay: 0.2s">
        <div class="tabs tabs-boxed bg-base-200/50 backdrop-blur-sm flex-wrap">
          <a
            class="tab"
            :class="{ 'tab-active': activeTab === 'overview' }"
            @click="activeTab = 'overview'"
          >
            <LayoutDashboardIcon class="w-4 h-4 mr-2" />
            Genel Bakış
          </a>
          <a
            class="tab"
            :class="{ 'tab-active': activeTab === 'console' }"
            @click="activeTab = 'console'"
          >
            <TerminalIcon class="w-4 h-4 mr-2" />
            Konsol
          </a>
          <a
            class="tab"
            :class="{ 'tab-active': activeTab === 'files' }"
            @click="activeTab = 'files'"
          >
            <FolderIcon class="w-4 h-4 mr-2" />
            Dosyalar
          </a>
          <a
            class="tab"
            :class="{ 'tab-active': activeTab === 'plugins' }"
            @click="activeTab = 'plugins'"
          >
            <PuzzleIcon class="w-4 h-4 mr-2" />
            Eklentiler
          </a>
          <a
            class="tab"
            :class="{ 'tab-active': activeTab === 'config' }"
            @click="activeTab = 'config'"
          >
            <SettingsIcon class="w-4 h-4 mr-2" />
            Ayarlar
          </a>
          <a
            class="tab"
            :class="{ 'tab-active': activeTab === 'players' }"
            @click="activeTab = 'players'"
          >
            <UsersIcon class="w-4 h-4 mr-2" />
            Oyuncular
          </a>
          <a
            class="tab"
            :class="{ 'tab-active': activeTab === 'bans' }"
            @click="activeTab = 'bans'"
          >
            <ShieldBanIcon class="w-4 h-4 mr-2" />
            Banlar
          </a>
          <a
            class="tab"
            :class="{ 'tab-active': activeTab === 'tasks' }"
            @click="activeTab = 'tasks'"
          >
            <CalendarClockIcon class="w-4 h-4 mr-2" />
            Zamanlanmış
          </a>
          <a
            class="tab"
            :class="{ 'tab-active': activeTab === 'backups' }"
            @click="activeTab = 'backups'"
          >
            <DatabaseBackupIcon class="w-4 h-4 mr-2" />
            Yedekler
          </a>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="animate-fade-in">
        <!-- Overview Tab -->
        <div v-if="activeTab === 'overview'" class="space-y-6">
          <!-- Performance Chart -->
          <BaseCard variant="glass">
            <div class="p-6">
              <h3 class="text-xl font-bold mb-4">Performans Grafiği</h3>
              <div class="h-64">
                <Line :data="chartData" :options="chartOptions" />
              </div>
            </div>
          </BaseCard>

          <div class="grid md:grid-cols-2 gap-6">
            <!-- Server Info -->
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                  <InfoIcon class="w-5 h-5 text-primary" />
                  Sunucu Bilgileri
                </h3>
                <div class="space-y-3">
                  <div class="flex justify-between items-center p-3 bg-base-200/50 rounded-lg">
                    <span class="opacity-60">Sunucu Adı</span>
                    <span class="font-semibold">{{ server?.name }}</span>
                  </div>
                  <div class="flex justify-between items-center p-3 bg-base-200/50 rounded-lg">
                    <span class="opacity-60">IP Adresi</span>
                    <span class="font-mono text-primary">{{ server?.ip }}:{{ server?.port }}</span>
                  </div>
                  <div class="flex justify-between items-center p-3 bg-base-200/50 rounded-lg">
                    <span class="opacity-60">Mevcut Map</span>
                    <span class="font-mono">{{ server?.current_map || 'de_dust2' }}</span>
                  </div>
                  <div class="flex justify-between items-center p-3 bg-base-200/50 rounded-lg">
                    <span class="opacity-60">Oyun Modu</span>
                    <span class="badge badge-primary">{{ server?.game_mode || 'Classic' }}</span>
                  </div>
                  <div class="flex justify-between items-center p-3 bg-base-200/50 rounded-lg">
                    <span class="opacity-60">Oluşturulma</span>
                    <span class="text-sm">{{ formatDate(server?.created_at) }}</span>
                  </div>
                </div>
              </div>
            </BaseCard>

            <!-- Recent Activity -->
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                  <ActivityIcon class="w-5 h-5 text-secondary" />
                  Son Aktiviteler
                </h3>
                <div class="space-y-3">
                  <div v-for="activity in recentActivity" :key="activity.id" class="flex items-start gap-3 p-3 bg-base-200/50 rounded-lg">
                    <div
                      :class="[
                        'w-2 h-2 rounded-full mt-2',
                        activity.type === 'success' ? 'bg-success' : activity.type === 'error' ? 'bg-error' : 'bg-primary'
                      ]"
                    ></div>
                    <div class="flex-1">
                      <p class="text-sm">{{ activity.message }}</p>
                      <span class="text-xs opacity-50">{{ activity.time }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </BaseCard>
          </div>
        </div>

        <!-- Console Tab -->
        <div v-if="activeTab === 'console'">
          <BaseCard variant="glass">
            <div class="p-6">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-bold flex items-center gap-2">
                  <TerminalIcon class="w-5 h-5 text-primary" />
                  Sunucu Konsolu
                </h3>
                <div class="flex gap-2">
                  <BaseButton variant="ghost" size="sm" @click="clearConsole">
                    <TrashIcon class="w-4 h-4" />
                  </BaseButton>
                  <BaseButton variant="ghost" size="sm" @click="scrollToBottom">
                    <ArrowDownIcon class="w-4 h-4" />
                  </BaseButton>
                </div>
              </div>

              <!-- Console Output -->
              <div
                ref="consoleOutput"
                class="bg-base-300 rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm text-green-400 mb-4"
              >
                <div v-for="(log, index) in consoleLogs" :key="index" class="mb-1">
                  <span class="opacity-40">[{{ log.time }}]</span>
                  <span :class="getLogColor(log.level)"> {{ log.message }}</span>
                </div>
              </div>

              <!-- Console Input -->
              <div class="flex gap-2">
                <input
                  v-model="consoleCommand"
                  type="text"
                  placeholder="Komut girin..."
                  class="input input-bordered flex-1 bg-base-200 font-mono"
                  @keyup.enter="sendCommand"
                />
                <BaseButton variant="primary" @click="sendCommand">
                  <SendIcon class="w-4 h-4 mr-2" />
                  Gönder
                </BaseButton>
              </div>
            </div>
          </BaseCard>
        </div>

        <!-- Files Tab -->
        <div v-if="activeTab === 'files'">
          <BaseCard variant="glass">
            <div class="p-6">
              <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                <FolderIcon class="w-5 h-5 text-primary" />
                Dosya Yöneticisi
              </h3>

              <!-- Breadcrumb -->
              <div class="breadcrumbs text-sm mb-4">
                <ul>
                  <li><a @click="navigateToFolder('/')">cstrike</a></li>
                  <li v-for="folder in currentPath.split('/').filter(Boolean)" :key="folder">
                    <a>{{ folder }}</a>
                  </li>
                </ul>
              </div>

              <!-- File List -->
              <div class="overflow-x-auto">
                <table class="table table-sm">
                  <thead>
                    <tr>
                      <th>Ad</th>
                      <th>Boyut</th>
                      <th>Değiştirme</th>
                      <th>İşlemler</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="file in files" :key="file.name" class="hover">
                      <td>
                        <div class="flex items-center gap-2">
                          <FolderIcon v-if="file.type === 'folder'" class="w-4 h-4 text-primary" />
                          <FileIcon v-else class="w-4 h-4 opacity-60" />
                          <span>{{ file.name }}</span>
                        </div>
                      </td>
                      <td>{{ file.size }}</td>
                      <td>{{ file.modified }}</td>
                      <td>
                        <div class="flex gap-1">
                          <button class="btn btn-xs btn-ghost" title="İndir">
                            <DownloadIcon class="w-3 h-3" />
                          </button>
                          <button class="btn btn-xs btn-ghost" title="Düzenle">
                            <EditIcon class="w-3 h-3" />
                          </button>
                          <button class="btn btn-xs btn-ghost text-error" title="Sil">
                            <TrashIcon class="w-3 h-3" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </BaseCard>
        </div>

        <!-- Config Tab -->
        <div v-if="activeTab === 'config'">
          <BaseCard variant="glass">
            <div class="p-6">
              <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                <SettingsIcon class="w-5 h-5 text-primary" />
                Sunucu Ayarları
              </h3>

              <form @submit.prevent="saveConfig" class="space-y-4">
                <BaseInput
                  v-model="config.hostname"
                  label="Sunucu Adı"
                  placeholder="My CS 1.6 Server"
                />

                <BaseInput
                  v-model="config.maxplayers"
                  label="Maksimum Oyuncu"
                  type="number"
                  min="2"
                  max="32"
                />

                <BaseInput
                  v-model="config.rcon_password"
                  label="RCON Şifresi"
                  type="password"
                />

                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Map Rotasyonu</span>
                  </label>
                  <textarea
                    v-model="config.mapcycle"
                    class="textarea textarea-bordered h-24 bg-base-200"
                    placeholder="de_dust2&#10;de_inferno&#10;de_nuke"
                  ></textarea>
                </div>

                <div class="flex gap-2">
                  <BaseButton variant="gaming" type="submit">
                    <SaveIcon class="w-4 h-4 mr-2" />
                    Kaydet
                  </BaseButton>
                  <BaseButton variant="ghost" type="button">
                    İptal
                  </BaseButton>
                </div>
              </form>
            </div>
          </BaseCard>
        </div>

        <!-- Players Tab -->
        <div v-if="activeTab === 'players'">
          <BaseCard variant="glass">
            <div class="p-6">
              <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                <UsersIcon class="w-5 h-5 text-primary" />
                Aktif Oyuncular ({{ onlinePlayers.length }})
              </h3>

              <div class="overflow-x-auto">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Oyuncu</th>
                      <th>Skor</th>
                      <th>Ping</th>
                      <th>Süre</th>
                      <th>İşlemler</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="player in onlinePlayers" :key="player.id">
                      <td>
                        <div class="flex items-center gap-3">
                          <div class="avatar">
                            <div class="w-8 h-8 rounded-full">
                              <img :src="player.avatar" />
                            </div>
                          </div>
                          <span class="font-semibold">{{ player.name }}</span>
                        </div>
                      </td>
                      <td>
                        <span class="badge badge-primary">{{ player.score }}</span>
                      </td>
                      <td>{{ player.ping }}ms</td>
                      <td>{{ player.duration }}</td>
                      <td>
                        <div class="flex gap-1">
                          <button class="btn btn-xs btn-ghost" title="Profil">
                            <UserIcon class="w-3 h-3" />
                          </button>
                          <button class="btn btn-xs btn-error" title="Kick">
                            <XCircleIcon class="w-3 h-3" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </BaseCard>
        </div>

        <!-- Plugins Tab -->
        <div v-if="activeTab === 'plugins'">
          <div class="grid lg:grid-cols-3 gap-6">
            <!-- Installed Plugins -->
            <div class="lg:col-span-2">
              <BaseCard variant="glass">
                <div class="p-6">
                  <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-bold flex items-center gap-2">
                      <PuzzleIcon class="w-5 h-5 text-primary" />
                      Yüklü Eklentiler
                    </h3>
                    <BaseButton variant="primary" size="sm">
                      <PlusIcon class="w-4 h-4 mr-1" />
                      Eklenti Yükle
                    </BaseButton>
                  </div>

                  <div class="space-y-3">
                    <div v-for="plugin in installedPlugins" :key="plugin.id"
                         class="flex items-center justify-between p-4 bg-base-200/50 rounded-lg hover:bg-base-200 transition-colors">
                      <div class="flex items-center gap-3">
                        <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                          <PuzzleIcon class="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <h4 class="font-bold">{{ plugin.name }}</h4>
                          <p class="text-sm opacity-60">{{ plugin.version }} · {{ plugin.author }}</p>
                        </div>
                      </div>
                      <div class="flex items-center gap-2">
                        <span :class="['badge badge-sm', plugin.enabled ? 'badge-success' : 'badge-error']">
                          {{ plugin.enabled ? 'Aktif' : 'Pasif' }}
                        </span>
                        <button class="btn btn-xs btn-ghost" @click="togglePlugin(plugin)">
                          <SettingsIcon class="w-3 h-3" />
                        </button>
                        <button class="btn btn-xs btn-error" @click="removePlugin(plugin)">
                          <TrashIcon class="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </BaseCard>
            </div>

            <!-- Popular Plugins -->
            <div>
              <BaseCard variant="glass">
                <div class="p-6">
                  <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                    <StarIcon class="w-5 h-5 text-yellow-500" />
                    Popüler Eklentiler
                  </h3>
                  <div class="space-y-3">
                    <div v-for="plugin in popularPlugins" :key="plugin.id"
                         class="p-3 bg-base-200/50 rounded-lg hover:bg-base-200 transition-colors cursor-pointer">
                      <div class="flex items-center justify-between mb-2">
                        <h4 class="font-semibold text-sm">{{ plugin.name }}</h4>
                        <span class="text-xs text-yellow-500">{{ plugin.downloads }}</span>
                      </div>
                      <p class="text-xs opacity-60 mb-2">{{ plugin.description }}</p>
                      <BaseButton variant="outline" size="xs" block @click="installPlugin(plugin)">
                        <DownloadIcon class="w-3 h-3 mr-1" />
                        Yükle
                      </BaseButton>
                    </div>
                  </div>
                </div>
              </BaseCard>
            </div>
          </div>
        </div>

        <!-- Bans Tab -->
        <div v-if="activeTab === 'bans'">
          <BaseCard variant="glass">
            <div class="p-6">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-bold flex items-center gap-2">
                  <ShieldBanIcon class="w-5 h-5 text-error" />
                  Ban Listesi
                </h3>
                <BaseButton variant="error" size="sm" @click="showBanModal = true">
                  <PlusIcon class="w-4 h-4 mr-1" />
                  Yeni Ban
                </BaseButton>
              </div>

              <div class="overflow-x-auto">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Oyuncu</th>
                      <th>Steam ID</th>
                      <th>Sebep</th>
                      <th>Süre</th>
                      <th>Banlayan</th>
                      <th>İşlemler</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="ban in banList" :key="ban.id">
                      <td class="font-semibold">{{ ban.playerName }}</td>
                      <td class="font-mono text-sm">{{ ban.steamId }}</td>
                      <td>{{ ban.reason }}</td>
                      <td>
                        <span :class="['badge badge-sm', ban.permanent ? 'badge-error' : 'badge-warning']">
                          {{ ban.permanent ? 'Kalıcı' : ban.duration }}
                        </span>
                      </td>
                      <td class="opacity-60">{{ ban.bannedBy }}</td>
                      <td>
                        <button class="btn btn-xs btn-success" @click="unbanPlayer(ban)">
                          Kaldır
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </BaseCard>
        </div>

        <!-- Scheduled Tasks Tab -->
        <div v-if="activeTab === 'tasks'">
          <div class="grid lg:grid-cols-2 gap-6">
            <BaseCard variant="glass">
              <div class="p-6">
                <div class="flex justify-between items-center mb-4">
                  <h3 class="text-xl font-bold flex items-center gap-2">
                    <CalendarClockIcon class="w-5 h-5 text-primary" />
                    Zamanlanmış Görevler
                  </h3>
                  <BaseButton variant="primary" size="sm" @click="showTaskModal = true">
                    <PlusIcon class="w-4 h-4 mr-1" />
                    Yeni Görev
                  </BaseButton>
                </div>

                <div class="space-y-3">
                  <div v-for="task in scheduledTasks" :key="task.id"
                       class="flex items-center justify-between p-4 bg-base-200/50 rounded-lg">
                    <div class="flex items-center gap-3">
                      <div :class="['w-10 h-10 rounded-lg flex items-center justify-center',
                                   task.type === 'restart' ? 'bg-warning/20 text-warning' :
                                   task.type === 'backup' ? 'bg-info/20 text-info' :
                                   'bg-primary/20 text-primary']">
                        <RefreshCwIcon v-if="task.type === 'restart'" class="w-5 h-5" />
                        <DatabaseBackupIcon v-else-if="task.type === 'backup'" class="w-5 h-5" />
                        <TerminalIcon v-else class="w-5 h-5" />
                      </div>
                      <div>
                        <h4 class="font-bold">{{ task.name }}</h4>
                        <p class="text-sm opacity-60">{{ task.schedule }}</p>
                      </div>
                    </div>
                    <div class="flex items-center gap-2">
                      <input type="checkbox" :checked="task.enabled" class="toggle toggle-sm toggle-primary"
                             @change="toggleTask(task)" />
                      <button class="btn btn-xs btn-ghost" @click="editTask(task)">
                        <EditIcon class="w-3 h-3" />
                      </button>
                      <button class="btn btn-xs btn-error" @click="deleteTask(task)">
                        <TrashIcon class="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </BaseCard>

            <!-- Quick Task Templates -->
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                  <ZapIcon class="w-5 h-5 text-yellow-500" />
                  Hızlı Görev Şablonları
                </h3>
                <div class="space-y-3">
                  <button class="w-full p-4 bg-base-200/50 rounded-lg hover:bg-base-200 transition-colors text-left"
                          @click="createQuickTask('daily-restart')">
                    <div class="flex items-center gap-3">
                      <RefreshCwIcon class="w-5 h-5 text-warning" />
                      <div>
                        <h4 class="font-semibold">Günlük Yeniden Başlatma</h4>
                        <p class="text-sm opacity-60">Her gün 04:00'da sunucuyu yeniden başlat</p>
                      </div>
                    </div>
                  </button>
                  <button class="w-full p-4 bg-base-200/50 rounded-lg hover:bg-base-200 transition-colors text-left"
                          @click="createQuickTask('hourly-backup')">
                    <div class="flex items-center gap-3">
                      <DatabaseBackupIcon class="w-5 h-5 text-info" />
                      <div>
                        <h4 class="font-semibold">Saatlik Yedekleme</h4>
                        <p class="text-sm opacity-60">Her saat başı otomatik yedek al</p>
                      </div>
                    </div>
                  </button>
                  <button class="w-full p-4 bg-base-200/50 rounded-lg hover:bg-base-200 transition-colors text-left"
                          @click="createQuickTask('map-rotation')">
                    <div class="flex items-center gap-3">
                      <MapIcon class="w-5 h-5 text-success" />
                      <div>
                        <h4 class="font-semibold">Map Rotasyonu</h4>
                        <p class="text-sm opacity-60">Her 30 dakikada map değiştir</p>
                      </div>
                    </div>
                  </button>
                </div>
              </div>
            </BaseCard>
          </div>
        </div>

        <!-- Backups Tab -->
        <div v-if="activeTab === 'backups'">
          <div class="grid lg:grid-cols-3 gap-6">
            <div class="lg:col-span-2">
              <BaseCard variant="glass">
                <div class="p-6">
                  <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-bold flex items-center gap-2">
                      <DatabaseBackupIcon class="w-5 h-5 text-primary" />
                      Yedekler
                    </h3>
                    <BaseButton variant="gaming" size="sm" @click="createBackup">
                      <PlusIcon class="w-4 h-4 mr-1" />
                      Yeni Yedek
                    </BaseButton>
                  </div>

                  <div class="space-y-3">
                    <div v-for="backup in backups" :key="backup.id"
                         class="flex items-center justify-between p-4 bg-base-200/50 rounded-lg">
                      <div class="flex items-center gap-3">
                        <div class="w-12 h-12 rounded-lg bg-info/20 flex items-center justify-center">
                          <DatabaseBackupIcon class="w-6 h-6 text-info" />
                        </div>
                        <div>
                          <h4 class="font-bold">{{ backup.name }}</h4>
                          <p class="text-sm opacity-60">{{ backup.date }} · {{ backup.size }}</p>
                        </div>
                      </div>
                      <div class="flex items-center gap-2">
                        <span :class="['badge badge-sm', backup.type === 'auto' ? 'badge-info' : 'badge-primary']">
                          {{ backup.type === 'auto' ? 'Otomatik' : 'Manuel' }}
                        </span>
                        <button class="btn btn-xs btn-success" @click="restoreBackup(backup)">
                          <RefreshCwIcon class="w-3 h-3 mr-1" />
                          Geri Yükle
                        </button>
                        <button class="btn btn-xs btn-ghost" @click="downloadBackup(backup)">
                          <DownloadIcon class="w-3 h-3" />
                        </button>
                        <button class="btn btn-xs btn-error" @click="deleteBackup(backup)">
                          <TrashIcon class="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </BaseCard>
            </div>

            <!-- Backup Settings -->
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                  <SettingsIcon class="w-5 h-5 text-primary" />
                  Yedekleme Ayarları
                </h3>
                <div class="space-y-4">
                  <div class="form-control">
                    <label class="label cursor-pointer justify-start gap-3">
                      <input type="checkbox" v-model="backupSettings.autoBackup" class="toggle toggle-primary" />
                      <div>
                        <span class="label-text font-semibold">Otomatik Yedekleme</span>
                        <p class="text-xs opacity-60">Düzenli aralıklarla yedek al</p>
                      </div>
                    </label>
                  </div>

                  <div class="form-control">
                    <label class="label">
                      <span class="label-text">Yedekleme Sıklığı</span>
                    </label>
                    <select v-model="backupSettings.frequency" class="select select-bordered bg-base-200">
                      <option value="hourly">Saatlik</option>
                      <option value="daily">Günlük</option>
                      <option value="weekly">Haftalık</option>
                    </select>
                  </div>

                  <div class="form-control">
                    <label class="label">
                      <span class="label-text">Maksimum Yedek Sayısı</span>
                    </label>
                    <input type="number" v-model="backupSettings.maxBackups"
                           class="input input-bordered bg-base-200" min="1" max="50" />
                  </div>

                  <BaseButton variant="gaming" block @click="saveBackupSettings">
                    <SaveIcon class="w-4 h-4 mr-2" />
                    Ayarları Kaydet
                  </BaseButton>
                </div>
              </div>
            </BaseCard>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
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

// Scheduled Tasks Data
const showTaskModal = ref(false)
const scheduledTasks = ref([
  { id: 1, name: 'Günlük Restart', type: 'restart', schedule: 'Her gün 04:00', enabled: true },
  { id: 2, name: 'Saatlik Yedek', type: 'backup', schedule: 'Her saat başı', enabled: true },
  { id: 3, name: 'Haftalık Temizlik', type: 'command', schedule: 'Her Pazar 03:00', enabled: false },
])

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

const chartData = computed(() => ({
  labels: ['15:00', '15:05', '15:10', '15:15', '15:20', '15:25', '15:30'],
  datasets: [
    {
      label: 'CPU %',
      data: [45, 52, 38, 65, 45, 48, 55],
      borderColor: '#ec4899',
      backgroundColor: 'rgba(236, 72, 153, 0.1)',
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
    // Failed to load server - will show empty state
  }
})

const startServer = async () => {
  try {
    await serversAPI.start(serverId)
    if (server.value) server.value.status = 'active'
  } catch (err) {
    // Failed to start server - status unchanged
  }
}

const stopServer = async () => {
  try {
    await serversAPI.stop(serverId)
    if (server.value) server.value.status = 'inactive'
  } catch (err) {
    // Failed to stop server - status unchanged
  }
}

const restartServer = async () => {
  try {
    await serversAPI.restart(serverId)
  } catch (err) {
    // Failed to restart server - status unchanged
  }
}

const reinstallServer = async () => {
  if (confirm('Sunucuyu yeniden kurmak istediğinizden emin misiniz?')) {
    // Reinstall logic
  }
}

const copyServerIP = () => {
  if (server.value) {
    navigator.clipboard.writeText(`${server.value.ip}:${server.value.port}`)
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
    case 'error': return 'text-error'
    case 'success': return 'text-success'
    case 'command': return 'text-primary'
    default: return 'text-green-400'
  }
}

const navigateToFolder = (path) => {
  currentPath.value = path
}

const saveConfig = async () => {
  // Save config logic
  // Save config
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('tr-TR')
}

// Plugin Methods
const togglePlugin = (plugin) => {
  plugin.enabled = !plugin.enabled
}

const removePlugin = (plugin) => {
  installedPlugins.value = installedPlugins.value.filter(p => p.id !== plugin.id)
}

const installPlugin = (plugin) => {
  installedPlugins.value.push({
    id: Date.now(),
    name: plugin.name,
    version: '1.0.0',
    author: 'Unknown',
    enabled: true
  })
}

// Ban Methods
const unbanPlayer = (ban) => {
  banList.value = banList.value.filter(b => b.id !== ban.id)
}

// Task Methods
const toggleTask = (task) => {
  task.enabled = !task.enabled
}

const editTask = (task) => {
  // Edit task
}

const deleteTask = (task) => {
  scheduledTasks.value = scheduledTasks.value.filter(t => t.id !== task.id)
}

const createQuickTask = (type) => {
  const templates = {
    'daily-restart': { name: 'Günlük Restart', type: 'restart', schedule: 'Her gün 04:00', enabled: true },
    'hourly-backup': { name: 'Saatlik Yedek', type: 'backup', schedule: 'Her saat başı', enabled: true },
    'map-rotation': { name: 'Map Rotasyonu', type: 'command', schedule: 'Her 30 dakika', enabled: true }
  }
  scheduledTasks.value.push({ id: Date.now(), ...templates[type] })
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
}

const restoreBackup = (backup) => {
  if (confirm(`"${backup.name}" yedeğini geri yüklemek istediğinizden emin misiniz?`)) {
    // Restore backup
  }
}

const downloadBackup = (backup) => {
  // Download backup
}

const deleteBackup = (backup) => {
  backups.value = backups.value.filter(b => b.id !== backup.id)
}

const saveBackupSettings = () => {
  // Save backup settings
}
</script>

<style scoped>
.neon-text {
  @apply text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-accent;
}

.status-online {
  @apply bg-success shadow-[0_0_10px_rgba(16,185,129,0.5)];
  animation: pulse-glow 2s ease-in-out infinite;
}

.status-offline {
  @apply bg-error;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.8);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-down {
  animation: slideDown 0.6s ease-out;
}

.animate-slide-up {
  animation: slideUp 0.6s ease-out 0.2s backwards;
}

.animate-fade-in {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
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
  background: rgba(99, 102, 241, 0.5);
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(99, 102, 241, 0.8);
}
</style>
