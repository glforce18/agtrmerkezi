<template>
  <Transition name="slide-up">
    <nav v-if="isMobile && !isHidden" class="mobile-bottom-nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="mobile-nav-item"
        :class="{ active: isActive(item.path) }"
      >
        <div class="mobile-nav-icon-wrapper">
          <component :is="item.icon" class="mobile-nav-icon" />
          <span v-if="item.badge && item.badge > 0" class="mobile-nav-badge">
            {{ item.badge > 99 ? '99+' : item.badge }}
          </span>
          <span v-if="item.live" class="mobile-nav-live-dot"></span>
        </div>
        <span class="mobile-nav-label">{{ item.label }}</span>
        <div v-if="isActive(item.path)" class="mobile-nav-indicator"></div>
      </router-link>

      <!-- Center Action Button -->
      <button class="mobile-nav-center-btn" @click="openAction">
        <div class="mobile-nav-center-icon">
          <PlusIcon class="w-6 h-6" />
        </div>
      </button>
    </nav>
  </Transition>

  <!-- Quick Action Modal -->
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="showActionModal" class="action-modal-overlay" @click.self="showActionModal = false">
        <Transition name="slide-up">
          <div v-if="showActionModal" class="action-modal">
            <div class="action-modal-header">
              <span class="action-modal-title">Hizli Islem</span>
              <button class="action-modal-close" @click="showActionModal = false">
                <XIcon class="w-5 h-5" />
              </button>
            </div>
            <div class="action-modal-grid">
              <button
                v-for="action in quickActions"
                :key="action.id"
                class="action-modal-item"
                @click="handleAction(action)"
              >
                <div class="action-modal-icon" :class="action.color">
                  <component :is="action.icon" class="w-6 h-6" />
                </div>
                <span class="action-modal-label">{{ action.label }}</span>
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  HomeIcon,
  MessageSquareIcon,
  TrophyIcon,
  ShoppingBagIcon,
  UserIcon,
  PlusIcon,
  XIcon,
  PlusCircleIcon,
  ServerIcon,
  WalletIcon,
  SettingsIcon,
  SearchIcon,
  BellIcon
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// State
const isMobile = ref(false)
const isHidden = ref(false)
const showActionModal = ref(false)
const lastScrollY = ref(0)
const unreadNotifications = ref(0)

// Computed
const user = computed(() => authStore.user)

const navItems = computed(() => [
  {
    path: '/',
    label: 'Ana Sayfa',
    icon: HomeIcon
  },
  {
    path: '/forum',
    label: 'Forum',
    icon: MessageSquareIcon,
    badge: 0 // New topics count
  },
  // Center space for action button
  {
    path: '/tournaments',
    label: 'Turnuva',
    icon: TrophyIcon,
    live: true // Show live indicator
  },
  {
    path: user.value ? '/profile' : '/login',
    label: user.value ? 'Profil' : 'Giris',
    icon: user.value ? UserIcon : UserIcon,
    badge: unreadNotifications.value
  }
])

const quickActions = [
  { id: 'new-topic', label: 'Yeni Konu', icon: PlusCircleIcon, color: 'primary', action: () => router.push('/forum/new') },
  { id: 'servers', label: 'Sunucularim', icon: ServerIcon, color: 'success', action: () => router.push('/servers') },
  { id: 'wallet', label: 'Cuzdan', icon: WalletIcon, color: 'warning', action: () => router.push('/wallet') },
  { id: 'shop', label: 'Magaza', icon: ShoppingBagIcon, color: 'secondary', action: () => router.push('/shop') },
  { id: 'search', label: 'Ara', icon: SearchIcon, color: 'accent', action: () => emit('open-search') },
  { id: 'notifications', label: 'Bildirimler', icon: BellIcon, color: 'error', action: () => router.push('/notifications') }
]

const emit = defineEmits(['open-search'])

// Methods
const isActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const openAction = () => {
  showActionModal.value = true
}

const handleAction = (action) => {
  showActionModal.value = false
  if (action.action) {
    action.action()
  }
}

