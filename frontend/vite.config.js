import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
  server: {
    // 127.0.0.1 evita conflito com serviços Docker escutando em localhost/::1
    proxy: {
      '/api': 'http://127.0.0.1:8050',
      '/login': 'http://127.0.0.1:8050',
      '/me': 'http://127.0.0.1:8050',
      '/logout': 'http://127.0.0.1:8050',
      '/docs': 'http://127.0.0.1:8050',
      '/openapi.json': 'http://127.0.0.1:8050',
    },
  },
})
