import { defineStore } from 'pinia'

const STORAGE_KEY = 'theme'

const getSystemTheme = () =>
  window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'

const applyClass = (mode) => {
  document.documentElement.classList.toggle('my-app-dark', mode === 'dark')
}

export const useThemeStore = defineStore('theme', {
  state: () => ({
    mode: 'light',
    _mediaListener: null,
  }),
  getters: {
    isDark: (state) => state.mode === 'dark',
  },
  actions: {
    init() {
      const saved = localStorage.getItem(STORAGE_KEY)
      this.mode = saved === 'dark' || saved === 'light' ? saved : getSystemTheme()
      applyClass(this.mode)

      // Segue o SO apenas enquanto o usuário não escolher manualmente
      if (!saved && !this._mediaListener) {
        const mq = window.matchMedia('(prefers-color-scheme: dark)')
        this._mediaListener = (e) => {
          this.mode = e.matches ? 'dark' : 'light'
          applyClass(this.mode)
        }
        mq.addEventListener('change', this._mediaListener)
      }
    },
    setMode(mode) {
      this.mode = mode
      localStorage.setItem(STORAGE_KEY, mode)
      applyClass(mode)
    },
    toggle() {
      this.setMode(this.isDark ? 'light' : 'dark')
    },
  },
})
