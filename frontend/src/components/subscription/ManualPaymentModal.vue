<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>💰 Manuel Ödeme</h3>
        <button @click="$emit('close')" class="close-btn">&times;</button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="handlePayment">
          <div class="form-group">
            <label>Kaç ay uzatmak istiyorsunuz?</label>
            <select v-model.number="months" required>
              <option value="1">1 Ay - {{ calculatePrice(1) }} TL</option>
              <option value="3">3 Ay - {{ calculatePrice(3) }} TL (İndirimli)</option>
              <option value="6">6 Ay - {{ calculatePrice(6) }} TL (İndirimli)</option>
              <option value="12">12 Ay - {{ calculatePrice(12) }} TL (İndirimli)</option>
            </select>
          </div>

          <div class="form-group">
            <label>Ödeme Yöntemi</label>
            <select v-model="paymentMethod" required>
              <option value="real">TL Bakiye ({{ walletBalance.real }} TL)</option>
              <option value="coin">Armor ({{ walletBalance.coin }})</option>
            </select>
          </div>

          <div class="total-price">
            <strong>Toplam: {{ calculatePrice(months) }} TL</strong>
          </div>

          <div class="form-actions">
            <button type="button" @click="$emit('close')" class="btn btn-secondary">
              İptal
            </button>
            <button type="submit" class="btn btn-primary" :disabled="processing">
              {{ processing ? 'İşleniyor...' : 'Öde' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useSubscriptionStore } from '@/stores/subscriptions'
import { useAuthStore } from '@/stores/auth'

export default {
  props: {
    subscription: Object
  },
  emits: ['close', 'success'],
  setup(props, { emit }) {
    const subscriptionStore = useSubscriptionStore()
    const authStore = useAuthStore()

    const months = ref(1)
    const paymentMethod = ref('real')
    const processing = ref(false)

    const walletBalance = computed(() => ({
      real: authStore.user?.balance || 0,
      coin: authStore.user?.balance_coin || 0
    }))

    const calculatePrice = (m) => {
      let price = props.subscription.monthly_amount * m

      // İndirimler
      if (m >= 12) price *= 0.75 // %25 indirim
      else if (m >= 6) price *= 0.85 // %15 indirim
      else if (m >= 3) price *= 0.90 // %10 indirim

      return price.toFixed(2)
    }

    const handlePayment = async () => {
      processing.value = true
      try {
        await subscriptionStore.manualPayment(
          props.subscription.id,
          months.value,
          paymentMethod.value
        )
        alert(`Sunucu ${months.value} ay uzatıldı!`)
        emit('success')
        emit('close')
      } catch (err) {
        alert(err.message || 'Ödeme başarısız')
      } finally {
        processing.value = false
      }
    }

    return {
      months,
      paymentMethod,
      processing,
      walletBalance,
      calculatePrice,
      handlePayment
    }
  }
}
</script>

<style scoped>
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
}

.total-price {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  text-align: center;
  margin: 20px 0;
  font-size: 18px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

.btn-primary { background: #667eea; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
