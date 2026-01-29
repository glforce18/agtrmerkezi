<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>📊 Fatura Geçmişi</h3>
        <button @click="$emit('close')" class="close-btn">&times;</button>
      </div>

      <div class="modal-body">
        <div v-if="loading" class="loading">Yükleniyor...</div>

        <div v-else-if="history.length > 0" class="history-table">
          <table>
            <thead>
              <tr>
                <th>Tarih</th>
                <th>Tutar</th>
                <th>Yöntem</th>
                <th>Durum</th>
                <th>Detay</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in history" :key="record.id">
                <td>{{ formatDate(record.billing_date) }}</td>
                <td>{{ record.amount }} TL</td>
                <td>{{ record.payment_method === 'real' ? 'TL' : 'Armor' }}</td>
                <td>
                  <span class="status-badge" :class="record.status">
                    {{ getStatusText(record.status) }}
                  </span>
                </td>
                <td>
                  <small v-if="record.failure_reason">{{ record.failure_reason }}</small>
                  <small v-else>-</small>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="no-data">
          Henüz fatura geçmişi yok
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useSubscriptionStore } from '@/stores/subscriptions'

export default {
  props: {
    subscription: Object
  },
  emits: ['close'],
  setup(props) {
    const store = useSubscriptionStore()
    const loading = ref(false)
    const history = ref([])

    const loadHistory = async () => {
      loading.value = true
      try {
        history.value = await store.fetchBillingHistory(props.subscription.id)
      } catch (err) {
        alert('Geçmiş yüklenemedi')
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateStr) => {
      return new Date(dateStr).toLocaleDateString('tr-TR')
    }

    const getStatusText = (status) => {
      const texts = {
        'success': 'Başarılı',
        'failed': 'Başarısız',
        'cancelled': 'İptal',
        'retrying': 'Yeniden Deniyor'
      }
      return texts[status] || status
    }

    onMounted(loadHistory)

    return { loading, history, formatDate, getStatusText }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #dee2e6;
}

.modal-body {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
}

.status-badge.success { background: #28a745; color: white; }
.status-badge.failed { background: #dc3545; color: white; }
</style>
