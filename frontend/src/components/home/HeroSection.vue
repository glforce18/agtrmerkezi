<template>
  <section class="hero-section" ref="heroRef">
    <!-- Video/Animated Background -->
    <div class="hero-background">
      <div class="hero-video-overlay"></div>
      <video
        v-if="videoUrl"
        ref="videoRef"
        class="hero-video"
        autoplay
        muted
        loop
        playsinline
      >
        <source :src="videoUrl" type="video/mp4" />
      </video>
      <div v-else class="hero-animated-bg">
        <div class="hero-grid"></div>
        <div class="hero-particles">
          <div
            v-for="n in 20"
            :key="n"
            class="hero-particle"
            :style="getParticleStyle(n)"
          ></div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="hero-content" :style="parallaxStyle">
      <!-- Badge -->
      <div class="hero-badge animate-slide-up">
        <span class="hero-badge-dot"></span>
        <span>{{ badge }}</span>
      </div>

      <!-- Title -->
      <h1 class="hero-title animate-slide-up" style="animation-delay: 0.1s">
        <span class="hero-title-main">{{ title }}</span>
        <span class="hero-title-gradient">{{ titleGradient }}</span>
      </h1>

      <!-- Subtitle -->
      <p class="hero-subtitle animate-slide-up" style="animation-delay: 0.2s">
        {{ subtitle }}
      </p>

      <!-- Live Stats -->
      <div class="hero-live-stats animate-slide-up" style="animation-delay: 0.3s">
        <div class="hero-stat">
          <span class="hero-stat-value">
            <AnimatedCounter :value="stats.onlinePlayers" />
          </span>
          <span class="hero-stat-label">Aktif Oyuncu</span>
        </div>
        <div class="hero-stat-divider"></div>
        <div class="hero-stat">
          <span class="hero-stat-value">
            <AnimatedCounter :value="stats.activeServers" />
          </span>
          <span class="hero-stat-label">Canli Sunucu</span>
        </div>
        <div class="hero-stat-divider"></div>
        <div class="hero-stat">
          <span class="hero-stat-value">
            <AnimatedCounter :value="stats.totalMembers" />+
          </span>
          <span class="hero-stat-label">Topluluk Uyesi</span>
        </div>
      </div>

      <!-- CTAs -->
      <div class="hero-actions animate-slide-up" style="animation-delay: 0.4s">
        <router-link to="/register" class="hero-btn primary">
          <RocketIcon class="w-5 h-5" />
          <span>Hemen Basla</span>
          <div class="hero-btn-particles">
            <span v-for="n in 6" :key="n"></span>
          </div>
        </router-link>
        <router-link to="/servers" class="hero-btn secondary">
          <ServerIcon class="w-5 h-5" />
          <span>Sunuculari Gor</span>
        </router-link>
      </div>

      <!-- Scroll Indicator -->
      <div class="hero-scroll-indicator animate-fade-in" style="animation-delay: 1s">
        <div class="hero-scroll-mouse">
          <div class="hero-scroll-wheel"></div>
        </div>
        <span>Kesfetmek icin asagi kaydir</span>
      </div>
    </div>

    <!-- Floating Elements -->
    <div class="hero-floats">
      <div class="hero-float hero-float-1">
        <TrophyIcon class="w-6 h-6" />
      </div>
      <div class="hero-float hero-float-2">
        <CrosshairIcon class="w-6 h-6" />
      </div>
      <div class="hero-float hero-float-3">
        <ShieldIcon class="w-6 h-6" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { RocketIcon, ServerIcon, TrophyIcon, CrosshairIcon, ShieldIcon } from 'lucide-vue-next'

const props = defineProps({
  title: { type: String, default: 'AGTR' },
  titleGradient: { type: String, default: 'MERKEZİ' },
  subtitle: { type: String, default: 'Turkiye\'nin en buyuk Half-Life ve Counter-Strike 1.6 oyun toplulugu' },
  badge: { type: String, default: 'Turkiye\'nin #1 Oyun Toplulugu' },
  videoUrl: { type: String, default: '' }
})

