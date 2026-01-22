<template>
  <div class="shop-page">
    <!-- Maintenance Check -->
    <MaintenanceOverlay feature="shop" />

    <!-- Subtle Background -->
    <div class="animated-bg">
      <div class="gradient-orbs">
        <div class="orb orb-1"></div>
      </div>
    </div>

    <div class="container-custom py-3 relative z-10">
      <!-- Compact Header -->
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
        <h1 class="text-lg font-bold flex items-center gap-2">
          <Package :size="20" class="text-orange-500" />
          Mağaza
        </h1>

        <!-- Compact Balance Display -->
        <div v-if="user" class="flex items-center gap-3">
          <div class="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded-lg">
            <Banknote :size="16" class="text-green-500" />
            <span class="text-sm font-semibold text-green-500">{{ animatedTlBalance }} TL</span>
          </div>
          <div class="flex items-center gap-2 px-3 py-1.5 bg-orange-500/10 border border-orange-500/30 rounded-lg">
            <Shield :size="16" class="text-orange-500" />
            <span class="text-sm font-semibold text-orange-500">{{ animatedArmorBalance }} Armor</span>
          </div>

          <router-link to="/wallet" class="flex items-center gap-1 px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-sm text-gray-400 hover:text-white hover:border-orange-500 transition-all">
            <Plus :size="14" />
            Yükle
          </router-link>
        </div>
      </div>

      <!-- Payment Method Toggle -->
      <div class="payment-section">
        <div class="payment-toggle-wrapper">
          <div class="payment-toggle">
            <div class="toggle-slider" :class="{ armor: paymentMethod === 'armor' }"></div>
            <button
              class="toggle-btn"
              :class="{ active: paymentMethod === 'tl' }"
              @click="paymentMethod = 'tl'"
            >
              <div class="toggle-icon tl-icon">
                <Banknote :size="20" />
              </div>
              <div class="toggle-content">
                <span class="toggle-label">TL ile Öde</span>
                <span class="toggle-desc">Türk Lirası</span>
              </div>
            </button>
            <button
              class="toggle-btn"
              :class="{ active: paymentMethod === 'armor' }"
              @click="paymentMethod = 'armor'"
            >
              <div class="toggle-icon armor-icon">
                <Shield :size="20" />
              </div>
              <div class="toggle-content">
                <span class="toggle-label">Armor ile Öde</span>
                <span class="toggle-desc">{{ ARMOR_RATE }}x Bonus</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- Game Type Filter -->
      <div class="filter-section">
        <div class="filter-wrapper">
          <button
            v-for="game in gameTypes"
            :key="game.value"
            class="game-filter-btn"
            :class="{ active: selectedGame === game.value }"
            @click="selectedGame = game.value"
          >
            <div class="filter-icon-wrapper" :class="game.value">
              <component :is="game.icon" :size="22" />
            </div>
            <span class="filter-label">{{ game.label }}</span>
            <span class="filter-count" v-if="game.value !== 'all'">
              {{ getGameCount(game.value) }}
            </span>
            <div class="filter-active-indicator"></div>
          </button>
        </div>
      </div>

      <!-- View Toggle -->
      <div class="view-toggle-section">
        <button
          class="view-toggle-btn"
          :class="{ active: viewMode === 'grid' }"
          @click="viewMode = 'grid'"
        >
          <LayoutGrid :size="18" />
          Kart Görünümü
        </button>
        <button
          class="view-toggle-btn"
          :class="{ active: viewMode === 'table' }"
          @click="viewMode = 'table'"
        >
          <Table2 :size="18" />
          Karşılaştırma
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner">
          <Loader2 :size="48" class="spinner-icon" />
        </div>
        <p class="loading-text">Paketler yükleniyor...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">
          <AlertTriangle :size="56" />
        </div>
        <h3>Bir Hata Oluştu</h3>
        <p>{{ error }}</p>
        <button @click="fetchPackages" class="retry-btn">
          <RefreshCw :size="18" />
          Tekrar Dene
        </button>
      </div>

      <!-- Packages Grid View -->
      <div v-else-if="viewMode === 'grid'" class="packages-grid">
        <div
          v-for="(pkg, index) in filteredPackages"
          :key="pkg.id"
          class="package-card"
          :class="{
            featured: pkg.slug.includes('pro'),
            'animate-in': true
          }"
          :style="{ animationDelay: `${index * 100}ms` }"
          @mouseenter="handleCardHover($event, pkg.id)"
          @mouseleave="handleCardLeave"
          @mousemove="handleCardMove"
        >
          <!-- Featured Badge -->
          <div v-if="pkg.slug.includes('pro')" class="featured-badge popular-badge-pulse">
            <Crown :size="14" />
            <span>En Popüler</span>
          </div>

          <!-- Spotlight Effect -->
          <div v-if="pkg.slug.includes('pro')" class="spotlight"></div>

          <!-- Card Glow -->
          <div class="card-glow" :class="pkg.game_type"></div>

          <!-- 3D Tilt Inner -->
          <div class="card-tilt-inner">
            <!-- Package Image -->
            <div class="package-image-wrapper">
              <div class="image-bg" :class="pkg.game_type"></div>
              <img :src="getPackageImage(pkg.slug)" :alt="pkg.name" class="package-img" />
              <div class="image-overlay">
                <div class="game-badge" :class="pkg.game_type">
                  {{ getGameShortLabel(pkg.game_type) }}
                </div>
              </div>
            </div>

            <!-- Card Content -->
            <div class="card-content">
              <!-- Header -->
              <div class="package-header">
                <h3 class="package-name">{{ pkg.name }}</h3>
                <p class="package-tagline">{{ pkg.description }}</p>
              </div>

              <!-- Price Section -->
              <div class="price-section">
                <div class="current-price">
                  <div v-if="paymentMethod === 'tl'" class="price-display tl">
                    <span class="price-amount">{{ formatCurrency(pkg.price_monthly) }}</span>
                    <span class="price-currency">TL</span>
                    <span class="price-period">/ay</span>
                  </div>
                  <div v-else class="price-display armor">
                    <Shield :size="20" class="armor-icon" />
                    <span class="price-amount">{{ formatNumber(Math.floor(pkg.price_monthly * ARMOR_RATE)) }}</span>
                    <span class="price-currency">Armor</span>
                    <span class="price-period">/ay</span>
                  </div>
                </div>
                <div class="original-price" v-if="pkg.original_price && pkg.original_price > pkg.price_monthly">
                  <span class="strikethrough">{{ formatCurrency(pkg.original_price) }} TL</span>
                  <span class="discount-badge">
                    %{{ Math.round((1 - pkg.price_monthly / pkg.original_price) * 100) }} İndirim
                  </span>
                </div>
                <div class="alt-price">
                  <span v-if="paymentMethod === 'tl'">
                    veya {{ formatNumber(Math.floor(pkg.price_monthly * ARMOR_RATE)) }} Armor
                  </span>
                  <span v-else>
                    veya {{ formatCurrency(pkg.price_monthly) }} TL
                  </span>
                </div>
              </div>

              <!-- Specs -->
              <div class="specs-row">
                <div class="spec-item">
                  <Users :size="16" />
                  <span>{{ pkg.slots }} Slot</span>
                </div>
                <div class="spec-item">
                  <Server :size="16" />
                  <span>{{ getGameLabel(pkg.game_type) }}</span>
                </div>
              </div>

              <!-- Features List -->
              <div class="features-list">
                <div
                  v-for="(feature, fIndex) in pkg.features.slice(0, 5)"
                  :key="feature"
                  class="feature-item"
                  :style="{ animationDelay: `${fIndex * 50}ms` }"
                >
                  <div class="feature-check">
                    <Check :size="12" />
                  </div>
                  <span>{{ getFeatureLabel(feature) }}</span>
                </div>
                <div v-if="pkg.features.length > 5" class="more-features">
                  +{{ pkg.features.length - 5 }} daha fazla özellik
                </div>
              </div>

              <!-- Purchase Button -->
              <button class="purchase-btn muzzle-flash-hover recoil-click" @click="selectPackage(pkg)">
                <span class="btn-text">Satın Al</span>
                <ShoppingCart :size="18" />
                <div class="btn-shine"></div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Comparison Table View -->
      <div v-else-if="viewMode === 'table'" class="comparison-table-wrapper">
        <table class="comparison-table">
          <thead>
            <tr>
              <th class="feature-col">Özellikler</th>
              <th
                v-for="pkg in filteredPackages"
                :key="pkg.id"
                class="package-col"
                :class="{ featured: pkg.slug.includes('pro') }"
              >
                <div class="table-pkg-header">
                  <span class="table-pkg-name">{{ pkg.name }}</span>
                  <span class="table-pkg-price">
                    {{ paymentMethod === 'tl' ? formatCurrency(pkg.price_monthly) + ' TL' : formatNumber(Math.floor(pkg.price_monthly * ARMOR_RATE)) + ' Armor' }}
                  </span>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Slot Sayısı</td>
              <td v-for="pkg in filteredPackages" :key="pkg.id + '-slots'">
                <span class="table-value">{{ pkg.slots }}</span>
              </td>
            </tr>
            <tr>
              <td>Oyun Tipi</td>
              <td v-for="pkg in filteredPackages" :key="pkg.id + '-game'">
                <span class="table-value">{{ getGameShortLabel(pkg.game_type) }}</span>
              </td>
            </tr>
            <tr v-for="feature in allFeatures" :key="feature">
              <td>{{ getFeatureLabel(feature) }}</td>
              <td v-for="pkg in filteredPackages" :key="pkg.id + '-' + feature">
                <div v-if="pkg.features.includes(feature)" class="check-icon">
                  <Check :size="18" />
                </div>
                <div v-else class="x-icon">
                  <X :size="18" />
                </div>
              </td>
            </tr>
            <tr class="action-row">
              <td></td>
              <td v-for="pkg in filteredPackages" :key="pkg.id + '-action'">
                <button class="table-purchase-btn" @click="selectPackage(pkg)">
                  Satın Al
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- No Packages State -->
      <div v-if="!loading && !error && filteredPackages.length === 0" class="empty-state">
        <div class="empty-icon">
          <Package :size="64" />
        </div>
        <h3>Paket Bulunamadı</h3>
        <p>Bu kategoride henüz paket bulunmuyor</p>
      </div>

      <!-- Rate Info Card -->
      <div class="rate-info-card">
        <div class="rate-icon">
          <Shield :size="28" />
        </div>
        <div class="rate-content">
          <h4>Armor ile Ödemede Avantaj</h4>
          <p><strong>1 TL = {{ ARMOR_RATE }} Armor</strong> - Armor ile ödeme yaparak ekstra avantajlardan yararlanın</p>
        </div>
        <router-link to="/wallet" class="rate-cta">
          Armor Yükle
          <ArrowRight :size="16" />
        </router-link>
      </div>

      <!-- Testimonials Section -->
      <div class="testimonials-section">
        <div class="section-header">
          <h2>Müşterilerimiz Ne Diyor?</h2>
          <p>Binlerce memnun oyuncunun tercih ettigi sunucular</p>
        </div>
        <div class="testimonials-grid">
          <div v-for="(testimonial, index) in testimonials" :key="index" class="testimonial-card">
            <div class="testimonial-content">
              <div class="stars">
                <Star v-for="s in 5" :key="s" :size="16" class="star-icon" />
              </div>
              <p class="testimonial-text">"{{ testimonial.text }}"</p>
            </div>
            <div class="testimonial-author">
              <div class="author-avatar">{{ testimonial.name.charAt(0) }}</div>
              <div class="author-info">
                <span class="author-name">{{ testimonial.name }}</span>
                <span class="author-role">{{ testimonial.role }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Purchase Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
          <div class="modal-container">
            <!-- Modal Background Effects -->
            <div class="modal-bg-effect"></div>

            <!-- Close Button -->
            <button @click="closeModal" class="modal-close">
              <X :size="20" />
            </button>

            <!-- Step Indicator -->
            <div class="step-indicator">
              <div class="step" :class="{ active: modalStep >= 1, completed: modalStep > 1 }">
                <div class="step-number">
                  <Check v-if="modalStep > 1" :size="14" />
                  <span v-else>1</span>
                </div>
                <span class="step-label">Paket</span>
              </div>
              <div class="step-line" :class="{ active: modalStep > 1 }"></div>
              <div class="step" :class="{ active: modalStep >= 2, completed: modalStep > 2 }">
                <div class="step-number">
                  <Check v-if="modalStep > 2" :size="14" />
                  <span v-else>2</span>
                </div>
                <span class="step-label">Ayarlar</span>
              </div>
              <div class="step-line" :class="{ active: modalStep > 2 }"></div>
              <div class="step" :class="{ active: modalStep >= 3 }">
                <div class="step-number">3</div>
                <span class="step-label">Ödeme</span>
              </div>
            </div>

            <!-- Step 1: Package Info -->
            <div v-if="modalStep === 1" class="modal-step">
              <div class="selected-package-card" v-if="selectedPkg">
                <div class="pkg-visual">
                  <div class="pkg-icon" :class="selectedPkg.game_type">
                    <Gamepad2 :size="32" />
                  </div>
                  <div class="pkg-glow" :class="selectedPkg.game_type"></div>
                </div>
                <div class="pkg-details">
                  <h3>{{ selectedPkg.name }}</h3>
                  <p>{{ selectedPkg.slots }} Slot - {{ getGameLabel(selectedPkg.game_type) }}</p>
                  <div class="pkg-price-tag">
                    <span v-if="paymentMethod === 'tl'">{{ formatCurrency(selectedPkg.price_monthly) }} TL/ay</span>
                    <span v-else>{{ formatNumber(Math.floor(selectedPkg.price_monthly * ARMOR_RATE)) }} Armor/ay</span>
                  </div>
                </div>
              </div>
              <button class="modal-next-btn" @click="modalStep = 2">
                Devam Et
                <ArrowRight :size="18" />
              </button>
            </div>

            <!-- Step 2: Server Settings -->
            <div v-if="modalStep === 2" class="modal-step">
              <!-- Server Name -->
              <div class="form-group">
                <label>
                  <Server :size="16" />
                  Sunucu Adı
                </label>
                <input
                  v-model="serverName"
                  type="text"
                  placeholder="Örnek: My AG Server"
                  class="form-input"
                  :class="{ error: serverName.length > 0 && serverName.length < 3 }"
                />
                <span class="input-hint" v-if="serverName.length > 0 && serverName.length < 3">
                  En az 3 karakter giriniz
                </span>
              </div>

              <!-- Duration Selection with Price Chart -->
              <div class="form-group">
                <label>
                  <Calendar :size="16" />
                  Süre Seçin
                </label>
                <div class="duration-grid">
                  <button
                    v-for="opt in durationOptions"
                    :key="opt.months"
                    class="duration-card"
                    :class="{ active: duration === opt.months, best: opt.months === 12 }"
                    @click="duration = opt.months"
                  >
                    <div class="duration-header">
                      <span class="duration-months">{{ opt.label }}</span>
                      <span v-if="opt.discount" class="duration-save">%{{ opt.discount }} Tasarruf</span>
                    </div>
                    <div class="duration-price" v-if="selectedPkg">
                      <span class="duration-total">
                        {{ paymentMethod === 'tl'
                          ? formatCurrency(calculateDurationPrice(opt.months, opt.discount)) + ' TL'
                          : formatNumber(Math.floor(calculateDurationPrice(opt.months, opt.discount) * ARMOR_RATE)) + ' Armor'
                        }}
                      </span>
                      <span v-if="opt.discount" class="duration-original">
                        {{ paymentMethod === 'tl'
                          ? formatCurrency(selectedPkg.price_monthly * opt.months) + ' TL'
                          : formatNumber(Math.floor(selectedPkg.price_monthly * opt.months * ARMOR_RATE)) + ' Armor'
                        }}
                      </span>
                    </div>
                    <div v-if="opt.months === 12" class="best-badge">
                      <Star :size="12" />
                      En İyi Fiyat
                    </div>
                    <div class="duration-check">
                      <Check :size="16" />
                    </div>
                  </button>
                </div>

                <!-- Visual Price Comparison Chart -->
                <div class="price-chart" v-if="selectedPkg">
                  <div class="chart-title">Fiyat Karşılaştırması</div>
                  <div class="chart-bars">
                    <div
                      v-for="opt in durationOptions"
                      :key="'chart-' + opt.months"
                      class="chart-bar-wrapper"
                      :class="{ active: duration === opt.months }"
                    >
                      <div
                        class="chart-bar"
                        :style="{ height: getBarHeight(opt) + '%' }"
                        :class="{ 'has-discount': opt.discount }"
                      >
                        <span class="bar-label">{{ opt.months }}Ay</span>
                      </div>
                      <span class="bar-price">
                        {{ paymentMethod === 'tl'
                          ? formatCurrency(calculateDurationPrice(opt.months, opt.discount) / opt.months)
                          : formatNumber(Math.floor(calculateDurationPrice(opt.months, opt.discount) * ARMOR_RATE / opt.months))
                        }}
                        <small>/ay</small>
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="modal-nav-btns">
                <button class="modal-back-btn" @click="modalStep = 1">
                  <ArrowLeft :size="18" />
                  Geri
                </button>
                <button
                  class="modal-next-btn"
                  @click="modalStep = 3"
                  :disabled="serverName.trim().length < 3"
                >
                  Devam Et
                  <ArrowRight :size="18" />
                </button>
              </div>
            </div>

            <!-- Step 3: Payment -->
            <div v-if="modalStep === 3" class="modal-step">
              <!-- Order Summary -->
              <div class="order-summary">
                <h4>Siparis Ozeti</h4>
                <div class="summary-item">
                  <span>Paket</span>
                  <span>{{ selectedPkg?.name }}</span>
                </div>
                <div class="summary-item">
                  <span>Sunucu Adı</span>
                  <span>{{ serverName }}</span>
                </div>
                <div class="summary-item">
                  <span>Sure</span>
                  <span>{{ duration }} Ay</span>
                </div>
                <div class="summary-item">
                  <span>Aylık Ücret</span>
                  <span>{{ formatCurrency(selectedPkg?.price_monthly) }} TL</span>
                </div>
                <div v-if="getDiscount() > 0" class="summary-item discount">
                  <span>İndirim (%{{ getDiscount() }})</span>
                  <span>-{{ formatCurrency(getDiscountAmount()) }} TL</span>
                </div>
                <div class="summary-divider"></div>
                <div class="summary-item total">
                  <span>Toplam</span>
                  <span v-if="paymentMethod === 'tl'" class="total-tl">{{ formatCurrency(getTotalPrice()) }} TL</span>
                  <span v-else class="total-armor">{{ formatNumber(getTotalArmor()) }} Armor</span>
                </div>
              </div>

              <!-- Balance Status -->
              <div class="balance-status" :class="{ sufficient: hasEnoughBalance, insufficient: !hasEnoughBalance }">
                <div class="balance-status-icon">
                  <CheckCircle v-if="hasEnoughBalance" :size="24" />
                  <AlertTriangle v-else :size="24" />
                </div>
                <div class="balance-status-content">
                  <span class="balance-status-label">Bakiyeniz</span>
                  <span class="balance-status-amount">
                    {{ paymentMethod === 'tl' ? formatCurrency(user?.balance || 0) + ' TL' : formatNumber(user?.balance_coin || 0) + ' Armor' }}
                  </span>
                </div>
                <div v-if="hasEnoughBalance" class="balance-after">
                  <span>Kalan:</span>
                  <span>
                    {{ paymentMethod === 'tl'
                      ? formatCurrency((user?.balance || 0) - getTotalPrice()) + ' TL'
                      : formatNumber((user?.balance_coin || 0) - getTotalArmor()) + ' Armor'
                    }}
                  </span>
                </div>
              </div>

              <!-- Insufficient Balance Warning -->
              <div v-if="!hasEnoughBalance" class="insufficient-warning">
                <div class="warning-content">
                  <AlertTriangle :size="20" />
                  <div>
                    <h5>Yetersiz Bakiye</h5>
                    <p>
                      {{ paymentMethod === 'tl'
                        ? formatCurrency(getTotalPrice() - (user?.balance || 0)) + ' TL'
                        : formatNumber(getTotalArmor() - (user?.balance_coin || 0)) + ' Armor'
                      }} daha gerekiyor
                    </p>
                  </div>
                </div>
                <router-link to="/wallet" class="warning-cta" @click="closeModal">
                  <Wallet :size="18" />
                  Bakiye Yükle
                  <ArrowRight :size="16" />
                </router-link>
              </div>

              <div class="modal-nav-btns">
                <button class="modal-back-btn" @click="modalStep = 2">
                  <ArrowLeft :size="18" />
                  Geri
                </button>
                <button
                  @click="confirmPurchase"
                  class="modal-confirm-btn"
                  :disabled="!canPurchase || purchasing"
                >
                  <Loader2 v-if="purchasing" :size="18" class="spin" />
                  <template v-else>
                    <ShoppingCart :size="18" />
                    Satın Al
                  </template>
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Success Modal -->
    <Teleport to="body">
      <Transition name="success">
        <div v-if="showSuccessModal" class="success-overlay">
          <div class="success-modal">
            <div class="success-animation">
              <div class="success-circle">
                <Check :size="48" class="success-check" />
              </div>
              <div class="success-rings">
                <div class="ring ring-1"></div>
                <div class="ring ring-2"></div>
                <div class="ring ring-3"></div>
              </div>
              <div class="success-confetti">
                <div v-for="i in 20" :key="'conf-' + i" class="confetti" :style="getConfettiStyle(i)"></div>
              </div>
            </div>
            <h2>Tebrikler!</h2>
            <p>Sunucunuz başarıyla oluşturuldu</p>
            <div class="success-details" v-if="purchaseResult">
              <div class="detail-item">
                <span>Sunucu Adı:</span>
                <strong>{{ purchaseResult.server_info?.name }}</strong>
              </div>
              <div class="detail-item">
                <span>IP Adresi:</span>
                <strong>{{ purchaseResult.server_info?.ip }}</strong>
              </div>
            </div>
            <button class="success-btn" @click="goToDashboard">
              Kontrol Paneline Git
              <ArrowRight :size="18" />
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import MaintenanceOverlay from '@/components/MaintenanceOverlay.vue'
import {
  Banknote,
  Shield,
  Plus,
  Gamepad2,
  Users,
  Server,
  Check,
  ShoppingCart,
  Package,
  Loader2,
  AlertTriangle,
  X,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Crown,
  LayoutGrid,
  Table2,
  RefreshCw,
  Calendar,
  Star,
  CheckCircle,
  Wallet,
  Crosshair,
  Target,
  Zap,
  Cpu,
  Wifi,
  Globe
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

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

// Constants
const ARMOR_RATE = 100

// State
const packages = ref([])
const loading = ref(true)
const error = ref(null)
const selectedGame = ref('all')
const paymentMethod = ref('tl')
const showModal = ref(false)
const selectedPkg = ref(null)
const serverName = ref('')
const duration = ref(1)
const purchasing = ref(false)
const viewMode = ref('grid')
const hoveredPackage = ref(null)
const modalStep = ref(1)
const showSuccessModal = ref(false)
const purchaseResult = ref(null)
const cardTiltX = ref(0)
const cardTiltY = ref(0)

// Animated balance values
const animatedTlBalance = ref(0)
const animatedArmorBalance = ref(0)

// Game types
const gameTypes = [
  { value: 'all', label: 'Tümü', icon: Package },
  { value: 'ag', label: 'Adrenaline Gamer', icon: Gamepad2 },
  { value: 'cs16', label: 'CS 1.6', icon: Crosshair },
  { value: 'hldm', label: 'HLDM', icon: Target }
]

// Duration options
const durationOptions = [
  { months: 1, label: '1 Ay', discount: 0 },
  { months: 3, label: '3 Ay', discount: 10 },
  { months: 6, label: '6 Ay', discount: 15 },
  { months: 12, label: '12 Ay', discount: 20 }
]

// Floating icons for background
const floatingIcons = [Gamepad2, Crosshair, Target, Zap, Cpu, Wifi, Globe, Shield, Server, Users]

// Testimonials
const testimonials = ref([
  {
    name: 'Ahmet Y.',
    role: 'AG Oyuncusu',
    text: 'Harika sunucu performansi ve mukemmel destek. 2 yildir kullaniyorum, hic sorun yasamadim.'
  },
  {
    name: 'Mehmet K.',
    role: 'Klan Lideri',
    text: 'Klanmiz için en iyi seçim oldu. Dusuk ping, yuksek performans. Kesinlikle tavsiye ederim.'
  },
  {
    name: 'Can S.',
    role: 'CS 1.6 Oyuncusu',
    text: 'Armor sistemi sayesinde çok avantajlı fiyatlarla sunucu aldım. Memnuniyet %100.'
  }
])

// Computed
const user = computed(() => authStore.user)

const filteredPackages = computed(() => {
  if (selectedGame.value === 'all') {
    return packages.value
  }
  return packages.value.filter(p => p.game_type === selectedGame.value)
})

const allFeatures = computed(() => {
  const features = new Set()
  packages.value.forEach(pkg => {
    pkg.features.forEach(f => features.add(f))
  })
  return Array.from(features)
})

const hasEnoughBalance = computed(() => {
  if (!user.value || !selectedPkg.value) return false

  if (paymentMethod.value === 'tl') {
    return (user.value.balance || 0) >= getTotalPrice()
  } else {
    return (user.value.balance_coin || 0) >= getTotalArmor()
  }
})

const canPurchase = computed(() => {
  return selectedPkg.value && serverName.value.trim().length >= 3 && hasEnoughBalance.value
})

// Methods - animateValue must be defined before the watch that uses it
const animateValue = (ref, start, end, duration) => {
  const startTime = performance.now()
  const animate = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    ref.value = Math.floor(start + (end - start) * eased)
    if (progress < 1) {
      requestAnimationFrame(animate)
    }
  }
  requestAnimationFrame(animate)
}

// Animate balance on user change
watch(() => user.value, (newUser) => {
  if (newUser) {
    animateValue(animatedTlBalance, 0, newUser.balance || 0, 1000)
    animateValue(animatedArmorBalance, 0, newUser.balance_coin || 0, 1000)
  }
}, { immediate: true })

const formatCurrency = (val) => {
  return new Intl.NumberFormat('tr-TR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(val || 0)
}

const formatNumber = (val) => {
  return new Intl.NumberFormat('tr-TR').format(val || 0)
}

const getPackageImage = (slug) => {
  const images = {
    halflife: '/static/images/packages/hlpaket.png',
    halflife_ag: '/static/images/packages/hlagpaket.png',
    cs16_pro: '/static/images/packages/cspropublicpaket.png',
    cs16_fun: '/static/images/packages/cszombiefunpaket.png'
  }
  return images[slug] || '/static/images/packages/hlpaket.png'
}

const getGameLabel = (type) => {
  const labels = {
    ag: 'Adrenaline Gamer',
    cs16: 'Counter-Strike 1.6',
    hldm: 'Half-Life Deathmatch'
  }
  return labels[type] || type
}

const getGameShortLabel = (type) => {
  const labels = {
    ag: 'AG',
    cs16: 'CS 1.6',
    hldm: 'HLDM'
  }
  return labels[type] || type
}

const getFeatureLabel = (feature) => {
  const labels = {
    basic_plugins: 'Temel Pluginler',
    fun_plugins: 'Fun Pluginler',
    zombie_mod: 'Zombie Mod',
    rcon_access: 'RCON Erisimi',
    anticheat: 'Anti-Cheat',
    amvp: 'AMVP Sistemi',
    statsme: 'StatsMe',
    custom_domain: 'Özel Domain',
    priority_support: 'Oncelikli Destek',
    ddos_protection: 'DDoS Koruma',
    '247_support': '7/24 Destek',
    auto_backup: 'Otomatik Yedekleme'
  }
  return labels[feature] || feature
}

const getGameCount = (gameType) => {
  return packages.value.filter(p => p.game_type === gameType).length
}

const getDiscount = () => {
  const opt = durationOptions.find(o => o.months === duration.value)
  return opt?.discount || 0
}

const getDiscountAmount = () => {
  if (!selectedPkg.value) return 0
  const base = selectedPkg.value.price_monthly * duration.value
  return base * (getDiscount() / 100)
}

const getTotalPrice = () => {
  if (!selectedPkg.value) return 0
  const base = selectedPkg.value.price_monthly * duration.value
  return base - getDiscountAmount()
}

const getTotalArmor = () => {
  return Math.floor(getTotalPrice() * ARMOR_RATE)
}

const calculateDurationPrice = (months, discount) => {
  if (!selectedPkg.value) return 0
  const base = selectedPkg.value.price_monthly * months
  return base - (base * (discount / 100))
}

const getBarHeight = (opt) => {
  if (!selectedPkg.value) return 0
  const maxPrice = selectedPkg.value.price_monthly
  const pricePerMonth = calculateDurationPrice(opt.months, opt.discount) / opt.months
  return (pricePerMonth / maxPrice) * 100
}

const getParticleStyle = (i) => {
  const x = Math.random() * 100
  const y = Math.random() * 100
  const size = 2 + Math.random() * 4
  const dur = 15 + Math.random() * 25
  const delay = Math.random() * 10
  return {
    left: `${x}%`,
    top: `${y}%`,
    width: `${size}px`,
    height: `${size}px`,
    animationDuration: `${dur}s`,
    animationDelay: `-${delay}s`
  }
}

const getFloatingIconStyle = (i) => {
  const x = 5 + (i * 8) % 90
  const y = 10 + Math.random() * 80
  const dur = 20 + Math.random() * 20
  const delay = Math.random() * 10
  return {
    left: `${x}%`,
    top: `${y}%`,
    animationDuration: `${dur}s`,
    animationDelay: `-${delay}s`,
    opacity: 0.05 + Math.random() * 0.1
  }
}

const getFloatingIcon = (i) => {
  return floatingIcons[i % floatingIcons.length]
}

const getConfettiStyle = (i) => {
  const colors = ['#f97316', '#10b981', '#3b82f6', '#ec4899', '#8b5cf6']
  return {
    left: `${10 + Math.random() * 80}%`,
    backgroundColor: colors[i % colors.length],
    animationDelay: `${Math.random() * 0.5}s`,
    animationDuration: `${1 + Math.random()}s`
  }
}

// 3D Card Tilt handlers
const handleCardHover = (e, pkgId) => {
  hoveredPackage.value = pkgId
}

const handleCardLeave = () => {
  hoveredPackage.value = null
  cardTiltX.value = 0
  cardTiltY.value = 0
}

const handleCardMove = (e) => {
  if (!hoveredPackage.value) return
  const card = e.currentTarget
  const rect = card.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const centerX = rect.width / 2
  const centerY = rect.height / 2
  cardTiltX.value = (y - centerY) / 20
  cardTiltY.value = (centerX - x) / 20
}

const selectPackage = (pkg) => {
  if (!user.value) {
    router.push('/login')
    return
  }
  selectedPkg.value = pkg
  serverName.value = ''
  duration.value = 1
  modalStep.value = 1
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  modalStep.value = 1
}

const fetchPackages = async () => {
  loading.value = true
  error.value = null

  try {
    const res = await fetch('/api/servers/packages')
    if (!res.ok) throw new Error('Paketler yüklenemedi')

    const data = await res.json()
    packages.value = data.packages || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const confirmPurchase = async () => {
  if (!canPurchase.value || purchasing.value) return

  purchasing.value = true

  try {
    const res = await fetch('/api/servers/order/package-wallet', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        package_id: selectedPkg.value.id,
        months: duration.value,
        server_name: serverName.value.trim(),
        auto_renew: false,
        payment_type: paymentMethod.value
      })
    })

    const data = await res.json()

    if (res.ok) {
      purchaseResult.value = data.order
      showModal.value = false
      showSuccessModal.value = true
      await authStore.fetchUser()
    } else {
      alert(data.detail || 'Satin alma başarısız')
    }
  } catch (e) {
    alert('Bir hata oluştu: ' + e.message)
  } finally {
    purchasing.value = false
  }
}

const goToDashboard = () => {
  showSuccessModal.value = false
  router.push('/dashboard')
}

onMounted(() => {
  fetchPackages()
})
</script>

<style scoped>
/* ============================================
   SHOP PAGE - MODERN GAMING UI
   ============================================ */

.shop-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

/* ============================================
   ANIMATED BACKGROUND
   ============================================ */

.animated-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

/* Grid Lines */
.grid-lines {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(249, 115, 22, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(249, 115, 22, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: grid-move 20s linear infinite;
}

@keyframes grid-move {
  0% { transform: translate(0, 0); }
  100% { transform: translate(50px, 50px); }
}

/* Particles */
.particles {
  position: absolute;
  inset: 0;
}

.particle {
  position: absolute;
  background: #f97316;
  border-radius: 50%;
  opacity: 0.3;
  animation: float-particle linear infinite;
}

@keyframes float-particle {
  0%, 100% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  10% {
    opacity: 0.3;
  }
  90% {
    opacity: 0.3;
  }
  100% {
    transform: translateY(-100vh) translateX(50px);
    opacity: 0;
  }
}

/* Floating Icons */
.floating-icons {
  position: absolute;
  inset: 0;
}

.floating-icon {
  position: absolute;
  color: #f97316;
  animation: float-icon ease-in-out infinite;
}

@keyframes float-icon {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-30px) rotate(10deg);
  }
}

/* Gradient Orbs */
.gradient-orbs {
  position: absolute;
  inset: 0;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.15;
}

.orb-1 {
  width: 600px;
  height: 600px;
  background: #f97316;
  top: -200px;
  right: -200px;
  animation: pulse-orb 8s ease-in-out infinite;
}

.orb-2 {
  width: 500px;
  height: 500px;
  background: #3b82f6;
  bottom: -150px;
  left: -150px;
  animation: pulse-orb 10s ease-in-out infinite reverse;
}

.orb-3 {
  width: 400px;
  height: 400px;
  background: #10b981;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: pulse-orb 12s ease-in-out infinite;
}

@keyframes pulse-orb {
  0%, 100% {
    transform: scale(1);
    opacity: 0.15;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.25;
  }
}

/* ============================================
   HERO SECTION
   ============================================ */

.hero-section {
  text-align: center;
  padding: 40px 0 60px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  background: rgba(249, 115, 22, 0.15);
  border: 1px solid rgba(249, 115, 22, 0.3);
  border-radius: 30px;
  color: #f97316;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 24px;
  animation: badge-glow 2s ease-in-out infinite;
}

@keyframes badge-glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(249, 115, 22, 0.2);
  }
  50% {
    box-shadow: 0 0 30px rgba(249, 115, 22, 0.4);
  }
}

