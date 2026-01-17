/*
 * AGTR Merkezi - Special Effects v3.0
 * Particles, Matrix Rain, Parallax, 3D Models
 */

// ==================== PARTICLE SYSTEM ====================
const Particles = {
    canvas: null,
    ctx: null,
    particles: [],
    mouse: { x: 0, y: 0 },
    animationId: null,
    
    config: {
        particleCount: 80,
        connectionDistance: 150,
        particleColor: '#00ff88',
        lineColor: 'rgba(0, 255, 136, 0.1)',
        speed: 0.5,
        size: 2
    },
    
    init(containerId = 'particles-bg') {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        this.canvas = document.createElement('canvas');
        this.canvas.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        `;
        
        container.style.position = 'relative';
        container.appendChild(this.canvas);
        
        this.ctx = this.canvas.getContext('2d');
        this.resize();
        this.createParticles();
        this.animate();
        
        window.addEventListener('resize', () => this.resize());
        document.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });
    },
    
    resize() {
        this.canvas.width = this.canvas.parentElement.offsetWidth;
        this.canvas.height = this.canvas.parentElement.offsetHeight;
    },
    
    createParticles() {
        this.particles = [];
        for (let i = 0; i < this.config.particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * this.config.speed,
                vy: (Math.random() - 0.5) * this.config.speed,
                size: Math.random() * this.config.size + 1
            });
        }
    },
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.particles.forEach((p, i) => {
            // Move
            p.x += p.vx;
            p.y += p.vy;
            
            // Bounce
            if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;
            
            // Draw particle
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fillStyle = this.config.particleColor;
            this.ctx.fill();
            
            // Connect nearby particles
            for (let j = i + 1; j < this.particles.length; j++) {
                const p2 = this.particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist < this.config.connectionDistance) {
                    const opacity = 1 - dist / this.config.connectionDistance;
                    this.ctx.beginPath();
                    this.ctx.moveTo(p.x, p.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.strokeStyle = `rgba(0, 255, 136, ${opacity * 0.2})`;
                    this.ctx.stroke();
                }
            }
            
            // Mouse interaction
            const mdx = p.x - this.mouse.x;
            const mdy = p.y - this.mouse.y;
            const mdist = Math.sqrt(mdx * mdx + mdy * mdy);
            
            if (mdist < 100) {
                const force = (100 - mdist) / 100;
                p.vx += mdx * force * 0.01;
                p.vy += mdy * force * 0.01;
            }
        });
        
        this.animationId = requestAnimationFrame(() => this.animate());
    },
    
    destroy() {
        cancelAnimationFrame(this.animationId);
        this.canvas?.remove();
    }
};

// ==================== MATRIX RAIN ====================
const MatrixRain = {
    canvas: null,
    ctx: null,
    columns: [],
    animationId: null,
    
    chars: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()λΩπ∆',
    
    init(containerId = 'matrix-bg') {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        this.canvas = document.createElement('canvas');
        this.canvas.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            opacity: 0.15;
        `;
        
        container.style.position = 'relative';
        container.appendChild(this.canvas);
        
        this.ctx = this.canvas.getContext('2d');
        this.resize();
        this.animate();
        
        window.addEventListener('resize', () => this.resize());
    },
    
    resize() {
        this.canvas.width = this.canvas.parentElement.offsetWidth;
        this.canvas.height = this.canvas.parentElement.offsetHeight;
        
        const columnCount = Math.floor(this.canvas.width / 20);
        this.columns = Array(columnCount).fill(0);
    },
    
    animate() {
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = '#00ff88';
        this.ctx.font = '15px monospace';
        
        this.columns.forEach((y, i) => {
            const char = this.chars[Math.floor(Math.random() * this.chars.length)];
            const x = i * 20;
            
            this.ctx.fillText(char, x, y);
            
            if (y > this.canvas.height && Math.random() > 0.975) {
                this.columns[i] = 0;
            } else {
                this.columns[i] = y + 20;
            }
        });
        
        this.animationId = requestAnimationFrame(() => this.animate());
    },
    
    destroy() {
        cancelAnimationFrame(this.animationId);
        this.canvas?.remove();
    }
};

