const path = require('path')

module.exports = {
  rootDir: path.resolve(__dirname, '../../../'),
  moduleFileExtensions: [
    'js',
    'json',
    'vue'
  ],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/frontend/src/$1'
  },
  transform: {
    '^.+\\.js$': '<rootDir>/node_modules/babel-jest',
    '.*\\.(vue)$': '<rootDir>/node_modules/vue-jest'
  },
  snapshotSerializers: ['<rootDir>/node_modules/jest-serializer-vue'],
  setupFiles: ['<rootDir>/frontend/test/unit/setup'],
  mapCoverage: true,
  coverageDirectory: '<rootDir>/frontend/test/unit/coverage',
  collectCoverageFrom: [
    'frontend/src/**/*.{js,vue}',
    '!frontend/src/main.js',
    '!frontend/src/router/index.js',
    '!**/node_modules/**'
  ]
}
