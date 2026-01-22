<template>
  <div class="min-h-screen profile-page">
    <!-- Hero Section with Gradient & Pattern -->
    <div class="hero-section">
      <div class="hero-gradient"></div>
      <div class="hero-pattern"></div>
      <div class="hero-glow"></div>

      <!-- Cover Photo Edit -->
      <n-button
        circle
        size="small"
        class="cover-edit-btn"
        @click="showCoverUpload = true"
      >
        <template #icon><ImageIcon class="w-4 h-4" /></template>
      </n-button>
    </div>

    <div class="container-custom relative -mt-24 pb-6">
      <!-- Profile Header Card -->
      <div class="glass-card-hero rounded-2xl p-6 mb-6">
        <div class="flex flex-col lg:flex-row items-start lg:items-center gap-8">
          <!-- Animated Avatar with Online Status Ring -->
          <div class="relative group">
            <div class="avatar-container">
              <div class="avatar-ring-animated">
                <div class="avatar-ring-inner">
                  <n-avatar
                    round
                    :size="150"
                    :src="user?.avatar || '/default-avatar.png'"
                    class="avatar-main"
                  />
                </div>
              </div>
              <!-- Online Status Ring Indicator -->
              <div class="status-ring" :class="statusClass">
                <div class="status-dot"></div>
              </div>
            </div>

            <!-- Avatar Edit Button -->
            <n-button
              circle
              size="small"
              type="primary"
              class="avatar-edit-btn"
              @click="showAvatarUpload = true"
            >
              <template #icon><CameraIcon class="w-4 h-4" /></template>
            </n-button>

            <!-- Level Badge -->
            <div class="level-badge-floating floating-weapon">
              <ZapIcon class="w-4 h-4" />
              <span>{{ userLevel }}</span>
            </div>
          </div>

          <!-- User Info Section -->
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-3 mb-3">
              <h1 class="text-3xl md:text-4xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                {{ user?.username }}
              </h1>

              <!-- Verification Badge -->
              <div v-if="user?.verified" class="verification-badge">
                <CheckCircleIcon class="w-4 h-4" />
                <span>Doğrulanmış</span>
              </div>

              <!-- Role Badge -->
              <div class="role-badge" :style="getRoleBadgeStyle(userRank)">
                <CrownIcon class="w-3.5 h-3.5" />
                <span>{{ userRank }}</span>
              </div>
            </div>

            <p class="text-gray-400 mb-5 flex items-center gap-2">
              <MailIcon class="w-4 h-4" />
              {{ user?.email || 'E-posta eklenmemiş' }}
            </p>

            <!-- User Stats Row with Icons -->
            <div class="stats-row">
              <div class="stat-card">
                <div class="stat-icon stat-icon-orange">
                  <ServerIcon class="w-5 h-5" />
                </div>
                <div class="stat-content">
                  <span class="stat-value">{{ user?.servers_count || 0 }}</span>
                  <span class="stat-label">Sunucu</span>
                </div>
              </div>

              <div class="stat-card">
                <div class="stat-icon stat-icon-blue">
                  <MessageSquareIcon class="w-5 h-5" />
                </div>
                <div class="stat-content">
                  <span class="stat-value">{{ user?.forum_posts || 0 }}</span>
                  <span class="stat-label">Forum Gönderi</span>
                </div>
              </div>

              <div class="stat-card">
                <div class="stat-icon stat-icon-green">
                  <CalendarIcon class="w-5 h-5" />
                </div>
                <div class="stat-content">
                  <span class="stat-value">{{ formatMemberSince(user?.created_at) }}</span>
                  <span class="stat-label">Üye</span>
                </div>
              </div>

              <div class="stat-card">
                <div class="stat-icon stat-icon-purple">
                  <TrophyIcon class="w-5 h-5" />
                </div>
                <div class="stat-content">
                  <span class="stat-value">{{ user?.achievements_count || 0 }}</span>
                  <span class="stat-label">Başarı</span>
                </div>
              </div>
            </div>

            <!-- Level/Rank Progress Bar -->
            <div class="level-progress-section mt-6">
              <div class="flex justify-between items-center mb-2">
                <div class="flex items-center gap-2">
                  <div class="level-icon">
                    <StarIcon class="w-4 h-4" />
                  </div>
                  <span class="text-sm font-medium">Seviye {{ userLevel }}</span>
                </div>
                <div class="xp-display">
                  <span class="text-orange-500 font-bold">{{ currentXP.toLocaleString() }}</span>
                  <span class="text-gray-500"> / {{ nextLevelXP.toLocaleString() }} XP</span>
                </div>
              </div>
              <div class="level-progress-track">
                <div class="level-progress-fill" :style="{ width: `${levelProgress}%` }">
                  <div class="level-progress-glow"></div>
                </div>
              </div>
              <p class="text-xs text-gray-500 mt-2">
                Sonraki seviyeye {{ (nextLevelXP - currentXP).toLocaleString() }} XP kaldı
              </p>
            </div>
          </div>

          <!-- Profile Completeness Circular Progress -->
          <div class="completeness-section">
            <div class="completeness-card">
              <div class="circular-progress" :style="{ '--progress': profileCompleteness }">
                <svg viewBox="0 0 100 100">
                  <circle class="progress-bg" cx="50" cy="50" r="45" />
                  <circle class="progress-fill" cx="50" cy="50" r="45" />
                </svg>
                <div class="progress-content">
                  <span class="progress-value">{{ profileCompleteness }}%</span>
                  <span class="progress-label">Tamamlandı</span>
                </div>
              </div>
              <h4 class="text-sm font-medium mt-4 text-center">Profil Durumu</h4>
              <p class="text-xs text-gray-500 text-center mt-1">{{ getCompletenessMessage() }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs Navigation with Icons & Active Indicator -->
      <nav class="tabs-navigation mb-8" aria-label="Profil seçenekleri">
        <div class="tabs-container" role="tablist" aria-label="Profil sekmeleri">
          <button
            v-for="(tab, index) in tabs"
            :key="tab.name"
            :id="`tab-${tab.name}`"
            class="tab-item"
            :class="{ 'tab-active': activeTab === tab.name }"
            role="tab"
            :aria-selected="activeTab === tab.name"
            :aria-controls="`tabpanel-${tab.name}`"
            :tabindex="activeTab === tab.name ? 0 : -1"
            @click="activeTab = tab.name"
            @keydown="handleTabKeydown($event, index)"
          >
            <component :is="tab.icon" class="w-5 h-5" aria-hidden="true" />
            <span class="tab-label">{{ tab.label }}</span>
            <span v-if="tab.count !== undefined" class="tab-badge" :aria-label="`${tab.count} öğe`">{{ tab.count }}</span>
            <div v-if="activeTab === tab.name" class="tab-indicator" aria-hidden="true"></div>
          </button>
        </div>
      </nav>

      <!-- Tab Content with Smooth Transitions -->
      <Transition name="tab-slide" mode="out-in">
        <!-- Profile Tab -->
        <div
          v-if="activeTab === 'profile'"
          key="profile"
          id="tabpanel-profile"
          role="tabpanel"
          aria-labelledby="tab-profile"
          class="tab-content"
        >
          <div class="grid lg:grid-cols-3 gap-6">
            <!-- Profile Form -->
            <div class="lg:col-span-2 space-y-6">
              <div class="glass-card rounded-2xl p-6">
                <div class="section-header">
                  <div class="section-icon">
                    <UserIcon class="w-5 h-5" />
                  </div>
                  <h3 class="section-title">Profil Bilgileri</h3>
                </div>

                <n-form @submit.prevent="updateProfile" class="space-y-5" aria-label="Profil bilgileri formu">
                  <div class="grid md:grid-cols-2 gap-5">
                    <!-- Modern Input with Icon -->
                    <div class="input-group">
                      <label for="username" class="sr-only">Kullanıcı Adı</label>
                      <div class="input-icon-wrapper" aria-hidden="true">
                        <UserIcon class="w-4 h-4" />
                      </div>
                      <n-input
                        id="username"
                        v-model:value="profileForm.username"
                        placeholder="Kullanıcı Adı"
                        class="modern-input"
                        :status="validationStatus.username"
                        aria-describedby="username-status"
                      />
                      <CheckCircleIcon v-if="profileForm.username" class="input-valid-icon" aria-hidden="true" />
                      <span id="username-status" class="sr-only">
                        {{ profileForm.username ? 'Kullanıcı adı girildi' : 'Kullanıcı adı gerekli' }}
                      </span>
                    </div>

                    <div class="input-group">
                      <label for="email" class="sr-only">E-posta Adresi</label>
                      <div class="input-icon-wrapper" aria-hidden="true">
                        <MailIcon class="w-4 h-4" />
                      </div>
                      <n-input
                        id="email"
                        v-model:value="profileForm.email"
                        type="email"
                        placeholder="E-posta Adresi"
                        class="modern-input"
                        :status="validationStatus.email"
                        aria-describedby="email-status"
                        autocomplete="email"
                      />
                      <CheckCircleIcon v-if="isValidEmail(profileForm.email)" class="input-valid-icon" aria-hidden="true" />
                      <XCircleIcon v-else-if="profileForm.email" class="input-invalid-icon" aria-hidden="true" />
                      <span id="email-status" class="sr-only">
                        {{ isValidEmail(profileForm.email) ? 'Geçerli e-posta' : 'Geçersiz e-posta formatı' }}
                      </span>
                    </div>

                    <div class="input-group">
                      <label for="first-name" class="sr-only">Ad</label>
                      <div class="input-icon-wrapper" aria-hidden="true">
                        <UserIcon class="w-4 h-4" />
                      </div>
                      <n-input
                        id="first-name"
                        v-model:value="profileForm.first_name"
                        placeholder="Ad"
                        class="modern-input"
                        autocomplete="given-name"
                      />
                    </div>

                    <div class="input-group">
                      <label for="last-name" class="sr-only">Soyad</label>
                      <div class="input-icon-wrapper" aria-hidden="true">
                        <UserIcon class="w-4 h-4" />
                      </div>
                      <n-input
                        id="last-name"
                        v-model:value="profileForm.last_name"
                        placeholder="Soyad"
                        class="modern-input"
                        autocomplete="family-name"
                      />
                    </div>

                    <div class="input-group">
                      <label for="phone" class="sr-only">Telefon</label>
                      <div class="input-icon-wrapper" aria-hidden="true">
                        <PhoneIcon class="w-4 h-4" />
                      </div>
                      <n-input
                        id="phone"
                        v-model:value="profileForm.phone"
                        placeholder="Telefon"
                        class="modern-input"
                        autocomplete="tel"
                      />
                    </div>

                    <div class="input-group">
                      <label for="country" class="sr-only">Ülke</label>
                      <div class="input-icon-wrapper" aria-hidden="true">
                        <GlobeIcon class="w-4 h-4" />
                      </div>
                      <n-input
                        id="country"
                        v-model:value="profileForm.country"
                        placeholder="Ülke"
                        class="modern-input"
                        autocomplete="country-name"
                      />
                    </div>
                  </div>

                  <div class="input-group">
                    <div class="input-icon-wrapper textarea-icon">
                      <FileTextIcon class="w-4 h-4" />
                    </div>
                    <n-input
                      v-model:value="profileForm.bio"
                      type="textarea"
                      placeholder="Biyografi - Kendinizi tanıtın..."
                      :rows="4"
                      :maxlength="bioMaxLength"
                      show-count
                      class="modern-input modern-textarea"
                    />
                    <div class="bio-counter" :class="{ 'bio-counter-warning': bioRemaining < 50 }">
                      {{ bioCharCount }}/{{ bioMaxLength }}
                    </div>
                  </div>

                  <div class="flex justify-end gap-3 pt-2">
                    <n-button
                      quaternary
                      size="large"
                      class="btn-cancel"
                      :disabled="!hasUnsavedChanges"
                      @click="resetForm"
                    >
                      İptal
                    </n-button>
                    <n-button
                      type="primary"
                      size="large"
                      attr-type="submit"
                      :loading="saving"
                      :disabled="!hasUnsavedChanges"
                      class="btn-save"
                    >
                      <template #icon><SaveIcon class="w-4 h-4" /></template>
                      {{ hasUnsavedChanges ? 'Değişiklikleri Kaydet' : 'Kaydedildi' }}
                    </n-button>
                  </div>
                </n-form>
              </div>
            </div>

            <!-- Sidebar -->
            <div class="space-y-6">
              <!-- Connected Accounts Section -->
              <div class="glass-card rounded-2xl p-6">
                <div class="section-header">
                  <div class="section-icon">
                    <LinkIcon class="w-5 h-5" />
                  </div>
                  <h3 class="section-title">Bağlı Hesaplar</h3>
                </div>

                <div class="connected-accounts-list">
                  <!-- Steam -->
                  <div class="account-item" :class="{ 'connected': connectedAccounts.steam.connected }">
                    <div class="account-info">
                      <div class="account-icon steam-icon">
                        <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
                          <path d="M12 2C6.48 2 2 6.48 2 12c0 5.17 3.95 9.42 9 9.95v-2.02c-3.94-.49-7-3.86-7-7.93 0-4.42 3.58-8 8-8s8 3.58 8 8c0 .88-.14 1.73-.41 2.52l1.77.71c.41-1.01.64-2.1.64-3.23 0-5.52-4.48-10-10-10zm-1.5 11.5l-2.47-.99c.13 1.67 1.52 3 3.22 3 1.79 0 3.25-1.46 3.25-3.25s-1.46-3.25-3.25-3.25c-.67 0-1.29.2-1.81.55l2.56 1.03c.81.32 1.2 1.24.88 2.05-.32.8-1.24 1.19-2.05.87l-.33-.01z"/>
                        </svg>
                      </div>
                      <div>
                        <h4 class="font-medium">Steam</h4>
                        <p class="text-xs text-gray-400">
                          {{ connectedAccounts.steam.connected ? connectedAccounts.steam.username : 'Bağlı değil' }}
                        </p>
                      </div>
                    </div>
                    <n-button
                      v-if="connectedAccounts.steam.connected"
                      size="small"
                      type="error"
                      ghost
                      @click="disconnectAccount('steam')"
                    >
                      Kaldır
                    </n-button>
                    <n-button
                      v-else
                      size="small"
                      type="primary"
                      @click="connectAccount('steam')"
                    >
                      Bağla
                    </n-button>
                  </div>

                  <!-- Discord -->
                  <div class="account-item" :class="{ 'connected': connectedAccounts.discord.connected }">
                    <div class="account-info">
                      <div class="account-icon discord-icon">
                        <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
                          <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
                        </svg>
                      </div>
                      <div>
                        <h4 class="font-medium">Discord</h4>
                        <p class="text-xs text-gray-400">
                          {{ connectedAccounts.discord.connected ? connectedAccounts.discord.username : 'Bağlı değil' }}
                        </p>
                      </div>
                    </div>
                    <n-button
                      v-if="connectedAccounts.discord.connected"
                      size="small"
                      type="error"
                      ghost
                      @click="disconnectAccount('discord')"
                    >
                      Kaldır
                    </n-button>
                    <n-button
                      v-else
                      size="small"
                      type="primary"
                      @click="connectAccount('discord')"
                    >
                      Bağla
                    </n-button>
                  </div>
                </div>
              </div>

              <!-- Achievement Badges - Sadece başarı varsa göster -->
              <div v-if="achievements.length > 0" class="glass-card rounded-2xl p-6">
                <div class="section-header">
                  <div class="section-icon">
                    <AwardIcon class="w-5 h-5" />
                  </div>
                  <h3 class="section-title">Başarı Rozetleri</h3>
                </div>
                <div class="badges-grid">
                  <div
                    v-for="badge in achievements"
                    :key="badge.id"
                    class="badge-item"
                    :class="{ 'badge-locked': !badge.unlocked }"
                    :title="badge.name"
                  >
                    <component :is="badge.icon" class="w-5 h-5" />
                  </div>
                </div>
                <n-button quaternary block class="mt-4" @click="showAllAchievements = true">
                  Tüm Başarıları Gör
                </n-button>
              </div>
            </div>
          </div>
        </div>

        <!-- Appearance Tab -->
        <div
          v-else-if="activeTab === 'appearance'"
          key="appearance"
          id="tabpanel-appearance"
          role="tabpanel"
          aria-labelledby="tab-appearance"
          class="tab-content"
        >
          <ProfileCustomizer />
        </div>

        <!-- Security Tab -->
        <div
          v-else-if="activeTab === 'security'"
          key="security"
          id="tabpanel-security"
          role="tabpanel"
          aria-labelledby="tab-security"
          class="tab-content space-y-6"
        >
          <!-- Email Verification Section -->
          <div v-if="showEmailVerificationSection" class="glass-card rounded-2xl p-6">
            <div class="section-header">
              <div class="section-icon" :class="user?.email_verified ? 'section-icon-green' : 'section-icon-yellow'">
                <MailCheckIcon v-if="user?.email_verified" class="w-5 h-5" />
                <MailWarningIcon v-else class="w-5 h-5" />
              </div>
              <h3 class="section-title">E-posta Dogrulama</h3>
              <n-tag
                :type="user?.email_verified ? 'success' : 'warning'"
                size="medium"
                round
                class="ml-auto"
              >
                {{ user?.email_verified ? 'Dogrulandi' : 'Dogrulanmadi' }}
              </n-tag>
            </div>

            <!-- Verified State -->
            <div v-if="user?.email_verified" class="email-verified-state">
              <n-alert type="success" :bordered="false">
                <template #icon><CheckCircleIcon class="w-5 h-5" /></template>
                <template #header>E-posta Adresiniz Dogrulandi</template>
                E-posta adresiniz ({{ user?.email }}) basariyla dogrulandi.
              </n-alert>
            </div>

            <!-- Not Verified State -->
            <div v-else class="email-not-verified-state">
              <p class="text-gray-400 mb-4">
                E-posta adresinizi dogrulamaniz gerekmektedir. Dogrulama yapmadiginiz surece bazi ozellikler kisitli olabilir.
              </p>

              <div class="flex flex-wrap items-center gap-4">
                <n-button
                  v-if="emailVerification.canResend"
                  type="warning"
                  size="large"
                  :loading="emailVerification.sending"
                  @click="sendEmailVerification"
                  class="btn-save"
                >
                  <template #icon><SendIcon class="w-4 h-4" /></template>
                  Dogrulama Emaili Gonder
                </n-button>
                <n-button
                  v-else
                  disabled
                  size="large"
                  class="btn-save"
                >
                  <template #icon><ClockIcon class="w-4 h-4" /></template>
                  {{ emailVerification.countdown }}s bekleyin
                </n-button>

                <p class="text-sm text-gray-500">
                  <MailIcon class="w-4 h-4 inline-block mr-1" />
                  {{ user?.email }}
                </p>
              </div>
            </div>
          </div>

          <!-- Password Change Section -->
          <div v-if="!isOAuthUser" class="glass-card rounded-2xl p-6">
            <div class="section-header">
              <div class="section-icon">
                <KeyIcon class="w-5 h-5" />
              </div>
              <h3 class="section-title">Şifre Değiştir</h3>
            </div>

            <n-form @submit.prevent="changePassword" class="space-y-5" aria-label="Şifre değiştirme formu">
              <div class="input-group">
                <label for="current-password" class="sr-only">Mevcut Şifre</label>
                <div class="input-icon-wrapper" aria-hidden="true">
                  <LockIcon class="w-4 h-4" />
                </div>
                <n-input
                  id="current-password"
                  v-model:value="passwordForm.current_password"
                  type="password"
                  show-password-on="click"
                  placeholder="Mevcut Şifre"
                  class="modern-input"
                  autocomplete="current-password"
                />
              </div>

              <div class="grid md:grid-cols-2 gap-5">
                <div class="input-group">
                  <label for="new-password" class="sr-only">Yeni Şifre</label>
                  <div class="input-icon-wrapper" aria-hidden="true">
                    <LockIcon class="w-4 h-4" />
                  </div>
                  <n-input
                    id="new-password"
                    v-model:value="passwordForm.new_password"
                    type="password"
                    show-password-on="click"
                    placeholder="Yeni Şifre"
                    class="modern-input"
                    autocomplete="new-password"
                    aria-describedby="password-strength-info"
                    @input="checkPasswordStrength"
                  />
                </div>

                <div class="input-group">
                  <label for="confirm-password" class="sr-only">Yeni Şifre Tekrar</label>
                  <div class="input-icon-wrapper" aria-hidden="true">
                    <LockIcon class="w-4 h-4" />
                  </div>
                  <n-input
                    id="confirm-password"
                    v-model:value="passwordForm.confirm_password"
                    type="password"
                    show-password-on="click"
                    placeholder="Yeni Şifre (Tekrar)"
                    class="modern-input"
                    autocomplete="new-password"
                    aria-describedby="password-match-status"
                    :status="passwordForm.confirm_password && passwordForm.new_password !== passwordForm.confirm_password ? 'error' : undefined"
                  />
                  <span id="password-match-status" class="sr-only">
                    {{ passwordForm.confirm_password && passwordForm.new_password !== passwordForm.confirm_password ? 'Şifreler eşleşmiyor' : 'Şifreler eşleşiyor' }}
                  </span>
                </div>
              </div>

              <!-- Password Strength Meter -->
              <div v-if="passwordForm.new_password" class="password-strength-section" role="group" aria-labelledby="password-strength-label">
                <div class="strength-header">
                  <span id="password-strength-label" class="text-sm text-gray-400">Şifre Gücü</span>
                  <span class="strength-text" :class="strengthClass" aria-live="polite" id="password-strength-info">{{ strengthText }}</span>
                </div>
                <div class="strength-bars" role="progressbar" :aria-valuenow="passwordStrength" aria-valuemin="0" aria-valuemax="100" :aria-label="`Şifre gücü: ${strengthText}`">
                  <div
                    v-for="i in 5"
                    :key="i"
                    class="strength-bar"
                    :class="{ 'active': passwordStrength >= i * 20, [strengthClass]: passwordStrength >= i * 20 }"
                    aria-hidden="true"
                  ></div>
                </div>
                <ul class="strength-requirements" aria-label="Şifre gereksinimleri">
                  <li class="requirement" :class="{ 'met': passwordChecks.minLength }">
                    <component :is="passwordChecks.minLength ? CheckCircleIcon : CircleIcon" class="w-3.5 h-3.5" aria-hidden="true" />
                    <span>En az 8 karakter</span>
                    <span class="sr-only">{{ passwordChecks.minLength ? '- karşılandı' : '- karşılanmadı' }}</span>
                  </li>
                  <li class="requirement" :class="{ 'met': passwordChecks.hasLower }">
                    <component :is="passwordChecks.hasLower ? CheckCircleIcon : CircleIcon" class="w-3.5 h-3.5" aria-hidden="true" />
                    <span>Küçük harf</span>
                    <span class="sr-only">{{ passwordChecks.hasLower ? '- karşılandı' : '- karşılanmadı' }}</span>
                  </li>
                  <li class="requirement" :class="{ 'met': passwordChecks.hasNumber }">
                    <component :is="passwordChecks.hasNumber ? CheckCircleIcon : CircleIcon" class="w-3.5 h-3.5" aria-hidden="true" />
                    <span>Rakam</span>
                    <span class="sr-only">{{ passwordChecks.hasNumber ? '- karşılandı' : '- karşılanmadı' }}</span>
                  </li>
                  <li class="requirement" :class="{ 'met': passwordChecks.hasSpecial }">
                    <component :is="passwordChecks.hasSpecial ? CheckCircleIcon : CircleIcon" class="w-3.5 h-3.5" aria-hidden="true" />
                    <span>Özel karakter</span>
                    <span class="sr-only">{{ passwordChecks.hasSpecial ? '- karşılandı' : '- karşılanmadı' }}</span>
                  </li>
                </ul>
              </div>

              <div class="flex justify-end">
                <n-button type="primary" size="large" attr-type="submit" :loading="savingPassword" class="btn-save">
                  <template #icon><LockIcon class="w-4 h-4" /></template>
                  Şifreyi Güncelle
                </n-button>
              </div>
            </n-form>
          </div>

          <!-- OAuth User Notice -->
          <div v-else class="glass-card rounded-2xl p-6">
            <n-alert type="info" :bordered="false">
              <template #icon><InfoIcon class="w-5 h-5" /></template>
              <template #header>OAuth Hesabi</template>
              Steam veya Discord ile giriş yaptiginiz için şifre belirlemeniz gerekmemektedir.
            </n-alert>
          </div>

          <!-- 2FA Section with Setup Wizard -->
          <div class="glass-card rounded-2xl p-6">
            <div class="section-header">
              <div class="section-icon">
                <ShieldCheckIcon class="w-5 h-5" />
              </div>
              <h3 class="section-title">İki Faktörlü Doğrulama (2FA)</h3>
              <n-tag
                :type="user?.two_factor_enabled ? 'success' : 'warning'"
                size="medium"
                round
                class="ml-auto"
              >
                {{ user?.two_factor_enabled ? 'Aktif' : 'Pasif' }}
              </n-tag>
            </div>

            <p class="text-gray-400 mb-6">
              İki faktörlü doğrulama, hesabınıza ek bir güvenlik katmanı ekler.
            </p>

            <!-- 2FA Not Enabled -->
            <div v-if="!user?.two_factor_enabled && !show2FASetup">
              <n-button type="primary" size="large" @click="start2FASetup" class="btn-save">
                <template #icon><ShieldCheckIcon class="w-4 h-4" /></template>
                2FA'yi Etkinleştir
              </n-button>
            </div>

            <!-- 2FA Setup Wizard Steps -->
            <div v-else-if="show2FASetup" class="twofa-wizard">
              <!-- Wizard Steps Indicator -->
              <div class="wizard-steps">
                <div class="wizard-step" :class="{ 'active': twoFAStep >= 1, 'completed': twoFAStep > 1 }">
                  <div class="step-circle">
                    <CheckIcon v-if="twoFAStep > 1" class="w-4 h-4" />
                    <span v-else>1</span>
                  </div>
                  <span class="step-label">QR Kodu Tara</span>
                </div>
                <div class="step-line" :class="{ 'active': twoFAStep > 1 }"></div>
                <div class="wizard-step" :class="{ 'active': twoFAStep >= 2, 'completed': twoFAStep > 2 }">
                  <div class="step-circle">
                    <CheckIcon v-if="twoFAStep > 2" class="w-4 h-4" />
                    <span v-else>2</span>
                  </div>
                  <span class="step-label">Doğrula</span>
                </div>
                <div class="step-line" :class="{ 'active': twoFAStep > 2 }"></div>
                <div class="wizard-step" :class="{ 'active': twoFAStep >= 3 }">
                  <div class="step-circle">
                    <span>3</span>
                  </div>
                  <span class="step-label">Yedek Kodlar</span>
                </div>
              </div>

              <!-- Step 1: QR Code -->
              <div v-if="twoFAStep === 1" class="wizard-content text-center">
                <p class="text-gray-400 mb-6">
                  Google Authenticator veya benzeri bir uygulama ile QR kodunu tarayin.
                </p>
                <div class="qr-placeholder">
                  <div class="qr-frame">
                    <div class="qr-code">
                      <QrCodeIcon class="w-32 h-32 text-gray-600" />
                    </div>
                  </div>
                </div>
                <p class="text-sm text-gray-500 mt-4 mb-2">Manuel giriş kodu:</p>
                <code class="secret-code">{{ twoFASecret }}</code>
                <div class="flex justify-center gap-3 mt-6">
                  <n-button size="large" quaternary @click="cancel2FASetup">İptal</n-button>
                  <n-button size="large" type="primary" @click="twoFAStep = 2" class="btn-save">
                    Devam Et
                    <template #icon><ArrowRightIcon class="w-4 h-4" /></template>
                  </n-button>
                </div>
              </div>

              <!-- Step 2: Verify -->
              <div v-else-if="twoFAStep === 2" class="wizard-content text-center">
                <p class="text-gray-400 mb-6">
                  Uygulamanızda görünen 6 haneli kodu girin.
                </p>
                <div class="otp-container">
                  <n-input
                    v-model:value="twoFACode"
                    placeholder="000000"
                    :maxlength="6"
                    class="otp-input"
                  />
                </div>
                <div class="flex justify-center gap-3 mt-6">
                  <n-button size="large" quaternary @click="twoFAStep = 1">Geri</n-button>
                  <n-button size="large" type="primary" :loading="verifying2FA" @click="verify2FACode" class="btn-save">
                    Doğrula
                  </n-button>
                </div>
              </div>

              <!-- Step 3: Backup Codes -->
              <div v-else-if="twoFAStep === 3" class="wizard-content text-center">
                <div class="success-icon-wrapper">
                  <CheckCircleIcon class="w-12 h-12 text-green-500" />
                </div>
                <h4 class="text-xl font-semibold mt-4 mb-2">2FA Başarıyla Etkinleştirildi!</h4>
                <p class="text-gray-400 mb-6">
                  Bu yedek kodlari güvenli bir yerde saklayın.
                </p>
                <div class="backup-codes">
                  <div v-for="code in backupCodes" :key="code" class="backup-code">
                    {{ code }}
                  </div>
                </div>
                <div class="flex justify-center gap-3 mt-6">
                  <n-button size="large" @click="downloadBackupCodes">
                    <template #icon><DownloadIcon class="w-4 h-4" /></template>
                    Kodları İndir
                  </n-button>
                  <n-button size="large" type="primary" @click="finish2FASetup" class="btn-save">
                    Tamamla
                  </n-button>
                </div>
              </div>
            </div>

            <!-- 2FA Already Enabled -->
            <div v-else-if="user?.two_factor_enabled" class="space-y-4">
              <n-alert type="success" :bordered="false">
                <template #icon><ShieldCheckIcon class="w-5 h-5" /></template>
                2FA hesabınızda aktif durumda!
              </n-alert>
              <div class="flex flex-wrap gap-3">
                <n-button @click="show2FABackupCodes = true">
                  <template #icon><KeyIcon class="w-4 h-4" /></template>
                  Yedek Kodları Gör
                </n-button>
                <n-button type="error" ghost @click="disable2FA">
                  <template #icon><XCircleIcon class="w-4 h-4" /></template>
                  2FA'yi Devre Disi Birak
                </n-button>
              </div>
            </div>
          </div>

          <!-- Active Sessions with Device Icons -->
          <div class="glass-card rounded-2xl p-6">
            <div class="section-header">
              <div class="section-icon">
                <MonitorIcon class="w-5 h-5" />
              </div>
              <h3 class="section-title">Aktif Oturumlar</h3>
              <n-button type="error" ghost size="small" class="ml-auto" @click="revokeAllSessions">
                Tüm Oturumları Sonlandır
              </n-button>
            </div>

            <!-- Loading Skeleton -->
            <div v-if="sessionsLoading" class="sessions-grid" aria-busy="true" aria-label="Oturumlar yükleniyor">
              <div v-for="i in 3" :key="i" class="session-card skeleton-card">
                <div class="skeleton skeleton-icon"></div>
                <div class="session-details">
                  <div class="skeleton skeleton-title"></div>
                  <div class="skeleton skeleton-text"></div>
                  <div class="skeleton skeleton-text-sm"></div>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else-if="sessions.length === 0" class="empty-state" role="status">
              <MonitorIcon class="w-12 h-12 text-gray-600 mb-3" />
              <p class="text-gray-400">Aktif oturum bulunamadı</p>
            </div>

            <!-- Sessions List -->
            <div v-else class="sessions-grid" role="list" aria-label="Aktif oturumlar">
              <div
                v-for="session in sessions"
                :key="session.id"
                class="session-card"
                role="listitem"
                :aria-label="`${session.device_name} oturumu`"
              >
                <div class="session-device-icon" :class="getDeviceClass(session.device_type)" aria-hidden="true">
                  <MonitorIcon v-if="session.device_type === 'desktop'" class="w-6 h-6" />
                  <SmartphoneIcon v-else-if="session.device_type === 'mobile'" class="w-6 h-6" />
                  <TabletIcon v-else class="w-6 h-6" />
                </div>
                <div class="session-details">
                  <div class="flex items-center gap-2 mb-1">
                    <h4 class="font-medium">{{ session.device_name }}</h4>
                    <span v-if="session.is_current" class="current-badge" aria-label="Bu cihaz">Mevcut</span>
                  </div>
                  <div class="session-meta">
                    <span class="meta-item">
                      <GlobeIcon class="w-3 h-3" aria-hidden="true" />
                      <span class="sr-only">IP Adresi:</span>
                      {{ session.ip }}
                    </span>
                    <span class="meta-item">
                      <MapPinIcon class="w-3 h-3" aria-hidden="true" />
                      <span class="sr-only">Konum:</span>
                      {{ session.location }}
                    </span>
                  </div>
                  <p class="text-xs text-gray-500 mt-1">
                    <span class="sr-only">Son aktivite:</span>
                    {{ formatTime(session.last_activity) }}
                  </p>
                </div>
                <n-button
                  v-if="!session.is_current"
                  quaternary
                  size="small"
                  class="session-revoke"
                  :loading="revokingSession === session.id"
                  :aria-label="`${session.device_name} oturumunu sonlandır`"
                  @click="revokeSession(session.id)"
                >
                  <template #icon><LogOutIcon class="w-4 h-4" /></template>
                </n-button>
              </div>
            </div>
          </div>
        </div>

        <!-- Settings Tab -->
        <div
          v-else-if="activeTab === 'settings'"
          key="settings"
          id="tabpanel-settings"
          role="tabpanel"
          aria-labelledby="tab-settings"
          class="tab-content space-y-6"
        >
          <!-- Notification Preferences -->
          <div class="glass-card rounded-2xl p-6">
            <div class="section-header">
              <div class="section-icon">
                <BellIcon class="w-5 h-5" />
              </div>
              <h3 class="section-title">Bildirim Tercihleri</h3>
            </div>

            <div class="toggle-list" role="group" aria-label="Bildirim ayarları">
              <div class="toggle-item">
                <div class="toggle-info">
                  <MailIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                  <div>
                    <h4 id="email-notif-label">E-posta Bildirimleri</h4>
                    <p id="email-notif-desc">Önemli güncellemeler için e-posta alın</p>
                  </div>
                </div>
                <n-switch
                  v-model:value="settings.email_notifications"
                  :disabled="!hasEmail"
                  aria-labelledby="email-notif-label"
                  aria-describedby="email-notif-desc"
                />
              </div>

              <div class="toggle-item">
                <div class="toggle-info">
                  <ServerIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                  <div>
                    <h4 id="server-alerts-label">Sunucu Uyarıları</h4>
                    <p id="server-alerts-desc">Sunucu durumu değişikliklerinde bildirim alın</p>
                  </div>
                </div>
                <n-switch
                  v-model:value="settings.server_alerts"
                  aria-labelledby="server-alerts-label"
                  aria-describedby="server-alerts-desc"
                />
              </div>

              <div class="toggle-item">
                <div class="toggle-info">
                  <ShieldIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                  <div>
                    <h4 id="security-alerts-label">Güvenlik Bildirimleri</h4>
                    <p id="security-alerts-desc">Şüpheli aktivitelerde e-posta alın</p>
                  </div>
                </div>
                <n-switch
                  v-model:value="settings.security_alerts"
                  :disabled="!hasEmail"
                  aria-labelledby="security-alerts-label"
                  aria-describedby="security-alerts-desc"
                />
              </div>

              <div class="toggle-item">
                <div class="toggle-info">
                  <MegaphoneIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                  <div>
                    <h4 id="marketing-emails-label">Pazarlama E-postaları</h4>
                    <p id="marketing-emails-desc">Kampanya ve fırsatlardan haberdar olun</p>
                  </div>
                </div>
                <n-switch
                  v-model:value="settings.marketing_emails"
                  :disabled="!hasEmail"
                  aria-labelledby="marketing-emails-label"
                  aria-describedby="marketing-emails-desc"
                />
              </div>
            </div>
          </div>

          <!-- Privacy Settings -->
          <div class="glass-card rounded-2xl p-6">
            <div class="section-header">
              <div class="section-icon" aria-hidden="true">
                <EyeOffIcon class="w-5 h-5" />
              </div>
              <h3 class="section-title">Gizlilik Ayarları</h3>
            </div>

            <div class="toggle-list" role="group" aria-label="Gizlilik ayarları">
              <div class="toggle-item">
                <div class="toggle-info">
                  <UsersIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                  <div>
                    <h4 id="public-profile-label">Profil Görünürlüğü</h4>
                    <p id="public-profile-desc">Profilinizi herkese açık veya gizli yapın</p>
                  </div>
                </div>
                <n-switch
                  v-model:value="settings.public_profile"
                  aria-labelledby="public-profile-label"
                  aria-describedby="public-profile-desc"
                />
              </div>

              <div class="toggle-item">
                <div class="toggle-info">
                  <CircleDotIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                  <div>
                    <h4 id="online-status-label">Online Durumu</h4>
                    <p id="online-status-desc">Diğer kullanıcıların online durumunuzu görmesine izin verin</p>
                  </div>
                </div>
                <n-switch
                  v-model:value="settings.show_online_status"
                  aria-labelledby="online-status-label"
                  aria-describedby="online-status-desc"
                />
              </div>

              <div class="toggle-item">
                <div class="toggle-info">
                  <ActivityIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                  <div>
                    <h4 id="activity-history-label">Aktivite Geçmişi</h4>
                    <p id="activity-history-desc">Aktivite geçmişinizi profilinizde gösterin</p>
                  </div>
                </div>
                <n-switch
                  v-model:value="settings.show_activity"
                  aria-labelledby="activity-history-label"
                  aria-describedby="activity-history-desc"
                />
              </div>

              <div class="toggle-item">
                <div class="toggle-info">
                  <ServerIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                  <div>
                    <h4 id="server-list-label">Sunucu Listesi</h4>
                    <p id="server-list-desc">Sunucularınızı profilinizde gösterin</p>
                  </div>
                </div>
                <n-switch
                  v-model:value="settings.show_servers"
                  aria-labelledby="server-list-label"
                  aria-describedby="server-list-desc"
                />
              </div>
            </div>
          </div>

          <!-- Save Settings -->
          <div class="flex justify-end">
            <n-button type="primary" size="large" @click="saveSettings" :loading="savingSettings" class="btn-save">
              <template #icon><SaveIcon class="w-4 h-4" /></template>
              Ayarları Kaydet
            </n-button>
          </div>

          <!-- Danger Zone -->
          <section class="danger-zone-card rounded-2xl p-6" aria-labelledby="danger-zone-title">
            <div class="section-header danger">
              <div class="section-icon danger" aria-hidden="true">
                <AlertTriangleIcon class="w-5 h-5" />
              </div>
              <h3 id="danger-zone-title" class="section-title text-red-500">Tehlikeli Bölge</h3>
            </div>
            <p class="text-gray-400 mb-6" role="alert">Bu işlemler geri alınamaz. Dikkatli olun.</p>

            <div class="danger-actions" role="group" aria-label="Tehlikeli işlemler">
              <div class="danger-action-item">
                <div>
                  <h4 class="font-medium">Hesabı Dondur</h4>
                  <p class="text-sm text-gray-400">Hesabınızı geçici olarak devre dışı bırakın</p>
                </div>
                <n-button type="warning" ghost @click="freezeAccount" aria-label="Hesabı dondur">
                  <template #icon><PauseCircleIcon class="w-4 h-4" /></template>
                  Dondur
                </n-button>
              </div>

              <div class="danger-action-item">
                <div>
                  <h4 class="font-medium">Hesabı Sil</h4>
                  <p class="text-sm text-gray-400">Hesabınızı ve tüm verilerinizi kalıcı olarak silin</p>
                </div>
                <n-button type="error" ghost @click="showDeleteConfirm = true" aria-label="Hesabı kalıcı olarak sil">
                  <template #icon><Trash2Icon class="w-4 h-4" /></template>
                  Hesabı Sil
                </n-button>
              </div>
            </div>
          </section>
        </div>

        <!-- Activity Tab -->
        <div
          v-else-if="activeTab === 'activity'"
          key="activity"
          id="tabpanel-activity"
          role="tabpanel"
          aria-labelledby="tab-activity"
          class="tab-content"
        >
          <div class="glass-card rounded-2xl p-6">
            <div class="section-header">
              <div class="section-icon">
                <ActivityIcon class="w-5 h-5" />
              </div>
              <h3 class="section-title">Aktivite Geçmişi</h3>
            </div>

            <!-- Loading Skeleton -->
            <div v-if="activitiesLoading" class="activity-timeline" aria-busy="true" aria-label="Aktiviteler yükleniyor">
              <div v-for="i in 5" :key="i" class="timeline-entry skeleton-entry">
                <div class="timeline-icon skeleton"></div>
                <div class="timeline-connector"></div>
                <div class="timeline-card">
                  <div class="skeleton skeleton-title"></div>
                  <div class="skeleton skeleton-text"></div>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else-if="activities.length === 0" class="empty-state" role="status">
              <ActivityIcon class="w-12 h-12 text-gray-600 mb-3" />
              <p class="text-gray-400">Henüz aktivite kaydı yok</p>
              <p class="text-gray-500 text-sm mt-1">İşlemleriniz burada görünecektir</p>
            </div>

            <!-- Activity Timeline -->
            <div v-else class="activity-timeline" role="feed" aria-label="Aktivite geçmişi">
              <article
                v-for="(activity, index) in activities"
                :key="activity.id"
                class="timeline-entry"
                :class="{ 'last': index === activities.length - 1 }"
                role="article"
                :aria-label="activity.title"
              >
                <div class="timeline-icon" :class="`icon-${activity.type}`" aria-hidden="true">
                  <component :is="getActivityIcon(activity.type)" class="w-4 h-4" />
                </div>
                <div class="timeline-connector" v-if="index !== activities.length - 1" aria-hidden="true"></div>
                <div class="timeline-card">
                  <div class="timeline-header">
                    <h4>{{ activity.title }}</h4>
                    <time class="timeline-time" :datetime="activity.created_at?.toISOString?.()">
                      {{ formatTime(activity.created_at) }}
                    </time>
                  </div>
                  <p class="timeline-description">{{ activity.description }}</p>
                  <div v-if="activity.metadata" class="timeline-tags" aria-label="Ek bilgiler">
                    <span v-for="(value, key) in activity.metadata" :key="key" class="timeline-tag">
                      {{ key }}: {{ value }}
                    </span>
                  </div>
                </div>
              </article>
            </div>

            <div v-if="activities.length > 0" class="flex justify-center mt-6">
              <n-button
                quaternary
                :loading="loadingMore"
                :disabled="!hasMoreActivities"
                :aria-label="hasMoreActivities ? 'Daha fazla aktivite yükle' : 'Tüm aktiviteler yüklendi'"
                @click="loadMoreActivities"
              >
                <template #icon><RefreshCwIcon class="w-4 h-4" /></template>
                {{ hasMoreActivities ? 'Daha Fazla Yükle' : 'Tümü Yüklendi' }}
              </n-button>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Modals -->
    <!-- 2FA Backup Codes Modal -->
    <n-modal v-model:show="show2FABackupCodes" preset="card" title="Yedek Kodlar" class="modal-glass">
      <p class="text-gray-400 mb-6">
        Bu kodlari güvenli bir yerde saklayın.
      </p>
      <div class="backup-codes">
        <div v-for="code in backupCodes" :key="code" class="backup-code">
          {{ code }}
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <n-button quaternary @click="show2FABackupCodes = false">Kapat</n-button>
          <n-button type="primary" @click="downloadBackupCodes" class="btn-save">
            <template #icon><DownloadIcon class="w-4 h-4" /></template>
            İndir
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- Delete Account Confirmation Modal -->
    <n-modal v-model:show="showDeleteConfirm" preset="card" title="Hesabı Sil" class="modal-glass">
      <n-alert type="error" :bordered="false" class="mb-6">
        <template #icon><AlertTriangleIcon class="w-5 h-5" /></template>
        Bu işlem geri alınamaz! Tüm verileriniz kalıcı olarak silinecektir.
      </n-alert>
      <p class="text-gray-400 mb-4">
        Hesabınızı silmek istediğinizi onaylamak için aşağıya
        <strong style="color: var(--text-primary)">"HESABIMI SIL"</strong> yazın.
      </p>
      <n-input v-model:value="deleteConfirmText" placeholder="HESABIMI SIL" class="modern-input" />
      <template #footer>
        <div class="flex justify-end gap-3">
          <n-button quaternary @click="showDeleteConfirm = false">İptal</n-button>
          <n-button
            type="error"
            :disabled="deleteConfirmText !== 'HESABIMI SIL'"
            :loading="deletingAccount"
            @click="deleteAccount"
          >
            <template #icon><Trash2Icon class="w-4 h-4" /></template>
            Hesabi Kalıcı Olarak Sil
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- Avatar Upload Modal -->
    <n-modal v-model:show="showAvatarUpload" preset="card" title="Profil Fotoğrafı" class="modal-glass">
      <div class="upload-zone">
        <n-upload
          accept="image/*"
          :max="1"
          :show-file-list="false"
          @change="handleAvatarUpload"
        >
          <div class="upload-content">
            <UploadCloudIcon class="w-12 h-12 text-orange-500 mb-4" />
            <p class="text-gray-300">Fotografinizi sürükleyin veya tıklayın</p>
            <p class="text-sm text-gray-500 mt-2">PNG, JPG (max. 5MB)</p>
          </div>
        </n-upload>
      </div>
    </n-modal>

    <!-- Cover Photo Upload Modal -->
    <n-modal v-model:show="showCoverUpload" preset="card" title="Kapak Fotografi" class="modal-glass">
      <div class="upload-zone">
        <n-upload
          accept="image/*"
          :max="1"
          :show-file-list="false"
          @change="handleCoverUpload"
        >
          <div class="upload-content">
            <ImageIcon class="w-12 h-12 text-orange-500 mb-4" />
            <p class="text-gray-300">Kapak fotografinizi sürükleyin veya tıklayın</p>
            <p class="text-sm text-gray-500 mt-2">PNG, JPG (min. 1920x400, max. 10MB)</p>
          </div>
        </n-upload>
      </div>
    </n-modal>

    <!-- All Achievements Modal -->
    <n-modal v-model:show="showAllAchievements" preset="card" title="Tüm Başarılar" class="modal-glass modal-lg">
      <div class="achievements-modal-grid">
        <div
          v-for="badge in allAchievements"
          :key="badge.id"
          class="achievement-modal-card"
          :class="{ 'locked': !badge.unlocked }"
        >
          <div class="achievement-modal-icon">
            <component :is="badge.icon" class="w-8 h-8" />
          </div>
          <h4>{{ badge.name }}</h4>
          <p>{{ badge.description }}</p>
          <span v-if="badge.unlocked" class="achievement-date">
            {{ formatDate(badge.unlocked_at) }}
          </span>
          <div v-else class="achievement-progress-bar">
            <div class="progress-fill" :style="{ width: `${badge.progress || 0}%` }"></div>
            <span>{{ badge.progress || 0 }}%</span>
          </div>
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, onUnmounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ProfileCustomizer from '@/components/profile/ProfileCustomizer.vue'
import { authAPI } from '@/api'
import { useUIStore } from '@/stores/ui'
import {
  UserIcon,
  ShieldCheckIcon,
  SettingsIcon,
  ActivityIcon,
  PaletteIcon,
  CameraIcon,
  CheckCircleIcon,
  CalendarIcon,
  ServerIcon,
  KeyIcon,
  XCircleIcon,
  MonitorIcon,
  SmartphoneIcon,
  TabletIcon,
  InfoIcon,
  AlertCircleIcon,
  AlertTriangleIcon,
  MailIcon,
  MailCheck as MailCheckIcon,
  MailWarning as MailWarningIcon,
  Send as SendIcon,
  Clock as ClockIcon,
  PhoneIcon,
  GlobeIcon,
  SaveIcon,
  LockIcon,
  CheckIcon,
  XIcon,
  ArrowRightIcon,
  DownloadIcon,
  MapPinIcon,
  LogOutIcon,
  EyeIcon,
  EyeOffIcon,
  BellIcon,
  PauseCircleIcon,
  Trash2Icon,
  UploadCloudIcon,
  ImageIcon,
  LinkIcon,
  AwardIcon,
  TrophyIcon,
  CrownIcon,
  MessageSquareIcon,
  StarIcon,
  ZapIcon,
  RocketIcon,
  TargetIcon,
  HeartIcon,
  FlameIcon,
  ShieldIcon,
  BookIcon,
  FileTextIcon,
  CircleIcon,
  QrCodeIcon,
  RefreshCwIcon,
  UsersIcon,
  CircleDotIcon,
  MegaphoneIcon
} from 'lucide-vue-next'
import { formatDistanceToNow, format } from 'date-fns'
import { tr } from 'date-fns/locale'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

// Check if user logged in via OAuth
const isOAuthUser = computed(() => {
  const provider = user.value?.auth_provider || user.value?.oauth_provider
  return provider && provider !== 'local' && provider !== 'email'
})

const hasEmail = computed(() => !!user.value?.email)

// User status
const userStatus = ref('online')
const statusClass = computed(() => ({
  'status-online': userStatus.value === 'online',
  'status-away': userStatus.value === 'away',
  'status-offline': userStatus.value === 'offline'
}))

// Level system
const userLevel = computed(() => user.value?.level || 1)
const currentXP = computed(() => user.value?.xp || 350)
const nextLevelXP = computed(() => userLevel.value * 1000)
const levelProgress = computed(() => (currentXP.value / nextLevelXP.value) * 100)

// User rank
const userRank = computed(() => user.value?.rank || 'Oyuncu')

const getRoleBadgeStyle = (rank) => {
  const styles = {
    'Oyuncu': { background: 'linear-gradient(135deg, #6b7280, #4b5563)', color: '#fff' },
    'VIP': { background: 'linear-gradient(135deg, #f97316, #ea580c)', color: '#fff' },
    'Premium': { background: 'linear-gradient(135deg, #eab308, #ca8a04)', color: '#000' },
    'Moderatör': { background: 'linear-gradient(135deg, #3b82f6, #2563eb)', color: '#fff' },
    'Admin': { background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: '#fff' }
  }
  return styles[rank] || styles['Oyuncu']
}

// Profile completeness
const profileCompleteness = computed(() => {
  let score = 0
  const fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'country', 'bio', 'avatar']
  fields.forEach(field => {
    if (user.value?.[field]) score += 12.5
  })
  return Math.round(score)
})

