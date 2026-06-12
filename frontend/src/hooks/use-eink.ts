'use client';

import { useState, useEffect, useCallback } from 'react';

const EINK_STORAGE_KEY = 'aitutor-eink-mode';
const EINK_CLASS = 'eink-mode';

type EInkPreference = 'auto' | 'enabled' | 'disabled';

interface UseEInkReturn {
  isEInk: boolean;
  preference: EInkPreference;
  setPreference: (pref: EInkPreference) => void;
  toggleEInkMode: () => void;
  autoDetect: () => void;
}

export function useEInk(): UseEInkReturn {
  const [preference, setPreferenceState] = useState<EInkPreference>('auto');
  const [isEInk, setIsEInk] = useState(false);

  const applyEinkClass = useCallback((apply: boolean) => {
    if (typeof document === 'undefined') return;
    if (apply) {
      document.body.classList.add(EINK_CLASS);
    } else {
      document.body.classList.remove(EINK_CLASS);
    }
  }, []);

  const autoDetect = useCallback(() => {
    if (typeof window === 'undefined') return;
    const mediaQuery = window.matchMedia('(monochrome)');
    const detected = mediaQuery.matches;
    setIsEInk(detected);
    applyEinkClass(detected);
  }, [applyEinkClass]);

  useEffect(() => {
    const stored = localStorage.getItem(EINK_STORAGE_KEY) as EInkPreference | null;
    if (stored) {
      setPreferenceState(stored);
      if (stored === 'enabled') {
        setIsEInk(true);
        applyEinkClass(true);
      } else if (stored === 'disabled') {
        setIsEInk(false);
        applyEinkClass(false);
      } else {
        autoDetect();
      }
    } else {
      autoDetect();
    }
  }, [applyEinkClass, autoDetect]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const mediaQuery = window.matchMedia('(monochrome)');
    const handler = (e: MediaQueryListEvent) => {
      if (preference === 'auto') {
        setIsEInk(e.matches);
        applyEinkClass(e.matches);
      }
    };
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [preference, applyEinkClass]);

  const setPreference = useCallback((pref: EInkPreference) => {
    setPreferenceState(pref);
    localStorage.setItem(EINK_STORAGE_KEY, pref);
    if (pref === 'enabled') {
      setIsEInk(true);
      applyEinkClass(true);
    } else if (pref === 'disabled') {
      setIsEInk(false);
      applyEinkClass(false);
    } else {
      autoDetect();
    }
  }, [applyEinkClass, autoDetect]);

  const toggleEInkMode = useCallback(() => {
    if (preference === 'auto') {
      setPreference('enabled');
    } else if (preference === 'enabled') {
      setPreference('disabled');
    } else {
      setPreference('enabled');
    }
  }, [preference, setPreference]);

  return { isEInk, preference, setPreference, toggleEInkMode, autoDetect };
}