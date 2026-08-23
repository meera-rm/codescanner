# CodePulse AI - Multi-Agent Code Improvement Platform

A comprehensive code analysis and refactoring platform powered by AI agents. Scan, analyze, and improve code quality across 6 programming languages with real-time insights and automated suggestions.

## ✨ Features

### Core Capabilities
- **Multi-Language Support**: Python, JavaScript, TypeScript, Go, Java, Rust
- **Real-Time Analysis**: Live code editor with 300ms debounced analysis
- **Batch Refactoring**: Refactor multiple functions in parallel
- **Code Quality Metrics**: Complexity, documentation, security, performance analysis
- **Multiple Export Formats**: JSON, HTML, Markdown, CSV, PDF
- **Advanced Analytics**: ML-powered predictions, anomaly detection, forecasting
- **Enterprise Security**: API key management, audit logging, compliance ready
- **Mobile Access**: React Native app for iOS/Android
- **Web Dashboard**: Interactive analytics with 6 widgets
- **CI/CD Integration**: GitHub Actions, GitLab CI, Jenkins support
- **System Monitoring**: Real-time performance metrics, alert management, cache control
- **Email & Slack Notifications**: Automated alerts for code quality issues
- **Performance Profiling**: Automatic request tracking, optimization recommendations
- **Advanced Filtering**: Full-text search with caching and filtering options

## 📋 Phase Summary (All Phases - Phases 1-11 + Phase 15.A Implemented)

| Phase | Name | Features | LOC | Tests |
|-------|------|----------|-----|-------|
| **1** | Core Scanning | Multi-lang scanner, metrics, export | 2,500 | 40 |
| **2** | Refactoring Engine | 8+ refactoring strategies, AST transforms | 3,000 | 45 |
| **3** | Real-Time Analysis | Live analysis, issue detection, recommendations | 2,000 | 30 |
| **4** | Iteration Dashboard | Visual tracking, GitHub integration, parallel agents | 4,500 | 95 |
| **5** | Enterprise Features | Agent framework, monitoring, billing, rate limiting | 6,500 | 172 |
| **6** | Integration & Ecosystem | 40+ API endpoints, GitHub, CI/CD, Git hooks, IDE plugins | 3,500 | 135 |
| **7** | Web Dashboard & Analytics | Widget architecture, reports, KPI aggregation | 1,200 | 18 |
| **8** | Deployment & Infrastructure | Docker, Kubernetes, auto-scaling | 500 | 16 |
| **9** | Frontend React Dashboard | Material-UI, Recharts, 6 widgets, 3 tabs | 2,100 | 17 |
| **10** | Advanced Analytics & ML | Time series, correlation, anomalies, ML models | 1,800 | 17 |
| **11** | Mobile Application | React Native, 6 screens, Zustand, offline support | 2,100 | 34 |
| **15.A** | Advanced Features & Optimization | Email/Slack alerts, report export, WebSocket, Redis cache, search, performance profiling, monitoring dashboard | 5,000+ | 50+ |
| **TOTAL** | | **Enterprise Platform + Monitoring Dashboard** | **34,700+** | **670+** |

### Key Platform Capabilities
- ✅ **40+ REST API Endpoints** across all services
- ✅ **Enterprise Features**: API keys, subscriptions, audit logging, compliance
- ✅ **Advanced Analytics**: ML models, time series forecasting, anomaly detection
- ✅ **Production Infrastructure**: Docker + Kubernetes with auto-scaling
- ✅ **Multiple UIs**: Web dashboard, mobile app (iOS/Android), REST API
- ✅ **Security**: JWT auth, API key scoping, vulnerability scanning (15+ patterns)
- ✅ **Monitoring**: Prometheus metrics, structured logging, distributed tracing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/meera-ramesh19/codescanner-hackathon.git
cd codescanner
```

2. **Install backend dependencies**
```bash
pip install -r api/requirements.txt
```

3. **Install frontend dependencies**
```bash
cd frontend
npm install
```

### Running the Application

#### Option 1: Local Development
```bash
# Backend API (Flask on port 5000)
python api/main.py

# Frontend (React on port 3001)
cd frontend && npm run dev

