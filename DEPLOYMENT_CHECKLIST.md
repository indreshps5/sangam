# SANGAM Deployment Checklist

Use this checklist to ensure all steps are completed before, during, and after deployment.

---

## Pre-Deployment Checklist

### Environment Setup

- [ ] Clone repository to deployment environment
- [ ] Install Node.js 18+ and npm
- [ ] Install Python 3.11+
- [ ] Install PostgreSQL 15+ (or provision managed database)
- [ ] Install Docker (for local testing)
- [ ] Install Railway CLI or Fly.io CLI (for deployment)

### Configuration

- [ ] Copy `.env.example` to `.env` for frontend
- [ ] Set `VITE_API_URL` to production API endpoint
- [ ] Copy `apps/api/.env.example` to `apps/api/.env`
- [ ] Generate secure `SECRET_KEY`: `python -c "import secrets; print(secrets.token_urlsafe(64))"`
- [ ] Set `DATABASE_URL` to production database connection string
- [ ] Set `CORS_ORIGINS` to include frontend domain
- [ ] Set `DEBUG=false` and `ENVIRONMENT=production`
- [ ] Set `LOG_LEVEL=WARNING` and `LOG_FORMAT=json`
- [ ] Configure MQTT credentials (if using IoT module)
- [ ] Review all environment variables for correctness

### Database Preparation

- [ ] Create PostgreSQL database
- [ ] Verify database connection string works
- [ ] Run migrations: `cd apps/api && alembic upgrade head`
- [ ] Run seed script: `python -m sangam_api.scripts.seed`
- [ ] Verify tables created: `\dt` in psql
- [ ] Verify seed data: `SELECT COUNT(*) FROM users;`
- [ ] Create database backup before deployment

### Backend Preparation

- [ ] Install Python dependencies: `pip install -e ".[dev]"`
- [ ] Run backend tests: `pytest`
- [ ] Verify all tests pass
- [ ] Check for any pending migrations
- [ ] Review API documentation at `/docs`
- [ ] Test health endpoint: `curl http://localhost:8000/health`
- [ ] Verify CORS configuration allows frontend domain

### Frontend Preparation

- [ ] Install npm dependencies: `npm install`
- [ ] Run type checking: `npm run typecheck`
- [ ] Verify no TypeScript errors
- [ ] Run build: `npm run build`
- [ ] Verify build successful
- [ ] Check bundle size (should be ~250 KB gzipped)
- [ ] Test production build locally: `npm run preview`

### Security Review

- [ ] Verify no secrets in code: `git grep -i "password\|secret\|api_key"`
- [ ] Verify `.env` files in `.gitignore`
- [ ] Verify no `.env` files committed: `git ls-files | grep .env`
- [ ] Review CORS origins (should be production domains only)
- [ ] Verify JWT secret key is secure and unique
- [ ] Check database credentials are secure
- [ ] Review all environment variables for sensitive data
- [ ] Ensure HTTPS will be enforced in production

### Monitoring Setup

- [ ] Set up application monitoring (DataDog/New Relic/Sentry)
- [ ] Configure error tracking
- [ ] Set up logging aggregation
- [ ] Configure alerting for critical errors
- [ ] Set up uptime monitoring
- [ ] Configure database monitoring
- [ ] Set up performance monitoring

### Backup & Recovery

- [ ] Configure automated database backups
- [ ] Test backup restore procedure
- [ ] Document disaster recovery plan
- [ ] Set up point-in-time recovery (if available)
- [ ] Verify backup retention policy
- [ ] Test backup encryption

---

## Deployment Checklist

### Database Deployment

- [ ] Provision managed PostgreSQL (Neon/Supabase/Railway)
- [ ] Configure database credentials
- [ ] Enable SSL/TLS for database connections
- [ ] Configure connection pooling
- [ ] Set up automated backups
- [ ] Run migrations on production database
- [ ] Verify migrations successful
- [ ] Run seed script (if first deployment)
- [ ] Verify data integrity

### Backend Deployment

**Option A: Railway**
- [ ] Create Railway project
- [ ] Connect GitHub repository
- [ ] Configure environment variables
- [ ] Set build command: `cd apps/api && pip install -e .`
- [ ] Set start command: `uvicorn sangam_api.main:app --host 0.0.0.0 --port $PORT`
- [ ] Deploy: `railway up`
- [ ] Verify deployment successful
- [ ] Get deployment URL

**Option B: Fly.io**
- [ ] Create Fly.io app: `fly launch`
- [ ] Configure `fly.toml`
- [ ] Set secrets: `fly secrets set DATABASE_URL=...`
- [ ] Set secrets: `fly secrets set SECRET_KEY=...`
- [ ] Deploy: `fly deploy`
- [ ] Verify deployment successful
- [ ] Get deployment URL