const getCompletenessMessage = () => {
  const percent = profileCompleteness.value
  if (percent < 25) return 'Profilinizi tamamlayın!'
  if (percent < 50) return 'İyi bir başlangıç!'
  if (percent < 75) return 'Neredeyse tamam!'
  if (percent < 100) return 'Son bir adım!'
  return 'Profil tamamlandı!'
}

// Validation
const validationStatus = reactive({
  username: undefined,
  email: undefined
})

const isValidEmail = (email) => {
  if (!email) return false
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

// Tabs
const activeTab = ref('profile')
const tabs = computed(() => [
  { name: 'profile', label: 'Profil', icon: UserIcon },
  { name: 'appearance', label: 'Görünüm', icon: PaletteIcon },
  { name: 'security', label: 'Güvenlik', icon: ShieldCheckIcon },
  { name: 'settings', label: 'Ayarlar', icon: SettingsIcon },
  { name: 'activity', label: 'Aktivite', icon: ActivityIcon, count: activities.value.length }
])

// Tab keyboard navigation
const handleTabKeydown = (event, currentIndex) => {
  const tabsList = tabs.value
  let newIndex = currentIndex

  switch (event.key) {
    case 'ArrowLeft':
    case 'ArrowUp':
      event.preventDefault()
      newIndex = currentIndex === 0 ? tabsList.length - 1 : currentIndex - 1
      break
    case 'ArrowRight':
    case 'ArrowDown':
      event.preventDefault()
      newIndex = currentIndex === tabsList.length - 1 ? 0 : currentIndex + 1
      break
    case 'Home':
      event.preventDefault()
      newIndex = 0
      break
    case 'End':
      event.preventDefault()
      newIndex = tabsList.length - 1
      break
    default:
      return
  }

  activeTab.value = tabsList[newIndex].name
  // Focus the new tab
  const newTabEl = document.getElementById(`tab-${tabsList[newIndex].name}`)
  newTabEl?.focus()
}

// Loading states
const saving = ref(false)
const savingPassword = ref(false)
const savingSettings = ref(false)
const verifying2FA = ref(false)
const loadingMore = ref(false)
const deletingAccount = ref(false)

// Modals
const show2FABackupCodes = ref(false)
const show2FASetup = ref(false)
const showDeleteConfirm = ref(false)
const showAvatarUpload = ref(false)
const showCoverUpload = ref(false)
const showAllAchievements = ref(false)

// Delete confirmation
const deleteConfirmText = ref('')

// 2FA Setup
const twoFAStep = ref(1)
const twoFASecret = ref('')
const twoFACode = ref('')

// UI Store for notifications
const uiStore = useUIStore()

// Email Verification
const emailVerification = reactive({
  sending: false,
  canResend: true,
  countdown: 0
})
let emailCountdownInterval = null

// Show email verification section only for non-Steam users
const showEmailVerificationSection = computed(() => {
  // Steam users don't need email verification
  if (user.value?.steam_id) return false
  // Show for all non-Steam users (whether verified or not)
  return true
})

const sendEmailVerification = async () => {
  if (emailVerification.sending || !emailVerification.canResend) return

  emailVerification.sending = true
  try {
    await authAPI.sendVerificationEmail()
    uiStore.addNotification({
      type: 'success',
      message: 'Dogrulama emaili gonderildi! Lutfen gelen kutunuzu kontrol edin.'
    })
    startEmailCountdown(60)
  } catch (error) {
    const message = error.response?.data?.detail || 'Email gonderilemedi'
    uiStore.addNotification({
      type: 'error',
      message
    })
    // Rate limit hatasi ise countdown baslat
    if (error.response?.status === 429) {
      const match = message.match(/(\d+)/)
      if (match) {
        startEmailCountdown(parseInt(match[1]))
      }
    }
  } finally {
    emailVerification.sending = false
  }
}

const startEmailCountdown = (seconds) => {
  emailVerification.countdown = seconds
  emailVerification.canResend = false
  if (emailCountdownInterval) clearInterval(emailCountdownInterval)
  emailCountdownInterval = setInterval(() => {
    emailVerification.countdown--
    if (emailVerification.countdown <= 0) {
      clearInterval(emailCountdownInterval)
      emailVerification.canResend = true
    }
  }, 1000)
}

const checkEmailVerificationStatus = async () => {
  if (!user.value || user.value.steam_id || user.value.email_verified) return

  try {
    const status = await authAPI.getEmailVerificationStatus()
    if (!status.resend_available && status.resend_wait_seconds > 0) {
      startEmailCountdown(status.resend_wait_seconds)
    }
  } catch (error) {
    // Sessiz hata
  }
}

// Forms
const profileForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  country: '',
  bio: ''
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const settings = reactive({
  email_notifications: true,
  server_alerts: true,
  security_alerts: true,
  marketing_emails: false,
  public_profile: false,
  show_online_status: true,
  show_activity: true,
  show_servers: true
})

// Password strength
const passwordStrength = ref(0)
const passwordChecks = reactive({
  minLength: false,
  hasUpper: false,
  hasLower: false,
  hasNumber: false,
  hasSpecial: false
})

const checkPasswordStrength = () => {
  const pwd = passwordForm.new_password
  passwordChecks.minLength = pwd.length >= 8
  passwordChecks.hasUpper = /[A-Z]/.test(pwd)
  passwordChecks.hasLower = /[a-z]/.test(pwd)
  passwordChecks.hasNumber = /[0-9]/.test(pwd)
  passwordChecks.hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(pwd)
  const checks = Object.values(passwordChecks).filter(Boolean).length
  passwordStrength.value = checks * 20
}

const strengthClass = computed(() => {
  if (passwordStrength.value <= 20) return 'strength-weak'
  if (passwordStrength.value <= 40) return 'strength-fair'
  if (passwordStrength.value <= 60) return 'strength-good'
  if (passwordStrength.value <= 80) return 'strength-strong'
  return 'strength-excellent'
})

const strengthText = computed(() => {
  if (passwordStrength.value <= 20) return 'Çok Zayıf'
  if (passwordStrength.value <= 40) return 'Zayıf'
  if (passwordStrength.value <= 60) return 'Orta'
  if (passwordStrength.value <= 80) return 'Güçlü'
  return 'Çok Güçlü'
})

// Sessions
const sessions = ref([])
const sessionsLoading = ref(false)

const fetchSessions = async () => {
  sessionsLoading.value = true
  try {
    const response = await apiCall('/api/user/sessions')
    sessions.value = (response.sessions || response || []).map(s => ({
      id: s.id,
      device_name: s.device_name || parseUserAgent(s.user_agent),
      device_type: detectDeviceType(s.user_agent),
      ip: maskIP(s.ip_address || s.ip),
      location: s.location || 'Bilinmiyor',
      last_activity: new Date(s.last_activity || s.created_at),
      is_current: s.is_current || false
    }))
  } catch (error) {
    console.error('Sessions fetch error:', error)
  } finally {
    sessionsLoading.value = false
  }
}

const parseUserAgent = (ua) => {
  if (!ua) return 'Bilinmeyen Cihaz'
  if (ua.includes('Chrome')) return 'Chrome'
  if (ua.includes('Firefox')) return 'Firefox'
  if (ua.includes('Safari')) return 'Safari'
  if (ua.includes('Edge')) return 'Edge'
  return 'Tarayıcı'
}

const detectDeviceType = (ua) => {
  if (!ua) return 'desktop'
  const lower = ua.toLowerCase()
  if (lower.includes('mobile') || lower.includes('android') || lower.includes('iphone')) return 'mobile'
  if (lower.includes('tablet') || lower.includes('ipad')) return 'tablet'
  return 'desktop'
}

const maskIP = (ip) => {
  if (!ip) return '***.***.***'
  const parts = ip.split('.')
  if (parts.length === 4) {
    return `${parts[0]}.${parts[1]}.***.***`
  }
  return ip.substring(0, ip.length / 2) + '***'
}

const getDeviceClass = (type) => `device-${type}`

// Activities
const activities = ref([])
const activitiesLoading = ref(false)
const activitiesPage = ref(1)
const hasMoreActivities = ref(true)

const fetchActivities = async (loadMore = false) => {
  if (loadMore) {
    loadingMore.value = true
  } else {
    activitiesLoading.value = true
  }

  try {
    const response = await apiCall(`/api/security/activity?page=${activitiesPage.value}&limit=10`)
    const newActivities = (response.activities || response || []).map(a => ({
      id: a.id,
      type: getActivityType(a.action),
      title: formatActivityTitle(a.action),
      description: a.details || a.description || '',
      created_at: new Date(a.created_at || a.timestamp),
      metadata: a.metadata || (a.ip_address ? { IP: maskIP(a.ip_address) } : null)
    }))

    if (loadMore) {
      activities.value = [...activities.value, ...newActivities]
    } else {
      activities.value = newActivities
    }

    hasMoreActivities.value = newActivities.length === 10
    if (loadMore) activitiesPage.value++
  } catch (error) {
    console.error('Activities fetch error:', error)
    // Fallback to empty if API fails
    if (!loadMore) activities.value = []
  } finally {
    activitiesLoading.value = false
    loadingMore.value = false
  }
}

const getActivityType = (action) => {
  if (!action) return 'info'
  const lower = action.toLowerCase()
  if (lower.includes('success') || lower.includes('create') || lower.includes('update')) return 'success'
  if (lower.includes('fail') || lower.includes('error') || lower.includes('delete')) return 'error'
  if (lower.includes('warn') || lower.includes('attempt')) return 'warning'
  return 'info'
}

const formatActivityTitle = (action) => {
  const titles = {
    'login': 'Giriş yapıldı',
    'login_success': 'Başarılı giriş',
    'login_failed': 'Başarısız giriş denemesi',
    'logout': 'Çıkış yapıldı',
    'password_change': 'Şifre değiştirildi',
    'profile_update': 'Profil güncellendi',
    '2fa_enabled': '2FA etkinleştirildi',
    '2fa_disabled': '2FA devre dışı bırakıldı',
    'session_revoked': 'Oturum sonlandırıldı',
    'server_created': 'Sunucu oluşturuldu',
    'server_deleted': 'Sunucu silindi'
  }
  return titles[action] || action || 'Aktivite'
}

const getActivityIcon = (type) => {
  const icons = { info: InfoIcon, success: CheckCircleIcon, warning: AlertCircleIcon, error: XCircleIcon }
  return icons[type] || InfoIcon
}

// Backup codes (fetched from API during 2FA setup)
const backupCodes = ref([])

// Achievements - API'den çekilecek
const achievements = ref([])
const allAchievements = ref([])

// Connected accounts - API'den çekilecek
const connectedAccounts = reactive({
  steam: { connected: false, username: null },
  discord: { connected: false, username: null }
})

// Formatters
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true, locale: tr })
}

