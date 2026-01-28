import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/Login.vue'),
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/Register.vue'),
      meta: { guest: true }
    },
    {
      path: '/oauth-callback',
      name: 'oauth-callback',
      component: () => import('@/views/auth/OAuthCallback.vue')
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
      name: 'server-panel',
      component: () => import('@/views/server/ServerPanel.vue'),
      meta: { requiresAuth: true }
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

  // Initialize auth if not done
  if (!authStore.user && authStore.token) {
    authStore.init()
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
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
