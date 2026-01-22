<template>
  <Teleport to="body">
    <div class="xp-container">
      <TransitionGroup name="xp">
        <div
          v-for="xp in xpGains"
          :key="xp.id"
          class="xp-gain"
          :class="[`xp-${xp.type || 'default'}`]"
          :style="xp.style"
        >
          <span class="xp-sign">+</span>
          <span class="xp-amount">{{ xp.amount }}</span>
          <span class="xp-label">{{ xp.label || 'XP' }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const xpGains = ref([])
let xpId = 0

const show = (amount, options = {}) => {
  const xp = {
    id: ++xpId,
    amount,
    label: options.label || 'XP',
    type: options.type || 'default',
    style: {
      left: options.x ? `${options.x}px` : '50%',
      top: options.y ? `${options.y}px` : '50%',
      transform: options.x ? 'translateX(-50%)' : 'translate(-50%, -50%)',
      '--float-direction': options.direction || '-60px'
    },
    duration: options.duration || 1500
  }

  xpGains.value.push(xp)

  setTimeout(() => {
    removeXP(xp.id)
  }, xp.duration)
}

const showAtElement = (element, amount, options = {}) => {
  if (!element) return

  const rect = element.getBoundingClientRect()
  const x = rect.left + rect.width / 2
  const y = rect.top + rect.height / 2

  show(amount, { ...options, x, y })
}

const removeXP = (id) => {
  const index = xpGains.value.findIndex(x => x.id === id)
  if (index !== -1) {
    xpGains.value.splice(index, 1)
  }
}

defineExpose({ show, showAtElement })
</script>

<style scoped>
.xp-container {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9998;
}

.xp-gain {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 4px;
  font-family: 'Orbitron', 'Poppins', sans-serif;
  font-size: 24px;
  font-weight: 800;
  color: #22c55e;
  text-shadow:
    0 0 10px rgba(34, 197, 94, 0.8),
    0 0 20px rgba(34, 197, 94, 0.4),
    0 2px 4px rgba(0, 0, 0, 0.5);
  white-space: nowrap;
  animation: xpFloatUp 1.5s ease-out forwards;
}

.xp-sign {
  color: inherit;
}

.xp-amount {
  color: inherit;
}

.xp-label {
  font-size: 14px;
  font-weight: 600;
  opacity: 0.8;
}

/* XP Types */
.xp-default {
  color: #22c55e;
}

.xp-bonus {
  color: #fbbf24;
  font-size: 28px;
  text-shadow:
    0 0 15px rgba(251, 191, 36, 0.8),
    0 0 30px rgba(251, 191, 36, 0.4),
    0 2px 4px rgba(0, 0, 0, 0.5);
}

.xp-critical {
  color: #ef4444;
  font-size: 32px;
  text-shadow:
    0 0 15px rgba(239, 68, 68, 0.8),
    0 0 30px rgba(239, 68, 68, 0.4),
    0 2px 4px rgba(0, 0, 0, 0.5);
}

.xp-armor {
  color: #f97316;
  text-shadow:
    0 0 10px rgba(249, 115, 22, 0.8),
    0 0 20px rgba(249, 115, 22, 0.4),
    0 2px 4px rgba(0, 0, 0, 0.5);
}

.xp-money {
  color: #22c55e;
}

@keyframes xpFloatUp {
  0% {
    transform: translateY(0) scale(0.5);
    opacity: 0;
  }
  20% {
    transform: translateY(-10px) scale(1.2);
    opacity: 1;
  }
  40% {
    transform: translateY(-25px) scale(1);
    opacity: 1;
  }
  100% {
    transform: translateY(var(--float-direction, -60px)) scale(0.8);
    opacity: 0;
  }
}

/* Vue Transitions */
.xp-enter-active {
  animation: xpFloatUp 1.5s ease-out forwards;
}

.xp-leave-active {
  animation: xpFadeOut 0.3s ease-out forwards;
}

@keyframes xpFadeOut {
  to {
    opacity: 0;
    transform: scale(0.5);
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .xp-gain {
    animation: xpFadeOnly 1s ease-out forwards;
  }

  @keyframes xpFadeOnly {
    from { opacity: 0; }
    50% { opacity: 1; }
    to { opacity: 0; }
  }
}
</style>
