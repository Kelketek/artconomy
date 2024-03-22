import { sentryVitePlugin } from "@sentry/vite-plugin";
/// <reference types="vitest" />

// Plugins
import vue from '@vitejs/plugin-vue'
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
import ViteFonts from 'unplugin-fonts/vite'
import ChildProcess from 'child_process'

// Utilities
import {defineConfig} from 'vite'
import { fileURLToPath, URL } from 'node:url'
import checker from 'vite-plugin-checker'

const commitHash = ChildProcess.execSync('git rev-parse --short HEAD').toString().trim()

const productionMode = process.env.NODE_ENV === 'production'

const base = productionMode ? '/static/dist/' : '/vite/'

const input = productionMode ? undefined : 'frontend/main.ts'

const plugins = [
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
]

if (productionMode) {
  plugins.push(sentryVitePlugin({
    org: "artconomycom",
    project: "vue"
  }))
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins,
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['specs/setupTestEnv.ts'],
    server: {
      deps: {
        inline: ['vuetify']
      }
    },
    reporters: ['dot'],
    coverage: {
      provider: 'istanbul',
      reporter: ['text', 'html', 'clover'],
      reportsDirectory: '../reports/coverage'
    },
  },
  base: base,
  build: {
    manifest: "manifest.json",
    emptyOutDir: true,
    rollupOptions: {
      external: [
        /static\/.*/,
        /.*[/]specs[/].*/,
      ],
      output: {
        manualChunks: {
          vueCore: ['vue', 'vuetify', 'vuex', 'vue-facing-decorator', 'vue-router', 'vue-observe-visibility', '@devindex/vue-mask'],
          captcha: ['@hcaptcha/vue3-hcaptcha', '@/components/fields/AcCaptchaField.vue'],
          dataProcessing: ['decimal.js', 'lodash', 'date-fns'],
          qrCode: ['qrcode'],
          sortable: ['sortablejs', 'sortablejs-vue3', 'list-diff.js'],
          faq: [
            '@/components/views/faq/FAQ.vue',
            '@/components/views/faq/About.vue',
            '@/components/views/faq/BuyAndSell.vue',
            '@/components/views/faq/Other.vue',
            '@/components/views/faq/AcQuestion.vue',
            '@/components/views/faq/mixins/question-set.ts',
          ],
          uppy: ['@uppy/core', '@uppy/dashboard', '@uppy/url', '@uppy/xhr-upload', '@/components/fields/AcUppyFile.vue']
        },
      },
      input,
    },
    outDir: '../public/dist',
    sourcemap: true
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
