<template>
  <div class="forum-advanced-search">
    <!-- Search Input -->
    <n-input-group>
      <n-input
        v-model:value="searchQuery"
        placeholder="Forum'da ara..."
        clearable
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <n-icon><SearchOutlined /></n-icon>
        </template>
      </n-input>
      <n-button type="primary" @click="handleSearch" :loading="loading">
        Ara
      </n-button>
      <n-button @click="showFilters = !showFilters">
        <template #icon>
          <n-icon><FilterListOutlined /></n-icon>
        </template>
        Filtreler
        <n-badge v-if="activeFilterCount > 0" :value="activeFilterCount" :max="9" />
      </n-button>
    </n-input-group>

    <!-- Advanced Filters -->
    <n-collapse-transition :show="showFilters">
      <n-card size="small" class="filters-card">
        <n-space vertical>
          <n-grid :cols="2" :x-gap="16" :y-gap="12">
            <!-- Category -->
            <n-gi>
              <n-form-item label="Kategori" label-placement="left">
                <n-select
                  v-model:value="filters.category_id"
                  :options="categoryOptions"
                  placeholder="Tum kategoriler"
                  clearable
                />
              </n-form-item>
            </n-gi>

            <!-- Sort -->
            <n-gi>
              <n-form-item label="Siralama" label-placement="left">
                <n-select
                  v-model:value="filters.sort"
                  :options="sortOptions"
                />
              </n-form-item>
            </n-gi>

            <!-- Date Range -->
            <n-gi>
              <n-form-item label="Tarih" label-placement="left">
                <n-date-picker
                  v-model:value="dateRange"
                  type="daterange"
                  clearable
                  :shortcuts="dateShortcuts"
                />
              </n-form-item>
            </n-gi>

            <!-- Tags -->
            <n-gi>
              <n-form-item label="Etiketler" label-placement="left">
                <n-select
                  v-model:value="filters.tags"
                  :options="tagOptions"
                  multiple
                  filterable
                  placeholder="Etiket sec..."
                  max-tag-count="responsive"
                />
              </n-form-item>
            </n-gi>

            <!-- Solved Filter -->
            <n-gi>
              <n-form-item label="Durum" label-placement="left">
                <n-radio-group v-model:value="filters.is_solved">
                  <n-radio-button :value="null">Tumu</n-radio-button>
                  <n-radio-button :value="true">Cozulmus</n-radio-button>
                  <n-radio-button :value="false">Cozulmemis</n-radio-button>
                </n-radio-group>
              </n-form-item>
            </n-gi>
          </n-grid>

          <n-space justify="end">
            <n-button @click="resetFilters">Temizle</n-button>
            <n-button type="primary" @click="handleSearch">Filtrele</n-button>
          </n-space>
        </n-space>
      </n-card>
    </n-collapse-transition>

    <!-- Search Results -->
    <div v-if="hasSearched" class="search-results">
      <div class="results-header">
        <span v-if="results.length > 0">
          {{ total }} sonuc bulundu
        </span>
        <span v-else>
          Sonuc bulunamadi
        </span>
      </div>

      <n-spin :show="loading">
        <div class="results-list">
          <div
            v-for="topic in results"
            :key="topic.id"
            class="result-item"
            @click="goToTopic(topic.id)"
          >
            <div class="result-title">
              <n-icon v-if="topic.is_solved" color="#18a058" size="16">
                <CheckCircle />
              </n-icon>
              {{ topic.title }}
            </div>
            <div class="result-meta">
              <span>{{ topic.author?.username }}</span>
              <span>{{ topic.reply_count }} yanit</span>
              <span>{{ topic.view_count }} goruntulenme</span>
              <span>{{ formatDate(topic.created_at) }}</span>
            </div>
            <div class="result-preview" v-html="highlightText(topic.content_preview)"></div>
          </div>
        </div>
      </n-spin>

      <!-- Pagination -->
      <n-pagination
        v-if="total > limit"
        v-model:page="page"
        :page-count="Math.ceil(total / limit)"
        @update:page="handleSearch"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NInput, NInputGroup, NButton, NIcon, NBadge, NCard, NSpace, NGrid, NGi,
  NFormItem, NSelect, NDatePicker, NRadioGroup, NRadioButton, NSpin,
  NPagination, NCollapseTransition
} from 'naive-ui'
import { SearchIcon, FilterIcon, CheckCircleIcon } from 'lucide-vue-next'
import { searchApi } from '@/services/forumAdvanced.js'

