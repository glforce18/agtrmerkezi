// ============================================
// AGTR v6.0 - Forum Advanced Composables
// ============================================

import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  reactionApi,
  pollApi,
  templateApi,
  draftApi,
  searchApi,
  reputationApi,
  bookmarkApi,
  infiniteScrollApi
} from '@/services/forumAdvanced'

/**
 * Use Reactions Hook
 */
export function useReactions(contentType, contentId) {
  const reactions = ref({})
  const userReaction = ref(null)
  const totalReactions = ref(0)
  const loading = ref(false)

  const fetchReactions = async () => {
    try {
      const { data } = await reactionApi.getReactions(contentType, contentId)
      if (data.success) {
        reactions.value = data.reactions
        userReaction.value = data.user_reaction
        totalReactions.value = data.total
      }
    } catch (err) {
      // Silent fail
    }
  }

  const addReaction = async (type) => {
    loading.value = true
    try {
      const { data } = await reactionApi.addReaction(contentType, contentId, type)
      if (data.success) {
        await fetchReactions()
        return data
      }
    } catch (err) {
      throw err
    } finally {
      loading.value = false
    }
  }

  onMounted(fetchReactions)

  return {
    reactions,
    userReaction,
    totalReactions,
    loading,
    fetchReactions,
    addReaction
  }
}

/**
 * Use Bookmarks Hook
 */
export function useBookmarks() {
  const bookmarks = ref([])
  const loading = ref(false)
  const total = ref(0)
  const page = ref(1)

  const fetchBookmarks = async (pageNum = 1) => {
    loading.value = true
    try {
      const { data } = await bookmarkApi.getMyBookmarks(pageNum)
      if (data.success) {
        bookmarks.value = data.bookmarks
        total.value = data.total
        page.value = pageNum
      }
    } catch (err) {
      // Silent fail
    } finally {
      loading.value = false
    }
  }

  const toggleBookmark = async (topicId) => {
    try {
      const { data } = await bookmarkApi.toggleBookmark(topicId)
      if (data.success) {
        await fetchBookmarks(page.value)
        return data.bookmarked
      }
    } catch (err) {
      throw err
    }
  }

  const isBookmarked = async (topicId) => {
    try {
      const { data } = await bookmarkApi.isBookmarked(topicId)
      return data.success && data.bookmarked
    } catch (err) {
      return false
    }
  }

  return {
    bookmarks,
    loading,
    total,
    page,
    fetchBookmarks,
    toggleBookmark,
    isBookmarked
  }
}

/**
 * Use Draft Auto-Save Hook
 */
export function useDraftAutoSave(draftType, topicId = null, autoSaveInterval = 30000) {
  const draft = ref(null)
  const saving = ref(false)
  const lastSaved = ref(null)
  let saveTimer = null

  const saveDraft = async (data) => {
    saving.value = true
    try {
      await draftApi.saveDraft({
        draft_type: draftType,
        topic_id: topicId,
        ...data
      })
      lastSaved.value = new Date()
    } catch (err) {
      // Silent fail
    } finally {
      saving.value = false
    }
  }

  const loadDraft = async () => {
    try {
      const { data } = await draftApi.getDraft(draftType, topicId)
      if (data.success && data.draft) {
        draft.value = data.draft
        return data.draft
      }
    } catch (err) {
      // No draft
    }
    return null
  }

  const deleteDraft = async () => {
    try {
      await draftApi.deleteDraft(draftType, topicId)
      draft.value = null
      lastSaved.value = null
    } catch (err) {
      // Silent fail
    }
  }

  const startAutoSave = (getDataFn) => {
    if (saveTimer) clearInterval(saveTimer)
    saveTimer = setInterval(() => {
      const data = getDataFn()
      if (data.content || data.title) {
        saveDraft(data)
      }
    }, autoSaveInterval)
  }

  const stopAutoSave = () => {
    if (saveTimer) {
      clearInterval(saveTimer)
      saveTimer = null
    }
  }

  onUnmounted(stopAutoSave)

  return {
    draft,
    saving,
    lastSaved,
    saveDraft,
    loadDraft,
    deleteDraft,
    startAutoSave,
    stopAutoSave
  }
}

/**
 * Use Infinite Scroll Hook
 */
