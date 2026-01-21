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
            <div class="level-badge-floating">
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
                <span>Doğrulanmis</span>
              </div>

              <!-- Role Badge -->
              <div class="role-badge" :style="getRoleBadgeStyle(userRank)">
                <CrownIcon class="w-3.5 h-3.5" />
                <span>{{ userRank }}</span>
              </div>
            </div>

            <p class="text-gray-400 mb-5 flex items-center gap-2">
              <MailIcon class="w-4 h-4" />
              {{ user?.email || 'E-posta eklenmemis' }}
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
                  <span class="stat-label">Basari</span>
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
                Sonraki seviyeye {{ (nextLevelXP - currentXP).toLocaleString() }} XP kaldi
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
      <div class="tabs-navigation mb-8">
        <div class="tabs-container">
          <button
            v-for="tab in tabs"
            :key="tab.name"
            class="tab-item"
            :class="{ 'tab-active': activeTab === tab.name }"
            @click="activeTab = tab.name"
          >
            <component :is="tab.icon" class="w-5 h-5" />
            <span class="tab-label">{{ tab.label }}</span>
            <span v-if="tab.count !== undefined" class="tab-badge">{{ tab.count }}</span>
            <div v-if="activeTab === tab.name" class="tab-indicator"></div>
          </button>
        </div>
      </div>

      <!-- Tab Content with Smooth Transitions -->
      <Transition name="tab-slide" mode="out-in">
        <!-- Profile Tab -->
        <div v-if="activeTab === 'profile'" key="profile" class="tab-content">
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

                <n-form @submit.prevent="updateProfile" class="space-y-5">
                  <div class="grid md:grid-cols-2 gap-5">
                    <!-- Modern Input with Icon -->
                    <div class="input-group">
                      <div class="input-icon-wrapper">
                        <UserIcon class="w-4 h-4" />
                      </div>
                      <n-input
                        v-model:value="profileForm.username"
                        placeholder="Kullanıcı Adı"
                        class="modern-input"
                        :status="validationStatus.username"
                      />
                      <CheckCircleIcon v-if="profileForm.username" class="input-valid-icon" />
                    </div>

                    <div class="input-group">
                      <div class="input-icon-wrapper">
                        <MailIcon class="w-4 h-4" />
                      </div>
                      <n-input
                        v-model:value="profileForm.email"
                        type="email"
                        placeholder="E-posta Adresi"
                        class="modern-input"
                        :status="validationStatus.email"
                      />
                      <CheckCircleIcon v-if="isValidEmail(profileForm.email)" class="input-valid-icon" />
                      <XCircleIcon v-else-if="profileForm.email" class="input-invalid-icon" />
                    </div>

                    <div class="input-group">
                      <div class="input-icon-wrapper">
                        <UserIcon class="w-4 h-4" />
                      </div>
                      <n-input
                        v-model:value="profileForm.first_name"
                        placeholder="Ad"
                        class="modern-input"
                      />
                    </div>

                    <div class="input-group">
                      <div class="input-icon-wrapper">
                        <UserIcon class="w-4 h-4" />
                      </div>
                      <n-input
                        v-model:value="profileForm.last_name"
                        placeholder="Soyad"
                        class="modern-input"
                      />
                    </div>

                    <div class="input-group">
                      <div class="input-icon-wrapper">
                        <PhoneIcon class="w-4 h-4" />
                      </div>
                      <n-input
                        v-model:value="profileForm.phone"
                        placeholder="Telefon"
                        class="modern-input"
                      />
                    </div>

                    <div class="input-group">
                      <div class="input-icon-wrapper">
                        <GlobeIcon class="w-4 h-4" />
                      </div>
                      <n-input
                        v-model:value="profileForm.country"
                        placeholder="Ulke"
                        class="modern-input"
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
                      placeholder="Biyografi - Kendinizi tanitin..."
                      :rows="4"
                      class="modern-input modern-textarea"
                    />
                  </div>

                  <div class="flex justify-end gap-3 pt-2">
                    <n-button quaternary size="large" class="btn-cancel">İptal</n-button>
                    <n-button type="primary" size="large" attr-type="submit" :loading="saving" class="btn-save">
                      <template #icon><SaveIcon class="w-4 h-4" /></template>
                      Değişiklikleri Kaydet
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
                  <h3 class="section-title">Bagli Hesaplar</h3>
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
                          {{ connectedAccounts.steam.connected ? connectedAccounts.steam.username : 'Bagli degil' }}
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
                      Bagla
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
                          {{ connectedAccounts.discord.connected ? connectedAccounts.discord.username : 'Bagli degil' }}
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
                      Bagla
                    </n-button>
                  </div>
                </div>
              </div>

              <!-- Achievement Badges -->
              <div class="glass-card rounded-2xl p-6">
                <div class="section-header">
                  <div class="section-icon">
                    <AwardIcon class="w-5 h-5" />
                  </div>
                  <h3 class="section-title">Basari Rozetleri</h3>
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
                  Tum Basarilari Gor
                </n-button>
              </div>
            </div>
          </div>
        </div>

        <!-- Security Tab -->
        <div v-else-if="activeTab === 'security'" key="security" class="tab-content space-y-6">
          <!-- Password Change Section -->
          <div v-if="!isOAuthUser" class="glass-card rounded-2xl p-6">
            <div class="section-header">
              <div class="section-icon">
                <KeyIcon class="w-5 h-5" />
              </div>
              <h3 class="section-title">Şifre Degistir</h3>
            </div>

            <n-form @submit.prevent="changePassword" class="space-y-5">
              <div class="input-group">
                <div class="input-icon-wrapper">
                  <LockIcon class="w-4 h-4" />
                </div>
                <n-input
                  v-model:value="passwordForm.current_password"
                  type="password"
                  show-password-on="click"
                  placeholder="Mevcut Şifre"
                  class="modern-input"
                />
              </div>

              <div class="grid md:grid-cols-2 gap-5">
                <div class="input-group">
                  <div class="input-icon-wrapper">
                    <LockIcon class="w-4 h-4" />
                  </div>
                  <n-input
                    v-model:value="passwordForm.new_password"
                    type="password"
                    show-password-on="click"
                    placeholder="Yeni Şifre"
                    class="modern-input"
                    @input="checkPasswordStrength"
                  />
                </div>

                <div class="input-group">
                  <div class="input-icon-wrapper">
                    <LockIcon class="w-4 h-4" />
                  </div>
                  <n-input
                    v-model:value="passwordForm.confirm_password"
                    type="password"
                    show-password-on="click"
                    placeholder="Yeni Şifre (Tekrar)"
                    class="modern-input"
                    :status="passwordForm.confirm_password && passwordForm.new_password !== passwordForm.confirm_password ? 'error' : undefined"
                  />
                </div>
              </div>

              <!-- Password Strength Meter -->
              <div v-if="passwordForm.new_password" class="password-strength-section">
                <div class="strength-header">
                  <span class="text-sm text-gray-400">Şifre Gucu</span>
                  <span class="strength-text" :class="strengthClass">{{ strengthText }}</span>
                </div>
                <div class="strength-bars">
                  <div
                    v-for="i in 5"
                    :key="i"
                    class="strength-bar"
                    :class="{ 'active': passwordStrength >= i * 20, [strengthClass]: passwordStrength >= i * 20 }"
                  ></div>
                </div>
                <div class="strength-requirements">
                  <div class="requirement" :class="{ 'met': passwordChecks.minLength }">
                    <component :is="passwordChecks.minLength ? CheckCircleIcon : CircleIcon" class="w-3.5 h-3.5" />
                    <span>En az 8 karakter</span>
                  </div>
                  <div class="requirement" :class="{ 'met': passwordChecks.hasUpper }">
                    <component :is="passwordChecks.hasUpper ? CheckCircleIcon : CircleIcon" class="w-3.5 h-3.5" />
                    <span>Büyük harf</span>
                  </div>
                  <div class="requirement" :class="{ 'met': passwordChecks.hasLower }">
                    <component :is="passwordChecks.hasLower ? CheckCircleIcon : CircleIcon" class="w-3.5 h-3.5" />
                    <span>Küçük harf</span>
                  </div>
                  <div class="requirement" :class="{ 'met': passwordChecks.hasNumber }">
                    <component :is="passwordChecks.hasNumber ? CheckCircleIcon : CircleIcon" class="w-3.5 h-3.5" />
                    <span>Rakam</span>
                  </div>
                  <div class="requirement" :class="{ 'met': passwordChecks.hasSpecial }">
                    <component :is="passwordChecks.hasSpecial ? CheckCircleIcon : CircleIcon" class="w-3.5 h-3.5" />
                    <span>Özel karakter</span>
                  </div>
                </div>
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
              <h3 class="section-title">Iki Faktorlu Doğrulama (2FA)</h3>
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
              Iki faktorlu doğrulama, hesabınıza ek bir guvenlik katmani ekler.
            </p>

            <!-- 2FA Not Enabled -->
            <div v-if="!user?.two_factor_enabled && !show2FASetup">
              <n-button type="primary" size="large" @click="start2FASetup" class="btn-save">
                <template #icon><ShieldCheckIcon class="w-4 h-4" /></template>
                2FA'yi Etkinlestir
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
                  Uygulamanizda gorunen 6 haneli kodu girin.
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
                <h4 class="text-xl font-semibold mt-4 mb-2">2FA Basariyla Etkinlestirildi!</h4>
                <p class="text-gray-400 mb-6">
                  Bu yedek kodlari guvenli bir yerde saklayin.
                </p>
                <div class="backup-codes">
                  <div v-for="code in backupCodes" :key="code" class="backup-code">
                    {{ code }}
                  </div>
                </div>
                <div class="flex justify-center gap-3 mt-6">
                  <n-button size="large" @click="downloadBackupCodes">
                    <template #icon><DownloadIcon class="w-4 h-4" /></template>
                    Kodlari İndir
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
                  Yedek Kodlari Gor
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
                Tum Oturumlari Sonlandir
              </n-button>
            </div>

            <div class="sessions-grid">
              <div v-for="session in sessions" :key="session.id" class="session-card">
                <div class="session-device-icon" :class="getDeviceClass(session.device_type)">
                  <MonitorIcon v-if="session.device_type === 'desktop'" class="w-6 h-6" />
                  <SmartphoneIcon v-else-if="session.device_type === 'mobile'" class="w-6 h-6" />
                  <TabletIcon v-else class="w-6 h-6" />
                </div>
                <div class="session-details">
                  <div class="flex items-center gap-2 mb-1">
                    <h4 class="font-medium">{{ session.device_name }}</h4>
                    <span v-if="session.is_current" class="current-badge">Mevcut</span>
                  </div>
                  <div class="session-meta">
                    <span class="meta-item">
                      <GlobeIcon class="w-3 h-3" />
                      {{ session.ip }}
                    </span>
                    <span class="meta-item">
                      <MapPinIcon class="w-3 h-3" />
                      {{ session.location }}
                    </span>
                  </div>
                  <p class="text-xs text-gray-500 mt-1">
                    Son aktivite: {{ formatTime(session.last_activity) }}
                  </p>
                </div>
                <n-button
                  v-if="!session.is_current"
                  quaternary
                  size="small"
                  class="session-revoke"
                  @click="revokeSession(session.id)"
                >
                  <template #icon><LogOutIcon class="w-4 h-4" /></template>
                </n-button>
              </div>
            </div>
          </div>
        </div>

        <!-- Settings Tab -->
        <div v-else-if="activeTab === 'settings'" key="settings" class="tab-content space-y-6">
          <!-- Notification Preferences -->
          <div class="glass-card rounded-2xl p-6">
            <div class="section-header">
              <div class="section-icon">
                <BellIcon class="w-5 h-5" />
              </div>
              <h3 class="section-title">Bildirim Tercihleri</h3>
            </div>

            <div class="toggle-list">
              <div class="toggle-item">
                <div class="toggle-info">
                  <MailIcon class="w-5 h-5 text-gray-400" />
                  <div>
                    <h4>E-posta Bildirimleri</h4>
                    <p>Onemli güncellemeler için e-posta alin</p>
                  </div>
                </div>
                <n-switch v-model:value="settings.email_notifications" :disabled="!hasEmail" />
              </div>

              <div class="toggle-item">
                <div class="toggle-info">
                  <ServerIcon class="w-5 h-5 text-gray-400" />
                  <div>
                    <h4>Sunucu Uyarilari</h4>
                    <p>Sunucu durumu değişikliklerinde bildirim alin</p>
                  </div>
                </div>
                <n-switch v-model:value="settings.server_alerts" />
              </div>

              <div class="toggle-item">
                <div class="toggle-info">
                  <ShieldIcon class="w-5 h-5 text-gray-400" />
                  <div>
                    <h4>Guvenlik Bildirimleri</h4>
                    <p>Supheli aktivitelerde e-posta alin</p>
                  </div>
                </div>
                <n-switch v-model:value="settings.security_alerts" :disabled="!hasEmail" />
              </div>

              <div class="toggle-item">
                <div class="toggle-info">
                  <MegaphoneIcon class="w-5 h-5 text-gray-400" />
                  <div>
                    <h4>Pazarlama E-postalari</h4>
                    <p>Kampanya ve firsatlardan haberdar olun</p>
                  </div>
                </div>
                <n-switch v-model:value="settings.marketing_emails" :disabled="!hasEmail" />
              </div>
            </div>
          </div>

          <!-- Privacy Settings -->
          <div class="glass-card rounded-2xl p-6">
            <div class="section-header">
              <div class="section-icon">
                <EyeOffIcon class="w-5 h-5" />
              </div>
              <h3 class="section-title">Gizlilik Ayarlari</h3>
            </div>

            <div class="toggle-list">
              <div class="toggle-item">
                <div class="toggle-info">
                  <UsersIcon class="w-5 h-5 text-gray-400" />
                  <div>
                    <h4>Profil Gorunurlugu</h4>
                    <p>Profilinizi herkese acik veya gizli yapin</p>
                  </div>
                </div>
                <n-switch v-model:value="settings.public_profile" />
              </div>

              <div class="toggle-item">
                <div class="toggle-info">
                  <CircleDotIcon class="w-5 h-5 text-gray-400" />
                  <div>
                    <h4>Online Durumu</h4>
                    <p>Diger kullanıcılarin online durumunuzu gormesine izin verin</p>
                  </div>
                </div>
                <n-switch v-model:value="settings.show_online_status" />
              </div>

              <div class="toggle-item">
                <div class="toggle-info">
                  <ActivityIcon class="w-5 h-5 text-gray-400" />
                  <div>
                    <h4>Aktivite Gecmisi</h4>
                    <p>Aktivite gecmisinizi profilinizde gösterin</p>
                  </div>
                </div>
                <n-switch v-model:value="settings.show_activity" />
              </div>

              <div class="toggle-item">
                <div class="toggle-info">
                  <ServerIcon class="w-5 h-5 text-gray-400" />
                  <div>
                    <h4>Sunucu Listesi</h4>
                    <p>Sunucularinizi profilinizde gösterin</p>
                  </div>
                </div>
                <n-switch v-model:value="settings.show_servers" />
              </div>
            </div>
          </div>

          <!-- Save Settings -->
          <div class="flex justify-end">
            <n-button type="primary" size="large" @click="saveSettings" :loading="savingSettings" class="btn-save">
              <template #icon><SaveIcon class="w-4 h-4" /></template>
              Ayarlari Kaydet
            </n-button>
          </div>

          <!-- Danger Zone -->
          <div class="danger-zone-card rounded-2xl p-6">
            <div class="section-header danger">
              <div class="section-icon danger">
                <AlertTriangleIcon class="w-5 h-5" />
              </div>
              <h3 class="section-title text-red-500">Tehlikeli Bolge</h3>
            </div>
            <p class="text-gray-400 mb-6">Bu işlemler geri alinamaz. Dikkatli olun.</p>

            <div class="danger-actions">
              <div class="danger-action-item">
                <div>
                  <h4 class="font-medium">Hesabi Dondur</h4>
                  <p class="text-sm text-gray-400">Hesabınızi gecici olarak devre disi birakin</p>
                </div>
                <n-button type="warning" ghost @click="freezeAccount">
                  <template #icon><PauseCircleIcon class="w-4 h-4" /></template>
                  Dondur
                </n-button>
              </div>

              <div class="danger-action-item">
                <div>
                  <h4 class="font-medium">Hesabi Sil</h4>
                  <p class="text-sm text-gray-400">Hesabınızi ve tum verilerinizi kalici olarak silin</p>
                </div>
                <n-button type="error" ghost @click="showDeleteConfirm = true">
                  <template #icon><Trash2Icon class="w-4 h-4" /></template>
                  Hesabi Sil
                </n-button>
              </div>
            </div>
          </div>
        </div>

        <!-- Activity Tab -->
        <div v-else-if="activeTab === 'activity'" key="activity" class="tab-content">
          <div class="glass-card rounded-2xl p-6">
            <div class="section-header">
              <div class="section-icon">
                <ActivityIcon class="w-5 h-5" />
              </div>
              <h3 class="section-title">Aktivite Gecmisi</h3>
            </div>

            <!-- Activity Timeline -->
            <div class="activity-timeline">
              <div
                v-for="(activity, index) in activities"
                :key="activity.id"
                class="timeline-entry"
                :class="{ 'last': index === activities.length - 1 }"
              >
                <div class="timeline-icon" :class="`icon-${activity.type}`">
                  <component :is="getActivityIcon(activity.type)" class="w-4 h-4" />
                </div>
                <div class="timeline-connector" v-if="index !== activities.length - 1"></div>
                <div class="timeline-card">
                  <div class="timeline-header">
                    <h4>{{ activity.title }}</h4>
                    <span class="timeline-time">{{ formatTime(activity.created_at) }}</span>
                  </div>
                  <p class="timeline-description">{{ activity.description }}</p>
                  <div v-if="activity.metadata" class="timeline-tags">
                    <span v-for="(value, key) in activity.metadata" :key="key" class="timeline-tag">
                      {{ key }}: {{ value }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div class="flex justify-center mt-6">
              <n-button quaternary :loading="loadingMore" @click="loadMoreActivities">
                <template #icon><RefreshCwIcon class="w-4 h-4" /></template>
                Daha Fazla Yükle
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
        Bu kodlari guvenli bir yerde saklayin.
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
    <n-modal v-model:show="showDeleteConfirm" preset="card" title="Hesabi Sil" class="modal-glass">
      <n-alert type="error" :bordered="false" class="mb-6">
        <template #icon><AlertTriangleIcon class="w-5 h-5" /></template>
        Bu işlem geri alinamaz! Tum verileriniz kalici olarak silinecektir.
      </n-alert>
      <p class="text-gray-400 mb-4">
        Hesabınızi silmek istediginizi onaylamak için asagiya
        <strong style="color: var(--text-primary)">"HESABIMI SIL"</strong> yazin.
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
            Hesabi Kalici Olarak Sil
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- Avatar Upload Modal -->
    <n-modal v-model:show="showAvatarUpload" preset="card" title="Profil Fotografi" class="modal-glass">
      <div class="upload-zone">
        <n-upload
          accept="image/*"
          :max="1"
          :show-file-list="false"
          @change="handleAvatarUpload"
        >
          <div class="upload-content">
            <UploadCloudIcon class="w-12 h-12 text-orange-500 mb-4" />
            <p class="text-gray-300">Fotografinizi surukleyin veya tiklayin</p>
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
            <p class="text-gray-300">Kapak fotografinizi surukleyin veya tiklayin</p>
            <p class="text-sm text-gray-500 mt-2">PNG, JPG (min. 1920x400, max. 10MB)</p>
          </div>
        </n-upload>
      </div>
    </n-modal>

    <!-- All Achievements Modal -->
    <n-modal v-model:show="showAllAchievements" preset="card" title="Tum Basarilar" class="modal-glass modal-lg">
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  UserIcon,
  ShieldCheckIcon,
  SettingsIcon,
  ActivityIcon,
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
  if (percent < 25) return 'Profilinizi tamamlayin!'
  if (percent < 50) return 'Iyi bir baslangic!'
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
  { name: 'security', label: 'Guvenlik', icon: ShieldCheckIcon },
  { name: 'settings', label: 'Ayarlar', icon: SettingsIcon },
  { name: 'activity', label: 'Aktivite', icon: ActivityIcon, count: activities.value.length }
])

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
const twoFASecret = ref('JBSWY3DPEHPK3PXP')
const twoFACode = ref('')

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
  if (passwordStrength.value <= 20) return 'Çok Zayif'
  if (passwordStrength.value <= 40) return 'Zayif'
  if (passwordStrength.value <= 60) return 'Orta'
  if (passwordStrength.value <= 80) return 'Guclu'
  return 'Çok Guclu'
})