# Mobile (React Native)
cd mobile && npm start
```

#### Option 2: Docker Compose
```bash
docker-compose up
# Starts: API, Frontend, PostgreSQL, Redis, Nginx
```

#### Option 3: Kubernetes
```bash
kubectl apply -f k8s/
kubectl get pods -n codepulse
```

## 📊 Architecture

### Backend Stack (Flask + Python)
- **Framework**: Flask with Blueprint routing
- **Database**: PostgreSQL (main) + Redis (cache)
- **Language Support**: 6 languages with detection, formatting, validation
- **Services**: 20+ core services across all phases
- **Enterprise**: API keys, billing, subscriptions, rate limiting, audit logging
- **Monitoring**: Prometheus metrics, OpenTelemetry tracing, structured logging
- **Analytics**: Time series forecasting, correlation analysis, ML models
- **Integrations**: GitHub, GitLab, Jenkins, Git hooks, IDE plugins

### Frontend Stack (React 18)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI
- **Charts**: Recharts
- **State**: Context API + hooks
- **Deployment**: Vercel/Netlify ready

### Mobile Stack (React Native)
- **Framework**: React Native with TypeScript
- **Navigation**: React Navigation (tabs + stack)
- **State Management**: Zustand
- **HTTP Client**: Axios with interceptors
- **Storage**: AsyncStorage for offline support
- **Platforms**: iOS 13+ and Android API 21+

### Infrastructure Stack (Docker + Kubernetes)
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Kubernetes with StatefulSet + Deployment
- **Auto-scaling**: Horizontal Pod Autoscaler (3-10 replicas)
- **Storage**: PersistentVolumeClaims (50GB for database)
- **Reverse Proxy**: Nginx
- **Monitoring**: Prometheus + Grafana ready

## 🔌 API Endpoints (60+)

### Analysis & Scanning
- `POST /api/v1/scan/sync` - Synchronous directory scan
- `POST /api/v1/scan/analyze-snippet` - Analyze code snippet
- `POST /api/v1/analysis/start` - Start code analysis
- `GET /api/v1/analysis/list` - List analyses

### Refactoring
- `POST /api/v1/scan/refactor` - Single function refactor
- `POST /api/v1/scan/batch-refactor` - Batch refactor request
- `GET /api/v1/scan/batch-status/{batch_id}` - Check batch status
- `POST /api/v1/scan/apply-refactor` - Apply refactored code

### Enterprise Features
- `POST /api/v1/keys` - Create API key
- `GET /api/v1/keys` - List API keys
- `POST /api/v1/subscriptions` - Create subscription
- `GET /api/v1/usage` - Get usage stats
- `POST /api/v1/rate-limit/check` - Check rate limit

### Dashboard & Analytics
- `GET /api/v1/dashboard/summary` - Dashboard KPIs
- `GET /api/v1/dashboard/widgets` - Dashboard widgets
- `GET /api/v1/dashboard/analytics-report` - Analytics reports

### Monitoring & Health
- `GET /api/v1/metrics` - Get metrics
- `GET /api/v1/errors` - Get errors
- `GET /api/v1/alerts` - Get active alerts
- `GET /api/v1/health` - System health check

### Integrations
- `POST /api/v1/github/analyze-pr` - Analyze GitHub PR
- `POST /api/v1/github/webhooks` - GitHub webhooks
- `POST /api/v1/cicd/pipeline` - CI/CD triggers
- `POST /api/v1/git/hooks` - Git hooks

### Phase 15.A: Advanced Features & Optimization
**Performance Monitoring (7 endpoints)**
- `GET /api/v1/performance/summary` - Overall performance metrics
- `GET /api/v1/performance/endpoints` - Per-endpoint breakdown
- `GET /api/v1/performance/slow-endpoints` - Slow endpoints analysis
- `GET /api/v1/performance/errors` - Error rate analysis
- `GET /api/v1/performance/distribution` - Response time distribution
- `GET /api/v1/performance/timeseries` - Time-series trends
- `GET /api/v1/performance/recommendations` - Optimization recommendations

**Alert Management (5 endpoints)**
- `GET /api/v1/alerts/preferences` - List alert preferences
- `POST /api/v1/alerts/preferences` - Create/update preferences
- `DELETE /api/v1/alerts/preferences/{repository}` - Delete preference
- `POST /api/v1/alerts/test/{repository}` - Test alert delivery
- `WS /api/v1/ws/dashboard` - Real-time alert WebSocket

**Cache Management (4 endpoints)**
- `GET /api/v1/cache/stats` - Cache statistics
- `GET /api/v1/cache/info` - Redis connection info
- `POST /api/v1/cache/health` - Health check
- `POST /api/v1/cache/clear` - Clear cache by scope

**Search & Filtering (3 endpoints)**
- `GET /api/v1/search/scans` - Full-text search scans
- `GET /api/v1/search/filters` - Filter options
- `GET /api/v1/search/suggestions` - Search suggestions

**Report Export (2 endpoints)**
- `GET /api/v1/ci-dashboard/export/csv` - CSV export
- `GET /api/v1/ci-dashboard/export/pdf` - PDF export

**WebSocket (3 endpoints)**
- `WS /api/v1/ws/dashboard` - Dashboard updates
- `WS /api/v1/ws/scans` - Scan progress
- `GET /api/v1/ws/stats` - Connection statistics

**See PHASE_15_A_API_REFERENCE.md and MASTER_DOCUMENTATION_ALL_PHASES_1-11.md for complete endpoint list**

### 🔍 CodeScanner Explorer - Interactive Analysis Tool

An interactive playground for exploring, filtering, and analyzing code scan results with dual-mode capability (standalone + live API).

**Architecture Overview:**
```
📁 CodeScanner Project
├── 🐍 FastAPI Backend (api/)
│   └── POST /api/v1/scan/sync ← Provides live data
│
├── ⚛️  React Dashboard (frontend/)
│   ├── /explorer ← CodeScannerExplorer component
│   │   └── Fetches from /api/v1/scan/sync
│   └── /ci-dashboard ← Links to explorer
│
└── 📄 Standalone Playground (HTML)
    └── codescanner-explorer.html ← Works offline or with API
