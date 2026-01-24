<template>
  <Teleport to="body">
    <Transition name="level-up">
      <div v-if="visible" class="level-up-overlay" @click="hide">
        <div class="level-up-container" @click.stop>
          <!-- Rings Effect -->
          <div class="rings">
            <div class="ring ring-1"></div>
            <div class="ring ring-2"></div>
            <div class="ring ring-3"></div>
          </div>

          <!-- Particles -->
          <div class="particles">
            <div
              v-for="i in 20"
              :key="i"
              class="particle"
              :style="getParticleStyle(i)"
            ></div>
          </div>

          <!-- Main Content -->
          <div class="level-up-content">
            <!-- Level Badge -->
            <div class="level-badge-wrapper">
              <div class="level-badge">
                <span class="level-number">{{ level }}</span>
              </div>
              <div class="level-glow"></div>
            </div>

            <!-- Text -->
            <div class="level-up-text">
              <div class="label">SEVIYE ATLADIN!</div>
              <div class="title">Level {{ level }}</div>
              <div v-if="title" class="rank-title">{{ title }}</div>
            </div>

            <!-- Rewards -->
            <div v-if="rewards.length" class="rewards">
              <div class="rewards-label">Ödüllerin:</div>
              <div class="rewards-list">
                <div
                  v-for="(reward, index) in rewards"
                  :key="index"
                  class="reward-item"
                  :style="{ animationDelay: `${0.5 + index * 0.1}s` }"
                >
                  <GameIcon
                    v-if="reward.icon"
                    :name="reward.icon"
                    size="sm"
                    :color="reward.color || '#fbbf24'"
                  />
                  <span class="reward-text">{{ reward.text }}</span>
                </div>
              </div>
            </div>

            <!-- Continue Button -->
            <button class="continue-btn muzzle-flash-hover" @click="hide">
              Devam Et
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import GameIcon from './GameIcon.vue'

const visible = ref(false)
const level = ref(1)
const title = ref('')
const rewards = ref([])

const show = (data) => {
  level.value = data.level || 1
  title.value = data.title || ''
  rewards.value = data.rewards || []
  visible.value = true

  // Auto hide after duration if specified
  if (data.duration) {
    setTimeout(() => {
      hide()
    }, data.duration)
  }
}

const hide = () => {
  visible.value = false
}

const getParticleStyle = (index) => {
  const angle = (index / 20) * 360
  const distance = 100 + Math.random() * 100
  const size = 4 + Math.random() * 8
  const duration = 1 + Math.random() * 0.5
  const delay = Math.random() * 0.3

  return {
    '--angle': `${angle}deg`,
    '--distance': `${distance}px`,
    '--size': `${size}px`,
    '--duration': `${duration}s`,
    '--delay': `${delay}s`,
    background: ['#fbbf24', '#f97316', '#8b5cf6', '#22c55e', '#ef4444'][index % 5]
  }
}

defineExpose({ show, hide })
</script>

<style scoped>
.level-up-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.level-up-container {
  position: relative;
  text-align: center;
}

/* Rings */
.rings {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border: 3px solid rgba(251, 191, 36, 0.5);
  border-radius: 50%;
  animation: ringExpand 1.5s ease-out forwards;
}

.ring-1 {
  width: 100px;
  height: 100px;
  animation-delay: 0s;
}

.ring-2 {
  width: 100px;
  height: 100px;
  animation-delay: 0.2s;
}

.ring-3 {
  width: 100px;
  height: 100px;
  animation-delay: 0.4s;
}

@keyframes ringExpand {
  0% {
    transform: translate(-50%, -50%) scale(0.5);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(3);
    opacity: 0;
  }
}

/* Particles */
.particles {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.particle {
  position: absolute;
  width: var(--size);
  height: var(--size);
  border-radius: 50%;
  animation: particleBurst var(--duration) ease-out var(--delay) forwards;
}

@keyframes particleBurst {
  0% {
    transform: translate(-50%, -50%) rotate(var(--angle)) translateY(0);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) rotate(var(--angle)) translateY(var(--distance));
    opacity: 0;
  }
}

/* Content */
.level-up-content {
  position: relative;
  z-index: 1;
  animation: levelUpBurst 0.8s ease-out;
}

@keyframes levelUpBurst {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Level Badge */
.level-badge-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 24px;
}

.level-badge {
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fbbf24 0%, #f97316 100%);
  border-radius: 50%;
  box-shadow:
    0 0 40px rgba(251, 191, 36, 0.6),
    0 0 80px rgba(249, 115, 22, 0.4),
    inset 0 0 30px rgba(255, 255, 255, 0.3);
  animation: badgePulse 2s ease-in-out infinite;
}

.level-number {
  font-family: 'Orbitron', 'Poppins', sans-serif;
  font-size: 48px;
  font-weight: 900;
  color: #fff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.level-glow {
  position: absolute;
  inset: -20px;
  background: radial-gradient(circle, rgba(251, 191, 36, 0.4) 0%, transparent 70%);
  border-radius: 50%;
  animation: glowPulse 2s ease-in-out infinite;
}

@keyframes badgePulse {
  0%, 100% {
    transform: scale(1);
    box-shadow:
      0 0 40px rgba(251, 191, 36, 0.6),
      0 0 80px rgba(249, 115, 22, 0.4);
  }
  50% {
    transform: scale(1.05);
    box-shadow:
      0 0 60px rgba(251, 191, 36, 0.8),
      0 0 120px rgba(249, 115, 22, 0.6);
  }
}

@keyframes glowPulse {
  0%, 100% {
    opacity: 0.5;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.1);
  }
}

/* Text */
.level-up-text {
  margin-bottom: 24px;
}

.label {
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 4px;
  color: #fbbf24;
  margin-bottom: 8px;
}

.title {
  font-family: 'Orbitron', 'Poppins', sans-serif;
  font-size: 36px;
  font-weight: 900;
  color: #f8fafc;
  text-shadow: 0 0 20px rgba(248, 250, 252, 0.5);
}

.rank-title {
  font-size: 18px;
  font-weight: 600;
  color: #8b5cf6;
  margin-top: 8px;
}

/* Rewards */
.rewards {
  margin-bottom: 32px;
}

.rewards-label {
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #64748b;
  margin-bottom: 12px;
}

.rewards-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
}

.reward-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  animation: rewardSlideIn 0.5s ease-out backwards;
}

.reward-text {
  font-size: 14px;
  font-weight: 600;
  color: #f8fafc;
}

@keyframes rewardSlideIn {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Button */
.continue-btn {
  padding: 14px 48px;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(249, 115, 22, 0.4);
}

.continue-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(249, 115, 22, 0.5);
}

/* Transition */
.level-up-enter-active {
  animation: overlayFadeIn 0.3s ease-out;
}

.level-up-leave-active {
  animation: overlayFadeOut 0.3s ease-in;
}

@keyframes overlayFadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes overlayFadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .ring,
  .particle,
  .level-up-content,
  .level-badge,
  .level-glow,
  .reward-item {
    animation: none;
  }

  .level-up-content {
    opacity: 1;
    transform: none;
  }
}
</style>
