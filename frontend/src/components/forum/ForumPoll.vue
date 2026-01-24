<template>
  <div class="forum-poll" v-if="poll">
    <n-card :title="poll.question" size="small">
      <template #header-extra>
        <n-tag v-if="poll.is_ended" type="warning" size="small">Sona Erdi</n-tag>
        <n-tag v-else-if="poll.ends_at" type="info" size="small">
          {{ formatTimeRemaining(poll.ends_at) }}
        </n-tag>
      </template>

      <!-- Options -->
      <div class="poll-options">
        <div
          v-for="option in poll.options"
          :key="option.id"
          class="poll-option"
          :class="{
            'voted': option.voted,
            'clickable': !poll.user_voted && !poll.is_ended && !voting
          }"
          @click="handleVote(option.id)"
        >
          <!-- Checkbox/Radio -->
          <div class="option-select" v-if="!poll.user_voted && !poll.is_ended">
            <n-checkbox
              v-if="poll.allow_multiple"
              :checked="selectedOptions.includes(option.id)"
              @update:checked="toggleOption(option.id)"
            />
            <n-radio
              v-else
              :checked="selectedOptions.includes(option.id)"
              @update:checked="selectOption(option.id)"
            />
          </div>

          <!-- Option Content -->
          <div class="option-content">
            <div class="option-text">
              {{ option.text }}
              <n-icon v-if="option.voted" color="#18a058" size="16">
                <CheckCircle />
              </n-icon>
            </div>

            <!-- Progress Bar (after voting) -->
            <div v-if="poll.user_voted || poll.is_ended" class="option-progress">
              <n-progress
                type="line"
                :percentage="option.percentage"
                :height="20"
                :border-radius="4"
                :fill-border-radius="4"
                :indicator-placement="'inside'"
                :processing="option.voted"
              />
              <span class="vote-count">{{ option.vote_count }} oy</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Vote Button -->
      <template #action v-if="!poll.user_voted && !poll.is_ended">
        <n-button
          type="primary"
          :disabled="selectedOptions.length === 0"
          :loading="voting"
          @click="submitVote"
        >
          Oy Ver
        </n-button>
        <span class="vote-info">
          <span v-if="poll.allow_multiple">Birden fazla secenek secilebilir</span>
          <span v-if="poll.is_anonymous">Anonim oylama</span>
        </span>
      </template>

      <!-- Stats -->
      <template #footer>
        <div class="poll-stats">
          <span>Toplam {{ poll.total_votes }} oy</span>
        </div>
      </template>
    </n-card>
  </div>

  <!-- Create Poll Button -->
  <div class="create-poll" v-else-if="canCreate && !showCreateForm">
    <n-button dashed @click="showCreateForm = true">
      <template #icon><n-icon><PollOutlined /></n-icon></template>
      Anket Ekle
    </n-button>
  </div>

  <!-- Create Poll Form -->
  <n-modal v-model:show="showCreateForm" preset="card" title="Anket Olustur" style="width: 500px">
    <n-form ref="formRef" :model="newPoll" :rules="rules">
      <n-form-item label="Soru" path="question">
        <n-input
          v-model:value="newPoll.question"
          placeholder="Anket sorusunu yazin..."
          maxlength="500"
          show-count
        />
      </n-form-item>

      <n-form-item label="Secenekler" path="options">
        <div class="options-input">
          <div v-for="(opt, index) in newPoll.options" :key="index" class="option-input-row">
            <n-input
              v-model:value="newPoll.options[index]"
              :placeholder="`Secenek ${index + 1}`"
              maxlength="200"
            />
            <n-button
              v-if="newPoll.options.length > 2"
              text
              type="error"
              @click="removeOption(index)"
            >
              <n-icon><CloseOutlined /></n-icon>
            </n-button>
          </div>
          <n-button
            v-if="newPoll.options.length < 10"
            dashed
            size="small"
            @click="addOption"
          >
            Secenek Ekle
          </n-button>
        </div>
      </n-form-item>

      <n-form-item label="Ayarlar">
        <n-space vertical>
          <n-checkbox v-model:checked="newPoll.allow_multiple">
            Birden fazla secenek secilebilsin
          </n-checkbox>
          <n-checkbox v-model:checked="newPoll.is_anonymous">
            Anonim oylama
          </n-checkbox>
          <n-checkbox v-model:checked="hasEndDate">
            Bitis tarihi belirle
          </n-checkbox>
          <n-date-picker
            v-if="hasEndDate"
            v-model:value="newPoll.ends_at"
            type="datetime"
            clearable
          />
        </n-space>
      </n-form-item>
    </n-form>

    <template #footer>
      <n-space justify="end">
        <n-button @click="showCreateForm = false">Iptal</n-button>
        <n-button type="primary" :loading="creating" @click="createPoll">
          Olustur
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  NCard, NTag, NCheckbox, NRadio, NProgress, NButton, NIcon,
  NModal, NForm, NFormItem, NInput, NSpace, NDatePicker
} from 'naive-ui'
import { CheckCircleIcon, BarChart3Icon, XIcon } from 'lucide-vue-next'
import { pollApi } from '@/services/forumAdvanced.js'

