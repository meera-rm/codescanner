# CodePulse AI - Developer Integration Guide

## Quick Start

### Prerequisites
- Node.js 16+ (frontend)
- Python 3.10+ (backend)
- npm or yarn (package manager)

### Setup

#### 1. Backend Setup
```bash
cd api
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm start
```

Frontend will be available at: `http://localhost:3000`

#### 3. Environment Configuration
Create `.env.local` in frontend directory:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

---

## Component Integration

### Using the API Client

#### Import the client
```typescript
import { apiClient } from '@/services/apiClient';
```

#### Load team CAQI data
```typescript
const CAQIGauge = ({ teamId }: { teamId: string }) => {
  const [caqi, setCAQI] = useState<TeamCAQI | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .getTeamCAQI(teamId)
      .then(setCAQI)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [teamId]);

  if (loading) return <div>Loading...</div>;
  if (!caqi) return <div>Failed to load CAQI data</div>;

  return (
    <CAQIGauge
      teamId={caqi.team_id}
      overallCaqi={caqi.overall_caqi}
      dimensions={caqi.dimensions}
      calculatedAt={caqi.calculated_at}
    />
  );
};
```

#### Load anomalies with filtering
```typescript
const AnomaliesDashboard = ({ teamId }: { teamId: string }) => {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [severity, setSeverity] = useState<string | undefined>();
  const [reviewed, setReviewed] = useState<boolean | undefined>();

  useEffect(() => {
    apiClient
      .getAnomalies(teamId, severity as any, reviewed)
      .then(setAnomalies)
      .catch(console.error);
  }, [teamId, severity, reviewed]);

  return (
    <div>
      <select onChange={(e) => setSeverity(e.target.value)}>
        <option value="">All Severities</option>
        <option value="critical">Critical</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
        <option value="low">Low</option>
      </select>
      
      <AnomaliesTable
        teamId={teamId}
        anomalies={anomalies}
        onReviewAnomaly={(id) =>
          apiClient.reviewAnomaly(teamId, id).then(() => {
            // Refresh anomalies
          })
        }
      />
    </div>
  );
};
```

#### Load developer contributions
```typescript
const DeveloperMetrics = ({ teamId }: { teamId: string }) => {
  const [developers, setDevelopers] = useState<Developer[]>([]);
  const [period, setPeriod] = useState(30);

  useEffect(() => {
    apiClient
      .getDeveloperContributions(teamId, period)
      .then(setDevelopers)
      .catch(console.error);
  }, [teamId, period]);

  return (
    <DeveloperContributions
      teamId={teamId}
      developers={developers}
      period={period}
    />
  );
};
```

---

## API Integration Patterns

### Pattern 1: Simple Data Loading
```typescript
useEffect(() => {
  apiClient
    .getTeamCAQI(teamId)
    .then((data) => {
      // Use data
    })
    .catch((error) => {
      // Handle error
      console.error('Failed to load CAQI:', error);
    });
}, [teamId]);
```

### Pattern 2: Loading with State Management
```typescript
const [state, setState] = useState({
  loading: true,
  error: null,
  data: null,
});

useEffect(() => {
  setState({ loading: true, error: null, data: null });
  apiClient
    .getTeamCAQI(teamId)
    .then((data) => {
      setState({ loading: false, error: null, data });
    })
    .catch((error) => {
      setState({ loading: false, error, data: null });
    });
}, [teamId]);
```

### Pattern 3: Filtering and Refetching
```typescript
const [anomalies, setAnomalies] = useState([]);
const [filters, setFilters] = useState({
  severity: undefined,
  reviewed: undefined,
});

const fetchAnomalies = useCallback(async () => {
  try {
    const data = await apiClient.getAnomalies(
      teamId,
      filters.severity,
      filters.reviewed
    );
    setAnomalies(data);
  } catch (error) {
    console.error('Failed to load anomalies:', error);
  }
}, [teamId, filters]);

useEffect(() => {
  fetchAnomalies();
}, [fetchAnomalies]);
```

### Pattern 4: Concurrent Requests
```typescript
useEffect(() => {
  Promise.all([
    apiClient.getTeamCAQI(teamId),
    apiClient.getAnomalies(teamId),
    apiClient.getDeveloperContributions(teamId),
  ])
    .then(([caqi, anomalies, developers]) => {
      // All data loaded
      setState({
        caqi,
        anomalies,
        developers,
      });
    })
    .catch((error) => {
      // Handle error
    });
}, [teamId]);
```

---

## Testing Integration

### Unit Testing with API Client Mock
```typescript
import { apiClient } from '@/services/apiClient';

jest.mock('@/services/apiClient');

describe('CAQIGauge Integration', () => {
  it('should load and display CAQI data', async () => {
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

    (apiClient.getTeamCAQI as jest.Mock).mockResolvedValueOnce(mockCAQI);

    render(<CAQIGauge teamId="backend-team" />);

    await waitFor(() => {
      expect(screen.getByText('380')).toBeInTheDocument();
    });
  });
});
```

