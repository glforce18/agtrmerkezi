/**
 * AGTR Merkezi - Animated Number Counter
 * Sayıları animasyonlu şekilde artırır/azaltır
 * 
 * Kullanım:
 * const { animatedValue, animateTo } = useAnimatedNumber(0, { duration: 1000 })
 * animateTo(100) // 0'dan 100'e animasyonlu sayar
 */

import { ref, onUnmounted } from 'vue'

export function useAnimatedNumber(initialValue = 0, options = {}) {
  const {
    duration = 1000,  // Animasyon süresi (ms)
    easing = 'easeOutQuart',  // Easing fonksiyonu
    formatter = (val) => Math.round(val)  // Değer formatı
  } = options

  const animatedValue = ref(initialValue)
  let animationFrame = null
  let startTime = null
  let startValue = initialValue
  let endValue = initialValue

  // Easing functions
  const easingFunctions = {
    linear: (t) => t,
    easeOutQuad: (t) => t * (2 - t),
    easeOutCubic: (t) => (--t) * t * t + 1,
    easeOutQuart: (t) => 1 - (--t) * t * t * t,
    easeOutExpo: (t) => t === 1 ? 1 : 1 - Math.pow(2, -10 * t),
    easeInOutQuad: (t) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t
  }

  const easeFn = easingFunctions[easing] || easingFunctions.easeOutQuart

  const animate = (timestamp) => {
    if (!startTime) startTime = timestamp
    const elapsed = timestamp - startTime
    const progress = Math.min(elapsed / duration, 1)
    const easedProgress = easeFn(progress)

    animatedValue.value = formatter(startValue + (endValue - startValue) * easedProgress)

    if (progress < 1) {
      animationFrame = requestAnimationFrame(animate)
    }
  }

  const animateTo = (target) => {
    if (animationFrame) {
      cancelAnimationFrame(animationFrame)
    }
    startTime = null
    startValue = animatedValue.value
    endValue = target
    animationFrame = requestAnimationFrame(animate)
  }

  const setValue = (value) => {
    if (animationFrame) {
      cancelAnimationFrame(animationFrame)
    }
    animatedValue.value = formatter(value)
    startValue = value
    endValue = value
  }

  onUnmounted(() => {
    if (animationFrame) {
      cancelAnimationFrame(animationFrame)
    }
  })

  return {
    animatedValue,
    animateTo,
    setValue
  }
}

// Helper: Format large numbers (1000 -> 1K, 1000000 -> 1M)
export function formatCompactNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K'
  }
  return num.toString()
}

// Helper: Multiple animated numbers
export function useAnimatedNumbers(initialValues = {}, options = {}) {
  const values = {}
  const animators = {}

  for (const [key, value] of Object.entries(initialValues)) {
    const { animatedValue, animateTo, setValue } = useAnimatedNumber(value, options)
    values[key] = animatedValue
    animators[key] = { animateTo, setValue }
  }

  const animateAll = (targets) => {
    for (const [key, target] of Object.entries(targets)) {
      if (animators[key]) {
        animators[key].animateTo(target)
      }
    }
  }

  return {
    values,
    animators,
    animateAll
  }
}