const SearchOutlined = SearchIcon
const FilterListOutlined = FilterIcon
const CheckCircle = CheckCircleIcon

const router = useRouter()

const props = defineProps({
  categories: {
    type: Array,
    default: () => []
  },
  tags: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['search', 'result-click'])

// State
const searchQuery = ref('')
const showFilters = ref(false)
const loading = ref(false)
const hasSearched = ref(false)
const results = ref([])
const total = ref(0)
const page = ref(1)
const limit = ref(20)

const filters = ref({
  category_id: null,
  sort: 'relevance',
  tags: [],
  is_solved: null
})

const dateRange = ref(null)

// Options
const sortOptions = [
  { label: 'Alaka', value: 'relevance' },
  { label: 'En Yeni', value: 'newest' },
  { label: 'En Eski', value: 'oldest' },
  { label: 'En Cok Yanit', value: 'most_replies' },
  { label: 'En Cok Goruntulenme', value: 'most_views' }
]

const dateShortcuts = {
  'Bugun': () => {
    const now = new Date()
    const start = new Date(now.setHours(0, 0, 0, 0))
    return [start.getTime(), Date.now()]
  },
  'Son 7 Gun': () => {
    const now = Date.now()
    return [now - 7 * 24 * 60 * 60 * 1000, now]
  },
  'Son 30 Gun': () => {
    const now = Date.now()
    return [now - 30 * 24 * 60 * 60 * 1000, now]
  },
  'Son 1 Yil': () => {
    const now = Date.now()
    return [now - 365 * 24 * 60 * 60 * 1000, now]
  }
}

// Computed
const categoryOptions = computed(() => [
  { label: 'Tum Kategoriler', value: null },
  ...props.categories.map(c => ({ label: c.name, value: c.id }))
])

const tagOptions = computed(() =>
  props.tags.map(t => ({ label: t.name, value: t.name }))
)

const activeFilterCount = computed(() => {
  let count = 0
  if (filters.value.category_id) count++
  if (filters.value.sort !== 'relevance') count++
  if (filters.value.tags.length > 0) count++
  if (filters.value.is_solved !== null) count++
  if (dateRange.value) count++
  return count
})

// Methods
const handleSearch = async () => {
  if (!searchQuery.value.trim() && activeFilterCount.value === 0) {
    window.$message?.warning('Arama terimi veya filtre girin')
    return
  }

  loading.value = true
  hasSearched.value = true

  try {
    const searchData = {
      query: searchQuery.value,
      ...filters.value,
      date_from: dateRange.value ? new Date(dateRange.value[0]).toISOString() : null,
      date_to: dateRange.value ? new Date(dateRange.value[1]).toISOString() : null
    }

    const { data } = await searchApi.advancedSearch(searchData, page.value, limit.value)

    if (data.success) {
      results.value = data.results
      total.value = data.total
      emit('search', { query: searchQuery.value, total: data.total })
    }
  } catch (err) {
    window.$message?.error('Arama yapilamadi')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    category_id: null,
    sort: 'relevance',
    tags: [],
    is_solved: null
  }
  dateRange.value = null
}

const goToTopic = (topicId) => {
  emit('result-click', topicId)
  router.push(`/forum/topic/${topicId}`)
}

const highlightText = (text) => {
  if (!searchQuery.value || !text) return text
  const regex = new RegExp(`(${searchQuery.value})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR')
}

// Watch page changes
watch(page, () => {
  handleSearch()
})
</script>

<style scoped>
.forum-advanced-search {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filters-card {
  margin-top: 12px;
}

.search-results {
  margin-top: 16px;
}

.results-header {
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--n-text-color-3);
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 100px;
}

.result-item {
  padding: 16px;
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.result-item:hover {
  border-color: var(--n-primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.result-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.result-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--n-text-color-3);
  margin-bottom: 8px;
}

.result-preview {
  font-size: 14px;
  color: var(--n-text-color-2);
  line-height: 1.5;
}

.result-preview :deep(mark) {
  background: var(--n-warning-color-suppl);
  padding: 0 2px;
  border-radius: 2px;
}
</style>
