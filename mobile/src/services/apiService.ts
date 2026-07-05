import axios, { AxiosInstance } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuthStore } from '../store/authStore';

const API_BASE_URL = 'http://localhost:5000/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });

    // Add token to requests
    this.client.interceptors.request.use(async (config) => {
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle token expiration
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          await AsyncStorage.removeItem('auth_token');
          const authStore = useAuthStore.getState();
          authStore.logout();
        }
        return Promise.reject(error);
      }
    );
  }

  async get(endpoint: string, config = {}) {
    return this.client.get(endpoint, config);
  }

  async post(endpoint: string, data = {}, config = {}) {
    return this.client.post(endpoint, data, config);
  }

  async put(endpoint: string, data = {}, config = {}) {
    return this.client.put(endpoint, data, config);
  }

  async delete(endpoint: string, config = {}) {
    return this.client.delete(endpoint, config);
  }

  setBaseURL(url: string) {
    this.client.defaults.baseURL = url;
  }
}

export const apiService = new ApiService();
