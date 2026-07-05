module.exports = {
  testEnvironment: 'node',
  setupFilesAfterEnv: [
    '<rootDir>/jest.setup.js',
  ],
  testMatch: [
    '<rootDir>/**/__tests__/**/*.js',
    '<rootDir>/**/?(*.)(spec|test).js',
    '<rootDir>/**/*.test.tsx',
  ],
  moduleFileExtensions: [
    'ts',
    'tsx',
    'js',
    'jsx',
    'json',
    'node',
  ],
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  transformIgnorePatterns: [
    'node_modules/(?!(zustand)/)',
  ],
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
  ],
  coverageThreshold: {
    global: {
      statements: 30,
      branches: 20,
      functions: 30,
      lines: 30,
    },
  },
};
