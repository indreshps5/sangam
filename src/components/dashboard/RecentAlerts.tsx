/**
 * Recent Alerts Component
 * Displays recent low stock and system alerts
 */

import { useEffect, useState } from 'react';
import { Bell, AlertTriangle, Loader2, AlertCircle } from 'lucide-react';
import { apiClient } from '../../lib/api';

interface LowStockAlert {
  inventory_item_id: string;
  item_name: string;
  sku: string;
  depot_id: string;
  depot_name: string;
  quantity_available: number;
  min_stock_level: number;
  shortage: number;
  unit_of_measure: string;
}

export function RecentAlerts() {
  const [alerts, setAlerts] = useState<LowStockAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await apiClient.request<{
          alerts: LowStockAlert[];
          total: number;
        }>('/inventory/alerts/low-stock');

        setAlerts(response.alerts.slice(0, 5)); // Show top 5
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load alerts');
        setLoading(false);
      }
    };

    fetchAlerts();
    // Refresh every 60 seconds
    const interval = setInterval(fetchAlerts, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-blue-100 p-6">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="animate-spin text-blue-600" size={32} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl border border-blue-100 p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-blue-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
            <Bell className="text-blue-600" size={20} />
            Recent Alerts
          </h3>
          <p className="text-sm text-slate-500 mt-1">
            Low stock warnings and system notifications
          </p>
        </div>
        {alerts.length > 0 && (
          <span className="px-3 py-1 bg-orange-100 text-orange-700 text-xs font-semibold rounded-full">
            {alerts.length} Active
          </span>
        )}
      </div>

      {alerts.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-slate-500">
          <AlertCircle size={48} className="mb-3 text-slate-300" />
          <p className="text-sm">No active alerts</p>
          <p className="text-xs text-slate-400 mt-1">All inventory levels are healthy</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => {
            const severity = alert.quantity_available === 0 ? 'critical' : 'warning';
            const severityColors = {
              critical: 'bg-red-50 border-red-200',
              warning: 'bg-orange-50 border-orange-200',
            };

            return (
              <div
                key={alert.inventory_item_id}
                className={`p-4 rounded-lg border ${severityColors[severity as keyof typeof severityColors]}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <AlertTriangle
                        size={16}
                        className={severity === 'critical' ? 'text-red-600' : 'text-orange-600'}
                      />
                      <h4 className="font-semibold text-slate-900 text-sm">
                        {alert.item_name}
                      </h4>
                    </div>
                    <p className="text-xs text-slate-600 mb-2">
                      {alert.depot_name} • {alert.sku}
                    </p>
                    <div className="flex items-center gap-4 text-xs">
                      <div>
                        <span className="text-slate-500">Available: </span>
                        <span className="font-semibold text-slate-900">
                          {alert.quantity_available} {alert.unit_of_measure}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-500">Min: </span>
                        <span className="font-semibold text-slate-900">
                          {alert.min_stock_level} {alert.unit_of_measure}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-500">Shortage: </span>
                        <span className="font-semibold text-red-600">
                          -{alert.shortage} {alert.unit_of_measure}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
