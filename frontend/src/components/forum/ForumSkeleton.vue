<template>
  <div :class="['forum-skeleton-wrapper', `forum-skeleton-wrapper--${type}`]" role="status" aria-label="Yukleniyor">
    <span class="forum-sr-only">Icerik yukleniyor...</span>

    <!-- Topic Card Skeleton -->
    <div v-if="type === 'topic-card'" class="forum-skeleton-topic">
      <div class="forum-skeleton-topic__avatar forum-skeleton forum-skeleton--avatar" />
      <div class="forum-skeleton-topic__content">
        <div class="forum-skeleton forum-skeleton--title" style="width: 75%;" />
        <div class="forum-skeleton forum-skeleton--text" style="width: 50%;" />
        <div class="forum-skeleton-topic__stats">
          <div class="forum-skeleton" style="width: 60px; height: 24px;" />
          <div class="forum-skeleton" style="width: 60px; height: 24px;" />
          <div class="forum-skeleton" style="width: 60px; height: 24px;" />
        </div>
      </div>
    </div>

    <!-- Category Card Skeleton -->
    <div v-else-if="type === 'category-card'" class="forum-skeleton-category">
      <div class="forum-skeleton" style="height: 3px; width: 100%;" />
      <div class="forum-skeleton-category__content">
        <div class="forum-skeleton" style="width: 56px; height: 56px; border-radius: 12px;" />
        <div class="forum-skeleton-category__info">
          <div class="forum-skeleton forum-skeleton--title" style="width: 60%;" />
          <div class="forum-skeleton forum-skeleton--text" style="width: 80%;" />
          <div class="forum-skeleton-category__stats">
            <div class="forum-skeleton" style="width: 80px; height: 28px; border-radius: 14px;" />
            <div class="forum-skeleton" style="width: 80px; height: 28px; border-radius: 14px;" />
          </div>
        </div>
      </div>
    </div>

    <!-- Post Card Skeleton -->
    <div v-else-if="type === 'post-card'" class="forum-skeleton-post">
      <div class="forum-skeleton-post__sidebar">
        <div class="forum-skeleton forum-skeleton--avatar" style="width: 80px; height: 80px;" />
        <div class="forum-skeleton forum-skeleton--text" style="width: 80%;" />
        <div class="forum-skeleton forum-skeleton--text" style="width: 50%;" />
        <div class="forum-skeleton-post__stats-grid">
          <div class="forum-skeleton" style="width: 100%; height: 40px;" />
          <div class="forum-skeleton" style="width: 100%; height: 40px;" />
        </div>
      </div>
      <div class="forum-skeleton-post__content">
        <div class="forum-skeleton forum-skeleton--text" style="width: 30%;" />
        <div class="forum-skeleton" style="width: 100%; height: 100px; margin: 16px 0;" />
        <div class="forum-skeleton forum-skeleton--text" style="width: 90%;" />
        <div class="forum-skeleton forum-skeleton--text" style="width: 70%;" />
        <div class="forum-skeleton-post__actions">
          <div class="forum-skeleton" style="width: 80px; height: 32px;" />
          <div class="forum-skeleton" style="width: 80px; height: 32px;" />
          <div class="forum-skeleton" style="width: 80px; height: 32px;" />
        </div>
      </div>
    </div>

    <!-- Sidebar Skeleton -->
    <div v-else-if="type === 'sidebar'" class="forum-skeleton-sidebar">
      <div class="forum-skeleton forum-skeleton--title" style="width: 50%; margin-bottom: 16px;" />
      <div v-for="n in count" :key="n" class="forum-skeleton-sidebar__item">
        <div class="forum-skeleton" style="width: 32px; height: 32px; border-radius: 8px;" />
        <div class="forum-skeleton forum-skeleton--text" style="flex: 1;" />
        <div class="forum-skeleton" style="width: 30px; height: 20px; border-radius: 10px;" />
      </div>
    </div>

    <!-- Stats Skeleton -->
    <div v-else-if="type === 'stats'" class="forum-skeleton-stats">
      <div v-for="n in count" :key="n" class="forum-skeleton" style="height: 60px; border-radius: 12px;" />
    </div>

    <!-- List Skeleton (generic) -->
    <div v-else-if="type === 'list'" class="forum-skeleton-list">
      <div v-for="n in count" :key="n" class="forum-skeleton forum-skeleton--card" />
    </div>

    <!-- Text Lines Skeleton -->
    <div v-else class="forum-skeleton-text-lines">
      <div
        v-for="n in count"
        :key="n"
        class="forum-skeleton forum-skeleton--text"
        :style="{ width: getLineWidth(n) }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'text',
    validator: (value) => [
      'text',
      'topic-card',
      'category-card',
      'post-card',
      'sidebar',
      'stats',
      'list'
    ].includes(value)
  },
  count: {
    type: Number,
    default: 3,
    validator: (val) => val > 0 && val <= 20
  }
})

