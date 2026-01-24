<template>
  <div class="template-selector">
    <!-- Template Select Button -->
    <n-popover trigger="click" placement="bottom-start" :show="showPopover" @update:show="showPopover = $event">
      <template #trigger>
        <n-button :disabled="disabled">
          <template #icon><n-icon><ArticleOutlined /></n-icon></template>
          Sablon Kullan
        </n-button>
      </template>

      <div class="template-list">
        <div v-if="loading" class="loading">
          <n-spin size="small" />
        </div>

        <n-empty v-else-if="templates.length === 0" description="Sablon bulunamadi" size="small" />

        <div v-else>
          <div class="template-header">
            <span>Hazir Sablonlar</span>
          </div>

          <div
            v-for="template in templates"
            :key="template.id"
            class="template-item"
            @click="selectTemplate(template)"
          >
            <div class="template-name">{{ template.name }}</div>
            <div class="template-desc" v-if="template.description">
              {{ template.description }}
            </div>
            <div class="template-tags" v-if="template.required_fields?.length">
              <n-tag v-for="field in template.required_fields" :key="field" size="tiny">
                {{ field }}
              </n-tag>
            </div>
          </div>
        </div>
      </div>
    </n-popover>

    <!-- Template Preview Modal -->
    <n-modal v-model:show="showPreview" preset="card" title="Sablon Onizleme" style="width: 600px">
      <template v-if="selectedTemplate">
        <n-form-item label="Baslik">
          <n-input :value="selectedTemplate.title_template" disabled />
        </n-form-item>

        <n-form-item label="Icerik">
          <div class="preview-content" v-html="formatPreview(selectedTemplate.content_template)"></div>
        </n-form-item>

        <n-alert v-if="selectedTemplate.required_fields?.length" type="info" title="Gerekli Alanlar">
          Bu sablonu kullanirken su alanlari doldurmalisiniz:
          <ul>
            <li v-for="field in selectedTemplate.required_fields" :key="field">{{ field }}</li>
          </ul>
        </n-alert>
      </template>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showPreview = false">Iptal</n-button>
          <n-button type="primary" @click="applyTemplate">
            Sablonu Uygula
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { NButton, NIcon, NPopover, NEmpty, NSpin, NTag, NModal, NFormItem, NInput, NAlert, NSpace } from 'naive-ui'
import { FileTextIcon } from 'lucide-vue-next'
import { templateApi } from '@/services/forumAdvanced.js'

const ArticleOutlined = FileTextIcon

const props = defineProps({
  categoryId: {
    type: Number,
    default: null
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['template-selected'])

// State
const templates = ref([])
const loading = ref(false)
const showPopover = ref(false)
const showPreview = ref(false)
const selectedTemplate = ref(null)

// Methods
const fetchTemplates = async () => {
  loading.value = true
  try {
    const { data } = await templateApi.getTemplates(props.categoryId)
    if (data.success) {
      templates.value = data.templates
    }
  } catch (err) {
    // Silent fail
  } finally {
    loading.value = false
  }
}

const selectTemplate = (template) => {
  selectedTemplate.value = template
  showPopover.value = false
  showPreview.value = true
}

const applyTemplate = () => {
  if (selectedTemplate.value) {
    emit('template-selected', {
      title: selectedTemplate.value.title_template,
      content: selectedTemplate.value.content_template,
      requiredFields: selectedTemplate.value.required_fields || []
    })
    showPreview.value = false
    window.$message?.success('Sablon uygulandi')
  }
}

const formatPreview = (content) => {
  if (!content) return ''
  // Simple markdown-like formatting
  return content
    .replace(/\n/g, '<br>')
    .replace(/\[([^\]]+)\]/g, '<span class="placeholder">[$1]</span>')
}

// Watch category changes
watch(() => props.categoryId, fetchTemplates)

// Lifecycle
onMounted(fetchTemplates)
</script>

<style scoped>
.template-list {
  min-width: 300px;
  max-width: 400px;
  max-height: 400px;
  overflow-y: auto;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.template-header {
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--n-text-color-3);
  border-bottom: 1px solid var(--n-border-color);
}

.template-item {
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid var(--n-border-color);
  transition: background 0.2s;
}

.template-item:hover {
  background: var(--n-color-hover);
}

.template-item:last-child {
  border-bottom: none;
}

.template-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.template-desc {
  font-size: 12px;
  color: var(--n-text-color-3);
  margin-bottom: 6px;
}

.template-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.preview-content {
  padding: 12px;
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
  line-height: 1.6;
  max-height: 300px;
  overflow-y: auto;
}

.preview-content :deep(.placeholder) {
  background: var(--n-warning-color-suppl);
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}
</style>