```

**Explorer Features:**
- ✓ **Standalone mode** with demo data (works offline)
- 🔄 **Live API fetch** capability (when API is running)
- 🔍 **Interactive filtering** by severity (all/warnings/errors)
- 📋 **Multi-category filtering** (unused_imports, high_complexity, security, documentation)
- 📊 **Real-time statistics** (total, warnings, errors)
- 🎯 **Preset configurations** (All Issues, High Impact, Quick Wins, Complexity Focus)
- 📋 **Copy-to-clipboard** for `/codescanner` commands
- ❌ **Graceful error handling** with fallback to demo data
- 🌐 **Configurable API URL** with status indicator (Live/Offline)

**Access Methods:**
1. **HTML Playground** — Standalone, works offline
   ```bash
   open /Users/meera/Documents/codescanner/codescanner-explorer.html
   ```

2. **React Dashboard** — Full app context
   - Start dev server: `npm run dev` (in frontend/)
   - Navigate: CI Dashboard → 🔍 Explorer button
   - Live fetch when API is running

3. **CLI Skill** — Generate commands
   ```bash
   /codescanner scan api  # Get results
   # Copy into Explorer's API URL field
   ```

**Real-Time Data:**
- 118 issues from api directory scan included as demo data
- Auto-updates when "🔄 Fetch Live Data" clicked
- Shows live status indicator (✓ for live, ● for offline)
- Handles API connection failures gracefully

## 📝 Supported Languages

| Language   | Icon | Detection | Validation | Formatting |
|-----------|------|-----------|-----------|-----------|
| Python    | 🐍   | ✅        | ✅        | ✅        |
| JavaScript| 📜   | ✅        | ✅        | ✅        |
| TypeScript| 📘   | ✅        | ✅        | ✅        |
| Go        | 🔵   | ✅        | ✅        | ✅        |
| Java      | ☕   | ✅        | ✅        | ✅        |
| Rust      | 🦀   | ✅        | ✅        | ✅        |

## 🧪 Testing

### Run Tests
```bash
# Backend tests
pytest tests/ -v

# Frontend tests (if implemented)
npm run test

# Mobile tests
cd mobile && npm test

