/**
 * Sensor Alerts Component
 * 
 * Displays sensor alerts with filtering and acknowledgment.
 */

import { useState, useEffect } from 'react';
import { apiClient } from '../../lib/api';
import { AlertTriangle, CheckCircle, Filter } from 'lucide-react';

interface SensorAlert {
  id: string;
  sensor_id: string;
  alert_type: string;
  severity: string;
  message: string;
  triggered_value: number | null;
  threshold_value: number | null;
  is_acknowledged: boolean;
  acknowledged_at: string | null;
  triggered_at: string;
  resolved_at: string | null;
  sensor?: {
    name: string;
    sensor_id: string;
  };
}

export function SensorAlerts() {
  const [alerts, setAlerts] = useState<SensorAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'active' | 'acknowledged'>('active');
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  useEffect(() => {
    loadAlerts();
  }, [filter, severityFilter]);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const params: any = { limit: 100 };
      
      if (filter === 'active') {
        params.is_acknowledged = false;
      } else if (filter === 'acknowledged') {
        params.is_acknowledged = true;
      }
      
      if (severityFilter !== 'all') {
        params.severity = severityFilter;
      }

      const response = await apiClient.request<{ items: SensorAlert[] }>(
        '/iot/alerts',
        { params }
      );
      setAlerts(response.items);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load alerts:', err);
      setLoading(false);
    }
  };

  const handleAcknowledge = async (alertId: string) => {
    try {
      // In production, you would get the current user ID from auth context
      const userId = '00000000-0000-0000-0000-000000000001'; // Placeholder
      
      await apiClient.request(`/iot/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        body: JSON.stringify({ acknowledged_by: userId }),
      });
      
      loadAlerts();
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'info':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getAlertTypeLabel = (type: string) => {
    switch (type) {
      case 'threshold_high':
        return 'High Threshold';
      case 'threshold_low':
        return 'Low Threshold';
      case 'offline':
        return 'Offline';
      case 'malfunction':
        return 'Malfunction';
      default:
        return type;
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-12 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="text-slate-600 mt-4">Loading alerts...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-lg shadow-lg p-4">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter size={18} className="text-slate-500" />
            <span className="text-sm font-medium text-slate-700">Status:</span>
            <div className="flex gap-2">
              {['all', 'active', 'acknowledged'].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f as any)}
                  className={`px-3 py-1 rounded text-xs font-medium ${
                    filter === f
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-slate-700">Severity:</span>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="px-3 py-1 rounded border border-slate-300 text-sm"
            >
              <option value="all">All</option>
              <option value="critical">Critical</option>
              <option value="warning">Warning</option>
              <option value="info">Info</option>
            </select>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="bg-white rounded-lg shadow-lg">
        <div className="p-4 border-b border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900">
            Alerts ({alerts.length})
          </h2>
        </div>

        {alerts.length === 0 ? (
          <div className="p-12 text-center">
            <CheckCircle size={48} className="mx-auto mb-4 text-green-500" />
            <p className="text-slate-600">No alerts found</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-200">
            {alerts.map((alert) => (
              <div key={alert.id} className="p-4 hover:bg-slate-50">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-start gap-3">
                    <AlertTriangle
                      size={20}
                      className={
                        alert.severity === 'critical'
                          ? 'text-red-500'
                          : alert.severity === 'warning'
                          ? 'text-yellow-500'
                          : 'text-blue-500'
                      }
                    />
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold border ${getSeverityColor(alert.severity)}`}>
                          {alert.severity.toUpperCase()}
                        </span>
                        <span className="text-xs text-slate-500">
                          {getAlertTypeLabel(alert.alert_type)}
                        </span>
                      </div>
                      <p className="text-sm text-slate-900">{alert.message}</p>
                      {alert.sensor && (
                        <p className="text-xs text-slate-500 mt-1">
                          Sensor: {alert.sensor.name} ({alert.sensor.sensor_id})
                        </p>
                      )}
                    </div>
                  </div>

                  {!alert.is_acknowledged && (
                    <button
                      onClick={() => handleAcknowledge(alert.id)}
                      className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700"
                    >
                      Acknowledge
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs text-slate-500 mt-2">
                  <div>
                    Triggered: {new Date(alert.triggered_at).toLocaleString()}
                  </div>
                  {alert.triggered_value !== null && (
                    <div>
                      Value: {alert.triggered_value.toFixed(2)}
                      {alert.threshold_value !== null && (
                        <span> (threshold: {alert.threshold_value.toFixed(2)})</span>
                      )}
                    </div>
                  )}
                  {alert.is_acknowledged && alert.acknowledged_at && (
                    <div className="col-span-2 text-green-600">
                      Acknowledged: {new Date(alert.acknowledged_at).toLocaleString()}
                    </div>
                  )}
                  {alert.resolved_at && (
                    <div className="col-span-2 text-green-600">
                      Resolved: {new Date(alert.resolved_at).toLocaleString()}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
