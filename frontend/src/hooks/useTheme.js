import { useState, useEffect, useCallback } from 'react';

export default function useTheme() {
  const [theme, setThemeState] = useState(() => {
    try {
      return localStorage.getItem('codalyra-theme') || 'system';
    } catch {
      return 'system';
    }
  });

  const applyTheme = useCallback((t) => {
    if (t === 'system') {
      document.documentElement.removeAttribute('data-theme');
    } else {
      document.documentElement.setAttribute('data-theme', t);
    }
  }, []);

  useEffect(() => {
    applyTheme(theme);
  }, [theme, applyTheme]);

  const setTheme = useCallback((t) => {
    setThemeState(t);
    try {
      localStorage.setItem('codalyra-theme', t);
    } catch {}
    applyTheme(t);
  }, [applyTheme]);

  const toggle = useCallback(() => {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (theme === 'system') {
      setTheme(prefersDark ? 'light' : 'dark');
    } else if (theme === 'dark') {
      setTheme('light');
    } else {
      setTheme('dark');
    }
  }, [theme, setTheme]);

  const isDark = theme === 'dark' ||
    (theme === 'system' && typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches);

  return { theme, isDark, toggle, setTheme };
}