.hero-title {
  font-size: 56px;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 20px;
}

.title-line {
  display: block;
}

.title-line.gradient {
  background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #f97316 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradient-shift 3s ease-in-out infinite;
}

@keyframes gradient-shift {
  0%, 100% {
    background-position: 0% center;
  }
  50% {
    background-position: 100% center;
  }
}

.hero-subtitle {
  font-size: 18px;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto 40px;
  line-height: 1.6;
}

/* ============================================
   BALANCE CARDS
   ============================================ */

.balance-cards {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.balance-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 28px;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.balance-card:hover {
  transform: translateY(-4px);
}

.balance-card-bg {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
}

.balance-card-content {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 1;
}

.balance-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tl-card .balance-icon {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.armor-card .balance-icon {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white;
}

.balance-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.balance-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.balance-amount {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.balance-amount .counter {
  font-variant-numeric: tabular-nums;
}

.balance-amount .currency {
  font-size: 14px;
  margin-left: 4px;
  opacity: 0.7;
}

.balance-amount.armor {
  color: #f97316;
}

.balance-glow {
  position: absolute;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.3;
  top: 50%;
  right: -50px;
  transform: translateY(-50%);
}

.balance-glow.tl {
  background: #10b981;
}

.balance-glow.armor {
  background: #f97316;
}

/* Add Balance Card */
.add-card {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1), rgba(249, 115, 22, 0.05));
  border: 2px dashed rgba(249, 115, 22, 0.3);
  text-decoration: none;
  cursor: pointer;
}

.add-card:hover {
  border-style: solid;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(249, 115, 22, 0.1));
}

