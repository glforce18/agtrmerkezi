<template>
  <div class="verify-page">
    <!-- Header -->
    <div class="page-header">
      <ShieldCheckIcon :size="40" class="header-icon" />
      <div>
        <h1>Provably Fair</h1>
        <p class="subtitle">Jackpot sonuçlarının doğruluğunu kendin kontrol et</p>
      </div>
    </div>

    <!-- How It Works -->
    <div class="info-section">
      <h2>Nasıl Çalışır?</h2>
      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3>Server Seed Hash</h3>
            <p>Her tur başında sunucu gizli bir seed oluşturur ve hash'ini gösterir. Bu hash değiştirilemez.</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h3>Client Seed</h3>
            <p>Tur bittiğinde rastgele bir client seed oluşturulur veya kullanıcılardan alınır.</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h3>Sonuç Hesaplama</h3>
            <p>Server seed + Client seed = SHA256 hash → Kazanan bilet numarası</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">4</div>
          <div class="step-content">
            <h3>Doğrulama</h3>
            <p>Tur bittikten sonra server seed açıklanır. Sonucu kendin hesaplayabilirsin.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Verification Tool -->
    <div class="verify-section">
      <h2>Tur Doğrulama</h2>

      <!-- Search by Round -->
      <div class="search-box">
        <div class="input-group">
          <label>Tur Numarası</label>
          <input
            v-model.number="roundNumber"
            type="number"
            placeholder="Örn: 1234"
            min="1"
          />
        </div>
        <button @click="fetchRound" :disabled="loading" class="search-btn">
          <Loader2Icon v-if="loading" :size="18" class="spin" />
          <SearchIcon v-else :size="18" />
          Getir
        </button>
      </div>

      <!-- Round Info -->
      <div v-if="roundData" class="round-info">
        <div class="info-card">
          <h3>Tur #{{ roundData.round_number }}</h3>

          <div class="info-grid">
            <div class="info-item">
              <span class="label">Server Seed</span>
              <code class="value">{{ roundData.server_seed }}</code>
            </div>

            <div class="info-item">
              <span class="label">Server Seed Hash</span>
              <code class="value">{{ roundData.server_seed_hash }}</code>
            </div>

            <div class="info-item">
              <span class="label">Client Seed</span>
              <code class="value">{{ roundData.client_seed }}</code>
            </div>

            <div class="info-item">
              <span class="label">Kazanan Bilet</span>
              <span class="value highlight">{{ roundData.winning_ticket }}</span>
            </div>

            <div class="info-item">
              <span class="label">Hesaplanan Bilet</span>
              <span class="value" :class="{ success: roundData.ticket_verified }">
                {{ roundData.calculated_ticket }}
              </span>
            </div>
          </div>

          <!-- Verification Status -->
          <div class="verification-status" :class="{ verified: roundData.fully_verified }">
            <div v-if="roundData.fully_verified" class="status success">
              <CheckCircleIcon :size="24" />
              <span>DOĞRULANDI - Sonuç manipüle edilmemiş</span>
            </div>
            <div v-else class="status error">
              <XCircleIcon :size="24" />
              <span>DOĞRULANAMADI - Bir sorun var!</span>
            </div>
          </div>

          <!-- Detailed Checks -->
          <div class="checks">
            <div class="check" :class="{ passed: roundData.hash_verified }">
              <span>Hash Doğrulaması:</span>
              <span v-if="roundData.hash_verified">
                <CheckIcon :size="16" /> Geçti
              </span>
              <span v-else>
                <XIcon :size="16" /> Başarısız
              </span>
            </div>
            <div class="check" :class="{ passed: roundData.ticket_verified }">
              <span>Bilet Doğrulaması:</span>
              <span v-if="roundData.ticket_verified">
                <CheckIcon :size="16" /> Geçti
              </span>
              <span v-else>
                <XIcon :size="16" /> Başarısız
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Error -->
      <div v-if="error" class="error-message">
        <AlertCircleIcon :size="20" />
        {{ error }}
      </div>
    </div>

    <!-- Manual Calculator -->
    <div class="calculator-section">
      <h2>Manuel Hesaplama</h2>
      <p class="section-desc">Kendi değerlerinle hesapla</p>

      <div class="calc-form">
        <div class="input-group">
          <label>Server Seed</label>
          <input
            v-model="calcServerSeed"
            type="text"
            placeholder="Server seed'i girin"
          />
        </div>

        <div class="input-group">
          <label>Client Seed</label>
          <input
            v-model="calcClientSeed"
            type="text"
            placeholder="Client seed'i girin"
          />
        </div>

        <div class="input-group">
          <label>Toplam Bilet Sayısı</label>
          <input
            v-model.number="calcTotalTickets"
            type="number"
            placeholder="Toplam havuz miktarı"
            min="1"
          />
        </div>

        <button @click="calculate" class="calc-btn">
          Hesapla
        </button>
      </div>

      <div v-if="calcResult !== null" class="calc-result">
        <h3>Sonuç</h3>
        <div class="result-grid">
          <div class="result-item">
            <span>Birleşik Hash:</span>
            <code>{{ calcHash }}</code>
          </div>
          <div class="result-item">
            <span>Ham Sayı:</span>
            <code>{{ calcRawNumber }}</code>
          </div>
          <div class="result-item highlight">
            <span>Kazanan Bilet:</span>
            <strong>{{ calcResult }}</strong>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Rounds -->
    <div class="recent-section">
      <h2>Son Turlar</h2>
      <div class="rounds-list">
        <div
          v-for="round in recentRounds"
          :key="round.id"
          class="round-item"
          @click="roundNumber = round.round_number; fetchRound()"
        >
          <span class="round-num">#{{ round.round_number }}</span>
          <span class="round-pot">{{ formatArmor(round.total_pot) }} Armor</span>
          <span class="round-winner">{{ round.winner_username }}</span>
          <ChevronRightIcon :size="16" class="arrow" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  ShieldCheck as ShieldCheckIcon,
  Search as SearchIcon,
  Loader2 as Loader2Icon,
  CheckCircle as CheckCircleIcon,
  XCircle as XCircleIcon,
  Check as CheckIcon,
  X as XIcon,
  AlertCircle as AlertCircleIcon,
  ChevronRight as ChevronRightIcon
} from 'lucide-vue-next'

