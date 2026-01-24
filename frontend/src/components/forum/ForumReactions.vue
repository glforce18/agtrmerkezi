<template>
  <div class="forum-reactions">
    <!-- Reaction Buttons -->
    <div class="reaction-buttons">
      <n-tooltip v-for="(icon, type) in reactionIcons" :key="type" trigger="hover">
        <template #trigger>
          <n-button
            :type="userReaction === type ? 'primary' : 'default'"
            :ghost="userReaction !== type"
            size="small"
            circle
            @click="handleReaction(type)"
            :loading="loading === type"
          >
            <span class="reaction-icon">{{ icon }}</span>
          </n-button>
        </template>
        {{ reactionLabels[type] }} ({{ reactions[type] || 0 }})
      </n-tooltip>
    </div>

    <!-- Reaction Summary -->
    <div v-if="totalReactions > 0" class="reaction-summary" @click="showDetails = true">
      <span class="summary-icons">
        <span v-for="(count, type) in topReactions" :key="type" class="summary-icon">
          {{ reactionIcons[type] }}
        </span>
      </span>
      <span class="summary-count">{{ totalReactions }}</span>
    </div>

    <!-- Reaction Details Modal -->
    <n-modal v-model:show="showDetails" preset="card" title="Tepkiler" style="width: 400px">
      <n-tabs type="line" animated>
        <n-tab-pane v-for="(icon, type) in reactionIcons" :key="type" :name="type">
          <template #tab>
            <span>{{ icon }} {{ reactions[type] || 0 }}</span>
          </template>
          <div class="reaction-users">
            <n-spin :show="loadingUsers">
              <div v-if="reactionUsers[type]?.length" class="user-list">
                <div v-for="user in reactionUsers[type]" :key="user.id" class="user-item">
                  <n-avatar :src="user.avatar" size="small" round />
                  <span class="username">{{ user.username }}</span>
                </div>
              </div>
              <n-empty v-else description="Henuz tepki yok" size="small" />
            </n-spin>
          </div>
        </n-tab-pane>
      </n-tabs>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { NButton, NTooltip, NModal, NTabs, NTabPane, NAvatar, NSpin, NEmpty } from 'naive-ui'
import { reactionApi } from '@/services/forumAdvanced.js'

const props = defineProps({
  contentType: {
    type: String,
    required: true,
    validator: (v) => ['topic', 'reply'].includes(v)
  },
  contentId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['reaction-changed'])

// State
const reactions = ref({})
const userReaction = ref(null)
const totalReactions = ref(0)
const loading = ref(null)
const showDetails = ref(false)
const loadingUsers = ref(false)
const reactionUsers = ref({})

// Constants
const reactionIcons = {
  like: '\uD83D\uDC4D',
  love: '\u2764\uFE0F',
  laugh: '\uD83D\uDE04',
  thinking: '\uD83E\uDD14',
  solution: '\u2705',
  played: '\uD83C\uDFAE'
}

const reactionLabels = {
  like: 'Begendim',
  love: 'Harika',
  laugh: 'Komik',
  thinking: 'Dusundurucu',
  solution: 'Cozum',
  played: 'Oynadim'
}

// Computed
const topReactions = computed(() => {
  const sorted = Object.entries(reactions.value)
    .filter(([, count]) => count > 0)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
  return Object.fromEntries(sorted)
})

// Methods
const fetchReactions = async () => {
  try {
    const { data } = await reactionApi.getReactions(props.contentType, props.contentId)
    if (data.success) {
      reactions.value = data.reactions
      userReaction.value = data.user_reaction
      totalReactions.value = data.total
    }
  } catch (err) {
    // Silent fail
  }
}

const handleReaction = async (type) => {
  loading.value = type
  try {
    const { data } = await reactionApi.addReaction(props.contentType, props.contentId, type)
    if (data.success) {
      // Update local state
      if (data.action === 'removed') {
        reactions.value[type] = Math.max(0, (reactions.value[type] || 1) - 1)
        userReaction.value = null
        totalReactions.value = Math.max(0, totalReactions.value - 1)
      } else if (data.action === 'updated') {
        // Decrease old, increase new
        if (userReaction.value) {
          reactions.value[userReaction.value] = Math.max(0, (reactions.value[userReaction.value] || 1) - 1)
        }
        reactions.value[type] = (reactions.value[type] || 0) + 1
        userReaction.value = type
      } else {
        reactions.value[type] = (reactions.value[type] || 0) + 1
        userReaction.value = type
        totalReactions.value++
      }
      emit('reaction-changed', { type, action: data.action })
    }
  } catch (err) {
    window.$message?.error('Tepki eklenemedi')
  } finally {
    loading.value = null
  }
}

const loadReactionUsers = async (type) => {
  if (reactionUsers.value[type]) return

  loadingUsers.value = true
  try {
    const { data } = await reactionApi.getReactionUsers(props.contentType, props.contentId, type)
    if (data.success) {
      reactionUsers.value[type] = data.users
    }
  } catch (err) {
    // Silent fail
  } finally {
    loadingUsers.value = false
  }
}

// Watch for modal tab changes
watch(showDetails, (val) => {
  if (val && Object.keys(topReactions.value).length > 0) {
    loadReactionUsers(Object.keys(topReactions.value)[0])
  }
})

// Lifecycle
onMounted(fetchReactions)
</script>

<style scoped>
.forum-reactions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.reaction-buttons {
  display: flex;
  gap: 4px;
}

.reaction-icon {
  font-size: 14px;
}

.reaction-summary {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 12px;
  background: var(--n-color-hover);
  transition: background 0.2s;
}

.reaction-summary:hover {
  background: var(--n-color-pressed);
}

.summary-icons {
  display: flex;
}

.summary-icon {
  margin-left: -4px;
  font-size: 12px;
}

.summary-icon:first-child {
  margin-left: 0;
}

.summary-count {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.reaction-users {
  min-height: 100px;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px;
}

.username {
  font-size: 14px;
}
</style>
