<template>
  <nav class="sticky top-0 z-50 bg-cyber-black border-b border-cyber-border backdrop-blur-lg bg-opacity-95">
    <div class="max-w-7xl mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-3 group">
          <div class="text-4xl text-lambda-orange transition-all group-hover:scale-110">λ</div>
          <div class="flex flex-col">
            <span class="text-xl font-lambda font-bold text-lambda-orange">AGTR</span>
            <span class="text-xs font-hev text-text-secondary -mt-1">MERKEZI</span>
          </div>
        </router-link>

        <!-- Desktop Menu -->
        <div class="hidden md:flex items-center gap-1">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="px-4 py-2 font-lambda font-bold text-sm rounded transition-all"
            :class="isActive(item.path)
              ? 'bg-lambda-orange bg-opacity-20 text-lambda-orange border border-lambda-orange'
              : 'text-text-secondary hover:text-lambda-orange hover:bg-lambda-orange hover:bg-opacity-10'"
          >
            <component :is="item.icon" :size="16" class="inline mr-2" />
            {{ item.label }}
          </router-link>
        </div>

        <!-- Right Side -->
        <div class="flex items-center gap-3">
          <!-- Auth Buttons -->
          <template v-if="!isAuthenticated">
            <router-link
              to="/login"
              class="hidden md:block px-4 py-2 text-text-primary hover:text-lambda-orange font-lambda font-bold text-sm transition-all"
            >
              GİRİŞ YAP
            </router-link>
            <router-link
              to="/register"
              class="hidden md:block px-4 py-2 bg-lambda-gradient text-cyber-black font-lambda font-bold text-sm rounded hover:shadow-neon-orange transition-all"
            >
              KAYIT OL
            </router-link>
          </template>

          <!-- User Menu -->
          <div v-else class="relative">
            <button
              @click="showUserMenu = !showUserMenu"
              class="flex items-center gap-2 px-3 py-2 bg-cyber-panel border border-cyber-border rounded hover:border-lambda-orange transition-all"
            >
              <div class="w-8 h-8 rounded-full bg-lambda-orange bg-opacity-20 border border-lambda-orange flex items-center justify-center text-lambda-orange font-lambda font-bold text-sm">
                {{ user.username?.[0]?.toUpperCase() || 'U' }}
              </div>
              <span class="hidden md:block font-lambda text-text-primary text-sm">{{ user.username }}</span>
              <ChevronDown :size="16" class="text-text-secondary" />
            </button>

            <!-- Dropdown -->
            <div
              v-if="showUserMenu"
              v-click-outside="() => showUserMenu = false"
              class="absolute right-0 mt-2 w-48 bg-cyber-panel border border-cyber-border rounded-lg shadow-xl overflow-hidden"
            >
              <router-link
                to="/profile"
                @click="showUserMenu = false"
                class="flex items-center gap-2 px-4 py-3 text-text-primary hover:bg-lambda-orange hover:bg-opacity-10 hover:text-lambda-orange transition-all"
              >
                <User :size="16" />
                <span class="font-hev text-sm">Profilim</span>
              </router-link>
              <router-link
                to="/servers/my"
                @click="showUserMenu = false"
                class="flex items-center gap-2 px-4 py-3 text-text-primary hover:bg-lambda-orange hover:bg-opacity-10 hover:text-lambda-orange transition-all"
              >
                <Server :size="16" />
                <span class="font-hev text-sm">Sunucularım</span>
              </router-link>
              <router-link
                v-if="isAdmin"
                to="/admin"
                @click="showUserMenu = false"
                class="flex items-center gap-2 px-4 py-3 text-text-primary hover:bg-lambda-orange hover:bg-opacity-10 hover:text-lambda-orange transition-all border-t border-cyber-border"
              >
                <Shield :size="16" />
                <span class="font-hev text-sm">Admin Panel</span>
              </router-link>
              <button
                @click="handleLogout"
                class="w-full flex items-center gap-2 px-4 py-3 text-combine-red hover:bg-combine-red hover:bg-opacity-10 transition-all border-t border-cyber-border"
              >
                <LogOut :size="16" />
                <span class="font-hev text-sm">Çıkış Yap</span>
              </button>
            </div>
          </div>

          <!-- Mobile Menu Button -->
          <button
            @click="showMobileMenu = !showMobileMenu"
            class="md:hidden p-2 text-text-secondary hover:text-lambda-orange transition-all"
          >
            <Menu v-if="!showMobileMenu" :size="24" />
            <X v-else :size="24" />
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <div
        v-if="showMobileMenu"
        class="md:hidden border-t border-cyber-border py-4 space-y-2"
      >
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          @click="showMobileMenu = false"
          class="flex items-center gap-2 px-4 py-3 font-lambda font-bold rounded transition-all"
          :class="isActive(item.path)
            ? 'bg-lambda-orange bg-opacity-20 text-lambda-orange'
            : 'text-text-secondary hover:bg-lambda-orange hover:bg-opacity-10 hover:text-lambda-orange'"
        >
          <component :is="item.icon" :size="18" />
          {{ item.label }}
        </router-link>

        <!-- Mobile Auth Buttons -->
        <template v-if="!isAuthenticated">
          <router-link
            to="/login"
            @click="showMobileMenu = false"
            class="block px-4 py-3 text-center border border-lambda-orange text-lambda-orange font-lambda font-bold rounded hover:bg-lambda-orange hover:bg-opacity-10 transition-all"
          >
            GİRİŞ YAP
          </router-link>
          <router-link
            to="/register"
            @click="showMobileMenu = false"
            class="block px-4 py-3 text-center bg-lambda-gradient text-cyber-black font-lambda font-bold rounded hover:shadow-neon-orange transition-all"
          >
            KAYIT OL
          </router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Home,
  Server,
  MessageSquare,
  Settings,
  Menu,
  X,
  ChevronDown,
  User,
  Shield,
  LogOut
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const showMobileMenu = ref(false)
const showUserMenu = ref(false)

const navItems = [
  { path: '/', label: 'ANA SAYFA', icon: Home },
  { path: '/servers', label: 'SUNUCULAR', icon: Server },
  { path: '/forum', label: 'FORUM', icon: MessageSquare },
  { path: '/servers/rent', label: 'KİRALA', icon: Settings }
]

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isAdmin = computed(() => authStore.isAdmin)
const user = computed(() => authStore.user || {})

function isActive(path) {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

async function handleLogout() {
  showUserMenu.value = false
  await authStore.logout()
  router.push('/login')
}

// Click outside directive
const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value()
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}
</script>

<style scoped>
.bg-lambda-gradient {
  background: linear-gradient(135deg, #FF6B35 0%, #E85D2C 100%);
}

.shadow-neon-orange {
  box-shadow: 0 0 20px rgba(255, 107, 53, 0.6);
}
</style>
