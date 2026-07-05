import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import '@testing-library/jest-native/extend-expect';
import DashboardScreen from '../src/screens/DashboardScreen';
import AnalysisScreen from '../src/screens/AnalysisScreen';
import LoginScreen from '../src/screens/LoginScreen';
import SettingsScreen from '../src/screens/SettingsScreen';
import ProfileScreen from '../src/screens/ProfileScreen';
import SplashScreen from '../src/screens/SplashScreen';
import App from '../src/App';

// Mock API and stores
jest.mock('../src/services/apiService', () => ({
  apiService: {
    get: jest.fn(() => Promise.resolve({ data: {} })),
    post: jest.fn(() => Promise.resolve({ data: {} })),
  },
}));

jest.mock('../src/store/authStore', () => ({
  useAuthStore: () => ({
    user: { name: 'Test User', email: 'test@example.com' },
    isLoggedIn: true,
    login: jest.fn(),
    logout: jest.fn(),
    checkAuthStatus: jest.fn(),
  }),
}));

jest.mock('../src/store/dashboardStore', () => ({
  useDashboardStore: () => ({
    refreshInterval: 60,
    setRefreshInterval: jest.fn(),
    dashboardData: null,
    setDashboardData: jest.fn(),
  }),
}));

jest.mock('react-native-push-notification', () => ({
  default: {
    configure: jest.fn(),
    localNotificationSchedule: jest.fn(),
  },
}));

