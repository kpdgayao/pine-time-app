import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  console.log('Vite build mode:', mode);
  
  return {
    plugins: [react()],
    // Fix: Use root base path with HashRouter for proper path resolution
    // HashRouter will handle the routing internally after the # symbol
    base: '/',
    build: {
      outDir: 'dist',
      // Clean the output directory to ensure a fresh build
      emptyOutDir: true,
      // Ensure assets are referenced correctly with the admin base path
      assetsDir: 'assets',
      // Add source maps for better debugging
      sourcemap: true,
      // Split chunks for better caching
      rollupOptions: {
        output: {
          manualChunks: (id) => {
            // Create separate chunks for large dependencies
            if (id.includes('node_modules')) {
              if (id.includes('@mui')) return 'vendor-mui';
              return 'vendor';
            }
          }
        }
      }
    },
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
  }
})
