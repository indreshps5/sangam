# SANGAM Deployment Guide

Complete deployment instructions for the SANGAM platform across all environments.

## Table of Contents

1. [Deployment Architecture](#deployment-architecture)
2. [Prerequisites](#prerequisites)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Backend Deployment](#backend-deployment)
6. [Frontend Deployment](#frontend-deployment)
7. [MQTT Worker Deployment](#mqtt-worker-deployment)
8. [Production Hardening](#production-hardening)
9. [Monitoring & Logging](#monitoring--logging)
10. [Backup & Recovery](#backup--recovery)
11. [Troubleshooting](#troubleshooting)

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Vercel)                     │
│  React + TypeScript + Tailwind CSS                          │
│  - Static site with Service Worker                          │
│  - Offline support with IndexedDB                           │
│  - Auto-deployed from Git                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (Railway/Fly.io)              │
│  FastAPI + Python 3.11 + SQLAlchemy                         │
│  - RESTful API with JWT authentication                      │
│  - Async database operations                                │
│  - Auto-deployed from Git                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ TCP 5432
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Database (Neon/Supabase/Railway)                │
│  PostgreSQL 15+                                             │
│  - Managed service with backups                             │
│  - Connection pooling                                       │
│  - SSL/TLS encryption                                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              MQTT Worker (Separate Service)                  │
│  Python + Paho MQTT                                         │
│  - Persistent connection to MQTT broker                     │
│  - Cannot run in serverless                                 │
│  - Deploy on Railway/Fly.io/VPS                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Required Accounts

1. **Vercel** (Frontend)
   - Sign up: https://vercel.com/signup
   - Connect GitHub repository

2. **Railway** or **Fly.io** (Backend)
   - Railway: https://railway.app/
   - Fly.io: https://fly.io/

3. **Neon** or **Supabase** (Database)
   - Neon: https://neon.tech/
   - Supabase: https://supabase.com/

4. **MQTT Broker** (IoT)
   - HiveMQ: https://www.hivemq.com/
   - EMQX: https://www.emqx.com/
   - Or self-hosted Mosquitto

### Required Tools

```bash
# Node.js 18+ and npm
node --version  # Should be 18+
npm --version

# Python 3.11+
python --version  # Should be 3.11+

# Git
git --version

# Docker (optional, for local testing)
docker --version

# Railway CLI (if using Railway)
npm i -g @railway/cli

# Fly.io CLI (if using Fly.io)
curl -L https://fly.io/install.sh | sh
```

---

## Environment Configuration

### Frontend Environment Variables (Vercel)

Set these in Vercel Dashboard → Settings → Environment Variables:

```bash
# API endpoint (use your deployed backend URL)
VITE_API_URL=https://your-backend.railway.app/api/v1

# For production
VITE_API_URL=https://api.yourdomain.com/api/v1
```

### Backend Environment Variables (Railway/Fly.io)

Set these in your deployment platform's environment variables:

```bash
# Application
APP_NAME=SANGAM API
APP_VERSION=0.1.0
DEBUG=false
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=8000

# Database (get from your database provider)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/sangam?sslmode=require

# Connection pool
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# CORS (use your frontend domain)
CORS_ORIGINS=["https://your-frontend.vercel.app"]

# Logging
LOG_LEVEL=WARNING
LOG_FORMAT=json

# Security (GENERATE SECURE KEY)
SECRET_KEY=<generate-with-python-c-secrets-print-secrets.token_urlsafe-64->
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ML Service (if separate)
ML_SERVICE_URL=https://your-ml-service.railway.app

# MQTT (for IoT module)
MQTT_BROKER_HOST=your-mqtt-broker.com
MQTT_BROKER_PORT=8883
MQTT_USERNAME=your-mqtt-username
MQTT_PASSWORD=your-mqtt-password
MQTT_USE_TLS=true
MQTT_TOPIC_PREFIX=sangam/sensors
```

### Generate Secure Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copy the output and use it as `SECRET_KEY`.

---

## Database Setup

### Option 1: Neon (Recommended for Vercel)

1. **Create Database**
   - Go to https://neon.tech/
   - Create new project
   - Create new database
   - Copy connection string

2. **Connection String Format**
   ```
   postgresql+asyncpg://user:password@host:5432/sangam?sslmode=require
   ```

3. **Run Migrations**
   ```bash
   cd apps/api
   source .venv/bin/activate
   alembic upgrade head
   ```

4. **Seed Data**
   ```bash
   python -m sangam_api.scripts.seed
   ```

### Option 2: Supabase

1. **Create Project**
   - Go to https://supabase.com/
   - Create new project
   - Wait for database to be ready

2. **Get Connection String**
   - Go to Project Settings → Database
   - Copy Connection string (URI)
   - Format for asyncpg:
     ```
     postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
     ```

3. **Run Migrations**
   ```bash
   cd apps/api
   alembic upgrade head
   python -m sangam_api.scripts.seed
   ```

### Option 3: Railway PostgreSQL

1. **Create Database**
   - In Railway dashboard, create new PostgreSQL database
   - Get connection details

2. **Connection String**
   ```
   postgresql+asyncpg://user:password@host:5432/sangam
   ```

3. **Run Migrations**
   ```bash
   cd apps/api
   alembic upgrade head
   python -m sangam_api.scripts.seed
   ```

---

## Backend Deployment

### Option A: Railway (Recommended)

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   railway init
   # Select: Create new project
   # Name: sangam-api
   ```

4. **Configure Environment**
   ```bash
   railway variables set DATABASE_URL="your-database-url"
   railway variables set SECRET_KEY="your-secret-key"
   railway variables set CORS_ORIGINS='["https://your-frontend.vercel.app"]'
   ```

5. **Deploy**
   ```bash
   railway up
   ```

6. **Get URL**
   ```bash
   railway domain
   # Returns: https://your-app.railway.app
   ```

### Option B: Fly.io

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Launch App**
   ```bash
   fly launch
   # Name: sangam-api
   # Region: choose closest
   # Create PostgreSQL: No (use external)
   ```

4. **Set Secrets**
   ```bash
   fly secrets set DATABASE_URL="your-database-url"
   fly secrets set SECRET_KEY="your-secret-key"
   fly secrets set CORS_ORIGINS='["https://your-frontend.vercel.app"]'
   ```

5. **Deploy**
   ```bash
   fly deploy
   ```

6. **Get URL**
   ```bash
   fly status
   # Shows: https://sangam-api.fly.dev
   ```

### Option C: Docker (Self-hosted)

1. **Build Image**
   ```bash
   docker build -f infra/docker/Dockerfile.api -t sangam-api:latest .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     --name sangam-api \
     -p 8000:8000 \
     -e DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/sangam" \
     -e SECRET_KEY="your-secret-key" \
     -e CORS_ORIGINS='["https://your-frontend.com"]' \
     -e ENVIRONMENT=production \
     -e DEBUG=false \
     sangam-api:latest
   ```

3. **Verify**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

---

## Frontend Deployment

### Vercel Deployment

1. **Connect Repository**
   - Go to https://vercel.com/new
   - Import GitHub repository
   - Select `sangam` repository

2. **Configure Build Settings**
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

3. **Set Environment Variables**
   - VITE_API_URL: `https://your-backend.railway.app/api/v1`

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Get URL: `https://your-project.vercel.app`

5. **Custom Domain (Optional)**
   - Go to Project Settings → Domains
   - Add your domain
   - Configure DNS records

### Verify Deployment

```bash
# Check frontend
curl https://your-frontend.vercel.app

# Check API connection
curl https://your-frontend.vercel.app/api/v1/health
```

---

## MQTT Worker Deployment

**Important**: MQTT worker cannot run in serverless environments. Deploy as a separate service.

### Option A: Railway Background Worker

1. **Create New Service**
   ```bash
   railway init
   # Name: sangam-mqtt-worker
   ```

2. **Configure**
   ```bash
   railway variables set MQTT_BROKER_HOST="your-broker.com"
   railway variables set MQTT_BROKER_PORT="8883"
   railway variables set MQTT_USERNAME="your-username"
   railway variables set MQTT_PASSWORD="your-password"
   railway variables set MQTT_USE_TLS="true"
   railway variables set DATABASE_URL="your-database-url"
   ```

3. **Set Start Command**
   ```bash
   railway variables set RAILWAY_START_COMMAND="python -m sangam_api.iot.mqtt_worker"
   ```

4. **Deploy**
   ```bash
   railway up
   ```

### Option B: Fly.io Dedicated Service

1. **Create New App**
   ```bash
   fly launch --name sangam-mqtt-worker
   ```

2. **Set Secrets**
   ```bash
   fly secrets set MQTT_BROKER_HOST="your-broker.com"
   fly secrets set MQTT_USERNAME="your-username"
   fly secrets set MQTT_PASSWORD="your-password"
   fly secrets set DATABASE_URL="your-database-url"
   ```

3. **Deploy**
   ```bash
   fly deploy
   ```

### Option C: VPS with Systemd

1. **Create Service File**
   ```bash
   sudo nano /etc/systemd/system/sangam-mqtt.service
   ```

2. **Service Configuration**
   ```ini
   [Unit]
   Description=SANGAM MQTT Worker
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/opt/sangam/apps/api
   Environment="MQTT_BROKER_HOST=your-broker.com"
   Environment="MQTT_USERNAME=your-username"
   Environment="MQTT_PASSWORD=your-password"
   Environment="DATABASE_URL=your-database-url"
   ExecStart=/opt/sangam/apps/api/.venv/bin/python -m sangam_api.iot.mqtt_worker
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and Start**
   ```bash
   sudo systemctl enable sangam-mqtt
   sudo systemctl start sangam-mqtt
   sudo systemctl status sangam-mqtt
   ```

---

## Production Hardening

### 1. Security Headers

Add to `apps/api/src/sangam_api/main.py`:

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Add security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

### 2. Rate Limiting

Install slowapi:
```bash
pip install slowapi
```

Add to `main.py`:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...
```

### 3. HTTPS Redirect

For production, ensure all traffic uses HTTPS:

```python
@app.middleware("https")
async def https_redirect(request, call_next):
    if not request.url.scheme == "https":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url=url)
    return await call_next(request)
```

### 4. Database Connection Security

Ensure SSL is enabled:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/sangam?sslmode=require
```

### 5. API Key Rotation

Implement regular secret key rotation:
```bash
# Generate new key
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Update environment variable
# Deploy with new key
# Old tokens will be invalidated
```

---

## Monitoring & Logging

### 1. Application Monitoring

**Recommended**: DataDog, New Relic, or Sentry

**Sentry Setup**:
```bash
pip install sentry-sdk[fastapi]
```

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### 2. Logging Configuration

Production logging setup:
```python
import logging
import json

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/sangam/api.log')
    ]
)
```

### 3. Health Checks

Implement comprehensive health checks:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}
```

### 4. Metrics Collection

Track key metrics:
- API response times
- Error rates
- Database query performance
- Active users
- Offline sync success rate

---

## Backup & Recovery

### 1. Database Backups

**Neon**: Automatic daily backups with point-in-time recovery
**Supabase**: Automatic daily backups
**Railway**: Automatic daily backups

**Manual Backup**:
```bash
pg_dump -h host -U user -d sangam > backup_$(date +%Y%m%d).sql
```

### 2. Restore Procedure

```bash
# Restore from backup
psql -h host -U user -d sangam < backup_20240115.sql

# Verify restore
psql -h host -U user -d sangam -c "SELECT COUNT(*) FROM users;"
```

### 3. Disaster Recovery Plan

1. **RPO (Recovery Point Objective)**: 24 hours (daily backups)
2. **RTO (Recovery Time Objective)**: 4 hours
3. **Backup Frequency**: Daily
4. **Backup Retention**: 30 days
5. **Test Restore**: Monthly

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Symptoms**: API returns 500 errors
**Solution**:
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check firewall rules
# Ensure database allows connections from your IP
```

#### 2. CORS Errors

**Symptoms**: Frontend can't connect to API
**Solution**:
```bash
# Check CORS_ORIGINS
echo $CORS_ORIGINS

# Ensure frontend URL is included
CORS_ORIGINS='["https://your-frontend.vercel.app"]'
```

#### 3. JWT Token Errors

**Symptoms**: 401 Unauthorized errors
**Solution**:
```bash
# Check SECRET_KEY is set
echo $SECRET_KEY

# Ensure same SECRET_KEY on all instances
# Regenerate if compromised
```

#### 4. MQTT Connection Failed

**Symptoms**: No sensor data
**Solution**:
```bash
# Check MQTT credentials
echo $MQTT_BROKER_HOST
echo $MQTT_USERNAME

# Test connection
mosquitto_sub -h $MQTT_BROKER_HOST -u $MQTT_USERNAME -P $MQTT_PASSWORD -t "test"

# Check MQTT worker logs
railway logs -s sangam-mqtt-worker
```

#### 5. Offline Sync Failed

**Symptoms**: Data not syncing after reconnection
**Solution**:
```javascript
// Check browser console for errors
// Verify IndexedDB is not full
// Check network connectivity
// Manually trigger sync
offlineService.sync();
```

### Debug Mode

Enable debug logging:
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

### Support Contacts

- **Vercel Support**: https://vercel.com/support
- **Railway Support**: https://docs.railway.app/
- **Neon Support**: https://neon.tech/support
- **SANGAM Issues**: Create GitHub issue

---

## Deployment Verification Checklist

### Pre-Deployment

- [ ] All environment variables configured
- [ ] Database migrations run
- [ ] Seed data loaded
- [ ] SECRET_KEY generated and secure
- [ ] CORS origins configured correctly
- [ ] SSL/TLS certificates in place
- [ ] DNS records configured
- [ ] Monitoring tools set up
- [ ] Backup strategy documented
- [ ] Disaster recovery plan tested

### Post-Deployment

- [ ] Health check endpoint responds
- [ ] API documentation accessible
- [ ] Frontend loads successfully
- [ ] Login flow works
- [ ] All modules functional
- [ ] Offline mode works
- [ ] MQTT worker connected
- [ ] Logs are being collected
- [ ] Metrics are being tracked
- [ ] Backups are running

### Production Monitoring

- [ ] Error rate < 1%
- [ ] Response time < 500ms
- [ ] Database connections healthy
- [ ] MQTT worker running
- [ ] Offline sync successful
- [ ] No security alerts
- [ ] Backups completing
- [ ] Logs being aggregated

---

## Rollback Procedure

If deployment fails:

### Backend Rollback

**Railway**:
```bash
railway deployment rollback
```

**Fly.io**:
```bash
fly releases
fly rollback
```

### Frontend Rollback

**Vercel**:
```bash
# Go to Deployments tab
# Select previous deployment
# Click "Promote to Production"
```

### Database Rollback

```bash
# Restore from backup
psql -h host -U user -d sangam < backup_before_deployment.sql
```

---

## Cost Estimation

### Development/Staging

| Service | Provider | Cost |
|---------|----------|------|
| Frontend | Vercel Hobby | Free |
| Backend | Railway Hobby | $5/month |
| Database | Neon Free | Free |
| MQTT | HiveMQ Free | Free |
| **Total** | | **$5/month** |

### Production

| Service | Provider | Cost |
|---------|----------|------|
| Frontend | Vercel Pro | $20/month |
| Backend | Railway Pro | $20/month |
| Database | Neon Launch | $19/month |
| MQTT | HiveMQ Professional | $149/month |
| Monitoring | DataDog | $15/host/month |
| **Total** | | **$223+/month** |

---

## Conclusion

This deployment guide provides complete instructions for deploying SANGAM to production. Follow the steps in order, verify each stage, and monitor closely after deployment.

**Key Points**:
- Frontend deploys to Vercel (static site)
- Backend deploys to Railway/Fly.io (persistent server)
- Database uses managed PostgreSQL
- MQTT worker requires separate deployment
- All secrets in environment variables
- Production hardening recommended
- Monitoring essential

**Next Steps**:
1. Review this guide completely
2. Set up staging environment
3. Test all deployment steps
4. Conduct security audit
5. Plan production deployment
6. Set up monitoring
7. Document operational procedures

---

**Last Updated**: 2024-01-15  
**Version**: 1.0.0  
**Status**: Production Ready
