<template>
  <div class="shared-system-dashboard">
    <div class="dashboard-header">
      <h1>Shared Installation System</h1>
      <p class="subtitle">Template monitoring and disk usage analytics</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading shared system status...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-state">
      <p class="error-message">{{ error }}</p>
      <button @click="loadData" class="btn btn-primary">Retry</button>
    </div>

    <!-- Main Content -->
    <div v-if="!loading && !error" class="dashboard-content">

      <!-- Status Cards -->
      <div class="status-cards">
        <div class="card">
          <div class="card-icon">📦</div>
          <div class="card-content">
            <h3>{{ sharedStatus.templates?.length || 0 }}</h3>
            <p>Shared Templates</p>
          </div>
        </div>

        <div class="card">
          <div class="card-icon">💾</div>
          <div class="card-content">
            <h3>{{ formatSize(sharedStatus.total_size_mb || 0) }}</h3>
            <p>Total Disk Usage</p>
          </div>
        </div>

        <div class="card">
          <div class="card-icon">🎯</div>
          <div class="card-content">
            <h3>{{ sharedStatus.servers_using_shared || 0 }}</h3>
            <p>Active Servers</p>
          </div>
        </div>

        <div class="card success">
          <div class="card-icon">💰</div>
          <div class="card-content">
            <h3>{{ formatSize(sharedStatus.disk_savings_mb || 0) }}</h3>
            <p>Disk Savings</p>
            <small>vs Full Copy</small>
          </div>
        </div>
      </div>

      <!-- Templates List -->
      <div class="templates-section">
        <div class="section-header">
          <h2>Templates</h2>
          <button @click="refreshData" class="btn btn-secondary" :disabled="refreshing">
            <span v-if="!refreshing">🔄 Refresh</span>
            <span v-else>🔄 Refreshing...</span>
          </button>
        </div>

        <div class="templates-table-container">
          <table class="templates-table">
            <thead>
              <tr>
                <th>Template Name</th>
                <th>Size</th>
                <th>Files</th>
                <th>Last Modified</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="template in sharedStatus.templates" :key="template.name">
                <td>
                  <strong>{{ template.name }}</strong>
                  <br>
                  <small class="text-muted">{{ template.path }}</small>
                </td>
                <td>
                  <span class="size-badge">{{ formatSize(template.size_mb) }}</span>
                </td>
                <td>{{ template.file_count.toLocaleString() }}</td>
                <td>{{ formatDate(template.last_modified) }}</td>
                <td>
                  <span :class="['status-badge', template.status]">
                    {{ template.status }}
                  </span>
                  <div v-if="template.issues.length > 0" class="issues-list">
                    <small v-for="(issue, idx) in template.issues" :key="idx" class="issue">
                      ⚠️ {{ issue }}
                    </small>
                  </div>
                </td>
                <td>
                  <button
                    @click="validateTemplate(template.name)"
                    class="btn btn-sm"
                    :disabled="validatingTemplate === template.name"
                  >
                    {{ validatingTemplate === template.name ? 'Validating...' : 'Validate' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Orphan Cleanup Section -->
      <div class="orphans-section">
        <div class="section-header">
          <h2>Orphaned Directories</h2>
          <button @click="scanOrphans" class="btn btn-secondary" :disabled="scanningOrphans">
            {{ scanningOrphans ? 'Scanning...' : '🔍 Scan' }}
          </button>
        </div>

        <div v-if="orphans" class="orphans-content">
          <div v-if="orphans.orphans_found === 0" class="empty-state">
            <p>✅ No orphaned directories found!</p>
          </div>

          <div v-else>
            <div class="orphans-summary">
              <p>Found <strong>{{ orphans.orphans_found }}</strong> orphaned directories</p>
              <p>Total size: <strong>{{ formatSize(orphans.total_size_mb) }}</strong></p>
            </div>

            <table class="orphans-table">
              <thead>
                <tr>
                  <th>Server ID</th>
                  <th>Path</th>
                  <th>Size</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="orphan in orphans.orphans" :key="orphan.server_id">
                  <td>{{ orphan.server_id }}</td>
                  <td><code>{{ orphan.path }}</code></td>
                  <td>{{ formatSize(orphan.size_mb) }}</td>
                </tr>
              </tbody>
            </table>

            <div class="orphans-actions">
              <button
                @click="cleanupOrphans"
                class="btn btn-danger"
                :disabled="cleaningOrphans"
              >
                {{ cleaningOrphans ? 'Cleaning...' : '🗑️ Delete All Orphans' }}
              </button>
              <p class="warning-text">⚠️ This action cannot be undone!</p>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'

export default {
  name: 'SharedSystemDashboard',

  setup() {
    const loading = ref(true)
    const error = ref(null)
    const refreshing = ref(false)
    const sharedStatus = ref({})
    const validatingTemplate = ref(null)
    const scanningOrphans = ref(false)
    const cleaningOrphans = ref(false)
    const orphans = ref(null)

    const loadData = async () => {
      try {
        loading.value = true
        error.value = null

        const response = await apiClient.get('/admin/shared-system/status')
        sharedStatus.value = response.data
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to load shared system status'
        console.error('Load error:', err)
      } finally {
        loading.value = false
      }
    }

    const refreshData = async () => {
      try {
        refreshing.value = true
        await loadData()
      } finally {
        refreshing.value = false
      }
    }

    const validateTemplate = async (templateName) => {
      try {
        validatingTemplate.value = templateName

        const response = await apiClient.post(`/admin/shared-system/validate-template/${templateName}`)

        const result = response.data
        const issuesText = result.issues.length > 0
          ? `\n\nIssues found:\n${result.issues.join('\n')}`
          : '\n\nNo issues found!'

        alert(`Template Validation: ${result.status}\n` +
              `Size: ${formatSize(result.size_mb)}\n` +
              `Files: ${result.file_count}` +
              issuesText)

        // Refresh data to update status
        await loadData()
      } catch (err) {
        alert('Validation failed: ' + (err.response?.data?.detail || err.message))
      } finally {
        validatingTemplate.value = null
      }
    }

    const scanOrphans = async () => {
      try {
        scanningOrphans.value = true

        const response = await apiClient.post('/admin/shared-system/cleanup-orphans', null, {
          params: { confirm: false }
        })

        orphans.value = response.data
      } catch (err) {
        alert('Scan failed: ' + (err.response?.data?.detail || err.message))
      } finally {
        scanningOrphans.value = false
      }
    }

    const cleanupOrphans = async () => {
      if (!confirm(`Are you sure you want to delete ${orphans.value.orphans_found} orphaned directories?\n\n` +
                   `This will free up ${formatSize(orphans.value.total_size_mb)} of disk space.\n\n` +
                   `THIS ACTION CANNOT BE UNDONE!`)) {
        return
      }

      try {
        cleaningOrphans.value = true

        const response = await axios.post('/api/admin/shared-system/cleanup-orphans', null, {
          params: { confirm: true }
        })

        const result = response.data
        alert(`Successfully deleted ${result.deleted_count} directories!\n` +
              `Freed up ${formatSize(result.total_size_freed_mb)} of disk space.`)

        // Rescan to update list
        await scanOrphans()
      } catch (err) {
        alert('Cleanup failed: ' + (err.response?.data?.detail || err.message))
      } finally {
        cleaningOrphans.value = false
      }
    }

    const formatSize = (mb) => {
      if (!mb || mb === 0) return '0 MB'
      if (mb >= 1024) {
        return `${(mb / 1024).toFixed(1)} GB`
      }
      return `${mb.toFixed(0)} MB`
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
      } catch {
        return dateString
      }
    }

    onMounted(() => {
      loadData()
    })

    return {
      loading,
      error,
      refreshing,
      sharedStatus,
      validatingTemplate,
      scanningOrphans,
      cleaningOrphans,
      orphans,
      loadData,
      refreshData,
      validateTemplate,
      scanOrphans,
      cleanupOrphans,
      formatSize,
      formatDate
    }
  }
}
</script>

<style scoped>
.shared-system-dashboard {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-header h1 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 5px;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.loading-state, .error-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #e74c3c;
  margin-bottom: 15px;
}

.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.card.success {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.card-icon {
  font-size: 36px;
}

.card-content h3 {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 5px 0;
}

.card-content p {
  margin: 0;
  font-size: 14px;
  opacity: 0.8;
}

.card-content small {
  font-size: 12px;
  opacity: 0.7;
}

.templates-section, .orphans-section {
  background: white;
  border-radius: 8px;
  padding: 25px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c0392b;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

.templates-table-container {
  overflow-x: auto;
}

.templates-table {
  width: 100%;
  border-collapse: collapse;
}

.templates-table th {
  background: #f8f9fa;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  font-size: 13px;
  color: #555;
  border-bottom: 2px solid #dee2e6;
}

.templates-table td {
  padding: 12px;
  border-bottom: 1px solid #dee2e6;
  font-size: 14px;
}

.text-muted {
  color: #999;
  font-size: 12px;
}

.size-badge {
  display: inline-block;
  padding: 4px 10px;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.healthy {
  background: #d4edda;
  color: #155724;
}

.status-badge.degraded {
  background: #fff3cd;
  color: #856404;
}

.issues-list {
  margin-top: 5px;
}

.issue {
  display: block;
  color: #d32f2f;
  font-size: 11px;
  margin-top: 2px;
}

.orphans-content {
  margin-top: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #28a745;
  font-size: 16px;
}

.orphans-summary {
  background: #fff3cd;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.orphans-summary p {
  margin: 5px 0;
}

.orphans-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.orphans-table th {
  background: #f8f9fa;
  padding: 10px;
  text-align: left;
  font-weight: 600;
  font-size: 13px;
  border-bottom: 2px solid #dee2e6;
}

.orphans-table td {
  padding: 10px;
  border-bottom: 1px solid #dee2e6;
  font-size: 14px;
}

.orphans-table code {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 3px;
}

.orphans-actions {
  text-align: center;
}

.warning-text {
  margin-top: 10px;
  color: #d32f2f;
  font-size: 12px;
  font-weight: 600;
}
</style>
