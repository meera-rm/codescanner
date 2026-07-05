import { create } from 'zustand';

interface DashboardData {
  system_health: number;
  api_health: number;
  patterns_found: number;
  plan_usage: number;
}

interface DashboardStore {
  dashboardData: DashboardData | null;
  refreshInterval: number;
  lastRefresh: number;
  isRefreshing: boolean;
  setDashboardData: (data: DashboardData) => void;
  setRefreshInterval: (interval: number) => void;
  setIsRefreshing: (refreshing: boolean) => void;
  shouldRefresh: () => boolean;
  markRefreshed: () => void;
}

export const useDashboardStore = create<DashboardStore>((set, get) => ({
  dashboardData: null,
  refreshInterval: 60,
  lastRefresh: 0,
  isRefreshing: false,

  setDashboardData: (data: DashboardData) => {
    set({ dashboardData: data });
  },

  setRefreshInterval: (interval: number) => {
    set({ refreshInterval: interval });
  },

  setIsRefreshing: (refreshing: boolean) => {
    set({ isRefreshing: refreshing });
  },

  shouldRefresh: () => {
    const state = get();
    const now = Date.now();
    return (now - state.lastRefresh) > (state.refreshInterval * 1000);
  },

  markRefreshed: () => {
    set({ lastRefresh: Date.now() });
  },
}));