// ==================== PARALLAX EFFECT ====================
const Parallax = {
    elements: [],
    
    init() {
        this.elements = document.querySelectorAll('[data-parallax]');
        if (this.elements.length === 0) return;
        
        window.addEventListener('scroll', () => this.update());
        window.addEventListener('mousemove', (e) => this.mouseMove(e));
        
        this.update();
    },
    
    update() {
        const scrollY = window.pageYOffset;
        
        this.elements.forEach(el => {
            const speed = parseFloat(el.getAttribute('data-parallax')) || 0.5;
            const rect = el.getBoundingClientRect();
            const visible = rect.top < window.innerHeight && rect.bottom > 0;
            
            if (visible) {
                const yPos = scrollY * speed;
                el.style.transform = `translateY(${yPos}px)`;
            }
        });
    },
    
    mouseMove(e) {
        document.querySelectorAll('[data-parallax-mouse]').forEach(el => {
            const speed = parseFloat(el.getAttribute('data-parallax-mouse')) || 0.05;
            const x = (e.clientX - window.innerWidth / 2) * speed;
            const y = (e.clientY - window.innerHeight / 2) * speed;
            
            el.style.transform = `translate(${x}px, ${y}px)`;
        });
    }
};

// ==================== 3D MODELS (THREE.JS) ====================
const Models3D = {
    scenes: {},
    
    init() {
        // Check if Three.js is loaded
        if (typeof THREE === 'undefined') {
            console.warn('Three.js not loaded');
            return;
        }
        
        document.querySelectorAll('[data-3d-model]').forEach(container => {
            const model = container.getAttribute('data-3d-model');
            this.createScene(container, model);
        });
    },
    
    createScene(container, model) {
        const width = container.offsetWidth;
        const height = container.offsetHeight || 300;
        
        // Scene
        const scene = new THREE.Scene();
        scene.background = null;
        
        // Camera
        const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        camera.position.z = 5;
        
        // Renderer
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(window.devicePixelRatio);
        container.appendChild(renderer.domElement);
        
        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        
        const pointLight = new THREE.PointLight(0x00ff88, 1, 100);
        pointLight.position.set(10, 10, 10);
        scene.add(pointLight);
        
        // Add model based on type
        let mesh;
        
        switch (model) {
            case 'lambda':
                mesh = this.createLambda();
                break;
            case 'crowbar':
                mesh = this.createCrowbar();
                break;
            case 'hev':
                mesh = this.createHEVSuit();
                break;
            case 'ct':
                mesh = this.createCT();
                break;
            case 'terrorist':
                mesh = this.createTerrorist();
                break;
            default:
                mesh = this.createCube();
        }
        
        scene.add(mesh);
        
        // Store scene reference
        const id = 'scene-' + Math.random().toString(36).substr(2, 9);
        this.scenes[id] = { scene, camera, renderer, mesh };
        
        // Animate
        const animate = () => {
            requestAnimationFrame(animate);
            mesh.rotation.y += 0.01;
            renderer.render(scene, camera);
        };
        animate();
        
        // Resize handler
        const resizeObserver = new ResizeObserver(() => {
            const w = container.offsetWidth;
            const h = container.offsetHeight || 300;
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
            renderer.setSize(w, h);
        });
        resizeObserver.observe(container);
    },
    
    createLambda() {
        // Lambda symbol (Half-Life logo)
        const shape = new THREE.Shape();
        shape.moveTo(0, 2);
        shape.lineTo(-1.5, -2);
        shape.lineTo(-0.5, -2);
        shape.lineTo(0, -0.5);
        shape.lineTo(0.5, -2);
        shape.lineTo(1.5, -2);
        shape.lineTo(0, 2);
        
        const geometry = new THREE.ExtrudeGeometry(shape, {
            depth: 0.5,
            bevelEnabled: true,
            bevelThickness: 0.1,
            bevelSize: 0.1
        });
        
        const material = new THREE.MeshStandardMaterial({
            color: 0xff6b00,
            metalness: 0.8,
            roughness: 0.2
        });
        
        return new THREE.Mesh(geometry, material);
    },
    
    createCrowbar() {
        // Simple crowbar shape
        const geometry = new THREE.BoxGeometry(0.2, 3, 0.2);
        const material = new THREE.MeshStandardMaterial({
            color: 0xff0000,
            metalness: 0.9,
            roughness: 0.3
        });
        
        return new THREE.Mesh(geometry, material);
    },
    
    createHEVSuit() {
        // Simplified HEV suit helmet
        const geometry = new THREE.SphereGeometry(1, 32, 32);
        const material = new THREE.MeshStandardMaterial({
            color: 0xff6b00,
            metalness: 0.7,
            roughness: 0.3,
            emissive: 0xff3300,
            emissiveIntensity: 0.2
        });
        
        return new THREE.Mesh(geometry, material);
    },
    
    createCT() {
        // CT helmet
        const geometry = new THREE.CylinderGeometry(0.8, 1, 1.5, 8);
        const material = new THREE.MeshStandardMaterial({
            color: 0x3366ff,
            metalness: 0.5,
            roughness: 0.5
        });
        
        return new THREE.Mesh(geometry, material);
    },
    
    createTerrorist() {
        // Terrorist head
        const geometry = new THREE.SphereGeometry(1, 32, 32);
        const material = new THREE.MeshStandardMaterial({
            color: 0xcc6600,
            metalness: 0.3,
            roughness: 0.7
        });
        
        return new THREE.Mesh(geometry, material);
    },
    
    createCube() {
        const geometry = new THREE.BoxGeometry(2, 2, 2);
        const material = new THREE.MeshStandardMaterial({
            color: 0x00ff88,
            metalness: 0.5,
            roughness: 0.5,
            wireframe: true
        });
        
        return new THREE.Mesh(geometry, material);
    }
};

