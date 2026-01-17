<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="handleClick"
  >
    <span v-if="loading" class="loading loading-spinner loading-sm"></span>
    <component v-if="icon && !loading" :is="icon" :class="iconClasses" />
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'secondary', 'accent', 'ghost', 'outline', 'gaming'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['xs', 'sm', 'md', 'lg'].includes(v)
  },
  type: {
    type: String,
    default: 'button'
  },
  disabled: Boolean,
  loading: Boolean,
  block: Boolean,
  icon: Object
})

const emit = defineEmits(['click'])

const buttonClasses = computed(() => {
  const classes = ['btn', 'transition-all', 'duration-300']

  // Variant
  const variants = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    accent: 'btn-accent',
    ghost: 'btn-ghost',
    outline: 'btn-outline',
    gaming: 'btn-gaming'
  }
  classes.push(variants[props.variant])

  // Size
  const sizes = {
    xs: 'btn-xs',
    sm: 'btn-sm',
    md: '',
    lg: 'btn-lg'
  }
  if (sizes[props.size]) classes.push(sizes[props.size])

  if (props.block) classes.push('btn-block')
  if (props.loading) classes.push('gap-2')

  return classes.join(' ')
})

const iconClasses = computed(() => {
  const sizes = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  }
  return sizes[props.size]
})

const handleClick = (e) => {
  if (!props.disabled && !props.loading) {
    emit('click', e)
  }
}
</script>
