import {readFileSync} from 'fs'
import {sentryVitePlugin} from '@sentry/vite-plugin'
import wasm from "vite-plugin-wasm"
/// <reference types="vitest" />

// Plugins
import vue from '@vitejs/plugin-vue'
import vuetify, {transformAssetUrls} from 'vite-plugin-vuetify'
import ViteFonts from 'unplugin-fonts/vite'
import topLevelAwait from "vite-plugin-top-level-await"

// Utilities
import {defineConfig} from 'vite'
import {fileURLToPath, URL} from 'node:url'
import checker from 'vite-plugin-checker'


const path = readFileSync('.git/HEAD', 'utf-8').split(': ')[1].trim()
const commitHash = readFileSync('.git/' + path, 'utf-8').slice(0, 8)


const productionMode = process.env.NODE_ENV === 'production'

const base = productionMode ? '/static/dist/' : '/vite/'

const input = productionMode ? undefined : 'frontend/main.ts'

const plugins = [
  vue({
    template: {transformAssetUrls},
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
  wasm(),
]

if (productionMode) {
  plugins.push(sentryVitePlugin({
    org: 'artconomycom',
    project: 'vue',
  }))
  plugins.push(
    topLevelAwait({
      // The export name of top-level await promise for each chunk module
      promiseExportName: "__tla",
      // The function to generate import names of top-level await promise in each chunk module
      promiseImportName: i => `__tla_${i}`
    })
  )
} else {
  plugins.push(
    checker({
      typescript: true,
    }
  ))
}

// https://vitejs.dev/config/
export default defineConfig({
  __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false',
  plugins,
  test: {
    globals: true,
    pool: 'forks',
    poolOptions: {
      forks: {
        minForks: 4,
        maxForks: 8,
      }
    },
    environment: 'jsdom',
    setupFiles: ['specs/setupTestEnv.ts'],
    server: {
      deps: {
        inline: ['vuetify'],
      },
    },
    reporters: ['dot'],
    coverage: {
      provider: 'istanbul',
      reporter: ['text', 'html', 'clover'],
      reportsDirectory: '../reports/coverage',
    },
  },
  base: base,
  build: {
    manifest: 'manifest.json',
    emptyOutDir: true,
    rollupOptions: {
      external: [
        /static\/.*/,
        /.*[/]specs[/].*/,
      ],
      output: {
        manualChunks: {
          vueCore: ['vue', 'vuetify', 'vuex', 'vue-router'],
          vueStyles: ['vuetify/styles'],
          captcha: ['@/components/fields/hcaptcha/VueHcaptcha.vue', '@/components/fields/hcaptcha/hcaptchaScript.js', '@/components/fields/AcCaptchaField.vue'],
          navAssist: ['@/components/navigation/AcTabs.vue', '@/components/AcTab.vue', '@/components/wrappers/AcLoadSection.vue', '@/components/wrappers/AcLoadingSpinner.vue'],
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
          uppy: ['@uppy/core', '@uppy/dashboard', '@uppy/url', '@uppy/xhr-upload', '@/components/fields/AcUppyFile.vue'],
        },
      },
      input,
    },
    outDir: '../public/dist',
    sourcemap: true,
  },
  optimizeDeps: {
    exclude: ['@date-io/date-fns', 'vuetify', '../node_modules', 'node_modules'],
    include: ['@hcaptcha/vue3-hcaptcha'],
  },
  define: {
    'process.env': {
      '__COMMIT_HASH__': commitHash,
      'NODE_ENV': process.env.NODE_ENV,
    },
  },
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
    warmup: {clientFiles: ['store/**/*.ts', 'lib/*.ts', 'components/wrappers/*.vue']},
    fs: {cachedChecks: true},
  },
})