const heroRef = ref(null)
const videoRef = ref(null)
const scrollY = ref(0)

const stats = reactive({
  onlinePlayers: 0,
  activeServers: 0,
  totalMembers: 0
})

// Parallax effect
const parallaxStyle = computed(() => ({
  transform: `translateY(${scrollY.value * 0.3}px)`,
  opacity: 1 - scrollY.value / 600
}))

// Particle styles
const getParticleStyle = (n) => {
  const colors = ['#f97316', '#8b5cf6', '#06b6d4', '#22c55e']
  return {
    '--delay': `${Math.random() * 5}s`,
    '--duration': `${10 + Math.random() * 20}s`,
    '--x': `${Math.random() * 100}%`,
    '--y': `${Math.random() * 100}%`,
    '--size': `${2 + Math.random() * 4}px`,
    backgroundColor: colors[n % colors.length]
  }
}

// Animated Counter Component
const AnimatedCounter = {
  props: { value: { type: Number, default: 0 } },
  setup(props) {
    const displayValue = ref(0)

    const animate = (target) => {
      const duration = 2000
      const start = displayValue.value
      const startTime = performance.now()

      const step = (currentTime) => {
        const elapsed = currentTime - startTime
        const progress = Math.min(elapsed / duration, 1)
        const easeOut = 1 - Math.pow(1 - progress, 3)
        displayValue.value = Math.floor(start + (target - start) * easeOut)

        if (progress < 1) {
          requestAnimationFrame(step)
        }
      }

      requestAnimationFrame(step)
    }

    onMounted(() => {
      setTimeout(() => animate(props.value), 500)
    })

    return () => displayValue.value.toLocaleString('tr-TR')
  }
}

// Fetch live stats
const fetchStats = async () => {
  try {
    const response = await fetch('/api/stats/live')
    if (response.ok) {
      const data = await response.json()
      stats.onlinePlayers = data.online_players || 247
      stats.activeServers = data.active_servers || 42
      stats.totalMembers = data.total_members || 15000
    }
  } catch {
    // Default values
    stats.onlinePlayers = 247
    stats.activeServers = 42
    stats.totalMembers = 15000
  }
}

// Scroll handler
const handleScroll = () => {
  scrollY.value = window.scrollY
}

onMounted(() => {
  fetchStats()
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 120px 24px 60px;
}

/* Background */
.hero-background {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.hero-video-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    rgba(9, 9, 11, 0.9) 0%,
    rgba(9, 9, 11, 0.7) 50%,
    rgba(9, 9, 11, 0.95) 100%
  );
  z-index: 1;
}

.hero-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-animated-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #09090b 0%, #18181b 50%, #09090b 100%);
}

.hero-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(249, 115, 22, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(249, 115, 22, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
}

.hero-particles {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.hero-particle {
  position: absolute;
  width: var(--size);
  height: var(--size);
  left: var(--x);
  top: var(--y);
  border-radius: 50%;
  opacity: 0.5;
  animation: particle-drift var(--duration) ease-in-out infinite;
  animation-delay: var(--delay);
}

@keyframes particle-drift {
  0%, 100% {
    transform: translate(0, 0) scale(1);
    opacity: 0.3;
  }
  50% {
    transform: translate(30px, -50px) scale(1.5);
    opacity: 0.7;
  }
}

/* Content */
.hero-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 900px;
}

/* Badge */
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  background: rgba(249, 115, 22, 0.1);
  border: 1px solid rgba(249, 115, 22, 0.3);
  border-radius: 100px;
  font-size: 13px;
  font-weight: 600;
  color: #f97316;
  margin-bottom: 24px;
}

.hero-badge-dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  animation: badge-pulse 2s ease-in-out infinite;
}

@keyframes badge-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

/* Title */
.hero-title {
  font-family: 'Rajdhani', sans-serif;
  font-size: clamp(48px, 10vw, 80px);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 20px;
}

.hero-title-main {
  display: block;
  color: #fafafa;
}

