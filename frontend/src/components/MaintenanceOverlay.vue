<template>
  <Teleport to="body">
    <Transition name="maintenance-fade">
      <div v-if="show" class="maintenance-overlay">
        <div class="maintenance-content">
          <div class="maintenance-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
            </svg>
          </div>
          <h2 class="maintenance-title">Bakım Modu</h2>
          <p class="maintenance-message">{{ message }}</p>
          <div v-if="estimatedEnd" class="maintenance-eta">
            <span class="eta-label">Tahmini Bitiş:</span>
            <span class="eta-time">{{ formatDate(estimatedEnd) }}</span>
          </div>
          <button class="back-btn" @click="goBack">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m12 19-7-7 7-7"/>
              <path d="M19 12H5"/>
            </svg>
            Geri Dön
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  feature: {
    type: String,
    required: true
  },
  autoCheck: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['maintenance-status'])

const router = useRouter()
const show = ref(false)
const message = ref('')
const estimatedEnd = ref(null)

const checkMaintenance = async () => {
  try {
    const res = await fetch(`/api/maintenance/check/${props.feature}`)
    if (res.ok) {
      const data = await res.json()
      if (data.in_maintenance) {
        show.value = true
        message.value = data.message || 'Bu sayfa su anda bakimdadir.'
        estimatedEnd.value = data.estimated_end
        emit('maintenance-status', { inMaintenance: true, message: message.value })
      } else {
        show.value = false
        emit('maintenance-status', { inMaintenance: false })
      }
    }
  } catch (e) {
    console.error('Maintenance check error:', e)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  if (props.autoCheck) {
    checkMaintenance()
  }
})

watch(() => props.feature, () => {
  if (props.autoCheck) {
    checkMaintenance()
  }
})

defineExpose({ checkMaintenance, show })
</script>

<style scoped>
.maintenance-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(15, 15, 20, 0.98) 0%, rgba(25, 25, 35, 0.98) 100%);
  backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.maintenance-content {
  text-align: center;
  max-width: 500px;
}

.maintenance-icon {
  width: 140px;
  height: 140px;
  margin: 0 auto 32px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(234, 88, 12, 0.1) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f97316;
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 30px rgba(249, 115, 22, 0.3);
    transform: scale(1);
  }
  50% {
    box-shadow: 0 0 50px rgba(249, 115, 22, 0.5);
    transform: scale(1.02);
  }
}

.maintenance-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.maintenance-message {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  margin-bottom: 24px;
}

.maintenance-eta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: rgba(249, 115, 22, 0.1);
  border: 1px solid rgba(249, 115, 22, 0.3);
  border-radius: 12px;
  margin-bottom: 32px;
}

.eta-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
}

.eta-time {
  color: #f97316;
  font-weight: 600;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(249, 115, 22, 0.4);
}

.maintenance-fade-enter-active,
.maintenance-fade-leave-active {
  transition: all 0.3s ease;
}

.maintenance-fade-enter-from,
.maintenance-fade-leave-to {
  opacity: 0;
}
</style>
