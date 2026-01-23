<template>
  <div class="map-gallery" v-if="maps.length > 0">
    <div class="map-gallery__header">
      <h3 class="map-gallery__title">
        <MapIcon class="w-5 h-5" />
        {{ title || 'Populer Haritalar' }}
      </h3>
      <div class="map-gallery__controls">
        <button
          class="map-gallery__nav"
          :disabled="currentIndex === 0"
          @click="prev"
          aria-label="Onceki harita"
        >
          <ChevronLeftIcon class="w-5 h-5" />
        </button>
        <span class="map-gallery__counter">
          {{ currentIndex + 1 }} / {{ maps.length }}
        </span>
        <button
          class="map-gallery__nav"
          :disabled="currentIndex === maps.length - 1"
          @click="next"
          aria-label="Sonraki harita"
        >
          <ChevronRightIcon class="w-5 h-5" />
        </button>
      </div>
    </div>

    <div class="map-gallery__viewport" ref="viewport">
      <TransitionGroup name="map-slide" tag="div" class="map-gallery__track">
        <div
          v-for="(map, index) in visibleMaps"
          :key="map.id || index"
          class="map-gallery__item"
          :class="{ 'map-gallery__item--active': index === 1 }"
          @click="selectMap(map)"
        >
          <div class="map-card">
            <div class="map-card__image">
              <img
                :src="map.thumbnail || getDefaultMapImage(map.game)"
                :alt="map.name"
                loading="lazy"
                @error="handleImageError"
              />
              <div class="map-card__overlay">
                <div class="map-card__game-badge" :class="`map-card__game-badge--${map.game}`">
                  {{ getGameLabel(map.game) }}
                </div>
              </div>
              <div class="map-card__glow" />
            </div>
            <div class="map-card__info">
              <h4 class="map-card__name">{{ map.name }}</h4>
              <div class="map-card__meta">
                <span v-if="map.players" class="map-card__players">
                  <UsersIcon class="w-3.5 h-3.5" />
                  {{ map.players }}
                </span>
                <span v-if="map.mode" class="map-card__mode">
                  <TargetIcon class="w-3.5 h-3.5" />
                  {{ map.mode }}
                </span>
              </div>
              <div v-if="map.description" class="map-card__description">
                {{ map.description }}
              </div>
            </div>
            <div class="map-card__hover-effect" />
          </div>
        </div>
      </TransitionGroup>
    </div>

    <!-- Thumbnail strip -->
    <div class="map-gallery__thumbnails">
      <button
        v-for="(map, index) in maps"
        :key="`thumb-${index}`"
        class="map-gallery__thumb"
        :class="{ 'map-gallery__thumb--active': index === currentIndex }"
        @click="goTo(index)"
        :aria-label="`${map.name} haritasina git`"
      >
        <img
          :src="map.thumbnail || getDefaultMapImage(map.game)"
          :alt="map.name"
          loading="lazy"
        />
        <div class="map-gallery__thumb-overlay" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  MapIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  UsersIcon,
  TargetIcon
} from 'lucide-vue-next'

const props = defineProps({
  maps: {
    type: Array,
    default: () => [
      { id: 1, name: 'de_dust2', game: 'cs16', mode: 'Defuse', players: '10-20', description: 'Klasik ciftci haritasi' },
      { id: 2, name: 'de_inferno', game: 'cs16', mode: 'Defuse', players: '10-20', description: 'Italyan kasabasi' },
      { id: 3, name: 'cs_assault', game: 'cs16', mode: 'Hostage', players: '10-20', description: 'Depo operasyonu' },
      { id: 4, name: 'crossfire', game: 'halflife', mode: 'AG', players: '2-8', description: 'Adrenaline Gamer klasigi' },
      { id: 5, name: 'stalkyard', game: 'halflife', mode: 'AG', players: '2-8', description: 'Hizli AG aksiyonu' },
      { id: 6, name: 'boot_camp', game: 'halflife', mode: 'AG', players: '2-8', description: 'Egitim sahasi' }
    ]
  },
  title: {
    type: String,
    default: 'Populer Haritalar'
  },
  autoPlay: {
    type: Boolean,
    default: true
  },
  interval: {
    type: Number,
    default: 5000
  }
})

const emit = defineEmits(['select'])

const viewport = ref(null)
const currentIndex = ref(0)
let autoPlayTimer = null

const visibleMaps = computed(() => {
  const maps = props.maps
  if (maps.length <= 1) return maps

  const prev = currentIndex.value === 0 ? maps.length - 1 : currentIndex.value - 1
  const next = currentIndex.value === maps.length - 1 ? 0 : currentIndex.value + 1

  return [
    maps[prev],
    maps[currentIndex.value],
    maps[next]
  ]
})

const getGameLabel = (game) => {
  const labels = {
    cs16: 'CS 1.6',
    halflife: 'Half-Life',
    csgo: 'CS:GO',
    css: 'CS:S',
    tf2: 'TF2',
    sven: 'Sven Co-op'
  }
  return labels[game] || game
}

