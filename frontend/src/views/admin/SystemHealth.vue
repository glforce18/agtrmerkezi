<template>
  <div class="system-health-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <ActivityIcon class="title-icon" />
          <div>
            <h1>Sistem Saglik Monitoru</h1>
            <p>Tüm bilesenlerin durumu ve otomatik duzeltme</p>
          </div>
        </div>
        <div class="header-actions">
          <button class="btn-refresh" @click="fetchHealth" :disabled="loading">
            <RefreshCwIcon class="w-4 h-4" :class="{ 'spin': loading }" />
            Yenile
          </button>
          <button
            class="btn-fix-all"
            @click="runAllFixes"
            :disabled="fixableCount === 0 || fixing"
          >
            <WrenchIcon class="w-4 h-4" />
            Tüm Sorunlari Duzelt ({{ fixableCount }})
          </button>
        </div>
      </div>
    </div>

    <!-- Overall Status Banner -->
    <div
      class="status-banner"
      :class="overallStatus"
    >
      <div class="status-icon">
        <CheckCircleIcon v-if="overallStatus === 'healthy'" class="w-8 h-8" />
        <AlertTriangleIcon v-else-if="overallStatus === 'warning'" class="w-8 h-8" />
        <XCircleIcon v-else class="w-8 h-8" />
      </div>
      <div class="status-content">
        <h2>
          {{ overallStatus === 'healthy' ? 'Sistem Saglikli' :
             overallStatus === 'warning' ? 'Dikkat Gerektiren Sorunlar Var' :
             'Kritik Sorunlar Mevcut' }}
        </h2>
        <p v-if="lastCheck">Son kontrol: {{ formatDate(lastCheck) }}</p>
      </div>
      <div class="status-metrics">
        <div class="metric healthy">
          <span class="value">{{ metrics.healthy || 0 }}</span>
          <span class="label">Saglikli</span>
        </div>
        <div class="metric warning">
          <span class="value">{{ metrics.warning || 0 }}</span>
          <span class="label">Uyari</span>
        </div>
        <div class="metric critical">
          <span class="value">{{ metrics.critical || 0 }}</span>
          <span class="label">Kritik</span>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- Components Status -->
      <section class="section components-section">
        <h3 class="section-title">
          <ServerIcon class="w-5 h-5" />
          Bilesen Durumu
        </h3>

        <div class="components-grid">
          <div
            v-for="(component, name) in components"
            :key="name"
            class="component-card"
            :class="component.status"
          >
            <div class="component-header">
              <div class="component-icon">
                <component :is="getComponentIcon(name)" class="w-5 h-5" />
              </div>
              <div class="component-info">
                <h4>{{ formatComponentName(name) }}</h4>
                <span class="status-badge" :class="component.status">
                  {{ getStatusText(component.status) }}
                </span>
              </div>
              <button
                v-if="component.auto_fixable && component.status !== 'healthy'"
                class="fix-btn"
                @click="runFix(component.fix_action)"
                :disabled="fixing"
              >
                <WrenchIcon class="w-4 h-4" />
              </button>
            </div>

            <p class="component-message">{{ component.message }}</p>

            <div v-if="component.details" class="component-details">
              <div v-for="(value, key) in component.details" :key="key" class="detail-item">
                <span class="detail-key">{{ formatDetailKey(key) }}:</span>
                <span class="detail-value">{{ formatDetailValue(value) }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Dependency Graph -->
      <section class="section dependency-section">
        <h3 class="section-title">
          <GitBranchIcon class="w-5 h-5" />
          Bagimllik Haritasi
        </h3>

        <div class="dependency-graph">
          <div
            v-for="(deps, component) in dependencies"
            :key="component"
            class="dep-row"
          >
            <div class="dep-source">
              <component :is="getComponentIcon(component)" class="w-4 h-4" />
              {{ formatComponentName(component) }}
            </div>
            <div class="dep-arrow">
              <ArrowRightIcon class="w-4 h-4" />
            </div>
            <div class="dep-targets">
              <span
                v-for="dep in deps"
                :key="dep"
                class="dep-tag"
                :class="getComponentStatus(dep)"
              >
                {{ formatComponentName(dep) }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Pages Status -->
      <section class="section pages-section">
        <h3 class="section-title">
          <LayoutIcon class="w-5 h-5" />
          Sayfa Durumu
        </h3>

        <div class="pages-table">
          <div class="table-header">
            <span>Sayfa</span>
            <span>Path</span>
            <span>Bilesenler</span>
            <span>Bagimliliklar</span>
            <span>Durum</span>
          </div>
          <div
            v-for="(page, name) in pages"
            :key="name"
            class="table-row"
          >
            <span class="page-name">{{ formatPageName(name) }}</span>
            <span class="page-path">{{ page.path }}</span>
            <span class="page-components">
              <span v-for="comp in page.components?.slice(0, 2)" :key="comp" class="comp-tag">
                {{ comp }}
              </span>
              <span v-if="page.components?.length > 2" class="comp-more">
                +{{ page.components.length - 2 }}
              </span>
            </span>
            <span class="page-deps">
              <span
                v-for="dep in page.dependencies"
                :key="dep"
                class="dep-mini-tag"
                :class="getComponentStatus(dep)"
              >
                {{ dep }}
              </span>
            </span>
            <span class="page-status">
              <CheckCircleIcon
                v-if="isPageHealthy(page)"
                class="w-4 h-4 text-green"
              />
              <AlertTriangleIcon
                v-else
                class="w-4 h-4 text-yellow"
              />
            </span>
          </div>
        </div>
      </section>

      <!-- Fix History -->
      <section class="section history-section">
        <h3 class="section-title">
          <ClockIcon class="w-5 h-5" />
          Son Duzeltmeler
        </h3>

        <div v-if="fixHistory.length === 0" class="empty-history">
          <CheckCircleIcon class="w-8 h-8" />
          <p>Henuz duzeltme yapilmadi</p>
        </div>

        <div v-else class="fix-history-list">
          <div
            v-for="(fix, index) in fixHistory"
            :key="index"
            class="fix-item"
            :class="{ success: fix.success, failed: !fix.success }"
          >
            <div class="fix-icon">
              <CheckIcon v-if="fix.success" class="w-4 h-4" />
              <XIcon v-else class="w-4 h-4" />
            </div>
            <div class="fix-content">
              <span class="fix-component">{{ fix.component }}</span>
              <span class="fix-action">{{ fix.action }}</span>
            </div>
            <span class="fix-message">{{ fix.message }}</span>
            <span class="fix-time">{{ fix.time }}</span>
          </div>
        </div>
      </section>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading || fixing" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>{{ fixing ? 'Duzeltme yapiliyor...' : 'Kontrol ediliyor...' }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  ActivityIcon,
  RefreshCwIcon,
  WrenchIcon,
  CheckCircleIcon,
  AlertTriangleIcon,
  XCircleIcon,
  ServerIcon,
  DatabaseIcon,
  HardDriveIcon,
  FileTextIcon,
  ShieldIcon,
  CodeIcon,
  GlobeIcon,
  GitBranchIcon,
  ArrowRightIcon,
  LayoutIcon,
  ClockIcon,
  CheckIcon,
  XIcon,
  ZapIcon,
  BoxIcon
} from 'lucide-vue-next'
import api from '@/services/api'

const loading = ref(false)
const fixing = ref(false)
const overallStatus = ref('healthy')
const lastCheck = ref(null)
const components = ref({})
const dependencies = ref({})
const pages = ref({})
const metrics = ref({})
const fixHistory = ref([])

let refreshInterval = null

const fixableCount = computed(() => {
  return Object.values(components.value).filter(
    c => c.auto_fixable && c.status !== 'healthy'
  ).length
})

const fetchHealth = async () => {
  loading.value = true
  try {
    let healthData, pagesData

    try {
      // Try authenticated endpoint first
      [healthData, pagesData] = await Promise.all([
        api.get('/admin/health/status'),
        api.get('/admin/health/pages')
      ])
    } catch (authError) {
      console.warn('Auth endpoint failed, trying test endpoint:', authError)
      // Fall back to test endpoint (no auth required)
      healthData = await api.get('/admin/health/test-status')
      pagesData = { success: true, pages: {} }
    }

    // API returns data directly (no .data wrapper)
    if (healthData?.success) {
      overallStatus.value = healthData.overall_status || 'unknown'
      components.value = healthData.components || {}
      dependencies.value = healthData.dependencies || {}
      metrics.value = healthData.metrics || { healthy: 0, warning: 0, critical: 0 }
      lastCheck.value = healthData.timestamp
    } else if (healthData?.overall_status) {
      // Direct access if no success wrapper
      overallStatus.value = healthData.overall_status
      components.value = healthData.components || {}
      dependencies.value = healthData.dependencies || {}
      metrics.value = healthData.metrics || {}
      lastCheck.value = healthData.timestamp
    }

    if (pagesData?.success) {
      pages.value = pagesData.pages || {}
    } else if (pagesData?.pages) {
      pages.value = pagesData.pages
    }
  } catch (error) {
    console.error('Health check failed:', error)
    // Set error state
    overallStatus.value = 'critical'
    components.value = {
      api_error: {
        status: 'critical',
        message: `API Hatasi: ${error.message || 'Bilinmeyen hata'}`,
        auto_fixable: false
      }
    }
    metrics.value = { healthy: 0, warning: 0, critical: 1 }
  } finally {
    loading.value = false
  }
}

const runFix = async (action) => {
  if (!action) return
  fixing.value = true

  try {
    const data = await api.post(`/admin/health/fix/${action}`)

    if (data?.result) {
      const result = data.result
      fixHistory.value.unshift({
        ...result,
        time: new Date().toLocaleTimeString('tr-TR')
      })

      // Keep only last 10 items
      if (fixHistory.value.length > 10) {
        fixHistory.value = fixHistory.value.slice(0, 10)
      }
    }

    // Refresh health status
    await fetchHealth()
  } catch (error) {
    console.error('Fix failed:', error)
    fixHistory.value.unshift({
      success: false,
      component: 'system',
      action: action,
      message: 'Duzeltme başarısız: ' + (error.message || 'Bilinmeyen hata'),
      time: new Date().toLocaleTimeString('tr-TR')
    })
  } finally {
    fixing.value = false
  }
}

const runAllFixes = async () => {
  fixing.value = true

  try {
    const data = await api.post('/admin/health/fix-all')

    if (data?.results) {
      for (const result of data.results) {
        fixHistory.value.unshift({
          ...result,
          time: new Date().toLocaleTimeString('tr-TR')
        })
      }

      // Keep only last 10 items
      if (fixHistory.value.length > 10) {
        fixHistory.value = fixHistory.value.slice(0, 10)
      }
    }

    // Refresh health status
    await fetchHealth()
  } catch (error) {
    console.error('Fix all failed:', error)
  } finally {
    fixing.value = false
  }
}

const getComponentIcon = (name) => {
  const icons = {
    database: DatabaseIcon,
    redis: ZapIcon,
    static_files: HardDriveIcon,
    api_endpoints: GlobeIcon,
    disk_space: HardDriveIcon,
    frontend_build: CodeIcon,
    logs: FileTextIcon,
    security: ShieldIcon,
    frontend: CodeIcon,
    api: GlobeIcon,
    forum: BoxIcon,
    jackpot: ZapIcon,
    auth: ShieldIcon,
    admin: ServerIcon,
    websocket: ActivityIcon
  }
  return icons[name] || ServerIcon
}

const formatComponentName = (name) => {
  const names = {
    database: 'Veritabani',
    redis: 'Redis Cache',
    static_files: 'Statik Dosyalar',
    api_endpoints: 'API Endpointleri',
    disk_space: 'Disk Alani',
    frontend_build: 'Frontend Build',
    logs: 'Log Dosyalari',
    security: 'Güvenlik',
    frontend: 'Frontend',
    api: 'API',
    forum: 'Forum',
    jackpot: 'Jackpot',
    auth: 'Kimlik Doğrulama',
    admin: 'Admin Panel',
    websocket: 'WebSocket'
  }
  return names[name] || name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

const formatPageName = (name) => {
  return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

const getStatusText = (status) => {
  const texts = {
    healthy: 'Saglikli',
    warning: 'Uyari',
    critical: 'Kritik'
  }
  return texts[status] || status
}

const formatDetailKey = (key) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

const formatDetailValue = (value) => {
  if (Array.isArray(value)) {
    return value.length > 0 ? value.join(', ') : '-'
  }
  if (typeof value === 'boolean') {
    return value ? 'Evet' : 'Hayir'
  }
  if (typeof value === 'number') {
    return value.toLocaleString('tr-TR')
  }
  return value || '-'
}

const formatDate = (isoString) => {
  if (!isoString) return ''
  return new Date(isoString).toLocaleString('tr-TR')
}

const getComponentStatus = (name) => {
  const component = components.value[name]
  return component?.status || 'unknown'
}

const isPageHealthy = (page) => {
  if (!page.dependencies) return true
  return page.dependencies.every(dep => {
    const comp = components.value[dep]
    return !comp || comp.status === 'healthy'
  })
}

onMounted(() => {
  fetchHealth()

  // Auto refresh every 30 seconds
  refreshInterval = setInterval(fetchHealth, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.system-health-page {
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
}

/* Header */
.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-icon {
  width: 48px;
  height: 48px;
  padding: 12px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 12px;
  color: white;
}

.title-section h1 {
  font-size: 24px;
  font-weight: 700;
  color: #f8fafc;
  margin: 0;
}

.title-section p {
  font-size: 14px;
  color: #64748b;
  margin: 4px 0 0 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-refresh,
.btn-fix-all {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-refresh {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: #f8fafc;
}

.btn-fix-all {
  background: linear-gradient(135deg, #f97316, #ea580c);
  border: none;
  color: white;
}

.btn-fix-all:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4);
}

.btn-refresh:disabled,
.btn-fix-all:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Status Banner */
.status-banner {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  border-radius: 16px;
  margin-bottom: 24px;
}

.status-banner.healthy {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(34, 197, 94, 0.05));
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.status-banner.warning {
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.15), rgba(234, 179, 8, 0.05));
  border: 1px solid rgba(234, 179, 8, 0.3);
}

.status-banner.critical {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.05));
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.status-banner.healthy .status-icon { color: #22c55e; }
.status-banner.warning .status-icon { color: #eab308; }
.status-banner.critical .status-icon { color: #ef4444; }

.status-content {
  flex: 1;
}

.status-content h2 {
  font-size: 20px;
  font-weight: 600;
  color: #f8fafc;
  margin: 0 0 4px 0;
}

.status-content p {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

.status-metrics {
  display: flex;
  gap: 24px;
}

.metric {
  text-align: center;
}

.metric .value {
  display: block;
  font-size: 28px;
  font-weight: 700;
}

.metric .label {
  font-size: 12px;
  color: #64748b;
}

.metric.healthy .value { color: #22c55e; }
.metric.warning .value { color: #eab308; }
.metric.critical .value { color: #ef4444; }

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.section {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #f8fafc;
  margin: 0 0 16px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

/* Components Section */
.components-section {
  grid-column: span 2;
}

.components-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.component-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s ease;
}

.component-card.healthy {
  border-left: 3px solid #22c55e;
}

.component-card.warning {
  border-left: 3px solid #eab308;
}

.component-card.critical {
  border-left: 3px solid #ef4444;
}

.component-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.component-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  color: #94a3b8;
}

.component-info {
  flex: 1;
}

.component-info h4 {
  font-size: 14px;
  font-weight: 600;
  color: #f8fafc;
  margin: 0 0 4px 0;
}

.status-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.status-badge.healthy {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.status-badge.warning {
  background: rgba(234, 179, 8, 0.2);
  color: #eab308;
}

.status-badge.critical {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.fix-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(249, 115, 22, 0.2);
  border: none;
  border-radius: 8px;
  color: #f97316;
  cursor: pointer;
  transition: all 0.2s ease;
}

.fix-btn:hover:not(:disabled) {
  background: #f97316;
  color: white;
}

.fix-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.component-message {
  font-size: 13px;
  color: #94a3b8;
  margin: 0 0 12px 0;
}

.component-details {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.detail-item {
  font-size: 12px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 4px;
}

.detail-key {
  color: #64748b;
}

.detail-value {
  color: #94a3b8;
  margin-left: 4px;
}

/* Dependency Section */
.dependency-graph {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dep-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
}

.dep-source {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #f8fafc;
  min-width: 120px;
}

.dep-arrow {
  color: #475569;
}

.dep-targets {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.dep-tag {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  color: #94a3b8;
}

.dep-tag.healthy {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.dep-tag.warning {
  background: rgba(234, 179, 8, 0.15);
  color: #eab308;
}

.dep-tag.critical {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

/* Pages Section */
.pages-section {
  grid-column: span 2;
}

.pages-table {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.table-header,
.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 2fr 1.5fr 80px;
  gap: 12px;
  padding: 12px 16px;
  align-items: center;
}

.table-header {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
}

.table-row {
  background: rgba(255, 255, 255, 0.01);
  border-radius: 8px;
  font-size: 13px;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.03);
}

.page-name {
  font-weight: 500;
  color: #f8fafc;
}

.page-path {
  color: #64748b;
  font-family: monospace;
  font-size: 12px;
}

.page-components {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.comp-tag {
  font-size: 11px;
  padding: 2px 6px;
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  border-radius: 4px;
}

.comp-more {
  font-size: 11px;
  color: #64748b;
}

.page-deps {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.dep-mini-tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  color: #94a3b8;
}

.dep-mini-tag.healthy {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.dep-mini-tag.warning {
  background: rgba(234, 179, 8, 0.1);
  color: #eab308;
}

.page-status {
  text-align: center;
}

.text-green { color: #22c55e; }
.text-yellow { color: #eab308; }

/* History Section */
.empty-history {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #64748b;
  text-align: center;
}

.empty-history svg {
  opacity: 0.5;
  margin-bottom: 12px;
}

.fix-history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.fix-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
}

.fix-item.success {
  border-left: 3px solid #22c55e;
}

.fix-item.failed {
  border-left: 3px solid #ef4444;
}

.fix-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
}

.fix-item.success .fix-icon {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.fix-item.failed .fix-icon {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.fix-content {
  flex: 1;
}

.fix-component {
  font-weight: 500;
  color: #f8fafc;
  margin-right: 8px;
}

.fix-action {
  font-size: 12px;
  color: #64748b;
}

.fix-message {
  font-size: 12px;
  color: #94a3b8;
}

.fix-time {
  font-size: 11px;
  color: #64748b;
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(249, 115, 22, 0.2);
  border-top-color: #f97316;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

.loading-overlay p {
  color: #94a3b8;
}

/* Mobile */
@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .components-section,
  .pages-section {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .system-health-page {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .status-banner {
    flex-direction: column;
    text-align: center;
  }

  .status-metrics {
    width: 100%;
    justify-content: center;
  }

  .components-grid {
    grid-template-columns: 1fr;
  }

  .table-header,
  .table-row {
    grid-template-columns: 1fr 1fr auto;
  }

  .page-components,
  .page-deps {
    display: none;
  }
}
</style>
