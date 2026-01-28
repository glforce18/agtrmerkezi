/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Modern Dark Mode Color Palette
        primary: {
          DEFAULT: '#FF6B35',
          dark: '#E85D2C',
          light: '#FF8A5C',
        },
        dark: {
          bg: '#0F1419',        // Main background
          card: '#1A1F29',      // Card background
          elevated: '#242933',  // Elevated elements
          border: '#2F3640',    // Borders
          hover: '#2A3038',     // Hover states
        },
        text: {
          primary: '#E8EAED',   // Main text
          secondary: '#9AA0A6', // Secondary text
          muted: '#5F6368',     // Muted text
        },
        status: {
          success: '#10B981',
          warning: '#F59E0B',
          error: '#EF4444',
          info: '#3B82F6',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'Monaco', 'monospace'],
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.3)',
        'card-hover': '0 4px 12px 0 rgba(0, 0, 0, 0.4)',
        'elevated': '0 2px 8px 0 rgba(0, 0, 0, 0.35)',
      },
      borderRadius: {
        'card': '12px',
      },
    },
  },
  plugins: [],
}
