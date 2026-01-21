import { ref } from 'vue'
import { useThemeStore } from '@/stores/theme'

const sounds = {
  // Placeholder - will be added later
  click: null,
  notification: null,
  success: null,
  error: null
}

export function useSound() {
  const themeStore = useThemeStore()
  const audioCache = ref(new Map())

  function loadSound(name) {
    if (!sounds[name]) {
      return null
    }

    if (!audioCache.value.has(name)) {
      const audio = new Audio(sounds[name])
      audio.volume = 0.3
      audioCache.value.set(name, audio)
    }

    return audioCache.value.get(name)
  }

  function play(name) {
    if (!themeStore.soundEnabled) return

    const audio = loadSound(name)
    if (audio) {
      audio.currentTime = 0
      audio.play().catch(() => {
        // Sound play failed - browser autoplay policy
      })
    }
  }

  return {
    play
  }
}
