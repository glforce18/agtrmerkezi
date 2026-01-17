<template>
  <div
    class="flex items-center gap-2 cursor-pointer group"
    :class="sizeClasses"
    @click="handleClick"
  >
    <!-- Logo Icon/SVG -->
    <div
      class="relative flex-shrink-0 transition-all duration-300"
      :class="[
        iconOnly ? '' : 'group-hover:scale-110',
        variant === 'glow' && 'animate-glow'
      ]"
    >
      <!-- Gaming Controller Icon with Gradient -->
      <svg
        :width="iconSize"
        :height="iconSize"
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        class="transition-transform duration-300"
      >
        <defs>
          <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" :style="`stop-color:${gradientStart};stop-opacity:1`" />
            <stop offset="100%" :style="`stop-color:${gradientEnd};stop-opacity:1`" />
          </linearGradient>
        </defs>

        <!-- Controller Base -->
        <path
          d="M32 12C18 12 8 22 8 32C8 42 12 48 18 50C20 51 22 51 24 50L28 46C29 45 30 44 32 44C34 44 35 45 36 46L40 50C42 51 44 51 46 50C52 48 56 42 56 32C56 22 46 12 32 12Z"
          fill="url(#logoGradient)"
          class="drop-shadow-lg"
        />

        <!-- D-Pad (Left) -->
        <circle cx="20" cy="30" r="2.5" fill="white" opacity="0.9" />
        <circle cx="14" cy="30" r="2" fill="white" opacity="0.7" />
        <circle cx="26" cy="30" r="2" fill="white" opacity="0.7" />
        <circle cx="20" cy="24" r="2" fill="white" opacity="0.7" />
        <circle cx="20" cy="36" r="2" fill="white" opacity="0.7" />

        <!-- Buttons (Right) -->
        <circle cx="44" cy="26" r="3" fill="#10b981" opacity="0.9" />
        <circle cx="50" cy="30" r="3" fill="#ef4444" opacity="0.9" />
        <circle cx="44" cy="34" r="3" fill="#3b82f6" opacity="0.9" />
        <circle cx="38" cy="30" r="3" fill="#f59e0b" opacity="0.9" />

        <!-- Center Buttons -->
        <rect x="28" y="28" width="8" height="2" rx="1" fill="white" opacity="0.6" />

        <!-- Glow Effect (for glow variant) -->
        <circle
          v-if="variant === 'glow'"
          cx="32"
          cy="32"
          r="30"
          fill="none"
          stroke="url(#logoGradient)"
          stroke-width="0.5"
          opacity="0.3"
          class="animate-ping"
        />
      </svg>

      <!-- Badge/Notification Dot -->
      <span
        v-if="showBadge"
        class="absolute -top-1 -right-1 flex h-3 w-3"
      >
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-gaming-red opacity-75"></span>
        <span class="relative inline-flex rounded-full h-3 w-3 bg-gaming-red"></span>
      </span>
    </div>

    <!-- Text Logo -->
    <div
      v-if="!iconOnly"
      class="flex flex-col leading-none transition-all duration-300"
      :class="variant === 'glow' && 'group-hover:text-shadow-lg'"
    >
      <span
        :class="textClasses"
        class="font-display tracking-wider transition-all duration-300"
      >
        {{ mainText }}
      </span>
      <span
        v-if="showSubtitle"
        class="text-xs font-medium opacity-70 tracking-wide"
        :class="subtitleColorClass"
      >
        {{ subtitle }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { BRAND_COLORS, GAMING_COLORS } from '@/constants/design'

const props = defineProps({
  // Size variants
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value)
  },

  // Display options
  iconOnly: {
    type: Boolean,
    default: false
  },

  showSubtitle: {
    type: Boolean,
    default: true
  },

  // Style variant
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'gradient', 'glow', 'minimal'].includes(value)
  },

  // Text
  mainText: {
    type: String,
    default: 'AGTR'
  },

  subtitle: {
    type: String,
    default: 'MERKEZI'
  },

  // Badge/notification
  showBadge: {
    type: Boolean,
    default: false
  },

  // Custom colors
  gradientStart: {
    type: String,
    default: BRAND_COLORS.primary
  },

  gradientEnd: {
    type: String,
    default: BRAND_COLORS.secondary
  },

  // Navigation
  to: {
    type: String,
    default: '/'
  }
})

const router = useRouter()

// Size mappings
const sizeClasses = computed(() => {
  const sizes = {
    xs: 'text-sm',
    sm: 'text-base',
    md: 'text-xl',
    lg: 'text-2xl',
    xl: 'text-4xl'
  }
  return sizes[props.size]
})

const iconSize = computed(() => {
  const sizes = {
    xs: 24,
    sm: 32,
    md: 40,
    lg: 56,
    xl: 72
  }
  return sizes[props.size]
})

// Text styling based on variant
const textClasses = computed(() => {
  const variants = {
    default: 'text-base-content font-extrabold',
    gradient: 'neon-text font-extrabold',
    glow: 'text-primary font-extrabold group-hover:text-shadow-lg',
    minimal: 'text-base-content/90 font-bold'
  }
  return variants[props.variant]
})

const subtitleColorClass = computed(() => {
  return props.variant === 'gradient' ? 'text-secondary' : 'text-base-content/70'
})

// Click handler
const handleClick = () => {
  if (props.to) {
    router.push(props.to)
  }
}
</script>

<style scoped>
.animate-glow {
  animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
  from {
    filter: drop-shadow(0 0 10px rgba(99, 102, 241, 0.5));
  }
  to {
    filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.8));
  }
}
</style>
