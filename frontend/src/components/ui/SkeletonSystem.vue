<template>
  <div class="skeleton-wrapper" :class="[variant, { animated }]">
    <!-- Preset: Card -->
    <template v-if="type === 'card'">
      <div class="skeleton-card">
        <div class="skeleton skeleton-image"></div>
        <div class="skeleton-card-content">
          <div class="skeleton skeleton-title"></div>
          <div class="skeleton skeleton-text"></div>
          <div class="skeleton skeleton-text short"></div>
        </div>
      </div>
    </template>

    <!-- Preset: List Item -->
    <template v-else-if="type === 'list-item'">
      <div class="skeleton-list-item">
        <div class="skeleton skeleton-avatar"></div>
        <div class="skeleton-list-content">
          <div class="skeleton skeleton-text"></div>
          <div class="skeleton skeleton-text short"></div>
        </div>
      </div>
    </template>

    <!-- Preset: Table Row -->
    <template v-else-if="type === 'table-row'">
      <div class="skeleton-table-row">
        <div class="skeleton skeleton-cell"></div>
        <div class="skeleton skeleton-cell wide"></div>
        <div class="skeleton skeleton-cell"></div>
        <div class="skeleton skeleton-cell narrow"></div>
      </div>
    </template>

    <!-- Preset: Post -->
    <template v-else-if="type === 'post'">
      <div class="skeleton-post">
        <div class="skeleton-post-header">
          <div class="skeleton skeleton-avatar"></div>
          <div class="skeleton-post-meta">
            <div class="skeleton skeleton-text short"></div>
            <div class="skeleton skeleton-text shorter"></div>
          </div>
        </div>
        <div class="skeleton-post-body">
          <div class="skeleton skeleton-text"></div>
          <div class="skeleton skeleton-text"></div>
          <div class="skeleton skeleton-text short"></div>
        </div>
        <div class="skeleton-post-footer">
          <div class="skeleton skeleton-btn"></div>
          <div class="skeleton skeleton-btn"></div>
          <div class="skeleton skeleton-btn"></div>
        </div>
      </div>
    </template>

    <!-- Preset: Stats -->
    <template v-else-if="type === 'stats'">
      <div class="skeleton-stats">
        <div class="skeleton-stat" v-for="n in count" :key="n">
          <div class="skeleton skeleton-stat-value"></div>
          <div class="skeleton skeleton-stat-label"></div>
        </div>
      </div>
    </template>

    <!-- Preset: Profile -->
    <template v-else-if="type === 'profile'">
      <div class="skeleton-profile">
        <div class="skeleton skeleton-avatar large"></div>
        <div class="skeleton skeleton-title"></div>
        <div class="skeleton skeleton-text short"></div>
        <div class="skeleton-profile-stats">
          <div class="skeleton skeleton-stat-item"></div>
          <div class="skeleton skeleton-stat-item"></div>
          <div class="skeleton skeleton-stat-item"></div>
        </div>
      </div>
    </template>

    <!-- Preset: Server Card -->
    <template v-else-if="type === 'server'">
      <div class="skeleton-server">
        <div class="skeleton-server-header">
          <div class="skeleton skeleton-badge"></div>
          <div class="skeleton skeleton-text short"></div>
        </div>
        <div class="skeleton skeleton-title"></div>
        <div class="skeleton skeleton-progress"></div>
        <div class="skeleton-server-footer">
          <div class="skeleton skeleton-text shorter"></div>
          <div class="skeleton skeleton-btn"></div>
        </div>
      </div>
    </template>

    <!-- Preset: Topic -->
    <template v-else-if="type === 'topic'">
      <div class="skeleton-topic">
        <div class="skeleton skeleton-avatar"></div>
        <div class="skeleton-topic-content">
          <div class="skeleton skeleton-title"></div>
          <div class="skeleton skeleton-text"></div>
        </div>
        <div class="skeleton-topic-stats">
          <div class="skeleton skeleton-stat-mini"></div>
          <div class="skeleton skeleton-stat-mini"></div>
        </div>
      </div>
    </template>

    <!-- Custom Slot -->
    <template v-else>
      <slot>
        <div class="skeleton" :style="customStyle"></div>
      </slot>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'custom',
    validator: (v) => ['card', 'list-item', 'table-row', 'post', 'stats', 'profile', 'server', 'topic', 'custom'].includes(v)
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '20px'
  },
  borderRadius: {
    type: String,
    default: '8px'
  },
  count: {
    type: Number,
    default: 4
  },
  animated: {
    type: Boolean,
    default: true
  },
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'darker', 'lighter'].includes(v)
  }
})

