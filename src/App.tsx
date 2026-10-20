/**
 * SANGAM Application - Main entry point with authentication.
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { InventoryPage } from './pages/InventoryPage';
import { GISPage } from './pages/GISPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          
          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          
          {/* Inventory routes - require inventory:read permission */}
          <Route
            path="/inventory"
            element={
              <ProtectedRoute requiredPermission="inventory:read">
                <div className="min-h-screen bg-slate-900">
                  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <InventoryPage />
                  </div>
                </div>
              </ProtectedRoute>
            }
          />
          
          {/* GIS routes - require routes:read permission */}
          <Route
            path="/gis"
            element={
              <ProtectedRoute requiredPermission="routes:read">
                <GISPage />
              </ProtectedRoute>
            }
          />
          
          {/* Admin routes - require admin:read permission */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute requiredPermission="admin:read">
                <div className="min-h-screen bg-slate-900 text-white p-8">
                  <h1 className="text-2xl font-bold mb-4">Admin Panel</h1>
                  <p className="text-slate-400">
                    This is a protected admin area requiring admin:read permission.
                  </p>
                </div>
              </ProtectedRoute>
            }
          />
          
          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