const formatDate = (timestamp) => {
  if (!timestamp) return ''
  return format(new Date(timestamp), 'dd MMMM yyyy', { locale: tr })
}

const formatMemberSince = (timestamp) => {
  if (!timestamp) return 'Yeni'
  const date = new Date(timestamp)
  const now = new Date()
  const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
  if (diffDays < 30) return `${diffDays} gun`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} ay`
  return `${Math.floor(diffDays / 365)} yil`
}

// API helper
const apiCall = async (url, options = {}) => {
  const token = localStorage.getItem('access_token')
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers
    }
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Bir hata oluştu' }))
    throw new Error(error.detail || 'İşlem başarısız')
  }
  return response.json()
}

// Profile methods
const updateProfile = async () => {
  // Validation
  if (!profileForm.email || !isValidEmail(profileForm.email)) {
    window.$message?.error('Geçerli bir e-posta adresi girin')
    return
  }

  saving.value = true
  try {
    const data = {
      display_name: profileForm.first_name && profileForm.last_name
        ? `${profileForm.first_name} ${profileForm.last_name}`
        : null,
      email: profileForm.email,
      bio: profileForm.bio
    }

    await apiCall('/api/user/profile', {
      method: 'PUT',
      body: JSON.stringify(data)
    })

    // Update local user data
    authStore.updateUser({
      email: profileForm.email,
      bio: profileForm.bio,
      display_name: data.display_name
    })

    window.$message?.success('Profil başarıyla güncellendi')
    hasUnsavedChanges.value = false
  } catch (error) {
    window.$message?.error(error.message || 'Profil güncellenemedi')
  } finally {
    saving.value = false
  }
}

// Password methods
const changePassword = async () => {
  // Validation
  if (!passwordForm.current_password) {
    window.$message?.error('Mevcut şifrenizi girin')
    return
  }
  if (!passwordForm.new_password) {
    window.$message?.error('Yeni şifre girin')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    window.$message?.error('Şifreler eşleşmiyor!')
    return
  }
  if (passwordStrength.value < 60) {
    window.$message?.warning('Lütfen daha güçlü bir şifre seçin (en az "Orta" seviye)')
    return
  }
  if (passwordForm.current_password === passwordForm.new_password) {
    window.$message?.error('Yeni şifre eskisiyle aynı olamaz')
    return
  }

  savingPassword.value = true
  try {
    await apiCall('/api/user/change-password', {
      method: 'POST',
      body: JSON.stringify({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
        confirm_password: passwordForm.confirm_password
      })
    })

    window.$message?.success('Şifre başarıyla güncellendi')
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    passwordStrength.value = 0
    Object.keys(passwordChecks).forEach(key => passwordChecks[key] = false)
  } catch (error) {
    window.$message?.error(error.message || 'Şifre güncellenemedi')
  } finally {
    savingPassword.value = false
  }
}

// 2FA methods
const twoFAQrCode = ref('')
const twoFALoading = ref(false)

const start2FASetup = async () => {
  show2FASetup.value = true
  twoFAStep.value = 1
  twoFALoading.value = true

  try {
    const response = await apiCall('/api/auth/2fa/setup', { method: 'POST' })
    twoFASecret.value = response.secret
    twoFAQrCode.value = response.qr_code || `otpauth://totp/AGTR:${user.value?.email}?secret=${response.secret}&issuer=AGTR`
    if (response.backup_codes) {
      backupCodes.value = response.backup_codes
    }
  } catch (error) {
    window.$message?.error(error.message || '2FA kurulumu başlatılamadı')
    show2FASetup.value = false
  } finally {
    twoFALoading.value = false
  }
}