// Sessions
const sessions = ref([
  {
    id: 1,
    device_name: 'Chrome on Windows',
    device_type: 'desktop',
    ip: '192.168.1.100',
    location: 'Istanbul, Turkiye',
    last_activity: new Date(),
    is_current: true
  },
  {
    id: 2,
    device_name: 'Safari on iPhone',
    device_type: 'mobile',
    ip: '192.168.1.101',
    location: 'Ankara, Turkiye',
    last_activity: new Date(Date.now() - 1000 * 60 * 60 * 3),
    is_current: false
  }
])

const getDeviceClass = (type) => `device-${type}`

// Activities
const activities = ref([
  {
    id: 1,
    type: 'success',
    title: 'Şifre degistirildi',
    description: 'Hesap şifreniz basariyla güncellendi',
    created_at: new Date(Date.now() - 1000 * 60 * 30),
    metadata: { IP: '192.168.1.100' }
  },
  {
    id: 2,
    type: 'info',
    title: 'Yeni oturum acildi',
    description: 'Chrome on Windows - Istanbul, Turkiye',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2)
  },
  {
    id: 3,
    type: 'warning',
    title: 'Başarısız giriş denemesi',
    description: 'Yanlış şifre girildi',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 5),
    metadata: { IP: '192.168.1.105', Konum: 'Bilinmiyor' }
  },
  {
    id: 4,
    type: 'success',
    title: 'Sunucu oluşturuldu',
    description: 'Yeni CS2 sunucusu basariyla kuruldu',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24)
  }
])

