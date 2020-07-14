const path = require('path')
const BundleTracker = require('webpack-bundle-tracker')
const VuetifyLoaderPlugin = require('vuetify-loader/lib/plugin')
const SentryWebpackPlugin = require('@sentry/webpack-plugin')
const webpack = require('webpack')

const commitHash = require('child_process')
  .execSync('git rev-parse --short HEAD')
  .toString()

module.exports = {
  assetsDir: 'dist',
  configureWebpack: config => {
    let packName = './webpack-stats.json'
    if (process.env.VUE_CLI_MODERN_MODE && !process.env.VUE_CLI_MODERN_BUILD) {
      packName = './webpack-stats-legacy.json'
    }
    config.plugins.push(new BundleTracker({filename: packName}), new VuetifyLoaderPlugin())
    config.plugins.push(new webpack.DefinePlugin({
      __COMMIT_HASH__: JSON.stringify(commitHash),
    }))
    if (process.env.NODE_ENV === 'production') {
      config.plugins.push(new SentryWebpackPlugin({
        include: '.',
        ignoreFile: '.sentrycliignore',
        ignore: ['node_modules', 'vue.config.js', 'jest.config.js', 'reports'],
        configFile: 'sentry.properties',
      }))
    }
    config.entry = {
      app: [
        './frontend/main.ts',
      ],
    }
    config.resolve.alias['@'] = path.resolve('./frontend/')
  },
  chainWebpack: config => {
    config
      .plugin('html')
      .tap(args => {
        args[0].template = './frontend/index.html'
        return args
      })
  },
  devServer: {
    public: 'https://artconomy.vulpinity.com',
    allowedHosts: ['localhost', '.vulpinity.com', '.artconomy.com'],
  },
  outputDir: 'public',
  publicPath: '/static/',
  runtimeCompiler: true,
}
