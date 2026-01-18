import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { ScanResult } from '../api'

interface ScanHistory {
  id: string
  result: ScanResult
  timestamp: Date
}

interface AppState {
  // Scan history
  scanHistory: ScanHistory[]
  addScan: (result: ScanResult) => void
  clearHistory: () => void
  
  // Theme
  isDarkMode: boolean
  toggleDarkMode: () => void
  
  // Language
  language: string
  setLanguage: (lang: string) => void
  
  // Settings
  autoScan: boolean
  setAutoScan: (enabled: boolean) => void
  showNotifications: boolean
  setShowNotifications: (enabled: boolean) => void
  strictMode: boolean
  setStrictMode: (enabled: boolean) => void
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      // Scan history
      scanHistory: [],
      addScan: (result) =>
        set((state) => ({
          scanHistory: [
            {
              id: crypto.randomUUID(),
              result,
              timestamp: new Date(),
            },
            ...state.scanHistory.slice(0, 99), // Keep last 100 scans
          ],
        })),
      clearHistory: () => set({ scanHistory: [] }),
      
      // Theme
      isDarkMode: true,
      toggleDarkMode: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
      
      // Language
      language: 'en',
      setLanguage: (lang) => set({ language: lang }),
      
      // Settings
      autoScan: true,
      setAutoScan: (enabled) => set({ autoScan: enabled }),
      showNotifications: true,
      setShowNotifications: (enabled) => set({ showNotifications: enabled }),
      strictMode: false,
      setStrictMode: (enabled) => set({ strictMode: enabled }),
    }),
    {
      name: 'nabih-storage',
    }
  )
)