.add-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: rgba(249, 115, 22, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f97316;
}

.add-text {
  font-weight: 600;
  color: #f97316;
}

.add-arrow {
  color: #f97316;
  transition: transform 0.3s;
}

.add-card:hover .add-arrow {
  transform: translateX(4px);
}

/* ============================================
   PAYMENT TOGGLE
   ============================================ */

.payment-section {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
}

.payment-toggle-wrapper {
  position: relative;
}

.payment-toggle {
  position: relative;
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 6px;
}

.toggle-slider {
  position: absolute;
  top: 6px;
  left: 6px;
  width: calc(50% - 6px);
  height: calc(100% - 12px);
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 16px;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 20px rgba(249, 115, 22, 0.4);
}

.toggle-slider.armor {
  transform: translateX(100%);
}

.toggle-btn {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 32px;
  background: transparent;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  z-index: 1;
  transition: all 0.3s;
}

.toggle-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.toggle-btn:not(.active) .toggle-icon {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
}

.toggle-btn.active .toggle-icon {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.toggle-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.toggle-label {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-secondary);
  transition: color 0.3s;
}

.toggle-desc {
  font-size: 11px;
  color: var(--text-muted);
  transition: color 0.3s;
}

.toggle-btn.active .toggle-label {
  color: white;
}

