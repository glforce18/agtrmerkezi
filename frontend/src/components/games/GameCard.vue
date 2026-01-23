<template>
  <div class="game-card" :class="{ featured: isFeatured }" @click="handleClick">
    <div class="card-image">
      <img
        v-if="imageUrl"
        :src="imageUrl"
        :alt="game.name"
        @error="onImageError"
      />
      <div v-else class="image-placeholder" :style="placeholderStyle">
        <span class="placeholder-icon">{{ game.icon || '🎮' }}</span>
      </div>

      <!-- Hover overlay -->
      <div class="card-hover-overlay">
        <span class="play-icon">▶</span>
      </div>
    </div>

    <div class="card-content">
      <h3 class="game-name">{{ game.name }}</h3>
      <div class="game-meta">
        <span class="steam-id">Steam ID: {{ game.steam_id }}</span>
        <span v-if="assetCount" class="asset-count">{{ assetCount }} gorsel</span>
      </div>
    </div>

    <!-- Featured badge -->
    <div v-if="isFeatured" class="featured-badge">
      <span>⭐</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  game: {
    type: Object,
    required: true
  },
  imageUrl: {
    type: String,
    default: null
  },
  assetCount: {
    type: Number,
    default: null
  },
  isFeatured: {
    type: Boolean,
    default: false
  },
  clickable: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click'])

const hasImageError = ref(false)

// Game color mapping
const gameColors = {
  cs16: '#ff6b00',
  halflife: '#ff8c00',
  css: '#2a9d8f',
  csgo: '#e63946',
  tf2: '#b5838d',
  sven: '#457b9d'
}

const placeholderStyle = computed(() => ({
  background: `linear-gradient(135deg, ${gameColors[props.game.slug] || '#f97316'} 0%, #1a1a2e 100%)`
}))

function onImageError() {
  hasImageError.value = true
}

function handleClick() {
  if (props.clickable) {
    emit('click', props.game)
  }
}
</script>

<style scoped>
.game-card {
  position: relative;
  background: var(--bg-card, #131a22);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.game-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
  border-color: var(--primary-color, #f97316);
}

.game-card.featured {
  border-color: gold;
}

.card-image {
  position: relative;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.game-card:hover .card-image img {
  transform: scale(1.05);
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-icon {
  font-size: 48px;
}

.card-hover-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.game-card:hover .card-hover-overlay {
  opacity: 1;
}

.play-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-color, #f97316);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  transform: scale(0.8);
  transition: transform 0.3s ease;
}

.game-card:hover .play-icon {
  transform: scale(1);
}

.card-content {
  padding: 16px;
}

.game-name {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin: 0 0 8px 0;
}

.game-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-muted, #94a3b8);
}

.featured-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  background: gold;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}
</style>