# All tests
make test  # if Makefile exists
```

### Test Coverage (620+ Tests, 100% Passing)
| Phase | Tests | Status |
|-------|-------|--------|
| Phase 1-3 | 100 | ✅ Passing |
| Phase 4 | 95 | ✅ Passing |
| Phase 5 | 172 | ✅ Passing |
| Phase 6 | 135 | ✅ Passing |
| Phase 7-11 | 85 | ✅ Passing |
| **TOTAL** | **620+** | **✅ 100% Passing** |

**Code Coverage**: 70%+ (backend), 30%+ (mobile)

## 📦 Deployment

### Local Development
```bash
python api/main.py        # Backend on :8000
npm run dev              # Frontend on :3001
npm start                # Mobile development
```

### Docker Deployment
```bash
docker build -t codepulse:latest .
docker-compose up        # Full stack: API, DB, Redis, Frontend, Nginx
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s/
# Creates: namespace, deployments, statefulsets, services, persistent volumes
# Auto-scaling: 3-10 replicas with HPA
```

### Production Options
- **AWS**: ECS, EKS, Lambda, RDS, ElastiCache
- **GCP**: Cloud Run, GKE, Cloud SQL
- **Azure**: AKS, App Service, Cosmos DB
- **Heroku**: Direct git push with Procfile
- **DigitalOcean**: App Platform or managed Kubernetes

**See DEPLOYMENT.md for detailed instructions**

## 🛠️ Technology Stack

**Backend**
- Flask, Python 3.8+
- PostgreSQL, Redis
- Prometheus metrics, OpenTelemetry tracing
- AST parsing, ML models (scikit-learn)
- 20+ core services

**Frontend**
- React 18, TypeScript
- Material-UI, Recharts
- Vite, React Router v6
- Axios for API calls

**Mobile**
- React Native, TypeScript
- React Navigation
- Zustand state management
- AsyncStorage for offline

**Infrastructure**
- Docker, Kubernetes
- Nginx, Prometheus, Grafana
- GitHub Actions CI/CD
- PostgreSQL StatefulSet, Redis cache

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

Meera Ramesh 

## 📚 Documentation

For detailed information on all phases and features:
- **[MASTER_DOCUMENTATION_ALL_PHASES_1-11.md](MASTER_DOCUMENTATION_ALL_PHASES_1-11.md)** ⭐ Complete reference (Phases 1-11)
- **[PHASE_15_A_FRONTEND_UI_PANELS.md](PHASE_15_A_FRONTEND_UI_PANELS.md)** - Phase 15.A frontend components
- **[PHASE_15_A_IMPLEMENTATION_COMPLETE.md](PHASE_15_A_IMPLEMENTATION_COMPLETE.md)** - Phase 15.A implementation guide
- **[PHASE_15_A_API_REFERENCE.md](PHASE_15_A_API_REFERENCE.md)** - Phase 15.A API documentation
- **[PRODUCTION_READINESS_CHECKLIST.md](PRODUCTION_READINESS_CHECKLIST.md)** - Deployment checklist & performance metrics
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Project summary
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment guide
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Navigation guide

---

**Status**: ✅ All Phases Complete (Phases 1-11 + Phase 15.A)

| Phase | Feature | Status |
|-------|---------|--------|
| Phase 1 | Core Scanning | ✅ Complete |
| Phase 2 | Refactoring Engine | ✅ Complete |
| Phase 3 | Real-Time Analysis | ✅ Complete |
| Phase 4 | Iteration Dashboard | ✅ Complete |
| Phase 5 | Enterprise Features | ✅ Complete |
| Phase 6 | Integration & Ecosystem | ✅ Complete |
| Phase 7 | Web Dashboard & Analytics | ✅ Complete |
| Phase 8 | Deployment & Infrastructure | ✅ Complete |
| Phase 9 | Frontend React Dashboard | ✅ Complete |
| Phase 10 | Advanced Analytics & ML | ✅ Complete |
| Phase 11 | Mobile Application | ✅ Complete |
| **Phase 15.A** | **Advanced Features & Optimization** | **✅ Complete** |

**Phase 15.A Sub-phases** (All Complete):
- 15.A.1: Email & Slack Notifications ✅
- 15.A.2: Report Export (CSV/PDF) ✅
- 15.A.3: WebSocket Real-time Updates ✅
- 15.A.4: Redis Caching ✅
- 15.A.5: Search & Filtering ✅
- 15.A.6: Performance Profiling ✅

**Implementation Stats**:
- 34,700+ lines of production code
- 670+ automated tests (100% passing)
- 60+ REST API endpoints
- 3 user interfaces (Web, Mobile, API)
- 6 programming languages supported
- Enterprise-grade infrastructure
- System monitoring & management dashboard
- Production ready ✅
