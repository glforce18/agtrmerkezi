/**
 * Particles.js - Animasyonlu Parçacık Sistemi
 * Modern hero background için optimize edilmiş parçacık efektleri
 */

class ParticleSystem {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: null, y: null, radius: 150 };
        
        // Konfigürasyon
        this.config = {
            particleCount: options.particleCount || 80,
            particleColor: options.particleColor || 'rgba(139, 92, 246, 0.5)',
            lineColor: options.lineColor || 'rgba(139, 92, 246, 0.2)',
            particleSize: options.particleSize || 2,
            particleSpeed: options.particleSpeed || 0.5,
            lineDistance: options.lineDistance || 120,
            mouseInteraction: options.mouseInteraction !== false,
            ...options
        };
        
        this.init();
    }
    
    init() {
        this.resizeCanvas();
        this.createParticles();
        
        window.addEventListener('resize', () => this.resizeCanvas());
        
        if (this.config.mouseInteraction) {
            this.canvas.addEventListener('mousemove', (e) => {
                this.mouse.x = e.offsetX;
                this.mouse.y = e.offsetY;
            });
            
            this.canvas.addEventListener('mouseleave', () => {
                this.mouse.x = null;
                this.mouse.y = null;
            });
        }
        
        this.animate();
    }
    
    resizeCanvas() {
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
    }
    
    createParticles() {
        this.particles = [];
        for (let i = 0; i < this.config.particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * this.config.particleSpeed,
                vy: (Math.random() - 0.5) * this.config.particleSpeed,
                size: Math.random() * this.config.particleSize + 1
            });
        }
    }
    
    drawParticle(particle) {
        this.ctx.beginPath();
        this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        this.ctx.fillStyle = this.config.particleColor;
        this.ctx.fill();
    }
    
    updateParticle(particle) {
        particle.x += particle.vx;
        particle.y += particle.vy;
        
        // Kenarlara çarpınca yönünü değiştir
        if (particle.x < 0 || particle.x > this.canvas.width) particle.vx *= -1;
        if (particle.y < 0 || particle.y > this.canvas.height) particle.vy *= -1;
        
        // Mouse ile etkileşim
        if (this.mouse.x !== null && this.mouse.y !== null) {
            const dx = this.mouse.x - particle.x;
            const dy = this.mouse.y - particle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < this.mouse.radius) {
                const force = (this.mouse.radius - distance) / this.mouse.radius;
                const angle = Math.atan2(dy, dx);
                particle.vx -= Math.cos(angle) * force * 0.5;
                particle.vy -= Math.sin(angle) * force * 0.5;
            }
        }
        
        // Hız limiti
        const speed = Math.sqrt(particle.vx * particle.vx + particle.vy * particle.vy);
        if (speed > this.config.particleSpeed * 2) {
            particle.vx = (particle.vx / speed) * this.config.particleSpeed * 2;
            particle.vy = (particle.vy / speed) * this.config.particleSpeed * 2;
        }
    }
    
    connectParticles() {
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < this.config.lineDistance) {
                    const opacity = 1 - (distance / this.config.lineDistance);
                    this.ctx.strokeStyle = this.config.lineColor.replace('0.2', opacity * 0.2);
                    this.ctx.lineWidth = 0.5;
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.stroke();
                }
            }
        }
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.particles.forEach(particle => {
            this.updateParticle(particle);
            this.drawParticle(particle);
        });
        
        this.connectParticles();
        
        requestAnimationFrame(() => this.animate());
    }
    
    destroy() {
        this.particles = [];
        window.removeEventListener('resize', () => this.resizeCanvas());
    }
}

// Global export
window.ParticleSystem = ParticleSystem;

// Auto-init on DOM ready (only on home page)
document.addEventListener('DOMContentLoaded', () => {
    // Hero section için otomatik başlatma (sadece ana sayfada)
    const heroCanvas = document.getElementById('particles-canvas');
    if (heroCanvas) {
        console.log('🎨 Particles system initializing...');
        try {
            window.heroParticles = new ParticleSystem('particles-canvas', {
                particleCount: 60,
                particleColor: 'rgba(139, 92, 246, 0.6)',
                lineColor: 'rgba(139, 92, 246, 0.15)',
                particleSpeed: 0.3,
                lineDistance: 150
            });
            console.log('✅ Particles system ready!');
        } catch (error) {
            console.error('Particles error:', error);
        }
    }
    // Not a warning - particles only needed on home page
});
