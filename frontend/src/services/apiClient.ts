/**
 * API Client - handles all communication with backend API
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export interface TeamCAQI {
  team_id: string;
  overall_caqi: number;
  dimensions: {
    security: number;
    complexity: number;
    documentation: number;
    testing: number;
    dependencies: number;
    maintainability: number;
  };
  calculated_at: string;
}

export interface TrendData {
  team_id: string;
  dimension: string;
  scores: Array<{ date: string; score: number }>;
  trend: 'improving' | 'declining' | 'stable';
}

export interface Anomaly {
  id: string;
  dimension: string;
  previousScore: number;
  currentScore: number;
  changePercent: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  detectedAt: string;
  reviewed: boolean;
  reviewedBy?: string;
}

export interface Developer {
  developerId: string;
  teamId: string;
  contributions: {
    [key: string]: {
      developerScore: number;
      teamAvg: number;
      contribution: number;
    };
  };
  overallContribution: number;
}

export interface PeerComparison {
  team_id: string;
  dimension: string;
  score: number;
  percentile: number;
  peerMedian: number;
  peerMin: number;
  peerMax: number;
}

export interface Alert {
  id: string;
  type: 'regression' | 'trend' | 'threshold';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  createdAt: string;
  acknowledged: boolean;
}

export interface Benchmark {
  dimension: string;
  target: number;
  current: number;
  industry_median: number;
  status: 'on_track' | 'at_risk' | 'critical';
}

class APIClient {
  private baseUrl: string;
  private pendingRequests: Map<string, Promise<any>> = new Map();

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private getRequestKey(endpoint: string, options?: RequestInit): string {
    return `${options?.method || 'GET'}:${endpoint}`;
  }

  private async request<T>(endpoint: string, options?: RequestInit, retries: number = 3): Promise<T> {
    // Deduplication: reuse pending request if same endpoint+method
    const key = this.getRequestKey(endpoint, options);
    if (this.pendingRequests.has(key)) {
      return this.pendingRequests.get(key)!;
    }

    const promise = this.executeRequest<T>(endpoint, options, retries);
    this.pendingRequests.set(key, promise);

    return promise.finally(() => {
      this.pendingRequests.delete(key);
    });
  }

  private async executeRequest<T>(endpoint: string, options?: RequestInit, retries: number = 3): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 30000); // 30 second timeout

        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json',
            ...options?.headers,
          },
        });

        clearTimeout(timeout);

        if (!response.ok) {
          throw new Error(`API error: ${response.status} ${response.statusText}`);
        }

        return response.json();
      } catch (error) {
        clearTimeout(0);

        // Check if error is retryable
        const isRetryable = this.isRetryableError(error);
        const isLastAttempt = attempt === retries;

        if (isRetryable && !isLastAttempt) {
          // Exponential backoff: 1s, 2s, 4s
          const delay = Math.pow(2, attempt - 1) * 1000;
          if (process.env.NODE_ENV === 'development') {
            console.debug(`[API] Retry attempt ${attempt}/${retries} after ${delay}ms for ${endpoint}`);
          }
          await new Promise(resolve => setTimeout(resolve, delay));
          continue;
        }

        console.error(`API request failed: ${endpoint} (attempt ${attempt}/${retries})`, error);
        throw error;
      }
    }

    throw new Error(`API request failed after ${retries} retries: ${endpoint}`);
  }

  private isRetryableError(error: unknown): boolean {
    if (error instanceof TypeError) {
      // Network errors (e.g., "fetch failed")
      return true;
    }
    if (error instanceof Error) {
      // Timeout error (AbortError)
      if (error.name === 'AbortError') {
        return true;
      }
      // Only retry on 429 (rate limit), not on other HTTP errors (4xx, 5xx)
      // Client errors should not be retried
      if (error.message.includes('429')) {
        return true;
      }
    }
    return false;
  }

  /**
   * Get team CAQI score and dimensions
   */
  async getTeamCAQI(teamId: string): Promise<TeamCAQI> {
    return this.request<TeamCAQI>(`/analytics/teams/${teamId}/caqi`);
  }

  /**
   * Get trend data for a dimension
   */
  async getTeamTrends(teamId: string, days: number = 30): Promise<TrendData[]> {
    return this.request<TrendData[]>(`/analytics/teams/${teamId}/trends?days=${days}`);
  }

  /**
   * Get detected anomalies
   */
  async getAnomalies(teamId: string, severity?: string, reviewed?: boolean): Promise<Anomaly[]> {
    let query = '';
    const params: string[] = [];
    if (severity) params.push(`severity=${severity}`);
    if (reviewed !== undefined) params.push(`reviewed=${reviewed}`);
    if (params.length) query = '?' + params.join('&');

    return this.request<Anomaly[]>(`/analytics/teams/${teamId}/anomalies${query}`);
  }

  /**
   * Get developer contributions
   */
  async getDeveloperContributions(teamId: string, days: number = 30): Promise<Developer[]> {
    return this.request<Developer[]>(`/analytics/teams/${teamId}/developers?days=${days}`);
  }

  /**
   * Get peer comparison data
   */
  async getPeerComparison(teamId: string, dimension: string): Promise<PeerComparison> {
    return this.request<PeerComparison>(
      `/analytics/teams/${teamId}/peer-comparison?dimension=${dimension}`
    );
  }

  /**
   * Get alerts
   */
  async getAlerts(teamId: string, severity?: string): Promise<Alert[]> {
    let query = '';
    if (severity) query = `?severity=${severity}`;
    return this.request<Alert[]>(`/analytics/teams/${teamId}/alerts${query}`);
  }

  /**
   * Get benchmarks
   */
  async getBenchmarks(teamId: string): Promise<Benchmark[]> {
    return this.request<Benchmark[]>(`/analytics/teams/${teamId}/benchmarks`);
  }

  /**
   * Health check
   */
  async health(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/analytics/health');
  }

  /**
   * Review an anomaly
   */
  async reviewAnomaly(teamId: string, anomalyId: string, notes?: string): Promise<void> {
    return this.request(`/analytics/teams/${teamId}/anomalies/${anomalyId}/review`, {
      method: 'POST',
      body: JSON.stringify({ notes }),
    });
  }
}

export const apiClient = new APIClient();
export default APIClient;