const getActivityIcon = (type) => {
  const icons = { info: InfoIcon, success: CheckCircleIcon, warning: AlertCircleIcon, error: XCircleIcon }
  return icons[type] || InfoIcon
}

// Backup codes
const backupCodes = ref([
  'XXXX-XXXX-XXXX', 'YYYY-YYYY-YYYY', 'ZZZZ-ZZZZ-ZZZZ',
  'AAAA-AAAA-AAAA', 'BBBB-BBBB-BBBB', 'CCCC-CCCC-CCCC'
])

// Achievements
const achievements = ref([
  { id: 1, name: 'Ilk Adim', icon: RocketIcon, unlocked: true },
  { id: 2, name: 'Sunucu Ustaşı', icon: ServerIcon, unlocked: true },
  { id: 3, name: 'Topluluk Yildizi', icon: StarIcon, unlocked: true },
  { id: 4, name: 'Guvenlik Uzman', icon: ShieldIcon, unlocked: false },
  { id: 5, name: 'Sadik Üye', icon: HeartIcon, unlocked: true },
  { id: 6, name: 'Hiz Seytani', icon: ZapIcon, unlocked: false },
  { id: 7, name: 'Hedef Avcisi', icon: TargetIcon, unlocked: false },
  { id: 8, name: 'Alev Savasci', icon: FlameIcon, unlocked: true }
])

