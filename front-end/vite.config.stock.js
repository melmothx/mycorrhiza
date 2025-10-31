import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite';

const loggerPlugin  = () => ({
    name: 'request-logger',
    configureServer(server) {
        server.middlewares.use((req, res, next) => {
            const xForwardedFor = req.headers['x-forwarded-for'];
            const ip = Array.isArray(xForwardedFor)
                ? xForwardedFor[0]
                : xForwardedFor?.split(',')[0]?.trim() || req.socket?.remoteAddress;
            console.log(
                `[${new Date().toISOString()}] ${ip} ${req.method} ${req.url}`
            );
            next();
        })
    }
});

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    loggerPlugin(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
