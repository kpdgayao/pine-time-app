import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  // Set base path for production to '/admin/' using the mode parameter for consistency
  base: mode === 'production' ? '/admin/' : '/',
  server: {
    host: 'localhost',
    port: 5174, // Using a different port than frontend (5173)
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      },
      '^/login/.*': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => `/api/v1${path}`
      }
    }
  },
}))