const allAchievements = ref([
  { id: 1, name: 'Ilk Adim', description: 'Hesabınızi oluştürün', icon: RocketIcon, unlocked: true, unlocked_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30) },
  { id: 2, name: 'Sunucu Ustaşı', description: '5 sunucu oluştürün', icon: ServerIcon, unlocked: true, unlocked_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 15) },
  { id: 3, name: 'Topluluk Yildizi', description: 'Forumda 50 gönderi paylasim', icon: StarIcon, unlocked: true, unlocked_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7) },
  { id: 4, name: 'Guvenlik Uzmani', description: '2FA\'yi etkinlestirin', icon: ShieldIcon, unlocked: false, progress: 0 },
  { id: 5, name: 'Sadik Üye', description: '1 yillik üyelik', icon: HeartIcon, unlocked: true, unlocked_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5) },
  { id: 6, name: 'Hiz Seytani', description: '10 hizli işlem tamamlayin', icon: ZapIcon, unlocked: false, progress: 40 },
  { id: 7, name: 'Hedef Avcisi', description: 'Tum gorevleri tamamlayin', icon: TargetIcon, unlocked: false, progress: 75 },
  { id: 8, name: 'Alev Savasci', description: '100 oyun saati', icon: FlameIcon, unlocked: true, unlocked_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3) },
  { id: 9, name: 'Bilge', description: 'Tum kilavuzlari okuyun', icon: BookIcon, unlocked: false, progress: 20 }
])

