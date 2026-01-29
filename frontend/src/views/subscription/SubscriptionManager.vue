<template>
  <div class="subscription-manager">
    <!-- Yükleme durumu -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Abonelikler yükleniyor...</p>
    </div>

    <!-- Hata durumu -->
    <div v-else-if="error" class="error-message">
      <span class="icon">⚠️</span>
      <p>{{ error }}</p>
      <button @click="loadSubscriptions" class="btn-retry">Tekrar Dene</button>
    </div>

    <!-- Abonelik listesi -->
    <div v-else-if="subscriptions.length > 0" class="subscriptions-list">
      <h2>Aboneliklerim</h2>

      <!-- Her abonelik kartı -->
      <div
        v-for="subscription in subscriptions"
        :key="subscription.id"
        class="subscription-card"
        :class="getStatusClass(subscription.status)"
      >
        <!-- Başlık -->
        <div class="card-header">
          <div class="server-info">
            <h3>{{ subscription.server_name }}</h3>
            <span class="server-id">#{{ subscription.game_server_id }}</span>
          </div>
          <span class="status-badge" :class="subscription.status">
            {{ getStatusText(subscription.status) }}
          </span>
        </div>

        <!-- İçerik -->
        <div class="card-content">
          <!-- Süre bilgisi -->
          <div class="expiry-info">
            <div class="info-row">
              <span class="label">Bitiş Tarihi:</span>
              <span class="value">{{ formatDate(subscription.next_billing_date) }}</span>
            </div>
            <div class="countdown" :class="getCountdownClass(subscription.next_billing_date)">
              {{ getCountdown(subscription.next_billing_date) }}
            </div>
          </div>

          <!-- Fiyat bilgisi -->
          <div class="price-info">
            <div class="info-row">
              <span class="label">Aylık Ücret:</span>
              <span class="value price">{{ subscription.monthly_amount }} TL</span>
            </div>
            <div class="info-row">
              <span class="label">Dönem:</span>
              <span class="value">{{ getBillingPeriodText(subscription.billing_period) }}</span>
            </div>
          </div>

          <!-- Otomatik yenileme -->
          <div class="auto-renew-section">
            <label class="toggle-container">
              <input
                type="checkbox"
                v-model="subscription.auto_renew_enabled"
                @change="handleAutoRenewToggle(subscription)"
              />
              <span class="toggle-slider"></span>
              <span class="toggle-label">Otomatik Yenileme</span>
            </label>
            <span v-if="subscription.auto_renew_enabled" class="auto-renew-indicator">
              🔄 Aktif
            </span>
          </div>

          <!-- Ödeme yöntemi -->
          <div class="payment-method-section">
            <label>Ödeme Yöntemi:</label>
            <select
              v-model="subscription.payment_method"
              @change="handlePaymentMethodChange(subscription)"
              class="payment-select"
            >
              <option value="real">TL Bakiye ({{ walletBalance.real }} TL)</option>
              <option value="coin">Armor ({{ walletBalance.coin }})</option>
            </select>
          </div>

          <!-- Grace period uyarısı -->
          <div v-if="subscription.status === 'grace_period'" class="alert alert-warning">
            <span class="icon">⚠️</span>
            <div>
              <strong>Yetkisiz Kullanım Süresi</strong>
              <p>Ödeme başarısız oldu. {{ subscription.failure_count }} başarısız deneme.
                 Lütfen bakiye yükleyin.</p>
            </div>
          </div>

          <!-- Aksiyon butonları -->
          <div class="actions">
            <button
              @click="showBillingHistory(subscription)"
              class="btn btn-secondary"
            >
              📊 Fatura Geçmişi
            </button>

            <button
              @click="showManualPayment(subscription)"
              class="btn btn-primary"
            >
              💰 Manuel Uzat
            </button>

            <button
              v-if="subscription.status === 'suspended'"
              @click="reactivate(subscription)"
              class="btn btn-success"
            >
              ✅ Yeniden Etkinleştir
            </button>

            <button
              v-else-if="subscription.status === 'active'"
              @click="cancelSubscription(subscription)"
              class="btn btn-danger"
            >
              ❌ İptal Et
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Abonelik yok -->
    <div v-else class="no-subscriptions">
      <span class="icon">📋</span>
      <h3>Henüz aboneliğiniz yok</h3>
      <p>Sunucu kiralayarak otomatik abonelik oluşturabilirsiniz.</p>
      <router-link to="/servers/rent" class="btn btn-primary">
        Sunucu Kirala
      </router-link>
    </div>

    <!-- Modal: Fatura Geçmişi -->
    <BillingHistoryModal
      v-if="showHistoryModal"
      :subscription="selectedSubscription"
      @close="showHistoryModal = false"
    />

    <!-- Modal: Manuel Ödeme -->
    <ManualPaymentModal
      v-if="showPaymentModal"
      :subscription="selectedSubscription"
      @close="showPaymentModal = false"
      @success="loadSubscriptions"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useSubscriptionStore } from '@/stores/subscriptions'
import { useAuthStore } from '@/stores/auth'
import BillingHistoryModal from '@/components/subscription/BillingHistoryModal.vue'
import ManualPaymentModal from '@/components/subscription/ManualPaymentModal.vue'

