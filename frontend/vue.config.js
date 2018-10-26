let BundleTracker = require('webpack-bundle-tracker')

module.exports = {
  outputDir: '../public',
  baseUrl: '/static/',
  assetsDir: 'dist',
  runtimeCompiler: true,
  devServer: {
    proxy: 'http://artconomy.vulpinity.com:8002'
  },
  configureWebpack: {
    plugins: [
      new BundleTracker({filename: '../webpack-stats.json'})
    ],
  },
  transpileDependencies: ['*']
}