// ==================== GLITCH EFFECT ====================
const GlitchEffect = {
    init() {
        document.querySelectorAll('.glitch').forEach(el => {
            el.setAttribute('data-text', el.textContent);
        });
    },
    
    trigger(element) {
        element.classList.add('glitching');
        setTimeout(() => element.classList.remove('glitching'), 500);
    }
};

// ==================== CURSOR EFFECTS ====================
const CustomCursor = {
    cursor: null,
    cursorDot: null,
    
    init() {
        if ('ontouchstart' in window) return; // Disable on touch devices
        
        this.cursor = document.createElement('div');
        this.cursor.className = 'custom-cursor';
        
        this.cursorDot = document.createElement('div');
        this.cursorDot.className = 'custom-cursor-dot';
        
        document.body.appendChild(this.cursor);
        document.body.appendChild(this.cursorDot);
        
        document.addEventListener('mousemove', (e) => this.move(e));
        
        // Hover effects
        document.querySelectorAll('a, button, .btn, [role="button"]').forEach(el => {
            el.addEventListener('mouseenter', () => this.grow());
            el.addEventListener('mouseleave', () => this.shrink());
        });
        
        this.addStyles();
    },
    
    move(e) {
        this.cursor.style.transform = `translate(${e.clientX - 20}px, ${e.clientY - 20}px)`;
        this.cursorDot.style.transform = `translate(${e.clientX - 4}px, ${e.clientY - 4}px)`;
    },
    
    grow() {
        this.cursor.classList.add('cursor-hover');
    },
    
    shrink() {
        this.cursor.classList.remove('cursor-hover');
    },
    
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .custom-cursor {
                width: 40px;
                height: 40px;
                border: 2px solid var(--neon-green);
                border-radius: 50%;
                position: fixed;
                pointer-events: none;
                z-index: 99999;
                transition: transform 0.1s ease, width 0.2s, height 0.2s, border-color 0.2s;
                mix-blend-mode: difference;
            }
            .custom-cursor.cursor-hover {
                width: 60px;
                height: 60px;
                border-color: var(--neon-orange);
                transform: translate(-30px, -30px) !important;
            }
            .custom-cursor-dot {
                width: 8px;
                height: 8px;
                background: var(--neon-green);
                border-radius: 50%;
                position: fixed;
                pointer-events: none;
                z-index: 99999;
                transition: transform 0.05s ease;
            }
            body:has(.custom-cursor) * {
                cursor: none !important;
            }
        `;
        document.head.appendChild(style);
    }
};

// ==================== TILT EFFECT ====================
const TiltEffect = {
    init() {
        document.querySelectorAll('[data-tilt]').forEach(el => {
            el.addEventListener('mousemove', (e) => this.tilt(e, el));
            el.addEventListener('mouseleave', () => this.reset(el));
        });
    },
    
    tilt(e, el) {
        const rect = el.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const maxTilt = parseFloat(el.getAttribute('data-tilt')) || 10;
        
        const rotateX = ((y - centerY) / centerY) * -maxTilt;
        const rotateY = ((x - centerX) / centerX) * maxTilt;
        
        el.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    },
    
    reset(el) {
        el.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
    }
};

// ==================== MAGNETIC BUTTONS ====================
const MagneticButtons = {
    init() {
        document.querySelectorAll('[data-magnetic]').forEach(btn => {
            btn.addEventListener('mousemove', (e) => this.move(e, btn));
            btn.addEventListener('mouseleave', () => this.reset(btn));
        });
    },
    
    move(e, btn) {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        
        const strength = parseFloat(btn.getAttribute('data-magnetic')) || 0.3;
        
        btn.style.transform = `translate(${x * strength}px, ${y * strength}px)`;
    },
    
    reset(btn) {
        btn.style.transform = '';
    }
};

// ==================== SMOOTH SCROLL ====================
const SmoothScroll = {
    init() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
};

// ==================== PROGRESS SCROLL INDICATOR ====================
const ScrollProgress = {
    bar: null,
    
    init() {
        this.bar = document.createElement('div');
        this.bar.className = 'scroll-progress';
        this.bar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            background: var(--gradient-primary);
            z-index: 10000;
            transition: width 0.1s ease;
        `;
        document.body.appendChild(this.bar);
        
        window.addEventListener('scroll', () => this.update());
    },
    
    update() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = (scrollTop / docHeight) * 100;
        
        this.bar.style.width = `${progress}%`;
    }
};

