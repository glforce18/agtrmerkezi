<template>
  <div class="forum-page min-h-screen relative overflow-hidden">
    <!-- Skip to content link for accessibility -->
    <a href="#forum-main-content" class="forum-skip-link">
      Ana içeriği atla
    </a>

    <!-- Subtle Background -->
    <div class="subtle-bg" aria-hidden="true"></div>

    <!-- Main Layout -->
    <div :class="layoutClasses">
      <!-- Left Sidebar (Categories) -->
      <aside
        v-if="showLeftSidebar"
        class="forum-layout__sidebar-left"
        role="navigation"
        aria-label="Forum kategorileri"
      >
        <slot name="sidebar-left">
          <ForumSidebar />
        </slot>
      </aside>

      <!-- Main Content -->
      <main
        id="forum-main-content"
        class="forum-layout__content"
        role="main"
      >
        <slot></slot>
      </main>

      <!-- Right Sidebar -->
      <aside
        v-if="showRightSidebar"
        class="forum-layout__sidebar-right"
        role="complementary"
        aria-label="Forum yan panel"
      >
        <slot name="sidebar-right"></slot>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import ForumSidebar from './ForumSidebar.vue'

const props = defineProps({
  showLeftSidebar: {
    type: Boolean,
    default: true
  },
  showRightSidebar: {
    type: Boolean,
    default: true
  },
  fullWidth: {
    type: Boolean,
    default: false
  }
})

const layoutClasses = computed(() => {
  const classes = ['forum-layout']

  if (props.fullWidth) {
    classes.push('forum-layout--full')
  } else if (!props.showRightSidebar) {
    classes.push('forum-layout--no-right')
  }

  return classes
})
</script>

<style scoped>
/* Layout Grid */
.forum-layout {
  display: grid;
  grid-template-columns: 260px 1fr 280px;
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  align-items: start;
}

.forum-layout--no-right {
  grid-template-columns: 260px 1fr;
}

.forum-layout--full {
  grid-template-columns: 1fr;
}

/* Sticky Sidebars */
.forum-layout__sidebar-left,
.forum-layout__sidebar-right {
  position: sticky;
  top: 90px;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
  scrollbar-width: thin;
}

/* Background */
.subtle-bg {
  position: fixed;
  inset: 0;
  background: radial-gradient(ellipse at top, rgba(249, 115, 22, 0.03) 0%, transparent 50%);
  pointer-events: none;
  z-index: -1;
}

/* Skip Link */
.forum-skip-link {
  position: absolute;
  left: -9999px;
  z-index: 999;
  padding: 12px 24px;
  background: var(--forum-brand, #f97316);
  color: white;
  border-radius: 8px;
  text-decoration: none;
}

.forum-skip-link:focus {
  left: 16px;
  top: 16px;
}

/* Responsive */
@media (max-width: 1200px) {
  .forum-layout {
    grid-template-columns: 220px 1fr;
  }
  .forum-layout__sidebar-right {
    display: none;
  }
}

@media (max-width: 768px) {
  .forum-layout {
    grid-template-columns: 1fr;
    padding: 16px;
  }
  .forum-layout__sidebar-left {
    position: static;
    max-height: none;
    display: none;
  }
}
</style>