export default {
  name: 'SubscriptionManager',
  components: {
    BillingHistoryModal,
    ManualPaymentModal
  },
  setup() {
    const subscriptionStore = useSubscriptionStore()
    const authStore = useAuthStore()

    const loading = ref(false)
    const error = ref(null)
    const showHistoryModal = ref(false)
    const showPaymentModal = ref(false)
    const selectedSubscription = ref(null)

    const subscriptions = computed(() => subscriptionStore.subscriptions)
    const walletBalance = computed(() => ({
      real: authStore.user?.balance || 0,
      coin: authStore.user?.balance_coin || 0
    }))

    // Abonelikleri yükle
    const loadSubscriptions = async () => {
      loading.value = true
      error.value = null
      try {
        await subscriptionStore.fetchSubscriptions()
      } catch (err) {
        error.value = err.message || 'Abonelikler yüklenemedi'
      } finally {
        loading.value = false
      }
    }

    // Otomatik yenileme toggle
    const handleAutoRenewToggle = async (subscription) => {
      try {
        await subscriptionStore.toggleAutoRenew(
          subscription.id,
          subscription.auto_renew_enabled
        )
        alert(subscription.auto_renew_enabled ?
          'Otomatik yenileme açıldı' :
          'Otomatik yenileme kapatıldı'
        )
      } catch (err) {
        alert(err.message || 'İşlem başarısız')
        subscription.auto_renew_enabled = !subscription.auto_renew_enabled // Geri al
      }
    }

    // Ödeme yöntemi değiştir
    const handlePaymentMethodChange = async (subscription) => {
      try {
        await subscriptionStore.changePaymentMethod(
          subscription.id,
          subscription.payment_method
        )
        alert('Ödeme yöntemi değiştirildi')
      } catch (err) {
        alert(err.message || 'İşlem başarısız')
        await loadSubscriptions() // Yeniden yükle
      }
    }

    // Aboneliği iptal et
    const cancelSubscription = async (subscription) => {
      if (!confirm('Aboneliği iptal etmek istediğinizden emin misiniz?')) return

      const reason = prompt('İptal nedeni (opsiyonel):')

      try {
        await subscriptionStore.cancelSubscription(subscription.id, reason)
        alert('Abonelik iptal edildi. Sunucu mevcut süre sonuna kadar aktif kalacak.')
        await loadSubscriptions()
      } catch (err) {
        alert(err.message || 'İptal başarısız')
      }
    }

    // Yeniden etkinleştir
    const reactivate = async (subscription) => {
      try {
        await subscriptionStore.reactivateSubscription(subscription.id)
        alert('Abonelik yeniden etkinleştirildi')
        await loadSubscriptions()
      } catch (err) {
        alert(err.message || 'İşlem başarısız')
      }
    }

    // Fatura geçmişini göster
    const showBillingHistory = (subscription) => {
      selectedSubscription.value = subscription
      showHistoryModal.value = true
    }

    // Manuel ödeme göster
    const showManualPayment = (subscription) => {
      selectedSubscription.value = subscription
      showPaymentModal.value = true
    }

    // Yardımcı fonksiyonlar
    const getStatusClass = (status) => `status-${status}`

    const getStatusText = (status) => {
      const texts = {
        'active': 'Aktif',
        'cancelled': 'İptal Edildi',
        'suspended': 'Askıda',
        'expired': 'Süresi Doldu',
        'grace_period': 'Yetkisiz Kullanım'
      }
      return texts[status] || status
    }

    const getBillingPeriodText = (period) => {
      const texts = {
        'monthly': 'Aylık',
        'quarterly': '3 Aylık',
        'biannual': '6 Aylık',
        'annual': 'Yıllık'
      }
      return texts[period] || period
    }

    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('tr-TR', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      })
    }

    const getCountdown = (dateStr) => {
      const now = new Date()
      const expiry = new Date(dateStr)
      const diff = expiry - now
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))

      if (days < 0) return 'Süresi doldu'
      if (days === 0) return 'Bugün sona eriyor'
      if (days === 1) return 'Yarın sona eriyor'
      return `${days} gün kaldı`
    }

    const getCountdownClass = (dateStr) => {
      const days = Math.floor((new Date(dateStr) - new Date()) / (1000 * 60 * 60 * 24))
      if (days < 0) return 'expired'
      if (days <= 1) return 'urgent'
      if (days <= 3) return 'warning'
      if (days <= 7) return 'soon'
      return 'ok'
    }

    onMounted(() => {
      loadSubscriptions()
    })

    return {
      loading,
      error,
      subscriptions,
      walletBalance,
      showHistoryModal,
      showPaymentModal,
      selectedSubscription,
      loadSubscriptions,
      handleAutoRenewToggle,
      handlePaymentMethodChange,
      cancelSubscription,
      reactivate,
      showBillingHistory,
      showManualPayment,
      getStatusClass,
      getStatusText,
      getBillingPeriodText,
      formatDate,
      getCountdown,
      getCountdownClass
    }
  }
}
</script>

<style scoped>
.subscription-manager {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.subscription-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
  overflow: hidden;
  transition: transform 0.2s;
}

.subscription-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.active { background: #28a745; }
.status-badge.grace_period { background: #ffc107; color: #000; }
.status-badge.suspended { background: #dc3545; }
.status-badge.cancelled { background: #6c757d; }

.card-content {
  padding: 20px;
}

.countdown {
  font-weight: bold;
  margin-top: 5px;
}

.countdown.ok { color: #28a745; }
.countdown.soon { color: #17a2b8; }
.countdown.warning { color: #ffc107; }
.countdown.urgent { color: #fd7e14; }
.countdown.expired { color: #dc3545; }

.toggle-container {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: opacity 0.2s;
}

.btn:hover { opacity: 0.9; }
.btn-primary { background: #667eea; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn-success { background: #28a745; color: white; }
.btn-danger { background: #dc3545; color: white; }
</style>
