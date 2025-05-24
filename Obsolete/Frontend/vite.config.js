import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    allowedHosts: ['pic.byinfo.cloud', 'localhost'],
    proxy: {
      '/api': {
        target: 'http://localhost:5000/api',
        changeOrigin: true,
      }
    }
  }
});