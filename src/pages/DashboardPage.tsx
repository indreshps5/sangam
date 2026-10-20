/**
 * Dashboard page - demonstrates protected routes and user info.
 */

import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export function DashboardPage() {
  const { user, logout, hasPermission, hasRole } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">SANGAM Dashboard</h1>
              <p className="text-sm text-slate-400">Predictive Logistics & Supply Chain</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-white">{user.full_name || user.email}</p>
                <p className="text-xs text-slate-400">{user.roles.join(', ')}</p>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* User Info Card */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">User Information</h2>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-slate-400">Email</label>
                <p className="text-sm text-white">{user.email}</p>
              </div>
              <div>
                <label className="text-xs text-slate-400">Full Name</label>
                <p className="text-sm text-white">{user.full_name || 'Not set'}</p>
              </div>
              <div>
                <label className="text-xs text-slate-400">User ID</label>
                <p className="text-xs text-slate-300 font-mono">{user.id}</p>
              </div>
            </div>
          </div>

          {/* Roles Card */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Roles</h2>
            <div className="flex flex-wrap gap-2">
              {user.roles.map((role) => (
                <span
                  key={role}
                  className="px-3 py-1 bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm rounded-full"
                >
                  {role}
                </span>
              ))}
            </div>
          </div>

          {/* Permissions Card */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 md:col-span-2">
            <h2 className="text-lg font-semibold text-white mb-4">Permissions</h2>
            <div className="flex flex-wrap gap-2">
              {user.permissions.slice(0, 20).map((permission) => (
                <span
                  key={permission}
                  className="px-2 py-1 bg-slate-700 border border-slate-600 text-slate-300 text-xs rounded"
                >
                  {permission}
                </span>
              ))}
              {user.permissions.length > 20 && (
                <span className="px-2 py-1 text-slate-400 text-xs">
                  +{user.permissions.length - 20} more
                </span>
              )}
            </div>
          </div>

          {/* Permission Checks */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 md:col-span-2">
            <h2 className="text-lg font-semibold text-white mb-4">Permission Checks</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              <PermissionCheck
                label="depots:read"
                hasPermission={hasPermission('depots:read')}
              />
              <PermissionCheck
                label="shipments:write"
                hasPermission={hasPermission('shipments:write')}
              />
              <PermissionCheck
                label="admin:read"
                hasPermission={hasPermission('admin:read')}
              />
              <PermissionCheck
                label="audit:read"
                hasPermission={hasPermission('audit:read')}
              />
              <PermissionCheck
                label="users:write"
                hasPermission={hasPermission('users:write')}
              />
              <PermissionCheck
                label="forecasts:run"
                hasPermission={hasPermission('forecasts:run')}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function PermissionCheck({ label, hasPermission }: { label: string; hasPermission: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className={`w-3 h-3 rounded-full ${
          hasPermission ? 'bg-green-500' : 'bg-red-500'
        }`}
      />
      <span className="text-sm text-slate-300 font-mono">{label}</span>
    </div>
  );
}