const cancel2FASetup = () => {
  show2FASetup.value = false
  twoFAStep.value = 1
  twoFACode.value = ''
  twoFAQrCode.value = ''
}

const verify2FACode = async () => {
  if (twoFACode.value.length !== 6) {
    window.$message?.error('Lütfen 6 haneli kodu girin')
    return
  }
  if (!/^\d{6}$/.test(twoFACode.value)) {
    window.$message?.error('Kod sadece rakamlardan oluşmalı')
    return
  }

  verifying2FA.value = true
  try {
    const response = await apiCall('/api/auth/2fa/verify', {
      method: 'POST',
      body: JSON.stringify({ code: twoFACode.value })
    })

    if (response.backup_codes) {
      backupCodes.value = response.backup_codes
    }
    twoFAStep.value = 3

    // Update user 2FA status
    authStore.updateUser({ two_factor_enabled: true })
  } catch (error) {
    window.$message?.error(error.message || 'Doğrulama başarısız. Kodu kontrol edin.')
  } finally {
    verifying2FA.value = false
  }
}

const finish2FASetup = () => {
  show2FASetup.value = false
  twoFAStep.value = 1
  twoFACode.value = ''
  twoFAQrCode.value = ''
  window.$message?.success('2FA başarıyla etkinleştirildi!')
}

