let BundleTracker = require('webpack-bundle-tracker')

module.exports = {
  outputDir: '../public',
  baseUrl: '/static/',
  assetsDir: 'dist',
  runtimeCompiler: true,
  devServer: {
    proxy: 'http://artconomy.vulpinity.com:8002',
    public: 'https://artconomy.vulpinity.com'
  },
  configureWebpack: config => {
    let packName = '../webpack-stats.json'
    if (process.env.VUE_CLI_MODERN_MODE && !process.env.VUE_CLI_MODERN_BUILD) {
      packName = '../webpack-stats-legacy.json'
    }
    config.plugins.push(new BundleTracker({filename: packName}))
  },
  transpileDependencies: ['*']
}
