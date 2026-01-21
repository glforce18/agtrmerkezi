/**
 * AGTR Merkezi - Lazy Load Directive
 * v-lazy directive for lazy loading images
 */

const imageObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target

      // Get the src from data attribute
      const src = img.dataset.src
      const srcset = img.dataset.srcset

      if (src) {
        img.src = src
        img.removeAttribute('data-src')
      }

      if (srcset) {
        img.srcset = srcset
        img.removeAttribute('data-srcset')
      }

      // Add loaded class for animation
      img.classList.add('lazy-loaded')
      img.classList.remove('lazy-loading')

      // Stop observing
      observer.unobserve(img)
    }
  })
}, {
  rootMargin: '50px 0px',
  threshold: 0.01
})

/**
 * Lazy load directive
 * Usage: <img v-lazy="imageUrl" />
 */
export const lazyLoad = {
  mounted(el, binding) {
    // Set placeholder or blur
    el.classList.add('lazy-loading')

    // Store original src in data attribute
    if (binding.value) {
      el.dataset.src = binding.value
      // Set a placeholder or low-res version
      el.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"%3E%3C/svg%3E'
    }

    // Start observing
    imageObserver.observe(el)
  },

  updated(el, binding) {
    if (binding.value !== binding.oldValue) {
      el.dataset.src = binding.value
      imageObserver.observe(el)
    }
  },

  unmounted(el) {
    imageObserver.unobserve(el)
  }
}

/**
 * Background image lazy load directive
 * Usage: <div v-lazy-bg="imageUrl" />
 */
const bgObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target
      const src = el.dataset.bg

      if (src) {
        el.style.backgroundImage = `url(${src})`
        el.removeAttribute('data-bg')
        el.classList.add('lazy-bg-loaded')
      }

      observer.unobserve(el)
    }
  })
}, {
  rootMargin: '50px 0px',
  threshold: 0.01
})

export const lazyBg = {
  mounted(el, binding) {
    if (binding.value) {
      el.dataset.bg = binding.value
      bgObserver.observe(el)
    }
  },

  updated(el, binding) {
    if (binding.value !== binding.oldValue) {
      el.dataset.bg = binding.value
      bgObserver.observe(el)
    }
  },

  unmounted(el) {
    bgObserver.unobserve(el)
  }
}

/**
 * Install directives as Vue plugin
 */
export function install(app) {
  app.directive('lazy', lazyLoad)
  app.directive('lazy-bg', lazyBg)
}

export default {
  install,
  lazyLoad,
  lazyBg
}
