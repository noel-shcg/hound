import { useState, useEffect } from 'react';
import { getThemeColors, designTokens } from '../styles/design-tokens';

export const useTheme = () => {
  const [theme, setTheme] = useState<'day' | 'evening'>('day');

  useEffect(() => {
    // Check current time and set theme
    const updateTheme = () => {
      const now = new Date();
      const hour = now.getHours();
      
      // Default theme transition times (can be configured)
      const dayStart = 7; // 7 AM
      const eveningStart = 19; // 7 PM
      
      if (hour >= dayStart && hour < eveningStart) {
        setTheme('day');
      } else {
        setTheme('evening');
      }
    };

    updateTheme();
    const interval = setInterval(updateTheme, 60000); // Check every minute

    return () => clearInterval(interval);
  }, []);

  const colors = getThemeColors(theme);

  return { theme, colors, designTokens };
};