const getDefaultMapImage = (game) => {
  const images = {
    cs16: '/static/assets/games/cs16/heroes/cs16_hero.webp',
    halflife: '/static/assets/games/halflife/heroes/halflife_hero.webp'
  }
  return images[game] || '/images/default-map.jpg'
}

const handleImageError = (e) => {
  e.target.src = '/images/default-map.jpg'
}

const prev = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
    resetAutoPlay()
  }
}

const next = () => {
  if (currentIndex.value < props.maps.length - 1) {
    currentIndex.value++
    resetAutoPlay()
  }
}

const goTo = (index) => {
  currentIndex.value = index
  resetAutoPlay()
}

const selectMap = (map) => {
  emit('select', map)
}

const startAutoPlay = () => {
  if (!props.autoPlay || props.maps.length <= 1) return
  autoPlayTimer = setInterval(() => {
    currentIndex.value = (currentIndex.value + 1) % props.maps.length
  }, props.interval)
}

const resetAutoPlay = () => {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer)
    startAutoPlay()
  }
}

onMounted(() => {
  startAutoPlay()
})

onUnmounted(() => {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer)
  }
})
</script>

<style scoped>
.map-gallery {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(11, 15, 20, 0.98) 100%);
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 16px;
  padding: 20px;
  overflow: hidden;
  position: relative;
}

.map-gallery::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #f97316, #8b5cf6, #22d3ee);
}

.map-gallery__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.map-gallery__title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.map-gallery__controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.map-gallery__nav {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(249, 115, 22, 0.1);
  border: 1px solid rgba(249, 115, 22, 0.3);
  color: #f97316;
  transition: all 0.3s ease;
}

.map-gallery__nav:hover:not(:disabled) {
  background: rgba(249, 115, 22, 0.2);
  border-color: rgba(249, 115, 22, 0.5);
  transform: scale(1.05);
}

.map-gallery__nav:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.map-gallery__counter {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  min-width: 50px;
  text-align: center;
}

.map-gallery__viewport {
  overflow: hidden;
  margin: 0 -10px;
}

.map-gallery__track {
  display: flex;
  gap: 16px;
  padding: 10px;
}

.map-gallery__item {
  flex: 0 0 calc(33.333% - 12px);
  min-width: 200px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: center;
}

.map-gallery__item--active {
  transform: scale(1.05);
  z-index: 2;
}

.map-card {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  transition: all 0.3s ease;
}

.map-card:hover {
  border-color: rgba(249, 115, 22, 0.5);
  box-shadow: 0 8px 32px rgba(249, 115, 22, 0.2);
}

.map-card__image {
  position: relative;
  aspect-ratio: 16/9;
  overflow: hidden;
}

.map-card__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.map-card:hover .map-card__image img {
  transform: scale(1.1);
}

.map-card__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 40%, rgba(0, 0, 0, 0.8) 100%);
  pointer-events: none;
}

.map-card__glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(249, 115, 22, 0.3) 0%, transparent 70%);
  transform: translate(-50%, -50%) scale(0);
  transition: transform 0.3s ease;
  pointer-events: none;
}

.map-card:hover .map-card__glow {
  transform: translate(-50%, -50%) scale(2);
}

.map-card__game-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.map-card__game-badge--cs16 {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: #fff;
}

.map-card__game-badge--halflife {
  background: linear-gradient(135deg, #f97316, #dc2626);
  color: #fff;
}

.map-card__game-badge--csgo {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #fff;
}

.map-card__info {
  padding: 12px;
}

.map-card__name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 6px;
}

.map-card__meta {
  display: flex;
  gap: 12px;
  margin-bottom: 6px;
}

.map-card__players,
.map-card__mode {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.map-card__description {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.4;
}

.map-card__hover-effect {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, transparent 50%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.map-card:hover .map-card__hover-effect {
  opacity: 1;
}

/* Thumbnails */
.map-gallery__thumbnails {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  justify-content: center;
  overflow-x: auto;
  padding: 4px 0;
}

.map-gallery__thumb {
  position: relative;
  width: 48px;
  height: 36px;
  border-radius: 6px;
  overflow: hidden;
  border: 2px solid transparent;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.map-gallery__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.map-gallery__thumb-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  transition: opacity 0.3s ease;
}

.map-gallery__thumb:hover .map-gallery__thumb-overlay {
  opacity: 0.2;
}

.map-gallery__thumb--active {
  border-color: #f97316;
  box-shadow: 0 0 12px rgba(249, 115, 22, 0.5);
}

.map-gallery__thumb--active .map-gallery__thumb-overlay {
  opacity: 0;
}

/* Transitions */
.map-slide-enter-active,
.map-slide-leave-active {
  transition: all 0.4s ease;
}

.map-slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.map-slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* Responsive */
@media (max-width: 768px) {
  .map-gallery__item {
    flex: 0 0 100%;
  }

  .map-gallery__track {
    flex-wrap: nowrap;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
  }

  .map-gallery__item {
    scroll-snap-align: center;
  }
}
</style>
