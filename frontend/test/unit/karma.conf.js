// This is a karma config file. For more details see
//   http://karma-runner.github.io/0.13/config/configuration-file.html
// we are also using it with karma-webpack
//   https://github.com/webpack/karma-webpack

var webpackConfig = require('../../build/webpack.test.conf')

// function isDebug (argument) {
//   return argument === '--debug'
// }

let sourcePreprocessors = ['webpack', 'sourcemap']

// if (process.argv.some(isDebug)) {
//   sourcePreprocessors = []
// }

module.exports = function (config) {
  config.set({
    // to run in additional browsers:
    // 1. install corresponding karma launcher
    //    http://karma-runner.github.io/0.13/config/browsers.html
    browsers: ['FirefoxHeadless'],
    frameworks: ['mocha', 'sinon-chai', 'phantomjs-shim', 'polyfill'],
    reporters: ['spec', 'coverage'],
    files: [
      './index.js'
    ],
    polyfill: ['Promise'],
    preprocessors: {
      './index.js': sourcePreprocessors
    },
    webpack: webpackConfig,
    webpackMiddleware: {
      noInfo: true
    },
    coverageReporter: {
      dir: './coverage',
      reporters: [
        { type: 'lcov', subdir: '.' },
        { type: 'text-summary' }
      ]
    }
  })
}
