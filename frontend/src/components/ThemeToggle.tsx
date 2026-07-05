/**
 * Theme Toggle Component
 * Switch between light and dark modes
 */

import React, { useState, useEffect } from 'react';
import '../styles/theme-toggle.css';

type Theme = 'light' | 'dark' | 'system';

interface ThemeToggleProps {
  onThemeChange?: (theme: Theme) => void;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ onThemeChange }) => {
  const [theme, setTheme] = useState<Theme>('system');
  const [isOpen, setIsOpen] = useState(false);

  // Load saved theme on mount
  useEffect(() => {
    const saved = localStorage.getItem('theme') as Theme | null;
    if (saved) {
      setTheme(saved);
      applyTheme(saved);
    } else {
      // Default to system preference
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setTheme('system');
      document.documentElement.style.colorScheme = isDark ? 'dark' : 'light';
    }
  }, []);

  // Listen to system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      if (theme === 'system') {
        document.documentElement.style.colorScheme = e.matches ? 'dark' : 'light';
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  const applyTheme = (newTheme: Theme) => {
    if (newTheme === 'dark') {
      document.documentElement.style.colorScheme = 'dark';
      document.body.classList.add('dark-mode');
      document.body.classList.remove('light-mode');
    } else if (newTheme === 'light') {
      document.documentElement.style.colorScheme = 'light';
      document.body.classList.add('light-mode');
      document.body.classList.remove('dark-mode');
    } else {
      // system
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.style.colorScheme = isDark ? 'dark' : 'light';
      document.body.classList.toggle('dark-mode', isDark);
      document.body.classList.toggle('light-mode', !isDark);
    }
  };

  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
    setIsOpen(false);
    onThemeChange?.(newTheme);
  };

  const getThemeIcon = () => {
    switch (theme) {
      case 'dark':
        return '🌙';
      case 'light':
        return '☀️';
      case 'system':
        return '⚙️';
      default:
        return '⚙️';
    }
  };

  return (
    <div className="theme-toggle-container">
      <button
        className="theme-toggle-button"
        onClick={() => setIsOpen(!isOpen)}
        title="Toggle theme"
      >
        {getThemeIcon()}
      </button>

      {isOpen && (
        <div className="theme-dropdown">
          <button
            className={`theme-option ${theme === 'light' ? 'active' : ''}`}
            onClick={() => handleThemeChange('light')}
          >
            ☀️ Light
          </button>
          <button
            className={`theme-option ${theme === 'dark' ? 'active' : ''}`}
            onClick={() => handleThemeChange('dark')}
          >
            🌙 Dark
          </button>
          <button
            className={`theme-option ${theme === 'system' ? 'active' : ''}`}
            onClick={() => handleThemeChange('system')}
          >
            ⚙️ System
          </button>
        </div>
      )}
    </div>
  );
};

export default ThemeToggle;