// Scroll handling - hide on scroll down, show on scroll up
const handleScroll = () => {
  const currentScrollY = window.scrollY
  const scrollDiff = currentScrollY - lastScrollY.value

  if (scrollDiff > 10 && currentScrollY > 100) {
    isHidden.value = true
  } else if (scrollDiff < -10) {
    isHidden.value = false
  }

  lastScrollY.value = currentScrollY
}

// Check viewport
const checkViewport = () => {
  isMobile.value = window.innerWidth < 768
}

// Lifecycle
onMounted(() => {
  checkViewport()
  window.addEventListener('resize', checkViewport)
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('resize', checkViewport)
  window.removeEventListener('scroll', handleScroll)
})

// Hide action modal on route change
watch(() => route.path, () => {
  showActionModal.value = false
})
</script>

<style scoped>
.mobile-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(24, 24, 27, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 0 8px;
  padding-bottom: env(safe-area-inset-bottom, 0);
  z-index: 1000;
  transition: transform 0.3s ease;
}

.mobile-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  color: #71717a;
  text-decoration: none;
  position: relative;
  transition: color 0.2s;
}

.mobile-nav-item.active {
  color: #f97316;
}

.mobile-nav-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mobile-nav-icon {
  width: 24px;
  height: 24px;
  transition: transform 0.2s;
}

.mobile-nav-item.active .mobile-nav-icon {
  transform: scale(1.1);
}

.mobile-nav-badge {
  position: absolute;
  top: -4px;
  right: -8px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  border-radius: 8px;
  font-size: 10px;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: badge-pop 0.3s ease;
}

@keyframes badge-pop {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.mobile-nav-live-dot {
  position: absolute;
  top: -2px;
  right: -4px;
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  animation: live-pulse 2s ease-in-out infinite;
}

@keyframes live-pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.5); }
  50% { opacity: 0.8; box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); }
}

.mobile-nav-label {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.02em;
}

.mobile-nav-indicator {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  background: #f97316;
  border-radius: 50%;
  animation: indicator-appear 0.3s ease;
}

@keyframes indicator-appear {
  from { transform: translateX(-50%) scale(0); }
  to { transform: translateX(-50%) scale(1); }
}

/* Center Action Button */
.mobile-nav-center-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  margin-top: -28px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(249, 115, 22, 0.4);
  transition: all 0.3s ease;
}

.mobile-nav-center-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 28px rgba(249, 115, 22, 0.5);
}

.mobile-nav-center-btn:active {
  transform: scale(0.95);
}

.mobile-nav-center-icon {
  color: white;
  transition: transform 0.3s ease;
}

.mobile-nav-center-btn:hover .mobile-nav-center-icon {
  transform: rotate(90deg);
}

/* Action Modal */
.action-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.action-modal {
  width: 100%;
  max-width: 480px;
  background: #18181b;
  border-radius: 24px 24px 0 0;
  padding: 20px;
  padding-bottom: calc(20px + env(safe-area-inset-bottom, 0));
}

.action-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.action-modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #fafafa;
}

.action-modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: #27272a;
  border: none;
  border-radius: 50%;
  color: #a1a1aa;
  cursor: pointer;
  transition: all 0.2s;
}

.action-modal-close:hover {
  background: #3f3f46;
  color: #fafafa;
}

.action-modal-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.action-modal-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  background: #27272a;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-modal-item:hover {
  background: #3f3f46;
  transform: translateY(-2px);
}

.action-modal-item:active {
  transform: scale(0.95);
}

.action-modal-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  color: white;
}

.action-modal-icon.primary { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); }
.action-modal-icon.secondary { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); }
.action-modal-icon.success { background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); }
.action-modal-icon.warning { background: linear-gradient(135deg, #eab308 0%, #ca8a04 100%); }
.action-modal-icon.accent { background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); }
.action-modal-icon.error { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }

.action-modal-label {
  font-size: 12px;
  font-weight: 500;
  color: #a1a1aa;
}

/* Transitions */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Desktop - hide */
@media (min-width: 768px) {
  .mobile-bottom-nav {
    display: none;
  }
}

/* Safe area padding for phones with notch */
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .mobile-bottom-nav {
    height: calc(64px + env(safe-area-inset-bottom));
  }
}
</style>
