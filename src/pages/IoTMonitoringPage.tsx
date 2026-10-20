/**
 * IoT Monitoring Page
 * 
 * Main dashboard for IoT sensor monitoring.
 * Displays sensor list, readings, trends, and alerts.
 */

import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api';
import {
  Thermometer,
  Droplets,
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Play,
  StopCircle,
  RefreshCw,
} from 'lucide-react';
import { SensorList } from '../components/iot/SensorList';
import { SensorDetail } from '../components/iot/SensorDetail';
import { SensorAlerts } from '../components/iot/SensorAlerts';
import { SimulatorControl } from '../components/iot/SimulatorControl';

export interface Sensor {
  id: string;
  sensor_id: string;
  name: string;
  sensor_type: string;
  unit: string;
  depot_id: string | null;
  shipment_id: string | null;
  min_threshold: number | null;
  max_threshold: number | null;
  is_active: boolean;
  last_seen_at: string | null;
  last_reading_value: number | null;
  created_at: string;
  updated_at: string;
}

export function IoTMonitoringPage() {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [selectedSensor, setSelectedSensor] = useState<Sensor | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'sensors' | 'alerts' | 'simulator'>('sensors');

  useEffect(() => {
    loadSensors();
  }, []);

  const loadSensors = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.request<{ items: Sensor[] }>('/iot/sensors', {
        params: { limit: 100 }
      });
      setSensors(response.items);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sensors');
      setLoading(false);
    }
  };

  const getSensorIcon = (type: string) => {
    switch (type) {
      case 'temperature':
        return <Thermometer size={20} className="text-red-500" />;
      case 'humidity':
        return <Droplets size={20} className="text-blue-500" />;
      default:
        return <Activity size={20} className="text-green-500" />;
    }
  };

  const getSensorStatus = (sensor: Sensor) => {
    if (!sensor.is_active) {
      return { icon: <XCircle size={16} className="text-gray-500" />, text: 'Inactive', color: 'text-gray-600' };
    }

    if (!sensor.last_seen_at) {
      return { icon: <AlertTriangle size={16} className="text-yellow-500" />, text: 'No data', color: 'text-yellow-600' };
    }

    const lastSeen = new Date(sensor.last_seen_at);
    const now = new Date();
    const minutesAgo = (now.getTime() - lastSeen.getTime()) / 1000 / 60;

    if (minutesAgo < 5) {
      return { icon: <CheckCircle size={16} className="text-green-500" />, text: 'Online', color: 'text-green-600' };
    } else if (minutesAgo < 30) {
      return { icon: <AlertTriangle size={16} className="text-yellow-500" />, text: 'Delayed', color: 'text-yellow-600' };
    } else {
      return { icon: <XCircle size={16} className="text-red-500" />, text: 'Offline', color: 'text-red-600' };
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center gap-3 text-red-800">
          <XCircle size={24} />
          <div>
            <p className="font-semibold">Failed to load sensors</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
        <button
          onClick={loadSensors}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                <Activity className="text-green-600" size={28} />
                IoT Sensor Monitoring
              </h1>
              <p className="text-sm text-slate-600 mt-1">
                Real-time sensor data, trends, and alerts
              </p>
            </div>
            <button
              onClick={loadSensors}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <RefreshCw size={18} />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-slate-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('sensors')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'sensors'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                Sensors ({sensors.length})
              </button>
              <button
                onClick={() => setActiveTab('alerts')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'alerts'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                Alerts
              </button>
              <button
                onClick={() => setActiveTab('simulator')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'simulator'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                Simulator
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'sensors' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Sensor List */}
            <div className="lg:col-span-1">
              <SensorList
                sensors={sensors}
                selectedSensor={selectedSensor}
                onSelectSensor={setSelectedSensor}
                getSensorIcon={getSensorIcon}
                getSensorStatus={getSensorStatus}
              />
            </div>

            {/* Sensor Detail */}
            <div className="lg:col-span-2">
              {selectedSensor ? (
                <SensorDetail sensor={selectedSensor} />
              ) : (
                <div className="bg-white rounded-lg shadow-lg p-12 text-center">
                  <Activity size={64} className="mx-auto mb-4 text-slate-300" />
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    No Sensor Selected
                  </h3>
                  <p className="text-sm text-slate-600">
                    Select a sensor from the list to view details and readings
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'alerts' && <SensorAlerts />}

        {activeTab === 'simulator' && <SimulatorControl />}

        {/* Data Notice */}
        <div className="mt-6 bg-amber-50 border border-amber-200 rounded-lg p-4">
          <p className="text-xs text-amber-800">
            <strong>Note:</strong> Sensor data shown may include simulated readings for demonstration purposes.
            Simulated data is clearly labeled in the metadata.
          </p>
        </div>
      </div>
    </div>
  );
}
