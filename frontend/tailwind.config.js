/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // AGTR Merkezi Brand Colors
        brand: {
          50: '#f0f4ff',
          100: '#e0e9ff',
          200: '#c7d6fe',
          300: '#a5b9fc',
          400: '#818cf8',
          500: '#6366f1', // Primary
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
        // Gaming accent colors
        gaming: {
          red: '#ef4444',
          orange: '#f97316',
          yellow: '#eab308',
          green: '#10b981',
          cyan: '#06b6d4',
          purple: '#8b5cf6',
          pink: '#ec4899',
        },
        // Dark theme specific
        dark: {
          bg: '#0f172a',      // Slate 900
          card: '#1e293b',    // Slate 800
          border: '#334155',  // Slate 700
          hover: '#475569',   // Slate 600
        },
        // Light theme specific
        light: {
          bg: '#ffffff',
          card: '#f8fafc',    // Slate 50
          border: '#e2e8f0',  // Slate 200
          hover: '#cbd5e1',   // Slate 300
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Orbitron', 'sans-serif'], // Gaming font
        mono: ['Fira Code', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '100': '25rem',
        '112': '28rem',
        '128': '32rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'fade-out': 'fadeOut 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.5s ease-out',
        'slide-left': 'slideLeft 0.5s ease-out',
        'slide-right': 'slideRight 0.5s ease-out',
        'scale-up': 'scaleUp 0.3s ease-out',
        'bounce-slow': 'bounce 2s infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 3s linear infinite',
        'ping-slow': 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
        'gradient': 'gradient 15s ease infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideLeft: {
          '0%': { transform: 'translateX(20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideRight: {
          '0%': { transform: 'translateX(-20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        scaleUp: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(99, 102, 241, 0.5)' },
          '100%': { boxShadow: '0 0 40px rgba(99, 102, 241, 0.8), 0 0 60px rgba(99, 102, 241, 0.4)' },
        },
      },
      boxShadow: {
        'glow-sm': '0 0 10px rgba(99, 102, 241, 0.3)',
        'glow': '0 0 20px rgba(99, 102, 241, 0.5)',
        'glow-lg': '0 0 30px rgba(99, 102, 241, 0.6)',
        'neon': '0 0 5px theme(colors.brand.400), 0 0 20px theme(colors.brand.500)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-gaming': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'gradient-cyber': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'gradient-matrix': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: [
      {
        // Default AGTR Dark Theme - Clean Gaming
        agtr_dark: {
          "primary": "#f97316",           // Orange - HL inspired
          "primary-focus": "#ea580c",
          "primary-content": "#ffffff",

          "secondary": "#8b5cf6",
          "secondary-focus": "#7c3aed",
          "secondary-content": "#ffffff",

          "accent": "#06b6d4",
          "accent-focus": "#0891b2",
          "accent-content": "#ffffff",

          "neutral": "#1e293b",
          "neutral-focus": "#0f172a",
          "neutral-content": "#f1f5f9",

          "base-100": "#0a0f1a",           // Darker background
          "base-200": "#111827",
          "base-300": "#1f2937",
          "base-content": "#f1f5f9",

          "info": "#3b82f6",
          "success": "#10b981",
          "warning": "#f59e0b",
          "error": "#ef4444",

          "--rounded-box": "0.75rem",
          "--rounded-btn": "0.5rem",
          "--rounded-badge": "1rem",
          "--animation-btn": "0.2s",
          "--animation-input": "0.15s",
          "--btn-text-case": "uppercase",
          "--btn-focus-scale": "0.97",
          "--border-btn": "2px",
          "--tab-border": "2px",
          "--tab-radius": "0.5rem",
        },
        // Cyberpunk Neon Theme
        agtr_cyber: {
          "primary": "#ff00ff",           // Magenta
          "primary-focus": "#cc00cc",
          "primary-content": "#000000",

          "secondary": "#00ffff",          // Cyan
          "secondary-focus": "#00cccc",
          "secondary-content": "#000000",

          "accent": "#ffff00",             // Yellow
          "accent-focus": "#cccc00",
          "accent-content": "#000000",

          "neutral": "#1a1a2e",
          "neutral-focus": "#0f0f1a",
          "neutral-content": "#eaeaea",

          "base-100": "#0a0a14",
          "base-200": "#12121f",
          "base-300": "#1a1a2e",
          "base-content": "#eaeaea",

          "info": "#00d4ff",
          "success": "#00ff88",
          "warning": "#ffcc00",
          "error": "#ff0055",

          "--rounded-box": "0",
          "--rounded-btn": "0",
          "--rounded-badge": "0",
          "--animation-btn": "0.15s",
          "--animation-input": "0.1s",
          "--btn-text-case": "uppercase",
          "--btn-focus-scale": "1",
          "--border-btn": "2px",
        },
        // Half-Life Orange Theme
        agtr_halflife: {
          "primary": "#ff6600",           // HL Orange
          "primary-focus": "#cc5200",
          "primary-content": "#ffffff",

          "secondary": "#4a9c2d",          // HL Green
          "secondary-focus": "#3d8024",
          "secondary-content": "#ffffff",

          "accent": "#2d7a9c",
          "accent-focus": "#246580",
          "accent-content": "#ffffff",

          "neutral": "#2a2a2a",
          "neutral-focus": "#1a1a1a",
          "neutral-content": "#e0e0e0",

          "base-100": "#121212",
          "base-200": "#1a1a1a",
          "base-300": "#2a2a2a",
          "base-content": "#e0e0e0",

          "info": "#3498db",
          "success": "#4a9c2d",
          "warning": "#ff6600",
          "error": "#c0392b",

          "--rounded-box": "0.25rem",
          "--rounded-btn": "0.25rem",
          "--rounded-badge": "0.25rem",
          "--animation-btn": "0.2s",
          "--animation-input": "0.15s",
          "--btn-text-case": "uppercase",
          "--btn-focus-scale": "0.98",
          "--border-btn": "2px",
        },
        // Counter-Strike Blue Theme
        agtr_cs: {
          "primary": "#4a90d9",           // CS Blue
          "primary-focus": "#3a7bc0",
          "primary-content": "#ffffff",

          "secondary": "#c9a227",          // CS Gold
          "secondary-focus": "#a8871f",
          "secondary-content": "#000000",

          "accent": "#8b4513",
          "accent-focus": "#723a10",
          "accent-content": "#ffffff",

          "neutral": "#1c2833",
          "neutral-focus": "#0d1318",
          "neutral-content": "#ecf0f1",

          "base-100": "#0d1318",
          "base-200": "#1c2833",
          "base-300": "#2c3e50",
          "base-content": "#ecf0f1",

          "info": "#4a90d9",
          "success": "#27ae60",
          "warning": "#c9a227",
          "error": "#e74c3c",

          "--rounded-box": "0.5rem",
          "--rounded-btn": "0.375rem",
          "--rounded-badge": "1rem",
          "--animation-btn": "0.2s",
          "--btn-text-case": "uppercase",
          "--btn-focus-scale": "0.98",
          "--border-btn": "1px",
        },
        // Light theme
        agtr_light: {
          "primary": "#f97316",
          "primary-focus": "#ea580c",
          "primary-content": "#ffffff",

          "secondary": "#8b5cf6",
          "secondary-focus": "#7c3aed",
          "secondary-content": "#ffffff",

          "accent": "#06b6d4",
          "accent-focus": "#0891b2",
          "accent-content": "#ffffff",

          "neutral": "#64748b",
          "neutral-focus": "#475569",
          "neutral-content": "#ffffff",

          "base-100": "#ffffff",
          "base-200": "#f8fafc",
          "base-300": "#e2e8f0",
          "base-content": "#0f172a",

          "info": "#3b82f6",
          "success": "#10b981",
          "warning": "#f59e0b",
          "error": "#ef4444",

          "--rounded-box": "0.75rem",
          "--rounded-btn": "0.5rem",
          "--rounded-badge": "1rem",
          "--animation-btn": "0.2s",
          "--animation-input": "0.15s",
          "--btn-text-case": "uppercase",
          "--btn-focus-scale": "0.97",
          "--border-btn": "2px",
        },
      },
      // Include built-in gaming themes
      "synthwave",
      "cyberpunk",
      "halloween",
      "forest",
      "black",
      "luxury",
      "dracula",
    ],
    darkTheme: "agtr_dark",
    base: true,
    styled: true,
    utils: true,
    logs: false,
  },
}