// Connected accounts
const connectedAccounts = reactive({
  steam: { connected: true, username: 'gamer123' },
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

// Profile methods
const updateProfile = async () => {
  saving.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    authStore.updateUser(profileForm)
    window.$message?.success('Profil basariyla güncellendi')
  } catch (error) {
    window.$message?.error('Profil güncellenemedi')
  } finally {
    saving.value = false
  }
}

// Password methods
const changePassword = async () => {
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    window.$message?.error('Şifreler eşleşmiyor!')
    return
  }
  if (passwordStrength.value < 60) {
    window.$message?.warning('Lütfen daha guclu bir şifre secin')
    return
  }
  savingPassword.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    window.$message?.success('Şifre basariyla güncellendi')
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    passwordStrength.value = 0
  } catch (error) {
    window.$message?.error('Şifre güncellenemedi')
  } finally {
    savingPassword.value = false
  }
}

// 2FA methods
const start2FASetup = () => {
  show2FASetup.value = true
  twoFAStep.value = 1
}

const cancel2FASetup = () => {
  show2FASetup.value = false
  twoFAStep.value = 1
  twoFACode.value = ''
}

const verify2FACode = async () => {
  if (twoFACode.value.length !== 6) {
    window.$message?.error('Lütfen 6 haneli kodu girin')
    return
  }
  verifying2FA.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    twoFAStep.value = 3
  } catch (error) {
    window.$message?.error('Doğrulama başarısız')
  } finally {
    verifying2FA.value = false
  }
}

