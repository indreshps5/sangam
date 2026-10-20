# SANGAM Authentication - Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- npm or yarn

## 1. Setup Backend

### Install Dependencies

```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set:
```bash
# IMPORTANT: Generate a strong secret key
SECRET_KEY=your-secret-key-here  # Use: python -c "import secrets; print(secrets.token_urlsafe(64))"

# Database connection
DATABASE_URL=postgresql+asyncpg://sangam:sangam@localhost:5432/sangam
```

### Start Database

```bash
# Using Docker
docker-compose -f infra/docker/docker-compose.yml up -d postgres

# Or use your existing PostgreSQL instance
```

### Seed Database

```bash
cd apps/api
python -m sangam_api.scripts.seed
```

This creates:
- 5 demonstration roles
- 5 development users
- Sample depot data

### Start API Server

```bash
cd apps/api
uvicorn sangam_api.main:app --reload --port 8000
```

API will be available at: http://localhost:8000

## 2. Setup Frontend

### Install Dependencies

```bash
npm install
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

### Start Development Server

```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## 3. Test Authentication

### Login with Demo Users

Open http://localhost:3000 in your browser.

**Demo Credentials:**

| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@sangam.dev | admin123! |
| Logistics Officer | logistics@sangam.dev | logistics123! |
| Inventory Manager | inventory@sangam.dev | inventory123! |
| Analyst | analyst@sangam.dev | analyst123! |
| Viewer | viewer@sangam.dev | viewer123! |

### Test Protected Routes

1. **Login** with any demo user
2. **Dashboard** - View user info, roles, and permissions
3. **Admin Panel** - Try accessing `/admin` (requires admin:read permission)
4. **Logout** - Click logout button

### Test API Directly

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@sangam.dev", "password": "admin123!"}'

# Response includes access_token and refresh_token

# Get current user
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Access admin dashboard
curl http://localhost:8000/api/v1/admin/dashboard \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 4. Verify Features

### ✅ Authentication
- [ ] Login with valid credentials
- [ ] Login fails with invalid credentials
- [ ] Token refresh works
- [ ] Logout clears tokens

### ✅ Authorization
- [ ] Admin can access `/admin`
- [ ] Viewer cannot access `/admin`
- [ ] Permissions are enforced on backend
- [ ] Role-based access works

### ✅ Audit Logging
- [ ] Login events are logged
- [ ] Logout events are logged
- [ ] Permission denied events are logged
- [ ] Audit logs don't contain passwords

### ✅ Security
- [ ] Passwords are hashed (bcrypt)
- [ ] Tokens expire after 30 minutes
- [ ] Refresh tokens work
- [ ] No secrets in code

## 5. Run Tests

```bash
cd apps/api
pytest tests/unit/test_auth.py -v
pytest tests/unit/test_permissions.py -v
```

## 6. Explore the Code

### Backend
- `apps/api/src/sangam_api/core/auth.py` - JWT and password handling
- `apps/api/src/sangam_api/core/permissions.py` - Permission definitions
- `apps/api/src/sangam_api/api/routes/auth.py` - Auth endpoints
- `apps/api/src/sangam_api/services/audit_service.py` - Audit logging

### Frontend
- `src/lib/api.ts` - API client with auth
- `src/contexts/AuthContext.tsx` - Auth state management
- `src/components/ProtectedRoute.tsx` - Route protection
- `src/pages/LoginPage.tsx` - Login UI

### Documentation
- `docs/AUTHENTICATION.md` - Complete auth guide
- `AUTH_IMPLEMENTATION.md` - Implementation summary

## 7. Common Issues

### "Invalid token" error
- Check if `SECRET_KEY` matches between login and API calls
- Verify token hasn't expired (30 minutes default)
- Try refreshing the token

### "Permission denied" error
- Check user has the required role
- Verify permission string format (domain:action)
- Review role permissions in database

### Database connection error
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Ensure database `sangam` exists

### Frontend can't connect to API
- Check `VITE_API_URL` in `.env`
- Verify CORS settings in backend
- Check API server is running on port 8000

## 8. Next Steps

1. **Customize roles** - Modify permissions in `core/permissions.py`
2. **Add more endpoints** - Use `PermissionChecker` dependency
3. **Implement business logic** - Build on auth foundation
4. **Deploy to production** - Follow deployment guide
5. **Add monitoring** - Track auth events and errors

## 9. Production Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=false`
- [ ] Use HTTPS
- [ ] Configure proper CORS origins
- [ ] Remove demo users or change passwords
- [ ] Enable audit log monitoring
- [ ] Set up rate limiting
- [ ] Configure backup and recovery
- [ ] Test with production database
- [ ] Review security headers

## 10. Support

- **Documentation**: `docs/AUTHENTICATION.md`
- **Implementation Details**: `AUTH_IMPLEMENTATION.md`
- **API Docs**: http://localhost:8000/docs (when running)
- **Issues**: Check audit logs for details

---

**You're all set!** 🎉

The authentication system is ready for development and testing.