const customStyle = computed(() => ({
  width: props.width,
  height: props.height,
  borderRadius: props.borderRadius
}))
</script>

<style scoped>
.skeleton-wrapper {
  --skeleton-base: #27272a;
  --skeleton-shine: #3f3f46;
}

.skeleton-wrapper.darker {
  --skeleton-base: #1f1f23;
  --skeleton-shine: #27272a;
}

.skeleton-wrapper.lighter {
  --skeleton-base: #3f3f46;
  --skeleton-shine: #52525b;
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--skeleton-base) 0%,
    var(--skeleton-shine) 50%,
    var(--skeleton-base) 100%
  );
  background-size: 200% 100%;
  border-radius: 8px;
}

.animated .skeleton {
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Card Preset */
.skeleton-card {
  display: flex;
  flex-direction: column;
  border-radius: 16px;
  overflow: hidden;
  background: var(--skeleton-base);
}

.skeleton-image {
  width: 100%;
  height: 160px;
  border-radius: 0;
}

.skeleton-card-content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-title {
  height: 20px;
  width: 70%;
}

.skeleton-text {
  height: 14px;
  width: 100%;
}

.skeleton-text.short {
  width: 60%;
}

.skeleton-text.shorter {
  width: 40%;
}

/* List Item Preset */
.skeleton-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
}

.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
}

.skeleton-avatar.large {
  width: 80px;
  height: 80px;
}

.skeleton-list-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Table Row Preset */
.skeleton-table-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}

.skeleton-cell {
  height: 16px;
  width: 80px;
}

.skeleton-cell.wide {
  flex: 1;
}

.skeleton-cell.narrow {
  width: 50px;
}

/* Post Preset */
.skeleton-post {
  padding: 20px;
  background: var(--skeleton-base);
  border-radius: 16px;
}

.skeleton-post-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.skeleton-post-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.skeleton-post-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.skeleton-post-footer {
  display: flex;
  gap: 12px;
}

.skeleton-btn {
  width: 60px;
  height: 32px;
  border-radius: 8px;
}

/* Stats Preset */
.skeleton-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 16px;
}

.skeleton-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: var(--skeleton-base);
  border-radius: 12px;
}

.skeleton-stat-value {
  width: 60px;
  height: 28px;
}

.skeleton-stat-label {
  width: 80px;
  height: 12px;
}

/* Profile Preset */
.skeleton-profile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px;
}

.skeleton-profile-stats {
  display: flex;
  gap: 24px;
  margin-top: 16px;
}

.skeleton-stat-item {
  width: 60px;
  height: 40px;
  border-radius: 8px;
}

/* Server Card Preset */
.skeleton-server {
  padding: 16px;
  background: var(--skeleton-base);
  border-radius: 16px;
}

.skeleton-server-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.skeleton-badge {
  width: 24px;
  height: 24px;
  border-radius: 6px;
}

.skeleton-progress {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  margin: 16px 0;
}

.skeleton-server-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Topic Preset */
.skeleton-topic {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}

.skeleton-topic-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-topic-stats {
  display: flex;
  gap: 16px;
}

.skeleton-stat-mini {
  width: 40px;
  height: 20px;
  border-radius: 6px;
}
</style>
