<template>
  <Teleport to="body">
    <div class="kill-feed-container">
      <TransitionGroup name="kill-feed">
        <div
          v-for="kill in kills"
          :key="kill.id"
          class="kill-feed-item"
          :class="{ 'headshot': kill.headshot }"
        >
          <!-- Killer -->
          <span class="player killer" :style="{ color: kill.killerColor || '#22c55e' }">
            {{ kill.killer }}
          </span>

          <!-- Weapon Icon -->
          <div class="weapon-icon">
            <GameIcon
              v-if="kill.weapon"
              :name="`weapon-${kill.weapon}`"
              size="sm"
              color="#f8fafc"
            />
            <img
              v-else-if="kill.weaponImage"
              :src="kill.weaponImage"
              :alt="kill.weaponName || 'weapon'"
              class="weapon-img"
            />
            <span v-else class="weapon-text">{{ kill.weaponName || '?' }}</span>
          </div>

          <!-- Headshot Indicator -->
          <div v-if="kill.headshot" class="headshot-icon">
            <GameIcon name="kill-headshot" size="sm" color="#ef4444" />
          </div>

          <!-- Victim -->
          <span class="player victim" :style="{ color: kill.victimColor || '#ef4444' }">
            {{ kill.victim }}
          </span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import GameIcon from './GameIcon.vue'

const kills = ref([])
let killId = 0
const maxKills = 5

const addKill = (data) => {
  const kill = {
    id: ++killId,
    killer: data.killer || 'Player',
    victim: data.victim || 'Enemy',
    weapon: data.weapon || null,
    weaponImage: data.weaponImage || null,
    weaponName: data.weaponName || null,
    headshot: data.headshot || false,
    killerColor: data.killerColor || '#22c55e',
    victimColor: data.victimColor || '#ef4444',
    duration: data.duration || 4000
  }

  kills.value.push(kill)

  // Limit maximum kills shown
  if (kills.value.length > maxKills) {
    kills.value.shift()
  }

  // Auto remove after duration
  setTimeout(() => {
    removeKill(kill.id)
  }, kill.duration)
}

const removeKill = (id) => {
  const index = kills.value.findIndex(k => k.id === id)
  if (index !== -1) {
    kills.value.splice(index, 1)
  }
}

const clear = () => {
  kills.value = []
}

defineExpose({ addKill, removeKill, clear })
</script>

<style scoped>
.kill-feed-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 9997;
  display: flex;
  flex-direction: column;
  gap: 6px;
  pointer-events: none;
}

.kill-feed-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.85) 0%, rgba(0, 0, 0, 0.75) 100%);
  border-radius: 6px;
  border-left: 3px solid transparent;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  backdrop-filter: blur(8px);
}

.kill-feed-item.headshot {
  border-left-color: #ef4444;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(0, 0, 0, 0.85) 20%);
}

.player {
  font-weight: 700;
}

.killer {
  color: #22c55e;
}

.victim {
  color: #ef4444;
}

.weapon-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.weapon-img {
  height: 16px;
  width: auto;
  filter: brightness(0) invert(1);
}

.weapon-text {
  color: #94a3b8;
  font-size: 11px;
}

.headshot-icon {
  display: flex;
  align-items: center;
}

/* Vue Transitions */
.kill-feed-enter-active {
  animation: killFeedSlideIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.kill-feed-leave-active {
  animation: killFeedSlideOut 0.3s ease-in;
}

.kill-feed-move {
  transition: transform 0.3s ease;
}

@keyframes killFeedSlideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes killFeedSlideOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(-50%);
    opacity: 0;
  }
}

/* Responsive */
@media (max-width: 640px) {
  .kill-feed-container {
    top: 70px;
    right: 10px;
    left: 10px;
  }

  .kill-feed-item {
    font-size: 12px;
    padding: 6px 10px;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .kill-feed-enter-active,
  .kill-feed-leave-active {
    animation: none;
    transition: opacity 0.2s ease;
  }

  .kill-feed-enter-from,
  .kill-feed-leave-to {
    opacity: 0;
  }
}
</style>
