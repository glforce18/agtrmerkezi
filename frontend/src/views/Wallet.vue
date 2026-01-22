<template>
  <div class="wallet-page min-h-screen py-4">
    <!-- Maintenance Check -->
    <MaintenanceOverlay feature="payments" />

    <!-- Loading State -->
    <div v-if="!user" class="flex items-center justify-center min-h-[60vh]">
      <div class="text-center">
        <n-spin size="large" />
        <p class="mt-4 text-gray-400">Yükleniyor...</p>
      </div>
    </div>
    <div v-else class="container-custom">
      <!-- Page Header -->
      <div class="mb-4 flex items-start justify-between">
        <div>
          <h1 class="text-3xl font-bold flex items-center gap-3 mb-2">
            <div class="header-icon-wrapper">
              <WalletIcon class="w-8 h-8 text-orange-500" />
            </div>
            Cüzdan
          </h1>
          <p class="text-gray-400">Bakiyeni yönet, TL yükle ve Armor'a dönüştür</p>
        </div>
        <div class="hidden md:flex items-center gap-2 text-xs text-gray-500">
          <kbd class="kbd">D</kbd> TL Yükle
          <kbd class="kbd">A</kbd> Dönüştür
          <kbd class="kbd">E</kbd> Disa Aktar
        </div>
      </div>

      <!-- Balance Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <!-- TL Balance Card -->
        <div class="balance-card tl-card group" @click="showDepositModal = true">
          <div class="card-glow tl-glow"></div>
          <div class="card-shine"></div>
          <div class="card-content">
            <div class="flex items-start justify-between mb-4">
              <div class="icon-box tl-icon">
                <Banknote class="w-7 h-7 text-green-400" />
              </div>
              <div class="trend-badge trend-up" v-if="balanceTrend.tl > 0">
                <TrendingUp class="w-3 h-3" />
                <span>+{{ balanceTrend.tl }}%</span>
              </div>
              <div class="trend-badge trend-down" v-else-if="balanceTrend.tl < 0">
                <TrendingDown class="w-3 h-3" />
                <span>{{ balanceTrend.tl }}%</span>
              </div>
            </div>
            <div class="mb-4">
              <span class="text-sm text-gray-400 block mb-1">TL Bakiye</span>
              <div class="balance-amount">
                <span class="text-3xl font-bold balance-value" ref="tlBalanceRef">
                  {{ animatedTlBalance }}
                </span>
                <span class="text-xl text-gray-400 ml-1">TL</span>
              </div>
            </div>
            <!-- Mini Sparkline -->
            <div class="sparkline-container mb-4">
              <svg class="sparkline" viewBox="0 0 100 30" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="tlGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="rgba(16, 185, 129, 0.4)" />
                    <stop offset="100%" stop-color="rgba(16, 185, 129, 0)" />
                  </linearGradient>
                </defs>
                <path :d="tlSparklinePath" fill="url(#tlGradient)" class="sparkline-area" />
                <path :d="tlSparklineStroke" fill="none" stroke="#10b981" stroke-width="2" class="sparkline-line" />
                <circle :cx="sparklineEndX" :cy="sparklineEndY(tlHistory)" r="3" fill="#10b981" class="sparkline-dot" />
              </svg>
            </div>
            <n-button type="primary" block class="action-btn tl-action-btn">
              <template #icon><Plus class="w-4 h-4" /></template>
              TL Yükle
            </n-button>
          </div>
        </div>

        <!-- Armor Balance Card -->
        <div class="balance-card armor-card group" @click="showConvertModal = true">
          <div class="card-glow armor-glow"></div>
          <div class="card-shine"></div>
          <div class="card-content">
            <div class="flex items-start justify-between mb-4">
              <div class="icon-box armor-icon">
                <img :src="armorIconUrl" alt="Armor" class="w-10 h-10 object-contain armor-img" />
              </div>
              <div class="trend-badge trend-up" v-if="balanceTrend.armor > 0">
                <TrendingUp class="w-3 h-3" />
                <span>+{{ balanceTrend.armor }}%</span>
              </div>
              <div class="trend-badge trend-down" v-else-if="balanceTrend.armor < 0">
                <TrendingDown class="w-3 h-3" />
                <span>{{ balanceTrend.armor }}%</span>
              </div>
            </div>
            <div class="mb-4">
              <span class="text-sm text-gray-400 block mb-1">Armor Bakiye</span>
              <div class="balance-amount">
                <span class="text-3xl font-bold balance-value" ref="armorBalanceRef">
                  {{ animatedArmorBalance }}
                </span>
                <span class="text-xl text-orange-400 ml-1">Armor</span>
              </div>
            </div>
            <!-- Mini Sparkline -->
            <div class="sparkline-container mb-4">
              <svg class="sparkline" viewBox="0 0 100 30" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="armorGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="rgba(249, 115, 22, 0.4)" />
                    <stop offset="100%" stop-color="rgba(249, 115, 22, 0)" />
                  </linearGradient>
                </defs>
                <path :d="armorSparklinePath" fill="url(#armorGradient)" class="sparkline-area" />
                <path :d="armorSparklineStroke" fill="none" stroke="#f97316" stroke-width="2" class="sparkline-line" />
                <circle :cx="sparklineEndX" :cy="sparklineEndY(armorHistory)" r="3" fill="#f97316" class="sparkline-dot" />
              </svg>
            </div>
            <n-button block class="action-btn armor-btn">
              <template #icon><ArrowRightLeft class="w-4 h-4" /></template>
              Dönüştür
            </n-button>
          </div>
        </div>

        <!-- Rate Card with Live Indicator -->
        <div class="balance-card rate-card">
          <div class="card-glow rate-glow"></div>
          <div class="card-shine"></div>
          <div class="card-content">
            <div class="flex items-start justify-between mb-4">
              <div class="icon-box rate-icon">
                <TrendingUp class="w-7 h-7 text-purple-400" />
              </div>
              <div class="live-indicator">
                <span class="live-dot"></span>
                <span class="text-xs">CANLI</span>
              </div>
            </div>
            <div class="mb-4">
              <span class="text-sm text-gray-400 block mb-1">Dönüşüm Orani</span>
              <div class="rate-display">
                <div class="flex items-center gap-2">
                  <span class="text-2xl font-bold">1 TL</span>
                  <ArrowRight class="w-5 h-5 text-purple-400 rate-arrow" />
                  <span class="text-2xl font-bold text-purple-400">{{ armorRate }}</span>
                  <span class="text-lg text-purple-300">Armor</span>
                </div>
              </div>
            </div>
            <div class="rate-info">
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-400">Son güncelleme</span>
                <span class="text-gray-300">{{ lastRateUpdate }}</span>
              </div>
            </div>
            <n-tag type="info" size="small" class="mt-3 rate-tag">
              <template #icon><Lock class="w-3 h-3 mr-1" /></template>
              Sabit oran garantisi
            </n-tag>
          </div>
        </div>
      </div>

      <!-- Featured Package Spotlight -->
      <div class="featured-spotlight mb-10" v-if="featuredPackage">
        <div class="spotlight-bg"></div>
        <div class="spotlight-particles">
          <span v-for="i in 6" :key="i" class="particle" :style="{ '--i': i }"></span>
        </div>
        <div class="spotlight-content">
          <div class="flex flex-col md:flex-row items-center justify-between gap-6">
            <div class="flex items-center gap-6">
              <div class="spotlight-icon">
                <img :src="armorIconUrl" alt="Armor" class="w-16 h-16 object-contain spotlight-armor-img" />
                <div class="spotlight-badge">
                  <Zap class="w-4 h-4" />
                </div>
                <div class="spotlight-ring"></div>
              </div>
              <div>
                <div class="flex items-center gap-2 mb-1">
                  <n-tag type="warning" size="small" class="featured-tag">
                    <template #icon><Star class="w-3 h-3" /></template>
                    En Popüler
                  </n-tag>
                  <n-tag type="success" size="small">+{{ featuredPackage.bonus_percent }}% Bonus</n-tag>
                </div>
                <h3 class="text-2xl font-bold mb-1">{{ featuredPackage.name }} Paketi</h3>
                <p class="text-gray-400">
                  {{ formatNumber(featuredPackage.armor_amount) }} Armor +
                  <span class="text-green-400">{{ formatNumber(Math.floor(featuredPackage.armor_amount * featuredPackage.bonus_percent / 100)) }} Bonus</span>
                </p>
              </div>
            </div>
            <div class="text-center md:text-right">
              <div class="text-3xl font-bold text-orange-500 mb-2 featured-price">{{ formatCurrency(featuredPackage.tl_amount) }} TL</div>
              <n-button type="primary" size="large" class="featured-buy-btn" @click="buyPackage(featuredPackage)">
                <template #icon><ShoppingCart class="w-5 h-5" /></template>
                Hemen Al
              </n-button>
            </div>
          </div>
        </div>
      </div>

      <!-- Armor Packages Carousel/Grid -->
      <div class="mb-10">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-xl font-bold mb-1">Armor Paketleri</h2>
            <p class="text-gray-400 text-sm">TL ile Armor satın al, bonus kazan!</p>
          </div>
          <div class="flex gap-2">
            <n-button quaternary circle size="small" class="scroll-btn" @click="scrollPackages('left')">
              <template #icon><ChevronLeft class="w-5 h-5" /></template>
            </n-button>
            <n-button quaternary circle size="small" class="scroll-btn" @click="scrollPackages('right')">
              <template #icon><ChevronRight class="w-5 h-5" /></template>
            </n-button>
          </div>
        </div>

        <div class="packages-container" ref="packagesRef">
          <div class="packages-grid">
            <div
              v-for="(pkg, index) in armorPackages"
              :key="pkg.id"
              class="package-card"
              :class="{
                'featured': pkg.is_featured,
                'selected': selectedPackage?.id === pkg.id
              }"
              :style="{ '--delay': index * 0.1 + 's' }"
              @click="selectPackage(pkg)"
            >
              <!-- Card Glow Effect -->
              <div class="package-glow"></div>

              <!-- Bonus Badge -->
              <div v-if="pkg.bonus_percent > 0" class="bonus-badge">
                <Gift class="w-3 h-3 mr-1" />
                +{{ pkg.bonus_percent }}%
              </div>

              <!-- Featured Star -->
              <div v-if="pkg.is_featured" class="featured-star">
                <Star class="w-4 h-4" />
              </div>

              <div class="package-content">
                <div class="package-icon">
                  <img :src="armorIconUrl" alt="Armor" class="w-14 h-14 object-contain" />
                </div>
                <div class="text-3xl font-bold mb-1 package-amount">{{ formatNumber(pkg.armor_amount) }}</div>
                <div class="text-sm text-gray-400 mb-2">Armor</div>
                <div v-if="pkg.bonus_percent > 0" class="bonus-text">
                  <Sparkles class="w-3 h-3 inline mr-1" />
                  +{{ formatNumber(Math.floor(pkg.armor_amount * pkg.bonus_percent / 100)) }} Bonus
                </div>
                <div class="package-price">{{ formatCurrency(pkg.tl_amount) }} TL</div>
                <n-button
                  type="primary"
                  size="small"
                  block
                  class="package-btn"
                  @click.stop="buyPackage(pkg)"
                >
                  <template #icon><ShoppingCart class="w-4 h-4" /></template>
                  Satın Al
                </n-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Transaction History with Filters -->
      <div>
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 gap-4">
          <div>
            <h2 class="text-xl font-bold">İşlem Gecmisi</h2>
            <p class="text-gray-400 text-sm">Tüm finansal işlemleriniz</p>
          </div>
          <div class="flex flex-wrap items-center gap-3">
            <!-- Date Range Filter -->
            <n-date-picker
              v-model:value="dateRange"
              type="daterange"
              clearable
              size="small"
              :shortcuts="dateShortcuts"
              start-placeholder="Başlangıç"
              end-placeholder="Bitis"
              class="date-picker"
            />
            <!-- Export Button -->
            <n-button size="small" class="export-btn" @click="exportTransactions">
              <template #icon><Download class="w-4 h-4" /></template>
              Disa Aktar
            </n-button>
          </div>
        </div>

        <!-- Transaction Type Filter Buttons -->
        <div class="filter-buttons-container mb-4">
          <button
            v-for="filter in transactionFilters"
            :key="filter.value"
            class="filter-btn"
            :class="{
              active: transactionTypeFilter === filter.value,
              [filter.colorClass]: transactionTypeFilter === filter.value
            }"
            @click="transactionTypeFilter = filter.value"
          >
            <component :is="filter.icon" class="w-4 h-4" />
            <span>{{ filter.label }}</span>
            <span v-if="getFilterCount(filter.value) > 0" class="filter-count">{{ getFilterCount(filter.value) }}</span>
          </button>
        </div>

        <n-card class="glass-card transactions-card">
          <!-- Stats Row -->
          <div class="tx-stats-row mb-4" v-if="filteredTransactions.length > 0">
            <div class="tx-stat">
              <div class="tx-stat-icon">
                <Receipt class="w-4 h-4 text-gray-400" />
              </div>
              <div>
                <span class="tx-stat-label">Toplam İşlem</span>
                <span class="tx-stat-value">{{ filteredTransactions.length }}</span>
              </div>
            </div>
            <div class="tx-stat">
              <div class="tx-stat-icon green">
                <ArrowDownLeft class="w-4 h-4 text-green-400" />
              </div>
              <div>
                <span class="tx-stat-label">Toplam Giriş</span>
                <span class="tx-stat-value text-green-400">+{{ formatCurrency(totalDeposits) }} TL</span>
              </div>
            </div>
            <div class="tx-stat">
              <div class="tx-stat-icon purple">
                <RefreshCw class="w-4 h-4 text-purple-400" />
              </div>
              <div>
                <span class="tx-stat-label">Toplam Dönüşüm</span>
                <span class="tx-stat-value text-purple-400">{{ formatNumber(totalConversions) }} Armor</span>
              </div>
            </div>
          </div>

          <n-data-table
            :columns="txColumns"
            :data="filteredTransactions"
            :bordered="false"
            :single-line="false"
            :pagination="pagination"
            :row-class-name="getRowClassName"
            class="transactions-table"
          />

          <!-- Empty State with Illustration -->
          <div v-if="filteredTransactions.length === 0" class="empty-state">
            <div class="empty-illustration">
              <div class="empty-circle">
                <Receipt class="w-16 h-16 text-gray-600" />
              </div>
              <div class="empty-dots">
                <span v-for="i in 3" :key="i" :style="{ '--delay': i * 0.2 + 's' }"></span>
              </div>
            </div>
            <h3 class="text-xl font-semibold text-gray-400 mt-6 mb-2">Henüz işlem yok</h3>
            <p class="text-gray-500 mb-6">İlk işlemini yaparak başla!</p>
            <div class="empty-actions">
              <n-button type="primary" @click="showDepositModal = true">
                <template #icon><Plus class="w-4 h-4" /></template>
                TL Yükle
              </n-button>
              <n-button @click="showConvertModal = true">
                <template #icon><ArrowRightLeft class="w-4 h-4" /></template>
                Dönüştür
              </n-button>
            </div>
          </div>
        </n-card>
      </div>
    </div>

    <!-- Animated TL Deposit Modal -->
    <n-modal
      v-model:show="showDepositModal"
      :mask-closable="true"
      class="deposit-modal"
    >
      <div class="modal-container deposit-modal-content">
        <div class="modal-glow deposit-glow"></div>
        <div class="modal-header">
          <div class="modal-icon deposit-icon">
            <Banknote class="w-8 h-8 text-green-400" />
            <div class="icon-ring"></div>
          </div>
          <h2 class="text-xl font-bold">TL Yükle</h2>
          <p class="text-gray-400 text-sm">Hesabınıza güvenle TL yükleyin</p>
          <button class="modal-close" @click="showDepositModal = false">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="modal-body">
          <!-- Amount Input -->
          <div class="mb-6">
            <label class="input-label">Yüklenecek Miktar</label>
            <div class="amount-input-wrapper">
              <n-input-number
                v-model:value="depositAmount"
                :min="10"
                :max="10000"
                placeholder="0.00"
                size="large"
                :show-button="false"
              />
              <span class="amount-suffix">TL</span>
            </div>
            <!-- Quick Amount Buttons -->
            <div class="quick-amounts">
              <button
                v-for="amount in quickAmounts"
                :key="amount"
                class="quick-amount-btn"
                :class="{ active: depositAmount === amount }"
                @click="depositAmount = amount"
              >
                <span class="quick-amount-value">{{ amount }}</span>
                <span class="quick-amount-label">TL</span>
              </button>
            </div>
          </div>

          <!-- Payment Methods -->
          <div class="mb-6">
            <label class="input-label">Ödeme Yontemi</label>
            <div class="payment-methods-grid">
              <div
                v-for="method in paymentMethods"
                :key="method.id"
                class="payment-method-card"
                :class="{ selected: selectedMethod === method.id }"
                @click="selectedMethod = method.id"
              >
                <div class="method-glow" :class="method.glowClass"></div>
                <div class="method-icon" :class="method.color">
                  <component :is="method.icon" class="w-8 h-8" />
                </div>
                <span class="method-name">{{ method.name }}</span>
                <div class="method-check" v-if="selectedMethod === method.id">
                  <Check class="w-4 h-4" />
                </div>
              </div>
            </div>
          </div>

          <!-- Summary -->
          <div v-if="depositAmount >= 10" class="summary-box">
            <div class="summary-row">
              <span>Yükleme Miktari</span>
              <span>{{ formatCurrency(depositAmount) }} TL</span>
            </div>
            <div class="summary-row">
              <span>İşlem Ücreti</span>
              <span class="text-green-400">Ücretsiz</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-row total">
              <span>Hesabınıza Eklenecek</span>
              <span class="text-green-400 text-xl font-bold">{{ formatCurrency(depositAmount) }} TL</span>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <n-button quaternary @click="showDepositModal = false">İptal</n-button>
          <n-button
            type="primary"
            size="large"
            class="submit-btn"
            @click="processDeposit"
            :disabled="depositAmount < 10 || !selectedMethod"
            :loading="depositing"
          >
            <template #icon><Lock class="w-4 h-4" /></template>
            Güvenli Ödeme
          </n-button>
        </div>
      </div>
    </n-modal>

    <!-- Animated Conversion Modal -->
    <n-modal
      v-model:show="showConvertModal"
      :mask-closable="true"
      class="convert-modal"
    >
      <div class="modal-container convert-modal-content">
        <div class="modal-glow convert-glow"></div>
        <div class="modal-header">
          <div class="modal-icon convert-icon">
            <ArrowRightLeft class="w-8 h-8 text-orange-400" />
            <div class="icon-ring orange"></div>
          </div>
          <h2 class="text-xl font-bold">TL'yi Armor'a Dönüştür</h2>
          <p class="text-gray-400 text-sm">Anlik dönüşüm, sabit kur</p>
          <button class="modal-close" @click="showConvertModal = false">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="modal-body">
          <!-- Live Rate Display -->
          <div class="live-rate-box">
            <div class="rate-live-indicator">
              <span class="live-dot"></span>
              CANLI KUR
            </div>
            <div class="rate-conversion">
              <span class="rate-from">1 TL</span>
              <div class="rate-arrow-animated">
                <div class="arrow-trail"></div>
                <ArrowRight class="w-6 h-6" />
              </div>
              <span class="rate-to">{{ armorRate }} Armor</span>
            </div>
          </div>

          <!-- Conversion Calculator -->
          <div class="conversion-calculator">
            <div class="calc-input-group">
              <label class="input-label">TL Miktari</label>
              <div class="calc-input">
                <Banknote class="input-icon text-green-400" />
                <n-input-number
                  v-model:value="convertAmount"
                  :min="1"
                  :max="user?.balance || 0"
                  placeholder="0"
                  :show-button="false"
                  size="large"
                />
                <span class="input-currency">TL</span>
              </div>
              <div class="input-hint">
                Mevcut: <span class="text-green-400">{{ formatCurrency(user?.balance || 0) }} TL</span>
              </div>
            </div>

            <div class="calc-arrow">
              <div class="arrow-circle">
                <ArrowDown class="w-5 h-5 text-orange-500 arrow-bounce" />
              </div>
              <div class="arrow-line"></div>
            </div>

            <div class="calc-output-group">
              <label class="input-label">Alacaginiz Armor</label>
              <div class="calc-output">
                <img :src="armorIconUrl" alt="Armor" class="w-10 h-10 output-icon" />
                <span class="output-value">{{ formatNumber(convertAmount * armorRate) }}</span>
                <span class="output-currency">Armor</span>
              </div>
            </div>
          </div>

          <!-- Quick Convert Buttons -->
          <div class="quick-convert-amounts">
            <button
              v-for="pct in quickPercentages"
              :key="pct.value"
              class="quick-convert-btn"
              :class="{ active: isPercentageActive(pct.value) }"
              @click="setConvertPercentage(pct.value)"
            >
              <span class="pct-value">{{ pct.label }}</span>
            </button>
          </div>
        </div>

        <div class="modal-footer">
          <n-button quaternary @click="showConvertModal = false">İptal</n-button>
          <n-button
            type="primary"
            size="large"
            class="submit-btn"
            @click="processConversion"
            :disabled="convertAmount < 1 || convertAmount > (user?.balance || 0)"
            :loading="converting"
          >
            <template #icon><RefreshCw class="w-4 h-4" /></template>
            Dönüştür
          </n-button>
        </div>
      </div>
    </n-modal>

    <!-- Success Animation Overlay -->
    <Teleport to="body">
      <Transition name="success-overlay">
        <div v-if="showSuccessAnimation" class="success-overlay" @click="showSuccessAnimation = false">
          <div class="success-content">
            <div class="success-rings">
              <span v-for="i in 3" :key="i" :style="{ '--delay': i * 0.2 + 's' }"></span>
            </div>
            <div class="success-icon">
              <CheckCircle class="w-20 h-20 text-green-500" />
            </div>
            <h3 class="text-2xl font-bold mt-4">{{ successMessage.title }}</h3>
            <p class="text-gray-400 mt-2">{{ successMessage.description }}</p>
            <div class="success-confetti">
              <span v-for="i in 12" :key="i" :style="{ '--i': i }"></span>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Error Animation Overlay -->
    <Teleport to="body">
      <Transition name="error-overlay">
        <div v-if="showErrorAnimation" class="error-overlay" @click="showErrorAnimation = false">
          <div class="error-content">
            <div class="error-icon">
              <XCircle class="w-20 h-20 text-red-500" />
            </div>
            <h3 class="text-2xl font-bold mt-4">{{ errorMessage.title }}</h3>
            <p class="text-gray-400 mt-2">{{ errorMessage.description }}</p>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, h, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import MaintenanceOverlay from '@/components/MaintenanceOverlay.vue'
