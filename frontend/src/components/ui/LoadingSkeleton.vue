<template>
  <div class="skeleton-wrapper" :class="variant">
    <template v-if="variant === 'card'">
      <div class="skeleton-card" v-for="n in count" :key="n">
        <div class="skeleton-header">
          <div class="skeleton-avatar"></div>
          <div class="skeleton-lines">
            <div class="skeleton-line w-3/4"></div>
            <div class="skeleton-line w-1/2"></div>
          </div>
        </div>
        <div class="skeleton-content">
          <div class="skeleton-line"></div>
          <div class="skeleton-line w-5/6"></div>
        </div>
      </div>
    </template>

    <template v-else-if="variant === 'list'">
      <div class="skeleton-list-item" v-for="n in count" :key="n">
        <div class="skeleton-circle"></div>
        <div class="skeleton-lines flex-1">
          <div class="skeleton-line w-1/2"></div>
          <div class="skeleton-line w-1/3"></div>
        </div>
      </div>
    </template>

    <template v-else-if="variant === 'table'">
      <div class="skeleton-table">
        <div class="skeleton-table-header">
          <div class="skeleton-cell" v-for="i in columns" :key="i"></div>
        </div>
        <div class="skeleton-table-row" v-for="n in count" :key="n">
          <div class="skeleton-cell" v-for="i in columns" :key="i"></div>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="skeleton-line" v-for="n in count" :key="n" :style="{ width: getRandomWidth() }"></div>
    </template>
  </div>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'text', // text, card, list, table
    validator: (v) => ['text', 'card', 'list', 'table'].includes(v)
  },
  count: {
    type: Number,
    default: 3
  },
  columns: {
    type: Number,
    default: 4
  }
})

const getRandomWidth = () => {
  const widths = ['60%', '75%', '90%', '100%', '85%']
  return widths[Math.floor(Math.random() * widths.length)]
}
</script>

<style scoped>
.skeleton-wrapper {
  width: 100%;
}

.skeleton-line {
  height: 1rem;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
}

.skeleton-circle,
.skeleton-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  flex-shrink: 0;
}

.skeleton-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.skeleton-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.skeleton-lines {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.skeleton-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.skeleton-table {
  width: 100%;
}

.skeleton-table-header,
.skeleton-table-row {
  display: flex;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.skeleton-table-header .skeleton-cell {
  height: 1.25rem;
}

.skeleton-cell {
  flex: 1;
  height: 1rem;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 0.25rem;
}

.w-1\/2 { width: 50%; }
.w-1\/3 { width: 33%; }
.w-2\/3 { width: 66%; }
.w-3\/4 { width: 75%; }
.w-5\/6 { width: 83%; }

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
