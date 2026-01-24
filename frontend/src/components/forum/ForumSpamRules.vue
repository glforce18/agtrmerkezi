<template>
  <div class="spam-rules-manager">
    <n-card title="Spam Filtreleme Kurallari">
      <template #header-extra>
        <n-button type="primary" @click="showAddModal = true">
          <template #icon><n-icon><Add /></n-icon></template>
          Kural Ekle
        </n-button>
      </template>

      <n-spin :show="loading">
        <n-data-table
          :columns="columns"
          :data="rules"
          :pagination="false"
          :bordered="false"
        />
      </n-spin>
    </n-card>

    <!-- Add/Edit Modal -->
    <n-modal v-model:show="showAddModal" preset="card" title="Spam Kurali Ekle" style="width: 500px">
      <n-form ref="formRef" :model="newRule" :rules="formRules">
        <n-form-item label="Kural Tipi" path="rule_type">
          <n-select v-model:value="newRule.rule_type" :options="ruleTypeOptions" />
        </n-form-item>

        <n-form-item label="Desen (Pattern)" path="pattern">
          <n-input
            v-model:value="newRule.pattern"
            :placeholder="getPatternPlaceholder(newRule.rule_type)"
          />
          <template #feedback>
            <div v-if="newRule.rule_type === 'regex'" class="helper-text">
              Regex deseni girin. Ornek: badword\d+
            </div>
            <div v-else-if="newRule.rule_type === 'keyword'" class="helper-text">
              Engellenecek kelimeyi girin
            </div>
            <div v-else class="helper-text">
              URL deseni girin. Ornek: spam-site.com
            </div>
          </template>
        </n-form-item>

        <n-form-item label="Islem" path="action">
          <n-radio-group v-model:value="newRule.action">
            <n-space>
              <n-radio value="warn">
                <n-tag type="warning" size="small">Uyar</n-tag>
              </n-radio>
              <n-radio value="review">
                <n-tag type="info" size="small">Incelemeye Al</n-tag>
              </n-radio>
              <n-radio value="block">
                <n-tag type="error" size="small">Engelle</n-tag>
              </n-radio>
            </n-space>
          </n-radio-group>
        </n-form-item>

        <n-form-item label="Onem Derecesi" path="severity">
          <n-slider
            v-model:value="newRule.severity"
            :min="1"
            :max="10"
            :marks="severityMarks"
            :step="1"
          />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showAddModal = false">Iptal</n-button>
          <n-button type="primary" :loading="saving" @click="handleSave">
            Kaydet
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, h, onMounted } from 'vue'
import {
  NCard, NButton, NIcon, NDataTable, NModal, NForm, NFormItem,
  NInput, NSelect, NRadioGroup, NRadio, NSpace, NSlider, NTag, NSpin,
  NPopconfirm
} from 'naive-ui'
import { PlusIcon, Trash2Icon } from 'lucide-vue-next'
import { spamApi } from '@/services/forumAdvanced.js'

const Add = PlusIcon
const Delete = Trash2Icon

// State
const rules = ref([])
const loading = ref(false)
const showAddModal = ref(false)
const saving = ref(false)
const formRef = ref(null)

const newRule = ref({
  rule_type: 'keyword',
  pattern: '',
  action: 'review',
  severity: 3
})

// Options
const ruleTypeOptions = [
  { label: 'Kelime (Keyword)', value: 'keyword' },
  { label: 'Regex', value: 'regex' },
  { label: 'Link Deseni', value: 'link_pattern' }
]

const severityMarks = {
  1: 'Dusuk',
  5: 'Orta',
  10: 'Yuksek'
}

// Form Rules
const formRules = {
  rule_type: { required: true, message: 'Kural tipi secin' },
  pattern: { required: true, message: 'Desen girin', trigger: 'blur' },
  action: { required: true, message: 'Islem secin' }
}

// Table Columns
const columns = [
  {
    title: 'Tip',
    key: 'rule_type',
    width: 120,
    render: (row) => {
      const labels = {
        keyword: 'Kelime',
        regex: 'Regex',
        link_pattern: 'Link'
      }
      return labels[row.rule_type] || row.rule_type
    }
  },
  {
    title: 'Desen',
    key: 'pattern',
    ellipsis: { tooltip: true }
  },
  {
    title: 'Islem',
    key: 'action',
    width: 120,
    render: (row) => {
      const types = {
        warn: 'warning',
        review: 'info',
        block: 'error'
      }
      const labels = {
        warn: 'Uyar',
        review: 'Incele',
        block: 'Engelle'
      }
      return h(NTag, { type: types[row.action], size: 'small' }, () => labels[row.action])
    }
  },
  {
    title: 'Onem',
    key: 'severity',
    width: 80,
    render: (row) => {
      const color = row.severity >= 7 ? '#d03050' : row.severity >= 4 ? '#f0a020' : '#18a058'
      return h('span', { style: { color, fontWeight: 'bold' } }, row.severity)
    }
  },
  {
    title: 'Islemler',
    key: 'actions',
    width: 80,
    render: (row) => {
      return h(
        NPopconfirm,
        {
          onPositiveClick: () => handleDelete(row.id)
        },
        {
          trigger: () => h(
            NButton,
            { text: true, type: 'error', size: 'small' },
            { icon: () => h(NIcon, null, { default: () => h(Delete) }) }
          ),
          default: () => 'Bu kurali silmek istediginize emin misiniz?'
        }
      )
    }
  }
]

// Methods
const fetchRules = async () => {
  loading.value = true
  try {
    const { data } = await spamApi.getRules()
    if (data.success) {
      rules.value = data.rules
    }
  } catch (err) {
    window.$message?.error('Kurallar yuklenemedi')
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  saving.value = true
  try {
    const { data } = await spamApi.createRule(newRule.value)
    if (data.success) {
      rules.value.push(data.rule)
      showAddModal.value = false
      resetForm()
      window.$message?.success('Kural eklendi')
    }
  } catch (err) {
    window.$message?.error(err.response?.data?.detail || 'Kural eklenemedi')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (ruleId) => {
  try {
    const { data } = await spamApi.deleteRule(ruleId)
    if (data.success) {
      rules.value = rules.value.filter(r => r.id !== ruleId)
      window.$message?.success('Kural silindi')
    }
  } catch (err) {
    window.$message?.error('Kural silinemedi')
  }
}

const resetForm = () => {
  newRule.value = {
    rule_type: 'keyword',
    pattern: '',
    action: 'review',
    severity: 3
  }
}

const getPatternPlaceholder = (type) => {
  switch (type) {
    case 'regex': return 'spam\\d+|badword.*'
    case 'link_pattern': return 'spam-domain.com'
    default: return 'kotu kelime'
  }
}

// Lifecycle
onMounted(fetchRules)
</script>

<style scoped>
.spam-rules-manager {
  padding: 16px;
}

.helper-text {
  font-size: 12px;
  color: var(--n-text-color-3);
  margin-top: 4px;
}
</style>
