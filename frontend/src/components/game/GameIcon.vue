<template>
  <svg
    :class="['game-icon', sizeClass, { 'floating-weapon': animated }]"
    :style="iconStyle"
    xmlns="http://www.w3.org/2000/svg"
    :width="computedSize"
    :height="computedSize"
    viewBox="0 0 24 24"
    fill="currentColor"
  >
    <use :href="`/static/images/icons.svg#icon-${name}`" />
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: {
    type: String,
    required: true,
    validator: (value) => {
      const validIcons = [
        // CS Weapons
        'weapon-ak47', 'weapon-awp', 'weapon-m4a1', 'weapon-deagle', 'weapon-knife',
        // HL Weapons
        'weapon-crowbar', 'weapon-gauss', 'weapon-crossbow',
        // HUD Elements
        'hud-health', 'hud-armor', 'hud-ammo', 'hud-money',
        // Kill Feed
        'kill-headshot', 'kill-arrow', 'kill-bomb', 'kill-defuse', 'kill-streak',
        // Game icons
        'halflife', 'ag', 'cs16', 'hldm', 'cs-crosshair',
        // Effects
        'muzzle-flash', 'recoil', 'xp-orb', 'server-pulse',
        // Ranks
        'rank-legendary', 'rank-master', 'rank-diamond', 'rank-gold', 'rank-silver', 'rank-bronze',
        // Achievements
        'achievement-first-win', 'achievement-100kills', 'achievement-champion',
        'achievement-veteran', 'achievement-top10', 'achievement-streak', 'achievement-early',
        'achievement-unlock', 'level-up', 'victory', 'star-burst', 'sparkles', 'party',
        'confetti', 'fireworks'
      ]
      return validIcons.includes(value) || value.startsWith('weapon-') || value.startsWith('hud-') || value.startsWith('kill-') || value.startsWith('rank-')
    }
  },
  size: {
    type: [String, Number],
    default: 'md'
  },
  color: {
    type: String,
    default: 'currentColor'
  },
  animated: {
    type: Boolean,
    default: false
  },
  animationDelay: {
    type: String,
    default: '0s'
  }
})

const sizeMap = {
  xs: 16,
  sm: 20,
  md: 24,
  lg: 32,
  xl: 48,
  '2xl': 64
}

const computedSize = computed(() => {
  if (typeof props.size === 'number') return props.size
  return sizeMap[props.size] || 24
})

const sizeClass = computed(() => {
  if (typeof props.size === 'string' && sizeMap[props.size]) {
    return `icon-${props.size}`
  }
  return ''
})

const iconStyle = computed(() => ({
  color: props.color,
  animationDelay: props.animationDelay
}))
</script>

<style scoped>
.game-icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
  transition: color 0.2s ease, transform 0.2s ease;
}

.game-icon:hover {
  transform: scale(1.1);
}

/* Size classes */
.icon-xs { width: 16px; height: 16px; }
.icon-sm { width: 20px; height: 20px; }
.icon-md { width: 24px; height: 24px; }
.icon-lg { width: 32px; height: 32px; }
.icon-xl { width: 48px; height: 48px; }
.icon-2xl { width: 64px; height: 64px; }

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .game-icon {
    animation: none !important;
  }
}
</style>
