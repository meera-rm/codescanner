// Global test setup for mobile app
global.fetch = jest.fn();

// Mock React Native core components
jest.mock('react-native', () => ({
  View: 'View',
  Text: 'Text',
  ScrollView: 'ScrollView',
  TouchableOpacity: 'TouchableOpacity',
  FlatList: 'FlatList',
  TextInput: 'TextInput',
  ActivityIndicator: 'ActivityIndicator',
  StyleSheet: { create: jest.fn(style => style) },
  Switch: 'Switch',
  StatusBar: 'StatusBar',
}));

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  default: {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
  },
}));

// Mock navigation
jest.mock('@react-navigation/native', () => ({
  useNavigation: jest.fn(),
  useRoute: jest.fn(),
  NavigationContainer: ({ children }) => children,
}));

// Mock notifications
jest.mock('react-native-push-notification', () => ({
  default: {
    configure: jest.fn(),
    localNotificationSchedule: jest.fn(),
  },
}));
