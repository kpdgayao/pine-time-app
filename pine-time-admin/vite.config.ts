import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  console.log('Vite build mode:', mode);
  
  return {
    plugins: [react()],
    // CRITICAL FIX: Must match the deployment subdirectory in production
    // This ensures assets are referenced with the correct base path
    base: mode === 'production' ? '/admin/' : '/',
    build: {
      outDir: 'dist',
      // Clean the output directory to ensure a fresh build
      emptyOutDir: true,
      // Ensure assets are referenced correctly with the admin base path
      assetsDir: 'assets',
      // Add source maps for better debugging
      sourcemap: true,
      // Fix asset paths to ensure they're loaded correctly
      assetsInlineLimit: 0,
      // Split chunks for better caching with predictable paths
      rollupOptions: {
        output: {
          // Ensure assets have predictable and absolute paths
          assetFileNames: 'assets/[name]-[hash][extname]',
          chunkFileNames: 'assets/[name]-[hash].js',
          entryFileNames: 'assets/[name]-[hash].js',
          // Create separate chunks for large dependencies
          manualChunks: (id) => {
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
