<template>
  <div class="skeleton-card" :class="variant">
    <!-- Server Card Skeleton -->
    <template v-if="variant === 'server'">
      <div class="skeleton-header">
        <Skeleton variant="circle" :width="48" :height="48" />
        <div class="skeleton-header-text">
          <Skeleton variant="text" width="60%" />
          <Skeleton variant="text" width="40%" />
        </div>
        <Skeleton variant="rect" :width="60" :height="24" />
      </div>
      <div class="skeleton-body">
        <Skeleton variant="text" width="80%" />
        <Skeleton variant="text" width="50%" />
      </div>
      <div class="skeleton-footer">
        <Skeleton variant="rect" :width="80" :height="32" />
        <Skeleton variant="rect" :width="80" :height="32" />
      </div>
    </template>

    <!-- User Card Skeleton -->
    <template v-else-if="variant === 'user'">
      <div class="skeleton-user">
        <Skeleton variant="circle" :width="64" :height="64" />
        <Skeleton variant="text" width="120px" />
        <Skeleton variant="text" width="80px" />
      </div>
    </template>

    <!-- Forum Topic Skeleton -->
    <template v-else-if="variant === 'topic'">
      <div class="skeleton-topic">
        <Skeleton variant="circle" :width="40" :height="40" />
        <div class="skeleton-topic-content">
          <Skeleton variant="text" width="70%" />
          <Skeleton variant="text" width="40%" />
        </div>
        <div class="skeleton-topic-stats">
          <Skeleton variant="text" :width="50" />
          <Skeleton variant="text" :width="50" />
        </div>
      </div>
    </template>

    <!-- Stats Card Skeleton -->
    <template v-else-if="variant === 'stats'">
      <div class="skeleton-stats">
        <Skeleton variant="circle" :width="48" :height="48" />
        <Skeleton variant="text" width="60%" :height="28" />
        <Skeleton variant="text" width="40%" />
      </div>
    </template>

    <!-- Table Row Skeleton -->
    <template v-else-if="variant === 'table-row'">
      <div class="skeleton-table-row">
        <Skeleton variant="text" width="50px" />
        <Skeleton variant="text" width="150px" />
        <Skeleton variant="text" width="100px" />
        <Skeleton variant="text" width="80px" />
        <Skeleton variant="rect" :width="100" :height="28" />
      </div>
    </template>

    <!-- Default Card Skeleton -->
    <template v-else>
      <Skeleton variant="rect" :height="120" />
      <div class="skeleton-default-content">
        <Skeleton variant="text" width="80%" />
        <Skeleton variant="text" width="60%" />
        <Skeleton variant="text" width="40%" />
      </div>
    </template>
  </div>
</template>

<script setup>
import Skeleton from './Skeleton.vue'

defineProps({
  variant: {
    type: String,
    default: 'default', // server, user, topic, stats, table-row, default
  }
})
</script>

<style scoped>
.skeleton-card {
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 12px;
  padding: 1rem;
}

/* Server Card */
.skeleton-card.server .skeleton-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.skeleton-header-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.skeleton-card.server .skeleton-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.skeleton-card.server .skeleton-footer {
  display: flex;
  gap: 0.5rem;
}

/* User Card */
.skeleton-user {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
}

/* Forum Topic */
.skeleton-topic {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.skeleton-topic-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.skeleton-topic-stats {
  display: flex;
  gap: 1rem;
}

/* Stats Card */
.skeleton-stats {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem;
  text-align: center;
}

/* Table Row */
.skeleton-table-row {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border-color, #2a2a4a);
}

/* Default */
.skeleton-default-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
}
</style>
