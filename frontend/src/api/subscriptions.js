/**
 * AGTR Merkezi - Subscription API Client
 * Abonelik yönetimi için API fonksiyonları
 */

import client from './client'

/**
 * Kullanıcının tüm aboneliklerini getir
 */
export async function getMySubscriptions() {
  const response = await client.get('/subscriptions/my-subscriptions')
  return response.data
}

/**
 * Abonelik detaylarını getir
 */
export async function getSubscription(subscriptionId) {
  const response = await client.get(`/subscriptions/${subscriptionId}`)
  return response.data
}

/**
 * Otomatik yenilemeyi aç/kapat
 */
export async function toggleAutoRenew(subscriptionId, enabled) {
  const response = await client.post(`/subscriptions/${subscriptionId}/toggle-auto-renew`, {
    enabled
  })
  return response.data
}

/**
 * Ödeme yöntemini değiştir (TL veya Armor)
 */
export async function changePaymentMethod(subscriptionId, method) {
  const response = await client.post(`/subscriptions/${subscriptionId}/change-payment-method`, {
    method
  })
  return response.data
}

/**
 * Aboneliği iptal et
 */
export async function cancelSubscription(subscriptionId, reason = null) {
  const response = await client.post(`/subscriptions/${subscriptionId}/cancel`, {
    reason
  })
  return response.data
}

/**
 * Askıya alınmış aboneliği yeniden etkinleştir
 */
export async function reactivateSubscription(subscriptionId) {
  const response = await client.post(`/subscriptions/${subscriptionId}/reactivate`)
  return response.data
}

/**
 * Fatura geçmişini getir
 */
export async function getBillingHistory(subscriptionId, limit = 50) {
  const response = await client.get(`/subscriptions/${subscriptionId}/billing-history`, {
    params: { limit }
  })
  return response.data
}

/**
 * Manuel ödeme ile aboneliği uzat
 */
export async function manualPayment(subscriptionId, months, paymentMethod) {
  const response = await client.post(`/subscriptions/${subscriptionId}/manual-payment`, {
    months,
    payment_method: paymentMethod
  })
  return response.data
}
