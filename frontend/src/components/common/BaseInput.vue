<template>
  <div class="form-control w-full">
    <label v-if="label" class="label">
      <span class="label-text font-medium">{{ label }}</span>
      <span v-if="required" class="label-text-alt text-error">*</span>
    </label>
    <div class="relative">
      <input
        :type="type"
        :placeholder="placeholder"
        :value="modelValue"
        :disabled="disabled"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
      />
      <component
        v-if="icon"
        :is="icon"
        class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 opacity-50"
      />
    </div>
    <label v-if="error || hint" class="label">
      <span v-if="error" class="label-text-alt text-error">{{ error }}</span>
      <span v-else-if="hint" class="label-text-alt">{{ hint }}</span>
    </label>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  type: { type: String, default: 'text' },
  label: String,
  placeholder: String,
  error: String,
  hint: String,
  disabled: Boolean,
  required: Boolean,
  icon: Object,
  size: { type: String, default: 'md' }
})

const emit = defineEmits(['update:modelValue', 'blur'])

const inputClasses = computed(() => {
  const classes = ['input', 'input-bordered', 'w-full', 'transition-all']

  if (props.error) classes.push('input-error')
  if (props.icon) classes.push('pl-10')

  const sizes = {
    sm: 'input-sm',
    md: '',
    lg: 'input-lg'
  }
  if (sizes[props.size]) classes.push(sizes[props.size])

  return classes.join(' ')
})

const handleInput = (e) => {
  emit('update:modelValue', e.target.value)
}

const handleBlur = (e) => {
  emit('blur', e)
}
</script>
