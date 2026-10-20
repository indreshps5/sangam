# SANGAM Authentication & Authorization Guide

## Overview

SANGAM implements JWT-based authentication with role-based access control (RBAC). All security logic is centralized in dedicated modules following SOLID principles.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Authentication Flow                     │
└─────────────────────────────────────────────────────────────┘

1. Login → Validate credentials → Generate JWT tokens
2. Access protected endpoint → Validate token → Check permissions
3. Token refresh → Validate refresh token → Issue new tokens
4. Logout → Log event → Client clears tokens

┌─────────────────────────────────────────────────────────────┐
│                    Authorization Model                       │
└─────────────────────────────────────────────────────────────┘

Users → Roles → Permissions
  ↓       ↓         ↓
 UUID   Name    domain:action
        Desc    (e.g., depots:read)
```

## Roles & Permissions

### Predefined Roles

| Role | Description | Key Permissions |
|------|-------------|-----------------|
| **super_admin** | Full system access | `*` (all permissions) |
| **admin** | Administrative access | All except user deletion |
| **logistics_officer** | Shipment & route management | `shipments:*`, `routes:*` |
| **inventory_manager** | Inventory operations | `inventory:*`, `depots:read` |
| **analyst** | Data analysis & forecasting | `forecasts:*`, `simulations:*` |
| **viewer** | Read-only access | `*:read` permissions only |

### Permission Format

Permissions follow the pattern: `domain:action`

**Domains:**
- `depots` - Depot/facility management
- `shipments` - Shipment operations
- `inventory` - Inventory management
- `forecasts` - Demand forecasting
- `routes` - Route management
- `users` - User management
- `roles` - Role management
- `audit` - Audit log access
- `admin` - Administrative functions
- `sensors` - IoT sensor data
- `alerts` - Alert management
- `simulations` - Simulation scenarios
- `recommendations` - AI recommendations

**Actions:**
- `read` - View data
- `write` - Create/update data
- `delete` - Delete data
- `admin` - Administrative actions
- `*` - All actions in domain

**Wildcards:**
- `depots:*` - All depot permissions
- `*` - All permissions (super admin)

## API Endpoints

### Authentication

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@sangam.dev",
  "password": "password123!"
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

```http
POST /api/v1/auth/logout
Authorization: Bearer <access_token>

Response:
{
  "message": "Successfully logged out"
}
```

```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>

Response:
{
  "id": "uuid",
  "email": "user@sangam.dev",
  "full_name": "User Name",
  "roles": ["logistics_officer"],
  "permissions": ["shipments:read", "shipments:write", ...]
}
```

```http
POST /api/v1/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "oldpass123!",
  "new_password": "newpass456!"
}
```

### Protected Endpoints

All protected endpoints require the `Authorization: Bearer <token>` header.

```http
GET /api/v1/admin/dashboard
Authorization: Bearer <access_token>
# Requires: admin:read permission
```

```http
GET /api/v1/admin/users
Authorization: Bearer <access_token>
# Requires: users:read permission
```

## Security Features

### Password Hashing
- Algorithm: **bcrypt** (via passlib)
- Automatically salts each password
- Computationally expensive to prevent brute force

### JWT Tokens

**Access Tokens:**
- Short-lived (default: 30 minutes)
- Contains: user_id, roles, permissions
- Used for API authentication

**Refresh Tokens:**
- Longer-lived (default: 7 days)
- Contains: user_id only
- Used to obtain new access tokens
- Stateless (not stored in database)

**Security Notes:**
- Tokens are signed with HS256 algorithm
- Secret key must be changed in production
- Tokens expire automatically
- Refresh tokens can be revoked by changing secret key

### Audit Logging

All authentication events are logged:
- Login attempts (success/failure)
- Logout events
- Password changes
- Permission denied events

**Audit log entries include:**
- User ID
- Action type
- Timestamp
- IP address
- User agent
- Metadata (success/failure, etc.)

**Note:** Passwords and tokens are **never** logged.

## Configuration

### Environment Variables

```bash
# JWT Configuration
SECRET_KEY=your-secret-key-here  # Change in production!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Development seed users (JSON array)
DEV_SEED_USERS=[
  {
    "email": "admin@sangam.dev",
    "password": "admin123!",
    "full_name": "System Administrator",
    "roles": ["super_admin"]
  }
]
```

### Generating Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## Development Setup

### 1. Seed Database

```bash
cd apps/api
python -m sangam_api.scripts.seed
```

This creates:
- 5 demonstration roles
- 5 development users
- Sample depot data

### 2. Development Users

| Email | Password | Role |
|-------|----------|------|
| admin@sangam.dev | admin123! | Super Admin |
| logistics@sangam.dev | logistics123! | Logistics Officer |
| inventory@sangam.dev | inventory123! | Inventory Manager |
| analyst@sangam.dev | analyst123! | Analyst |
| viewer@sangam.dev | viewer123! | Viewer |

### 3. Custom Seed Users

Set `DEV_SEED_USERS` environment variable with JSON array:

```bash
export DEV_SEED_USERS='[
  {
    "email": "custom@sangam.dev",
    "password": "custom123!",
    "full_name": "Custom User",
    "roles": ["analyst"]
  }
]'
```

## Frontend Integration

### API Client

```typescript
import apiClient from './lib/api';

