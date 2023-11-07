/// <reference types="vitest" />

// Plugins
import vue from '@vitejs/plugin-vue'
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
import ViteFonts from 'unplugin-fonts/vite'
import ChildProcess from 'child_process'

// Utilities
import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'node:url'
import checker from 'vite-plugin-checker'

const commitHash = ChildProcess.execSync('git rev-parse --short HEAD').toString().trim()

const productionMode = process.env.NODE_ENV === 'production'

const base = productionMode ? '/static/dist/' : '/vite/'

const input = productionMode ? undefined : 'frontend/main.ts'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue({
      template: { transformAssetUrls }
    }),
    // https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vite-plugin
    vuetify({
      autoImport: true,
    }),
    ViteFonts({
      google: {
        families: [{
          name: 'Roboto',
          styles: 'wght@100;300;400;500;700;900',
        }],
      },
    }),
    checker({
      typescript: true,
    }),
  ],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['specs/setupTestEnv.ts'],
    server: {
      deps: {
        inline: ['vuetify']
      }
    }
  },
  base: base,
  build: {
    manifest: "manifest.json",
    rollupOptions: {
      external: [/static\/.*/],
      input,
    },
    outDir: '../public/dist'
  },
  optimizeDeps: {
    exclude: ['@date-io/date-fns']
  },
  define: { 'process.env': {'__COMMIT_HASH__': commitHash, 'NODE_ENV': process.env.NODE_ENV} },
  root: './frontend/',
  resolve: {
    alias: {
      '@/': fileURLToPath(new URL('./frontend/', import.meta.url)),
    },
    extensions: [
      '.js',
      '.json',
      '.jsx',
      '.mjs',
      '.ts',
      '.tsx',
      '.vue',
    ],
  },
  server: {
    port: 8001,
    host: true,
  },
})
