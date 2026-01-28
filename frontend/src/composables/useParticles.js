import { onMounted, onUnmounted } from 'vue'

export function useParticles(canvasRef, options = {}) {
  const {
    particleCount = 50,
    particleColor = 'rgba(249, 115, 22, 0.5)',
    lineColor = 'rgba(249, 115, 22, 0.2)',
    particleSize = 2,
    speed = 0.5,
    connectionDistance = 150
  } = options

  let animationId = null
  let particles = []

  class Particle {
    constructor(canvas) {
      this.canvas = canvas
      this.x = Math.random() * canvas.width
      this.y = Math.random() * canvas.height
      this.vx = (Math.random() - 0.5) * speed
      this.vy = (Math.random() - 0.5) * speed
      this.size = particleSize
    }

    update() {
      this.x += this.vx
      this.y += this.vy

      if (this.x < 0 || this.x > this.canvas.width) this.vx *= -1
      if (this.y < 0 || this.y > this.canvas.height) this.vy *= -1
    }

    draw(ctx) {
      ctx.fillStyle = particleColor
      ctx.beginPath()
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
      ctx.fill()
    }
  }

  const init = () => {
    const canvas = canvasRef.value
    if (!canvas) return

    const ctx = canvas.getContext('2d')

    // Set canvas size
    const resize = () => {
      canvas.width = canvas.offsetWidth
      canvas.height = canvas.offsetHeight
    }
    resize()
    window.addEventListener('resize', resize)

    // Create particles
    particles = []
    for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle(canvas))
    }

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Update and draw particles
      particles.forEach(particle => {
        particle.update()
        particle.draw(ctx)
      })

      // Draw connections
      ctx.strokeStyle = lineColor
      ctx.lineWidth = 1
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x
          const dy = particles[i].y - particles[j].y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < connectionDistance) {
            const opacity = (1 - distance / connectionDistance) * 0.3
            ctx.strokeStyle = `rgba(249, 115, 22, ${opacity})`
            ctx.beginPath()
            ctx.moveTo(particles[i].x, particles[i].y)
            ctx.lineTo(particles[j].x, particles[j].y)
            ctx.stroke()
          }
        }
      }

      animationId = requestAnimationFrame(animate)
    }

    animate()

    // Cleanup
    return () => {
      window.removeEventListener('resize', resize)
      if (animationId) {
        cancelAnimationFrame(animationId)
      }
    }
  }

  onMounted(() => {
    const cleanup = init()
    onUnmounted(() => {
      if (cleanup) cleanup()
    })
  })
}