**Option C: Docker**
- [ ] Build Docker image: `docker build -f infra/docker/Dockerfile.api -t sangam-api .`
- [ ] Push to container registry
- [ ] Deploy container to hosting platform
- [ ] Configure environment variables
- [ ] Set up health checks
- [ ] Verify deployment successful

**Post-Deployment Verification**
- [ ] Test health endpoint: `curl https://api.yourdomain.com/health`
- [ ] Test API documentation: `https://api.yourdomain.com/docs`
- [ ] Test authentication: Login with demo credentials
- [ ] Test CRUD operations on each module
- [ ] Verify database connections
- [ ] Check logs for errors
- [ ] Monitor response times
- [ ] Verify CORS working correctly

### MQTT Worker Deployment (if using IoT)

- [ ] Create separate service for MQTT worker
- [ ] Configure MQTT broker credentials
- [ ] Set database connection
- [ ] Deploy MQTT worker service
- [ ] Verify MQTT connection
- [ ] Test sensor data ingestion
- [ ] Monitor MQTT worker logs

### Frontend Deployment

**Vercel Deployment**
- [ ] Connect GitHub repository to Vercel
- [ ] Configure build settings:
  - Framework: Vite
  - Build command: `npm run build`
  - Output directory: `dist`
- [ ] Set environment variable: `VITE_API_URL`
- [ ] Deploy to production
- [ ] Verify deployment successful
- [ ] Get deployment URL
- [ ] Configure custom domain (if needed)
- [ ] Set up DNS records

**Post-Deployment Verification**
- [ ] Test frontend loads: `https://yourdomain.com`
- [ ] Test login flow
- [ ] Test all modules (Inventory, Shipments, etc.)
- [ ] Verify API calls working
- [ ] Test offline functionality
- [ ] Check Service Worker registration
- [ ] Verify IndexedDB working
- [ ] Test on multiple browsers
- [ ] Test on mobile devices

---

## Post-Deployment Checklist

### Functional Testing

- [ ] Test login with all demo users
- [ ] Test inventory operations (create, read, update, delete)
- [ ] Test shipment tracking
- [ ] Test GIS map functionality
- [ ] Test forecasting generation
- [ ] Test simulation scenarios
- [ ] Test IoT sensor monitoring
- [ ] Test recommendations workflow
- [ ] Test offline mode
- [ ] Test synchronization

### Performance Testing

- [ ] Load test API endpoints
- [ ] Test concurrent users
- [ ] Monitor response times
- [ ] Check database query performance
- [ ] Verify caching working
- [ ] Test offline sync performance
- [ ] Monitor memory usage
- [ ] Check CPU utilization

### Security Testing

- [ ] Test authentication flow
- [ ] Verify authorization enforcement
- [ ] Test token refresh
- [ ] Verify CORS restrictions
- [ ] Test input validation
- [ ] Check for SQL injection
- [ ] Test XSS prevention
- [ ] Verify audit logging
- [ ] Test rate limiting (if implemented)

### Monitoring Verification

- [ ] Verify logs are being collected
- [ ] Check error tracking working
- [ ] Verify metrics are being captured
- [ ] Test alerting system
- [ ] Monitor database performance
- [ ] Check API response times
- [ ] Verify uptime monitoring
- [ ] Test incident response procedures

### Backup Verification

- [ ] Verify automated backups running
- [ ] Test backup restore procedure
- [ ] Verify backup encryption
- [ ] Check backup retention policy
- [ ] Test point-in-time recovery
- [ ] Document backup procedures

---

## Rollback Plan

### If Deployment Fails

**Backend Rollback**

Railway:
```bash
railway deployment rollback
```

Fly.io:
```bash
fly releases
fly rollback
```

Docker:
```bash
# Deploy previous image version
docker deploy previous-image-tag
```

**Frontend Rollback**

Vercel:
```bash
# Go to Deployments tab
# Select previous deployment
# Click "Promote to Production"
```

**Database Rollback**
```bash
# Restore from backup
psql -h host -U user -d sangam < backup_before_deployment.sql
```

### Rollback Verification

- [ ] Verify backend health endpoint responding
- [ ] Verify frontend loads correctly
- [ ] Test login flow
- [ ] Verify database integrity
- [ ] Check logs for errors
- [ ] Monitor for 30 minutes
- [ ] Notify stakeholders

---

## Production Monitoring

### Daily Checks

- [ ] Review error logs
- [ ] Check API response times
- [ ] Monitor database performance
- [ ] Verify backups completed
- [ ] Check disk space usage
- [ ] Review user activity
- [ ] Monitor API usage patterns

### Weekly Checks

