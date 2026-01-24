<template>
  <div class="draft-indicator" :class="{ 'has-draft': hasDraft }">
    <!-- Saving Status -->
    <transition name="fade" mode="out-in">
      <div v-if="saving" class="status saving">
        <n-spin size="small" />
        <span>Kaydediliyor...</span>
      </div>
      <div v-else-if="lastSaved" class="status saved">
        <n-icon color="#18a058"><CheckCircle /></n-icon>
        <span>{{ formatLastSaved }}</span>
      </div>
      <div v-else-if="hasDraft" class="status has-draft">
        <n-icon color="#f0a020"><EditNote /></n-icon>
        <span>Taslak mevcut</span>
      </div>
    </transition>

    <!-- Actions -->
    <div class="actions" v-if="hasDraft && !saving">
      <n-button text size="small" @click="restoreDraft" :disabled="restoring">
        <template #icon><n-icon><RestoreOutlined /></n-icon></template>
        Geri Yukle
      </n-button>
      <n-button text size="small" type="error" @click="discardDraft" :disabled="discarding">
        <template #icon><n-icon><DeleteOutline /></n-icon></template>
        Sil
      </n-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { NButton, NIcon, NSpin } from 'naive-ui'
import { CheckCircleIcon, Edit3Icon, RotateCcwIcon, Trash2Icon } from 'lucide-vue-next'
import { draftApi } from '@/services/forumAdvanced.js'

const CheckCircle = CheckCircleIcon
const EditNote = Edit3Icon
const RestoreOutlined = RotateCcwIcon
const DeleteOutline = Trash2Icon
import { useThrottleFn, useDebounceFn } from '@vueuse/core'

const props = defineProps({
  draftType: {
    type: String,
    required: true,
    validator: (v) => ['topic', 'reply'].includes(v)
  },
  topicId: {
    type: Number,
    default: null
  },
  title: {
    type: String,
    default: ''
  },
  content: {
    type: String,
    default: ''
  },
  categoryId: {
    type: Number,
    default: null
  },
  pollData: {
    type: Object,
    default: null
  },
  autoSaveInterval: {
    type: Number,
    default: 30000 // 30 seconds
  }
})

const emit = defineEmits(['draft-restored', 'draft-discarded'])

// State
const saving = ref(false)
const lastSaved = ref(null)
const hasDraft = ref(false)
const restoring = ref(false)
const discarding = ref(false)
const draftData = ref(null)

// Computed
const formatLastSaved = computed(() => {
  if (!lastSaved.value) return ''
  const diff = Date.now() - lastSaved.value
  if (diff < 60000) return 'Az once kaydedildi'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} dk once`
  return `${Math.floor(diff / 3600000)} saat once`
})

// Auto-save with debounce
const saveDraft = useDebounceFn(async () => {
  if (!props.content && !props.title) return

  saving.value = true
  try {
    const data = {
      draft_type: props.draftType,
      title: props.title || null,
      content: props.content || null,
      category_id: props.categoryId,
      topic_id: props.topicId,
      poll_data: props.pollData,
      device_id: getDeviceId()
    }

    await draftApi.saveDraft(data)
    lastSaved.value = Date.now()
    hasDraft.value = true
  } catch (err) {
    // Silent fail
  } finally {
    saving.value = false
  }
}, 2000) // 2 second debounce

// Check for existing draft
const checkDraft = async () => {
  try {
    const { data } = await draftApi.getDraft(props.draftType, props.topicId)
    if (data.success && data.draft) {
      hasDraft.value = true
      draftData.value = data.draft
    }
  } catch (err) {
    // No draft
  }
}

// Restore draft
const restoreDraft = async () => {
  if (!draftData.value) {
    restoring.value = true
    try {
      const { data } = await draftApi.getDraft(props.draftType, props.topicId)
      if (data.success && data.draft) {
        draftData.value = data.draft
      }
    } catch (err) {
      window.$message?.error('Taslak yuklenemedi')
      return
    } finally {
      restoring.value = false
    }
  }

  emit('draft-restored', {
    title: draftData.value.title,
    content: draftData.value.content,
    categoryId: draftData.value.category_id,
    pollData: draftData.value.poll_data
  })
  window.$message?.success('Taslak yuklendi')
}

// Discard draft
const discardDraft = async () => {
  discarding.value = true
  try {
    await draftApi.deleteDraft(props.draftType, props.topicId)
    hasDraft.value = false
    draftData.value = null
    lastSaved.value = null
    emit('draft-discarded')
    window.$message?.success('Taslak silindi')
  } catch (err) {
    window.$message?.error('Taslak silinemedi')
  } finally {
    discarding.value = false
  }
}

// Get device ID for cross-device sync
const getDeviceId = () => {
  let deviceId = localStorage.getItem('agtr_device_id')
  if (!deviceId) {
    deviceId = 'device_' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem('agtr_device_id', deviceId)
  }
  return deviceId
}

// Watch for content changes
watch(() => [props.title, props.content], () => {
  saveDraft()
})

// Auto-save interval
let autoSaveTimer = null

onMounted(() => {
  checkDraft()
  autoSaveTimer = setInterval(() => {
    if (props.content || props.title) {
      saveDraft()
    }
  }, props.autoSaveInterval)
})

onUnmounted(() => {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
  }
})

// Expose methods
defineExpose({
  saveDraft,
  restoreDraft,
  discardDraft
})
</script>

<style scoped>
.draft-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--n-color);
  border-radius: 8px;
  font-size: 12px;
  min-height: 36px;
}

.draft-indicator.has-draft {
  background: var(--n-warning-color-suppl);
}

.status {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--n-text-color-3);
}

.status.saving {
  color: var(--n-primary-color);
}

.status.saved {
  color: var(--n-success-color);
}

.status.has-draft {
  color: var(--n-warning-color);
}

.actions {
  display: flex;
  gap: 8px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
