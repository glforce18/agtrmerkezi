<template>
  <div class="min-h-screen ">
    <div class="container-custom py-8">
      <!-- Header with Quick Actions -->
      <div class="mb-8 animate-slide-down">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div>
            <h1 class="text-4xl font-display font-bold mb-2">
              <span class="neon-text">Admin Control Center</span>
            </h1>
            <p class="opacity-60">
              Tüm sistem kontrolü ve yönetimi
            </p>
          </div>
          <div class="flex gap-2">
            <BaseButton variant="success" size="sm" @click="refreshData">
              <RefreshCwIcon class="w-4 h-4 mr-1" />
              Yenile
            </BaseButton>
            <BaseButton variant="error" size="sm" @click="showMaintenanceModal = true">
              <AlertTriangleIcon class="w-4 h-4 mr-1" />
              Bakım Modu
            </BaseButton>
            <BaseButton variant="ghost" size="sm" @click="exportLogs">
              <DownloadIcon class="w-4 h-4 mr-1" />
              Export
            </BaseButton>
          </div>
        </div>

        <!-- Advanced Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <BaseCard variant="glass" class="card-hover cursor-pointer" @click="activeTab = 'users'">
            <div class="p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm opacity-60">Total Users</span>
                <UsersIcon class="w-5 h-5 text-primary" />
              </div>
              <div class="text-3xl font-bold text-primary">{{ stats.totalUsers }}</div>
              <div class="flex items-center gap-2 text-xs mt-1">
                <TrendingUpIcon class="w-3 h-3 text-success" />
                <span class="text-success">+{{ stats.newUsersToday }} bugün</span>
              </div>
            </div>
          </BaseCard>

          <BaseCard variant="glass" class="card-hover cursor-pointer" @click="activeTab = 'servers'">
            <div class="p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm opacity-60">Active Servers</span>
                <ServerIcon class="w-5 h-5 text-secondary" />
              </div>
              <div class="text-3xl font-bold text-secondary">{{ stats.activeServers }}/{{ stats.totalServers }}</div>
              <div class="w-full bg-base-200/50 rounded-full h-1 mt-2">
                <div class="bg-secondary h-full rounded-full" :style="{ width: `${(stats.activeServers/stats.totalServers)*100}%` }"></div>
              </div>
            </div>
          </BaseCard>

          <BaseCard variant="glass" class="card-hover cursor-pointer" @click="activeTab = 'analytics'">
            <div class="p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm opacity-60">Revenue (MTD)</span>
                <DollarSignIcon class="w-5 h-5 text-accent" />
              </div>
              <div class="text-3xl font-bold text-accent">${{ stats.revenue.toLocaleString() }}</div>
              <div class="text-xs text-success mt-1">
                +12.5% vs last month
              </div>
            </div>
          </BaseCard>

          <BaseCard variant="glass" class="card-hover cursor-pointer" @click="activeTab = 'monitoring'">
            <div class="p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm opacity-60">System Load</span>
                <CpuIcon class="w-5 h-5 text-warning" />
              </div>
              <div class="text-3xl font-bold text-warning">{{ systemMetrics.cpuUsage }}%</div>
              <div class="text-xs opacity-60 mt-1">
                RAM: {{ systemMetrics.ramUsage }}%
              </div>
            </div>
          </BaseCard>

          <BaseCard variant="glass" class="card-hover cursor-pointer" @click="activeTab = 'logs'">
            <div class="p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm opacity-60">System Health</span>
                <ActivityIcon class="w-5 h-5 text-success" />
              </div>
              <div class="text-3xl font-bold text-success">{{ systemMetrics.health }}%</div>
              <div class="text-xs text-success mt-1">
                All systems operational
              </div>
            </div>
          </BaseCard>
        </div>
      </div>

      <!-- Advanced Tabs Navigation -->
      <div class="mb-6 animate-slide-up" style="animation-delay: 0.1s">
        <div class="tabs tabs-boxed bg-base-200/50 backdrop-blur-sm overflow-x-auto flex-nowrap">
          <a class="tab whitespace-nowrap" :class="{ 'tab-active': activeTab === 'dashboard' }" @click="activeTab = 'dashboard'">
            <LayoutDashboardIcon class="w-4 h-4 mr-2" />
            Dashboard
          </a>
          <a class="tab whitespace-nowrap" :class="{ 'tab-active': activeTab === 'users' }" @click="activeTab = 'users'">
            <UsersIcon class="w-4 h-4 mr-2" />
            Users
          </a>
          <a class="tab whitespace-nowrap" :class="{ 'tab-active': activeTab === 'servers' }" @click="activeTab = 'servers'">
            <ServerIcon class="w-4 h-4 mr-2" />
            Servers
          </a>
          <a class="tab whitespace-nowrap" :class="{ 'tab-active': activeTab === 'analytics' }" @click="activeTab = 'analytics'">
            <BarChartIcon class="w-4 h-4 mr-2" />
            Analytics
          </a>
          <a class="tab whitespace-nowrap" :class="{ 'tab-active': activeTab === 'monitoring' }" @click="activeTab = 'monitoring'">
            <MonitorIcon class="w-4 h-4 mr-2" />
            Monitoring
          </a>
          <a class="tab whitespace-nowrap" :class="{ 'tab-active': activeTab === 'logs' }" @click="activeTab = 'logs'">
            <ScrollTextIcon class="w-4 h-4 mr-2" />
            Logs
          </a>
          <a class="tab whitespace-nowrap" :class="{ 'tab-active': activeTab === 'security' }" @click="activeTab = 'security'">
            <ShieldIcon class="w-4 h-4 mr-2" />
            Security
          </a>
          <a class="tab whitespace-nowrap" :class="{ 'tab-active': activeTab === 'database' }" @click="activeTab = 'database'">
            <DatabaseIcon class="w-4 h-4 mr-2" />
            Database
          </a>
          <a class="tab whitespace-nowrap" :class="{ 'tab-active': activeTab === 'api' }" @click="activeTab = 'api'">
            <CodeIcon class="w-4 h-4 mr-2" />
            API
          </a>
          <a class="tab whitespace-nowrap" :class="{ 'tab-active': activeTab === 'notifications' }" @click="activeTab = 'notifications'">
            <BellIcon class="w-4 h-4 mr-2" />
            Notifications
          </a>
          <a class="tab whitespace-nowrap" :class="{ 'tab-active': activeTab === 'settings' }" @click="activeTab = 'settings'">
            <SettingsIcon class="w-4 h-4 mr-2" />
            Settings
          </a>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="animate-fade-in">
        <!-- Dashboard Tab -->
        <div v-if="activeTab === 'dashboard'">
          <div class="grid lg:grid-cols-2 gap-6 mb-6">
            <!-- Real-time Activity Chart -->
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">Real-time Activity (Last 24h)</h3>
                <div class="h-64">
                  <Line :data="activityChartData" :options="chartOptions" />
                </div>
              </div>
            </BaseCard>

            <!-- User Growth Chart -->
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">User Growth (Last 30 days)</h3>
                <div class="h-64">
                  <Line :data="userGrowthData" :options="chartOptions" />
                </div>
              </div>
            </BaseCard>
          </div>

          <div class="grid lg:grid-cols-3 gap-6">
            <!-- Recent Activity -->
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">Recent Activity</h3>
                <div class="space-y-3 max-h-96 overflow-y-auto">
                  <div v-for="activity in recentActivity" :key="activity.id" class="flex items-start gap-3 p-3 bg-base-200/50 rounded-lg">
                    <div :class="['w-2 h-2 rounded-full mt-2', `bg-${activity.type}`]"></div>
                    <div class="flex-1">
                      <p class="text-sm">{{ activity.message }}</p>
                      <span class="text-xs opacity-50">{{ activity.time }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </BaseCard>

            <!-- Top Users -->
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">Top Users (Activity)</h3>
                <div class="space-y-3">
                  <div v-for="user in topUsers" :key="user.id" class="flex items-center justify-between p-3 bg-base-200/50 rounded-lg">
                    <div class="flex items-center gap-3">
                      <div class="avatar">
                        <div class="w-10 h-10 rounded-full">
                          <img :src="user.avatar" />
                        </div>
                      </div>
                      <div>
                        <p class="font-semibold">{{ user.username }}</p>
                        <p class="text-xs opacity-50">{{ user.servers }} servers</p>
                      </div>
                    </div>
                    <span class="badge badge-primary">{{ user.activity }}</span>
                  </div>
                </div>
              </div>
            </BaseCard>

            <!-- Quick Actions -->
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">Quick Actions</h3>
                <div class="space-y-2">
                  <BaseButton variant="primary" block size="sm" @click="createBackup">
                    <DatabaseIcon class="w-4 h-4 mr-2" />
                    Create Backup
                  </BaseButton>
                  <BaseButton variant="secondary" block size="sm" @click="clearCache">
                    <TrashIcon class="w-4 h-4 mr-2" />
                    Clear Cache
                  </BaseButton>
                  <BaseButton variant="accent" block size="sm" @click="activeTab = 'users'">
                    <UserPlusIcon class="w-4 h-4 mr-2" />
                    Add User
                  </BaseButton>
                  <BaseButton variant="warning" block size="sm" @click="restartServices">
                    <RefreshCwIcon class="w-4 h-4 mr-2" />
                    Restart Services
                  </BaseButton>
                  <BaseButton variant="ghost" block size="sm" @click="activeTab = 'settings'">
                    <SettingsIcon class="w-4 h-4 mr-2" />
                    System Settings
                  </BaseButton>
                </div>
              </div>
            </BaseCard>
          </div>
        </div>

        <!-- Users Tab -->
        <div v-if="activeTab === 'users'">
          <BaseCard variant="glass">
            <div class="p-6">
              <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                <h3 class="text-xl font-bold">User Management</h3>
                <div class="flex flex-wrap gap-2">
                  <BaseInput
                    v-model="userSearch"
                    placeholder="Search users..."
                    :icon="SearchIcon"
                    class="w-64"
                  />
                  <select class="select select-bordered select-sm bg-base-200">
                    <option value="all">All Roles</option>
                    <option value="admin">Admin</option>
                    <option value="moderatör">Moderatör</option>
                    <option value="user">User</option>
                  </select>
                  <select class="select select-bordered select-sm bg-base-200">
                    <option value="all">All Status</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="banned">Banned</option>
                  </select>
                  <BaseButton variant="gaming" size="sm">
                    <PlusCircleIcon class="w-4 h-4 mr-1" />
                    New User
                  </BaseButton>
                  <BaseButton variant="ghost" size="sm">
                    <DownloadIcon class="w-4 h-4 mr-1" />
                    Export CSV
                  </BaseButton>
                </div>
              </div>

              <div class="overflow-x-auto">
                <table class="table">
                  <thead>
                    <tr>
                      <th>
                        <input type="checkbox" class="checkbox checkbox-sm" />
                      </th>
                      <th>User</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Servers</th>
                      <th>Status</th>
                      <th>2FA</th>
                      <th>Last Login</th>
                      <th>Registered</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="user in users" :key="user.id" class="hover">
                      <td>
                        <input type="checkbox" class="checkbox checkbox-sm" />
                      </td>
                      <td>
                        <div class="flex items-center gap-3">
                          <div class="avatar">
                            <div class="w-10 h-10 rounded-full">
                              <img :src="user.avatar" />
                            </div>
                          </div>
                          <div>
                            <div class="font-semibold">{{ user.username }}</div>
                            <div class="text-xs opacity-50">ID: {{ user.id }}</div>
                          </div>
                        </div>
                      </td>
                      <td>{{ user.email }}</td>
                      <td>
                        <select class="select select-xs bg-base-200" v-model="user.role">
                          <option value="admin">Admin</option>
                          <option value="moderatör">Moderatör</option>
                          <option value="user">User</option>
                        </select>
                      </td>
                      <td>{{ user.serverCount }}</td>
                      <td>
                        <span :class="['badge badge-sm', user.isActive ? 'badge-success' : 'badge-error']">
                          {{ user.isActive ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>
                        <span :class="['badge badge-sm', user.twoFactorEnabled ? 'badge-success' : 'badge-ghost']">
                          {{ user.twoFactorEnabled ? 'Enabled' : 'Disabled' }}
                        </span>
                      </td>
                      <td class="text-xs">{{ user.lastLogin }}</td>
                      <td class="text-xs">{{ user.createdAt }}</td>
                      <td>
                        <div class="dropdown dropdown-end">
                          <label tabindex="0" class="btn btn-xs btn-ghost">
                            <MoreVerticalIcon class="w-4 h-4" />
                          </label>
                          <ul tabindex="0" class="dropdown-content menu p-2 shadow bg-base-200 rounded-box w-52">
                            <li><a><EditIcon class="w-4 h-4" /> Edit User</a></li>
                            <li><a><KeyIcon class="w-4 h-4" /> Reset Password</a></li>
                            <li><a><ShieldIcon class="w-4 h-4" /> Ban User</a></li>
                            <li><a><MailIcon class="w-4 h-4" /> Send Email</a></li>
                            <li><a class="text-error"><TrashIcon class="w-4 h-4" /> Delete User</a></li>
                          </ul>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Bulk Actions -->
              <div class="flex items-center justify-between mt-4 p-4 bg-base-200/50 rounded-lg">
                <div class="flex gap-2">
                  <BaseButton variant="ghost" size="sm">
                    <TrashIcon class="w-4 h-4 mr-1" />
                    Delete Selected
                  </BaseButton>
                  <BaseButton variant="ghost" size="sm">
                    <MailIcon class="w-4 h-4 mr-1" />
                    Email Selected
                  </BaseButton>
                  <BaseButton variant="ghost" size="sm">
                    <ShieldIcon class="w-4 h-4 mr-1" />
                    Ban Selected
                  </BaseButton>
                </div>
                <div class="join">
                  <button class="join-item btn btn-sm">«</button>
                  <button class="join-item btn btn-sm btn-active">1</button>
                  <button class="join-item btn btn-sm">2</button>
                  <button class="join-item btn btn-sm">3</button>
                  <button class="join-item btn btn-sm">»</button>
                </div>
              </div>
            </div>
          </BaseCard>
        </div>

        <!-- Servers Tab -->
        <div v-if="activeTab === 'servers'">
          <BaseCard variant="glass">
            <div class="p-6">
              <div class="flex justify-between items-center mb-6">
                <h3 class="text-xl font-bold">Server Management</h3>
                <div class="flex gap-2">
                  <select class="select select-bordered select-sm bg-base-200">
                    <option value="all">All Status</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="error">Error</option>
                  </select>
                  <BaseButton variant="ghost" size="sm">
                    <RefreshCwIcon class="w-4 h-4 mr-1" />
                    Refresh All
                  </BaseButton>
                </div>
              </div>

              <div class="overflow-x-auto">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Server</th>
                      <th>Owner</th>
                      <th>IP:Port</th>
                      <th>Map</th>
                      <th>Players</th>
                      <th>CPU/RAM</th>
                      <th>Status</th>
                      <th>Uptime</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="server in servers" :key="server.id" class="hover">
                      <td>
                        <div class="font-semibold">{{ server.name }}</div>
                        <div class="text-xs opacity-50">ID: {{ server.id }}</div>
                      </td>
                      <td>{{ server.owner }}</td>
                      <td class="font-mono text-sm">{{ server.ip }}:{{ server.port }}</td>
                      <td class="font-mono text-xs">{{ server.map }}</td>
                      <td>
                        <div class="text-sm font-semibold">{{ server.players }}/{{ server.maxPlayers }}</div>
                        <div class="w-20 bg-base-200/50 rounded-full h-1">
                          <div class="bg-primary h-full rounded-full" :style="{ width: `${(server.players/server.maxPlayers)*100}%` }"></div>
                        </div>
                      </td>
                      <td class="text-xs">
                        <div>CPU: {{ server.cpu }}%</div>
                        <div>RAM: {{ server.ram }}%</div>
                      </td>
                      <td>
                        <span :class="['badge badge-sm', server.status === 'running' ? 'badge-success' : 'badge-error']">
                          {{ server.status }}
                        </span>
                      </td>
                      <td class="text-xs">{{ server.uptime }}</td>
                      <td>
                        <div class="flex gap-1">
                          <button class="btn btn-xs btn-ghost" title="View">
                            <EyeIcon class="w-3 h-3" />
                          </button>
                          <button class="btn btn-xs btn-ghost" :title="server.status === 'running' ? 'Stop' : 'Start'">
                            <component :is="server.status === 'running' ? StopCircleIcon : PlayCircleIcon" class="w-3 h-3" />
                          </button>
                          <button class="btn btn-xs btn-ghost" title="Restart">
                            <RefreshCwIcon class="w-3 h-3" />
                          </button>
                          <button class="btn btn-xs btn-ghost text-error" title="Delete">
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

        <!-- Analytics Tab -->
        <div v-if="activeTab === 'analytics'">
          <div class="grid lg:grid-cols-2 gap-6 mb-6">
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">Revenue Analytics</h3>
                <div class="h-64">
                  <Line :data="revenueChartData" :options="chartOptions" />
                </div>
              </div>
            </BaseCard>

            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">Server Usage Distribution</h3>
                <div class="h-64">
                  <Bar :data="serverDistributionData" :options="chartOptions" />
                </div>
              </div>
            </BaseCard>
          </div>

          <div class="grid lg:grid-cols-3 gap-6">
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-lg font-bold mb-4">Top Revenue Sources</h3>
                <div class="space-y-3">
                  <div v-for="source in topRevenueSources" :key="source.name" class="flex justify-between items-center p-3 bg-base-200/50 rounded-lg">
                    <span>{{ source.name }}</span>
                    <span class="font-bold text-primary">${{ source.amount }}</span>
                  </div>
                </div>
              </div>
            </BaseCard>

            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-lg font-bold mb-4">Conversion Rates</h3>
                <div class="space-y-4">
                  <div>
                    <div class="flex justify-between mb-1">
                      <span class="text-sm">Free to Pro</span>
                      <span class="text-sm font-bold">12.5%</span>
                    </div>
                    <div class="w-full bg-base-200/50 rounded-full h-2">
                      <div class="bg-primary h-full rounded-full" style="width: 12.5%"></div>
                    </div>
                  </div>
                  <div>
                    <div class="flex justify-between mb-1">
                      <span class="text-sm">Pro to Enterprise</span>
                      <span class="text-sm font-bold">8.3%</span>
                    </div>
                    <div class="w-full bg-base-200/50 rounded-full h-2">
                      <div class="bg-secondary h-full rounded-full" style="width: 8.3%"></div>
                    </div>
                  </div>
                  <div>
                    <div class="flex justify-between mb-1">
                      <span class="text-sm">Trial Conversion</span>
                      <span class="text-sm font-bold">45.2%</span>
                    </div>
                    <div class="w-full bg-base-200/50 rounded-full h-2">
                      <div class="bg-accent h-full rounded-full" style="width: 45.2%"></div>
                    </div>
                  </div>
                </div>
              </div>
            </BaseCard>

            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-lg font-bold mb-4">Geographic Distribution</h3>
                <div class="space-y-3">
                  <div v-for="country in topCountries" :key="country.name" class="flex justify-between items-center">
                    <span class="text-sm">{{ country.name }}</span>
                    <div class="flex items-center gap-2">
                      <div class="w-20 bg-base-200/50 rounded-full h-2">
                        <div class="bg-primary h-full rounded-full" :style="{ width: `${country.percentage}%` }"></div>
                      </div>
                      <span class="text-xs font-semibold w-10 text-right">{{ country.percentage }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </BaseCard>
          </div>
        </div>

        <!-- Monitoring Tab -->
        <div v-if="activeTab === 'monitoring'">
          <div class="grid lg:grid-cols-2 gap-6 mb-6">
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">System Resources (Real-time)</h3>
                <div class="h-64">
                  <Line :data="systemResourcesData" :options="realtimeChartOptions" />
                </div>
              </div>
            </BaseCard>

            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">Network Traffic</h3>
                <div class="h-64">
                  <Line :data="networkTrafficData" :options="realtimeChartOptions" />
                </div>
              </div>
            </BaseCard>
          </div>

          <div class="grid lg:grid-cols-4 gap-6 mb-6">
            <BaseCard variant="glass">
              <div class="p-4">
                <h4 class="text-sm opacity-60 mb-2">CPU Usage</h4>
                <div class="text-3xl font-bold text-warning mb-2">{{ systemMetrics.cpuUsage }}%</div>
                <div class="w-full bg-base-200/50 rounded-full h-2">
                  <div class="bg-warning h-full rounded-full transition-all" :style="{ width: `${systemMetrics.cpuUsage}%` }"></div>
                </div>
              </div>
            </BaseCard>

            <BaseCard variant="glass">
              <div class="p-4">
                <h4 class="text-sm opacity-60 mb-2">RAM Usage</h4>
                <div class="text-3xl font-bold text-secondary mb-2">{{ systemMetrics.ramUsage }}%</div>
                <div class="w-full bg-base-200/50 rounded-full h-2">
                  <div class="bg-secondary h-full rounded-full transition-all" :style="{ width: `${systemMetrics.ramUsage}%` }"></div>
                </div>
              </div>
            </BaseCard>

            <BaseCard variant="glass">
              <div class="p-4">
                <h4 class="text-sm opacity-60 mb-2">Disk Usage</h4>
                <div class="text-3xl font-bold text-primary mb-2">{{ systemMetrics.diskUsage }}%</div>
                <div class="w-full bg-base-200/50 rounded-full h-2">
                  <div class="bg-primary h-full rounded-full transition-all" :style="{ width: `${systemMetrics.diskUsage}%` }"></div>
                </div>
              </div>
            </BaseCard>

            <BaseCard variant="glass">
              <div class="p-4">
                <h4 class="text-sm opacity-60 mb-2">Network I/O</h4>
                <div class="text-3xl font-bold text-accent mb-2">{{ systemMetrics.networkIO }} MB/s</div>
                <div class="text-xs opacity-60">
                  ↑ {{ systemMetrics.networkIn }} ↓ {{ systemMetrics.networkOut }}
                </div>
              </div>
            </BaseCard>
          </div>

          <div class="grid lg:grid-cols-3 gap-6">
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-lg font-bold mb-4">Services Status</h3>
                <div class="space-y-3">
                  <div v-for="service in services" :key="service.name" class="flex items-center justify-between p-3 bg-base-200/50 rounded-lg">
                    <div class="flex items-center gap-3">
                      <div :class="['w-2 h-2 rounded-full', service.status === 'running' ? 'bg-success' : 'bg-error']"></div>
                      <span>{{ service.name }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-xs opacity-50">{{ service.uptime }}</span>
                      <button class="btn btn-xs btn-ghost">
                        <RefreshCwIcon class="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </BaseCard>

            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-lg font-bold mb-4">Database Status</h3>
                <div class="space-y-3">
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Total Queries</span>
                    <span class="font-bold">245.3K</span>
                  </div>
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Avg Response Time</span>
                    <span class="font-bold">12ms</span>
                  </div>
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Active Connections</span>
                    <span class="font-bold">42/100</span>
                  </div>
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Database Size</span>
                    <span class="font-bold">2.4 GB</span>
                  </div>
                </div>
              </div>
            </BaseCard>

            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-lg font-bold mb-4">Cache Status</h3>
                <div class="space-y-3">
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Hit Rate</span>
                    <span class="font-bold text-success">94.5%</span>
                  </div>
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Memory Used</span>
                    <span class="font-bold">156 MB</span>
                  </div>
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Total Keys</span>
                    <span class="font-bold">12.4K</span>
                  </div>
                  <BaseButton variant="error" size="sm" block @click="clearCache">
                    Clear Cache
                  </BaseButton>
                </div>
              </div>
            </BaseCard>
          </div>
        </div>

        <!-- Logs Tab -->
        <div v-if="activeTab === 'logs'">
          <BaseCard variant="glass">
            <div class="p-6">
              <div class="flex justify-between items-center mb-6">
                <h3 class="text-xl font-bold">System Logs</h3>
                <div class="flex gap-2">
                  <select v-model="logLevel" class="select select-bordered select-sm bg-base-200">
                    <option value="all">All Levels</option>
                    <option value="error">Error</option>
                    <option value="warning">Warning</option>
                    <option value="info">Info</option>
                    <option value="debug">Debug</option>
                  </select>
                  <select v-model="logSource" class="select select-bordered select-sm bg-base-200">
                    <option value="all">All Sources</option>
                    <option value="api">API</option>
                    <option value="database">Database</option>
                    <option value="auth">Authentication</option>
                    <option value="server">Server</option>
                  </select>
                  <BaseInput
                    v-model="logSearch"
                    placeholder="Search logs..."
                    :icon="SearchIcon"
                    class="w-48"
                  />
                  <BaseButton variant="ghost" size="sm" @click="exportLogs">
                    <DownloadIcon class="w-4 h-4 mr-1" />
                    Export
                  </BaseButton>
                  <BaseButton variant="ghost" size="sm" @click="clearLogs">
                    <TrashIcon class="w-4 h-4 mr-1" />
                    Clear
                  </BaseButton>
                </div>
              </div>

              <div class="space-y-2 max-h-[600px] overflow-y-auto">
                <div v-for="log in filteredLogs" :key="log.id" class="flex items-start gap-3 p-4 bg-base-200/50 rounded-lg font-mono text-xs">
                  <div :class="['w-2 h-2 rounded-full mt-1 flex-shrink-0', getLogColor(log.level)]"></div>
                  <div class="flex-1 min-w-0">
                    <div class="flex justify-between items-start mb-1">
                      <div class="flex items-center gap-2">
                        <span :class="['badge badge-xs', getLogBadgeClass(log.level)]">
                          {{ log.level.toUpperCase() }}
                        </span>
                        <span class="badge badge-xs badge-ghost">{{ log.source }}</span>
                        <span class="font-semibold">{{ log.action }}</span>
                      </div>
                      <span class="opacity-50">{{ log.time }}</span>
                    </div>
                    <p class="opacity-60 break-all">{{ log.message }}</p>
                    <div class="opacity-40 mt-1">
                      <span>User: {{ log.user }}</span> •
                      <span>IP: {{ log.ip }}</span> •
                      <span>ID: {{ log.id }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </BaseCard>
        </div>

        <!-- Security Tab -->
        <div v-if="activeTab === 'security'">
          <div class="grid lg:grid-cols-2 gap-6">
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">Security Settings</h3>
                <form class="space-y-4">
                  <label class="label cursor-pointer justify-start gap-3">
                    <input type="checkbox" v-model="securitySettings.require2FA" class="checkbox" />
                    <div>
                      <span class="label-text font-semibold">Require 2FA for all users</span>
                      <p class="text-xs opacity-50">Force two-factor authentication</p>
                    </div>
                  </label>

                  <label class="label cursor-pointer justify-start gap-3">
                    <input type="checkbox" v-model="securitySettings.emailVerification" class="checkbox" />
                    <div>
                      <span class="label-text font-semibold">Email verification required</span>
                      <p class="text-xs opacity-50">Users must verify email</p>
                    </div>
                  </label>

                  <label class="label cursor-pointer justify-start gap-3">
                    <input type="checkbox" v-model="securitySettings.ipWhitelist" class="checkbox" />
                    <div>
                      <span class="label-text font-semibold">IP Whitelist</span>
                      <p class="text-xs opacity-50">Restrict access by IP</p>
                    </div>
                  </label>

                  <label class="label cursor-pointer justify-start gap-3">
                    <input type="checkbox" v-model="securitySettings.ddosProtection" class="checkbox" />
                    <div>
                      <span class="label-text font-semibold">DDoS Protection</span>
                      <p class="text-xs opacity-50">Advanced DDoS mitigation</p>
                    </div>
                  </label>

                  <BaseInput
                    v-model="securitySettings.maxLoginAttempts"
                    label="Max Login Attempts"
                    type="number"
                    min="3"
                    max="10"
                  />

                  <BaseInput
                    v-model="securitySettings.sessionTimeout"
                    label="Session Timeout (minutes)"
                    type="number"
                    min="15"
                    max="1440"
                  />

                  <BaseInput
                    v-model="securitySettings.passwordMinLength"
                    label="Min Password Length"
                    type="number"
                    min="8"
                    max="32"
                  />

                  <BaseButton variant="gaming">
                    <SaveIcon class="w-4 h-4 mr-2" />
                    Save Security Settings
                  </BaseButton>
                </form>
              </div>
            </BaseCard>

            <div class="space-y-6">
              <BaseCard variant="glass">
                <div class="p-6">
                  <h3 class="text-lg font-bold mb-4">Recent Security Events</h3>
                  <div class="space-y-3 max-h-64 overflow-y-auto">
                    <div v-for="event in securityEvents" :key="event.id" class="flex items-start gap-3 p-3 bg-base-200/50 rounded-lg">
                      <div :class="['w-2 h-2 rounded-full mt-2', event.severity === 'high' ? 'bg-error' : event.severity === 'medium' ? 'bg-warning' : 'bg-info']"></div>
                      <div class="flex-1">
                        <div class="flex justify-between mb-1">
                          <span class="font-semibold text-sm">{{ event.type }}</span>
                          <span class="text-xs opacity-50">{{ event.time }}</span>
                        </div>
                        <p class="text-xs opacity-60">{{ event.description }}</p>
                        <p class="text-xs opacity-40 mt-1">IP: {{ event.ip }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </BaseCard>

              <BaseCard variant="glass">
                <div class="p-6">
                  <h3 class="text-lg font-bold mb-4">Failed Login Attempts (Last 24h)</h3>
                  <div class="space-y-3">
                    <div v-for="attempt in failedLogins" :key="attempt.id" class="flex justify-between items-center p-3 bg-base-200/50 rounded-lg">
                      <div>
                        <p class="font-semibold text-sm">{{ attempt.username }}</p>
                        <p class="text-xs opacity-50">{{ attempt.ip }}</p>
                      </div>
                      <div class="text-right">
                        <p class="text-sm font-bold text-error">{{ attempt.attempts }} attempts</p>
                        <p class="text-xs opacity-50">{{ attempt.lastAttempt }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </BaseCard>
            </div>
          </div>
        </div>

        <!-- Database Tab -->
        <div v-if="activeTab === 'database'">
          <div class="grid lg:grid-cols-2 gap-6 mb-6">
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">Database Overview</h3>
                <div class="space-y-3">
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Database Type</span>
                    <span class="font-bold">PostgreSQL 15.2</span>
                  </div>
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Total Size</span>
                    <span class="font-bold">2.4 GB</span>
                  </div>
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Tables</span>
                    <span class="font-bold">42</span>
                  </div>
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Total Records</span>
                    <span class="font-bold">1.2M</span>
                  </div>
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Connections</span>
                    <span class="font-bold">42/100</span>
                  </div>
                </div>
              </div>
            </BaseCard>

            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">Backup Management</h3>
                <div class="space-y-3 mb-4">
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Last Backup</span>
                    <span class="font-bold">2 hours ago</span>
                  </div>
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Backup Size</span>
                    <span class="font-bold">1.8 GB</span>
                  </div>
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Auto Backup</span>
                    <span class="badge badge-success">Enabled</span>
                  </div>
                </div>
                <div class="space-y-2">
                  <BaseButton variant="primary" block @click="createBackup">
                    <DatabaseIcon class="w-4 h-4 mr-2" />
                    Create Backup Now
                  </BaseButton>
                  <BaseButton variant="ghost" block>
                    <DownloadIcon class="w-4 h-4 mr-2" />
                    Download Latest Backup
                  </BaseButton>
                  <BaseButton variant="ghost" block>
                    <UploadIcon class="w-4 h-4 mr-2" />
                    Restore from Backup
                  </BaseButton>
                </div>
              </div>
            </BaseCard>
          </div>

          <BaseCard variant="glass">
            <div class="p-6">
              <h3 class="text-xl font-bold mb-4">Database Tables</h3>
              <div class="overflow-x-auto">
                <table class="table table-sm">
                  <thead>
                    <tr>
                      <th>Table Name</th>
                      <th>Records</th>
                      <th>Size</th>
                      <th>Last Updated</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="table in databaseTables" :key="table.name" class="hover">
                      <td class="font-mono">{{ table.name }}</td>
                      <td>{{ table.records.toLocaleString() }}</td>
                      <td>{{ table.size }}</td>
                      <td class="text-xs">{{ table.lastUpdated }}</td>
                      <td>
                        <div class="flex gap-1">
                          <button class="btn btn-xs btn-ghost">Optimize</button>
                          <button class="btn btn-xs btn-ghost">Export</button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </BaseCard>
        </div>

        <!-- API Tab -->
        <div v-if="activeTab === 'api'">
          <div class="grid lg:grid-cols-2 gap-6 mb-6">
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">API Keys</h3>
                <BaseButton variant="gaming" size="sm" class="mb-4" @click="generateApiKey">
                  <PlusCircleIcon class="w-4 h-4 mr-1" />
                  Generate New Key
                </BaseButton>
                <div class="space-y-3">
                  <div v-for="key in apiKeys" :key="key.id" class="p-3 bg-base-200/50 rounded-lg">
                    <div class="flex justify-between items-start mb-2">
                      <div>
                        <p class="font-semibold">{{ key.name }}</p>
                        <p class="text-xs opacity-50">Created {{ key.created }}</p>
                      </div>
                      <span :class="['badge badge-sm', key.active ? 'badge-success' : 'badge-error']">
                        {{ key.active ? 'Active' : 'Revoked' }}
                      </span>
                    </div>
                    <div class="flex gap-2">
                      <input type="text" :value="key.key" readonly class="input input-xs bg-base-300 flex-1 font-mono" />
                      <button class="btn btn-xs btn-ghost">
                        <CopyIcon class="w-3 h-3" />
                      </button>
                      <button class="btn btn-xs btn-error">
                        <TrashIcon class="w-3 h-3" />
                      </button>
                    </div>
                    <div class="mt-2 text-xs opacity-50">
                      Last used: {{ key.lastUsed }} • Requests: {{ key.requests }}
                    </div>
                  </div>
                </div>
              </div>
            </BaseCard>

            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">API Usage (Last 24h)</h3>
                <div class="space-y-3 mb-4">
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Total Requests</span>
                    <span class="font-bold">45.2K</span>
                  </div>
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Success Rate</span>
                    <span class="font-bold text-success">99.7%</span>
                  </div>
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Avg Response Time</span>
                    <span class="font-bold">142ms</span>
                  </div>
                  <div class="flex justify-between p-3 bg-base-200/50 rounded-lg">
                    <span>Rate Limit Hits</span>
                    <span class="font-bold text-warning">23</span>
                  </div>
                </div>

                <h4 class="font-bold mb-3">Top Endpoints</h4>
                <div class="space-y-2">
                  <div v-for="endpoint in topEndpoints" :key="endpoint.path" class="flex justify-between items-center">
                    <span class="text-sm font-mono">{{ endpoint.path }}</span>
                    <span class="text-sm font-bold">{{ endpoint.requests }}</span>
                  </div>
                </div>
              </div>
            </BaseCard>
          </div>

          <BaseCard variant="glass">
            <div class="p-6">
              <h3 class="text-xl font-bold mb-4">Rate Limiting Configuration</h3>
              <div class="grid md:grid-cols-2 gap-4">
                <BaseInput
                  v-model="rateLimitSettings.requestsPerMinute"
                  label="Requests per Minute"
                  type="number"
                />
                <BaseInput
                  v-model="rateLimitSettings.requestsPerHour"
                  label="Requests per Hour"
                  type="number"
                />
                <BaseInput
                  v-model="rateLimitSettings.requestsPerDay"
                  label="Requests per Day"
                  type="number"
                />
                <BaseInput
                  v-model="rateLimitSettings.burstSize"
                  label="Burst Size"
                  type="number"
                />
              </div>
              <div class="mt-4">
                <BaseButton variant="gaming">
                  <SaveIcon class="w-4 h-4 mr-2" />
                  Update Rate Limits
                </BaseButton>
              </div>
            </div>
          </BaseCard>
        </div>

        <!-- Notifications Tab -->
        <div v-if="activeTab === 'notifications'">
          <div class="grid lg:grid-cols-2 gap-6">
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">Email Notifications</h3>
                <form class="space-y-4">
                  <BaseInput
                    v-model="notificationSettings.smtpHost"
                    label="SMTP Host"
                    placeholder="smtp.example.com"
                  />
                  <BaseInput
                    v-model="notificationSettings.smtpPort"
                    label="SMTP Port"
                    type="number"
                  />
                  <BaseInput
                    v-model="notificationSettings.smtpUser"
                    label="SMTP Username"
                  />
                  <BaseInput
                    v-model="notificationSettings.smtpPassword"
                    label="SMTP Password"
                    type="password"
                  />
                  <BaseInput
                    v-model="notificationSettings.fromEmail"
                    label="From Email"
                    type="email"
                  />

                  <label class="label cursor-pointer justify-start gap-3">
                    <input type="checkbox" v-model="notificationSettings.emailEnabled" class="checkbox" />
                    <span class="label-text">Enable Email Notifications</span>
                  </label>

                  <BaseButton variant="ghost" size="sm" @click="testEmail">
                    <MailIcon class="w-4 h-4 mr-2" />
                    Send Test Email
                  </BaseButton>

                  <BaseButton variant="gaming">
                    <SaveIcon class="w-4 h-4 mr-2" />
                    Save Email Settings
                  </BaseButton>
                </form>
              </div>
            </BaseCard>

            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">Notification Triggers</h3>
                <div class="space-y-3">
                  <label class="label cursor-pointer justify-start gap-3 p-3 bg-base-200/50 rounded-lg">
                    <input type="checkbox" v-model="notificationTriggers.newUser" class="checkbox" />
                    <div>
                      <span class="label-text font-semibold">New User Registration</span>
                      <p class="text-xs opacity-50">Notify when new user registers</p>
                    </div>
                  </label>

                  <label class="label cursor-pointer justify-start gap-3 p-3 bg-base-200/50 rounded-lg">
                    <input type="checkbox" v-model="notificationTriggers.serverDown" class="checkbox" />
                    <div>
                      <span class="label-text font-semibold">Server Down</span>
                      <p class="text-xs opacity-50">Alert when server goes down</p>
                    </div>
                  </label>

                  <label class="label cursor-pointer justify-start gap-3 p-3 bg-base-200/50 rounded-lg">
                    <input type="checkbox" v-model="notificationTriggers.highCpu" class="checkbox" />
                    <div>
                      <span class="label-text font-semibold">High CPU Usage</span>
                      <p class="text-xs opacity-50">Alert when CPU > 80%</p>
                    </div>
                  </label>

                  <label class="label cursor-pointer justify-start gap-3 p-3 bg-base-200/50 rounded-lg">
                    <input type="checkbox" v-model="notificationTriggers.failedPayment" class="checkbox" />
                    <div>
                      <span class="label-text font-semibold">Failed Payment</span>
                      <p class="text-xs opacity-50">Notify on payment failures</p>
                    </div>
                  </label>

                  <label class="label cursor-pointer justify-start gap-3 p-3 bg-base-200/50 rounded-lg">
                    <input type="checkbox" v-model="notificationTriggers.securityAlert" class="checkbox" />
                    <div>
                      <span class="label-text font-semibold">Security Alerts</span>
                      <p class="text-xs opacity-50">Critical security events</p>
                    </div>
                  </label>

                  <BaseButton variant="gaming" block>
                    <SaveIcon class="w-4 h-4 mr-2" />
                    Save Notification Settings
                  </BaseButton>
                </div>
              </div>
            </BaseCard>
          </div>
        </div>

        <!-- Settings Tab -->
        <div v-if="activeTab === 'settings'">
          <div class="grid lg:grid-cols-2 gap-6">
            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">General Settings</h3>
                <form class="space-y-4">
                  <BaseInput
                    v-model="settings.siteName"
                    label="Site Name"
                    placeholder="AGTR Merkezi"
                  />

                  <BaseInput
                    v-model="settings.siteUrl"
                    label="Site URL"
                    placeholder="https://example.com"
                  />

                  <div class="form-control">
                    <label class="label">
                      <span class="label-text">Site Description</span>
                    </label>
                    <textarea
                      v-model="settings.siteDescription"
                      class="textarea textarea-bordered bg-base-200"
                      rows="3"
                    ></textarea>
                  </div>

                  <BaseInput
                    v-model="settings.supportEmail"
                    label="Support Email"
                    type="email"
                  />

                  <label class="label cursor-pointer justify-start gap-3">
                    <input type="checkbox" v-model="settings.maintenanceMode" class="checkbox" />
                    <div>
                      <span class="label-text font-semibold">Maintenance Mode</span>
                      <p class="text-xs opacity-50">Put site in maintenance</p>
                    </div>
                  </label>

                  <label class="label cursor-pointer justify-start gap-3">
                    <input type="checkbox" v-model="settings.allowRegistration" class="checkbox" />
                    <div>
                      <span class="label-text font-semibold">Allow Registration</span>
                      <p class="text-xs opacity-50">Enable new user registration</p>
                    </div>
                  </label>

                  <BaseButton variant="gaming">
                    <SaveIcon class="w-4 h-4 mr-2" />
                    Save General Settings
                  </BaseButton>
                </form>
              </div>
            </BaseCard>

            <BaseCard variant="glass">
              <div class="p-6">
                <h3 class="text-xl font-bold mb-4">Advanced Settings</h3>
                <form class="space-y-4">
                  <BaseInput
                    v-model="settings.maxUploadSize"
                    label="Max Upload Size (MB)"
                    type="number"
                  />

                  <BaseInput
                    v-model="settings.cacheTimeout"
                    label="Cache Timeout (seconds)"
                    type="number"
                  />

                  <BaseInput
                    v-model="settings.logRetention"
                    label="Log Retention (days)"
                    type="number"
                  />

                  <label class="label cursor-pointer justify-start gap-3">
                    <input type="checkbox" v-model="settings.enableCdn" class="checkbox" />
                    <span class="label-text">Enable CDN</span>
                  </label>

                  <label class="label cursor-pointer justify-start gap-3">
                    <input type="checkbox" v-model="settings.enableCompression" class="checkbox" />
                    <span class="label-text">Enable Compression</span>
                  </label>

                  <label class="label cursor-pointer justify-start gap-3">
                    <input type="checkbox" v-model="settings.enableAnalytics" class="checkbox" />
                    <span class="label-text">Enable Analytics</span>
                  </label>

                  <BaseButton variant="gaming">
                    <SaveIcon class="w-4 h-4 mr-2" />
                    Save Advanced Settings
                  </BaseButton>
                </form>
              </div>
            </BaseCard>
          </div>
        </div>
      </div>
    </div>

    <!-- Maintenance Mode Modal -->
    <div v-if="showMaintenanceModal" class="modal modal-open">
      <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">Enable Maintenance Mode</h3>
        <p class="mb-4">Are you sure you want to put the site in maintenance mode? All users except admins will be unable to access the site.</p>
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text">Maintenance Message</span>
          </label>
          <textarea
            v-model="maintenanceMessage"
            class="textarea textarea-bordered bg-base-200"
            placeholder="We're performing maintenance. We'll be back soon!"
          ></textarea>
        </div>
        <div class="flex gap-2">
          <BaseButton variant="error" @click="enableMaintenance">
            Enable Maintenance
          </BaseButton>
          <BaseButton variant="ghost" @click="showMaintenanceModal = false">
            Cancel
          </BaseButton>
        </div>
      </div>
      <div class="modal-backdrop" @click="showMaintenanceModal = false"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Line, Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend } from 'chart.js'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import {
  LayoutDashboardIcon,
  UsersIcon,
  ServerIcon,
  BarChartIcon,
  MonitorIcon,
  ScrollTextIcon,
  ShieldIcon,
  DatabaseIcon,
  CodeIcon,
  BellIcon,
  SettingsIcon,
  DollarSignIcon,
  ActivityIcon,
  CpuIcon,
  TrendingUpIcon,
  RefreshCwIcon,
  AlertTriangleIcon,
  DownloadIcon,
  SearchIcon,
  PlusCircleIcon,
  EditIcon,
  TrashIcon,
  EyeIcon,
  StopCircleIcon,
  PlayCircleIcon,
  MoreVerticalIcon,
  KeyIcon,
  MailIcon,
  UserPlusIcon,
  SaveIcon,
  CopyIcon,
  UploadIcon
} from 'lucide-vue-next'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend)

const activeTab = ref('dashboard')
const userSearch = ref('')
const logLevel = ref('all')
const logSource = ref('all')
const logSearch = ref('')
const showMaintenanceModal = ref(false)
const maintenanceMessage = ref('')

const stats = reactive({
  totalUsers: 3456,
  newUsersToday: 23,
  totalServers: 1248,
  activeServers: 1132,
  revenue: 12500
})

const systemMetrics = reactive({
  cpuUsage: 45,
  ramUsage: 62,
  diskUsage: 38,
  networkIO: 12.5,
  networkIn: '8.2 MB/s',
  networkOut: '4.3 MB/s',
  health: 98
})

const users = ref([
  {
    id: 1,
    username: 'Player123',
    email: 'player123@example.com',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=1',
    role: 'admin',
    serverCount: 5,
    isActive: true,
    twoFactorEnabled: true,
    lastLogin: '2024-01-17 14:30',
    createdAt: '2023-01-15'
  },
  {
    id: 2,
    username: 'ProGamer',
    email: 'progamer@example.com',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=2',
    role: 'moderatör',
    serverCount: 3,
    isActive: true,
    twoFactorEnabled: true,
    lastLogin: '2024-01-17 12:15',
    createdAt: '2023-02-20'
  },
  {
    id: 3,
    username: 'NewbieCS',
    email: 'newbie@example.com',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=3',
    role: 'user',
    serverCount: 1,
    isActive: true,
    twoFactorEnabled: false,
    lastLogin: '2024-01-17 10:45',
    createdAt: '2023-03-10'
  },
  {
    id: 4,
    username: 'BannedUser',
    email: 'banned@example.com',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=4',
    role: 'user',
    serverCount: 0,
    isActive: false,
    twoFactorEnabled: false,
    lastLogin: '2024-01-10 08:20',
    createdAt: '2023-01-05'
  }
])

const servers = ref([
  {
    id: 1,
    name: 'AGTR Public #1',
    owner: 'Player123',
    ip: '192.168.1.100',
    port: 27015,
    map: 'de_dust2',
    players: 24,
    maxPlayers: 32,
    cpu: 45,
    ram: 62,
    status: 'active',
    uptime: '5d 12h'
  },
  {
    id: 2,
    name: 'DM Arena',
    owner: 'ProGamer',
    ip: '192.168.1.101',
    port: 27016,
    map: 'de_inferno',
    players: 0,
    maxPlayers: 24,
    cpu: 12,
    ram: 28,
    status: 'inactive',
    uptime: '0m'
  }
])

const logs = ref([
  { id: 1, level: 'error', source: 'api', action: 'Login Failed', message: 'Multiple failed login attempts detected from IP 192.168.1.50', user: 'Unknown', ip: '192.168.1.50', time: '5 min ago' },
  { id: 2, level: 'warning', source: 'server', action: 'High CPU Usage', message: 'Server CPU usage exceeded 80% threshold', user: 'System', ip: '127.0.0.1', time: '15 min ago' },
  { id: 3, level: 'info', source: 'auth', action: 'User Registration', message: 'New user registered successfully', user: 'NewbieCS', ip: '192.168.1.75', time: '30 min ago' },
  { id: 4, level: 'info', source: 'server', action: 'Server Created', message: 'New server instance created and started', user: 'Player123', ip: '192.168.1.25', time: '1 hour ago' },
  { id: 5, level: 'debug', source: 'database', action: 'Query Execution', message: 'Slow query detected: SELECT * FROM users WHERE...', user: 'System', ip: '127.0.0.1', time: '2 hours ago' }
])

const filteredLogs = computed(() => {
  let filtered = logs.value

  if (logLevel.value !== 'all') {
    filtered = filtered.filter(log => log.level === logLevel.value)
  }

  if (logSource.value !== 'all') {
    filtered = filtered.filter(log => log.source === logSource.value)
  }

  if (logSearch.value) {
    const query = logSearch.value.toLowerCase()
    filtered = filtered.filter(log =>
      log.message.toLowerCase().includes(query) ||
      log.action.toLowerCase().includes(query)
    )
  }

  return filtered
})

const recentActivity = ref([
  { id: 1, type: 'primary', message: 'New user registered: NewbieCS', time: '2 min ago' },
  { id: 2, type: 'success', message: 'Server started: AGTR Public #1', time: '5 min ago' },
  { id: 3, type: 'warning', message: 'High CPU usage detected on server #4', time: '12 min ago' },
  { id: 4, type: 'error', message: 'Failed login attempt from 192.168.1.50', time: '18 min ago' }
])

const topUsers = ref([
  { id: 1, username: 'Player123', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=1', servers: 5, activity: '98%' },
  { id: 2, username: 'ProGamer', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=2', servers: 3, activity: '87%' },
  { id: 3, username: 'AdminUser', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=3', servers: 4, activity: '76%' }
])

const services = ref([
  { name: 'API Server', status: 'running', uptime: '15d 8h' },
  { name: 'Database', status: 'running', uptime: '30d 12h' },
  { name: 'Redis Cache', status: 'running', uptime: '25d 6h' },
  { name: 'Background Workers', status: 'running', uptime: '15d 8h' }
])

const securityEvents = ref([
  { id: 1, type: 'Failed Login', severity: 'high', description: '5 failed attempts from 192.168.1.50', ip: '192.168.1.50', time: '10 min ago' },
  { id: 2, type: 'Suspicious Activity', severity: 'medium', description: 'Unusual API usage pattern detected', ip: '192.168.1.75', time: '1 hour ago' },
  { id: 3, type: 'Rate Limit Hit', severity: 'low', description: 'API rate limit exceeded', ip: '192.168.1.100', time: '2 hours ago' }
])

const failedLogins = ref([
  { id: 1, username: 'admin', ip: '192.168.1.50', attempts: 5, lastAttempt: '10 min ago' },
  { id: 2, username: 'root', ip: '192.168.1.75', attempts: 3, lastAttempt: '1 hour ago' }
])

const databaseTables = ref([
  { name: 'users', records: 3456, size: '1.2 MB', lastUpdated: '5 min ago' },
  { name: 'servers', records: 1248, size: '856 KB', lastUpdated: '10 min ago' },
  { name: 'logs', records: 245320, size: '125 MB', lastUpdated: '1 min ago' },
  { name: 'sessions', records: 1542, size: '456 KB', lastUpdated: '3 min ago' }
])

const apiKeys = ref([
  { id: 1, name: 'Production API', key: 'sk_live_abc123...', active: true, created: '2 months ago', lastUsed: '5 min ago', requests: 45230 },
  { id: 2, name: 'Development API', key: 'sk_test_xyz789...', active: true, created: '1 month ago', lastUsed: '2 hours ago', requests: 8542 }
])

const topEndpoints = ref([
  { path: '/api/servers/list', requests: '12.4K' },
  { path: '/api/users/profile', requests: '8.2K' },
  { path: '/api/auth/login', requests: '6.8K' },
  { path: '/api/servers/status', requests: '5.3K' }
])

const topRevenueSources = ref([
  { name: 'Pro Plans', amount: '8,500' },
  { name: 'Enterprise Plans', amount: '3,200' },
  { name: 'Add-ons', amount: '800' }
])

const topCountries = ref([
  { name: 'United States', percentage: 45 },
  { name: 'Germany', percentage: 22 },
  { name: 'United Kingdom', percentage: 15 },
  { name: 'Turkey', percentage: 10 },
  { name: 'Others', percentage: 8 }
])

const settings = reactive({
  siteName: 'AGTR Merkezi',
  siteUrl: 'https://agtrmerkezi.com',
  siteDescription: 'Counter-Strike 1.6 sunucu yönetim platformu',
  supportEmail: 'support@agtrmerkezi.com',
  maintenanceMode: false,
  allowRegistration: true,
  maxUploadSize: 10,
  cacheTimeout: 3600,
  logRetention: 30,
  enableCdn: true,
  enableCompression: true,
  enableAnalytics: true
})

const securitySettings = reactive({
  require2FA: true,
  emailVerification: true,
  ipWhitelist: false,
  ddosProtection: true,
  maxLoginAttempts: 5,
  sessionTimeout: 720,
  passwordMinLength: 8
})

const notificationSettings = reactive({
  smtpHost: 'smtp.example.com',
  smtpPort: 587,
  smtpUser: 'noreply@agtrmerkezi.com',
  smtpPassword: '',
  fromEmail: 'noreply@agtrmerkezi.com',
  emailEnabled: true
})

const notificationTriggers = reactive({
  newUser: true,
  serverDown: true,
  highCpu: true,
  failedPayment: true,
  securityAlert: true
})

const rateLimitSettings = reactive({
  requestsPerMinute: 60,
  requestsPerHour: 1000,
  requestsPerDay: 10000,
  burstSize: 100
})

const activityChartData = computed(() => ({
  labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
  datasets: [{
    label: 'Active Users',
    data: [120, 80, 150, 280, 420, 380, 200],
    borderColor: '#6366f1',
    backgroundColor: 'rgba(99, 102, 241, 0.1)',
    fill: true,
    tension: 0.4
  }]
}))

const userGrowthData = computed(() => ({
  labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
  datasets: [{
    label: 'New Users',
    data: [145, 189, 234, 287],
    borderColor: '#8b5cf6',
    backgroundColor: 'rgba(139, 92, 246, 0.1)',
    fill: true,
    tension: 0.4
  }]
}))

const revenueChartData = computed(() => ({
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [{
    label: 'Revenue ($)',
    data: [8500, 9200, 10100, 11500, 12300, 12500],
    borderColor: '#ec4899',
    backgroundColor: 'rgba(236, 72, 153, 0.1)',
    fill: true,
    tension: 0.4
  }]
}))

const serverDistributionData = computed(() => ({
  labels: ['Free', 'Pro', 'Enterprise'],
  datasets: [{
    label: 'Servers',
    data: [456, 632, 160],
    backgroundColor: ['#6366f1', '#8b5cf6', '#ec4899']
  }]
}))

const systemResourcesData = computed(() => ({
  labels: ['1m', '2m', '3m', '4m', '5m'],
  datasets: [
    {
      label: 'CPU %',
      data: [42, 45, 48, 43, 45],
      borderColor: '#f59e0b',
      tension: 0.4
    },
    {
      label: 'RAM %',
      data: [58, 60, 62, 61, 62],
      borderColor: '#8b5cf6',
      tension: 0.4
    }
  ]
}))

const networkTrafficData = computed(() => ({
  labels: ['1m', '2m', '3m', '4m', '5m'],
  datasets: [
    {
      label: 'Inbound (MB/s)',
      data: [8.2, 7.8, 8.5, 8.0, 8.2],
      borderColor: '#10b981',
      tension: 0.4
    },
    {
      label: 'Outbound (MB/s)',
      data: [4.3, 4.1, 4.5, 4.2, 4.3],
      borderColor: '#ef4444',
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

const realtimeChartOptions = {
  ...chartOptions,
  animation: {
    duration: 750
  }
}

const getLogColor = (level) => {
  switch (level) {
    case 'error': return 'bg-error'
    case 'warning': return 'bg-warning'
    case 'info': return 'bg-info'
    case 'debug': return 'bg-base-200'
    default: return 'bg-primary'
  }
}

const getLogBadgeClass = (level) => {
  switch (level) {
    case 'error': return 'badge-error'
    case 'warning': return 'badge-warning'
    case 'info': return 'badge-info'
    case 'debug': return 'badge-ghost'
    default: return 'badge-primary'
  }
}

const refreshData = () => {
  // Refresh data
}

const createBackup = () => {
  // Create backup
}

const clearCache = () => {
  // Clear cache
}

const restartServices = () => {
  // Restart services
}

const exportLogs = () => {
  // Export logs
}

const clearLogs = () => {
  // Clear logs
}

const testEmail = () => {
  // Send test email
}

const generateApiKey = () => {
  // Generate API key
}

const enableMaintenance = () => {
  settings.maintenanceMode = true
  showMaintenanceModal.value = false
  // Maintenance mode enabled
}
</script>

<style scoped>
.neon-text {
  background: linear-gradient(to right, #f97316, #8b5cf6, #06b6d4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
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
</style>