// ==================== IMAGE HOVER ZOOM ====================
const ImageZoom = {
    init() {
        document.querySelectorAll('[data-zoom]').forEach(img => {
            img.style.cursor = 'zoom-in';
            img.addEventListener('click', () => this.show(img));
        });
    },
    
    show(img) {
        const overlay = document.createElement('div');
        overlay.className = 'image-zoom-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 100000;
            cursor: zoom-out;
            animation: fadeIn 0.3s ease;
        `;
        
        const clone = img.cloneNode();
        clone.style.cssText = `
            max-width: 90vw;
            max-height: 90vh;
            object-fit: contain;
            animation: scaleIn 0.3s ease;
        `;
        
        overlay.appendChild(clone);
        document.body.appendChild(overlay);
        
        overlay.addEventListener('click', () => {
            overlay.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => overlay.remove(), 300);
        });
    }
};

// ==================== INITIALIZE EFFECTS ====================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize based on page requirements
    if (document.getElementById('particles-bg')) {
        Particles.init('particles-bg');
    }
    
    if (document.getElementById('matrix-bg')) {
        MatrixRain.init('matrix-bg');
    }
    
    Parallax.init();
    GlitchEffect.init();
    TiltEffect.init();
    MagneticButtons.init();
    SmoothScroll.init();
    ScrollProgress.init();
    ImageZoom.init();
    
    // 3D models require Three.js
    if (typeof THREE !== 'undefined') {
        Models3D.init();
    }
    
    // Custom cursor on desktop
    if (window.innerWidth > 1024) {
        // CustomCursor.init(); // Disabled by default, uncomment to enable
    }
});

// Export for global use
window.Effects = {
    Particles,
    MatrixRain,
    Models3D,
    CustomCursor,
    TiltEffect
};

// ==================== FASE 3: CONFETTI SYSTEM ====================
const ConfettiSystem = {
    container: null,
    colors: ['#ef4444', '#3b82f6', '#10b981', '#fbbf24', '#8b5cf6', '#ec4899', '#f97316', '#06b6d4'],
    shapes: ['square', 'circle', 'triangle', 'ribbon'],
    
    trigger(options = {}) {
        const count = options.count || 150;
        const duration = options.duration || 3000;
        const spread = options.spread || window.innerWidth;
        
        // Create container
        this.container = document.createElement('div');
        this.container.className = 'confetti-container';
        document.body.appendChild(this.container);
        
        // Create confetti pieces
        for (let i = 0; i < count; i++) {
            const confetti = document.createElement('div');
            const shape = this.shapes[Math.floor(Math.random() * this.shapes.length)];
            const color = this.colors[Math.floor(Math.random() * this.colors.length)];
            
            confetti.className = `confetti confetti-${shape}`;
            confetti.style.left = Math.random() * spread + 'px';
            confetti.style.backgroundColor = shape !== 'triangle' ? color : 'transparent';
            confetti.style.borderBottomColor = shape === 'triangle' ? color : 'transparent';
            confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
            confetti.style.animationDelay = Math.random() * 0.5 + 's';
            
            this.container.appendChild(confetti);
        }
        
        // Cleanup
        setTimeout(() => {
            this.container?.remove();
        }, duration + 1000);
    },
    
    burst(x, y, options = {}) {
        const count = options.count || 30;
        
        for (let i = 0; i < count; i++) {
            const confetti = document.createElement('div');
            const color = this.colors[Math.floor(Math.random() * this.colors.length)];
            const angle = (Math.PI * 2 / count) * i;
            const velocity = Math.random() * 100 + 50;
            const destX = x + Math.cos(angle) * velocity;
            const destY = y + Math.sin(angle) * velocity;
            
            confetti.className = 'confetti confetti-circle';
            confetti.style.cssText = `
                position: fixed;
                left: ${x}px;
                top: ${y}px;
                width: 10px;
                height: 10px;
                background: ${color};
                border-radius: 50%;
                pointer-events: none;
                z-index: 9999;
            `;
            
            document.body.appendChild(confetti);
            
            // Animate
            confetti.animate([
                { transform: 'translate(0, 0) scale(1)', opacity: 1 },
                { transform: `translate(${destX - x}px, ${destY - y}px) scale(0)`, opacity: 0 }
            ], {
                duration: 800,
                easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
            }).onfinish = () => confetti.remove();
        }
    }
};

// Global trigger function
function triggerConfetti(options) {
    ConfettiSystem.trigger(options);
}

function confettiBurst(x, y, options) {
    ConfettiSystem.burst(x, y, options);
}

// ==================== FASE 3: FIREWORKS SYSTEM ====================
const FireworksSystem = {
    colors: ['#fbbf24', '#ef4444', '#3b82f6', '#10b981', '#8b5cf6', '#ec4899'],
    
    launch(options = {}) {
        const count = options.count || 5;
        const delay = options.delay || 300;
        
        for (let i = 0; i < count; i++) {
            setTimeout(() => {
                const x = Math.random() * (window.innerWidth - 200) + 100;
                const y = Math.random() * (window.innerHeight / 2) + 100;
                this.explode(x, y);
            }, i * delay);
        }
    },
    
    explode(x, y) {
        const color = this.colors[Math.floor(Math.random() * this.colors.length)];
        const particles = 12;
        
        // Create explosion container
        const firework = document.createElement('div');
        firework.className = 'firework';
        firework.style.cssText = `left: ${x}px; top: ${y}px;`;
        
        // Create particles
        for (let i = 0; i < particles; i++) {
            const particle = document.createElement('div');
            particle.className = 'firework-particle';
            particle.style.backgroundColor = color;
            
            const angle = (Math.PI * 2 / particles) * i;
            const distance = Math.random() * 30 + 50;
            particle.style.setProperty('--particle-direction', 
                `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px)`);
            
            firework.appendChild(particle);
        }
        
        document.body.appendChild(firework);
        
        // Play sound if available
        if (typeof SoundEffects !== 'undefined') {
            SoundEffects.play('firework');
        }
        
        // Cleanup
        setTimeout(() => firework.remove(), 1500);
    }
};

function launchFireworks(options) {
    FireworksSystem.launch(options);
}

// ==================== FASE 3: ACHIEVEMENT UNLOCK ====================
const AchievementSystem = {
    queue: [],
    isShowing: false,
    
    unlock(achievement) {
        this.queue.push(achievement);
        if (!this.isShowing) {
            this.showNext();
        }
    },
    
    showNext() {
        if (this.queue.length === 0) {
            this.isShowing = false;
            return;
        }
        
        this.isShowing = true;
        const achievement = this.queue.shift();
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'achievement-notification';
        notification.innerHTML = `
            <div class="badge-icon">
                <svg width="64" height="64" viewBox="0 0 24 24">
                    <use href="/static/images/icons.svg#icon-${achievement.icon || 'achievement-unlock'}"></use>
                </svg>
            </div>
            <div class="badge-info">
                <span class="badge-title">Başarım Açıldı!</span>
                <span class="badge-name">${achievement.name}</span>
                <span class="badge-desc">${achievement.description || ''}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Trigger confetti burst
        setTimeout(() => {
            const rect = notification.getBoundingClientRect();
            ConfettiSystem.burst(rect.left + 32, rect.top + 40, { count: 20 });
        }, 300);
        
        // Play sound
        if (typeof SoundEffects !== 'undefined') {
            SoundEffects.play('achievement');
        }
        
        // Auto dismiss
        setTimeout(() => {
            notification.style.animation = 'slideInRight 0.3s ease-out reverse forwards';
            setTimeout(() => {
                notification.remove();
                this.showNext();
            }, 300);
        }, achievement.duration || 5000);
    }
};

