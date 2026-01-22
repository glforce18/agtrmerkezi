<template>
  <div
    class="achievement-card"
    :class="{
      unlocked: isUnlocked,
      [rarity.toLowerCase()]: true
    }"
  >
    <!-- Rarity Glow -->
    <div class="rarity-glow" :style="{ background: rarityColor }"></div>

    <!-- Icon -->
    <div class="achievement-icon" :class="{ locked: !isUnlocked }">
      <span class="icon-emoji">{{ achievement.icon }}</span>
      <div v-if="!isUnlocked" class="lock-overlay">
        <Lock class="w-5 h-5" />
      </div>
    </div>

    <!-- Info -->
    <div class="achievement-info">
      <h4 class="achievement-name">{{ achievement.name }}</h4>
      <p class="achievement-description">{{ achievement.description }}</p>

      <!-- Progress Bar -->
      <div v-if="!isUnlocked && achievement.maxProgress > 1" class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
        </div>
        <span class="progress-text">{{ currentProgress }} / {{ achievement.maxProgress }}</span>
      </div>

      <!-- Unlocked Date -->
      <div v-if="isUnlocked && unlockedAt" class="unlocked-date">
        <Check class="w-3 h-3" />
        {{ formatDate(unlockedAt) }}
      </div>
    </div>

    <!-- Rarity Badge -->
    <div class="rarity-badge" :style="{ background: rarityColor }">
      {{ rarityName }}
      <span class="rarity-points">+{{ rarityPoints }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Lock, Check } from 'lucide-vue-next'
import { AchievementRarity } from '@/stores/achievements'

const props = defineProps({
  achievement: {
    type: Object,
    required: true
  },
  isUnlocked: {
    type: Boolean,
    default: false
  },
  currentProgress: {
    type: Number,
    default: 0
  },
  unlockedAt: {
    type: String,
    default: null
  }
})

const rarity = computed(() => props.achievement.rarity || 'COMMON')
const rarityInfo = computed(() => AchievementRarity[rarity.value] || AchievementRarity.COMMON)
const rarityColor = computed(() => rarityInfo.value.color)
const rarityName = computed(() => rarityInfo.value.name)
const rarityPoints = computed(() => rarityInfo.value.points)

const progressPercent = computed(() => {
  if (!props.achievement.maxProgress) return 0
  return Math.min(100, Math.round((props.currentProgress / props.achievement.maxProgress) * 100))
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}
</script>

<style scoped>
.achievement-card {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.achievement-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.achievement-card.unlocked {
  background: linear-gradient(135deg, var(--bg-secondary) 0%, rgba(34, 197, 94, 0.05) 100%);
  border-color: rgba(34, 197, 94, 0.3);
}

/* Rarity-specific styles */
.achievement-card.common { border-left: 3px solid #9ca3af; }
.achievement-card.uncommon { border-left: 3px solid #22c55e; }
.achievement-card.rare { border-left: 3px solid #3b82f6; }
.achievement-card.epic { border-left: 3px solid #8b5cf6; }
.achievement-card.legendary {
  border-left: 3px solid #f97316;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, rgba(249, 115, 22, 0.05) 100%);
}

.rarity-glow {
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.1;
}

.achievement-card.unlocked .rarity-glow {
  opacity: 0.2;
}

.achievement-icon {
  position: relative;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 12px;
  flex-shrink: 0;
}

.achievement-icon.locked {
  filter: grayscale(1);
  opacity: 0.5;
}

.icon-emoji {
  font-size: 28px;
}

.lock-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 12px;
  color: white;
}

.achievement-info {
  flex: 1;
  min-width: 0;
}

.achievement-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.achievement-description {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #f97316, #fb923c);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-tertiary);
  white-space: nowrap;
}

.unlocked-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #22c55e;
}

.rarity-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: white;
  text-transform: uppercase;
}

.rarity-points {
  opacity: 0.8;
  font-weight: 500;
}
</style>
