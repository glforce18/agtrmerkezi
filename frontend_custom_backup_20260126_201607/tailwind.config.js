/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Half-Life / Gaming inspired colors
        lambda: {
          orange: '#FF6B35',
          'orange-dark': '#E85D2C',
          'orange-light': '#FF7F50',
        },
        hev: {
          cyan: '#00F5FF',
          'cyan-dark': '#00D4E6',
          'cyan-light': '#33F7FF',
        },
        xen: {
          purple: '#B537F2',
          'purple-dark': '#9B2DD9',
          'purple-light': '#C65FF5',
        },
        combine: {
          red: '#FF0040',
          green: '#39FF14',
          yellow: '#FFFD37',
          blue: '#00D9FF',
        },
        cyber: {
          black: '#0a0a0a',
          dark: '#0f0f0f',
          darker: '#050505',
          panel: '#121212',
          elevated: '#1a1a1a',
          border: '#1f1f1f',
        },
        text: {
          primary: '#E0E0E0',
          secondary: '#A0A0A0',
          muted: '#707070',
        }
      },
      fontFamily: {
        'lambda': ['Orbitron', 'sans-serif'],        // Half-Life UI style
        'hev': ['"Share Tech Mono"', 'monospace'],   // HEV Terminal style
        'body': ['Electrolize', 'sans-serif'],        // Body text - futuristic
        'sans': ['Inter', 'sans-serif'],              // Fallback
      },
      backgroundImage: {
        'grid-pattern': 'linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)',
        'lambda-gradient': 'linear-gradient(135deg, #FF6B35, #00F5FF)',
        'xen-gradient': 'linear-gradient(135deg, #B537F2, #FF006E)',
        'combine-gradient': 'linear-gradient(135deg, #FF0040, #39FF14)',
      },
      boxShadow: {
        'neon-orange': '0 0 20px rgba(255, 107, 53, 0.5)',
        'neon-cyan': '0 0 20px rgba(0, 245, 255, 0.5)',
        'neon-purple': '0 0 20px rgba(181, 55, 242, 0.5)',
        'neon-green': '0 0 20px rgba(57, 255, 20, 0.5)',
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'scan': 'scan 8s linear infinite',
        'glitch': 'glitch 1s linear infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 5px currentColor, 0 0 10px currentColor' },
          '50%': { boxShadow: '0 0 20px currentColor, 0 0 40px currentColor' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        glitch: {
          '0%, 100%': { transform: 'translate(0)' },
          '20%': { transform: 'translate(-2px, 2px)' },
          '40%': { transform: 'translate(-2px, -2px)' },
          '60%': { transform: 'translate(2px, 2px)' },
          '80%': { transform: 'translate(2px, -2px)' },
        },
      },
    },
  },
  plugins: [],
}