const finish2FASetup = () => {
  show2FASetup.value = false
  twoFAStep.value = 1
  twoFACode.value = ''
  window.$message?.success('2FA basariyla etkinlestirildi!')
}

const disable2FA = () => {
  window.$dialog?.warning({
    title: 'Uyari',
    content: '2FA\'yi devre disi birakmak istediginizden emin misiniz?',
    positiveText: 'Evet, Devre Disi Birak',
    negativeText: 'İptal',
    onPositiveClick: () => {
      window.$message?.success('2FA devre disi birakildi')
    }
  })
}

const downloadBackupCodes = () => {
  const content = backupCodes.value.join('\n')
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '2fa-yedek-kodlar.txt'
  a.click()
  URL.revokeObjectURL(url)
  window.$message?.success('Yedek kodlar indirildi')
}

// Session methods
const revokeSession = (sessionId) => {
  window.$dialog?.warning({
    title: 'Oturumu Sonlandir',
    content: 'Bu oturumu sonlandirmak istediginizden emin misiniz?',
    positiveText: 'Evet',
    negativeText: 'İptal',
    onPositiveClick: () => {
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      window.$message?.success('Oturum sonlandirildi')
    }
  })
}

const revokeAllSessions = () => {
  window.$dialog?.warning({
    title: 'Tum Oturumlari Sonlandir',
    content: 'Mevcut oturum haric tum oturumlari sonlandirmak istediginizden emin misiniz?',
    positiveText: 'Evet',
    negativeText: 'İptal',
    onPositiveClick: () => {
      sessions.value = sessions.value.filter(s => s.is_current)
      window.$message?.success('Tum oturumlar sonlandirildi')
    }
  })
}

