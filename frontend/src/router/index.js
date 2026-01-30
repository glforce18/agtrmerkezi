import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue'),
      beforeEnter: (to, from, next) => {
        // If on panel subdomain, redirect to panel login
        if (window.location.hostname === 'panel.agtrmerkezi.com') {
          next('/panel')
        } else {
          next()
        }
      }
    },
    {
      path: '/panel',
      name: 'panel-login',
      component: () => import('@/views/panel/PanelLogin.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/Login.vue'),
      meta: { guest: true }
    },
    {
      path: '/auth/login',
      redirect: '/login'
    },
    {
      path: '/register',
      redirect: '/login'
    },
    {
      path: '/auth/register',
      redirect: '/login'
    },
    {
      path: '/oauth-callback',
      name: 'oauth-callback',
      component: () => import('@/views/auth/OAuthCallback.vue')
    },
    {
      path: '/auth/callback',
      name: 'steam-callback',
      component: () => import('@/views/auth/SteamCallback.vue')
    },
    {
      path: '/servers',
      name: 'servers',
      component: () => import('@/views/server/ServerList.vue')
    },
    {
      path: '/servers/my',
      name: 'my-servers',
      component: () => import('@/views/server/MyServers.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/servers/:id',
      redirect: to => ({ name: 'server-webpanel-dashboard', params: { id: to.params.id } })
    },
    {
      path: '/servers/:id/panel',
      component: () => import('@/views/server/ServerWebPanel.vue'),
      // NO AUTH REQUIRED - Panel mode uses panel_token instead
      children: [
        {
          path: '',
          name: 'server-webpanel-dashboard',
          component: () => import('@/views/server/webpanel/Dashboard.vue')
        },
        {
          path: 'settings',
          name: 'server-webpanel-settings',
          component: () => import('@/views/server/webpanel/Settings.vue')
        },
        {
          path: 'files',
          name: 'server-webpanel-files',
          component: () => import('@/views/server/webpanel/FileEditor.vue')
        }
      ]
    },
    {
      path: '/servers/rent',
      name: 'server-rent',
      component: () => import('@/views/server/ServerRent.vue')
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/user/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/wallet',
      name: 'wallet',
      component: () => import('@/views/user/Wallet.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/shop',
      name: 'shop',
      component: () => import('@/views/shop/Shop.vue')
    },
    {
      path: '/forum',
      name: 'forum',
      component: () => import('@/views/forum/ForumHome.vue')
    },
    {
      path: '/forum/category/:id',
      name: 'forum-category',
      component: () => import('@/views/forum/ForumCategory.vue')
    },
    {
      path: '/forum/topic/new',
      name: 'forum-topic-new',
      component: () => import('@/views/forum/ForumTopicNew.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/forum/topic/:id',
      name: 'forum-topic',
      component: () => import('@/views/forum/ForumTopic.vue')
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/user/Profile.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/admin/AdminDashboard.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: () => import('@/views/admin/AdminUsers.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/servers',
      name: 'admin-servers',
      component: () => import('@/views/admin/AdminServers.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/payments',
      name: 'admin-payments',
      component: () => import('@/views/admin/AdminPayments.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/packages',
      name: 'admin-packages',
      component: () => import('@/views/admin/AdminPackages.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/server-approval',
      name: 'admin-server-approval',
      component: () => import('@/views/admin/ServerApproval.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/settings',
      name: 'admin-settings',
      component: () => import('@/views/admin/AdminSettings.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Check if user is in panel mode (logged in with panel password)
  const isPanelMode = localStorage.getItem('panel_mode') === 'true'
  const panelToken = localStorage.getItem('panel_token')
  const panelServerId = localStorage.getItem('panel_server_id')

  console.log('[ROUTER] Navigation to:', to.path)
  console.log('[ROUTER] Panel mode:', isPanelMode, 'Token:', panelToken ? 'exists' : 'none', 'Server ID:', panelServerId)

  // If accessing panel routes with panel token, allow access without Steam auth
  if (to.path.includes('/servers/') && to.path.includes('/panel') && isPanelMode && panelToken) {
    console.log('[ROUTER] Panel route detected, checking server ID...')

    // Verify the server ID matches if in panel mode
    const requestedServerId = to.params.id ? String(to.params.id) : null
    const storedServerId = panelServerId ? String(panelServerId) : null

    console.log('[ROUTER] Requested:', requestedServerId, 'Stored:', storedServerId)

    if (requestedServerId && storedServerId && requestedServerId !== storedServerId) {
      console.log('[ROUTER] Server ID mismatch, redirecting...')
      // Redirect to correct server panel
      next({ name: 'server-webpanel-dashboard', params: { id: storedServerId } })
      return
    }
    console.log('[ROUTER] Panel access granted!')
    next()
    return
  }

  // Initialize auth if not done
  if (!authStore.user && authStore.token) {
    authStore.init()

    // If still no user after init, fetch from API
    if (!authStore.user) {
      try {
        await authStore.fetchUser()
      } catch (error) {
        console.error('Failed to fetch user in router guard:', error)
      }
    }
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Don't redirect if user is in panel mode - panel routes don't need Steam auth
    const isPanelModeForAuth = localStorage.getItem('panel_mode') === 'true'
    const hasPanelToken = localStorage.getItem('panel_token')

    if (isPanelModeForAuth && hasPanelToken && to.path.includes('/panel')) {
      console.log('[ROUTER] Skipping auth check - panel mode active')
      next()
      return
    }

    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // Check if route requires admin
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'home' })
    return
  }

  // Redirect authenticated users away from guest pages
  if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'home' })
    return
  }

  next()
})

export default router
