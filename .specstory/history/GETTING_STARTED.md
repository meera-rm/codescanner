---
created_at: 2026-06-12T18:16:43Z
title: Getting Started
source: claude-code
project: codescanner
---

# CodePulse AI - Getting Started Guide

Welcome to the CodePulse AI team! This guide will help you get up and running quickly.

---

## 5-Minute Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/company/codepulse.git
cd codepulse
```

### 2. Start with Docker
```bash
docker-compose up -d
```

### 3. Access Application
- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/v1

That's it! You now have CodePulse AI running locally.

---

## Development Setup

### Prerequisites
- Git
- Docker & Docker Compose (or Node.js 16+ and Python 3.10+)
- VS Code or preferred IDE

### Installation

#### Option A: With Docker (Recommended)
```bash
# Clone repo
git clone https://github.com/company/codepulse.git
cd codepulse

# Start services
docker-compose up

# Frontend available at http://localhost:3000
# Backend available at http://localhost:8000
```

#### Option B: Local Setup
```bash
# Clone repo
git clone https://github.com/company/codepulse.git
cd codepulse

# Setup backend
cd api
pip install -r requirements.txt
python -m uvicorn main:app --reload

# In another terminal, setup frontend
cd frontend
npm install
npm start
```

---

## Project Structure

```
codepulse/
├── api/                          # Backend (FastAPI)
│   ├── main.py                   # App entry point
│   ├── routes/                   # API endpoints
│   │   └── advanced_analytics.py # Analytics endpoints (8 endpoints)
│   ├── services/                 # Business logic
│   │   ├── alerting_service.py
│   │   └── ...
│   └── requirements.txt
│
├── frontend/                     # Frontend (React)
│   ├── src/
│   │   ├── components/           # Reusable components
│   │   │   ├── CAQIGauge.tsx
│   │   │   ├── AnomaliesTable.tsx
│   │   │   └── DeveloperContributions.tsx
│   │   ├── services/
│   │   │   └── apiClient.ts      # API communication
│   │   ├── pages/                # Page components
│   │   └── __tests__/            # Tests
│   ├── package.json
│   └── tsconfig.json
│
├── tests/                        # Integration tests
│   ├── test_api_integration_simple.py
│   └── ...
│
├── docs/                         # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── DEVELOPER_GUIDE.md
│   ├── COMPONENT_INTEGRATION_GUIDE.md
│   └── DEPLOYMENT_GUIDE.md
│
└── docker-compose.yml           # Local development setup
```

---

## Common Tasks

### Run Tests
```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd ..
pytest tests/

# All tests
npm test && pytest tests/
```

### Add a New API Endpoint

1. **Define route** in `api/routes/advanced_analytics.py`
2. **Add service logic** in `api/services/`
3. **Write tests** in `tests/`
4. **Document** in `API_DOCUMENTATION.md`
5. **Update API client** in `frontend/src/services/apiClient.ts`

Example:
```python
# api/routes/advanced_analytics.py
@router.get("/teams/{team_id}/custom")
async def get_custom_data(team_id: str):
    return {"team_id": team_id, "data": "..."}

# frontend/src/services/apiClient.ts
async getCustomData(teamId: string): Promise<CustomData> {
  return this.request<CustomData>(`/analytics/teams/${teamId}/custom`);
}
```

### Add a New Frontend Component

1. **Create component** in `frontend/components/`
2. **Add types** in interface
3. **Write tests** in `__tests__/`
4. **Document** in `COMPONENT_INTEGRATION_GUIDE.md`

---

## Common Commands

### Frontend
```bash
cd frontend

# Start dev server
npm start

# Build for production
npm run build

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Lint code
npm run lint
```

### Backend
```bash
cd api

# Run dev server
python -m uvicorn main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=api

# Format code
black .
```

### Docker
```bash
# Build images
docker-compose build

# Start services
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Execute command in container
docker-compose exec backend python -m pytest
```

---

## Understanding the Architecture

### High-Level Flow
```
User (Browser)
    ↓
Frontend (React)
    ↓
API Client (TypeScript)
    ↓
Backend (FastAPI)
    ↓
Services (Business Logic)
    ↓
