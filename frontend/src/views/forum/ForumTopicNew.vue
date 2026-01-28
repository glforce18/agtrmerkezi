<template>
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-text-primary mb-2">Yeni Konu Aç</h1>
      <p class="text-text-secondary">Toplulukla paylaşmak istediğiniz konuyu oluşturun</p>
    </div>

    <div class="card p-6">
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Category Selection -->
        <div>
          <label class="block text-text-primary font-medium mb-2">Kategori *</label>
          <select
            v-model="form.category_id"
            class="input"
            required
          >
            <option value="">Kategori seçin...</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
        </div>

        <!-- Title -->
        <div>
          <label class="block text-text-primary font-medium mb-2">Başlık *</label>
          <input
            v-model="form.title"
            type="text"
            class="input"
            placeholder="Konu başlığı"
            required
            minlength="5"
            maxlength="200"
          />
          <p class="text-text-muted text-xs mt-1">{{ form.title.length }}/200 karakter</p>
        </div>

        <!-- Content -->
        <div>
          <label class="block text-text-primary font-medium mb-2">İçerik *</label>
          <textarea
            v-model="form.content"
            class="input min-h-[300px] font-mono text-sm"
            placeholder="Konu içeriğinizi buraya yazın..."
            required
            minlength="10"
          ></textarea>
          <p class="text-text-muted text-xs mt-1">{{ form.content.length }} karakter</p>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="alert alert-error">
          {{ error }}
        </div>

        <!-- Buttons -->
        <div class="flex gap-3 justify-end">
          <button
            type="button"
            @click="$router.back()"
            class="btn btn-secondary"
            :disabled="loading"
          >
            İptal
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loading || !isFormValid"
          >
            <span v-if="loading">Gönderiliyor...</span>
            <span v-else>Konuyu Aç</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import forumAPI from '@/api/forum'

const router = useRouter()

const loading = ref(false)
const error = ref('')
const categories = ref([])

const form = ref({
  category_id: '',
  title: '',
  content: ''
})

const isFormValid = computed(() => {
  return form.value.category_id &&
         form.value.title.length >= 5 &&
         form.value.content.length >= 10
})

onMounted(async () => {
  try {
    const response = await forumAPI.getCategories()
    categories.value = Array.isArray(response.data) ? response.data : []
  } catch (err) {
    console.error('Failed to fetch categories:', err)
    error.value = 'Kategoriler yüklenemedi'
  }
})

const handleSubmit = async () => {
  error.value = ''
  loading.value = true

  try {
    const response = await forumAPI.createTopic({
      title: form.value.title,
      content: form.value.content,
      category_id: parseInt(form.value.category_id)
    })

    // Redirect to the new topic
    const topicId = response.data.id || response.data.slug
    router.push(`/forum/topic/${topicId}`)
  } catch (err) {
    console.error('Failed to create topic:', err)
    error.value = err.response?.data?.detail || 'Konu oluşturulamadı'
  } finally {
    loading.value = false
  }
}
</script>
