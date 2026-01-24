/**
 * Design System Constants
 * AGTR Merkezi v7.0 - Modern UI/UX
 */

// Brand Colors
export const BRAND_COLORS = {
  primary: '#6366f1',      // Indigo 500
  secondary: '#8b5cf6',    // Purple 500
  accent: '#ec4899',       // Pink 500
  success: '#10b981',      // Green 500
  warning: '#f59e0b',      // Amber 500
  error: '#ef4444',        // Red 500
  info: '#3b82f6',         // Blue 500
}

// Gaming Colors
export const GAMING_COLORS = {
  red: '#ef4444',
  orange: '#f97316',
  yellow: '#eab308',
  green: '#10b981',
  cyan: '#06b6d4',
  purple: '#8b5cf6',
  pink: '#ec4899',
}

// Dark Theme
export const DARK_THEME = {
  bg: '#0f172a',          // Slate 900
  card: '#1e293b',        // Slate 800
  border: '#334155',      // Slate 700
  hover: '#475569',       // Slate 600
  text: '#f1f5f9',        // Slate 100
}

// Light Theme
export const LIGHT_THEME = {
  bg: '#ffffff',
  card: '#f8fafc',        // Slate 50
  border: '#e2e8f0',      // Slate 200
  hover: '#cbd5e1',       // Slate 300
  text: '#0f172a',        // Slate 900
}

// Spacing Scale (based on 4px)
export const SPACING = {
  xs: '0.25rem',   // 4px
  sm: '0.5rem',    // 8px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem',      // 32px
  '2xl': '3rem',   // 48px
  '3xl': '4rem',   // 64px
  '4xl': '6rem',   // 96px
}

// Typography Scale
export const TYPOGRAPHY = {
  // Font Families - Turkish character support
  fontSans: 'Inter, system-ui, sans-serif',
  fontDisplay: 'Rajdhani, Poppins, sans-serif',
  fontMono: 'JetBrains Mono, Fira Code, monospace',

  // Font Sizes
  xs: '0.75rem',    // 12px
  sm: '0.875rem',   // 14px
  base: '1rem',     // 16px
  lg: '1.125rem',   // 18px
  xl: '1.25rem',    // 20px
  '2xl': '1.5rem',  // 24px
  '3xl': '1.875rem',// 30px
  '4xl': '2.25rem', // 36px
  '5xl': '3rem',    // 48px
  '6xl': '3.75rem', // 60px
  '7xl': '4.5rem',  // 72px
  '8xl': '6rem',    // 96px
  '9xl': '8rem',    // 128px

  // Font Weights
  thin: '100',
  extralight: '200',
  light: '300',
  normal: '400',
  medium: '500',
  semibold: '600',
  bold: '700',
  extrabold: '800',
  black: '900',

  // Line Heights
  tight: '1.25',
  snug: '1.375',
  normal: '1.5',
  relaxed: '1.625',
  loose: '2',
}

// Border Radius
export const RADIUS = {
  none: '0',
  sm: '0.125rem',   // 2px
  default: '0.25rem', // 4px
  md: '0.375rem',   // 6px
  lg: '0.5rem',     // 8px
  xl: '0.75rem',    // 12px
  '2xl': '1rem',    // 16px
  '3xl': '1.5rem',  // 24px
  full: '9999px',
}

// Shadows
export const SHADOWS = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  default: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
  none: 'none',

  // Glow effects
  glowSm: '0 0 10px rgba(99, 102, 241, 0.3)',
  glow: '0 0 20px rgba(99, 102, 241, 0.5)',
  glowLg: '0 0 30px rgba(99, 102, 241, 0.6)',
  neon: '0 0 5px #6366f1, 0 0 20px #6366f1',
}

// Z-Index Scale
export const Z_INDEX = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
}

// Breakpoints (matches Tailwind defaults)
export const BREAKPOINTS = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
}

// Transition Durations
export const TRANSITIONS = {
  fast: '150ms',
  base: '300ms',
  slow: '500ms',
  slower: '700ms',
}

// Animation Easings
export const EASINGS = {
  linear: 'linear',
  in: 'cubic-bezier(0.4, 0, 1, 1)',
  out: 'cubic-bezier(0, 0, 0.2, 1)',
  inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
}

// Component Sizes
export const SIZES = {
  button: {
    xs: { padding: '0.25rem 0.5rem', fontSize: '0.75rem' },
    sm: { padding: '0.5rem 0.75rem', fontSize: '0.875rem' },
    md: { padding: '0.5rem 1rem', fontSize: '1rem' },
    lg: { padding: '0.75rem 1.5rem', fontSize: '1.125rem' },
    xl: { padding: '1rem 2rem', fontSize: '1.25rem' },
  },
  input: {
    sm: { padding: '0.5rem', fontSize: '0.875rem' },
    md: { padding: '0.75rem', fontSize: '1rem' },
    lg: { padding: '1rem', fontSize: '1.125rem' },
  },
  avatar: {
    xs: '1.5rem',   // 24px
    sm: '2rem',     // 32px
    md: '2.5rem',   // 40px
    lg: '3rem',     // 48px
    xl: '4rem',     // 64px
    '2xl': '6rem',  // 96px
  },
}

// Icon Sizes
export const ICON_SIZES = {
  xs: 12,
  sm: 16,
  md: 20,
  lg: 24,
  xl: 32,
  '2xl': 48,
}

// Status Colors
export const STATUS_COLORS = {
  online: '#10b981',    // Green
  offline: '#6b7280',   // Gray
  away: '#f59e0b',      // Amber
  busy: '#ef4444',      // Red
}

// Server Status Colors
export const SERVER_STATUS = {
  online: '#10b981',
  offline: '#6b7280',
  starting: '#3b82f6',
  stopping: '#f59e0b',
  error: '#ef4444',
  maintenance: '#8b5cf6',
}

// Badge Variants
export const BADGE_VARIANTS = {
  default: { bg: BRAND_COLORS.primary, text: '#ffffff' },
  success: { bg: BRAND_COLORS.success, text: '#ffffff' },
  warning: { bg: BRAND_COLORS.warning, text: '#ffffff' },
  error: { bg: BRAND_COLORS.error, text: '#ffffff' },
  info: { bg: BRAND_COLORS.info, text: '#ffffff' },
  secondary: { bg: BRAND_COLORS.secondary, text: '#ffffff' },
}

// Social Media Colors
export const SOCIAL_COLORS = {
  steam: '#171a21',
  discord: '#5865F2',
  google: '#4285F4',
  youtube: '#FF0000',
  twitter: '#1DA1F2',
  facebook: '#1877F2',
  instagram: '#E4405F',
}

// Gradient Presets
export const GRADIENTS = {
  gaming: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  cyber: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  matrix: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  sunset: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  ocean: 'linear-gradient(135deg, #2e3192 0%, #1bffff 100%)',
  purple: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
}

// Export all as default
export default {
  BRAND_COLORS,
  GAMING_COLORS,
  DARK_THEME,
  LIGHT_THEME,
  SPACING,
  TYPOGRAPHY,
  RADIUS,
  SHADOWS,
  Z_INDEX,
  BREAKPOINTS,
  TRANSITIONS,
  EASINGS,
  SIZES,
  ICON_SIZES,
  STATUS_COLORS,
  SERVER_STATUS,
  BADGE_VARIANTS,
  SOCIAL_COLORS,
  GRADIENTS,
}