Database/External APIs
```

### Key Components

**Frontend Components (React)**
- `CAQIGauge` - Display code quality score
- `AnomaliesTable` - Show detected issues
- `DeveloperContributions` - Developer impact metrics

**Backend Services**
- `AlertingService` - Detect quality regressions
- `AdvancedAnalyticsRoutes` - 8 REST endpoints
- `MetricsAggregator` - Calculate CAQI scores

**API Endpoints** (8 total)
- `GET /teams/{id}/caqi` - Overall score
- `GET /teams/{id}/trends` - Historical trends
- `GET /teams/{id}/anomalies` - Issues detected
- `GET /teams/{id}/developers` - Developer metrics
- `GET /teams/{id}/peer-comparison` - vs other teams
- `GET /teams/{id}/alerts` - Quality alerts
- `GET /teams/{id}/benchmarks` - Performance targets
- `GET /health` - API health

---

## Key Concepts

### CAQI Score (0-500)
Code quality metric on a 0-500 scale:
- **A+ (450-500):** Excellent
- **A (400-449):** Very Good
- **B+ (350-399):** Good
- **B (300-349):** Acceptable
- **C (200-299):** Poor
- **F (0-99):** Failing

### 6 Dimensions
1. **Security** - Vulnerability detection
2. **Complexity** - Code complexity analysis
3. **Documentation** - Doc coverage
4. **Testing** - Test coverage
5. **Dependencies** - Dependency management
6. **Maintainability** - Code maintainability

### Severity Levels
- **Critical** - Requires immediate action
- **High** - Should be addressed soon
- **Medium** - Can be addressed later
- **Low** - Minor issue

---

## Debugging Tips

### Frontend Issues
1. Open DevTools (F12 → Console tab)
2. Check for JavaScript errors
3. Check Network tab for API calls
4. Verify `REACT_APP_API_URL` environment variable

### Backend Issues
1. Check logs: `docker-compose logs backend`
2. Verify database connection: `psql postgresql://...`
3. Test endpoint: `curl http://localhost:8000/api/v1/analytics/health`
4. Check Python errors in logs

### Connection Issues
```bash
# Test API connectivity
curl http://localhost:8000/api/v1/analytics/health

# Test frontend connectivity
curl http://localhost:3000

# Check container health
docker-compose ps
```

---

## Important Files

### Frontend
- **src/services/apiClient.ts** - All API calls
- **components/CAQIGauge.tsx** - Quality gauge
- **components/AnomaliesTable.tsx** - Issues table
- **components/DeveloperContributions.tsx** - Team metrics
- **src/__tests__/** - Tests

### Backend
- **main.py** - App entry point
- **routes/advanced_analytics.py** - 8 API endpoints
- **services/alerting_service.py** - Alert logic
- **tests/** - Backend tests

---

## Testing Workflow

### Before Committing
```bash
# 1. Run frontend tests
cd frontend && npm test

# 2. Run backend tests
cd api && pytest

# 3. Build for production
npm run build

# 4. Lint code
npm run lint
```

### Running Specific Tests
```bash
# Frontend - specific test file
npm test CAQIGauge.test.tsx

# Backend - specific test file
pytest tests/test_api_integration.py

# Backend - specific test
pytest tests/test_api_integration.py::TestCAQIEndpoint::test_get_team_caqi_success
```

---

## Git Workflow

### Creating a Feature
```bash
# Create feature branch
git checkout -b feature/anomaly-filtering

# Make changes and commit
git commit -m "Add severity filtering to anomalies"

# Push branch
git push origin feature/anomaly-filtering

# Create pull request on GitHub
```

### Code Review Checklist
- [ ] Tests pass locally
- [ ] Code follows style guide
- [ ] No hardcoded secrets
- [ ] Documentation updated
- [ ] Commit messages clear

### Merging
```bash
# Merge to main
git checkout main
git merge feature/anomaly-filtering
git push origin main
```

---

## Useful Resources

- **API Documentation:** `docs/API_DOCUMENTATION.md`
- **Developer Guide:** `docs/DEVELOPER_GUIDE.md`
- **Component Guide:** `docs/COMPONENT_INTEGRATION_GUIDE.md`
- **Deployment Guide:** `docs/DEPLOYMENT_GUIDE.md`
- **Test Examples:** `frontend/src/__tests__/integration.e2e.test.ts`

---

## Common Issues & Solutions

### "npm install fails"
```bash
# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### "Port 3000 already in use"
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm start
```

### "Docker container fails to start"
```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### "API returning 422 errors"
Check parameter validation against API_DOCUMENTATION.md:
- `days` must be 1-365
- `severity` must be low, medium, high, or critical
- `dimension` must be security, complexity, documentation, testing, dependencies, or maintainability

---

## Getting Help

### Resources
1. Check documentation in `docs/`
2. Search similar issues in GitHub
3. Ask in team Slack/chat
4. Check logs for error messages

### Reporting Issues
When reporting a bug, include:
1. Steps to reproduce
2. Expected vs actual behavior
3. Environment (OS, Node/Python version)
4. Error logs
5. Screenshots (if applicable)

---

## Next Steps

1. **Complete this guide** - 5 minutes
2. **Start local dev server** - 5 minutes
3. **Review API documentation** - 10 minutes
4. **Run the tests** - 2 minutes
5. **Make your first change** - 30 minutes

You're now ready to contribute to CodePulse AI!

---

## Quick Reference

| Task | Command |
|------|---------|
| Start services | `docker-compose up` |
| Stop services | `docker-compose down` |
| Run tests | `npm test && pytest` |
| View logs | `docker-compose logs -f` |
| Build frontend | `npm run build` |
| Test API | `curl http://localhost:8000/api/v1/analytics/health` |
| Format code | `black . && npm run lint` |

---

**Welcome to the team! Happy coding! 🚀**

---

**Last Updated:** 2026-06-06  
**Questions?** Ask your team lead or check the documentation.
