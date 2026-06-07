/**
 * End-to-End Integration Tests
 * Tests frontend components with real API client calls and mocked backend responses
 */

import APIClient, { TeamCAQI, Anomaly, Developer } from '../services/apiClient';

describe('E2E Integration: Frontend Components with API Client', () => {
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

  describe('Dashboard Loading Flow', () => {
    it('should load CAQI gauge data', async () => {
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

      expect(result.overall_caqi).toBe(380);
      expect(result.dimensions.security).toBe(85);
    });

    it('should load anomalies table data', async () => {
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
        {
          id: 'anom-2',
          dimension: 'complexity',
          previousScore: 70,
          currentScore: 65,
          changePercent: -7.1,
          severity: 'medium',
          detectedAt: '2026-06-04T14:00:00Z',
          reviewed: true,
          reviewedBy: 'user-1',
        },
      ];

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomalies,
      });

      const result = await client.getAnomalies('backend-team');

      expect(result).toHaveLength(2);
      expect(result[0].severity).toBe('high');
      expect(result[0].reviewed).toBe(false);
      expect(result[1].reviewed).toBe(true);
    });

    it('should load developer contributions data', async () => {
      const mockDevelopers: Developer[] = [
        {
          developerId: 'dev-1',
          teamId: 'backend-team',
          contributions: {
            security: { developerScore: 80, teamAvg: 75, contribution: 5.0 },
            complexity: { developerScore: 72, teamAvg: 70, contribution: 2.0 },
            documentation: {
              developerScore: 75,
              teamAvg: 65,
              contribution: 10.0,
            },
            testing: { developerScore: 85, teamAvg: 80, contribution: 5.0 },
            dependencies: { developerScore: 70, teamAvg: 60, contribution: 10.0 },
            maintainability: {
              developerScore: 80,
              teamAvg: 75,
              contribution: 5.0,
            },
          },
          overallContribution: 6.17,
        },
      ];

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDevelopers,
      });

      const result = await client.getDeveloperContributions('backend-team');

      expect(result).toHaveLength(1);
      expect(result[0].developerId).toBe('dev-1');
      expect(result[0].overallContribution).toBeGreaterThan(0);
    });
  });

  describe('Dashboard Data Filtering', () => {
    it('should filter anomalies by severity', async () => {
      const mockAnomalies: Anomaly[] = [
        {
          id: 'crit-1',
          dimension: 'security',
          previousScore: 80,
          currentScore: 50,
          changePercent: -37.5,
          severity: 'critical',
          detectedAt: '2026-06-06T10:00:00Z',
          reviewed: false,
        },
      ];

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomalies,
      });

      const result = await client.getAnomalies('backend-team', 'critical');

      expect(result).toHaveLength(1);
      expect(result[0].severity).toBe('critical');
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('severity=critical'),
        expect.any(Object)
      );
    });

    it('should filter anomalies by reviewed status', async () => {
      const mockAnomalies: Anomaly[] = [
        {
          id: 'anom-2',
          dimension: 'complexity',
          previousScore: 70,
          currentScore: 65,
          changePercent: -7.1,
          severity: 'medium',
          detectedAt: '2026-06-04T14:00:00Z',
          reviewed: true,
          reviewedBy: 'user-1',
        },
      ];

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomalies,
      });

      const result = await client.getAnomalies('backend-team', undefined, true);

      expect(result).toHaveLength(1);
      expect(result[0].reviewed).toBe(true);
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('reviewed=true'),
        expect.any(Object)
      );
    });

    it('should get developers with custom period', async () => {
      const mockDevelopers: Developer[] = [];

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDevelopers,
      });

      await client.getDeveloperContributions('backend-team', 90);

      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('days=90'),
        expect.any(Object)
      );
    });
  });

  describe('Peer Comparison Flow', () => {
    it('should load peer comparison for security dimension', async () => {
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

      expect(result.score).toBe(85);
      expect(result.percentile).toBe(75);
      expect(result.dimension).toBe('security');
    });

    it('should compare all dimensions', async () => {
      const dimensions = [
        'security',
        'complexity',
        'documentation',
        'testing',
        'dependencies',
        'maintainability',
      ];

      for (const dim of dimensions) {
        fetchMock.mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            team_id: 'backend-team',
            dimension: dim,
            score: 75,
            percentile: 60,
            peerMedian: 70,
            peerMin: 50,
            peerMax: 90,
          }),
        });
      }

      for (const dim of dimensions) {
        const result = await client.getPeerComparison('backend-team', dim);
        expect(result.dimension).toBe(dim);
      }

      expect(fetchMock).toHaveBeenCalledTimes(6);
    });
  });

  describe('Trends and Alerts Flow', () => {
    it('should load trend data for last 30 days', async () => {
      const mockTrends = [
        {
          team_id: 'backend-team',
          dimension: 'security',
          scores: [
            { date: '2026-05-07', score: 75 },
            { date: '2026-05-14', score: 78 },
            { date: '2026-05-21', score: 80 },
            { date: '2026-05-28', score: 82 },
            { date: '2026-06-04', score: 85 },
          ],
          trend: 'improving',
        },
      ];

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTrends,
      });

      const result = await client.getTeamTrends('backend-team', 30);

      expect(result).toHaveLength(1);
      expect(result[0].trend).toBe('improving');
      expect(result[0].scores).toHaveLength(5);
    });

    it('should load alerts', async () => {
      const mockAlerts = [
        {
          id: 'alert-1',
          type: 'regression',
          severity: 'high',
          message: 'Security score declined 10%',
          createdAt: '2026-06-06T10:00:00Z',
          acknowledged: false,
        },
        {
          id: 'alert-2',
          type: 'trend',
          severity: 'medium',
          message: 'Testing dimension declining',
          createdAt: '2026-06-05T14:00:00Z',
          acknowledged: true,
        },
      ];

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAlerts,
      });

      const result = await client.getAlerts('backend-team');

      expect(result).toHaveLength(2);
      expect(result[0].severity).toBe('high');
      expect(result[1].acknowledged).toBe(true);
    });
  });

  describe('User Actions Flow', () => {
    it('should review an anomaly', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      await client.reviewAnomaly('backend-team', 'anom-1', 'Reviewed and confirmed');

      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/anomalies/anom-1/review'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('Reviewed and confirmed'),
        })
      );
    });

    it('should review anomaly without notes', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      await client.reviewAnomaly('backend-team', 'anom-1');

      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/anomalies/anom-1/review'),
        expect.any(Object)
      );
    });
  });

  describe('Error Handling Flow', () => {
    it('should handle API errors gracefully', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      });

      await expect(client.getTeamCAQI('backend-team')).rejects.toThrow(
        'API error: 500'
      );
    });

    it('should handle network errors', async () => {
      fetchMock.mockRejectedValueOnce(new Error('Network error'));

      await expect(client.getTeamCAQI('backend-team')).rejects.toThrow(
        'Network error'
      );
    });

    it('should handle validation errors', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 422,
        statusText: 'Unprocessable Entity',
      });

      await expect(client.getTeamTrends('backend-team', 0)).rejects.toThrow(
        'API error: 422'
      );
    });
  });

  describe('Health Check and Connectivity', () => {
    it('should check API health', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'ok' }),
      });

      const result = await client.health();

      expect(result.status).toBe('ok');
    });

    it('should verify API is reachable', async () => {
      const mockCAQI = {
        team_id: 'test-team',
        overall_caqi: 300,
        dimensions: {
          security: 60,
          complexity: 60,
          documentation: 60,
          testing: 60,
          dependencies: 60,
          maintainability: 60,
        },
        calculated_at: '2026-06-06T10:00:00Z',
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockCAQI,
      });

      const result = await client.getTeamCAQI('test-team');

      expect(result.team_id).toBe('test-team');
      expect(result.overall_caqi).toBe(300);
    });
  });

  describe('Multi-Team Support', () => {
    it('should load data for different teams', async () => {
      const teams = ['backend-team', 'frontend-team', 'devops-team'];

      for (const team of teams) {
        fetchMock.mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            team_id: team,
            overall_caqi: 350,
            dimensions: {
              security: 70,
              complexity: 70,
              documentation: 70,
              testing: 70,
              dependencies: 70,
              maintainability: 70,
            },
            calculated_at: '2026-06-06T10:00:00Z',
          }),
        });
      }

      for (const team of teams) {
        const result = await client.getTeamCAQI(team);
        expect(result.team_id).toBe(team);
      }

      expect(fetchMock).toHaveBeenCalledTimes(3);
    });
  });

  describe('Concurrent Requests', () => {
    it('should handle multiple concurrent API calls', async () => {
      const mockCAQI = {
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

      const mockAnomalies: Anomaly[] = [];
      const mockDevelopers: Developer[] = [];

      fetchMock
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockCAQI,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockAnomalies,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockDevelopers,
        });

      const [caqi, anomalies, developers] = await Promise.all([
        client.getTeamCAQI('backend-team'),
        client.getAnomalies('backend-team'),
        client.getDeveloperContributions('backend-team'),
      ]);

      expect(caqi.overall_caqi).toBe(380);
      expect(anomalies).toHaveLength(0);
      expect(developers).toHaveLength(0);
      expect(fetchMock).toHaveBeenCalledTimes(3);
    });
  });
});
