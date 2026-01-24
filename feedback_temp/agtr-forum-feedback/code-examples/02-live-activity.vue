<!-- LiveActivityFeed.vue - Canlı Forum Aktivite Akışı -->
<template>
  <div class="live-activity-feed card">
    <div class="feed-header">
      <h2 class="feed-title">
        <span class="live-indicator"></span>
        Canlı Aktivite
      </h2>
      <span class="activity-count">{{ activities.length }} aktivite</span>
    </div>

    <div class="activity-stream" ref="streamRef">
      <TransitionGroup name="activity-fade">
        <div 
          v-for="activity in activities" 
          :key="activity.id"
          class="activity-item"
          @click="handleActivityClick(activity)"
        >
          <div class="activity-avatar">
            <img :src="activity.user.avatar" :alt="activity.user.username" />
            <div class="activity-type-icon" :class="activity.type">
              {{ getActivityIcon(activity.type) }}
            </div>
          </div>

          <div class="activity-content">
            <div class="activity-main">
              <strong class="activity-username">{{ activity.user.username }}</strong>
              <span class="activity-action">{{ activity.action }}</span>
            </div>
            
            <div class="activity-meta">
              <span class="activity-time">{{ activity.time }}</span>
              
              <div v-if="activity.topic_title" class="activity-topic">
                <span class="topic-icon">💬</span>
                <span class="topic-title">{{ activity.topic_title }}</span>
              </div>
            </div>
          </div>

          <div class="activity-arrow">
            →
          </div>
        </div>
      </TransitionGroup>

      <!-- Boş Durum -->
      <div v-if="activities.length === 0" class="empty-state">
        <span class="empty-icon">💤</span>
        <p class="empty-text">Henüz aktivite yok</p>
        <p class="empty-subtext">İlk konuyu sen aç!</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Props
const props = defineProps({
  activities: {
    type: Array,
    default: () => []
  }
})

// Refs
const streamRef = ref(null)

// Methods
const getActivityIcon = (type) => {
  const icons = {
    'new_topic': '📝',
    'reply': '💬',
    'like': '❤️',
    'level_up': '⬆️',
    'achievement': '🏆'
  }
  return icons[type] || '•'
}

const handleActivityClick = (activity) => {
  if (activity.topic_id) {
    router.push(`/forum/topic/${activity.topic_id}`)
  }
}
</script>

<style scoped>
.live-activity-feed {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 20px;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(249, 115, 22, 0.2);
}

/* Animated Border */
.live-activity-feed::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(180deg, 
    var(--primary) 0%, 
    var(--primary-light) 100%);
  animation: pulse-bar 2s infinite;
}

@keyframes pulse-bar {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Header */
.feed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.feed-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.live-indicator {
  width: 12px;
  height: 12px;
  background: #ef4444;
  border-radius: 50%;
  animation: live-pulse 2s infinite;
  box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
}

@keyframes live-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
  }
}

.activity-count {
  font-size: 0.9rem;
  color: var(--text-secondary);
  padding: 4px 12px;
  background: rgba(249, 115, 22, 0.1);
  border-radius: 12px;
}

/* Activity Stream */
.activity-stream {
  max-height: 400px;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Custom Scrollbar */
.activity-stream::-webkit-scrollbar {
  width: 6px;
}

.activity-stream::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.activity-stream::-webkit-scrollbar-thumb {
  background: var(--primary);
  border-radius: 3px;
}

/* Activity Item */
.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-md);
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.activity-item:hover {
  background: rgba(249, 115, 22, 0.1);
  transform: translateX(4px);
}

.activity-item:hover .activity-arrow {
  opacity: 1;
  transform: translateX(0);
}

/* Avatar */
.activity-avatar {
  position: relative;
  flex-shrink: 0;
}

.activity-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid var(--primary);
}

.activity-type-icon {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  border-radius: 50%;
  border: 2px solid var(--bg-card);
}

.activity-type-icon.new_topic {
  background: #22c55e;
}

.activity-type-icon.reply {
  background: #3b82f6;
}

.activity-type-icon.like {
  background: #ef4444;
}

.activity-type-icon.level_up {
  background: #f59e0b;
}

.activity-type-icon.achievement {
  background: #8b5cf6;
}

/* Content */
.activity-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.activity-main {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: baseline;
}

.activity-username {
  color: var(--primary);
  font-weight: 600;
  font-size: 0.95rem;
}

.activity-action {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.4;
}

.activity-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.activity-time {
  color: var(--primary);
  font-size: 0.8rem;
  font-weight: 500;
}

.activity-topic {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  max-width: 250px;
}

.topic-icon {
  font-size: 0.9rem;
}

.topic-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Arrow */
.activity-arrow {
  color: var(--primary);
  font-size: 1.2rem;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
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
  font-size: 1.1rem;
  color: var(--text-secondary);
  margin: 0 0 6px 0;
}

.empty-subtext {
  font-size: 0.9rem;
  color: var(--text-secondary);
  opacity: 0.7;
  margin: 0;
}

/* Transition Animations */
.activity-fade-enter-active {
  animation: fadeInSlide 0.5s ease-out;
}

.activity-fade-leave-active {
  animation: fadeOutSlide 0.3s ease-in;
}

@keyframes fadeInSlide {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeOutSlide {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(20px);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .activity-stream {
    max-height: 300px;
  }
  
  .activity-topic {
    max-width: 150px;
  }
}
</style>
