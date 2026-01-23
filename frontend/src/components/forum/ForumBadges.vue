<template>
  <div :class="['forum-user-badges', { 'forum-user-badges--max-5': max === 5 }]" role="list" aria-label="Kullanici rozetleri">
    <!-- Level Badge (always first if shown) -->
    <n-tooltip v-if="showLevel && level" trigger="hover" placement="top">
      <template #trigger>
        <div class="forum-level-badge" role="listitem">
          <ZapIcon class="w-3 h-3" />
          <span>Lv.{{ level }}</span>
        </div>
      </template>
      <div class="forum-badges-tooltip">
        <strong>Seviye {{ level }}</strong>
        <div v-if="xp" class="forum-badges-tooltip__xp">
          {{ formatNumber(xp) }} XP
        </div>
      </div>
    </n-tooltip>

    <!-- Badge Icons -->
    <n-tooltip
      v-for="badge in visibleBadges"
      :key="badge.id"
      trigger="hover"
      placement="top"
    >
      <template #trigger>
        <div
          class="forum-user-badge"
          :style="{ background: badge.color || '#4f8cff' }"
          role="listitem"
        >
          <component :is="getBadgeIcon(badge.icon)" class="w-3 h-3 text-white" />
        </div>
      </template>
      <div class="forum-badges-tooltip">
        <strong>{{ badge.name }}</strong>
        <div v-if="badge.description" class="forum-badges-tooltip__desc">
          {{ badge.description }}
        </div>
        <div v-if="badge.earnedAt" class="forum-badges-tooltip__date">
          Kazanildi: {{ badge.earnedAt }}
        </div>
      </div>
    </n-tooltip>

    <!-- More indicator -->
    <n-tooltip v-if="hasMore" trigger="hover" placement="top">
      <template #trigger>
        <div class="forum-user-badges__more" role="listitem" aria-label="Daha fazla rozet">
          +{{ hiddenCount }}
        </div>
      </template>
      <div class="forum-badges-tooltip forum-badges-tooltip--list">
        <strong>Diger Rozetler</strong>
        <div
          v-for="badge in hiddenBadges"
          :key="badge.id"
          class="forum-badges-tooltip__item"
        >
          <div
            class="forum-badges-tooltip__icon"
            :style="{ background: badge.color || '#4f8cff' }"
          >
            <component :is="getBadgeIcon(badge.icon)" class="w-2.5 h-2.5 text-white" />
          </div>
          <span>{{ badge.name }}</span>
        </div>
      </div>
    </n-tooltip>

    <!-- XP Progress Bar (optional) -->
    <div v-if="showXpBar && xpProgress !== null" class="forum-badges-xp-container">
      <div class="forum-xp-bar forum-badges-xp-bar">
        <div
          class="forum-xp-bar__fill"
          :style="{ width: `${xpProgress}%` }"
        />
      </div>
      <span v-if="showXpText" class="forum-badges-xp-text">
        {{ xpProgress }}%
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  ZapIcon,
  StarIcon,
  ShieldIcon,
  AwardIcon,
  TrophyIcon,
  FlameIcon,
  HeartIcon,
  MessageSquareIcon,
  CodeIcon,
  BookOpenIcon,
  UsersIcon,
  CrownIcon,
  TargetIcon,
  RocketIcon,
  GemIcon
} from 'lucide-vue-next'

const props = defineProps({
  badges: {
    type: Array,
    default: () => [],
    validator: (badges) => {
      if (!Array.isArray(badges)) return false
      return badges.every(badge => badge && (typeof badge.id !== 'undefined' || typeof badge.name === 'string'))
    }
  },
  max: {
    type: Number,
    default: 5,
    validator: (val) => val > 0 && val <= 20
  },
  level: {
    type: Number,
    default: null,
    validator: (val) => val === null || (val >= 0 && val <= 999)
  },
  xp: {
    type: Number,
    default: null,
    validator: (val) => val === null || val >= 0
  },
  xpProgress: {
    type: Number,
    default: null,
    validator: (val) => val === null || (val >= 0 && val <= 100)
  },
  showLevel: {
    type: Boolean,
    default: true
  },
  showXpBar: {
    type: Boolean,
    default: false
  },
  showXpText: {
    type: Boolean,
    default: true
  }
})

// Safe computed properties
const safeLevel = computed(() => Math.max(0, props.level || 0))
const safeXp = computed(() => Math.max(0, props.xp || 0))
const safeXpProgress = computed(() => Math.min(100, Math.max(0, props.xpProgress || 0)))
const safeBadges = computed(() => props.badges || [])

// Icon mapping for badge types
const badgeIcons = {
  star: StarIcon,
  shield: ShieldIcon,
  award: AwardIcon,
  trophy: TrophyIcon,
  flame: FlameIcon,
  heart: HeartIcon,
  message: MessageSquareIcon,
  code: CodeIcon,
  book: BookOpenIcon,
  users: UsersIcon,
  crown: CrownIcon,
  target: TargetIcon,
  rocket: RocketIcon,
  gem: GemIcon,
  default: AwardIcon
}

const visibleBadges = computed(() => {
  const maxVisible = props.showLevel && props.level ? props.max - 1 : props.max
  return props.badges.slice(0, maxVisible)
})

const hiddenBadges = computed(() => {
  const maxVisible = props.showLevel && props.level ? props.max - 1 : props.max
  return props.badges.slice(maxVisible)
})

const hasMore = computed(() => {
  return hiddenBadges.value.length > 0
})

const hiddenCount = computed(() => {
  return hiddenBadges.value.length
})

const getBadgeIcon = (iconName) => {
  if (!iconName) return badgeIcons.default
  return badgeIcons[iconName.toLowerCase()] || badgeIcons.default
}

const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}
</script>

<style scoped>
.forum-user-badges {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.forum-badges-tooltip {
  text-align: center;
  padding: 4px;
}

.forum-badges-tooltip strong {
  display: block;
  margin-bottom: 4px;
}

.forum-badges-tooltip__xp {
  font-size: 12px;
  color: var(--forum-accent);
}

.forum-badges-tooltip__desc {
  font-size: 12px;
  color: var(--forum-muted);
  max-width: 200px;
}

.forum-badges-tooltip__date {
  font-size: 11px;
  color: var(--forum-muted);
  margin-top: 4px;
}

.forum-badges-tooltip--list {
  text-align: left;
  max-width: 220px;
}

.forum-badges-tooltip__item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 13px;
}

.forum-badges-tooltip__icon {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.forum-badges-xp-container {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  margin-top: 4px;
}

.forum-badges-xp-bar {
  flex: 1;
  height: 4px;
}

.forum-badges-xp-text {
  font-size: 11px;
  color: var(--forum-muted);
  white-space: nowrap;
}
</style>