// Settings methods
const saveSettings = async () => {
  savingSettings.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    window.$message?.success('Ayarlar kaydedildi')
  } catch (error) {
    window.$message?.error('Ayarlar kaydedilemedi')
  } finally {
    savingSettings.value = false
  }
}

// Account methods
const freezeAccount = () => {
  window.$dialog?.warning({
    title: 'Hesabi Dondur',
    content: 'Hesabınızi dondurmak istediginizden emin misiniz?',
    positiveText: 'Evet, Dondur',
    negativeText: 'İptal',
    onPositiveClick: () => {
      window.$message?.info('Hesabınız donduruldu')
    }
  })
}

const deleteAccount = async () => {
  deletingAccount.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    window.$message?.success('Hesabınız silindi')
    showDeleteConfirm.value = false
  } catch (error) {
    window.$message?.error('Hesap silinemedi')
  } finally {
    deletingAccount.value = false
  }
}

// Connected accounts methods
const connectAccount = (provider) => {
  window.$message?.info(`${provider} hesabi bağlaniyor...`)
}

const disconnectAccount = (provider) => {
  window.$dialog?.warning({
    title: 'Hesap Bağlantısini Kes',
    content: 'Bu hesabin bağlantısini kesmek istediginizden emin misiniz?',
    positiveText: 'Evet',
    negativeText: 'İptal',
    onPositiveClick: () => {
      connectedAccounts[provider].connected = false
      connectedAccounts[provider].username = null
      window.$message?.success('Hesap bağlantısi kesildi')
    }
  })
}