// Login
const user = await apiClient.login('email', 'password');

// Make authenticated requests
const data = await apiClient.request('/depots/');

// Check permissions
if (apiClient.hasPermission('shipments:write')) {
  // Show create button
}

// Logout
await apiClient.logout();
```

### Protected Routes

```tsx
import { ProtectedRoute } from './components/ProtectedRoute';

<Route
  path="/admin"
  element={
    <ProtectedRoute requiredPermission="admin:read">
      <AdminPage />
    </ProtectedRoute>
  }
/>
```

### Auth Context

```tsx
import { useAuth } from './contexts/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, hasPermission, logout } = useAuth();
  
  if (!isAuthenticated) {
    return <LoginPage />;
  }
  
  if (!hasPermission('shipments:write')) {
    return <AccessDenied />;
  }
  
  return <ShipmentForm />;
}
```

## Testing

### Run Auth Tests

```bash
cd apps/api
pytest tests/unit/test_auth.py -v
pytest tests/unit/test_permissions.py -v
```

### Test Coverage

- ✅ Valid login
- ✅ Invalid credentials
- ✅ Inactive user login
- ✅ Token refresh
- ✅ Expired tokens
- ✅ Current user retrieval
- ✅ Unauthorized access
- ✅ Role-specific permissions
- ✅ Permission denied events
- ✅ Audit logging

## Production Deployment

### Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=false`
- [ ] Use HTTPS in production
- [ ] Configure proper CORS origins
- [ ] Set appropriate token expiration times
- [ ] Enable audit log monitoring
- [ ] Implement rate limiting on auth endpoints
- [ ] Use environment variables for all secrets
- [ ] Never commit `.env` files
- [ ] Regular security audits

### Vercel Deployment

Frontend deployment is compatible with Vercel:
- Tokens stored in localStorage
- Automatic token refresh
- Protected routes work client-side
- API calls include auth headers

### Managed PostgreSQL

Database deployment compatible with managed PostgreSQL:
- Use connection pooling
- Configure SSL/TLS
- Set appropriate pool sizes
- Use connection string from environment

## Troubleshooting

### Token Expired

**Symptom:** 401 Unauthorized errors

**Solution:**
- Check token expiration time
- Implement automatic refresh in frontend
- Verify system clock is correct

### Permission Denied

**Symptom:** 403 Forbidden errors

**Solution:**
- Verify user has required role
- Check permission string format
- Review role permission assignments

### Login Failed

**Symptom:** 401 on login

**Solution:**
- Verify email and password
- Check user is active
- Review audit logs for details

## Additional Resources

- [JWT.io](https://jwt.io/) - JWT debugger
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
