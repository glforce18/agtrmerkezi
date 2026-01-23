<template>
  <div
    class="skeleton-loader"
    :class="[
      `skeleton-loader--${variant}`,
      { 'skeleton-loader--animated': animated }
    ]"
    :style="skeletonStyle"
    role="status"
    :aria-label="ariaLabel"
  >
    <span class="sr-only">{{ ariaLabel }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // Basic dimensions
  width: {
    type: [String, Number],
    default: '100%'
  },
  height: {
    type: [String, Number],
    default: '20px'
  },
  // Predefined variants
  variant: {
    type: String,
    default: 'text',
    validator: (v) => ['text', 'title', 'avatar', 'card', 'button', 'image', 'circle'].includes(v)
  },
  // Border radius
  borderRadius: {
    type: [String, Number],
    default: null
  },
  // Enable/disable animation
  animated: {
    type: Boolean,
    default: true
  },
  // Accessibility
  ariaLabel: {
    type: String,
    default: 'Yukleniyor...'
  }
})

// Predefined dimensions for variants
const variantDimensions = {
  text: { height: '16px', radius: '4px' },
  title: { height: '24px', radius: '4px' },
  avatar: { width: '40px', height: '40px', radius: '50%' },
  card: { height: '120px', radius: '12px' },
  button: { width: '100px', height: '36px', radius: '8px' },
  image: { height: '200px', radius: '8px' },
  circle: { width: '48px', height: '48px', radius: '50%' }
}

const skeletonStyle = computed(() => {
  const variantDefaults = variantDimensions[props.variant] || {}

  const formatDimension = (value) => {
    if (typeof value === 'number') return `${value}px`
    return value
  }

  return {
    width: formatDimension(props.width || variantDefaults.width || '100%'),
    height: formatDimension(props.height || variantDefaults.height || '20px'),
    borderRadius: props.borderRadius
      ? formatDimension(props.borderRadius)
      : variantDefaults.radius || '4px'
  }
})
</script>

<style scoped>
.skeleton-loader {
  display: block;
  background: linear-gradient(
    90deg,
    var(--skeleton-base, #2a2a3e) 0%,
    var(--skeleton-base, #2a2a3e) 40%,
    var(--skeleton-highlight, #3a3a4e) 50%,
    var(--skeleton-base, #2a2a3e) 60%,
    var(--skeleton-base, #2a2a3e) 100%
  );
  background-size: 200% 100%;
}

.skeleton-loader--animated {
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

@keyframes skeleton-shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Screen reader only */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
