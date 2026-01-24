import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/Home.vue'),
    meta: { title: 'Ana Sayfa' }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: 'Dashboard', requiresAuth: true }
  },
  {
    path: '/my-servers',
    name: 'my-servers',
    component: () => import('@/views/MyServers.vue'),
    meta: { title: 'Sunucularim', requiresAuth: true }
  },
  {
    path: '/servers',
    name: 'servers',
    component: () => import('@/views/Servers.vue'),
    meta: { title: 'Sunucular' }
  },
  {
    path: '/servers/:id',
    name: 'server-detail',
    component: () => import('@/views/ServerDetail.vue'),
    meta: { title: 'Sunucu Detayı' }
  },
  {
    path: '/community-servers',
    name: 'community-servers',
    component: () => import('@/views/CommunityServers.vue'),
    meta: { title: 'Topluluk Sunucuları' }
  },
  {
    path: '/forum',
    name: 'forum',
    component: () => import('@/views/Forum.vue'),
    meta: { title: 'Forum' }
  },
  {
    path: '/forum/category/:id',
    name: 'forum-category',
    component: () => import('@/views/ForumCategory.vue'),
    meta: { title: 'Forum Kategorisi' }
  },
  {
    path: '/test/game-assets',
    name: 'game-assets-test',
    component: () => import('@/views/GameAssetsTest.vue'),
    meta: { title: 'Game Assets Test' }
  },
  {
    path: '/forum/topic/:id',
    name: 'forum-topic',
    component: () => import('@/views/ForumTopic.vue'),
    meta: { title: 'Forum Konusu' }
  },
  {
    path: '/shop',
    name: 'shop',
    component: () => import('@/views/Shop.vue'),
    meta: { title: 'Mağaza' }
  },
  {
    path: '/leaderboard',
    name: 'leaderboard',
    component: () => import('@/views/Leaderboard.vue'),
    meta: { title: 'Sıralama' }
  },
  {
    path: '/tournaments',
    name: 'tournaments',
    component: () => import('@/views/Tournaments.vue'),
    meta: { title: 'Turnuvalar' }
  },
  {
    path: '/tournaments/:id',
    name: 'tournament-detail',
    component: () => import('@/views/TournamentDetail.vue'),
    meta: { title: 'Turnuva Detayı' }
  },
  {
    path: '/clans',
    name: 'clans',
    component: () => import('@/views/Clans.vue'),
    meta: { title: 'Klanlar' }
  },
  {
    path: '/clans/:id',
    name: 'clan-detail',
    component: () => import('@/views/ClanDetail.vue'),
    meta: { title: 'Klan Detayı' }
  },
  {
    path: '/jackpot',
    name: 'jackpot',
    component: () => import('@/views/Jackpot.vue'),
    meta: { title: 'Jackpot', requiresAuth: true }
  },
  {
    path: '/verify',
    name: 'verify',
    component: () => import('@/views/Verify.vue'),
    meta: { title: 'Provably Fair' }
  },
  {
    path: '/gizlilik-politikasi',
    name: 'privacy-policy',
    component: () => import('@/views/PrivacyPolicy.vue'),
    meta: { title: 'Gizlilik Politikasi' }
  },
  {
    path: '/wallet',
    name: 'wallet',
    component: () => import('@/views/Wallet.vue'),
    meta: { title: 'Cüzdan', requiresAuth: true }
  },
  {
    path: '/profile/:id?',
    name: 'profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: 'Profil', requiresAuth: true }
  },
  {
    path: '/user/:username',
    name: 'user-profile',
    component: () => import('@/views/UserProfile.vue'),
    meta: { title: 'Kullanıcı Profili' }
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/admin/Dashboard.vue'),
    meta: { title: 'Admin Panel', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'admin-users',
    component: () => import('@/views/admin/Users.vue'),
    meta: { title: 'Kullanıcı Yönetimi', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/servers',
    name: 'admin-servers',
    component: () => import('@/views/admin/Servers.vue'),
    meta: { title: 'Sunucu Yönetimi', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/payments',
    name: 'admin-payments',
    component: () => import('@/views/admin/Payments.vue'),
    meta: { title: 'Ödeme Yönetimi', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/packages',
    name: 'admin-packages',
    component: () => import('@/views/admin/Packages.vue'),
    meta: { title: 'Paket Yönetimi', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/settings',
    name: 'admin-settings',
    component: () => import('@/views/admin/Settings.vue'),
    meta: { title: 'Sistem Ayarları', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/media',
    name: 'admin-media',
    component: () => import('@/views/admin/Media.vue'),
    meta: { title: 'Görsel Yönetimi', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/pages',
    name: 'admin-pages',
    component: () => import('@/views/admin/Pages.vue'),
    meta: { title: 'Sayfa İçerikleri', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/banners',
    name: 'admin-banners',
    component: () => import('@/views/admin/Banners.vue'),
    meta: { title: 'Banner Yönetimi', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/theme',
    name: 'admin-theme',
    component: () => import('@/views/admin/Theme.vue'),
    meta: { title: 'Tema Ayarları', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/forum',
    name: 'admin-forum',
    component: () => import('@/views/admin/Forum.vue'),
    meta: { title: 'Forum Yönetimi', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/maintenance',
    name: 'admin-maintenance',
    component: () => import('@/views/admin/Maintenance.vue'),
    meta: { title: 'Bakım Modu', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/stats',
    name: 'admin-stats',
    component: () => import('@/views/admin/Stats.vue'),
    meta: { title: 'Istatistikler', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/game-assets',
    name: 'admin-game-assets',
    component: () => import('@/views/admin/GameAssets.vue'),
    meta: { title: 'Oyun Gorselleri', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/health',
    name: 'admin-health',
    component: () => import('@/views/admin/SystemHealth.vue'),
    meta: { title: 'Sistem Saglik Monitoru', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { title: 'Giriş Yap', guestOnly: true }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/Register.vue'),
    meta: { title: 'Kayıt Ol', guestOnly: true }
  },
  {
    path: '/oauth-callback',
    name: 'oauth-callback',
    component: () => import('@/views/OAuthCallback.vue'),
    meta: { title: 'Giriş Yapılıyor...' }
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('@/views/ForgotPassword.vue'),
    meta: { title: 'Şifremi Unuttum', guestOnly: true }
  },
  {
    path: '/verify-email',
    name: 'verify-email',
    component: () => import('@/views/VerifyEmail.vue'),
    meta: { title: 'E-posta Doğrulama' }
  },
  {
    path: '/terms',
    name: 'terms',
    component: () => import('@/views/Terms.vue'),
    meta: { title: 'Kullanım Koşulları' }
  },
  {
    path: '/privacy',
    name: 'privacy',
    component: () => import('@/views/Privacy.vue'),
    meta: { title: 'Gizlilik Politikası' }
  },
  {
    path: '/contact',
    name: 'contact',
    component: () => import('@/views/Contact.vue'),
    meta: { title: 'İletişim' }
  },
  {
    path: '/support',
    name: 'support',
    component: () => import('@/views/Support.vue'),
    meta: { title: 'Destek' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '404 - Sayfa Bulunamadı' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    } else {
      return { top: 0, behavior: 'smooth' }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const uiStore = useUIStore()

  // Set page title
  if (to.meta.title) {
    uiStore.setPageTitle(to.meta.title)
  }

  // Close mobile menu on navigation
  uiStore.mobileMenuOpen = false

  // Check authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Try to fetch user if token exists
    if (authStore.token) {
      const success = await authStore.fetchUser()
      if (!success) {
        return next({ name: 'login', query: { redirect: to.fullPath } })
      }
    } else {
      return next({ name: 'login', query: { redirect: to.fullPath } })
    }
  }

  // Check admin panel access (sadece superadmin)
  if (to.meta.requiresAdmin && !authStore.canAccessAdminPanel) {
    uiStore.addNotification({
      type: 'error',
      message: 'Admin paneline sadece Super Admin erişebilir!'
    })
    return next({ name: 'home' })
  }

  // Redirect authenticated users from guest pages
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return next({ name: 'home' })
  }

  next()
})

// After each navigation
router.afterEach((to, from) => {
  // Track page view (analytics placeholder)
  if (typeof gtag !== 'undefined') {
    gtag('config', 'GA_MEASUREMENT_ID', {
      page_path: to.path
    })
  }
})

export default router
