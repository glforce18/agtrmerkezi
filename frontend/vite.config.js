import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { NaiveUiResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      imports: [
        'vue',
        'vue-router',
        'pinia',
        {
          'naive-ui': [
            'useDialog',
            'useMessage',
            'useNotification',
            'useLoadingBar'
          ]
        }
      ],
      dts: 'src/auto-imports.d.ts'
    }),
    Components({
      resolvers: [NaiveUiResolver()],
      dts: 'src/components.d.ts'
    })
  ],
  base: '/',

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },

  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },

  build: {
    outDir: '../static/dist',
    emptyOutDir: true,
    sourcemap: false,
    chunkSizeWarningLimit: 1500,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks(id) {
          // Vendor chunk - core libraries
          if (id.includes('node_modules/vue') ||
              id.includes('node_modules/vue-router') ||
              id.includes('node_modules/pinia')) {
            return 'vendor'
          }
          // UI framework chunk
          if (id.includes('node_modules/naive-ui')) {
            return 'naive-ui'
          }
          // Utils chunk
          if (id.includes('node_modules/@vueuse') ||
              id.includes('node_modules/date-fns')) {
            return 'utils'
          }
          // Admin views - separate chunk for better caching
          if (id.includes('/views/admin/')) {
            return 'admin'
          }
          // Other node_modules - separate chunk
          if (id.includes('node_modules')) {
            return 'vendor-misc'
          }
        }
      }
    }
  },

  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'naive-ui', 'date-fns']
  }
})
