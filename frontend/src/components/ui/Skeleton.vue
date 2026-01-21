<template>
  <div
    class="skeleton"
    :class="[variant, { 'animate-pulse': animated }]"
    :style="skeletonStyle"
  ></div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'text', // text, circle, rect, card
    validator: (v) => ['text', 'circle', 'rect', 'card'].includes(v)
  },
  width: {
    type: [String, Number],
    default: '100%'
  },
  height: {
    type: [String, Number],
    default: null
  },
  animated: {
    type: Boolean,
    default: true
  }
})

const skeletonStyle = computed(() => {
  const style = {}

  if (props.width) {
    style.width = typeof props.width === 'number' ? `${props.width}px` : props.width
  }

  if (props.height) {
    style.height = typeof props.height === 'number' ? `${props.height}px` : props.height
  }

  return style
})
</script>

<style scoped>
.skeleton {
  background: linear-gradient(
    90deg,
    var(--skeleton-base, rgba(255,255,255,0.1)) 25%,
    var(--skeleton-highlight, rgba(255,255,255,0.2)) 50%,
    var(--skeleton-base, rgba(255,255,255,0.1)) 75%
  );
  background-size: 200% 100%;
  border-radius: 4px;
}

.skeleton.animate-pulse {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Variants */
.skeleton.text {
  height: 1em;
  margin: 0.25em 0;
}

.skeleton.circle {
  border-radius: 50%;
  width: 48px;
  height: 48px;
}

.skeleton.rect {
  height: 120px;
}

.skeleton.card {
  height: 200px;
  border-radius: 12px;
}

/* Dark mode support */
:root.dark .skeleton,
.dark .skeleton {
  --skeleton-base: rgba(255,255,255,0.05);
  --skeleton-highlight: rgba(255,255,255,0.1);
}
</style>
