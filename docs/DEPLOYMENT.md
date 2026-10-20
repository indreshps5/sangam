# SANGAM Deployment Guide

## Frontend Deployment (Vercel)

### Automatic Deployment
1. Connect repository to Vercel
2. Build settings are auto-detected from `vite.config.js`
3. Environment variables set in Vercel dashboard

### vercel.json Configuration
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### Environment Variables
| Variable | Description | Example |
|----------|-------------|---------|
| VITE_API_URL | Backend API base URL | https://api.sangam.io/api/v1 |

## API Deployment

### Option 1: Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Option 2: Fly.io
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

### Option 3: Docker (any cloud)
```bash
docker build -f infra/docker/Dockerfile.api -t sangam-api .
docker push <registry>/sangam-api:latest
```

## Database

### Recommended Providers
- **Neon**: Serverless PostgreSQL, great for Vercel integration
- **Supabase**: PostgreSQL + realtime + auth
- **Railway**: Managed PostgreSQL with easy scaling

### Connection String Format
```
postgresql+asyncpg://user:password@host:5432/database?sslmode=require
```

## Limitations & Considerations

### Vercel Serverless Constraints
- **Timeout**: 10s (Hobby) / 60s (Pro) / 900s (Enterprise)
- **Memory**: 1024 MB default
- **No persistent filesystem**: Cannot store model artifacts
- **No long-running processes**: Background jobs need separate service
- **WebSocket**: Not supported on Hobby plan

### Background Jobs
ML model training and batch processing should NOT run in serverless.
Options:
1. **Separate ML service** on Railway/Fly.io with GPU
2. **Serverless ML** using Modal/Replicate for inference only
3. **Cron-based** batch processing via external scheduler

### Database Connections
- Use connection pooling (PgBouncer, Neon serverless driver)
- Serverless functions create new connections per invocation
- Set appropriate pool sizes and timeouts
