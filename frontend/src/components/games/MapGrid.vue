<template>
  <div class="map-grid-container">
    <!-- Filter tabs -->
    <div v-if="showFilters" class="map-filters">
      <button
        v-for="filter in mapTypes"
        :key="filter.value"
        class="filter-btn"
        :class="{ active: activeFilter === filter.value }"
        @click="setFilter(filter.value)"
      >
        {{ filter.label }}
      </button>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="map-grid loading">
      <div v-for="i in 6" :key="i" class="map-card skeleton">
        <div class="skeleton-image"></div>
        <div class="skeleton-text"></div>
      </div>
    </div>

    <!-- Maps grid -->
    <div v-else-if="filteredMaps.length" class="map-grid">
      <div
        v-for="map in filteredMaps"
        :key="map.id"
        class="map-card"
        @click="$emit('select', map)"
      >
        <div class="map-image">
          <img
            v-if="map.thumbnail_path"
            :src="map.thumbnail_path"
            :alt="map.map_name"
            @error="(e) => e.target.style.display = 'none'"
          />
          <div class="map-placeholder" v-else>
            <span class="map-icon">🗺️</span>
          </div>

          <!-- Map type badge -->
          <span v-if="map.map_type" class="map-type-badge" :class="getMapTypeClass(map.map_type)">
            {{ map.map_type }}
          </span>

          <!-- Competitive badge -->
          <span v-if="map.is_competitive" class="competitive-badge">
            🏆
          </span>
        </div>

        <div class="map-info">
          <h4 class="map-name">{{ map.display_name || map.map_name }}</h4>
          <div class="map-meta">
            <span v-if="map.is_official" class="official-tag">Resmi</span>
            <span v-if="map.popularity_score" class="popularity">
              {{ formatPopularity(map.popularity_score) }} indirme
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="empty-state">
      <span class="empty-icon">🗺️</span>
      <p>Harita bulunamadi</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useGameAssets } from '@/composables/useGameAssets'

const props = defineProps({
  gameSlug: {
    type: String,
    required: true
  },
  limit: {
    type: Number,
    default: 20
  },
  showFilters: {
    type: Boolean,
    default: true
  },
  initialFilter: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['select', 'loaded'])

const { getGameMaps, loading } = useGameAssets()

const maps = ref([])
const activeFilter = ref(props.initialFilter)

// Map type filters
const mapTypes = [
  { value: null, label: 'Tumu' },
  { value: 'de_', label: 'Bomba (de_)' },
  { value: 'cs_', label: 'Rehine (cs_)' },
  { value: 'fy_', label: 'Fun (fy_)' },
  { value: 'aim_', label: 'Aim' },
  { value: 'awp_', label: 'AWP' }
]

const filteredMaps = computed(() => {
  if (!activeFilter.value) {
    return maps.value
  }
  return maps.value.filter(m => m.map_type === activeFilter.value)
})

async function loadMaps() {
  maps.value = await getGameMaps(props.gameSlug, null, props.limit)
  emit('loaded', maps.value)
}

function setFilter(filter) {
  activeFilter.value = filter
}

function getMapTypeClass(mapType) {
  const classes = {
    'de_': 'bomb',
    'cs_': 'hostage',
    'fy_': 'fun',
    'aim_': 'aim',
    'awp_': 'awp',
    'as_': 'assassin'
  }
  return classes[mapType] || 'other'
}

function formatPopularity(count) {
  if (count >= 1000000) {
    return (count / 1000000).toFixed(1) + 'M'
  }
  if (count >= 1000) {
    return (count / 1000).toFixed(1) + 'K'
  }
  return count.toString()
}

watch(() => props.gameSlug, loadMaps)

onMounted(loadMaps)
</script>

<style scoped>
.map-grid-container {
  width: 100%;
}

.map-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.filter-btn {
  padding: 8px 16px;
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: var(--text-muted, #94a3b8);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  border-color: var(--primary-color, #f97316);
  color: white;
}

.filter-btn.active {
  background: var(--primary-color, #f97316);
  border-color: var(--primary-color, #f97316);
  color: white;
}

.map-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.map-card {
  background: var(--bg-card, #131a22);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.map-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  border-color: var(--primary-color, #f97316);
}

.map-card.skeleton {
  pointer-events: none;
}

.map-image {
  position: relative;
  aspect-ratio: 4 / 3;
  background: var(--bg-secondary, #1a1a2e);
  overflow: hidden;
}

.map-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.map-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2a2a4e 0%, #1a1a2e 100%);
}

.map-icon {
  font-size: 32px;
  opacity: 0.5;
}

.map-type-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.map-type-badge.bomb { background: #e63946; color: white; }
.map-type-badge.hostage { background: #2a9d8f; color: white; }
.map-type-badge.fun { background: #f4a261; color: black; }
.map-type-badge.aim { background: #457b9d; color: white; }
.map-type-badge.awp { background: #9b59b6; color: white; }
.map-type-badge.other { background: #6c757d; color: white; }

.competitive-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 16px;
}

.map-info {
  padding: 12px;
}

.map-name {
  font-size: 14px;
  font-weight: 600;
  color: white;
  margin: 0 0 6px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.map-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: var(--text-muted, #94a3b8);
}

.official-tag {
  color: #22c55e;
  font-weight: 500;
}

.popularity {
  color: var(--text-muted, #94a3b8);
}

/* Skeleton */
.skeleton-image {
  aspect-ratio: 4 / 3;
  background: linear-gradient(90deg, #1a1a2e 0%, #2a2a4e 50%, #1a1a2e 100%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-text {
  height: 40px;
  margin: 12px;
  background: linear-gradient(90deg, #1a1a2e 0%, #2a2a4e 50%, #1a1a2e 100%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-muted, #94a3b8);
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
  opacity: 0.5;
}
</style>