export function useInfiniteScroll(fetchFn, options = {}) {
  const items = ref([])
  const cursor = ref(null)
  const loading = ref(false)
  const hasMore = ref(true)
  const error = ref(null)

  const { threshold = 200, initialLoad = true } = options

  let observer = null
  let sentinelElement = null

  const loadMore = async () => {
    if (loading.value || !hasMore.value) return

    loading.value = true
    error.value = null

    try {
      const result = await fetchFn(cursor.value)

      if (result.items?.length > 0) {
        items.value = [...items.value, ...result.items]
      }

      cursor.value = result.nextCursor
      hasMore.value = result.hasMore ?? false
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    items.value = []
    cursor.value = null
    hasMore.value = true
    error.value = null
  }

  const observe = (element) => {
    if (observer) observer.disconnect()
    sentinelElement = element

    observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !loading.value && hasMore.value) {
          loadMore()
        }
      },
      { rootMargin: `${threshold}px` }
    )

    observer.observe(element)
  }

  const disconnect = () => {
    if (observer) {
      observer.disconnect()
      observer = null
    }
  }

  onMounted(() => {
    if (initialLoad) loadMore()
  })

  onUnmounted(disconnect)

  return {
    items,
    loading,
    hasMore,
    error,
    loadMore,
    reset,
    observe,
    disconnect
  }
}

/**
 * Use Reputation Hook
 */
export function useReputation(userId = null) {
  const reputation = ref(null)
  const leaderboard = ref([])
  const loading = ref(false)

  const fetchReputation = async (id = userId) => {
    if (!id) return

    loading.value = true
    try {
      const { data } = await reputationApi.getUserReputation(id)
      if (data.success) {
        reputation.value = data.reputation
      }
    } catch (err) {
      // Silent fail
    } finally {
      loading.value = false
    }
  }

  const fetchMyReputation = async () => {
    loading.value = true
    try {
      const { data } = await reputationApi.getMyReputation()
      if (data.success) {
        reputation.value = data.reputation
      }
    } catch (err) {
      // Silent fail
    } finally {
      loading.value = false
    }
  }

  const fetchLeaderboard = async (timeframe = 'all', limit = 10) => {
    try {
      const { data } = await reputationApi.getLeaderboard(timeframe, limit)
      if (data.success) {
        leaderboard.value = data.leaderboard
      }
    } catch (err) {
      // Silent fail
    }
  }

  return {
    reputation,
    leaderboard,
    loading,
    fetchReputation,
    fetchMyReputation,
    fetchLeaderboard
  }
}

/**
 * Use Forum Search Hook
 */
export function useForumSearch() {
  const results = ref([])
  const total = ref(0)
  const loading = ref(false)
  const page = ref(1)
  const filters = ref({})

  const search = async (query, searchFilters = {}, pageNum = 1) => {
    loading.value = true
    try {
      const { data } = await searchApi.advancedSearch(
        { query, ...searchFilters },
        pageNum
      )
      if (data.success) {
        results.value = data.results
        total.value = data.total
        page.value = pageNum
        filters.value = searchFilters
      }
    } catch (err) {
      results.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  const quickSearch = async (query, pageNum = 1) => {
    loading.value = true
    try {
      const { data } = await searchApi.quickSearch(query, pageNum)
      if (data.success) {
        results.value = data.results
        total.value = data.total
        page.value = pageNum
      }
    } catch (err) {
      results.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  const findSimilar = async (title, content) => {
    try {
      const { data } = await searchApi.findSimilar(title, content)
      return data.success ? data.similar_topics : []
    } catch (err) {
      return []
    }
  }

  const reset = () => {
    results.value = []
    total.value = 0
    page.value = 1
    filters.value = {}
  }

  return {
    results,
    total,
    loading,
    page,
    filters,
    search,
    quickSearch,
    findSimilar,
    reset
  }
}

/**
 * Use Keyboard Shortcuts Hook
 */
export function useKeyboardShortcuts(shortcuts = {}) {
  const enabled = ref(true)

  const handleKeydown = (e) => {
    if (!enabled.value) return

    // Skip if in input/textarea
    const target = e.target
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
      // Allow specific shortcuts even in inputs
      if (!e.ctrlKey && !e.metaKey) return
    }

    const key = [
      e.ctrlKey ? 'ctrl' : '',
      e.shiftKey ? 'shift' : '',
      e.altKey ? 'alt' : '',
      e.key.toLowerCase()
    ].filter(Boolean).join('+')

    const handler = shortcuts[key]
    if (handler) {
      e.preventDefault()
      handler(e)
    }
  }

  onMounted(() => {
    document.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown)
  })

  return {
    enabled
  }
}

export default {
  useReactions,
  useBookmarks,
  useDraftAutoSave,
  useInfiniteScroll,
  useReputation,
  useForumSearch,
  useKeyboardShortcuts
}