const CheckCircle = CheckCircleIcon
const PollOutlined = BarChart3Icon
const CloseOutlined = XIcon

const props = defineProps({
  topicId: {
    type: Number,
    required: true
  },
  canCreate: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['poll-created', 'poll-voted'])

// State
const poll = ref(null)
const selectedOptions = ref([])
const voting = ref(false)
const showCreateForm = ref(false)
const creating = ref(false)
const hasEndDate = ref(false)
const formRef = ref(null)

const newPoll = ref({
  question: '',
  options: ['', ''],
  allow_multiple: false,
  is_anonymous: false,
  ends_at: null
})

// Validation Rules
const rules = {
  question: {
    required: true,
    message: 'Soru gerekli',
    trigger: 'blur'
  },
  options: {
    validator: () => {
      const validOptions = newPoll.value.options.filter(o => o.trim())
      return validOptions.length >= 2
    },
    message: 'En az 2 secenek gerekli',
    trigger: 'change'
  }
}

// Methods
const fetchPoll = async () => {
  try {
    const { data } = await pollApi.getTopicPoll(props.topicId)
    if (data.success && data.poll) {
      poll.value = data.poll
    }
  } catch (err) {
    // No poll exists
  }
}

const handleVote = (optionId) => {
  if (poll.value.user_voted || poll.value.is_ended || voting.value) return

  if (poll.value.allow_multiple) {
    toggleOption(optionId)
  } else {
    selectOption(optionId)
  }
}

const toggleOption = (optionId) => {
  const index = selectedOptions.value.indexOf(optionId)
  if (index === -1) {
    selectedOptions.value.push(optionId)
  } else {
    selectedOptions.value.splice(index, 1)
  }
}

const selectOption = (optionId) => {
  selectedOptions.value = [optionId]
}

const submitVote = async () => {
  if (selectedOptions.value.length === 0) return

  voting.value = true
  try {
    const { data } = await pollApi.vote(poll.value.id, selectedOptions.value)
    if (data.success) {
      poll.value = data.poll
      emit('poll-voted', data.poll)
      window.$message?.success('Oyunuz kaydedildi')
    }
  } catch (err) {
    window.$message?.error(err.response?.data?.detail || 'Oy verilemedi')
  } finally {
    voting.value = false
  }
}

const addOption = () => {
  if (newPoll.value.options.length < 10) {
    newPoll.value.options.push('')
  }
}

const removeOption = (index) => {
  if (newPoll.value.options.length > 2) {
    newPoll.value.options.splice(index, 1)
  }
}

const createPoll = async () => {
  const valid = await formRef.value?.validate()
  if (!valid) return

  creating.value = true
  try {
    const payload = {
      topic_id: props.topicId,
      question: newPoll.value.question,
      options: newPoll.value.options.filter(o => o.trim()),
      allow_multiple: newPoll.value.allow_multiple,
      is_anonymous: newPoll.value.is_anonymous,
      ends_at: hasEndDate.value && newPoll.value.ends_at
        ? new Date(newPoll.value.ends_at).toISOString()
        : null
    }

    const { data } = await pollApi.createPoll(payload)
    if (data.success) {
      poll.value = data.poll
      showCreateForm.value = false
      emit('poll-created', data.poll)
      window.$message?.success('Anket olusturuldu')
    }
  } catch (err) {
    window.$message?.error(err.response?.data?.detail || 'Anket olusturulamadi')
  } finally {
    creating.value = false
  }
}

const formatTimeRemaining = (endDate) => {
  const end = new Date(endDate)
  const now = new Date()
  const diff = end - now

  if (diff <= 0) return 'Sona Erdi'

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))

  if (days > 0) return `${days} gun kaldi`
  if (hours > 0) return `${hours} saat kaldi`
  return 'Az kaldi'
}

// Lifecycle
onMounted(fetchPoll)
</script>

<style scoped>
.forum-poll {
  margin: 16px 0;
}

.poll-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.poll-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  transition: all 0.2s;
}

.poll-option.clickable {
  cursor: pointer;
}

.poll-option.clickable:hover {
  border-color: var(--n-primary-color);
}

.poll-option.voted {
  border-color: var(--n-primary-color);
  background: var(--n-primary-color-suppl);
}

.option-select {
  padding-top: 2px;
}

.option-content {
  flex: 1;
}

.option-text {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  margin-bottom: 4px;
}

.option-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.vote-count {
  font-size: 12px;
  color: var(--n-text-color-3);
  white-space: nowrap;
}

.vote-info {
  margin-left: 16px;
  font-size: 12px;
  color: var(--n-text-color-3);
}

.poll-stats {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.create-poll {
  margin: 16px 0;
}

.options-input {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-input-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.option-input-row .n-input {
  flex: 1;
}
</style>
