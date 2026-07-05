# CodePulse AI - Multi-Agent Code Improvement Platform

A comprehensive code analysis and refactoring platform powered by AI agents. Scan, analyze, and improve code quality across 6 programming languages with real-time insights and automated suggestions.

## ✨ Features

### Core Capabilities
- **Multi-Language Support**: Python, JavaScript, TypeScript, Go, Java, Rust
- **Real-Time Analysis**: Live code editor with 300ms debounced analysis
- **Batch Refactoring**: Refactor multiple functions in parallel
- **Code Quality Metrics**: Complexity, documentation, security, performance analysis
- **Multiple Export Formats**: JSON, HTML, Markdown, CSV, PDF

### Phase Implementations

#### Phase 5.1 - Enhanced Agent Framework
- Agent registry with YAML/JSON configuration loading
- Sequential and conditional chain execution
- Specialized agents: SecurityAuditor, PerformanceOptimizer, DocumentationGenerator
- Parallel agent execution with semaphore-based concurrency control

#### Phase 5.2 - Production Operations & Observability
- **Metrics Collection**: Prometheus-compatible metrics with 15+ pre-configured metrics
- **Structured Logging**: JSON-based logging with correlation ID tracking
- **Distributed Tracing**: OpenTelemetry-compatible span hierarchy
- **Health Checks**: Parallel component health verification with status aggregation
- **Alert Rules**: 5 pre-configured alert rules with cooldown mechanism and tier-based rate limiting

#### Phase 5.3 - Multi-Language Support
- Language detection via file extension and content patterns
- Language-specific formatters with proper indentation rules
- Comprehensive validators with syntax and linting checks per language
- Language router unified interface for all language operations

#### Phase 5.4 - Enterprise Features
- **API Key Management**: Key generation, validation, scoping with READ/WRITE/ADMIN tiers
- **Usage Tracking**: Operation cost tracking with hourly aggregation
- **Billing Service**: 4-tier subscription model (Free, Starter, Pro, Enterprise)
- **Rate Limiting**: Tier-based limits from 10 to unlimited RPM
- **Audit Logging**: Compliance tracking with 12 audit action types

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

#### Start the Backend API
```bash
python api/main.py
```
API runs on `http://localhost:8000`
- Documentation: `http://localhost:8000/docs`

#### Start the Frontend
```bash
cd frontend
npm run dev
```
Frontend runs on `http://localhost:3001`

## 📊 Architecture

### Backend Stack
- **Framework**: FastAPI (Python)
- **Language Support**: 6 languages with detection, formatting, and validation
- **Agents**: Pluggable agent system with specialized agents
- **Services**: Metrics, logging, tracing, health checks, alerts
- **Enterprise**: API keys, billing, rate limiting, audit logging

### Frontend Stack
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Routing**: React Router v6
- **UI**: Styled with inline CSS for light/dark theme support

## 🔌 API Endpoints

### Scanning
- `POST /api/v1/scan/sync` - Synchronous directory scan
- `POST /api/v1/scan/analyze-snippet` - Analyze code snippet

### Refactoring
- `POST /api/v1/scan/refactor` - Single function refactor
- `POST /api/v1/scan/batch-refactor` - Batch refactor request
- `GET /api/v1/scan/batch-status/{batch_id}` - Check batch status
- `POST /api/v1/scan/apply-refactor` - Apply refactored code

### Enterprise
- `POST /api/v1/keys` - Create API key
- `POST /api/v1/subscriptions` - Create subscription
- `GET /api/v1/usage` - Get usage stats
- `POST /api/v1/rate-limit/check` - Check rate limit

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

# Frontend tests
npm run test

# E2E tests
npm run test:e2e
```

### Test Coverage
- **Phase 5.1**: 18 agent registry tests, 17 chain executor tests, 20 specialized agent tests
- **Phase 5.2**: 20 metrics tests, 12 production operations tests
- **Phase 5.3**: 33 language support tests
- **Phase 5.4**: 30 enterprise features tests

**Total**: 130+ tests, all passing

## 📦 Deployment

### Frontend
- Build: `npm run build`
- Deploy to Vercel, Netlify, or any static host

### Backend
- Docker support (Dockerfile available)
- Deploy to AWS Lambda, Heroku, or any Python-capable host

## 🛠️ Technology Stack

**Backend**
- FastAPI, Pydantic, SQLAlchemy
- Prometheus metrics
- OpenTelemetry tracing
- AST parsing for code analysis

**Frontend**
- React 18, TypeScript
- Vite, React Router
- Axios for API calls

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

Meera Ramesh - Data Engineer & AI Systems Developer

---

**Status**: All 5 phases completed ✅
- Phase 1: Core scanning ✅
- Phase 2: Refactoring engine ✅
- Phase 3: Real-time analysis ✅
- Phase 4: Iteration dashboard ✅
- Phase 5: Enterprise features ✅