.hero-title-gradient {
  display: block;
  background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #f97316 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradient-shift 3s ease-in-out infinite;
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% center; }
  50% { background-position: 100% center; }
}

/* Subtitle */
.hero-subtitle {
  font-size: clamp(16px, 3vw, 20px);
  color: #a1a1aa;
  max-width: 600px;
  line-height: 1.6;
  margin-bottom: 32px;
}

/* Live Stats */
.hero-live-stats {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 20px 32px;
  background: rgba(24, 24, 27, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  margin-bottom: 40px;
}

.hero-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.hero-stat-value {
  font-family: 'Rajdhani', sans-serif;
  font-size: 32px;
  font-weight: 700;
  color: #fafafa;
}

.hero-stat-label {
  font-size: 12px;
  color: #71717a;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.hero-stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
}

/* Actions */
.hero-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: center;
  margin-bottom: 60px;
}

.hero-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 14px;
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.hero-btn.primary {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: white;
  box-shadow: 0 8px 32px rgba(249, 115, 22, 0.4);
}

.hero-btn.primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(249, 115, 22, 0.5);
}

.hero-btn.secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fafafa;
}

.hero-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

/* Button Particles */
.hero-btn-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.hero-btn-particles span {
  position: absolute;
  width: 4px;
  height: 4px;
  background: white;
  border-radius: 50%;
  opacity: 0;
}

.hero-btn.primary:hover .hero-btn-particles span {
  animation: particle-burst 0.6s ease-out forwards;
}

.hero-btn-particles span:nth-child(1) { left: 20%; top: 50%; animation-delay: 0s; }
.hero-btn-particles span:nth-child(2) { left: 40%; top: 30%; animation-delay: 0.05s; }
.hero-btn-particles span:nth-child(3) { left: 60%; top: 70%; animation-delay: 0.1s; }
.hero-btn-particles span:nth-child(4) { left: 80%; top: 40%; animation-delay: 0.15s; }
.hero-btn-particles span:nth-child(5) { left: 30%; top: 60%; animation-delay: 0.2s; }
.hero-btn-particles span:nth-child(6) { left: 70%; top: 50%; animation-delay: 0.25s; }

@keyframes particle-burst {
  0% {
    transform: scale(0) translate(0, 0);
    opacity: 1;
  }
  100% {
    transform: scale(1) translate(var(--x, 20px), var(--y, -30px));
    opacity: 0;
  }
}

/* Scroll Indicator */
.hero-scroll-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #52525b;
  font-size: 12px;
}

.hero-scroll-mouse {
  width: 24px;
  height: 36px;
  border: 2px solid #52525b;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  padding-top: 8px;
}

.hero-scroll-wheel {
  width: 4px;
  height: 8px;
  background: #f97316;
  border-radius: 2px;
  animation: scroll-wheel 1.5s ease-in-out infinite;
}

@keyframes scroll-wheel {
  0%, 100% { transform: translateY(0); opacity: 1; }
  50% { transform: translateY(6px); opacity: 0.3; }
}

/* Floating Elements */
.hero-floats {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
}

.hero-float {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: rgba(24, 24, 27, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  color: #f97316;
  animation: float 6s ease-in-out infinite;
}

.hero-float-1 {
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.hero-float-2 {
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.hero-float-3 {
  bottom: 25%;
  left: 15%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(5deg); }
}

/* Animations */
.animate-slide-up {
  animation: slide-up 0.6s ease-out forwards;
  opacity: 0;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out forwards;
  opacity: 0;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Responsive */
@media (max-width: 768px) {
  .hero-section {
    padding: 100px 16px 40px;
  }

  .hero-live-stats {
    flex-direction: column;
    gap: 16px;
    padding: 20px;
  }

  .hero-stat-divider {
    width: 60px;
    height: 1px;
  }

  .hero-actions {
    flex-direction: column;
    width: 100%;
  }

  .hero-btn {
    width: 100%;
    justify-content: center;
  }

  .hero-floats {
    display: none;
  }
}
</style>
