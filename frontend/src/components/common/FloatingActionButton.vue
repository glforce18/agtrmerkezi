<template>
  <div class="fixed bottom-8 right-8 z-[100]">
    <!-- Main FAB Button -->
    <Transition name="fab">
      <button
        v-if="showFab"
        @click="toggleMenu"
        class="fab-main w-16 h-16 rounded-full bg-gradient-to-br from-primary via-secondary to-accent shadow-2xl shadow-primary/50 flex items-center justify-center text-white hover:scale-110 transition-all duration-300 hover:shadow-primary/70"
        :class="{ 'rotate-45': isMenuOpen }"
      >
        <Plus class="w-8 h-8" />
      </button>
    </Transition>

    <!-- FAB Menu Items -->
    <Transition name="fab-menu">
      <div v-if="isMenuOpen" class="absolute bottom-20 right-0 flex flex-col gap-3">
        <div
          v-for="(item, index) in menuItems"
          :key="item.id"
          class="fab-item"
          :style="{ transitionDelay: `${index * 50}ms` }"
        >
          <div class="relative group">
            <!-- Label -->
            <div class="absolute right-20 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none">
              <div class="bg-base-300 text-white px-4 py-2 rounded-lg shadow-xl whitespace-nowrap border border-base-300 backdrop-blur-xl">
                <div class="font-medium text-sm">{{ item.label }}</div>
                <div class="text-xs opacity-60">{{ item.description }}</div>
              </div>
            </div>

            <!-- Button -->
            <button
              @click="executeAction(item)"
              class="w-14 h-14 rounded-full shadow-xl flex items-center justify-center text-white hover:scale-110 transition-all duration-300"
              :class="item.class"
              :style="{ background: item.gradient }"
            >
              <component :is="item.icon" class="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Plus,
  Server,
  MessageSquare,
  Headphones,
  Search,
  ArrowUp,
  Zap
} from 'lucide-vue-next'

const router = useRouter()
const isMenuOpen = ref(false)
const showFab = ref(true)
const lastScrollY = ref(0)

const menuItems = [
  {
    id: 'new-server',
    label: 'Yeni Sunucu',
    description: 'Hızlıca sunucu oluştur',
    icon: Server,
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    class: 'shadow-purple-500/50',
    action: () => router.push('/dashboard?action=new-server')
  },
  {
    id: 'support',
    label: 'Destek Al',
    description: 'Canlı destek',
    icon: Headphones,
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    class: 'shadow-pink-500/50',
    action: () => router.push('/support')
  },
  {
    id: 'forum',
    label: 'Forum',
    description: 'Topluluğa katıl',
    icon: MessageSquare,
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    class: 'shadow-cyan-500/50',
    action: () => router.push('/forum')
  },
  {
    id: 'search',
    label: 'Hızlı Arama',
    description: 'Cmd+K ile ara',
    icon: Search,
    gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    class: 'shadow-green-500/50',
    action: () => window.dispatchEvent(new CustomEvent('open-command-palette'))
  },
  {
    id: 'scroll-top',
    label: 'Yukarı Çık',
    description: 'Sayfanın başına dön',
    icon: ArrowUp,
    gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    class: 'shadow-orange-500/50',
    action: () => window.scrollTo({ top: 0, behavior: 'smooth' })
  }
]

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const executeAction = (item) => {
  item.action()
  isMenuOpen.value = false
}

const handleScroll = () => {
  const currentScrollY = window.scrollY

  if (currentScrollY > lastScrollY.value && currentScrollY > 100) {
    // Scrolling down
    showFab.value = false
    isMenuOpen.value = false
  } else {
    // Scrolling up
    showFab.value = true
  }

  lastScrollY.value = currentScrollY
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.fab-main {
  cursor: pointer;
  backdrop-filter: blur(10px);
}

.fab-main:active {
  transform: scale(0.95);
}

.fab-enter-active,
.fab-leave-active {
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.fab-enter-from,
.fab-leave-to {
  transform: scale(0) rotate(180deg);
  opacity: 0;
}

.fab-menu-enter-active .fab-item,
.fab-menu-leave-active .fab-item {
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.fab-menu-enter-from .fab-item,
.fab-menu-leave-to .fab-item {
  transform: scale(0) translateX(20px);
  opacity: 0;
}

.fab-item {
  animation: fadeInUp 0.3s ease-out forwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.8);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

button {
  position: relative;
  overflow: hidden;
}

button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

button:active::before {
  width: 300px;
  height: 300px;
}
</style>
