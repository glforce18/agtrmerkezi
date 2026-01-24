<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="isActive && currentStep" class="onboarding-overlay">
        <!-- Backdrop with cutout -->
        <div class="onboarding-backdrop"></div>

        <!-- Highlight box -->
        <div
          ref="highlightRef"
          class="onboarding-highlight"
          :style="highlightStyle"
        ></div>

        <!-- Tooltip -->
        <div
          ref="tooltipRef"
          class="onboarding-tooltip"
          :class="tooltipPosition"
          :style="tooltipStyle"
        >
          <!-- Arrow -->
          <div class="onboarding-arrow" :class="tooltipPosition"></div>

          <!-- Progress Dots -->
          <div class="onboarding-progress">
            <div
              v-for="(step, idx) in steps"
              :key="step.id"
              class="onboarding-dot"
              :class="{
                active: idx === currentIndex,
                completed: idx < currentIndex
              }"
              @click="goToStep(idx)"
            ></div>
          </div>

          <!-- Content -->
          <div class="onboarding-content">
            <div class="onboarding-step-label">
              Adim {{ currentIndex + 1 }} / {{ steps.length }}
            </div>
            <h3 class="onboarding-title">{{ currentStep.title }}</h3>
            <p class="onboarding-description">{{ currentStep.description }}</p>
          </div>

          <!-- Actions -->
          <div class="onboarding-actions">
            <button class="onboarding-skip" @click="skip">
              {{ currentIndex === steps.length - 1 ? 'Kapat' : 'Atla' }}
            </button>
            <div class="onboarding-nav">
              <button
                v-if="currentIndex > 0"
                class="onboarding-btn secondary"
                @click="prev"
              >
                <ChevronLeftIcon class="w-4 h-4" />
                Geri
              </button>
              <button
                class="onboarding-btn primary"
                @click="next"
              >
                {{ currentIndex === steps.length - 1 ? 'Bitir' : 'Sonraki' }}
                <ChevronRightIcon v-if="currentIndex < steps.length - 1" class="w-4 h-4" />
                <CheckIcon v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Don't show again -->
          <label class="onboarding-checkbox">
            <input type="checkbox" v-model="dontShowAgain" />
            <span>Bir daha gosterme</span>
          </label>
        </div>

        <!-- Confetti on complete -->
        <div v-if="showConfetti" class="onboarding-confetti">
          <div v-for="n in 30" :key="n" class="confetti-piece" :style="getConfettiStyle(n)"></div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ChevronLeftIcon, ChevronRightIcon, CheckIcon } from 'lucide-vue-next'

const props = defineProps({
  steps: {
    type: Array,
    required: true
  },
  tourId: {
    type: String,
    required: true
  },
  autoStart: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['start', 'complete', 'skip', 'step-change'])

// State
const isActive = ref(false)
const currentIndex = ref(0)
const highlightRef = ref(null)
const tooltipRef = ref(null)
const dontShowAgain = ref(false)
const showConfetti = ref(false)

const highlightStyle = ref({})
const tooltipStyle = ref({})
const tooltipPosition = ref('bottom')

// Computed
const currentStep = computed(() => props.steps[currentIndex.value] || null)

// Methods
const start = () => {
  // Check if already seen
  const seen = localStorage.getItem(`onboarding_${props.tourId}_seen`)
  if (seen === 'true') return

  isActive.value = true
  currentIndex.value = 0
  emit('start')
  nextTick(updatePositions)
}

const stop = () => {
  isActive.value = false
  showConfetti.value = false

  if (dontShowAgain.value) {
    localStorage.setItem(`onboarding_${props.tourId}_seen`, 'true')
  }
}

const next = () => {
  if (currentIndex.value < props.steps.length - 1) {
    currentIndex.value++
    emit('step-change', currentIndex.value)
    nextTick(updatePositions)
  } else {
    complete()
  }
}

const prev = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
    emit('step-change', currentIndex.value)
    nextTick(updatePositions)
  }
}

const goToStep = (index) => {
  currentIndex.value = index
  emit('step-change', index)
  nextTick(updatePositions)
}