// Upload handlers
const handleAvatarUpload = ({ file }) => {
  window.$message?.success('Profil fotografi yüklendi')
  showAvatarUpload.value = false
}

const handleCoverUpload = ({ file }) => {
  window.$message?.success('Kapak fotografi yüklendi')
  showCoverUpload.value = false
}

// Load more activities
const loadMoreActivities = async () => {
  loadingMore.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    activities.value.push({
      id: activities.value.length + 1,
      type: 'info',
      title: 'Eski aktivite',
      description: 'Ornek aktivite açıklamasi',
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7)
    })
  } finally {
    loadingMore.value = false
  }
}

// Initialize form data
onMounted(() => {
  if (user.value) {
    profileForm.username = user.value.username || ''
    profileForm.email = user.value.email || ''
    profileForm.first_name = user.value.first_name || ''
    profileForm.last_name = user.value.last_name || ''
    profileForm.phone = user.value.phone || ''
    profileForm.country = user.value.country || ''
    profileForm.bio = user.value.bio || ''
  }
})

watch(user, (newUser) => {
  if (newUser) {
    profileForm.username = newUser.username || ''
    profileForm.email = newUser.email || ''
    profileForm.first_name = newUser.first_name || ''
    profileForm.last_name = newUser.last_name || ''
    profileForm.phone = newUser.phone || ''
    profileForm.country = newUser.country || ''
    profileForm.bio = newUser.bio || ''
  }
}, { deep: true })
</script>

<style scoped>
/* Base Styles */
.profile-page {
  background: #0a0a0a;
  min-height: 100vh;
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
</style>