.toggle-btn.active .toggle-desc {
  color: rgba(255, 255, 255, 0.8);
}

/* ============================================
   GAME FILTER
   ============================================ */

.filter-section {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.filter-wrapper {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.game-filter-btn {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 24px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
}

.game-filter-btn:hover {
  border-color: rgba(249, 115, 22, 0.5);
  transform: translateY(-2px);
}

.game-filter-btn:hover .filter-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.game-filter-btn.active {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(249, 115, 22, 0.1));
  border-color: #f97316;
  color: #f97316;
}

.filter-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  transition: all 0.3s;
}

.game-filter-btn.active .filter-icon-wrapper {
  background: #f97316;
  color: white;
  animation: icon-bounce 0.5s ease;
}

@keyframes icon-bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.filter-icon-wrapper.ag { color: #f97316; }
.filter-icon-wrapper.cs16 { color: #3b82f6; }
.filter-icon-wrapper.hldm { color: #10b981; }

.filter-count {
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.game-filter-btn.active .filter-count {
  background: rgba(249, 115, 22, 0.3);
}

.filter-active-indicator {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 3px;
  background: #f97316;
  border-radius: 3px 3px 0 0;
  transition: width 0.3s;
}

.game-filter-btn.active .filter-active-indicator {
  width: 60%;
}

/* ============================================
   VIEW TOGGLE
   ============================================ */

.view-toggle-section {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 32px;
}

.view-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.view-toggle-btn:hover {
  border-color: rgba(249, 115, 22, 0.5);
}

.view-toggle-btn.active {
  background: rgba(249, 115, 22, 0.15);
  border-color: #f97316;
  color: #f97316;
}

/* ============================================
   LOADING & ERROR STATES
   ============================================ */

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
}

.loading-spinner {
  margin-bottom: 20px;
}

.spinner-icon {
  color: #f97316;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: var(--text-secondary);
  font-size: 16px;
}

.error-state {
  text-align: center;
  padding: 80px 0;
}

.error-icon {
  margin-bottom: 20px;
  color: #ef4444;
}

.error-state h3 {
  font-size: 24px;
  margin-bottom: 12px;
}

.error-state p {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.retry-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border: none;
  border-radius: 12px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(249, 115, 22, 0.4);
}

/* ============================================
   PACKAGES GRID
   ============================================ */

.packages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 28px;
  margin-bottom: 48px;
}

/* ============================================
   PACKAGE CARD - GLASSMORPHISM + 3D
   ============================================ */

.package-card {
  position: relative;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d;
  perspective: 1000px;
  opacity: 0;
  animation: card-appear 0.6s ease forwards;
}

@keyframes card-appear {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.package-card:hover {
  transform: translateY(-12px) rotateX(2deg) rotateY(-2deg);
  border-color: rgba(249, 115, 22, 0.4);
  box-shadow:
    0 25px 50px rgba(0, 0, 0, 0.4),
    0 0 50px rgba(249, 115, 22, 0.1);
}

.package-card.featured {
  border-color: rgba(249, 115, 22, 0.5);
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.08), rgba(249, 115, 22, 0.02));
}

.card-tilt-inner {
  transform-style: preserve-3d;
  transition: transform 0.1s ease-out;
}

/* Card Glow Effect */
.card-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  opacity: 0;
  transition: opacity 0.4s;
  pointer-events: none;
}