const skip = () => {
  emit('skip', currentIndex.value)
  stop()
}

const complete = () => {
  showConfetti.value = true
  emit('complete')

  setTimeout(() => {
    stop()
  }, 2000)

  // Always mark as seen on complete
  localStorage.setItem(`onboarding_${props.tourId}_seen`, 'true')
}

const updatePositions = () => {
  if (!currentStep.value?.target) return

  const target = document.querySelector(currentStep.value.target)
  if (!target) return

  const rect = target.getBoundingClientRect()
  const padding = 8

  // Highlight position
  highlightStyle.value = {
    top: `${rect.top - padding}px`,
    left: `${rect.left - padding}px`,
    width: `${rect.width + padding * 2}px`,
    height: `${rect.height + padding * 2}px`
  }

  // Calculate best tooltip position
  const viewportHeight = window.innerHeight
  const viewportWidth = window.innerWidth
  const spaceAbove = rect.top
  const spaceBelow = viewportHeight - rect.bottom
  const spaceLeft = rect.left
  const spaceRight = viewportWidth - rect.right

  // Determine position
  if (spaceBelow >= 200) {
    tooltipPosition.value = 'bottom'
    tooltipStyle.value = {
      top: `${rect.bottom + 16}px`,
      left: `${rect.left + rect.width / 2}px`,
      transform: 'translateX(-50%)'
    }
  } else if (spaceAbove >= 200) {
    tooltipPosition.value = 'top'
    tooltipStyle.value = {
      bottom: `${viewportHeight - rect.top + 16}px`,
      left: `${rect.left + rect.width / 2}px`,
      transform: 'translateX(-50%)'
    }
  } else if (spaceRight >= 350) {
    tooltipPosition.value = 'right'
    tooltipStyle.value = {
      top: `${rect.top + rect.height / 2}px`,
      left: `${rect.right + 16}px`,
      transform: 'translateY(-50%)'
    }
  } else {
    tooltipPosition.value = 'left'
    tooltipStyle.value = {
      top: `${rect.top + rect.height / 2}px`,
      right: `${viewportWidth - rect.left + 16}px`,
      transform: 'translateY(-50%)'
    }
  }

  // Scroll into view if needed
  if (rect.top < 100 || rect.bottom > viewportHeight - 100) {
    target.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

const getConfettiStyle = (n) => {
  const colors = ['#f97316', '#8b5cf6', '#06b6d4', '#22c55e', '#eab308', '#ef4444']
  return {
    '--delay': `${Math.random() * 0.5}s`,
    '--x': `${Math.random() * 200 - 100}vw`,
    '--y': `${Math.random() * 100}vh`,
    '--rotation': `${Math.random() * 720}deg`,
    backgroundColor: colors[n % colors.length]
  }
}

// Reset tour
const reset = () => {
  localStorage.removeItem(`onboarding_${props.tourId}_seen`)
}

// Handle resize
const handleResize = () => {
  if (isActive.value) {
    updatePositions()
  }
}

// Lifecycle
onMounted(() => {
  if (props.autoStart) {
    start()
  }
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// Expose methods
defineExpose({
  start,
  stop,
  next,
  prev,
  reset
})
</script>

<style scoped>
.onboarding-overlay {
  position: fixed;
  inset: 0;
  z-index: 99999;
  pointer-events: none;
}

.onboarding-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  pointer-events: auto;
}

.onboarding-highlight {
  position: fixed;
  border-radius: 12px;
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.75);
  transition: all 0.3s ease;
  pointer-events: none;
  z-index: 1;
}

.onboarding-highlight::after {
  content: '';
  position: absolute;
  inset: -4px;
  border: 2px solid #f97316;
  border-radius: 14px;
  animation: highlight-pulse 2s ease-in-out infinite;
}

@keyframes highlight-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(249, 115, 22, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(249, 115, 22, 0); }
}

.onboarding-tooltip {
  position: fixed;
  width: 340px;
  padding: 20px;
  background: #18181b;
  border: 1px solid #f97316;
  border-radius: 16px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), 0 0 30px rgba(249, 115, 22, 0.2);
  pointer-events: auto;
  z-index: 2;
  animation: tooltip-appear 0.3s ease-out;
}

