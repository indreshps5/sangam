# SANGAM Setup Guide

## Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 15+ (or Docker)
- Git

## Quick Start

### 1. Clone and Install
```bash
git clone <repository-url>
cd sangam
npm install
```

### 2. Configure Environment
```bash
# Frontend
cp .env.example .env

# Backend
cd apps/api
cp .env.example .env
cd ../..
```

### 3. Start Database
```bash
docker-compose -f infra/docker/docker-compose.yml up -d postgres
```

### 4. Start Backend
```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn sangam_api.main:app --reload --port 8000
```

### 5. Start Frontend
```bash
npm run dev
```

### 6. Verify
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

## Line Endings (CRLF)

This project enforces CRLF line endings for all text source files.

### Verify Configuration
```bash
# Check .editorconfig is recognized
cat .editorconfig

# Check .gitattributes
cat .gitattributes

# Normalize existing files
git add . --renormalize
```

### Editor Support
- **VS Code**: Install "EditorConfig for VS Code" extension
- **IntelliJ**: Built-in EditorConfig support
- **Vim**: `plugin/editorconfig-vim` plugin

## Testing

### Frontend Tests
```bash
npm run test        # Unit tests
npm run test:e2e    # E2E tests (Playwright)
```

### Backend Tests
```bash
cd apps/api
pytest                    # All tests
pytest tests/unit/        # Unit tests only
pytest tests/integration/ # Integration tests
pytest --cov=sangam_api   # With coverage
```

### ML Tests
```bash
cd ml
pytest tests/
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
psql -h localhost -U sangam -d sangam -c "SELECT 1"
```

### Port Conflicts
- Frontend: 3000 (configurable in vite.config.js)
- API: 8000 (configurable via --port flag)
- PostgreSQL: 5432

### CRLF Issues
If you see `\r` characters or linting errors:
```bash
# Re-normalize all files
git rm --cached -r .
git reset --hard
```
