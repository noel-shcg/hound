export const designTokens = {
  // Colors - Day theme
  colors: {
    day: {
      background: '#1a1a2e',
      surface: '#16213e',
      surfaceLight: '#1f2a4a',
      primary: '#4A90E2',
      secondary: '#E94560',
      text: '#ffffff',
      textSecondary: '#a0a0a0',
      border: '#2a3a5a',
      success: '#4caf50',
      warning: '#ff9800',
      error: '#f44336',
    },
    evening: {
      background: '#0f0f1a',
      surface: '#1a1a2e',
      surfaceLight: '#252540',
      primary: '#5b9ce0',
      secondary: '#f5566e',
      text: '#e0e0e0',
      textSecondary: '#808080',
      border: '#1f1f3a',
      success: '#66bb6a',
      warning: '#ffa726',
      error: '#ef5350',
    },
  },

  // Typography
  typography: {
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '2rem',
      '4xl': '2.5rem',
      '5xl': '3rem',
      '6xl': '4rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
  },

  // Spacing
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
    '3xl': '4rem',
  },

  // Border radius
  borderRadius: {
    sm: '0.25rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
    '2xl': '1.5rem',
    full: '9999px',
  },

  // Shadows
  shadow: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
  },

  // Transitions
  transition: {
    fast: '150ms ease-in-out',
    base: '300ms ease-in-out',
    slow: '500ms ease-in-out',
  },
};

export type Theme = 'day' | 'evening';

export const getThemeColors = (theme: Theme) => designTokens.colors[theme];
