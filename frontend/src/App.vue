<template>
  <n-config-provider :theme="themeStore.naiveTheme" :theme-overrides="themeStore.themeOverrides">
    <n-notification-provider>
      <n-message-provider>
        <n-dialog-provider>
          <n-loading-bar-provider>
            <div id="app" class="min-h-screen">
              <!-- Subtle Ambient Particles -->
              <div class="ambient-particles">
                <div v-for="i in 8" :key="i" class="particle" :style="getParticleStyle(i)"></div>
              </div>

              <!-- Navbar -->
              <Navbar />

              <!-- Main Content -->
              <main class="page-wrapper">
                <router-view v-slot="{ Component }">
                  <transition name="page-slide" mode="out-in">
                    <component :is="Component" />
                  </transition>
                </router-view>
              </main>

              <!-- Footer -->
              <Footer />

              <!-- Global Command Palette (Ctrl+K) -->
              <CommandPalette />

              <!-- Chat Manager (Messaging System) -->
              <ChatManager ref="chatManager" />
            </div>
          </n-loading-bar-provider>
        </n-dialog-provider>
      </n-message-provider>
    </n-notification-provider>
  </n-config-provider>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import CommandPalette from '@/components/ui/CommandPalette.vue'
import ChatManager from '@/components/social/ChatManager.vue'

const authStore = useAuthStore()
const themeStore = useThemeStore()

// Generate random particle styles
const getParticleStyle = (index) => {
  const colors = ['#f97316', '#8b5cf6', '#06b6d4', '#22c55e', '#ef4444']
  return {
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    width: `${Math.random() * 4 + 2}px`,
    height: `${Math.random() * 4 + 2}px`,
    backgroundColor: colors[index % colors.length],
    animationDelay: `${Math.random() * 10}s`,
    animationDuration: `${Math.random() * 20 + 15}s`
  }
}

onMounted(async () => {
  // Try to restore auth session
  if (authStore.token) {
    await authStore.fetchUser()
  }

  // Mark app as loaded
  document.documentElement.classList.add('loaded')
})
</script>

<style>
/* ========================================
   OYUN TEMALI SAYFA GEÇİŞLERİ
   ======================================== */

/* Page Slide Transition - Game Style */
.page-slide-enter-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.page-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.7, 0, 0.84, 0);
}

.page-slide-enter-from {
  opacity: 0;
  transform: translateX(30px) scale(0.98);
  filter: blur(4px);
}

.page-slide-leave-to {
  opacity: 0;
  transform: translateX(-30px) scale(0.98);
  filter: blur(4px);
}

/* Global enhancements */
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.page-wrapper {
  flex: 1;
  animation: pageLoad 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  z-index: 1;
}

@keyframes pageLoad {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.99);
    filter: blur(2px);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0);
  }
}

/* Loading state */
html:not(.loaded) #app {
  opacity: 0;
}

html.loaded #app {
  opacity: 1;
  transition: opacity 0.4s ease;
}

/* ========================================
   AMBIENT PARTICLES - Floating Game Dust
   ======================================== */

.ambient-particles {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.particle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.3;
  animation: particleFloat linear infinite;
  filter: blur(1px);
}

@keyframes particleFloat {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.3;
  }
  90% {
    opacity: 0.3;
  }
  100% {
    transform: translateY(-100px) rotate(720deg);
    opacity: 0;
  }
}

/* ========================================
   GLOBAL GAME EFFECTS
   ======================================== */

/* Glow text effect */
.glow-text {
  text-shadow:
    0 0 10px currentColor,
    0 0 20px currentColor,
    0 0 40px currentColor;
}

/* Neon border effect */
.neon-border {
  box-shadow:
    0 0 5px currentColor,
    0 0 10px currentColor,
    inset 0 0 5px currentColor;
}

/* Pulse animation for live elements */
.pulse-live {
  animation: pulseLive 2s ease-in-out infinite;
}

@keyframes pulseLive {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(34, 197, 94, 0);
  }
}

/* Shake animation for damage effect */
.shake-damage {
  animation: shakeDamage 0.5s ease-in-out;
}

@keyframes shakeDamage {
  0%, 100% { transform: translateX(0); }
  10% { transform: translateX(-10px); }
  20% { transform: translateX(10px); }
  30% { transform: translateX(-8px); }
  40% { transform: translateX(8px); }
  50% { transform: translateX(-5px); }
  60% { transform: translateX(5px); }
  70% { transform: translateX(-3px); }
  80% { transform: translateX(3px); }
  90% { transform: translateX(-1px); }
}

/* Typewriter effect */
.typewriter {
  overflow: hidden;
  white-space: nowrap;
  animation: typewriter 3s steps(40) 1s forwards;
}

@keyframes typewriter {
  from { width: 0; }
  to { width: 100%; }
}

/* Glitch effect */
.glitch-text {
  position: relative;
}

.glitch-text::before,
.glitch-text::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.glitch-text::before {
  animation: glitchTop 1s linear infinite;
  clip-path: polygon(0 0, 100% 0, 100% 33%, 0 33%);
  -webkit-clip-path: polygon(0 0, 100% 0, 100% 33%, 0 33%);
}

.glitch-text::after {
  animation: glitchBottom 1.5s linear infinite;
  clip-path: polygon(0 67%, 100% 67%, 100% 100%, 0 100%);
  -webkit-clip-path: polygon(0 67%, 100% 67%, 100% 100%, 0 100%);
}

@keyframes glitchTop {
  0% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
  100% { transform: translate(0); }
}

@keyframes glitchBottom {
  0% { transform: translate(0); }
  20% { transform: translate(2px, -2px); }
  40% { transform: translate(2px, 2px); }
  60% { transform: translate(-2px, -2px); }
  80% { transform: translate(-2px, 2px); }
  100% { transform: translate(0); }
}

/* Rainbow glow for special items */
.rainbow-glow {
  animation: rainbowGlow 3s linear infinite;
}

@keyframes rainbowGlow {
  0% { box-shadow: 0 0 20px #f97316; }
  25% { box-shadow: 0 0 20px #8b5cf6; }
  50% { box-shadow: 0 0 20px #06b6d4; }
  75% { box-shadow: 0 0 20px #22c55e; }
  100% { box-shadow: 0 0 20px #f97316; }
}

/* ========================================
   REDUCED MOTION SUPPORT
   ======================================== */

@media (prefers-reduced-motion: reduce) {
  .ambient-particles {
    display: none;
  }

  .particle,
  .pulse-live,
  .shake-damage,
  .glitch-text::before,
  .glitch-text::after,
  .rainbow-glow {
    animation: none;
  }

  .page-slide-enter-active,
  .page-slide-leave-active {
    transition: opacity 0.2s ease;
  }

  .page-slide-enter-from,
  .page-slide-leave-to {
    transform: none;
    filter: none;
  }
}
</style>