// State
const roundNumber = ref(null)
const roundData = ref(null)
const loading = ref(false)
const error = ref('')
const recentRounds = ref([])

// Calculator state
const calcServerSeed = ref('')
const calcClientSeed = ref('')
const calcTotalTickets = ref(0)
const calcResult = ref(null)
const calcHash = ref('')
const calcRawNumber = ref(0)

// Methods
const formatArmor = (amount) => {
  if (!amount) return '0'
  return amount.toLocaleString('tr-TR')
}

const fetchRound = async () => {
  if (!roundNumber.value) {
    error.value = 'Tur numarası girin'
    return
  }

  loading.value = true
  error.value = ''
  roundData.value = null

  try {
    // Önce round ID'yi bulmak için history'den bakalım
    const historyRes = await fetch('/api/games/jackpot/history?limit=50')
    if (historyRes.ok) {
      const history = await historyRes.json()
      const round = history.find(r => r.round_number === roundNumber.value)

      if (round) {
        // Verify endpoint'ini çağır
        const verifyRes = await fetch(`/api/games/jackpot/verify/${round.id}`)
        if (verifyRes.ok) {
          roundData.value = await verifyRes.json()
        } else {
          const err = await verifyRes.json()
          error.value = err.detail || 'Doğrulama yapılamadı'
        }
      } else {
        error.value = 'Tur bulunamadı veya henüz bitmemiş'
      }
    }
  } catch (e) {
    error.value = 'Bir hata oluştu'
  } finally {
    loading.value = false
  }
}

const fetchRecentRounds = async () => {
  try {
    const res = await fetch('/api/games/jackpot/history?limit=10')
    if (res.ok) {
      recentRounds.value = await res.json()
    }
  } catch (e) {
    // Silently fail
  }
}

const calculate = async () => {
  if (!calcServerSeed.value || !calcClientSeed.value || !calcTotalTickets.value) {
    return
  }

  // SHA256 hesaplama (browser crypto API)
  const combined = `${calcServerSeed.value}:${calcClientSeed.value}`
  const encoder = new TextEncoder()
  const data = encoder.encode(combined)

  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')

  calcHash.value = hashHex

  // İlk 8 karakteri sayıya çevir
  const first8 = hashHex.slice(0, 8)
  const number = parseInt(first8, 16)
  calcRawNumber.value = number

  // Bilet numarası
  calcResult.value = (number % calcTotalTickets.value) + 1
}