// Safe count value
const safeCount = computed(() => Math.min(Math.max(1, props.count), 20))

const getLineWidth = (index) => {
  const widths = ['100%', '90%', '75%', '85%', '60%']
  return widths[(index - 1) % widths.length]
}
</script>

<style scoped>
.forum-skeleton-wrapper {
  width: 100%;
}

/* Base skeleton with shimmer animation */
.forum-skeleton {
  background: linear-gradient(
    90deg,
    var(--forum-bg-card, #12181f) 25%,
    var(--forum-bg-elevated, #1c2633) 50%,
    var(--forum-bg-card, #12181f) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
  border-radius: 6px;
}

.forum-skeleton--avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  flex-shrink: 0;
}

.forum-skeleton--title {
  height: 20px;
  border-radius: 4px;
}

.forum-skeleton--text {
  height: 14px;
  border-radius: 4px;
}

.forum-skeleton--card {
  height: 80px;
  border-radius: var(--forum-radius, 12px);
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Screen reader only */
.forum-sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Topic Card Skeleton */
.forum-skeleton-topic {
  display: flex;
  gap: 16px;
  padding: 16px 20px;
  background: var(--forum-bg-card);
  border: 1px solid var(--forum-border);
  border-radius: var(--forum-radius);
}

.forum-skeleton-topic__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.forum-skeleton-topic__stats {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

/* Category Card Skeleton */
.forum-skeleton-category {
  background: var(--forum-bg-card);
  border: 1px solid var(--forum-border);
  border-radius: var(--forum-radius);
  overflow: hidden;
}

.forum-skeleton-category__content {
  display: flex;
  gap: 16px;
  padding: 20px;
}

.forum-skeleton-category__info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.forum-skeleton-category__stats {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

/* Post Card Skeleton */
.forum-skeleton-post {
  display: flex;
  background: var(--forum-bg-card);
  border: 1px solid var(--forum-border);
  border-radius: var(--forum-radius);
  overflow: hidden;
}

.forum-skeleton-post__sidebar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: var(--forum-bg-hover);
  border-right: 1px solid var(--forum-border);
  min-width: 180px;
}

.forum-skeleton-post__stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  width: 100%;
  margin-top: 8px;
}

.forum-skeleton-post__content {
  flex: 1;
  padding: 20px;
}

.forum-skeleton-post__actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--forum-border);
}

/* Sidebar Skeleton */
.forum-skeleton-sidebar {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.forum-skeleton-sidebar__item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
}

/* Stats Skeleton */
.forum-skeleton-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

/* List Skeleton */
.forum-skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Text Lines Skeleton */
.forum-skeleton-text-lines {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

@media (max-width: 768px) {
  .forum-skeleton-post {
    flex-direction: column;
  }

  .forum-skeleton-post__sidebar {
    flex-direction: row;
    min-width: unset;
    border-right: none;
    border-bottom: 1px solid var(--forum-border);
  }

  .forum-skeleton-post__stats-grid {
    display: none;
  }
}
</style>