@keyframes tooltip-appear {
  from {
    opacity: 0;
    transform: translateX(-50%) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) scale(1);
  }
}

.onboarding-tooltip.top {
  animation-name: tooltip-appear-top;
}

@keyframes tooltip-appear-top {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(10px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0) scale(1);
  }
}

.onboarding-tooltip.right,
.onboarding-tooltip.left {
  animation-name: tooltip-appear-side;
}

@keyframes tooltip-appear-side {
  from {
    opacity: 0;
    transform: translateY(-50%) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(-50%) scale(1);
  }
}

/* Arrow */
.onboarding-arrow {
  position: absolute;
  width: 12px;
  height: 12px;
  background: #18181b;
  border: 1px solid #f97316;
  transform: rotate(45deg);
}

.onboarding-arrow.bottom {
  top: -7px;
  left: 50%;
  margin-left: -6px;
  border-right: none;
  border-bottom: none;
}

.onboarding-arrow.top {
  bottom: -7px;
  left: 50%;
  margin-left: -6px;
  border-left: none;
  border-top: none;
}

.onboarding-arrow.right {
  left: -7px;
  top: 50%;
  margin-top: -6px;
  border-top: none;
  border-right: none;
}

.onboarding-arrow.left {
  right: -7px;
  top: 50%;
  margin-top: -6px;
  border-bottom: none;
  border-left: none;
}

/* Progress */
.onboarding-progress {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
}

.onboarding-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3f3f46;
  cursor: pointer;
  transition: all 0.2s;
}

.onboarding-dot:hover {
  background: #52525b;
}

.onboarding-dot.active {
  background: #f97316;
  transform: scale(1.25);
}

.onboarding-dot.completed {
  background: #22c55e;
}

/* Content */
.onboarding-content {
  margin-bottom: 20px;
}

.onboarding-step-label {
  font-size: 11px;
  font-weight: 600;
  color: #f97316;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.onboarding-title {
  font-size: 18px;
  font-weight: 600;
  color: #fafafa;
  margin: 0 0 8px 0;
}

.onboarding-description {
  font-size: 14px;
  color: #a1a1aa;
  line-height: 1.6;
  margin: 0;
}

/* Actions */
.onboarding-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.onboarding-skip {
  background: none;
  border: none;
  color: #71717a;
  font-size: 13px;
  cursor: pointer;
  transition: color 0.2s;
}

.onboarding-skip:hover {
  color: #a1a1aa;
}

.onboarding-nav {
  display: flex;
  gap: 8px;
}

.onboarding-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.onboarding-btn.primary {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border: none;
  color: white;
}

.onboarding-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
}

.onboarding-btn.secondary {
  background: #27272a;
  border: 1px solid #3f3f46;
  color: #a1a1aa;
}

.onboarding-btn.secondary:hover {
  background: #3f3f46;
  color: #fafafa;
}

/* Checkbox */
.onboarding-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #71717a;
  cursor: pointer;
}

.onboarding-checkbox input {
  width: 14px;
  height: 14px;
  accent-color: #f97316;
}

/* Confetti */
.onboarding-confetti {
  position: fixed;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.confetti-piece {
  position: absolute;
  top: -20px;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  animation: confetti-fall 2.5s ease-out forwards;
  animation-delay: var(--delay);
}

@keyframes confetti-fall {
  0% {
    transform: translateX(50vw) translateY(0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateX(calc(50vw + var(--x))) translateY(var(--y)) rotate(var(--rotation));
    opacity: 0;
  }
}

/* Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Mobile */
@media (max-width: 480px) {
  .onboarding-tooltip {
    width: calc(100% - 32px);
    left: 16px !important;
    right: 16px !important;
    transform: none !important;
  }

  .onboarding-tooltip.bottom,
  .onboarding-tooltip.top {
    left: 16px !important;
  }
}
</style>