describe('CodePulse Mobile App', () => {
  describe('DashboardScreen', () => {
    test('renders greeting with user name', async () => {
      render(<DashboardScreen />);
      await waitFor(() => {
        expect(screen.getByText(/Hello, Test User/i)).toBeTruthy();
      });
    });

    test('displays stat cards', async () => {
      render(<DashboardScreen />);
      await waitFor(() => {
        expect(screen.getByText(/System Health/i)).toBeTruthy();
        expect(screen.getByText(/Patterns Found/i)).toBeTruthy();
      });
    });

    test('has action buttons', async () => {
      render(<DashboardScreen />);
      await waitFor(() => {
        expect(screen.getByText(/Analyze Code/i)).toBeTruthy();
        expect(screen.getByText(/View Reports/i)).toBeTruthy();
      });
    });
  });

  describe('AnalysisScreen', () => {
    test('renders analysis input section', () => {
      render(<AnalysisScreen />);
      expect(screen.getByText(/Analyze Code Repository/i)).toBeTruthy();
    });

    test('has repository URL input', () => {
      render(<AnalysisScreen />);
      const input = screen.getByPlaceholderText(/Enter repository URL/i);
      expect(input).toBeTruthy();
    });

    test('has start analysis button', () => {
      render(<AnalysisScreen />);
      expect(screen.getByText(/Start Analysis/i)).toBeTruthy();
    });

    test('displays recent analyses section', () => {
      render(<AnalysisScreen />);
      expect(screen.getByText(/Recent Analyses/i)).toBeTruthy();
    });

    test('shows empty state message initially', () => {
      render(<AnalysisScreen />);
      expect(screen.getByText(/No analyses yet/i)).toBeTruthy();
    });
  });

  describe('LoginScreen', () => {
    test('renders login form', () => {
      render(<LoginScreen />);
      expect(screen.getByText(/Sign In/i)).toBeTruthy();
    });

    test('has email and password inputs', () => {
      render(<LoginScreen />);
      expect(screen.getByPlaceholderText(/Email/i)).toBeTruthy();
      expect(screen.getByPlaceholderText(/Password/i)).toBeTruthy();
    });

    test('has sign in button', () => {
      render(<LoginScreen />);
      expect(screen.getByText(/Sign In/i)).toBeTruthy();
    });

    test('shows forgot password link', () => {
      render(<LoginScreen />);
      expect(screen.getByText(/Forgot Password?/i)).toBeTruthy();
    });

    test('displays create account link', () => {
      render(<LoginScreen />);
      expect(screen.getByText(/Create one/i)).toBeTruthy();
    });

    test('shows error on empty form submission', async () => {
      render(<LoginScreen />);
      const button = screen.getByText(/Sign In/i);
      fireEvent.press(button);
      await waitFor(() => {
        expect(screen.getByText(/Please fill in all fields/i)).toBeTruthy();
      });
    });
  });

  describe('SettingsScreen', () => {
    test('renders preferences section', () => {
      render(<SettingsScreen navigation={{}} />);
      expect(screen.getByText(/Preferences/i)).toBeTruthy();
    });

    test('has notification toggle', () => {
      render(<SettingsScreen navigation={{}} />);
      expect(screen.getByText(/Notifications/i)).toBeTruthy();
    });

    test('has dark mode toggle', () => {
      render(<SettingsScreen navigation={{}} />);
      expect(screen.getByText(/Dark Mode/i)).toBeTruthy();
    });

    test('has data refresh options', () => {
      render(<SettingsScreen navigation={{}} />);
      expect(screen.getByText(/Data Refresh/i)).toBeTruthy();
    });

    test('has sign out button', () => {
      render(<SettingsScreen navigation={{}} />);
      expect(screen.getByText(/Sign Out/i)).toBeTruthy();
    });

    test('has view profile button', () => {
      render(<SettingsScreen navigation={{}} />);
      expect(screen.getByText(/View Profile/i)).toBeTruthy();
    });

    test('shows version number', () => {
      render(<SettingsScreen navigation={{}} />);
      expect(screen.getByText(/v1\.0\.0/i)).toBeTruthy();
    });
  });

  describe('ProfileScreen', () => {
    test('displays user avatar', () => {
      render(<ProfileScreen />);
      expect(screen.getByText(/T/i)).toBeTruthy();
    });

    test('shows user name and email', () => {
      render(<ProfileScreen />);
      expect(screen.getByText(/Test User/i)).toBeTruthy();
      expect(screen.getByText(/test@example.com/i)).toBeTruthy();
    });

    test('displays account information section', () => {
      render(<ProfileScreen />);
      expect(screen.getByText(/Account Information/i)).toBeTruthy();
    });

    test('displays statistics', () => {
      render(<ProfileScreen />);
      expect(screen.getByText(/Statistics/i)).toBeTruthy();
      expect(screen.getByText(/Analyses/i)).toBeTruthy();
      expect(screen.getByText(/Patterns/i)).toBeTruthy();
    });

    test('has change password button', () => {
      render(<ProfileScreen />);
      expect(screen.getByText(/Change Password/i)).toBeTruthy();
    });

    test('has delete account button', () => {
      render(<ProfileScreen />);
      expect(screen.getByText(/Delete Account/i)).toBeTruthy();
    });
  });

  describe('SplashScreen', () => {
    test('displays logo', () => {
      render(<SplashScreen />);
      expect(screen.getByText(/CodePulse/i)).toBeTruthy();
    });

    test('displays tagline', () => {
      render(<SplashScreen />);
      expect(screen.getByText(/AI-Powered Code Analysis/i)).toBeTruthy();
    });
  });

  describe('API Service', () => {
    test('api service exists', () => {
      const { apiService } = require('../src/services/apiService');
      expect(apiService).toBeDefined();
      expect(apiService.get).toBeDefined();
      expect(apiService.post).toBeDefined();
    });

    test('auth store exists', () => {
      const { useAuthStore } = require('../src/store/authStore');
      expect(useAuthStore).toBeDefined();
    });

    test('dashboard store exists', () => {
      const { useDashboardStore } = require('../src/store/dashboardStore');
      expect(useDashboardStore).toBeDefined();
    });

    test('notification service exists', () => {
      const notificationService = require('../src/services/notificationService');
      expect(notificationService).toBeDefined();
      expect(notificationService.configurePushNotifications).toBeDefined();
      expect(notificationService.sendLocalNotification).toBeDefined();
    });
  });

  describe('Navigation Structure', () => {
    test('app has required screens', () => {
      expect(DashboardScreen).toBeDefined();
      expect(AnalysisScreen).toBeDefined();
      expect(LoginScreen).toBeDefined();
      expect(SettingsScreen).toBeDefined();
      expect(ProfileScreen).toBeDefined();
      expect(SplashScreen).toBeDefined();
    });
  });
});
