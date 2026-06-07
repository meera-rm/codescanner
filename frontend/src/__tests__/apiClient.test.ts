/**
 * Integration tests for API Client
 */

import APIClient, { TeamCAQI, Anomaly, Developer } from '../services/apiClient';

describe('APIClient', () => {
  let client: APIClient;
  let fetchMock: jest.Mock;

  beforeEach(() => {
    fetchMock = jest.fn();
    global.fetch = fetchMock;
    client = new APIClient('http://localhost:8000/api/v1');
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('getTeamCAQI', () => {
    it('should fetch team CAQI data', async () => {
      const mockCAQI: TeamCAQI = {
        team_id: 'backend-team',
        overall_caqi: 380,
        dimensions: {
          security: 85,
          complexity: 72,
          documentation: 80,
          testing: 88,
          dependencies: 65,
          maintainability: 78,
        },
        calculated_at: '2026-06-06T14:30:00Z',
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockCAQI,
      });

      const result = await client.getTeamCAQI('backend-team');

      expect(result).toEqual(mockCAQI);
      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/analytics/teams/backend-team/caqi',
        expect.objectContaining({
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });

    it('should throw on API error', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      });

      await expect(client.getTeamCAQI('backend-team')).rejects.toThrow(
        'API error: 500 Internal Server Error'
      );
    });
  });

  describe('getAnomalies', () => {
    it('should fetch anomalies without filters', async () => {
      const mockAnomalies: Anomaly[] = [
        {
          id: 'anom-1',
          dimension: 'security',
          previousScore: 75,
          currentScore: 85,
          changePercent: 13.3,
          severity: 'high',
          detectedAt: '2026-06-05T10:00:00Z',
          reviewed: false,
        },
      ];

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomalies,
      });

      const result = await client.getAnomalies('backend-team');

      expect(result).toEqual(mockAnomalies);
      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/analytics/teams/backend-team/anomalies',
        expect.any(Object)
      );
    });

    it('should fetch anomalies with severity filter', async () => {
      const mockAnomalies: Anomaly[] = [];

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomalies,
      });

      await client.getAnomalies('backend-team', 'critical');

      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/analytics/teams/backend-team/anomalies?severity=critical',
        expect.any(Object)
      );
    });

    it('should fetch anomalies with reviewed filter', async () => {
      const mockAnomalies: Anomaly[] = [];

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomalies,
      });

      await client.getAnomalies('backend-team', undefined, true);

      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/analytics/teams/backend-team/anomalies?reviewed=true',
        expect.any(Object)
      );
    });
  });

  describe('getDeveloperContributions', () => {
    it('should fetch developer contributions', async () => {
      const mockDevelopers: Developer[] = [
        {
          developerId: 'dev-1',
          teamId: 'backend-team',
          contributions: {
            security: { developerScore: 80, teamAvg: 75, contribution: 5.0 },
            complexity: { developerScore: 72, teamAvg: 70, contribution: 2.0 },
            documentation: { developerScore: 75, teamAvg: 65, contribution: 10.0 },
            testing: { developerScore: 85, teamAvg: 80, contribution: 5.0 },
            dependencies: { developerScore: 70, teamAvg: 60, contribution: 10.0 },
            maintainability: { developerScore: 80, teamAvg: 75, contribution: 5.0 },
          },
          overallContribution: 6.17,
        },
      ];

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDevelopers,
      });

      const result = await client.getDeveloperContributions('backend-team', 30);

      expect(result).toEqual(mockDevelopers);
      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/analytics/teams/backend-team/developers?days=30',
        expect.any(Object)
      );
    });
  });

  describe('getPeerComparison', () => {
    it('should fetch peer comparison data', async () => {
      const mockComparison = {
        team_id: 'backend-team',
        dimension: 'security',
        score: 85,
        percentile: 75,
        peerMedian: 80,
        peerMin: 60,
        peerMax: 95,
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockComparison,
      });

      const result = await client.getPeerComparison('backend-team', 'security');

      expect(result).toEqual(mockComparison);
      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/analytics/teams/backend-team/peer-comparison?dimension=security',
        expect.any(Object)
      );
    });
  });

  describe('getAlerts', () => {
    it('should fetch alerts', async () => {
      const mockAlerts = [
        {
          id: 'alert-1',
          type: 'regression',
          severity: 'high',
          message: 'Security score declined',
          createdAt: '2026-06-06T10:00:00Z',
        },
      ];

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAlerts,
      });

      const result = await client.getAlerts('backend-team', 'high');

      expect(result).toEqual(mockAlerts);
      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/analytics/teams/backend-team/alerts?severity=high',
        expect.any(Object)
      );
    });
  });

  describe('health', () => {
    it('should check API health', async () => {
      const mockHealth = { status: 'healthy' };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHealth,
      });

      const result = await client.health();

      expect(result).toEqual(mockHealth);
      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/analytics/health',
        expect.any(Object)
      );
    });
  });

  describe('reviewAnomaly', () => {
    it('should post anomaly review', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      await client.reviewAnomaly('backend-team', 'anom-1', 'Looks good');

      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/analytics/teams/backend-team/anomalies/anom-1/review',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ notes: 'Looks good' }),
        })
      );
    });
  });
});
