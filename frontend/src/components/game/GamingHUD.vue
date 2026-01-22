<template>
  <div class="gaming-hud" :class="{ 'hud-visible': isVisible }">
    <!-- Sol Alt - Health & Armor -->
    <div class="hud-section hud-left">
      <div class="hud-item health-bar">
        <div class="hud-icon">
          <Heart class="w-7 h-7" />
        </div>
        <div class="hud-value-container">
          <span class="hud-value">{{ health }}</span>
          <div class="hud-bar">
            <div class="hud-bar-fill health-fill" :style="{ width: health + '%' }"></div>
          </div>
        </div>
      </div>

      <div class="hud-item armor-bar">
        <div class="hud-icon armor-icon">
          <Shield class="w-7 h-7" />
        </div>
        <div class="hud-value-container">
          <span class="hud-value">{{ armor }}</span>
          <div class="hud-bar">
            <div class="hud-bar-fill armor-fill" :style="{ width: armor + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Orta Alt - Aktif Silah -->
    <div class="hud-section hud-center">
      <div class="weapon-display">
        <div class="weapon-icon floating-weapon">
          <Crosshair class="w-10 h-10" />
        </div>
        <div class="weapon-info">
          <span class="weapon-name">{{ weaponNames[currentWeapon] }}</span>
          <div class="ammo-display">
            <span class="ammo-clip">{{ ammoClip }}</span>
            <span class="ammo-separator">/</span>
            <span class="ammo-reserve">{{ ammoReserve }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Sag Alt - Money & Round -->
    <div class="hud-section hud-right">
      <div class="hud-item money-display">
        <div class="hud-icon money-icon">
          <DollarSign class="w-7 h-7" />
        </div>
        <span class="money-value">${{ money.toLocaleString() }}</span>
      </div>

      <div class="hud-item round-display">
        <span class="round-label">ROUND</span>
        <span class="round-value">{{ round }}</span>
      </div>
    </div>

    <!-- Ust Orta - Kill Feed -->
    <div class="kill-feed-container">
      <TransitionGroup name="kill-feed" tag="div" class="kill-feed">
        <div
          v-for="kill in recentKills"
          :key="kill.id"
          class="kill-entry"
          :class="{ 'headshot': kill.headshot }"
        >
          <span class="killer-name" :class="kill.killerTeam">{{ kill.killer }}</span>
          <div class="kill-icon">
            <Skull v-if="kill.headshot" class="w-5 h-5" />
            <Swords v-else class="w-5 h-5" />
          </div>
          <span class="victim-name" :class="kill.victimTeam">{{ kill.victim }}</span>
        </div>
      </TransitionGroup>
    </div>

    <!-- Crosshair -->
    <div v-if="showCrosshair" class="crosshair">
      <div class="crosshair-line crosshair-top"></div>
      <div class="crosshair-line crosshair-bottom"></div>
      <div class="crosshair-line crosshair-left"></div>
      <div class="crosshair-line crosshair-right"></div>
      <div class="crosshair-dot"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Heart, Shield, Crosshair, DollarSign, Skull, Swords } from 'lucide-vue-next'

const props = defineProps({
  showCrosshair: {
    type: Boolean,
    default: false
  }
})

const isVisible = ref(false)
const health = ref(100)
const armor = ref(100)
const money = ref(16000)
const round = ref(1)
const ammoClip = ref(30)
const ammoReserve = ref(90)
const currentWeapon = ref('ak47')

const weaponNames = {
  'ak47': 'AK-47',
  'awp': 'AWP',
  'm4a1': 'M4A1',
  'deagle': 'Desert Eagle',
  'knife': 'Knife',
  'crowbar': 'Crowbar',
  'gauss': 'Gauss Gun',
  'crossbow': 'Crossbow'
}

// Kill feed - gerçek oyun verisinden gelecek
const recentKills = ref([])

onMounted(() => {
  isVisible.value = true
  // Demo modu devre dışı - gerçek oyun verisi bağlandığında kullanılacak
})

onUnmounted(() => {
  // Cleanup for future real-time connections
})
</script>

<style scoped>
.gaming-hud {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 50;
  opacity: 0;
  transition: opacity 0.5s ease;
  font-family: 'Orbitron', 'Inter', monospace;
}

.hud-visible {
  opacity: 1;
}

/* HUD Sections */
.hud-section {
  position: absolute;
  display: flex;
  gap: 16px;
}