.package-card:hover .card-glow {
  opacity: 1;
}

.card-glow.ag {
  background: radial-gradient(circle at center, rgba(249, 115, 22, 0.15) 0%, transparent 50%);
}

.card-glow.cs16 {
  background: radial-gradient(circle at center, rgba(59, 130, 246, 0.15) 0%, transparent 50%);
}

.card-glow.hldm {
  background: radial-gradient(circle at center, rgba(16, 185, 129, 0.15) 0%, transparent 50%);
}

/* Featured Badge */
.featured-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 20px;
  color: white;
  font-size: 12px;
  font-weight: 600;
  z-index: 10;
  animation: badge-pulse 2s ease-in-out infinite;
}

@keyframes badge-pulse {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4);
  }
  50% {
    box-shadow: 0 4px 25px rgba(249, 115, 22, 0.6);
  }
}

/* Spotlight Effect for Featured */
.spotlight {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(180deg, rgba(249, 115, 22, 0.15) 0%, transparent 100%);
  pointer-events: none;
  animation: spotlight-pulse 3s ease-in-out infinite;
}

@keyframes spotlight-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Package Image */
.package-image-wrapper {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.image-bg {
  position: absolute;
  inset: 0;
  opacity: 0.3;
}

.image-bg.ag {
  background: linear-gradient(135deg, #f97316 0%, #1a1a1a 100%);
}

.image-bg.cs16 {
  background: linear-gradient(135deg, #3b82f6 0%, #1a1a1a 100%);
}

.image-bg.hldm {
  background: linear-gradient(135deg, #10b981 0%, #1a1a1a 100%);
}

.package-img {
  position: relative;
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 20px;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1;
}

.package-card:hover .package-img {
  transform: scale(1.08) translateY(-5px);
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: linear-gradient(0deg, rgba(0,0,0,0.8) 0%, transparent 100%);
  z-index: 2;
}

.game-badge {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.game-badge.ag {
  background: rgba(249, 115, 22, 0.3);
  color: #fb923c;
}

.game-badge.cs16 {
  background: rgba(59, 130, 246, 0.3);
  color: #60a5fa;
}

.game-badge.hldm {
  background: rgba(16, 185, 129, 0.3);
  color: #34d399;
}

/* Card Content */
.card-content {
  padding: 24px;
}

.package-header {
  margin-bottom: 20px;
}

.package-name {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 6px;
  color: var(--text-primary);
}

.package-tagline {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* Price Section */
.price-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.current-price {
  margin-bottom: 8px;
}

.price-display {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.price-display.armor {
  align-items: center;
}

.price-display .armor-icon {
  color: #f97316;
}

.price-amount {
  font-size: 36px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1;
}

.price-display.armor .price-amount {
  color: #f97316;
}

.price-currency {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-secondary);
}

.price-period {
  font-size: 14px;
  color: var(--text-muted);
}

.original-price {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.strikethrough {
  font-size: 14px;
  color: var(--text-muted);
  text-decoration: line-through;
}

.discount-badge {
  padding: 4px 10px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1));
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 20px;
  color: #10b981;
  font-size: 11px;
  font-weight: 700;
}

.alt-price {
  font-size: 12px;
  color: var(--text-muted);
}

/* Specs Row */
.specs-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.spec-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  font-size: 13px;
  color: var(--text-secondary);
}

.spec-item svg {
  color: #f97316;
}

/* Features List */
.features-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 24px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-secondary);
  opacity: 0;
  animation: feature-appear 0.4s ease forwards;
}

.package-card:hover .feature-item {
  animation-play-state: running;
}

@keyframes feature-appear {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.feature-check {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  background: rgba(16, 185, 129, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #10b981;
  flex-shrink: 0;
}

.more-features {
  font-size: 12px;
  color: #f97316;
  font-weight: 500;
  padding-left: 30px;
}

/* Purchase Button */
.purchase-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border: none;
  border-radius: 14px;
  color: white;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
}

.purchase-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(249, 115, 22, 0.4);
}

.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.5s;
}

.purchase-btn:hover .btn-shine {
  left: 100%;
}

/* ============================================
   COMPARISON TABLE
   ============================================ */

.comparison-table-wrapper {
  overflow-x: auto;
  margin-bottom: 48px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.comparison-table th,
.comparison-table td {
  padding: 16px 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.comparison-table th {
  background: rgba(0, 0, 0, 0.2);
  font-weight: 600;
}

.comparison-table th.featured {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(249, 115, 22, 0.1));
}

.feature-col {
  text-align: left !important;
  width: 200px;
}

.table-pkg-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.table-pkg-name {
  font-size: 16px;
  font-weight: 700;
}

.table-pkg-price {
  font-size: 14px;
  color: #f97316;
}

.table-value {
  font-weight: 600;
}

.check-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: rgba(16, 185, 129, 0.15);
  border-radius: 50%;
  color: #10b981;
}

.x-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 50%;
  color: #ef4444;
  opacity: 0.5;
}