import { NTag } from 'naive-ui'
import {
  Wallet as WalletIcon,
  Banknote,
  ShieldCheck,
  Plus,
  ArrowRightLeft,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  ArrowDown,
  CreditCard,
  Building2,
  Smartphone,
  Receipt,
  ArrowUpRight,
  ArrowDownLeft,
  RefreshCw,
  Download,
  Lock,
  Check,
  X,
  ChevronLeft,
  ChevronRight,
  Gift,
  Star,
  Sparkles,
  ShoppingCart,
  Zap,
  CheckCircle,
  XCircle,
  Wallet2,
  Clock,
  AlertCircle,
  Filter,
  Layers
} from 'lucide-vue-next'

const route = useRoute()
const authStore = useAuthStore()

// Refs
const packagesRef = ref(null)
const tlBalanceRef = ref(null)
const armorBalanceRef = ref(null)

// Get CSRF token from cookie
const getCsrfToken = () => {
  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'csrf_token') return value
  }
  return null
}

const getHeaders = () => {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authStore.token}`
  }
  const csrfToken = getCsrfToken()
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken
  }
  return headers
}

// State
const showDepositModal = ref(false)
const showConvertModal = ref(false)
const depositAmount = ref(100)
const convertAmount = ref(10)
const selectedMethod = ref(null)
const selectedPackage = ref(null)
const depositing = ref(false)
const converting = ref(false)
const transactions = ref([])
const dateRange = ref(null)
const transactionTypeFilter = ref(null)
const showSuccessAnimation = ref(false)
const showErrorAnimation = ref(false)
const successMessage = ref({ title: '', description: '' })
const errorMessage = ref({ title: '', description: '' })

// Animated balances
const animatedTlBalance = ref('0,00')
const animatedArmorBalance = ref('0')
const previousTlBalance = ref(0)
const previousArmorBalance = ref(0)

// Constants
const armorRate = 100
const armorIconUrl = '/static/images/icons/armor.png'
const quickAmounts = [50, 100, 250, 500, 1000]
const quickPercentages = [
  { value: 25, label: '25%' },
  { value: 50, label: '50%' },
  { value: 75, label: '75%' },
  { value: 100, label: 'Tümü' }
]

// Transaction filter buttons
const transactionFilters = [
  { value: null, label: 'Tümü', icon: Layers, colorClass: 'filter-all' },
  { value: 'deposit', label: 'Yüklemeler', icon: ArrowDownLeft, colorClass: 'filter-deposit' },
  { value: 'purchase', label: 'Satın Almalar', icon: ShoppingCart, colorClass: 'filter-purchase' },
  { value: 'convert', label: 'Dönüşümler', icon: RefreshCw, colorClass: 'filter-convert' }
]

// Balance trend (mock data - would come from API in real app)
const balanceTrend = ref({
  tl: 12,
  armor: 8
})

// Sparkline data (mock - would come from API)
const tlHistory = ref([20, 25, 22, 30, 28, 35, 40, 38, 45, 50])
const armorHistory = ref([100, 150, 120, 200, 180, 250, 300, 280, 350, 400])

// Last rate update
const lastRateUpdate = ref('Simdi')

// Computed
const user = computed(() => authStore.user)

const featuredPackage = computed(() => {
  return armorPackages.value.find(pkg => pkg.is_featured)
})

// Sparkline end position calculations
const sparklineEndX = 100

const sparklineEndY = (data) => {
  if (!data?.value?.length) return 15
  const max = Math.max(...data.value)
  const min = Math.min(...data.value)
  const range = max - min || 1
  const lastVal = data.value[data.value.length - 1]
  return 30 - ((lastVal - min) / range) * 25
}

// Generate sparkline paths
const generateSparklinePath = (data, fill = false) => {
  if (!data?.length) return ''
  const max = Math.max(...data)
  const min = Math.min(...data)
  const range = max - min || 1
  const step = 100 / (data.length - 1)

  let path = data.map((val, i) => {
    const x = i * step
    const y = 30 - ((val - min) / range) * 25
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')

  if (fill) {
    path += ` L 100 30 L 0 30 Z`
  }

  return path
}

const tlSparklinePath = computed(() => generateSparklinePath(tlHistory.value, true))
const tlSparklineStroke = computed(() => generateSparklinePath(tlHistory.value, false))
const armorSparklinePath = computed(() => generateSparklinePath(armorHistory.value, true))
const armorSparklineStroke = computed(() => generateSparklinePath(armorHistory.value, false))

// Get filter count
const getFilterCount = (filterValue) => {
  if (!transactions.value) return 0
  if (filterValue === null) return transactions.value.length
  return transactions.value.filter(tx => tx.type === filterValue).length
}

// Check if percentage is active
const isPercentageActive = (pct) => {
  const balance = user.value?.balance || 0
  if (balance === 0) return false
  const expectedAmount = Math.floor(balance * pct / 100)
  return convertAmount.value === expectedAmount
}

// Filtered transactions
const filteredTransactions = computed(() => {
  let result = [...(transactions.value || [])]

  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const start = new Date(dateRange.value[0])
    const end = new Date(dateRange.value[1])
    end.setHours(23, 59, 59, 999)
    result = result.filter(tx => {
      const txDate = new Date(tx.created_at)
      return txDate >= start && txDate <= end
    })
  }

  if (transactionTypeFilter.value) {
    result = result.filter(tx => tx.type === transactionTypeFilter.value)
  }

  return result
})

// Transaction stats
const totalDeposits = computed(() => {
  return filteredTransactions.value
    .filter(tx => tx.type === 'deposit' && tx.wallet_type === 'REAL')
    .reduce((sum, tx) => sum + Math.abs(tx.amount), 0)
})

const totalConversions = computed(() => {
  return filteredTransactions.value
    .filter(tx => tx.type === 'convert' && tx.wallet_type === 'COIN')
    .reduce((sum, tx) => sum + Math.abs(tx.amount), 0)
})

// Date shortcuts for filter
const dateShortcuts = {
  'Bugun': () => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    return [today.getTime(), Date.now()]
  },
  'Son 7 Gun': () => {
    const end = Date.now()
    const start = end - 7 * 24 * 60 * 60 * 1000
    return [start, end]
  },
  'Son 30 Gun': () => {
    const end = Date.now()
    const start = end - 30 * 24 * 60 * 60 * 1000
    return [start, end]
  },
  'Bu Ay': () => {
    const now = new Date()
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    return [start.getTime(), Date.now()]
  }
}

// Pagination
const pagination = ref({
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  showQuickJumper: true,
  prefix: ({ itemCount }) => `Toplam ${itemCount} işlem`
})

// Transaction table columns
const txColumns = [
  {
    title: 'Tarih',
    key: 'created_at',
    width: 160,
    render: (row) => h('div', { class: 'tx-date' }, [
      h('span', { class: 'date-main' }, formatDate(row.created_at)),
      h('span', { class: 'date-time' }, formatTime(row.created_at))
    ])
  },
  {
    title: 'İşlem',
    key: 'type',
    width: 150,
    render: (row) => {
      const config = {
        deposit: { icon: ArrowDownLeft, label: 'TL Yükleme', color: 'text-green-400', bg: 'bg-green-500/10', border: 'border-green-500/20' },
        withdraw: { icon: ArrowUpRight, label: 'Cekim', color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20' },
        convert: { icon: RefreshCw, label: 'Dönüşüm', color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20' },
        purchase: { icon: ShoppingCart, label: 'Satın Alma', color: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/20' }
      }
      const cfg = config[row.type] || { icon: Receipt, label: row.type, color: 'text-gray-400', bg: 'bg-gray-500/10', border: 'border-gray-500/20' }
      return h('div', { class: 'tx-type' }, [
        h('div', { class: ['tx-type-icon', cfg.bg, cfg.border] }, [
          h(cfg.icon, { class: ['w-4 h-4', cfg.color] })
        ]),
        h('span', { class: 'tx-type-label' }, cfg.label)
      ])
    }
  },
  {
    title: 'Miktar',
    key: 'amount',
    width: 140,
    render: (row) => {
      const isPositive = row.amount > 0
      const colorClass = isPositive ? 'text-green-400' : 'text-red-400'
      const prefix = isPositive ? '+' : ''
      const suffix = row.wallet_type === 'REAL' ? ' TL' : ' Armor'
      return h('span', { class: ['tx-amount', colorClass] }, prefix + formatNumber(Math.abs(row.amount)) + suffix)
    }
  },
  {
    title: 'Durum',
    key: 'status',
    width: 120,
    render: (row) => {
      const config = {
        pending: { type: 'warning', icon: Clock, label: 'Bekliyor', class: 'status-pending' },
        completed: { type: 'success', icon: CheckCircle, label: 'Tamamlandı', class: 'status-completed' },
        failed: { type: 'error', icon: XCircle, label: 'Başarısız', class: 'status-failed' },
        cancelled: { type: 'default', icon: AlertCircle, label: 'İptal', class: 'status-cancelled' }
      }
      const cfg = config[row.status] || config.pending
      return h(NTag, {
        type: cfg.type,
        size: 'small',
        round: true,
        bordered: false,
        class: ['status-tag', cfg.class]
      }, {
        default: () => cfg.label,
        icon: () => h(cfg.icon, { class: 'w-3 h-3' })
      })
    }
  }
]

// Get row class for animations
const getRowClassName = (row, index) => {
  return 'tx-row'
}

// Armor Packages
const armorPackages = ref([
  { id: 1, name: 'Başlangıç', tl_amount: 10, armor_amount: 1000, bonus_percent: 0, is_featured: false },
  { id: 2, name: 'Standart', tl_amount: 25, armor_amount: 2500, bonus_percent: 5, is_featured: false },
  { id: 3, name: 'Popüler', tl_amount: 50, armor_amount: 5000, bonus_percent: 10, is_featured: true },
  { id: 4, name: 'Premium', tl_amount: 100, armor_amount: 10000, bonus_percent: 15, is_featured: false },
  { id: 5, name: 'Elite', tl_amount: 250, armor_amount: 25000, bonus_percent: 20, is_featured: false },
  { id: 6, name: 'Legend', tl_amount: 500, armor_amount: 50000, bonus_percent: 25, is_featured: false }
])

// Payment Methods
const paymentMethods = [
  { id: 'card', name: 'Kredi Karti', icon: CreditCard, color: 'method-card', glowClass: 'glow-blue' },
  { id: 'bank', name: 'Havale/EFT', icon: Building2, color: 'method-bank', glowClass: 'glow-green' },
  { id: 'mobile', name: 'Mobil Ödeme', icon: Smartphone, color: 'method-mobile', glowClass: 'glow-purple' }
]

// Methods
const formatCurrency = (value) => {
  return new Intl.NumberFormat('tr-TR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value || 0)
}

const formatNumber = (value) => {
  return new Intl.NumberFormat('tr-TR').format(value || 0)
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const formatTime = (date) => {
  return new Date(date).toLocaleTimeString('tr-TR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Animate number
const animateNumber = (start, end, duration, callback, isDecimal = false) => {
  const startTime = performance.now()
  const diff = end - start

  const animate = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    const easeProgress = 1 - Math.pow(1 - progress, 3) // ease out cubic
    const current = start + diff * easeProgress

    if (isDecimal) {
      callback(formatCurrency(current))
    } else {
      callback(formatNumber(Math.floor(current)))
    }

    if (progress < 1) {
      requestAnimationFrame(animate)
    }
  }

  requestAnimationFrame(animate)
}

// Watch for balance changes and animate
watch(() => user.value?.balance, (newVal, oldVal) => {
  const start = oldVal || previousTlBalance.value || 0
  const end = newVal || 0
  previousTlBalance.value = end
  animateNumber(start, end, 1000, (val) => {
    animatedTlBalance.value = val
  }, true)
}, { immediate: true })

watch(() => user.value?.balance_coin, (newVal, oldVal) => {
  const start = oldVal || previousArmorBalance.value || 0
  const end = newVal || 0
  previousArmorBalance.value = end
  animateNumber(start, end, 1000, (val) => {
    animatedArmorBalance.value = val
  }, false)
}, { immediate: true })

const selectPackage = (pkg) => {
  selectedPackage.value = pkg
}

const scrollPackages = (direction) => {
  if (packagesRef.value) {
    const scrollAmount = 300
    packagesRef.value.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth'
    })
  }
}

const setConvertPercentage = (pct) => {
  const balance = user.value?.balance || 0
  convertAmount.value = Math.floor(balance * pct / 100)
}

const showSuccess = (title, description) => {
  successMessage.value = { title, description }
  showSuccessAnimation.value = true
  setTimeout(() => {
    showSuccessAnimation.value = false
  }, 2500)
}

const showError = (title, description) => {
  errorMessage.value = { title, description }
  showErrorAnimation.value = true
  setTimeout(() => {
    showErrorAnimation.value = false
  }, 2500)
}

const buyPackage = async (pkg) => {
  if (!user.value) {
    window.$message?.warning('Lütfen giriş yapin')
    return
  }

  if (user.value.balance < pkg.tl_amount) {
    window.$message?.warning('Yetersiz TL bakiye. Lütfen once TL yükleyin.')
    showDepositModal.value = true
    return
  }

  window.$dialog?.warning({
    title: 'Paket Satın Al',
    content: `${pkg.tl_amount} TL karşılığında ${formatNumber(pkg.armor_amount + (pkg.armor_amount * pkg.bonus_percent / 100))} Armor satın almak istiyor musunuz?`,
    positiveText: 'Satın Al',
    negativeText: 'İptal',
    onPositiveClick: async () => {
      try {
        const response = await fetch('/api/wallet/buy-armor-package', {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({ package_id: pkg.id })
        })

        if (response.ok) {
          showSuccess('Satın Alma Başarılı!', `${formatNumber(pkg.armor_amount)} Armor hesabınıza eklendi`)
          authStore.fetchUser()
          fetchTransactions()
        } else {
          const error = await response.json()
          showError('İşlem Başarısız', error.detail || 'Bir hata oluştu')
        }
      } catch (e) {
        showError('Hata', 'Bir hata oluştu')
      }
    }
  })
}

const processDeposit = async () => {
  if (depositAmount.value < 10 || !selectedMethod.value) return

  depositing.value = true
  try {
    const response = await fetch('/api/wallet/deposit', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        amount: depositAmount.value,
        payment_method: selectedMethod.value
      })
    })

    if (response.ok) {
      const data = await response.json()
      if (data.payment_url) {
        window.location.href = data.payment_url
      } else {
        showSuccess('TL Yüklendi!', `${formatCurrency(depositAmount.value)} TL hesabınıza eklendi`)
        showDepositModal.value = false
        authStore.fetchUser()
        fetchTransactions()
      }
    } else {
      const error = await response.json()
      showError('Yükleme Başarısız', error.detail || 'Bir hata oluştu')
    }
  } catch (e) {
    showError('Hata', 'Bir hata oluştu')
  } finally {
    depositing.value = false
  }
}

const processConversion = async () => {
  if (convertAmount.value < 1 || convertAmount.value > (user.value?.balance || 0)) return

  converting.value = true
  try {
    const response = await fetch('/api/wallet/exchange', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ tl_amount: convertAmount.value })
    })

    if (response.ok) {
      const data = await response.json()
      showSuccess('Dönüşüm Başarılı!', `${formatNumber(data.armor_added)} Armor hesabınıza eklendi`)
      showConvertModal.value = false
      authStore.fetchUser()
      fetchTransactions()
    } else {
      const error = await response.json()
      showError('Dönüşüm Başarısız', error.detail || 'Bir hata oluştu')
    }
  } catch (e) {
    showError('Hata', 'Bir hata oluştu')
  } finally {
    converting.value = false
  }
}

const fetchTransactions = async () => {
  try {
    const response = await fetch('/api/wallet/transactions', {
      headers: getHeaders()
    })
    if (response.ok) {
      const data = await response.json()
      transactions.value = (data || []).map(tx => ({
        id: tx.id,
        type: tx.type,
        amount: tx.amount,
        wallet_type: tx.wallet_type,
        status: tx.status || 'completed',
        created_at: tx.created_at
      }))
    }
  } catch (e) {
    // Error handled
    transactions.value = []
  }
}

const exportTransactions = () => {
  if (filteredTransactions.value.length === 0) {
    window.$message?.warning('Disa aktarilacak işlem bulunamadı')
    return
  }

  const data = filteredTransactions.value.map(tx => ({
    Tarih: formatDate(tx.created_at) + ' ' + formatTime(tx.created_at),
    İşlem: tx.type,
    Miktar: tx.amount,
    Tur: tx.wallet_type === 'REAL' ? 'TL' : 'Armor',
    Durum: tx.status
  }))

  const csv = [
    Object.keys(data[0] || {}).join(','),
    ...data.map(row => Object.values(row).join(','))
  ].join('\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `işlem-gecmisi-${formatDate(new Date())}.csv`
  link.click()

  window.$message?.success('İşlem gecmisi disa aktarildi')
}

// Handle tab query parameter from navbar
const handleTabQuery = () => {
  const tab = route.query.tab
  if (tab === 'tl') {
    showDepositModal.value = true
  } else if (tab === 'armor') {
    showConvertModal.value = true
  }
}

// Keyboard shortcuts
const handleKeyboard = (e) => {
  // Don't trigger if typing in input
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return

  switch (e.key.toLowerCase()) {
    case 'd':
      showDepositModal.value = true
      break
    case 'a':
      showConvertModal.value = true
      break
    case 'e':
      exportTransactions()
      break
    case 'escape':
      showDepositModal.value = false
      showConvertModal.value = false
      break
  }
}

onMounted(() => {
  fetchTransactions()
  handleTabQuery()

  // Initialize animated balances
  animatedTlBalance.value = formatCurrency(user.value?.balance || 0)
  animatedArmorBalance.value = formatNumber(user.value?.balance_coin || 0)

  // Add keyboard listener
  window.addEventListener('keydown', handleKeyboard)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyboard)
})

// Watch for query changes
watch(() => route.query.tab, () => {
  handleTabQuery()
})
</script>

<style scoped>
.wallet-page {
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.95) 0%, rgba(15, 15, 25, 0.98) 100%);
  min-height: 100vh;
}

/* Keyboard shortcuts */
.kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 22px;
  padding: 0 6px;
  font-size: 11px;
  font-family: monospace;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 4px;
  margin-right: 4px;
  transition: all 0.2s;
}

.kbd:hover {
  background: rgba(249, 115, 22, 0.2);
  border-color: rgba(249, 115, 22, 0.3);
}

/* Header icon */
.header-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(249, 115, 22, 0.05));
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse-glow 2s ease-in-out infinite;
  position: relative;
}

.header-icon-wrapper::before {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.4), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}

.header-icon-wrapper:hover::before {
  opacity: 1;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(249, 115, 22, 0.2); }
  50% { box-shadow: 0 0 35px rgba(249, 115, 22, 0.4); }
}

/* Balance Cards */
.balance-card {
  position: relative;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 24px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.balance-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.02) 100%);
  pointer-events: none;
}

.balance-card:hover {
  transform: translateY(-8px) scale(1.01);
  border-color: rgba(255, 255, 255, 0.15);
}

.balance-card:hover .card-glow {
  opacity: 1;
}

.balance-card:hover .card-shine {
  transform: translateX(100%);
}

.card-glow {
  position: absolute;
  top: -100%;
  left: -100%;
  width: 300%;
  height: 300%;
  opacity: 0;
  transition: opacity 0.5s;
  pointer-events: none;
}

.card-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
  transform: skewX(-20deg);
  transition: transform 0.8s ease;
  pointer-events: none;
}

.tl-glow {
  background: radial-gradient(ellipse at center, rgba(16, 185, 129, 0.2) 0%, transparent 60%);
}

.armor-glow {
  background: radial-gradient(ellipse at center, rgba(249, 115, 22, 0.2) 0%, transparent 60%);
}

.rate-glow {
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.2) 0%, transparent 60%);
}

.card-content {
  position: relative;
  z-index: 1;
}

.tl-card {
  border-color: rgba(16, 185, 129, 0.2);
}

.tl-card:hover {
  border-color: rgba(16, 185, 129, 0.4);
  box-shadow: 0 20px 50px rgba(16, 185, 129, 0.15);
}

.armor-card {
  border-color: rgba(249, 115, 22, 0.2);
}

.armor-card:hover {
  border-color: rgba(249, 115, 22, 0.4);
  box-shadow: 0 20px 50px rgba(249, 115, 22, 0.15);
}

.rate-card {
  border-color: rgba(139, 92, 246, 0.2);
  cursor: default;
}

.rate-card:hover {
  border-color: rgba(139, 92, 246, 0.4);
  box-shadow: 0 20px 50px rgba(139, 92, 246, 0.1);
  transform: translateY(-4px);
}

.icon-box {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s, box-shadow 0.3s;
}

.balance-card:hover .icon-box {
  transform: scale(1.1);
}

.tl-icon {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.05));
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.1);
}

.armor-icon {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(249, 115, 22, 0.05));
  box-shadow: 0 8px 20px rgba(249, 115, 22, 0.1);
}

.armor-img {
  transition: transform 0.3s;
}

.balance-card:hover .armor-img {
  transform: rotate(10deg) scale(1.1);
}

.rate-icon {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(139, 92, 246, 0.05));
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.1);
}

.trend-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  animation: trend-pop 0.5s ease-out;
}

@keyframes trend-pop {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); opacity: 1; }
}

.trend-up {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.trend-down {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.balance-amount {
  display: flex;
  align-items: baseline;
}

.balance-value {
  background: linear-gradient(90deg, #fff, rgba(255, 255, 255, 0.8));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Live Indicator */
.live-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: rgba(139, 92, 246, 0.15);
  border-radius: 20px;
  color: #a78bfa;
  font-weight: 600;
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #a78bfa;
  animation: live-pulse 1.5s ease-in-out infinite;
  box-shadow: 0 0 10px rgba(167, 139, 250, 0.6);
}

@keyframes live-pulse {
  0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 10px rgba(167, 139, 250, 0.6); }
  50% { opacity: 0.5; transform: scale(0.8); box-shadow: 0 0 20px rgba(167, 139, 250, 0.8); }
}

.rate-arrow {
  animation: rate-bounce 2s ease-in-out infinite;
}

@keyframes rate-bounce {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(6px); }
}

.rate-tag {
  animation: tag-glow 2s ease-in-out infinite;
}

@keyframes tag-glow {
  0%, 100% { box-shadow: 0 0 5px rgba(139, 92, 246, 0.3); }
  50% { box-shadow: 0 0 15px rgba(139, 92, 246, 0.5); }
}

/* Sparkline */
.sparkline-container {
  height: 35px;
  opacity: 0.9;
  transition: opacity 0.3s;
}

.balance-card:hover .sparkline-container {
  opacity: 1;
}

.sparkline {
  width: 100%;
  height: 100%;
}

.sparkline-line {
  stroke-linecap: round;
  stroke-linejoin: round;
}

.sparkline-dot {
  animation: dot-pulse 2s ease-in-out infinite;
}

@keyframes dot-pulse {
  0%, 100% { r: 3; opacity: 1; }
  50% { r: 5; opacity: 0.8; }
}

/* Action Buttons */
.action-btn {
  height: 46px;
  border-radius: 14px;
  font-weight: 600;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.action-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s;
}

.action-btn:hover::before {
  left: 100%;
}

.tl-action-btn {
  background: linear-gradient(135deg, #10b981, #059669);
}

.tl-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
}

.armor-btn {
  background: rgba(249, 115, 22, 0.15);
  border: 2px solid rgba(249, 115, 22, 0.3);
  color: #f97316;
}

.armor-btn:hover {
  background: rgba(249, 115, 22, 0.25);
  border-color: rgba(249, 115, 22, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(249, 115, 22, 0.2);
}

/* Featured Spotlight */
.featured-spotlight {
  position: relative;
  border-radius: 28px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1), rgba(249, 115, 22, 0.02));
  border: 2px solid rgba(249, 115, 22, 0.25);
  padding: 32px;
  transition: all 0.4s;
}

.featured-spotlight:hover {
  border-color: rgba(249, 115, 22, 0.5);
  box-shadow: 0 25px 60px rgba(249, 115, 22, 0.15);
}

.spotlight-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 10% 50%, rgba(249, 115, 22, 0.2) 0%, transparent 40%),
    radial-gradient(circle at 90% 50%, rgba(249, 115, 22, 0.1) 0%, transparent 40%);
  pointer-events: none;
}

.spotlight-particles {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: rgba(249, 115, 22, 0.6);
  border-radius: 50%;
  animation: particle-float 8s ease-in-out infinite;
  animation-delay: calc(var(--i) * 1.2s);
}

.particle:nth-child(1) { left: 10%; top: 20%; }
.particle:nth-child(2) { left: 20%; top: 70%; }
.particle:nth-child(3) { left: 50%; top: 10%; }
.particle:nth-child(4) { left: 70%; top: 80%; }
.particle:nth-child(5) { left: 85%; top: 30%; }
.particle:nth-child(6) { left: 95%; top: 60%; }

@keyframes particle-float {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.6; }
  50% { transform: translateY(-20px) scale(1.5); opacity: 1; }
}

.spotlight-content {
  position: relative;
  z-index: 1;
}

.spotlight-icon {
  position: relative;
  width: 90px;
  height: 90px;
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(249, 115, 22, 0.05));
  display: flex;
  align-items: center;
  justify-content: center;
}

.spotlight-armor-img {
  animation: spotlight-float 3s ease-in-out infinite;
}

@keyframes spotlight-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.spotlight-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f97316, #ea580c);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  animation: badge-pulse 2s ease-in-out infinite;
  box-shadow: 0 4px 15px rgba(249, 115, 22, 0.5);
}

.spotlight-ring {
  position: absolute;
  inset: -10px;
  border: 2px solid rgba(249, 115, 22, 0.3);
  border-radius: 30px;
  animation: ring-pulse 2s ease-in-out infinite;
}

@keyframes ring-pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0; }
}

@keyframes badge-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.15); }
}

.featured-tag {
  animation: featured-shine 3s ease-in-out infinite;
}

@keyframes featured-shine {
  0%, 100% { box-shadow: 0 0 5px rgba(251, 191, 36, 0.3); }
  50% { box-shadow: 0 0 20px rgba(251, 191, 36, 0.6); }
}

.featured-price {
  text-shadow: 0 0 30px rgba(249, 115, 22, 0.5);
}

.featured-buy-btn {
  position: relative;
  overflow: hidden;
}

.featured-buy-btn::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transform: rotate(45deg);
  animation: btn-shine 3s ease-in-out infinite;
}

@keyframes btn-shine {
  0% { transform: translateX(-100%) rotate(45deg); }
  50%, 100% { transform: translateX(100%) rotate(45deg); }
}

/* Packages Container */
.packages-container {
  overflow-x: auto;
  padding-bottom: 16px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.packages-container::-webkit-scrollbar {
  display: none;
}

.packages-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(180px, 1fr));
  gap: 16px;
}

.scroll-btn {
  transition: all 0.3s;
}

.scroll-btn:hover {
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
}

@media (max-width: 1200px) {
  .packages-grid {
    grid-template-columns: repeat(6, 180px);
  }
}

/* Package Cards */
.package-card {
  position: relative;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 24px 16px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: card-appear 0.5s ease-out backwards;
  animation-delay: var(--delay);
  overflow: hidden;
}

.package-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, rgba(249, 115, 22, 0.15) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.4s;
  pointer-events: none;
}

.package-card:hover .package-glow {
  opacity: 1;
}

@keyframes card-appear {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.package-card:hover {
  transform: translateY(-10px) scale(1.03);
  border-color: #f97316;
  box-shadow:
    0 25px 50px rgba(249, 115, 22, 0.2),
    0 0 0 1px rgba(249, 115, 22, 0.1);
}

.package-card.featured {
  border-color: #f97316;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.12) 0%, rgba(249, 115, 22, 0.02) 100%);
}

.package-card.featured::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #f97316, #ea580c, #f97316);
  background-size: 200% 100%;
  animation: gradient-flow 2s linear infinite;
}

@keyframes gradient-flow {
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 0%; }
}

.package-card.selected {
  border-color: #f97316;
  box-shadow: 0 0 0 4px rgba(249, 115, 22, 0.2);
}

.bonus-badge {
  position: absolute;
  top: -10px;
  right: 12px;
  display: flex;
  align-items: center;
  padding: 5px 12px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  color: white;
  box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4);
  animation: bonus-bounce 2s ease-in-out infinite;
}

@keyframes bonus-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

.featured-star {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  animation: star-rotate 4s linear infinite;
  box-shadow: 0 4px 12px rgba(251, 191, 36, 0.4);
}

@keyframes star-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.package-content {
  text-align: center;
  position: relative;
  z-index: 1;
}

.package-icon {
  margin-bottom: 12px;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.package-card:hover .package-icon {
  transform: scale(1.15) rotate(5deg);
}

.package-amount {
  background: linear-gradient(135deg, #fff, rgba(255, 255, 255, 0.8));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.bonus-text {
  color: #10b981;
  font-size: 13px;
  margin-bottom: 12px;
  animation: bonus-glow 2s ease-in-out infinite;
}

@keyframes bonus-glow {
  0%, 100% { text-shadow: 0 0 5px rgba(16, 185, 129, 0.3); }
  50% { text-shadow: 0 0 15px rgba(16, 185, 129, 0.6); }
}

.package-price {
  font-size: 22px;
  font-weight: 700;
  color: #f97316;
  margin-bottom: 16px;
}

.package-btn {
  border-radius: 12px;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.package-card:hover .package-btn {
  transform: scale(1.05);
  box-shadow: 0 8px 20px rgba(249, 115, 22, 0.3);
}

/* Transaction Filter Buttons */
.filter-buttons-container {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #9ca3af;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
  color: var(--text-primary);
}

.filter-btn.active {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
  color: #f97316;
}

.filter-btn.active.filter-all {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
}

.filter-btn.active.filter-deposit {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
  color: #10b981;
}

.filter-btn.active.filter-purchase {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
  color: #f97316;
}

.filter-btn.active.filter-convert {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.3);
  color: #a78bfa;
}

.filter-count {
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.filter-btn.active .filter-count {
  background: rgba(255, 255, 255, 0.15);
}

/* Transaction History */
.glass-card {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
}

.transactions-card {
  overflow: hidden;
}

.tx-stats-row {
  display: flex;
  gap: 24px;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
  flex-wrap: wrap;
}

.tx-stat {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tx-stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
}

.tx-stat-icon.green {
  background: rgba(16, 185, 129, 0.1);
}

.tx-stat-icon.purple {
  background: rgba(139, 92, 246, 0.1);
}

.tx-stat-label {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 2px;
}

.tx-stat-value {
  font-size: 16px;
  font-weight: 600;
}

.export-btn {
  transition: all 0.3s;
}

.export-btn:hover {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
  color: #f97316;
}

.date-picker {
  width: 240px;
}

/* Transaction Table Styles */
.transactions-table :deep(.n-data-table-tr) {
  transition: all 0.3s;
}

.transactions-table :deep(.n-data-table-tr:hover) {
  background: rgba(255, 255, 255, 0.03) !important;
}

.tx-row {
  transition: all 0.3s;
}

.tx-date {
  display: flex;
  flex-direction: column;
}

.date-main {
  font-weight: 500;
  color: #e5e7eb;
}

.date-time {
  font-size: 12px;
  color: #6b7280;
}

.tx-type {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tx-type-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid;
  transition: transform 0.3s;
}

.tx-row:hover .tx-type-icon {
  transform: scale(1.1);
}

.tx-type-label {
  font-weight: 500;
}

.tx-amount {
  font-weight: 600;
  font-size: 15px;
}

.status-tag {
  transition: all 0.3s;
}

.status-completed {
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
}

.status-pending {
  animation: status-pulse 2s ease-in-out infinite;
}

@keyframes status-pulse {
  0%, 100% { box-shadow: 0 0 5px rgba(251, 191, 36, 0.2); }
  50% { box-shadow: 0 0 15px rgba(251, 191, 36, 0.4); }
}

.status-failed {
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
}

/* Empty State */
.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.empty-illustration {
  position: relative;
  display: inline-block;
}

.empty-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
  border: 2px dashed rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: empty-float 4s ease-in-out infinite;
}

@keyframes empty-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.empty-dots {
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
}

.empty-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(249, 115, 22, 0.5);
  animation: dot-bounce 1.5s ease-in-out infinite;
  animation-delay: var(--delay);
}

@keyframes dot-bounce {
  0%, 100% { transform: translateY(0); opacity: 0.5; }
  50% { transform: translateY(-8px); opacity: 1; }
}

.empty-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

/* Modal Styles */
.modal-container {
  position: relative;
  background: rgba(15, 15, 25, 0.98);
  backdrop-filter: blur(40px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 28px;
  width: 520px;
  max-width: 95vw;
  overflow: hidden;
  animation: modal-appear 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  pointer-events: none;
}

.deposit-glow {
  background: radial-gradient(circle at 50% 100%, rgba(16, 185, 129, 0.1) 0%, transparent 50%);
}

.convert-glow {
  background: radial-gradient(circle at 50% 100%, rgba(249, 115, 22, 0.1) 0%, transparent 50%);
}

@keyframes modal-appear {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(30px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  position: relative;
  padding: 36px 36px 28px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.modal-icon {
  position: relative;
  width: 72px;
  height: 72px;
  border-radius: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 18px;
}

.deposit-icon {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.05));
}

.convert-icon {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(249, 115, 22, 0.05));
}

.icon-ring {
  position: absolute;
  inset: -6px;
  border: 2px solid rgba(16, 185, 129, 0.3);
  border-radius: 26px;
  animation: icon-ring-pulse 2s ease-in-out infinite;
}

.icon-ring.orange {
  border-color: rgba(249, 115, 22, 0.3);
}

@keyframes icon-ring-pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.15); opacity: 0; }
}

.modal-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #9ca3af;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: white;
  transform: rotate(90deg);
}

.modal-body {
  padding: 28px 36px;
}

.modal-footer {
  padding: 20px 36px 28px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.submit-btn {
  position: relative;
  overflow: hidden;
}

.submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
  transition: left 0.5s;
}

.submit-btn:not(:disabled):hover::before {
  left: 100%;
}

.input-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #9ca3af;
  margin-bottom: 10px;
}

/* Amount Input */
.amount-input-wrapper {
  position: relative;
}

.amount-input-wrapper :deep(.n-input-number) {
  width: 100%;
}

.amount-input-wrapper :deep(.n-input__input-el) {
  font-size: 28px !important;
  font-weight: 700 !important;
  padding-right: 50px !important;
}

.amount-suffix {
  position: absolute;
  right: 18px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 18px;
  font-weight: 600;
  color: #6b7280;
}

/* Quick Amount Buttons */
.quick-amounts {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}

.quick-amount-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-amount-btn:hover {
  border-color: rgba(249, 115, 22, 0.4);
  background: rgba(249, 115, 22, 0.05);
}

.quick-amount-btn.active {
  background: rgba(249, 115, 22, 0.15);
  border-color: #f97316;
}

.quick-amount-value {
  font-size: 18px;
  font-weight: 700;
  color: #e5e7eb;
  transition: color 0.3s;
}

.quick-amount-btn.active .quick-amount-value {
  color: #f97316;
}

.quick-amount-label {
  font-size: 11px;
  color: #6b7280;
  margin-top: 2px;
}

/* Payment Methods Grid */
.payment-methods-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.payment-method-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 2px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  cursor: pointer;
  transition: all 0.4s;
  overflow: hidden;
}

.method-glow {
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 0.4s;
  pointer-events: none;
}

.glow-blue { background: radial-gradient(circle at center, rgba(59, 130, 246, 0.15) 0%, transparent 70%); }
.glow-green { background: radial-gradient(circle at center, rgba(16, 185, 129, 0.15) 0%, transparent 70%); }
.glow-purple { background: radial-gradient(circle at center, rgba(168, 85, 247, 0.15) 0%, transparent 70%); }

.payment-method-card:hover .method-glow {
  opacity: 1;
}

.payment-method-card:hover {
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-4px);
}

.payment-method-card.selected {
  background: rgba(249, 115, 22, 0.08);
  border-color: #f97316;
  box-shadow: 0 0 30px rgba(249, 115, 22, 0.15);
}

.method-icon {
  position: relative;
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  transition: transform 0.3s;
}

.payment-method-card:hover .method-icon {
  transform: scale(1.1);
}

.method-card {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.05));
  color: #60a5fa;
}

.method-bank {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.05));
  color: #34d399;
}

.method-mobile {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(168, 85, 247, 0.05));
  color: #a78bfa;
}

.method-name {
  font-size: 13px;
  font-weight: 500;
  color: #d1d5db;
  position: relative;
  z-index: 1;
}

.method-check {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f97316, #ea580c);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  animation: check-pop 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.4);
}

@keyframes check-pop {
  from { transform: scale(0) rotate(-180deg); }
  to { transform: scale(1) rotate(0deg); }
}

/* Summary Box */
.summary-box {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 22px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  font-size: 14px;
  color: #9ca3af;
}

.summary-row.total {
  color: var(--text-primary);
  font-size: 16px;
}

.summary-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  margin: 8px 0;
}

/* Live Rate Box */
.live-rate-box {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.02));
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 18px;
  padding: 24px;
  margin-bottom: 28px;
  text-align: center;
}

.rate-live-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  background: rgba(139, 92, 246, 0.2);
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  color: #a78bfa;
  margin-bottom: 16px;
}

.rate-conversion {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
}

.rate-from {
  font-size: 26px;
  font-weight: 700;
}

.rate-arrow-animated {
  position: relative;
  color: #f97316;
}

.arrow-trail {
  position: absolute;
  width: 20px;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(249, 115, 22, 0.5));
  left: -15px;
  top: 50%;
  transform: translateY(-50%);
  animation: trail-move 1s ease-in-out infinite;
}

@keyframes trail-move {
  0%, 100% { opacity: 0; transform: translateY(-50%) translateX(-5px); }
  50% { opacity: 1; transform: translateY(-50%) translateX(0); }
}

.rate-arrow-animated svg {
  animation: arrow-move 1s ease-in-out infinite;
}

@keyframes arrow-move {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(10px); }
}

.rate-to {
  font-size: 26px;
  font-weight: 700;
  color: #f97316;
}

/* Conversion Calculator */
.conversion-calculator {
  margin-bottom: 24px;
}

.calc-input-group,
.calc-output-group {
  margin-bottom: 8px;
}

.calc-input {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.02);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 0 18px;
  transition: all 0.3s;
}

.calc-input:focus-within {
  border-color: #f97316;
  box-shadow: 0 0 20px rgba(249, 115, 22, 0.1);
}

.input-icon {
  width: 26px;
  height: 26px;
  margin-right: 14px;
}

.calc-input :deep(.n-input-number) {
  flex: 1;
  background: transparent;
}

.calc-input :deep(.n-input) {
  background: transparent;
}

.calc-input :deep(.n-input__input-el) {
  font-size: 26px !important;
  font-weight: 700 !important;
}

.input-currency {
  font-size: 16px;
  font-weight: 600;
  color: #6b7280;
  margin-left: 10px;
}

.input-hint {
  font-size: 12px;
  color: #6b7280;
  margin-top: 8px;
}

.calc-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
  position: relative;
}

.arrow-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(249, 115, 22, 0.1);
  border: 2px solid rgba(249, 115, 22, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.arrow-bounce {
  animation: calc-arrow-bounce 1.5s ease-in-out infinite;
}

@keyframes calc-arrow-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(5px); }
}

.arrow-line {
  position: absolute;
  width: 2px;
  height: 100%;
  background: linear-gradient(180deg, transparent, rgba(249, 115, 22, 0.3), transparent);
}

.calc-output {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1), rgba(249, 115, 22, 0.02));
  border: 2px solid rgba(249, 115, 22, 0.3);
  border-radius: 18px;
  transition: all 0.3s;
}

.calc-output:hover {
  border-color: rgba(249, 115, 22, 0.5);
  box-shadow: 0 10px 30px rgba(249, 115, 22, 0.1);
}

.output-icon {
  animation: output-bounce 2s ease-in-out infinite;
}

@keyframes output-bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.output-value {
  font-size: 36px;
  font-weight: 700;
  color: #f97316;
  text-shadow: 0 0 20px rgba(249, 115, 22, 0.3);
}

.output-currency {
  font-size: 18px;
  color: #fb923c;
}

/* Quick Convert Buttons */
.quick-convert-amounts {
  display: flex;
  gap: 10px;
}

.quick-convert-btn {
  flex: 1;
  padding: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  color: #d1d5db;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-convert-btn:hover {
  border-color: rgba(249, 115, 22, 0.4);
  color: #f97316;
  background: rgba(249, 115, 22, 0.05);
}

.quick-convert-btn.active {
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
}

.pct-value {
  font-size: 15px;
}

/* Success/Error Overlays */
.success-overlay,
.error-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  cursor: pointer;
}

.success-content,
.error-content {
  position: relative;
  text-align: center;
  animation: content-appear 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes content-appear {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.success-rings {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.success-rings span {
  position: absolute;
  width: 100px;
  height: 100px;
  border: 2px solid rgba(16, 185, 129, 0.3);
  border-radius: 50%;
  animation: ring-expand 2s ease-out infinite;
  animation-delay: var(--delay);
  left: 50%;
  top: 50%;
  margin-left: -50px;
  margin-top: -50px;
}

@keyframes ring-expand {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(2); opacity: 0; }
}

.success-icon,
.error-icon {
  position: relative;
  z-index: 1;
  animation: icon-bounce-in 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes icon-bounce-in {
  0% { transform: scale(0) rotate(-180deg); }
  50% { transform: scale(1.2) rotate(10deg); }
  100% { transform: scale(1) rotate(0deg); }
}

.success-confetti {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200px;
  height: 200px;
  margin-left: -100px;
  margin-top: -100px;
  pointer-events: none;
}

.success-confetti span {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #f97316;
  border-radius: 2px;
  animation: confetti-fall 1.5s ease-out forwards;
  animation-delay: calc(var(--i) * 0.1s);
}

.success-confetti span:nth-child(odd) {
  background: #10b981;
}

.success-confetti span:nth-child(3n) {
  background: #a78bfa;
}

@keyframes confetti-fall {
  0% {
    transform: translateY(0) rotate(0deg) scale(1);
    opacity: 1;
  }
  100% {
    transform: translateY(150px) rotate(720deg) scale(0);
    opacity: 0;
  }
}

.success-confetti span:nth-child(1) { left: 50%; top: 50%; }
.success-confetti span:nth-child(2) { left: 30%; top: 40%; }
.success-confetti span:nth-child(3) { left: 70%; top: 40%; }
.success-confetti span:nth-child(4) { left: 20%; top: 60%; }
.success-confetti span:nth-child(5) { left: 80%; top: 60%; }
.success-confetti span:nth-child(6) { left: 40%; top: 30%; }
.success-confetti span:nth-child(7) { left: 60%; top: 30%; }
.success-confetti span:nth-child(8) { left: 25%; top: 50%; }
.success-confetti span:nth-child(9) { left: 75%; top: 50%; }
.success-confetti span:nth-child(10) { left: 35%; top: 70%; }
.success-confetti span:nth-child(11) { left: 65%; top: 70%; }
.success-confetti span:nth-child(12) { left: 50%; top: 25%; }

/* Overlay Transitions */
.success-overlay-enter-active,
.success-overlay-leave-active,
.error-overlay-enter-active,
.error-overlay-leave-active {
  transition: all 0.4s ease;
}

.success-overlay-enter-from,
.success-overlay-leave-to,
.error-overlay-enter-from,
.error-overlay-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .packages-grid {
    grid-template-columns: repeat(6, 160px);
  }

  .payment-methods-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .modal-container {
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    border-radius: 28px 28px 0 0;
    margin-top: auto;
  }

  .tx-stats-row {
    flex-wrap: wrap;
  }

  .quick-amounts {
    flex-wrap: wrap;
  }

  .quick-amount-btn {
    flex: 0 0 calc(50% - 5px);
  }

  .filter-buttons-container {
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 10px;
  }

  .filter-btn {
    flex-shrink: 0;
  }
}
</style>