.hud-left {
  bottom: 20px;
  left: 20px;
  flex-direction: column;
}

.hud-center {
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
}

.hud-right {
  bottom: 20px;
  right: 20px;
  flex-direction: column;
  align-items: flex-end;
}

/* HUD Items */
.hud-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 8px 14px;
}

.hud-icon {
  width: 28px;
  height: 28px;
  color: #ef4444;
  filter: drop-shadow(0 0 8px rgba(239, 68, 68, 0.5));
}

.hud-icon.armor-icon {
  color: #3b82f6;
  filter: drop-shadow(0 0 8px rgba(59, 130, 246, 0.5));
}

.hud-icon.money-icon {
  color: #22c55e;
  filter: drop-shadow(0 0 8px rgba(34, 197, 94, 0.5));
}

.hud-icon svg {
  width: 100%;
  height: 100%;
}

.hud-value-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hud-value {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
  min-width: 36px;
}

.hud-bar {
  width: 80px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.hud-bar-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 3px;
}

.health-fill {
  background: linear-gradient(90deg, #ef4444, #f97316);
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
}

.armor-fill {
  background: linear-gradient(90deg, #3b82f6, #06b6d4);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
}

/* Weapon Display */
.weapon-display {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(249, 115, 22, 0.3);
  border-radius: 12px;
  padding: 12px 20px;
}

.weapon-icon {
  width: 64px;
  height: 40px;
  color: #f97316;
  filter: drop-shadow(0 0 12px rgba(249, 115, 22, 0.6));
}

.weapon-icon svg {
  width: 100%;
  height: 100%;
}

.weapon-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.weapon-name {
  font-size: 12px;
  color: #a1a1aa;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.ammo-display {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
}

.ammo-clip {
  color: #f97316;
  text-shadow: 0 0 10px rgba(249, 115, 22, 0.5);
}

.ammo-separator {
  color: #6b7280;
  margin: 0 4px;
}

.ammo-reserve {
  color: #a1a1aa;
}

/* Money Display */
.money-display {
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.money-value {
  font-size: 20px;
  font-weight: 700;
  color: #22c55e;
  text-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
}

/* Round Display */
.round-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 16px;
}

.round-label {
  font-size: 10px;
  color: #6b7280;
  letter-spacing: 2px;
}

.round-value {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

/* Kill Feed */
.kill-feed-container {
  position: absolute;
  top: 80px;
  right: 20px;
}

.kill-feed {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.kill-entry {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 13px;
  animation: killSlideIn 0.3s ease-out;
}

.kill-entry.headshot {
  border-left: 3px solid #ef4444;
}

@keyframes killSlideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.killer-name {
  font-weight: 600;
}

.killer-name.ct {
  color: #3b82f6;
}

.killer-name.t {
  color: #f97316;
}

.victim-name {
  font-weight: 500;
  color: #a1a1aa;
}

.victim-name.ct {
  color: #60a5fa;
}

.victim-name.t {
  color: #fb923c;
}

.kill-icon {
  width: 20px;
  height: 20px;
  color: #fff;
}

.kill-icon svg {
  width: 100%;
  height: 100%;
}

/* Kill Feed Transitions */
.kill-feed-enter-active {
  transition: all 0.3s ease-out;
}

.kill-feed-leave-active {
  transition: all 0.3s ease-in;
}

.kill-feed-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.kill-feed-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* Crosshair */
.crosshair {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.crosshair-line {
  position: absolute;
  background: #22c55e;
  box-shadow: 0 0 4px rgba(34, 197, 94, 0.8);
}

.crosshair-top {
  width: 2px;
  height: 12px;
  left: -1px;
  top: -20px;
}

.crosshair-bottom {
  width: 2px;
  height: 12px;
  left: -1px;
  top: 8px;
}

.crosshair-left {
  width: 12px;
  height: 2px;
  left: -20px;
  top: -1px;
}

.crosshair-right {
  width: 12px;
  height: 2px;
  left: 8px;
  top: -1px;
}

.crosshair-dot {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #22c55e;
  border-radius: 50%;
  left: -2px;
  top: -2px;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.8);
}

/* Floating Animation */
.floating-weapon {
  animation: weaponFloat 3s ease-in-out infinite;
}

@keyframes weaponFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .hud-left,
  .hud-right {
    display: none;
  }

  .kill-feed-container {
    top: 70px;
    right: 10px;
  }

  .kill-entry {
    font-size: 11px;
    padding: 4px 8px;
  }
}
</style>
