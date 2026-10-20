# SANGAM Infrastructure
# Database, deployment, and environment configuration

## Structure
```
infra/
├── database/
│   ├── migrations/          # SQL migration files
│   └── alembic.ini          # Alembic configuration
├── docker/
│   ├── Dockerfile.api       # API container
│   └── docker-compose.yml   # Local development stack
├── k8s/                     # Kubernetes manifests (future)
└── vercel/                  # Vercel deployment config
```

## Local Development
```bash
# Start PostgreSQL
docker-compose -f infra/docker/docker-compose.yml up -d

# Run migrations
alembic upgrade head
```

## Deployment Notes
- **Frontend**: Deployed to Vercel (static site, SPA)
- **API**: Deployed to Railway/Fly.io (persistent server)
- **Database**: Managed PostgreSQL (Supabase/Neon/Railway)
- **ML Service**: Separate deployment with GPU support (if needed)
