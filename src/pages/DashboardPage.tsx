/**
 * SANGAM Dashboard - Main Layout
 * Dark navy sidebar with light blue-white content area
 */

import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Package,
  Truck,
  Map,
  BarChart3,
  Settings,
  Bell,
  LogOut,
  Menu,
  X,
  Circle,
} from 'lucide-react';
import { KPICards } from '../components/dashboard/KPICards';
import { StockForecastChart } from '../components/dashboard/StockForecastChart';
import { CommodityChart } from '../components/dashboard/CommodityChart';
import { RecentAlerts } from '../components/dashboard/RecentAlerts';
import { RouteMap } from '../components/dashboard/RouteMap';
import { KeyInsights } from '../components/dashboard/KeyInsights';

export function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, current: true },
    { name: 'Inventory', href: '/inventory', icon: Package, current: false },
    { name: 'Shipments', href: '/shipments', icon: Truck, current: false },
    { name: 'Routes', href: '/routes', icon: Map, current: false },
    { name: 'Analytics', href: '/analytics', icon: BarChart3, current: false },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:fixed`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 bg-slate-800">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">S</span>
              </div>
              <div>
                <h1 className="text-white font-bold text-lg">SANGAM</h1>
                <p className="text-slate-400 text-xs">Predictive Logistics</p>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-slate-400 hover:text-white"
            >
              <X size={20} />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <a
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    item.current
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <Icon size={20} />
                  <span className="font-medium">{item.name}</span>
                </a>
              );
            })}
          </nav>

          {/* User profile */}
          <div className="p-4 border-t border-slate-800">
            <div className="flex items-center gap-3 px-4 py-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                <span className="text-white font-semibold">
                  {user?.full_name?.charAt(0) || user?.email?.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-medium truncate">
                  {user?.full_name || user?.email}
                </p>
                <p className="text-slate-400 text-xs truncate">{user?.roles?.[0]}</p>
              </div>
              <button
                onClick={handleLogout}
                className="text-slate-400 hover:text-white transition-colors"
                title="Logout"
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden text-slate-600 hover:text-slate-900"
              >
                <Menu size={24} />
              </button>
              <div>
                <h2 className="text-xl font-bold text-slate-900">Dashboard</h2>
                <p className="text-sm text-slate-500">Predictive Logistics & Supply Chain</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {/* Online status */}
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-full">
                <Circle size={8} className="text-green-500 fill-green-500" />
                <span className="text-sm font-medium text-green-700">Online</span>
              </div>

              {/* Notifications */}
              <button className="relative p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors">
                <Bell size={20} />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>

              {/* Settings */}
              <button className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors">
                <Settings size={20} />
              </button>
            </div>
          </div>
        </header>

        {/* Dashboard content */}
        <main className="p-4 sm:p-6 lg:p-8 space-y-6">
          {/* KPI Cards */}
          <KPICards />

          {/* Middle row - Charts and Alerts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <StockForecastChart />
            </div>
            <div>
              <CommodityChart />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <RecentAlerts />
            </div>
          </div>

          {/* Bottom row - Map and Insights */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <RouteMap />
            </div>
            <div>
              <KeyInsights />
            </div>
          </div>

          {/* Footer disclaimer */}
          <footer className="mt-8 pt-6 border-t border-slate-200">
            <p className="text-center text-sm text-slate-500">
              <strong>Disclaimer:</strong> This dashboard displays demonstration data for illustrative purposes only. 
              All metrics, forecasts, shipments, and alerts shown are simulated and do not represent real-world operations.
            </p>
          </footer>
        </main>
      </div>
    </div>
  );
}
