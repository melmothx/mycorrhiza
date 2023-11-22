import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
    server: {
        proxy: {
            '/account': 'http://127.0.0.1:8010/',
            '/search': 'http://127.0.0.1:8010/',
            '/admin': 'http://127.0.0.1:8010/',
            '/static': 'http://127.0.0.1:8010/',
        },
    },

  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
