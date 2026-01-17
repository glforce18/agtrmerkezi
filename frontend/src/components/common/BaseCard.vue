<template>
  <div :class="cardClasses">
    <figure v-if="$slots.image" class="relative overflow-hidden">
      <slot name="image" />
      <div v-if="badge" class="badge badge-primary absolute top-4 right-4">{{ badge }}</div>
    </figure>

    <div :class="bodyClasses">
      <h2 v-if="title" :class="titleClasses">
        <slot name="title">{{ title }}</slot>
      </h2>

      <slot />

      <div v-if="$slots.actions" class="card-actions justify-end mt-4">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: String,
  badge: String,
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'glass', 'hover', 'glow', 'bordered'].includes(v)
  },
  compact: Boolean,
  bordered: Boolean,
  shadow: Boolean
})

const cardClasses = computed(() => {
  const classes = ['card', 'bg-base-200']

  const variants = {
    default: '',
    glass: 'glass-card',
    hover: 'card-hover',
    glow: 'card-glow',
    bordered: 'border-2 border-primary'
  }
  if (variants[props.variant]) classes.push(variants[props.variant])

  if (props.bordered) classes.push('border border-base-300')
  if (props.shadow) classes.push('shadow-xl')

  return classes.join(' ')
})

const bodyClasses = computed(() => {
  return props.compact ? 'card-body p-4' : 'card-body'
})

const titleClasses = computed(() => {
  return 'card-title text-xl font-bold'
})
</script>
