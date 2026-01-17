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
    path: '/jackpot',
    name: 'jackpot',
    component: () => import('@/views/Jackpot.vue'),
    meta: { title: 'Jackpot', requiresAuth: true }
  },
  {
    path: '/profile/:id?',
    name: 'profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: 'Profil', requiresAuth: true }
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
    meta: { title: 'Sistem Ayarlari', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/media',
    name: 'admin-media',
    component: () => import('@/views/admin/Media.vue'),
    meta: { title: 'Gorsel Yonetimi', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/pages',
    name: 'admin-pages',
    component: () => import('@/views/admin/Pages.vue'),
    meta: { title: 'Sayfa Icerikleri', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/banners',
    name: 'admin-banners',
    component: () => import('@/views/admin/Banners.vue'),
    meta: { title: 'Banner Yonetimi', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/theme',
    name: 'admin-theme',
    component: () => import('@/views/admin/Theme.vue'),
    meta: { title: 'Tema Ayarlari', requiresAuth: true, requiresAdmin: true }
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

  // Check admin access
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    uiStore.addNotification({
      type: 'error',
      message: 'Bu sayfaya erişim yetkiniz yok!'
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
