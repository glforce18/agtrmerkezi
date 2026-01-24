<template>
  <div class="scroll-progress" v-show="showProgress">
    <div class="scroll-progress-bar" :style="{ width: progress + '%' }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const progress = ref(0)
const showProgress = ref(false)

const updateProgress = () => {
  const scrollTop = window.scrollY
  const docHeight = document.documentElement.scrollHeight - window.innerHeight

  if (docHeight > 0) {
    progress.value = Math.min((scrollTop / docHeight) * 100, 100)
    showProgress.value = scrollTop > 100
  }
}

onMounted(() => {
  window.addEventListener('scroll', updateProgress, { passive: true })
  updateProgress()
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateProgress)
})
</script>

<style scoped>
.scroll-progress {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(255, 255, 255, 0.05);
  z-index: 1000;
}

.scroll-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #f97316, #fb923c);
  transition: width 0.1s ease-out;
  box-shadow: 0 0 10px rgba(249, 115, 22, 0.5);
}
</style>