function unlockAchievement(achievement) {
    AchievementSystem.unlock(achievement);
}

// ==================== FASE 3: LEVEL UP ANIMATION ====================
const LevelUpSystem = {
    show(level, options = {}) {
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'level-up-container';
        overlay.style.display = 'flex';
        
        overlay.innerHTML = `
            <div class="level-up-rays">
                <svg viewBox="0 0 300 300" style="width: 100%; height: 100%;">
                    ${[...Array(12)].map((_, i) => 
                        `<line x1="150" y1="150" x2="150" y2="0" stroke="#fbbf24" stroke-width="2" opacity="0.3" transform="rotate(${i * 30} 150 150)"/>`
                    ).join('')}
                </svg>
            </div>
            <div class="level-up-badge">
                <svg width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="1.5">
                    <use href="/static/images/icons.svg#icon-level-up"></use>
                </svg>
            </div>
            <div class="level-up-number">${level}</div>
            <div class="level-up-text">${options.text || 'SEVİYE ATLADIN!'}</div>
        `;
        
        document.body.appendChild(overlay);
        
        // Trigger effects
        launchFireworks({ count: 3 });
        triggerConfetti({ count: 100 });
        
        // Play sound
        if (typeof SoundEffects !== 'undefined') {
            SoundEffects.play('levelup');
        }
        
        // Auto dismiss
        setTimeout(() => {
            overlay.style.opacity = '0';
            overlay.style.transition = 'opacity 0.5s';
            setTimeout(() => overlay.remove(), 500);
        }, options.duration || 4000);
    }
};