.action-row td {
  padding-top: 24px;
  padding-bottom: 24px;
}

.table-purchase-btn {
  padding: 12px 28px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.table-purchase-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(249, 115, 22, 0.4);
}

/* ============================================
   EMPTY STATE
   ============================================ */

.empty-state {
  text-align: center;
  padding: 80px 0;
}

.empty-icon {
  margin-bottom: 20px;
  color: var(--text-muted);
  opacity: 0.3;
}

.empty-state h3 {
  font-size: 24px;
  margin-bottom: 8px;
}

.empty-state p {
  color: var(--text-secondary);
}

/* ============================================
   RATE INFO CARD
   ============================================ */

.rate-info-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px 32px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1), rgba(249, 115, 22, 0.05));
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 20px;
  margin-top: 32px;
}

.rate-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.rate-content {
  flex: 1;
}

.rate-content h4 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
  color: #f97316;
}

.rate-content p {
  font-size: 14px;
  color: var(--text-secondary);
}

.rate-cta {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #f97316;
  border-radius: 12px;
  color: white;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
}

.rate-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(249, 115, 22, 0.4);
}

/* ============================================
   TESTIMONIALS SECTION
   ============================================ */

.testimonials-section {
  margin-top: 80px;
  padding-top: 60px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.section-header h2 {
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #f97316, #fb923c);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.section-header p {
  font-size: 16px;
  color: var(--text-secondary);
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.testimonial-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 28px;
  transition: all 0.3s;
}

.testimonial-card:hover {
  transform: translateY(-4px);
  border-color: rgba(249, 115, 22, 0.3);
}

.testimonial-content {
  margin-bottom: 20px;
}

.stars {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
}

.star-icon {
  color: #f97316;
  fill: #f97316;
}

.testimonial-text {
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.7;
  font-style: italic;
}

.testimonial-author {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.author-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 18px;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.author-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
}

.author-role {
  font-size: 12px;
  color: var(--text-muted);
}

/* ============================================
   MODAL STYLES
   ============================================ */

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  position: relative;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
  background: linear-gradient(180deg, rgba(30, 30, 35, 0.98), rgba(20, 20, 25, 0.98));
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 28px;
  padding: 32px;
}

