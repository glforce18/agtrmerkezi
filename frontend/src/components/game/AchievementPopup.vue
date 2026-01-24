<template>
  <Teleport to="body">
    <TransitionGroup
      name="achievement"
      tag="div"
      class="achievement-container"
    >
      <div
        v-for="achievement in achievements"
        :key="achievement.id"
        class="achievement-popup"
        :class="[`achievement-${achievement.type || 'default'}`]"
      >
        <!-- Achievement Icon -->
        <div class="achievement-icon-wrapper">
          <div class="achievement-icon" :class="achievement.iconClass">
            <GameIcon
              v-if="achievement.gameIcon"
              :name="achievement.gameIcon"
              size="lg"
              :color="achievement.color || '#fbbf24'"
            />
            <component
              v-else-if="achievement.icon"
              :is="achievement.icon"
              class="w-8 h-8"
            />
            <Trophy v-else class="w-8 h-8" />
          </div>
          <div class="achievement-glow" :style="{ background: achievement.color || '#fbbf24' }"></div>
        </div>

        <!-- Achievement Content -->
        <div class="achievement-content">
          <div class="achievement-label">Başarım Acildi!</div>
          <div class="achievement-title">{{ achievement.title }}</div>
          <div v-if="achievement.description" class="achievement-description">
            {{ achievement.description }}
          </div>
          <div v-if="achievement.reward" class="achievement-reward">
            <span class="reward-label">Ödül:</span>
            <span class="reward-value">{{ achievement.reward }}</span>
          </div>
        </div>

        <!-- Close Button -->
        <button class="achievement-close" @click="removeAchievement(achievement.id)">
          <X class="w-4 h-4" />
        </button>

        <!-- Progress Bar -->
        <div class="achievement-progress">
          <div class="progress-fill"></div>
        </div>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { Trophy, X } from 'lucide-vue-next'
import GameIcon from './GameIcon.vue'

const achievements = ref([])
let achievementId = 0

const show = (data) => {
  const achievement = {
    id: ++achievementId,
    title: data.title || 'Başarım',
    description: data.description || '',
    icon: data.icon || null,
    gameIcon: data.gameIcon || null,
    iconClass: data.iconClass || '',
    color: data.color || '#fbbf24',
    type: data.type || 'default',
    reward: data.reward || null,
    duration: data.duration || 4000
  }

  achievements.value.push(achievement)

  // Auto remove after duration
  setTimeout(() => {
    removeAchievement(achievement.id)
  }, achievement.duration)
}

const removeAchievement = (id) => {
  const index = achievements.value.findIndex(a => a.id === id)
  if (index !== -1) {
    achievements.value.splice(index, 1)
  }
}

// Expose methods for parent component
defineExpose({ show })
</script>

<style scoped>
.achievement-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: none;
}

.achievement-popup {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(24, 24, 28, 0.98) 0%, rgba(15, 15, 18, 0.98) 100%);
  border: 1px solid rgba(251, 191, 36, 0.4);
  border-radius: 16px;
  box-shadow:
    0 0 30px rgba(251, 191, 36, 0.3),
    0 10px 40px rgba(0, 0, 0, 0.4);
  min-width: 320px;
  max-width: 400px;
  pointer-events: auto;
  overflow: hidden;
}

.achievement-default {
  border-color: rgba(251, 191, 36, 0.4);
}

.achievement-epic {
  border-color: rgba(139, 92, 246, 0.5);
  box-shadow:
    0 0 30px rgba(139, 92, 246, 0.4),
    0 10px 40px rgba(0, 0, 0, 0.4);
}

.achievement-legendary {
  border-color: rgba(249, 115, 22, 0.6);
  box-shadow:
    0 0 40px rgba(249, 115, 22, 0.5),
    0 10px 40px rgba(0, 0, 0, 0.4);
  background: linear-gradient(135deg, rgba(30, 20, 15, 0.98) 0%, rgba(20, 15, 10, 0.98) 100%);
}

/* Icon */
.achievement-icon-wrapper {
  position: relative;
  flex-shrink: 0;
}

.achievement-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(249, 115, 22, 0.2));
  border-radius: 14px;
  animation: achievementIconBounce 0.6s ease-in-out 0.3s;
}

.achievement-glow {
  position: absolute;
  inset: -10px;
  border-radius: 50%;
  filter: blur(20px);
  opacity: 0.4;
  animation: pulseGlow 2s ease-in-out infinite;
}

@keyframes achievementIconBounce {
  0%, 100% { transform: scale(1) rotate(0deg); }
  25% { transform: scale(1.2) rotate(-10deg); }
  50% { transform: scale(1.1) rotate(5deg); }
  75% { transform: scale(1.15) rotate(-3deg); }
}

@keyframes pulseGlow {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

/* Content */
.achievement-content {
  flex: 1;
  min-width: 0;
}

.achievement-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #fbbf24;
  margin-bottom: 4px;
}

.achievement-title {
  font-size: 16px;
  font-weight: 700;
  color: #f8fafc;
  margin-bottom: 2px;
}

.achievement-description {
  font-size: 13px;
  color: #94a3b8;
  line-height: 1.4;
}

.achievement-reward {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 13px;
}

.reward-label {
  color: #64748b;
}

.reward-value {
  color: #22c55e;
  font-weight: 700;
}

/* Close Button */
.achievement-close {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 6px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.achievement-close:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #f8fafc;
}

/* Progress Bar */
.achievement-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(255, 255, 255, 0.1);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #fbbf24, #f97316);
  animation: progressShrink 4s linear forwards;
}

@keyframes progressShrink {
  from { width: 100%; }
  to { width: 0%; }
}

/* Transitions */
.achievement-enter-active {
  animation: achievementSlideIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.achievement-leave-active {
  animation: achievementSlideOut 0.3s ease-in;
}

@keyframes achievementSlideIn {
  from {
    transform: translateX(120%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes achievementSlideOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(120%);
    opacity: 0;
  }
}

/* Responsive */
@media (max-width: 480px) {
  .achievement-container {
    right: 10px;
    left: 10px;
  }

  .achievement-popup {
    min-width: auto;
    max-width: none;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .achievement-icon,
  .achievement-glow,
  .progress-fill {
    animation: none;
  }
}
</style>
