/**
 * AGTR Merkezi - Subscription Store (Pinia)
 * Abonelik state yönetimi
 */

import { defineStore } from 'pinia'
import * as subscriptionApi from '@/api/subscriptions'

export const useSubscriptionStore = defineStore('subscriptions', {
  state: () => ({
    subscriptions: [],
    currentSubscription: null,
    billingHistory: [],
    loading: false,
    error: null
  }),

  getters: {
    /**
     * Aktif abonelikleri getir
     */
    activeSubscriptions: (state) => {
      return state.subscriptions.filter(sub => sub.status === 'active')
    },

    /**
     * Grace period'daki abonelikleri getir
     */
    gracePeriodSubscriptions: (state) => {
      return state.subscriptions.filter(sub => sub.status === 'grace_period')
    },

    /**
     * Askıya alınmış abonelikleri getir
     */
    suspendedSubscriptions: (state) => {
      return state.subscriptions.filter(sub => sub.status === 'suspended')
    },

    /**
     * Sunucu ID'sine göre abonelik bul
     */
    getByServerId: (state) => (serverId) => {
      return state.subscriptions.find(sub => sub.game_server_id === serverId)
    },

    /**
     * Abonelik ID'sine göre abonelik bul
     */
    getById: (state) => (subscriptionId) => {
      return state.subscriptions.find(sub => sub.id === subscriptionId)
    },

    /**
     * Yakında süre dolacak abonelikleri getir (7 gün içinde)
     */
    expiringSoon: (state) => {
      const now = new Date()
      const sevenDaysLater = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)

      return state.subscriptions.filter(sub => {
        const expiryDate = new Date(sub.next_billing_date)
        return expiryDate <= sevenDaysLater && expiryDate > now
      })
    }
  },

  actions: {
    /**
     * Tüm abonelikleri yükle
     */
    async fetchSubscriptions() {
      this.loading = true
      this.error = null

      try {
        this.subscriptions = await subscriptionApi.getMySubscriptions()
        return this.subscriptions
      } catch (error) {
        this.error = error.response?.data?.detail || 'Abonelikler yüklenemedi'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Tek bir aboneliği yükle
     */
    async fetchSubscription(subscriptionId) {
      this.loading = true
      this.error = null

      try {
        this.currentSubscription = await subscriptionApi.getSubscription(subscriptionId)
        return this.currentSubscription
      } catch (error) {
        this.error = error.response?.data?.detail || 'Abonelik yüklenemedi'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Otomatik yenilemeyi aç/kapat
     */
    async toggleAutoRenew(subscriptionId, enabled) {
      this.loading = true
      this.error = null

      try {
        const result = await subscriptionApi.toggleAutoRenew(subscriptionId, enabled)

        // State'i güncelle
        const subscription = this.getById(subscriptionId)
        if (subscription) {
          subscription.auto_renew_enabled = enabled
        }

        return result
      } catch (error) {
        this.error = error.response?.data?.detail || 'İşlem başarısız'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Ödeme yöntemini değiştir
     */
    async changePaymentMethod(subscriptionId, method) {
      this.loading = true
      this.error = null

      try {
        const result = await subscriptionApi.changePaymentMethod(subscriptionId, method)

        // State'i güncelle
        const subscription = this.getById(subscriptionId)
        if (subscription) {
          subscription.payment_method = method
        }

        return result
      } catch (error) {
        this.error = error.response?.data?.detail || 'İşlem başarısız'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Aboneliği iptal et
     */
    async cancelSubscription(subscriptionId, reason = null) {
      this.loading = true
      this.error = null

      try {
        const result = await subscriptionApi.cancelSubscription(subscriptionId, reason)

        // State'i güncelle
        const subscription = this.getById(subscriptionId)
        if (subscription) {
          subscription.status = 'cancelled'
          subscription.cancelled_at = result.cancelled_at
        }

        return result
      } catch (error) {
        this.error = error.response?.data?.detail || 'İptal başarısız'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Aboneliği yeniden etkinleştir
     */
    async reactivateSubscription(subscriptionId) {
      this.loading = true
      this.error = null

      try {
        const result = await subscriptionApi.reactivateSubscription(subscriptionId)

        // State'i güncelle
        const subscription = this.getById(subscriptionId)
        if (subscription) {
          subscription.status = 'active'
        }

        return result
      } catch (error) {
        this.error = error.response?.data?.detail || 'Yeniden etkinleştirme başarısız'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Fatura geçmişini yükle
     */
    async fetchBillingHistory(subscriptionId, limit = 50) {
      this.loading = true
      this.error = null

      try {
        this.billingHistory = await subscriptionApi.getBillingHistory(subscriptionId, limit)
        return this.billingHistory
      } catch (error) {
        this.error = error.response?.data?.detail || 'Fatura geçmişi yüklenemedi'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Manuel ödeme ile uzat
     */
    async manualPayment(subscriptionId, months, paymentMethod) {
      this.loading = true
      this.error = null

      try {
        const result = await subscriptionApi.manualPayment(subscriptionId, months, paymentMethod)

        // Abonelikleri yeniden yükle
        await this.fetchSubscriptions()

        return result
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ödeme başarısız'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
