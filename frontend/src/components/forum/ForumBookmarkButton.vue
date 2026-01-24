<template>
  <n-button
    :type="isBookmarked ? 'primary' : 'default'"
    :ghost="!isBookmarked"
    :loading="loading"
    @click="toggleBookmark"
    v-bind="$attrs"
  >
    <template #icon>
      <BookmarkIcon v-if="isBookmarked" class="w-4 h-4" />
      <BookmarkIcon v-else class="w-4 h-4" />
    </template>
    <slot>
      {{ isBookmarked ? 'Kaydedildi' : 'Kaydet' }}
    </slot>
  </n-button>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { NButton } from 'naive-ui'
import { BookmarkIcon } from 'lucide-vue-next'
import { bookmarkApi } from '@/services/forumAdvanced.js'

const props = defineProps({
  topicId: {
    type: Number,
    required: true
  },
  initialBookmarked: {
    type: Boolean,
    default: null
  }
})

const emit = defineEmits(['toggled'])

// State
const isBookmarked = ref(props.initialBookmarked ?? false)
const loading = ref(false)

// Methods
const checkBookmark = async () => {
  if (props.initialBookmarked !== null) return

  try {
    const { data } = await bookmarkApi.isBookmarked(props.topicId)
    if (data.success) {
      isBookmarked.value = data.bookmarked
    }
  } catch (err) {
    // Silent fail
  }
}

const toggleBookmark = async () => {
  loading.value = true
  try {
    const { data } = await bookmarkApi.toggleBookmark(props.topicId)
    if (data.success) {
      isBookmarked.value = data.bookmarked
      emit('toggled', data.bookmarked)

      if (data.bookmarked) {
        window.$message?.success('Konuya yer imi eklendi')
      } else {
        window.$message?.info('Yer imi kaldirildi')
      }
    }
  } catch (err) {
    window.$message?.error('Islem basarisiz')
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(checkBookmark)
</script>