### Integration Testing
See `frontend/src/__tests__/integration.e2e.test.ts` for comprehensive E2E test examples.

---

## Adding New Endpoints

### Step 1: Define the API method in `apiClient.ts`
```typescript
async getCustomData(teamId: string, param: string): Promise<CustomData> {
  return this.request<CustomData>(
    `/analytics/teams/${teamId}/custom?param=${param}`
  );
}
```

### Step 2: Add types for the response
```typescript
export interface CustomData {
  team_id: string;
  customField: string;
  // other fields
}
```

### Step 3: Add tests
```typescript
it('should fetch custom data', async () => {
  const mockData = { team_id: 'backend-team', customField: 'value' };
  fetchMock.mockResolvedValueOnce({
    ok: true,
    json: async () => mockData,
  });

  const result = await client.getCustomData('backend-team', 'param-value');
  expect(result.customField).toBe('value');
});
```

### Step 4: Use in components
```typescript
const customData = await apiClient.getCustomData(teamId, 'param');
```

---

## Common Issues & Solutions

### Issue: 404 Not Found
**Cause:** API URL incorrect or endpoint doesn't exist  
**Solution:** Check `REACT_APP_API_URL` environment variable and API endpoint path

### Issue: CORS Errors
**Cause:** API doesn't allow requests from frontend origin  
**Solution:** Update CORS configuration in FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Timeout Errors
**Cause:** API is slow or not responding  
**Solution:** Add timeout handling:
```typescript
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 5000);

try {
  const response = await fetch(url, { signal: controller.signal });
  clearTimeout(timeout);
} catch (error) {
  if (error.name === 'AbortError') {
    console.error('Request timeout');
  }
}
```

### Issue: Validation Errors (422)
**Cause:** Invalid query parameters  
**Solution:** Check parameter values against API documentation

| Parameter | Valid Range | Example |
|-----------|-------------|---------|
| days | 1-365 | 30 |
| severity | low, medium, high, critical | high |
| dimension | security, complexity, documentation, testing, dependencies, maintainability | security |

---

## Performance Optimization

### 1. Debounce Filter Changes
```typescript
const debouncedFetch = useMemo(
  () =>
    debounce((filters) => {
      fetchAnomalies(filters);
    }, 300),
  []
);

useEffect(() => {
  debouncedFetch(filters);
}, [filters, debouncedFetch]);
```

### 2. Cache API Responses
```typescript
const cache = new Map();

const getCachedData = async (key: string, fetcher: () => Promise<T>) => {
  if (cache.has(key)) return cache.get(key);
  const data = await fetcher();
  cache.set(key, data);
  return data;
};
```

### 3. Lazy Load Components
```typescript
const CAQIGaugeComponent = lazy(() => import('./CAQIGauge'));

<Suspense fallback={<Loading />}>
  <CAQIGaugeComponent />
</Suspense>
```

---

## Debugging Tips

### Enable API request logging
```typescript
const apiClient = new APIClient(baseUrl);

// Intercept all requests
const originalRequest = apiClient.request.bind(apiClient);
apiClient.request = async (endpoint: string, options?: RequestInit) => {
  console.log('API Request:', endpoint, options);
  const result = await originalRequest(endpoint, options);
  console.log('API Response:', result);
  return result;
};
```

### Monitor API calls in browser
1. Open DevTools (F12)
2. Go to Network tab
3. Filter by XHR (XMLHttpRequest)
4. Watch API calls in real-time

### Check API health
```bash
curl http://localhost:8000/api/v1/analytics/health
```

---

## Deployment Considerations

### Environment Variables
```bash
# Development
REACT_APP_API_URL=http://localhost:8000/api/v1

# Production
REACT_APP_API_URL=https://api.codepulse.company/api/v1
```

### Backend Configuration
```python
# development.env
API_HOST=localhost
API_PORT=8000
DATABASE_URL=sqlite:///dev.db

# production.env
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=postgresql://user:pass@prod-db:5432/codepulse
```

---

## Testing Checklist

- [ ] API client imports without errors
- [ ] Environment variable is set correctly
- [ ] API is running and accessible
- [ ] Components load data on mount
- [ ] Filtering works correctly
- [ ] Error handling displays user-friendly messages
- [ ] Concurrent requests work
- [ ] API calls don't block UI
- [ ] Network errors are handled
- [ ] Tests pass with mocked API

---

## Additional Resources

- [API Documentation](./API_DOCUMENTATION.md)
- [Frontend Components](./frontend/components/README.md)
- [Testing Guide](./frontend/README.md)
- [Backend Services](./api/services/README.md)

---

**Last Updated:** 2026-06-06