.modal-bg-effect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(180deg, rgba(249, 115, 22, 0.1), transparent);
  pointer-events: none;
}

.modal-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 10;
}

.modal-close:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* Step Indicator */
.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin-bottom: 32px;
  position: relative;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  color: var(--text-secondary);
  transition: all 0.3s;
}

.step.active .step-number {
  background: #f97316;
  border-color: #f97316;
  color: white;
}

.step.completed .step-number {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

.step-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.step.active .step-label,
.step.completed .step-label {
  color: var(--text-primary);
}

.step-line {
  width: 60px;
  height: 2px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0 8px;
  margin-bottom: 24px;
  transition: background 0.3s;
}

.step-line.active {
  background: #f97316;
}

/* Modal Steps */
.modal-step {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Selected Package Card */
.selected-package-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
}

.pkg-visual {
  position: relative;
}

.pkg-icon {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  position: relative;
  z-index: 1;
}

.pkg-icon.ag { background: linear-gradient(135deg, #f97316, #ea580c); }
.pkg-icon.cs16 { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.pkg-icon.hldm { background: linear-gradient(135deg, #10b981, #059669); }

.pkg-glow {
  position: absolute;
  inset: -10px;
  border-radius: 24px;
  filter: blur(20px);
  opacity: 0.4;
}

.pkg-glow.ag { background: #f97316; }
.pkg-glow.cs16 { background: #3b82f6; }
.pkg-glow.hldm { background: #10b981; }

.pkg-details h3 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
}

.pkg-details p {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.pkg-price-tag {
  display: inline-block;
  padding: 6px 14px;
  background: rgba(249, 115, 22, 0.15);
  border-radius: 20px;
  color: #f97316;
  font-size: 14px;
  font-weight: 600;
}

/* Form Styles */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-input {
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  color: var(--text-primary);
  font-size: 15px;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.05);
}

.form-input.error {
  border-color: #ef4444;
}

.input-hint {
  font-size: 12px;
  color: #ef4444;
}

/* Duration Grid */
.duration-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.duration-card {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  cursor: pointer;
  text-align: left;
  transition: all 0.3s;
}

.duration-card:hover {
  border-color: rgba(249, 115, 22, 0.5);
  background: rgba(249, 115, 22, 0.05);
}

.duration-card.active {
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.1);
}

.duration-card.best {
  border-color: rgba(16, 185, 129, 0.5);
}

.duration-card.best.active {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.duration-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.duration-months {
  font-weight: 700;
  font-size: 15px;
}

.duration-save {
  font-size: 11px;
  color: #10b981;
  font-weight: 600;
}

.duration-price {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.duration-total {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.duration-original {
  font-size: 12px;
  color: var(--text-muted);
  text-decoration: line-through;
}

.best-badge {
  position: absolute;
  top: -8px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 12px;
  color: white;
  font-size: 10px;
  font-weight: 700;
}

.duration-check {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #f97316;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transform: scale(0);
  transition: all 0.3s;
}

.duration-card.active .duration-check {
  opacity: 1;
  transform: scale(1);
}

/* Price Comparison Chart */
.price-chart {
  margin-top: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
}

.chart-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 16px;
  text-align: center;
}

.chart-bars {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 120px;
  padding-top: 20px;
}

.chart-bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.chart-bar {
  width: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px 8px 0 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 8px;
  transition: all 0.3s;
  min-height: 30px;
}

.chart-bar.has-discount {
  background: linear-gradient(180deg, #10b981, rgba(16, 185, 129, 0.3));
}

.chart-bar-wrapper.active .chart-bar {
  background: linear-gradient(180deg, #f97316, rgba(249, 115, 22, 0.3));
}

.bar-label {
  font-size: 10px;
  font-weight: 600;
  color: white;
}

.bar-price {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-align: center;
}

.bar-price small {
  font-size: 10px;
  opacity: 0.7;
}

/* Order Summary */
.order-summary {
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
}

.order-summary h4 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 16px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.summary-item.discount {
  color: #10b981;
}

.summary-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 8px 0;
}

.summary-item.total {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  padding-top: 16px;
}

.total-tl {
  color: #10b981;
}

.total-armor {
  color: #f97316;
}

/* Balance Status */
.balance-status {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 16px;
  transition: all 0.3s;
}

.balance-status.sufficient {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.balance-status.insufficient {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.balance-status-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.balance-status.sufficient .balance-status-icon {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.balance-status.insufficient .balance-status-icon {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.balance-status-content {
  flex: 1;
}

.balance-status-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 2px;
}

.balance-status-amount {
  font-size: 18px;
  font-weight: 700;
}

.balance-status.sufficient .balance-status-amount {
  color: #10b981;
}

.balance-status.insufficient .balance-status-amount {
  color: #ef4444;
}

.balance-after {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-size: 12px;
  color: var(--text-secondary);
}

.balance-after span:last-child {
  font-weight: 600;
  color: #10b981;
}

/* Insufficient Warning */
.insufficient-warning {
  padding: 20px;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(249, 115, 22, 0.1));
  border: 2px solid transparent;
  border-image: linear-gradient(135deg, #ef4444, #f97316) 1;
  border-radius: 16px;
  position: relative;
  overflow: hidden;
}

.insufficient-warning::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.05), rgba(249, 115, 22, 0.05));
  border-radius: 16px;
}

.warning-content {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
  color: #f59e0b;
}

.warning-content h5 {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 4px;
}

.warning-content p {
  font-size: 13px;
  opacity: 0.9;
}

.warning-cta {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 12px;
  color: white;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
}

.warning-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(249, 115, 22, 0.4);
}

/* Modal Navigation Buttons */
.modal-nav-btns {
  display: flex;
  gap: 12px;
}

.modal-back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  color: var(--text-secondary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-back-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.modal-next-btn,
.modal-confirm-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex: 1;
  padding: 14px 24px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border: none;
  border-radius: 14px;
  color: white;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-next-btn:hover,
.modal-confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(249, 115, 22, 0.4);
}

.modal-next-btn:disabled,
.modal-confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.spin {
  animation: spin 1s linear infinite;
}

/* Modal Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9) translateY(20px);
  opacity: 0;
}

/* ============================================
   SUCCESS MODAL
   ============================================ */

.success-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
}

.success-modal {
  text-align: center;
  padding: 48px;
  background: linear-gradient(180deg, rgba(30, 30, 35, 0.98), rgba(20, 20, 25, 0.98));
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 32px;
  max-width: 400px;
  width: 90%;
}

.success-animation {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 32px;
}

.success-circle {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  animation: success-pop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes success-pop {
  0% {
    transform: scale(0);
  }
  100% {
    transform: scale(1);
  }
}

.success-check {
  color: white;
  animation: check-draw 0.5s ease 0.3s both;
}

@keyframes check-draw {
  0% {
    opacity: 0;
    transform: scale(0);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.success-rings {
  position: absolute;
  inset: 0;
}

.ring {
  position: absolute;
  inset: 0;
  border: 2px solid #10b981;
  border-radius: 50%;
  opacity: 0;
  animation: ring-expand 1s ease-out forwards;
}

.ring-1 { animation-delay: 0.2s; }
.ring-2 { animation-delay: 0.4s; }
.ring-3 { animation-delay: 0.6s; }

@keyframes ring-expand {
  0% {
    transform: scale(1);
    opacity: 0.5;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

.success-confetti {
  position: absolute;
  inset: -50px;
  pointer-events: none;
}

.confetti {
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  animation: confetti-fall 1.5s ease-out forwards;
}

@keyframes confetti-fall {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(150px) rotate(720deg);
    opacity: 0;
  }
}

.success-modal h2 {
  font-size: 28px;
  font-weight: 800;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #10b981, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.success-modal > p {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.success-details {
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  margin-bottom: 24px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.detail-item strong {
  color: var(--text-primary);
}

.success-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border: none;
  border-radius: 14px;
  color: white;
  font-weight: 700;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.success-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(249, 115, 22, 0.4);
}

/* Success Transition */
.success-enter-active,
.success-leave-active {
  transition: all 0.4s ease;
}

.success-enter-from,
.success-leave-to {
  opacity: 0;
}

.success-enter-from .success-modal,
.success-leave-to .success-modal {
  transform: scale(0.8);
  opacity: 0;
}

/* ============================================
   RESPONSIVE
   ============================================ */

@media (max-width: 768px) {
  .hero-title {
    font-size: 36px;
  }

  .hero-subtitle {
    font-size: 15px;
  }

  .balance-cards {
    flex-direction: column;
    align-items: stretch;
  }

  .balance-card {
    width: 100%;
  }

  .payment-toggle {
    flex-direction: column;
  }

  .toggle-slider {
    width: calc(100% - 12px);
    height: calc(50% - 6px);
  }

  .toggle-slider.armor {
    transform: translateY(100%);
  }

  .filter-wrapper {
    flex-direction: column;
    align-items: stretch;
  }

  .game-filter-btn {
    width: 100%;
  }

  .packages-grid {
    grid-template-columns: 1fr;
  }

  .duration-grid {
    grid-template-columns: 1fr;
  }

  .rate-info-card {
    flex-direction: column;
    text-align: center;
  }

  .rate-cta {
    width: 100%;
    justify-content: center;
  }

  .testimonials-grid {
    grid-template-columns: 1fr;
  }
}
</style>
