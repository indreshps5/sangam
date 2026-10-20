# SANGAM — Predictive Logistics & Forward Supply Chain

## Architecture Overview

SANGAM is a predictive logistics platform that provides demand forecasting,
shipment tracking, and warehouse management for supply chain optimization.

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Vercel)                     │
│  React + TypeScript + Tailwind CSS + Recharts               │
│  apps/web (root)                                            │
└────────────────────────────┬────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────┐
│                     API Gateway (FastAPI)                     │
│  Router → Service → Repository → Database                   │
│  apps/api                                                   │
└───────────┬────────────────────────────────┬────────────────┘
            │                                │
┌───────────▼──────────┐       ┌─────────────▼───────────────┐
│   PostgreSQL (DB)     │       │     ML Service (Python)     │
│   Managed / Docker    │       │     Forecasting Models      │
│   infra/database      │       │     ml/                     │
└──────────────────────┘       └─────────────────────────────┘
```

## Monorepo Structure

```
sangam/
├── src/                    # Frontend source (apps/web)
├── index.html              # Frontend entry point
├── vite.config.js          # Vite build configuration
├── apps/
│   └── api/                # FastAPI backend
│       ├── src/sangam_api/
│       │   ├── main.py           # Application factory
│       │   ├── config.py         # Settings (pydantic-settings)
│       │   ├── api/              # HTTP layer
│       │   │   ├── routes/       # Thin controllers
│       │   │   ├── schemas/      # Pydantic request/response
│       │   │   └── middleware.py # Error handling
│       │   ├── services/         # Business logic
│       │   ├── repositories/     # Data access (interface + impl)
│       │   ├── models/           # SQLAlchemy ORM
│       │   └── core/             # Cross-cutting (db, logging, exceptions)
│       └── pyproject.toml
├── packages/
│   └── contracts/          # Shared API types (TypeScript)
├── ml/                     # ML models & evaluation
├── infra/                  # Database, Docker, deployment
├── docs/                   # Architecture & setup documentation
├── tests/                  # Integration & E2E tests
├── .editorconfig           # CRLF enforcement
└── .gitattributes          # Line ending normalization
```

## Backend Architecture (SOLID)

```
Request → Router (thin) → Application Service → Repository Interface → Repository Impl → DB
```

- **Router**: Only handles HTTP concerns (parsing, status codes)
- **Service**: Contains business logic and orchestration
- **Repository Interface**: Abstract contract (dependency inversion)
- **Repository Impl**: Concrete data access (SQLAlchemy)

## Setup Commands

### Frontend
```bash
npm install
npm run dev        # Development server on port 3000
npm run build      # Production build
npm run typecheck  # TypeScript validation
```

### Backend
```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
uvicorn sangam_api.main:app --reload
```

### Database
```bash
# Using Docker
docker-compose -f infra/docker/docker-compose.yml up -d

# Or connect to external PostgreSQL
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/sangam"
```

### Full Stack
```bash
# Terminal 1: Database
docker-compose -f infra/docker/docker-compose.yml up -d

# Terminal 2: API
cd apps/api && uvicorn sangam_api.main:app --reload

# Terminal 3: Frontend
npm run dev
```

## Deployment

### Frontend → Vercel
- Static SPA deployment
- Environment variables for API URL
- See `vercel.json` for configuration

### API → Railway / Fly.io
- Persistent server (not serverless)
- Requires always-on process for background tasks
- Docker deployment recommended

### Limitations
- Vercel serverless functions have 10s timeout (Hobby) / 60s (Pro)
- Background ML jobs cannot run in serverless - use separate service
- WebSocket connections not supported on Vercel Hobby plan
- Database connections must use connection pooling (e.g., Neon, Supabase)

## Environment Variables

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api/v1
```

### Backend (apps/api/.env)
```
DATABASE_URL=postgresql+asyncpg://sangam:sangam@localhost:5432/sangam
DEBUG=true
LOG_FORMAT=console
SECRET_KEY=change-me-in-production
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```