onMounted(() => {
  fetchRecentRounds()
})
</script>

<style scoped>
.verify-page {
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  padding: 24px;
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.header-icon {
  color: var(--success-color);
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.subtitle {
  color: var(--text-secondary);
  margin: 4px 0 0;
}

/* Info Section */
.info-section {
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  padding: 24px;
  margin-bottom: 24px;
}

.info-section h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.step {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 12px;
}

.step-number {
  width: 32px;
  height: 32px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--bg-primary);
  flex-shrink: 0;
}

.step-content h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--text-primary);
}

.step-content p {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
}

/* Verify Section */
.verify-section {
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  padding: 24px;
  margin-bottom: 24px;
}

.verify-section h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.search-box {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.input-group {
  flex: 1;
}

.input-group label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.input-group input {
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
}

.input-group input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.search-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--primary-color);
  border: none;
  border-radius: 8px;
  color: var(--bg-primary);
  font-weight: 600;
  cursor: pointer;
  align-self: flex-end;
}

.search-btn:disabled {
  opacity: 0.5;
}

/* Round Info */
.round-info {
  margin-top: 20px;
}

.info-card {
  background: var(--bg-tertiary);
  border-radius: 12px;
  padding: 20px;
}

.info-card h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.info-grid {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.info-item .value {
  font-family: monospace;
  font-size: 12px;
  color: var(--text-primary);
  background: var(--bg-primary);
  padding: 8px;
  border-radius: 6px;
  word-break: break-all;
}

.info-item .value.highlight {
  color: var(--primary-color);
  font-weight: 700;
  font-size: 18px;
}

.info-item .value.success {
  color: var(--success-color);
}

/* Verification Status */
.verification-status {
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.verification-status.verified {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid var(--success-color);
}

.verification-status:not(.verified) {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--danger-color);
}

.status {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
}

.status.success {
  color: var(--success-color);
}

.status.error {
  color: var(--danger-color);
}

/* Checks */
.checks {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.check {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--bg-primary);
  border-radius: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.check.passed span:last-child {
  color: var(--success-color);
  display: flex;
  align-items: center;
  gap: 4px;
}

.check:not(.passed) span:last-child {
  color: var(--danger-color);
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Error */
.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--danger-color);
  border-radius: 8px;
  color: var(--danger-color);
  font-size: 14px;
}

/* Calculator Section */
.calculator-section {
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  padding: 24px;
  margin-bottom: 24px;
}

.calculator-section h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--text-primary);
}

.section-desc {
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 20px;
}

.calc-form {
  display: grid;
  gap: 16px;
}

.calc-btn {
  padding: 12px 24px;
  background: var(--primary-color);
  border: none;
  border-radius: 8px;
  color: var(--bg-primary);
  font-weight: 600;
  cursor: pointer;
  width: fit-content;
}

.calc-result {
  margin-top: 20px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 12px;
}

.calc-result h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.result-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.result-item span {
  color: var(--text-secondary);
}

.result-item code {
  font-family: monospace;
  font-size: 11px;
  color: var(--text-primary);
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-item.highlight {
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 8px;
  margin-top: 8px;
}

.result-item.highlight strong {
  font-size: 24px;
  color: var(--primary-color);
}

/* Recent Rounds */
.recent-section {
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  padding: 24px;
}

.recent-section h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.rounds-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.round-item {
  display: grid;
  grid-template-columns: 80px 1fr 1fr 30px;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.round-item:hover {
  background: var(--bg-primary);
}

.round-num {
  font-weight: 600;
  color: var(--text-secondary);
}

.round-pot {
  color: var(--primary-color);
  font-weight: 600;
}

.round-winner {
  color: var(--text-primary);
}

.arrow {
  color: var(--text-secondary);
}

/* Spin animation */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .steps {
    grid-template-columns: 1fr;
  }

  .search-box {
    flex-direction: column;
  }

  .round-item {
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .round-item .arrow {
    display: none;
  }
}
</style>
</template>