- [ ] Review security logs
- [ ] Analyze performance trends
- [ ] Check for unusual activity
- [ ] Review error rates
- [ ] Verify backup integrity
- [ ] Update dependencies (if needed)
- [ ] Review user feedback

### Monthly Checks

- [ ] Comprehensive security audit
- [ ] Performance optimization review
- [ ] Database optimization
- [ ] Backup and recovery test
- [ ] Disaster recovery drill
- [ ] Capacity planning review
- [ ] Cost optimization review

---

## Incident Response

### Critical Issues

**Database Down**
1. Check database provider status
2. Verify connection string
3. Check network connectivity
4. Restore from backup if needed
5. Notify stakeholders
6. Document incident

**API Down**
1. Check backend service status
2. Review logs for errors
3. Check resource usage (CPU, memory)
4. Restart service if needed
5. Verify health endpoint
6. Notify stakeholders

**Frontend Down**
1. Check Vercel deployment status
2. Review build logs
3. Verify environment variables
4. Redeploy if needed
5. Check DNS configuration
6. Notify stakeholders

**Security Incident**
1. Isolate affected systems
2. Review security logs
3. Identify scope of breach
4. Rotate all secrets
5. Notify security team
6. Document incident
7. Conduct post-mortem

### Contact Information

- **Database Provider**: [Provider Support Contact]
- **Hosting Provider**: [Provider Support Contact]
- **Security Team**: [Security Team Contact]
- **Development Team**: [Dev Team Contact]
- **Management**: [Management Contact]

---

## Maintenance Windows

### Scheduled Maintenance

- **Frequency**: Monthly
- **Duration**: 2-4 hours
- **Timing**: Low-traffic period (e.g., Sunday 2 AM)
- **Notification**: 48 hours in advance

### Maintenance Tasks

- [ ] Apply security patches
- [ ] Update dependencies
- [ ] Database maintenance (vacuum, analyze)
- [ ] Clear old logs
- [ ] Review and optimize queries
- [ ] Test backup restore
- [ ] Update documentation

### Communication Template

```
Subject: Scheduled Maintenance - [Date]

Dear Users,

We will be performing scheduled maintenance on [Date] from [Start Time] to [End Time] [Timezone].

During this time, the system will be unavailable.

We apologize for any inconvenience and appreciate your understanding.

Best regards,
SANGAM Team
```

---

## Success Criteria

### Deployment Success

- [ ] All health checks passing
- [ ] All functional tests passing
- [ ] Performance within acceptable limits
- [ ] No critical errors in logs
- [ ] Security checks passing
- [ ] Monitoring operational
- [ ] Backups verified
- [ ] Documentation updated
- [ ] Team trained
- [ ] Stakeholders notified

### Ongoing Success

- [ ] 99.9% uptime
- [ ] < 500ms average response time
- [ ] < 1% error rate
- [ ] Zero security incidents
- [ ] Positive user feedback
- [ ] Cost within budget
- [ ] Team satisfaction

---

## Sign-Off

### Deployment Approval

- [ ] Technical Lead: _________________ Date: _______
- [ ] Security Lead: _________________ Date: _______
- [ ] Operations Lead: _________________ Date: _______
- [ ] Product Owner: _________________ Date: _______

### Post-Deployment Review

- [ ] Deployment successful: Yes / No
- [ ] Issues encountered: _________________
- [ ] Lessons learned: _________________
- [ ] Action items: _________________
- [ ] Next review date: _________________

---

## Quick Reference

### Important URLs

- **Frontend**: https://yourdomain.com
- **Backend API**: https://api.yourdomain.com
- **API Docs**: https://api.yourdomain.com/docs
- **Database**: [Database Provider Dashboard URL]
- **Monitoring**: [Monitoring Dashboard URL]
- **Logs**: [Logging Dashboard URL]

### Important Commands

```bash
# Backend
cd apps/api
uvicorn sangam_api.main:app --host 0.0.0.0 --port 8000
pytest
alembic upgrade head
python -m sangam_api.scripts.seed

# Frontend
npm run dev
npm run build
npm run typecheck

# Database
psql -h host -U user -d sangam
pg_dump -h host -U user -d sangam > backup.sql

# Docker
docker-compose -f infra/docker/docker-compose.yml up -d
docker build -f infra/docker/Dockerfile.api -t sangam-api .

# Deployment
railway up
fly deploy
vercel --prod
```

### Important Files

- **README.md** - Project overview
- **DEPLOYMENT_GUIDE.md** - Deployment instructions
- **INTEGRATION_REVIEW.md** - Integration details
- **FINAL_SUMMARY.md** - Review summary
- **verify_integration.py** - Verification script
- **.env.example** - Environment template
- **vercel.json** - Vercel configuration
- **infra/docker/** - Docker configurations

---

**Checklist Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Next Review**: After first production deployment
