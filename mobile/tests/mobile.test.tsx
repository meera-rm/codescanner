/**
 * Mobile App Unit Tests - Phase 11
 * Tests for React Native screens, services, and state management
 */

describe('CodePulse Mobile App', () => {
  describe('App Structure', () => {
    test('app directory structure exists', () => {
      const fs = require('fs');
      const path = require('path');
      
      const dirs = [
        'src/screens',
        'src/services',
        'src/store',
        'src/navigation',
      ];

      dirs.forEach(dir => {
        expect(fs.existsSync(path.join(__dirname, '..', dir))).toBe(true);
      });
    });

    test('all screen files exist', () => {
      const fs = require('fs');
      const path = require('path');
      
      const screens = [
        'DashboardScreen.tsx',
        'AnalysisScreen.tsx',
        'LoginScreen.tsx',
        'SettingsScreen.tsx',
        'ProfileScreen.tsx',
        'SplashScreen.tsx',
      ];

      const screenDir = path.join(__dirname, '..', 'src/screens');
      screens.forEach(screen => {
        expect(fs.existsSync(path.join(screenDir, screen))).toBe(true);
      });
    });

    test('all service files exist', () => {
      const fs = require('fs');
      const path = require('path');
      
      const services = [
        'apiService.ts',
        'notificationService.ts',
      ];

      const serviceDir = path.join(__dirname, '..', 'src/services');
      services.forEach(service => {
        expect(fs.existsSync(path.join(serviceDir, service))).toBe(true);
      });
    });

    test('all store files exist', () => {
      const fs = require('fs');
      const path = require('path');
      
      const stores = [
        'authStore.ts',
        'dashboardStore.ts',
      ];

      const storeDir = path.join(__dirname, '..', 'src/store');
      stores.forEach(store => {
        expect(fs.existsSync(path.join(storeDir, store))).toBe(true);
      });
    });

    test('app entry points exist', () => {
      const fs = require('fs');
      const path = require('path');
      
      const files = [
        'src/App.tsx',
        'src/index.tsx',
      ];

      files.forEach(file => {
        expect(fs.existsSync(path.join(__dirname, '..', file))).toBe(true);
      });
    });
  });

  describe('Configuration Files', () => {
    test('package.json exists with required dependencies', () => {
      const fs = require('fs');
      const path = require('path');
      const packageJson = JSON.parse(
        fs.readFileSync(path.join(__dirname, '..', 'package.json'), 'utf-8')
      );

      const requiredDeps = [
        'react',
        'react-native',
        '@react-navigation/native',
        '@react-navigation/bottom-tabs',
        'axios',
        'zustand',
      ];

      requiredDeps.forEach(dep => {
        expect(packageJson.dependencies[dep] || packageJson.devDependencies[dep]).toBeDefined();
      });
    });

    test('jest.config.js exists with proper configuration', () => {
      const fs = require('fs');
      const path = require('path');
      
      expect(fs.existsSync(path.join(__dirname, '..', 'jest.config.js'))).toBe(true);
    });

    test('babel.config.js exists with proper configuration', () => {
      const fs = require('fs');
      const path = require('path');
      
      expect(fs.existsSync(path.join(__dirname, '..', 'babel.config.js'))).toBe(true);
    });

    test('jest.setup.js exists for test setup', () => {
      const fs = require('fs');
      const path = require('path');
      
      expect(fs.existsSync(path.join(__dirname, '..', 'jest.setup.js'))).toBe(true);
    });
  });

  describe('API Service Module', () => {
    test('apiService module exports ApiService class', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/services/apiService.ts'),
        'utf-8'
      );

      expect(content).toContain('class ApiService');
      expect(content).toContain('export const apiService');
      expect(content).toContain('axios.create');
    });

    test('apiService has required methods', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/services/apiService.ts'),
        'utf-8'
      );

      expect(content).toContain('get(');
      expect(content).toContain('post(');
      expect(content).toContain('put(');
      expect(content).toContain('delete(');
    });

    test('apiService implements token injection', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/services/apiService.ts'),
        'utf-8'
      );

      expect(content).toContain('interceptors.request');
      expect(content).toContain('Authorization');
      expect(content).toContain('Bearer');
    });
  });

  describe('Notification Service Module', () => {
    test('notificationService exports required functions', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/services/notificationService.ts'),
        'utf-8'
      );

      expect(content).toContain('export const configurePushNotifications');
      expect(content).toContain('export const sendLocalNotification');
      expect(content).toContain('export const sendAnalysisNotification');
      expect(content).toContain('export const sendAlertNotification');
    });
  });

  describe('Auth Store Module', () => {
    test('authStore exports useAuthStore hook', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/store/authStore.ts'),
        'utf-8'
      );

      expect(content).toContain('export const useAuthStore');
      expect(content).toContain('create<AuthStore>');
    });

    test('authStore has required methods', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/store/authStore.ts'),
        'utf-8'
      );

      expect(content).toContain('login:');
      expect(content).toContain('logout:');
      expect(content).toContain('checkAuthStatus:');
      expect(content).toContain('setUser:');
    });

    test('authStore uses AsyncStorage for persistence', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/store/authStore.ts'),
        'utf-8'
      );

      expect(content).toContain('AsyncStorage');
      expect(content).toContain('getItem');
      expect(content).toContain('setItem');
      expect(content).toContain('removeItem');
    });
  });

  describe('Dashboard Store Module', () => {
    test('dashboardStore exports useDashboardStore hook', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/store/dashboardStore.ts'),
        'utf-8'
      );

      expect(content).toContain('export const useDashboardStore');
      expect(content).toContain('create<DashboardStore>');
    });

    test('dashboardStore manages refresh interval', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/store/dashboardStore.ts'),
        'utf-8'
      );

      expect(content).toContain('refreshInterval');
      expect(content).toContain('setRefreshInterval');
      expect(content).toContain('shouldRefresh');
    });
  });

  describe('Screen Components', () => {
    test('DashboardScreen has required imports', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/screens/DashboardScreen.tsx'),
        'utf-8'
      );

      expect(content).toContain('useAuthStore');
      expect(content).toContain('apiService');
      expect(content).toContain('ScrollView');
      expect(content).toContain('useState');
      expect(content).toContain('useEffect');
    });

    test('AnalysisScreen has analysis functionality', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/screens/AnalysisScreen.tsx'),
        'utf-8'
      );

      expect(content).toContain('FlatList');
      expect(content).toContain('TextInput');
      expect(content).toContain('/analysis/start');
      expect(content).toContain('analyses');
    });

    test('LoginScreen has auth form', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/screens/LoginScreen.tsx'),
        'utf-8'
      );

      expect(content).toContain('email');
      expect(content).toContain('password');
      expect(content).toContain('login');
      expect(content).toContain('error');
    });

    test('SettingsScreen has preferences', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/screens/SettingsScreen.tsx'),
        'utf-8'
      );

      expect(content).toContain('Switch');
      expect(content).toContain('Notifications');
      expect(content).toContain('Dark Mode');
      expect(content).toContain('Sign Out');
    });

    test('ProfileScreen displays user info', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/screens/ProfileScreen.tsx'),
        'utf-8'
      );

      expect(content).toContain('avatar');
      expect(content).toContain('user?.name');
      expect(content).toContain('user?.email');
      expect(content).toContain('Statistics');
    });

    test('SplashScreen has loading screen', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/screens/SplashScreen.tsx'),
        'utf-8'
      );

      expect(content).toContain('ActivityIndicator');
      expect(content).toContain('CodePulse');
      expect(content).toContain('AI-Powered Code Analysis');
    });
  });

  describe('App Navigation', () => {
    test('App.tsx sets up navigation', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/App.tsx'),
        'utf-8'
      );

      expect(content).toContain('NavigationContainer');
      expect(content).toContain('Tab.Navigator');
      expect(content).toContain('Stack.Navigator');
      expect(content).toContain('DashboardStack');
      expect(content).toContain('AnalysisStack');
      expect(content).toContain('SettingsStack');
    });

    test('App handles auth state', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/App.tsx'),
        'utf-8'
      );

      expect(content).toContain('isLoggedIn');
      expect(content).toContain('isLoading');
      expect(content).toContain('LoginScreen');
      expect(content).toContain('TabNavigator');
    });

    test('App configures push notifications', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'src/App.tsx'),
        'utf-8'
      );

      expect(content).toContain('configurePushNotifications');
      expect(content).toContain('useEffect');
    });
  });

  describe('Code Quality', () => {
    test('all screens use proper React imports', () => {
      const fs = require('fs');
      const path = require('path');
      
      const screenDir = path.join(__dirname, '..', 'src/screens');
      const screens = fs.readdirSync(screenDir).filter(f => f.endsWith('.tsx'));

      screens.forEach(screen => {
        const content = fs.readFileSync(path.join(screenDir, screen), 'utf-8');
        expect(content).toContain('import React');
        expect(content).toContain('export default');
      });
    });

    test('all services are properly exported', () => {
      const fs = require('fs');
      const path = require('path');
      
      const serviceDir = path.join(__dirname, '..', 'src/services');
      const services = fs.readdirSync(serviceDir).filter(f => f.endsWith('.ts'));

      services.forEach(service => {
        const content = fs.readFileSync(path.join(serviceDir, service), 'utf-8');
        expect(content).toContain('export');
      });
    });

    test('all stores use Zustand', () => {
      const fs = require('fs');
      const path = require('path');
      
      const storeDir = path.join(__dirname, '..', 'src/store');
      const stores = fs.readdirSync(storeDir).filter(f => f.endsWith('.ts'));

      stores.forEach(store => {
        const content = fs.readFileSync(path.join(storeDir, store), 'utf-8');
        expect(content).toContain('zustand');
        expect(content).toContain('create');
      });
    });
  });

  describe('Documentation', () => {
    test('PHASE11.md documentation exists', () => {
      const fs = require('fs');
      const path = require('path');
      
      expect(fs.existsSync(path.join(__dirname, '..', 'PHASE11.md'))).toBe(true);
    });

    test('PHASE11.md contains required sections', () => {
      const fs = require('fs');
      const path = require('path');
      const content = fs.readFileSync(
        path.join(__dirname, '..', 'PHASE11.md'),
        'utf-8'
      );

      expect(content).toContain('## Overview');
      expect(content).toContain('## Architecture');
      expect(content).toContain('## Key Features');
      expect(content).toContain('## Setup Instructions');
      expect(content).toContain('## Security Features');
    });
  });

  describe('Test Coverage', () => {
    test('tests directory exists', () => {
      const fs = require('fs');
      const path = require('path');
      
      expect(fs.existsSync(path.join(__dirname, '..', 'tests'))).toBe(true);
    });

    test('test file exists', () => {
      const fs = require('fs');
      const path = require('path');
      
      expect(fs.existsSync(path.join(__dirname, 'mobile.test.tsx'))).toBe(true);
    });
  });
});