function showLevelUp(level, options) {
    LevelUpSystem.show(level, options);
}

// ==================== FASE 3: VICTORY CELEBRATION ====================
const VictorySystem = {
    show(options = {}) {
        const overlay = document.createElement('div');
        overlay.className = 'victory-container';
        overlay.style.cssText = `
            display: flex;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.85);
            z-index: 10000;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            animation: fadeIn 0.3s ease;
        `;
        
        overlay.innerHTML = `
            <svg class="victory-crown" width="150" height="150" viewBox="0 0 24 24">
                <use href="/static/images/icons.svg#icon-victory"></use>
            </svg>
            <h1 style="color: #fbbf24; font-size: 48px; font-weight: 900; margin: 20px 0 10px 0; text-transform: uppercase; letter-spacing: 4px; animation: fadeInUp 0.5s ease-out 0.3s forwards; opacity: 0;">${options.title || 'ZAFER!'}</h1>
            <p style="color: rgba(255,255,255,0.7); font-size: 18px; animation: fadeInUp 0.5s ease-out 0.5s forwards; opacity: 0;">${options.subtitle || 'Tebrikler, kazandınız!'}</p>
        `;
        
        document.body.appendChild(overlay);
        
        // Effects
        setTimeout(() => {
            launchFireworks({ count: 7, delay: 200 });
            triggerConfetti({ count: 200 });
        }, 500);
        
        // Dismiss on click
        overlay.addEventListener('click', () => {
            overlay.style.animation = 'fadeIn 0.3s ease reverse';
            setTimeout(() => overlay.remove(), 300);
        });
        
        // Auto dismiss
        if (options.duration !== false) {
            setTimeout(() => {
                overlay.click();
            }, options.duration || 6000);
        }
    }
};

function showVictory(options) {
    VictorySystem.show(options);
}

