<template>
  <div class="trending-topics-section card">
    <div class="section-header">
      <h2 class="section-title">
        <span class="title-icon">🔥</span>
        Trend Konular
      </h2>
      <span class="period-badge">Bu hafta</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div v-for="i in 5" :key="i" class="skeleton-topic"></div>
    </div>

    <!-- Topics List -->
    <div v-else-if="topics.length > 0" class="topics-list">
      <router-link
        v-for="(topic, index) in topics"
        :key="topic.id"
        :to="`/forum/topic/${topic.id}`"
        class="topic-item"
        :class="{ 'topic-hot': index < 3 }"
      >
        <div class="topic-rank" :class="getRankClass(index)">
          {{ index + 1 }}
        </div>

        <div class="topic-content">
          <div class="topic-title">{{ topic.title }}</div>
          <div class="topic-meta">
            <span class="topic-author">
              <img
                :src="topic.author?.avatar || '/static/images/default-avatar.png'"
                :alt="topic.author?.username"
                class="author-avatar"
                @error="handleAvatarError"
              />
              {{ topic.author?.username }}
            </span>
            <span class="topic-category" v-if="topic.category">
              {{ topic.category.name }}
            </span>
          </div>
        </div>

        <div class="topic-stats">
          <div class="stat-item stat-views">
            <span class="stat-icon">👁</span>
            <span class="stat-value">{{ formatNumber(topic.view_count || 0) }}</span>
          </div>
          <div class="stat-item stat-replies">
            <span class="stat-icon">💬</span>
            <span class="stat-value">{{ topic.reply_count || 0 }}</span>
          </div>
          <div class="stat-item stat-likes">
            <span class="stat-icon">❤️</span>
            <span class="stat-value">{{ topic.like_count || 0 }}</span>
          </div>
        </div>
      </router-link>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <span class="empty-icon">📭</span>
      <p class="empty-text">Henuz trend konu yok</p>
    </div>
  </div>
</template>

<script setup>
// Props
const props = defineProps({
  topics: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Methods
const getRankClass = (index) => {
  if (index === 0) return 'rank-gold'
  if (index === 1) return 'rank-silver'
  if (index === 2) return 'rank-bronze'
  return 'rank-default'
}

const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const handleAvatarError = (e) => {
  e.target.src = '/static/images/default-avatar.png'
}
</script>

<style scoped>
.trending-topics-section {
  background: var(--bg-card, rgba(255, 255, 255, 0.05));
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary, #ffffff);
}

.title-icon {
  font-size: 1.1rem;
  animation: flame 1s ease-in-out infinite;
}

@keyframes flame {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.period-badge {
  font-size: 0.7rem;
  color: var(--text-secondary, #a1a1aa);
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

/* Topics List */
.topics-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.topic-item {
  display: grid;
  grid-template-columns: 36px 1fr auto;
  gap: 14px;
  align-items: center;
  padding: 14px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.topic-item:hover {
  background: rgba(249, 115, 22, 0.1);
  transform: translateX(4px);
}

.topic-hot {
  border-left: 3px solid var(--primary, #f97316);
}

/* Rank Badge */
.topic-rank {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-weight: 700;
  font-size: 1rem;
}

.rank-gold {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: #1a1a1a;
  box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);
}

.rank-silver {
  background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(148, 163, 184, 0.3);
}

.rank-bronze {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(217, 119, 6, 0.3);
}

.rank-default {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary, #a1a1aa);
}

/* Topic Content */
.topic-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.topic-title {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-primary, #ffffff);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.2s ease;
}

.topic-item:hover .topic-title {
  color: var(--primary, #f97316);
}

.topic-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary, #a1a1aa);
}

.topic-author {
  display: flex;
  align-items: center;
  gap: 6px;
}

.author-avatar {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  object-fit: cover;
}

.topic-category {
  padding: 2px 8px;
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
  border-radius: 6px;
  font-size: 0.75rem;
}

/* Topic Stats */
.topic-stats {
  display: flex;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
}

.stat-icon {
  font-size: 0.85rem;
}

.stat-value {
  font-weight: 600;
}

.stat-views .stat-value {
  color: #3b82f6;
}

.stat-replies .stat-value {
  color: #22c55e;
}

.stat-likes .stat-value {
  color: #ef4444;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-topic {
  height: 70px;
  background: linear-gradient(90deg,
    rgba(255, 255, 255, 0.05) 25%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 12px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-text {
  font-size: 1rem;
  color: var(--text-secondary, #a1a1aa);
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .topic-item {
    grid-template-columns: 32px 1fr;
  }

  .topic-stats {
    display: none;
  }
}
</style>
