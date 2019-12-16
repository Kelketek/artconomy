module.exports = {
  moduleFileExtensions: [
    'js',
    'jsx',
    'json',
    'vue',
    'ts',
    'tsx',
  ],
  transform: {
    '^.+\\.vue$': 'vue-jest',
    '.+\\.(css|styl|less|sass|scss|svg|png|jpg|ttf|woff|woff2)$': 'jest-transform-stub',
    '^.+\\.tsx?$': 'ts-jest',
  },
  transformIgnorePatterns: [
    '/node_modules/(?!vuetify)',
  ],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/frontend/$1',
  },
  roots: [
    './frontend/',
  ],
  snapshotSerializers: [
    'jest-serializer-vue',
  ],
  testMatch: [
    '**/specs/**/*.spec.(js|jsx|ts|tsx)|**/__tests__/*.(js|jsx|ts|tsx)',
  ],
  testURL: 'http://localhost/',
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname',
  ],
  collectCoverage: true,
  coverageReporters: ['text', 'lcov'],
  coverageDirectory: 'reports/coverage',
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/specs/',
  ],
  globals: {
    'ts-jest': {
      babelConfig: true,
    },
  },
}