// ==================== FASE 3: THEME SYSTEM ====================
const ThemeSystem = {
    currentTheme: 'dark',
    
    init() {
        // Load saved theme
        const saved = localStorage.getItem('agtr-theme') || 'dark';
        this.setTheme(saved, false);
    },
    
    toggle() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme, true);
    },
    
    setTheme(theme, animate = true) {
        const html = document.documentElement;
        const body = document.body;
        
        if (animate) {
            // Add transition class
            html.setAttribute('data-theme-transitioning', '');
            
            // Optional: Create ripple effect from toggle button
            const btn = document.querySelector('.theme-toggle-btn');
            if (btn) {
                const rect = btn.getBoundingClientRect();
                const x = rect.left + rect.width / 2;
                const y = rect.top + rect.height / 2;
                
                const ripple = document.createElement('div');
                ripple.className = `theme-ripple theme-ripple-${theme}`;
                ripple.style.cssText = `
                    left: ${x}px;
                    top: ${y}px;
                    width: ${Math.max(window.innerWidth, window.innerHeight) * 2}px;
                    height: ${Math.max(window.innerWidth, window.innerHeight) * 2}px;
                `;
                
                document.body.appendChild(ripple);
                setTimeout(() => ripple.remove(), 800);
            }
            
            // Remove transition class after animation
            setTimeout(() => {
                html.removeAttribute('data-theme-transitioning');
            }, 300);
        }
        
        // Apply theme
        html.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        
        // Save preference
        localStorage.setItem('agtr-theme', theme);
        
        // Update toggle buttons
        document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
            const sunIcon = btn.querySelector('.icon-sun');
            const moonIcon = btn.querySelector('.icon-moon');
            
            if (theme === 'dark') {
                if (sunIcon) sunIcon.style.display = 'none';
                if (moonIcon) moonIcon.style.display = 'block';
            } else {
                if (sunIcon) sunIcon.style.display = 'block';
                if (moonIcon) moonIcon.style.display = 'none';
            }
        });
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
    },
    
    getTheme() {
        return this.currentTheme;
    }
};

// Global theme functions
function toggleTheme() {
    ThemeSystem.toggle();
}

function setTheme(theme) {
    ThemeSystem.setTheme(theme);
}

function getTheme() {
    return ThemeSystem.getTheme();
}

// ==================== FASE 3: SPLASH SCREEN ====================
const SplashScreen = {
    hide(delay = 2000) {
        const splash = document.getElementById('splash-screen');
        if (!splash) return;
        
        setTimeout(() => {
            splash.classList.add('splash-exit');
            setTimeout(() => splash.remove(), 500);
        }, delay);
    },
    
    show() {
        if (document.getElementById('splash-screen')) return;
        
        const splash = document.createElement('div');
        splash.id = 'splash-screen';
        splash.className = 'splash-screen';
        splash.innerHTML = `
            <div class="splash-logo">
                <img src="/static/images/logo.svg" alt="AGTR" style="width: 120px; height: 120px;">
            </div>
            <h1 class="splash-title" style="font-size: 28px; font-weight: 700; color: var(--text-primary); margin-top: 20px;">AGTR Merkezi</h1>
            <div class="splash-progress-bar">
                <div class="splash-progress-fill"></div>
            </div>
        `;
        
        document.body.prepend(splash);
    }
};

// ==================== FASE 3: SPARKLE EFFECT ====================
function addSparkles(element, count = 5) {
    const rect = element.getBoundingClientRect();
    
    for (let i = 0; i < count; i++) {
        const sparkle = document.createElement('div');
        sparkle.className = 'sparkle';
        sparkle.style.cssText = `
            position: fixed;
            left: ${rect.left + Math.random() * rect.width}px;
            top: ${rect.top + Math.random() * rect.height}px;
            width: 10px;
            height: 10px;
            pointer-events: none;
            z-index: 9999;
        `;
        sparkle.innerHTML = `
            <svg viewBox="0 0 24 24" fill="#fbbf24" style="width: 100%; height: 100%;">
                <use href="/static/images/icons.svg#icon-sparkles"></use>
            </svg>
        `;
        
        document.body.appendChild(sparkle);
        
        setTimeout(() => sparkle.remove(), 1500);
    }
}

// ==================== INITIALIZE FASE 3 EFFECTS ====================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme system
    ThemeSystem.init();
    
    // Hide splash screen if exists
    SplashScreen.hide();
});

// Export FASE 3 systems
window.Confetti = ConfettiSystem;
window.Fireworks = FireworksSystem;
window.Achievement = AchievementSystem;
window.LevelUp = LevelUpSystem;
window.Victory = VictorySystem;
window.Theme = ThemeSystem;
window.Splash = SplashScreen;