const disable2FA = () => {
  window.$dialog?.warning({
    title: 'Uyarı',
    content: '2FA\'yı devre dışı bırakmak hesabınızın güvenliğini azaltır. Devam etmek istediğinizden emin misiniz?',
    positiveText: 'Evet, Devre Dışı Bırak',
    negativeText: 'İptal',
    onPositiveClick: async () => {
      try {
        await apiCall('/api/auth/2fa/disable', { method: 'POST' })
        authStore.updateUser({ two_factor_enabled: false })
        window.$message?.success('2FA devre dışı bırakıldı')
      } catch (error) {
        window.$message?.error(error.message || '2FA devre dışı bırakılamadı')
      }
    }
  })
}

const downloadBackupCodes = () => {
  const header = 'AGTR Merkezi - 2FA Yedek Kodları\n'
  const warning = '⚠️ Bu kodları güvenli bir yerde saklayın!\n'
  const separator = '================================\n\n'
  const content = header + warning + separator + backupCodes.value.join('\n')

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `agtr-2fa-yedek-kodlar-${new Date().toISOString().split('T')[0]}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  window.$message?.success('Yedek kodlar indirildi')
}

const copyBackupCodes = () => {
  const text = backupCodes.value.join('\n')
  navigator.clipboard.writeText(text).then(() => {
    window.$message?.success('Yedek kodlar panoya kopyalandı')
  }).catch(() => {
    window.$message?.error('Kopyalama başarısız')
  })
}

const regenerateBackupCodes = async () => {
  window.$dialog?.warning({
    title: 'Yedek Kodları Yenile',
    content: 'Mevcut yedek kodlar geçersiz olacak. Devam etmek istediğinizden emin misiniz?',
    positiveText: 'Evet, Yenile',
    negativeText: 'İptal',
    onPositiveClick: async () => {
      try {
        const response = await apiCall('/api/auth/2fa/regenerate-backup-codes', { method: 'POST' })
        if (response.backup_codes) {
          backupCodes.value = response.backup_codes
          window.$message?.success('Yeni yedek kodlar oluşturuldu')
          show2FABackupCodes.value = true
        }
      } catch (error) {
        window.$message?.error(error.message || 'Yedek kodlar oluşturulamadı')
      }
    }
  })
}

// Session methods
const revokingSession = ref(null)

const revokeSession = (sessionId) => {
  window.$dialog?.warning({
    title: 'Oturumu Sonlandır',
    content: 'Bu oturumu sonlandırmak istediğinizden emin misiniz?',
    positiveText: 'Evet',
    negativeText: 'İptal',
    onPositiveClick: async () => {
      revokingSession.value = sessionId
      try {
        await apiCall(`/api/user/sessions/${sessionId}`, { method: 'DELETE' })
        sessions.value = sessions.value.filter(s => s.id !== sessionId)
        window.$message?.success('Oturum sonlandırıldı')
      } catch (error) {
        window.$message?.error(error.message || 'Oturum sonlandırılamadı')
      } finally {
        revokingSession.value = null
      }
    }
  })
}

const revokeAllSessions = () => {
  window.$dialog?.warning({
    title: 'Tüm Oturumları Sonlandır',
    content: 'Mevcut oturum hariç tüm oturumları sonlandırmak istediğinizden emin misiniz?',
    positiveText: 'Evet',
    negativeText: 'İptal',
    onPositiveClick: async () => {
      try {
        await apiCall('/api/user/sessions', { method: 'DELETE' })
        sessions.value = sessions.value.filter(s => s.is_current)
        window.$message?.success('Tüm oturumlar sonlandırıldı')
      } catch (error) {
        window.$message?.error(error.message || 'Oturumlar sonlandırılamadı')
      }
    }
  })
}

// Settings methods
const saveSettings = async () => {
  savingSettings.value = true
  try {
    await apiCall('/api/user/settings', {
      method: 'PUT',
      body: JSON.stringify({
        email_notifications: settings.email_notifications,
        server_alerts: settings.server_alerts,
        security_alerts: settings.security_alerts,
        marketing_emails: settings.marketing_emails,
        public_profile: settings.public_profile,
        show_online_status: settings.show_online_status,
        show_activity: settings.show_activity,
        show_servers: settings.show_servers
      })
    })
    window.$message?.success('Ayarlar kaydedildi')
  } catch (error) {
    // Settings endpoint might not exist yet, save locally
    localStorage.setItem('user_settings', JSON.stringify(settings))
    window.$message?.success('Ayarlar kaydedildi')
  } finally {
    savingSettings.value = false
  }
}

// Load settings from localStorage if API not available
const loadSettings = () => {
  const saved = localStorage.getItem('user_settings')
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      Object.assign(settings, parsed)
    } catch (e) {
      console.error('Settings parse error:', e)
    }
  }
}

// Account methods
const freezeAccount = () => {
  window.$dialog?.warning({
    title: 'Hesabı Dondur',
    content: 'Hesabınızı dondurmak istediğinizden emin misiniz? Bu işlem geri alınabilir.',
    positiveText: 'Evet, Dondur',
    negativeText: 'İptal',
    onPositiveClick: async () => {
      try {
        await apiCall('/api/user/freeze', { method: 'POST' })
        window.$message?.info('Hesabınız donduruldu')
        authStore.logout()
      } catch (error) {
        window.$message?.error(error.message || 'Hesap dondurulamadı')
      }
    }
  })
}

const deleteAccount = async () => {
  if (deleteConfirmText.value !== 'HESABIMI SIL') {
    window.$message?.error('Lütfen onay metnini doğru yazın')
    return
  }

  deletingAccount.value = true
  try {
    await apiCall('/api/user/delete', {
      method: 'DELETE',
      body: JSON.stringify({ confirmation: deleteConfirmText.value })
    })
    window.$message?.success('Hesabınız silindi')
    showDeleteConfirm.value = false
    authStore.logout()
  } catch (error) {
    window.$message?.error(error.message || 'Hesap silinemedi')
  } finally {
    deletingAccount.value = false
  }
}

// Connected accounts methods
const connectAccount = (provider) => {
  const redirectUrls = {
    steam: '/api/auth/steam/connect',
    discord: '/api/auth/discord/connect'
  }
  const url = redirectUrls[provider]
  if (url) {
    window.location.href = url
  } else {
    window.$message?.error('Bu bağlantı türü desteklenmiyor')
  }
}

const disconnectAccount = (provider) => {
  window.$dialog?.warning({
    title: 'Hesap Bağlantısını Kes',
    content: `${provider.charAt(0).toUpperCase() + provider.slice(1)} hesabının bağlantısını kesmek istediğinizden emin misiniz?`,
    positiveText: 'Evet',
    negativeText: 'İptal',
    onPositiveClick: async () => {
      try {
        await apiCall(`/api/auth/${provider}/disconnect`, { method: 'POST' })
        connectedAccounts[provider].connected = false
        connectedAccounts[provider].username = null
        window.$message?.success('Hesap bağlantısı kesildi')
      } catch (error) {
        window.$message?.error(error.message || 'Bağlantı kesilemedi')
      }
    }
  })
}

// Fetch connected accounts
const fetchConnectedAccounts = async () => {
  try {
    const response = await apiCall('/api/auth/connected-accounts')
    if (response.steam) {
      connectedAccounts.steam = response.steam
    }
    if (response.discord) {
      connectedAccounts.discord = response.discord
    }
  } catch (error) {
    // Use user data as fallback
    if (user.value?.steam_id) {
      connectedAccounts.steam = { connected: true, username: user.value.steam_id }
    }
  }
}

// Upload handlers
const uploadingAvatar = ref(false)
const uploadingCover = ref(false)

const handleAvatarUpload = async ({ file }) => {
  if (!file || !file.file) {
    window.$message?.error('Dosya seçilmedi')
    return
  }

  // Validate file
  const maxSize = 5 * 1024 * 1024 // 5MB
  if (file.file.size > maxSize) {
    window.$message?.error('Dosya boyutu 5MB\'dan küçük olmalı')
    return
  }

  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.file.type)) {
    window.$message?.error('Sadece JPG, PNG, GIF veya WebP formatları desteklenir')
    return
  }

  uploadingAvatar.value = true
  try {
    const formData = new FormData()
    formData.append('file', file.file)

    const token = localStorage.getItem('access_token')
    const response = await fetch('/api/user/avatar', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || 'Yükleme başarısız')
    }

    const data = await response.json()
    authStore.updateUser({ avatar: data.avatar_url || data.url })
    window.$message?.success('Profil fotoğrafı güncellendi')
    showAvatarUpload.value = false
  } catch (error) {
    window.$message?.error(error.message || 'Fotoğraf yüklenemedi')
  } finally {
    uploadingAvatar.value = false
  }
}

const handleCoverUpload = async ({ file }) => {
  if (!file || !file.file) {
    window.$message?.error('Dosya seçilmedi')
    return
  }

  const maxSize = 10 * 1024 * 1024 // 10MB for cover
  if (file.file.size > maxSize) {
    window.$message?.error('Dosya boyutu 10MB\'dan küçük olmalı')
    return
  }

  uploadingCover.value = true
  try {
    const formData = new FormData()
    formData.append('file', file.file)

    const token = localStorage.getItem('access_token')
    const response = await fetch('/api/user/cover', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || 'Yükleme başarısız')
    }

    window.$message?.success('Kapak fotoğrafı güncellendi')
    showCoverUpload.value = false
  } catch (error) {
    window.$message?.error(error.message || 'Kapak fotoğrafı yüklenemedi')
  } finally {
    uploadingCover.value = false
  }
}

// Load more activities
const loadMoreActivities = async () => {
  activitiesPage.value++
  await fetchActivities(true)
}

// Unsaved changes tracking
const hasUnsavedChanges = ref(false)
const initialFormState = ref({})

const trackChanges = () => {
  hasUnsavedChanges.value = JSON.stringify(profileForm) !== JSON.stringify(initialFormState.value)
}

const resetForm = () => {
  Object.assign(profileForm, initialFormState.value)
  hasUnsavedChanges.value = false
  window.$message?.info('Değişiklikler geri alındı')
}

// Bio character counter
const bioMaxLength = 500
const bioCharCount = computed(() => profileForm.bio?.length || 0)
const bioRemaining = computed(() => bioMaxLength - bioCharCount.value)

// Initialize form data and fetch real data
onMounted(async () => {
  // Initialize form from user data
  if (user.value) {
    const displayParts = user.value.display_name?.split(' ') || []
    profileForm.username = user.value.username || ''
    profileForm.email = user.value.email || ''
    profileForm.first_name = displayParts[0] || user.value.first_name || ''
    profileForm.last_name = displayParts.slice(1).join(' ') || user.value.last_name || ''
    profileForm.phone = user.value.phone || ''
    profileForm.country = user.value.country || ''
    profileForm.bio = user.value.bio || ''
    initialFormState.value = { ...profileForm }
  }

  // Load settings
  loadSettings()

  // Fetch real data in parallel
  await Promise.allSettled([
    fetchSessions(),
    fetchActivities(),
    fetchConnectedAccounts(),
    fetch2FAStatus(),
    checkEmailVerificationStatus()
  ])
})

// Fetch 2FA status
const fetch2FAStatus = async () => {
  try {
    const response = await apiCall('/api/auth/2fa/status')
    if (response.enabled !== undefined) {
      authStore.updateUser({ two_factor_enabled: response.enabled })
    }
  } catch (error) {
    // Use existing user data
  }
}

// Watch for form changes
watch(profileForm, trackChanges, { deep: true })

// Watch user data changes
watch(user, (newUser) => {
  if (newUser && !hasUnsavedChanges.value) {
    const displayParts = newUser.display_name?.split(' ') || []
    profileForm.username = newUser.username || ''
    profileForm.email = newUser.email || ''
    profileForm.first_name = displayParts[0] || newUser.first_name || ''
    profileForm.last_name = displayParts.slice(1).join(' ') || newUser.last_name || ''
    profileForm.phone = newUser.phone || ''
    profileForm.country = newUser.country || ''
    profileForm.bio = newUser.bio || ''
    initialFormState.value = { ...profileForm }
  }
})

// Warn before leaving with unsaved changes
onBeforeUnmount(() => {
  if (hasUnsavedChanges.value) {
    // Note: Browser may not show custom message
    window.onbeforeunload = () => 'Kaydedilmemiş değişiklikler var!'
  }
})

// Cleanup
onUnmounted(() => {
  window.onbeforeunload = null
  if (emailCountdownInterval) clearInterval(emailCountdownInterval)
})
</script>

<style scoped>
/* Base Styles */
.profile-page {
  background: #0a0a0a;
  min-height: 100vh;
  overflow-x: hidden;
  width: 100%;
  max-width: 100vw;
}

/* Hero Section with Gradient & Pattern */
.hero-section {
  position: relative;
  height: 280px;
  overflow: hidden;
}

.hero-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 30%, #1a1a1a 70%, #0a0a0a 100%);
}

.hero-pattern {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 1px, transparent 1px),
    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.08) 1px, transparent 1px),
    radial-gradient(circle at 40% 80%, rgba(255,255,255,0.06) 1px, transparent 1px);
  background-size: 60px 60px, 80px 80px, 100px 100px;
  animation: patternMove 20s linear infinite;
}

@keyframes patternMove {
  0% { background-position: 0 0, 0 0, 0 0; }
  100% { background-position: 60px 60px, -80px 80px, 100px -100px; }
}

.hero-glow {
  position: absolute;
  top: 50%;
  left: 30%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(249,115,22,0.3) 0%, transparent 70%);
  transform: translate(-50%, -50%);
  filter: blur(60px);
  animation: glowPulse 4s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.8; transform: translate(-50%, -50%) scale(1.1); }
}

.cover-edit-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(255,255,255,0.1) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2) !important;
  z-index: 10;
}

/* Glass Cards */
.glass-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s ease;
}

.glass-card:hover {
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.glass-card-hero {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

/* Avatar with Animated Ring */
.avatar-container {
  position: relative;
}

.avatar-ring-animated {
  padding: 4px;
  background: conic-gradient(from 0deg, #f97316, #ea580c, #f97316, #fbbf24, #f97316);
  border-radius: 50%;
  animation: ringRotate 3s linear infinite;
}

@keyframes ringRotate {
  0% { background: conic-gradient(from 0deg, #f97316, #ea580c, #f97316, #fbbf24, #f97316); }
  100% { background: conic-gradient(from 360deg, #f97316, #ea580c, #f97316, #fbbf24, #f97316); }
}

.avatar-ring-inner {
  padding: 3px;
  background: #111;
  border-radius: 50%;
}

.avatar-main {
  border: none !important;
}

/* Online Status Ring */
.status-ring {
  position: absolute;
  bottom: 10px;
  right: 10px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #111;
}

.status-ring.status-online {
  background: #22c55e;
  box-shadow: 0 0 12px rgba(34, 197, 94, 0.6);
}

.status-ring.status-online .status-dot {
  width: 8px;
  height: 8px;
  background: #fff;
  border-radius: 50%;
  animation: statusPulse 2s ease-in-out infinite;
}

@keyframes statusPulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(0.8); opacity: 0.7; }
}

.status-ring.status-away {
  background: #eab308;
  box-shadow: 0 0 12px rgba(234, 179, 8, 0.6);
}

.status-ring.status-offline {
  background: #6b7280;
}

.avatar-edit-btn {
  position: absolute;
  bottom: 0;
  left: 0;
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.3s ease;
}

.avatar-container:hover .avatar-edit-btn {
  opacity: 1;
  transform: scale(1);
}

.level-badge-floating {
  position: absolute;
  top: -8px;
  right: -8px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  color: white;
  border: 2px solid #111;
  box-shadow: 0 4px 16px rgba(249, 115, 22, 0.4);
}

/* Verification & Role Badges */
.verification-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(34, 197, 94, 0.1));
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 20px;
  color: #22c55e;
  font-size: 12px;
  font-weight: 500;
}

.role-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

/* Stats Row */
.stats-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.06);
  transform: translateY(-2px);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon-orange {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(249, 115, 22, 0.1));
  color: #f97316;
}

.stat-icon-blue {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.1));
  color: #3b82f6;
}

.stat-icon-green {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(34, 197, 94, 0.1));
  color: #22c55e;
}

.stat-icon-purple {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(168, 85, 247, 0.1));
  color: #a855f7;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 11px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Level Progress */
.level-progress-section {
  max-width: 500px;
}

.level-icon {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.xp-display {
  font-size: 14px;
}

.level-progress-track {
  height: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  overflow: hidden;
  position: relative;
}

.level-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #f97316, #fbbf24);
  border-radius: 5px;
  position: relative;
  transition: width 0.5s ease;
}

.level-progress-glow {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 20px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4));
  animation: progressGlow 1.5s ease-in-out infinite;
}

@keyframes progressGlow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Circular Progress */
.completeness-section {
  flex-shrink: 0;
}

.completeness-card {
  padding: 24px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
}

.circular-progress {
  width: 120px;
  height: 120px;
  margin: 0 auto;
  position: relative;
}

.circular-progress svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.circular-progress .progress-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.1);
  stroke-width: 8;
}

.circular-progress .progress-fill {
  fill: none;
  stroke: #f97316;
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 283;
  stroke-dashoffset: calc(283 - (283 * var(--progress)) / 100);
  transition: stroke-dashoffset 0.5s ease;
}

.progress-content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.progress-value {
  font-size: 28px;
  font-weight: 700;
  color: #f97316;
}

.progress-label {
  font-size: 11px;
  color: #6b7280;
  text-transform: uppercase;
}

/* Tabs Navigation */
.tabs-navigation {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.tabs-container {
  display: inline-flex;
  gap: 8px;
  padding: 6px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.tab-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 24px;
  background: transparent;
  border: none;
  border-radius: 16px;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.tab-item:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.tab-item.tab-active {
  color: #f97316;
  background: rgba(249, 115, 22, 0.1);
}

.tab-indicator {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 3px;
  background: #f97316;
  border-radius: 2px;
  animation: indicatorSlide 0.3s ease;
}

@keyframes indicatorSlide {
  from { width: 0; opacity: 0; }
  to { width: 24px; opacity: 1; }
}

.tab-badge {
  padding: 2px 8px;
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

/* Tab Transitions */
.tab-slide-enter-active,
.tab-slide-leave-active {
  transition: all 0.3s ease;
}

.tab-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.tab-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* Section Headers */
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.section-header.danger .section-icon {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1));
  color: #ef4444;
}

.section-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(249, 115, 22, 0.1));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f97316;
}

.section-icon-green {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1)) !important;
  color: #10b981 !important;
}

.section-icon-yellow {
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.2), rgba(234, 179, 8, 0.1)) !important;
  color: #eab308 !important;
}

.email-verified-state,
.email-not-verified-state {
  margin-top: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
}

/* Modern Input Group */
.input-group {
  position: relative;
}

.input-icon-wrapper {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  z-index: 1;
  pointer-events: none;
}

.input-icon-wrapper.textarea-icon {
  top: 20px;
  transform: none;
}

.modern-input :deep(.n-input) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 14px !important;
  padding-left: 48px !important;
  min-height: 52px;
  transition: all 0.3s ease !important;
}

.modern-textarea :deep(.n-input) {
  padding-top: 16px !important;
}

.bio-counter {
  position: absolute;
  bottom: 8px;
  right: 12px;
  font-size: 11px;
  color: #6b7280;
  pointer-events: none;
}

.bio-counter-warning {
  color: #f59e0b;
}

.modern-input :deep(.n-input:hover) {
  border-color: rgba(255, 255, 255, 0.2) !important;
}

.modern-input :deep(.n-input:focus-within) {
  border-color: #f97316 !important;
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15) !important;
}

.modern-input :deep(.n-input.n-input--error-status) {
  border-color: #ef4444 !important;
}

.input-valid-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: #22c55e;
}

.input-invalid-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: #ef4444;
}

/* Buttons */
.btn-save {
  background: linear-gradient(135deg, #f97316, #ea580c) !important;
  border: none !important;
  font-weight: 600;
}

.btn-save:hover {
  background: linear-gradient(135deg, #ea580c, #dc2626) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(249, 115, 22, 0.4);
}

.btn-cancel {
  color: #9ca3af !important;
}

/* Connected Accounts */
.connected-accounts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.account-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  transition: all 0.3s ease;
}

.account-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.account-item.connected {
  border-color: rgba(34, 197, 94, 0.3);
}

.account-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.account-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.steam-icon {
  background: linear-gradient(135deg, #1b2838, #2a475e);
}

.discord-icon {
  background: linear-gradient(135deg, #5865f2, #7289da);
}

/* Badges Grid */
.badges-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.badge-item {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.15), rgba(249, 115, 22, 0.05));
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 14px;
  color: #f97316;
  transition: all 0.3s ease;
  cursor: pointer;
}

.badge-item:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 20px rgba(249, 115, 22, 0.3);
}

.badge-item.badge-locked {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 255, 255, 0.08);
  color: #4b5563;
  opacity: 0.5;
}

/* Password Strength */
.password-strength-section {
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
}

.strength-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.strength-text {
  font-size: 13px;
  font-weight: 600;
}

.strength-text.strength-weak { color: #ef4444; }
.strength-text.strength-fair { color: #f97316; }
.strength-text.strength-good { color: #eab308; }
.strength-text.strength-strong { color: #22c55e; }
.strength-text.strength-excellent { color: #10b981; }

.strength-bars {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
}

.strength-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  transition: all 0.3s ease;
}

.strength-bar.active.strength-weak { background: #ef4444; }
.strength-bar.active.strength-fair { background: #f97316; }
.strength-bar.active.strength-good { background: #eab308; }
.strength-bar.active.strength-strong { background: #22c55e; }
.strength-bar.active.strength-excellent { background: #10b981; }

.strength-requirements {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.requirement {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #6b7280;
}

.requirement.met {
  color: #22c55e;
}

/* 2FA Wizard */
.twofa-wizard {
  padding: 24px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
}

.wizard-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin-bottom: 32px;
}

.wizard-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  color: #6b7280;
  transition: all 0.3s ease;
}

.wizard-step.active .step-circle {
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-color: #f97316;
  color: white;
}

.wizard-step.completed .step-circle {
  background: #22c55e;
  border-color: #22c55e;
  color: white;
}

.step-label {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
}

.wizard-step.active .step-label {
  color: #f97316;
}

.step-line {
  width: 60px;
  height: 2px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0 8px;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.step-line.active {
  background: #f97316;
}

.wizard-content {
  max-width: 400px;
  margin: 0 auto;
}

.qr-placeholder {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.qr-frame {
  padding: 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.qr-code {
  width: 160px;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 12px;
}

.secret-code {
  display: inline-block;
  padding: 14px 28px;
  background: rgba(249, 115, 22, 0.1);
  border: 1px solid rgba(249, 115, 22, 0.3);
  border-radius: 12px;
  font-family: 'Courier New', monospace;
  font-size: 18px;
  letter-spacing: 3px;
  color: #f97316;
}

.otp-container {
  max-width: 200px;
  margin: 0 auto;
}

.otp-input :deep(.n-input) {
  text-align: center !important;
  font-size: 28px !important;
  letter-spacing: 10px;
  font-family: 'Courier New', monospace;
  padding-left: 24px !important;
}

.success-icon-wrapper {
  width: 80px;
  height: 80px;
  margin: 0 auto;
  background: rgba(34, 197, 94, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: successPop 0.5s ease;
}

@keyframes successPop {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.backup-codes {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 16px;
}

.backup-code {
  padding: 14px;
  background: rgba(249, 115, 22, 0.1);
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 10px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #f97316;
  text-align: center;
}

/* Sessions Grid */
.sessions-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.session-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.session-card:hover {
  background: rgba(255, 255, 255, 0.05);
}

.session-device-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.session-device-icon.device-desktop {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.1));
  color: #3b82f6;
}

.session-device-icon.device-mobile {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(34, 197, 94, 0.1));
  color: #22c55e;
}

.session-device-icon.device-tablet {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(168, 85, 247, 0.1));
  color: #a855f7;
}

.session-details {
  flex: 1;
  min-width: 0;
}

.current-badge {
  padding: 3px 10px;
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

.session-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #6b7280;
}

/* Toggle List */
.toggle-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.toggle-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 14px;
  transition: all 0.3s ease;
}

.toggle-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.toggle-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.toggle-info h4 {
  font-weight: 500;
  margin-bottom: 2px;
}

.toggle-info p {
  font-size: 13px;
  color: #6b7280;
}

/* Danger Zone */
.danger-zone-card {
  background: rgba(239, 68, 68, 0.05);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.danger-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.danger-action-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: rgba(239, 68, 68, 0.05);
  border: 1px solid rgba(239, 68, 68, 0.1);
  border-radius: 14px;
}

/* Activity Timeline */
.activity-timeline {
  position: relative;
}

.timeline-entry {
  display: flex;
  gap: 16px;
  position: relative;
  padding-bottom: 24px;
}

.timeline-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.timeline-icon.icon-info {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.1));
  color: #3b82f6;
}

.timeline-icon.icon-success {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(34, 197, 94, 0.1));
  color: #22c55e;
}

.timeline-icon.icon-warning {
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.2), rgba(234, 179, 8, 0.1));
  color: #eab308;
}

.timeline-icon.icon-error {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1));
  color: #ef4444;
}

.timeline-connector {
  position: absolute;
  left: 19px;
  top: 44px;
  bottom: 0;
  width: 2px;
  background: rgba(255, 255, 255, 0.1);
}

.timeline-card {
  flex: 1;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 6px;
}

.timeline-header h4 {
  font-weight: 500;
}

.timeline-time {
  font-size: 12px;
  color: #6b7280;
}

.timeline-description {
  font-size: 14px;
  color: #9ca3af;
}

.timeline-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.timeline-tag {
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  font-size: 11px;
  color: #9ca3af;
}

/* Modal Styles */
.modal-glass :deep(.n-card) {
  background: rgba(20, 20, 20, 0.95) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-lg :deep(.n-card) {
  max-width: 800px;
}

/* Upload Zone */
.upload-zone {
  padding: 20px;
}

.upload-content {
  padding: 48px;
  border: 2px dashed rgba(249, 115, 22, 0.3);
  border-radius: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-content:hover {
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.05);
}

/* Achievements Modal */
.achievements-modal-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.achievement-modal-card {
  padding: 24px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  text-align: center;
  transition: all 0.3s ease;
}

.achievement-modal-card:hover:not(.locked) {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.achievement-modal-card.locked {
  opacity: 0.5;
}

.achievement-modal-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(249, 115, 22, 0.1));
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f97316;
}

.achievement-modal-card.locked .achievement-modal-icon {
  background: rgba(255, 255, 255, 0.05);
  color: #6b7280;
}

.achievement-modal-card h4 {
  font-weight: 600;
  margin-bottom: 4px;
}

.achievement-modal-card p {
  font-size: 13px;
  color: #6b7280;
}

.achievement-date {
  display: block;
  margin-top: 12px;
  font-size: 12px;
  color: #22c55e;
}

.achievement-progress-bar {
  margin-top: 12px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  position: relative;
}

.achievement-progress-bar .progress-fill {
  height: 100%;
  background: #f97316;
  border-radius: 3px;
}

.achievement-progress-bar span {
  position: absolute;
  right: 0;
  top: 10px;
  font-size: 11px;
  color: #6b7280;
}

/* Responsive */
@media (max-width: 1024px) {
  .completeness-section {
    width: 100%;
    margin-top: 24px;
  }

  .completeness-card {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .circular-progress {
    width: 80px;
    height: 80px;
    flex-shrink: 0;
  }

  .progress-value {
    font-size: 20px;
  }
}

@media (max-width: 768px) {
  .hero-section {
    height: 200px;
  }

  .tabs-container {
    width: 100%;
  }

  .tab-item {
    flex: 1;
    justify-content: center;
    padding: 12px 16px;
  }

  .tab-label {
    display: none;
  }

  .stats-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-label {
    display: none;
  }

  .backup-codes {
    grid-template-columns: 1fr;
  }

  .wizard-steps {
    transform: scale(0.85);
  }
}

/* Loading Skeletons */
.skeleton {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.06) 0%,
    rgba(255, 255, 255, 0.12) 50%,
    rgba(255, 255, 255, 0.06) 100%
  );
  background-size: 200% 100%;
  animation: skeletonShimmer 1.5s ease-in-out infinite;
  border-radius: 6px;
}

@keyframes skeletonShimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.skeleton-card {
  pointer-events: none;
}

.skeleton-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  flex-shrink: 0;
}

.skeleton-title {
  height: 18px;
  width: 60%;
  margin-bottom: 8px;
}

.skeleton-text {
  height: 14px;
  width: 80%;
  margin-bottom: 6px;
}

.skeleton-text-sm {
  height: 12px;
  width: 40%;
}

.skeleton-entry .timeline-icon {
  background: rgba(255, 255, 255, 0.06);
  animation: skeletonShimmer 1.5s ease-in-out infinite;
  background-size: 200% 100%;
}

.skeleton-entry .timeline-card {
  opacity: 0.7;
}

/* Empty States */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
  background: rgba(255, 255, 255, 0.02);
  border: 1px dashed rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  margin: 16px 0;
}

.empty-state svg {
  opacity: 0.5;
}

/* Screen Reader Only */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* Focus States for Accessibility */
.tab-item:focus-visible {
  outline: 2px solid #f97316;
  outline-offset: 2px;
}

.n-button:focus-visible {
  outline: 2px solid #f97316;
  outline-offset: 2px;
}

.n-input:focus-within {
  border-color: #f97316 !important;
  box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.2) !important;
}

.n-switch:focus-visible {
  outline: 2px solid #f97316;
  outline-offset: 2px;
}

/* High Contrast Mode Support */
@media (prefers-contrast: high) {
  .glass-card,
  .glass-card-hero {
    border-width: 2px;
    border-color: rgba(255, 255, 255, 0.3);
  }

  .tab-item.tab-active {
    border: 2px solid #f97316;
  }

  .empty-state {
    border-style: solid;
    border-width: 2px;
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }

  .skeleton {
    animation: none;
    background: rgba(255, 255, 255, 0.08);
  }
}
</style>
