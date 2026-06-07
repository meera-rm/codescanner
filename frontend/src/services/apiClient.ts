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

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
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
  async getAlerts(teamId: string, severity?: string): Promise<any[]> {
    let query = '';
    if (severity) query = `?severity=${severity}`;
    return this.request<any[]>(`/analytics/teams/${teamId}/alerts${query}`);
  }

  /**
   * Get benchmarks
   */
  async getBenchmarks(teamId: string): Promise<any[]> {
    return this.request<any[]>(`/analytics/teams/${teamId}/benchmarks`);
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
