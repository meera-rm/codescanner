import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface User {
  id: string;
  name: string;
  email: string;
  plan?: string;
  created_at?: string;
  analyses_count?: number;
  patterns_found?: number;
}

interface AuthStore {
  isLoggedIn: boolean;
  isLoading: boolean;
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => Promise<void>;
  logout: () => Promise<void>;
  checkAuthStatus: () => Promise<void>;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  isLoggedIn: false,
  isLoading: true,
  user: null,
  token: null,

  login: async (token: string, user: User) => {
    await AsyncStorage.setItem('auth_token', token);
    await AsyncStorage.setItem('user', JSON.stringify(user));
    set({ isLoggedIn: true, token, user });
  },

  logout: async () => {
    await AsyncStorage.removeItem('auth_token');
    await AsyncStorage.removeItem('user');
    set({ isLoggedIn: false, token: null, user: null });
  },

  checkAuthStatus: async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const userStr = await AsyncStorage.getItem('user');

      if (token && userStr) {
        const user = JSON.parse(userStr);
        set({ isLoggedIn: true, token, user });
      } else {
        set({ isLoggedIn: false });
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      set({ isLoggedIn: false });
    } finally {
      set({ isLoading: false });
    }
  },

  setUser: (user: User) => {
    set({ user });
    AsyncStorage.setItem('user', JSON.stringify(user));
  },
}));
