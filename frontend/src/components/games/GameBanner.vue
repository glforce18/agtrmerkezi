<template>
  <div class="game-banner" :class="[size, { loading: isLoading }]">
    <div v-if="isLoading" class="banner-skeleton">
      <div class="skeleton-animation"></div>
    </div>
    <img
      v-else-if="bannerUrl"
      :src="bannerUrl"
      :alt="gameName"
      class="banner-image"
      @load="onImageLoad"
      @error="onImageError"
    />
    <div v-else class="banner-fallback" :style="fallbackStyle">
      <span class="game-icon">{{ gameIcon }}</span>
      <span class="game-name">{{ gameName }}</span>
    </div>

    <!-- Overlay content slot -->
    <div v-if="$slots.default" class="banner-overlay">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useGameAssets } from '@/composables/useGameAssets'

const props = defineProps({
  gameSlug: {
    type: String,
    required: true
  },
  size: {
    type: String,
    default: 'medium', // small, medium, large, hero
    validator: (v) => ['small', 'medium', 'large', 'hero'].includes(v)
  },
  fallbackColor: {
    type: String,
    default: '#1a1a2e'
  }
})

const emit = defineEmits(['load', 'error'])

const { getGameBanner, loading } = useGameAssets()

const bannerData = ref(null)
const isLoading = ref(true)
const hasError = ref(false)

// Game info mapping
const gameInfo = {
  cs16: { name: 'Counter-Strike 1.6', icon: '🔫', color: '#ff6b00' },
  halflife: { name: 'Half-Life', icon: '🎮', color: '#ff8c00' },
  css: { name: 'Counter-Strike: Source', icon: '🎯', color: '#2a9d8f' },
  csgo: { name: 'CS:GO', icon: '💣', color: '#e63946' },
  tf2: { name: 'Team Fortress 2', icon: '🏰', color: '#b5838d' },
  sven: { name: 'Sven Co-op', icon: '👥', color: '#457b9d' }
}

const gameName = computed(() => gameInfo[props.gameSlug]?.name || props.gameSlug)
const gameIcon = computed(() => gameInfo[props.gameSlug]?.icon || '🎮')
const gameColor = computed(() => gameInfo[props.gameSlug]?.color || '#f97316')

const bannerUrl = computed(() => {
  if (bannerData.value?.file_path) {
    // Ensure proper URL format
    const path = bannerData.value.file_path
    return path.startsWith('http') ? path : path
  }
  return null
})

const fallbackStyle = computed(() => ({
  background: `linear-gradient(135deg, ${gameColor.value} 0%, ${props.fallbackColor} 100%)`
}))

async function loadBanner() {
  isLoading.value = true
  hasError.value = false

  try {
    const data = await getGameBanner(props.gameSlug)
    bannerData.value = data
  } catch (e) {
    hasError.value = true
  } finally {
    isLoading.value = false
  }
}

function onImageLoad() {
  emit('load')
}

function onImageError() {
  hasError.value = true
  bannerData.value = null
  emit('error')
}

watch(() => props.gameSlug, loadBanner)

onMounted(loadBanner)
</script>

<style scoped>
.game-banner {
  position: relative;
  overflow: hidden;
  border-radius: 12px;
  background: var(--bg-secondary, #1a1a2e);
}

.game-banner.small {
  height: 120px;
}

.game-banner.medium {
  height: 200px;
}

.game-banner.large {
  height: 300px;
}

.game-banner.hero {
  height: 400px;
}

.banner-skeleton {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, #1a1a2e 0%, #2a2a4e 50%, #1a1a2e 100%);
  background-size: 200% 100%;
}

.skeleton-animation {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.1) 50%, transparent 100%);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.banner-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.game-banner:hover .banner-image {
  transform: scale(1.02);
}

.banner-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 8px;
}

.game-icon {
  font-size: 48px;
}

.game-name {
  font-size: 18px;
  font-weight: 600;
  color: white;
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}

.banner-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 100%);
}
</style>
