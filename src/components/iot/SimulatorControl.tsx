/**
 * Simulator Control Component
 * 
 * Controls for starting and stopping sensor simulators.
 */

import { useState, useEffect } from 'react';
import { apiClient } from '../../lib/api';
import { Play, StopCircle, Activity, AlertCircle } from 'lucide-react';

interface SimulatorStatus {
  sensor_id: string;
  is_running: boolean;
  readings_generated: number;
  started_at: string | null;
  last_reading_at: string | null;
}

interface SimulatorConfig {
  sensor_id: string;
  sensor_type: string;
  unit: string;
  base_value: number;
  variance: number;
  interval_seconds: number;
  duration_minutes: number;
  depot_id?: string;
  shipment_id?: string;
}

const SENSOR_PRESETS = [
  {
    name: 'Temperature Sensor (Mumbai Warehouse)',
    sensor_type: 'temperature',
    unit: 'celsius',
    base_value: 25,
    variance: 3,
  },
  {
    name: 'Humidity Sensor (Delhi DC)',
    sensor_type: 'humidity',
    unit: 'percent',
    base_value: 60,
    variance: 5,
  },
  {
    name: 'Temperature Sensor (Cold Storage)',
    sensor_type: 'temperature',
    unit: 'celsius',
    base_value: -18,
    variance: 2,
  },
  {
    name: 'Vibration Sensor (Shipment)',
    sensor_type: 'vibration',
    unit: 'g_force',
    base_value: 0.5,
    variance: 0.3,
  },
];

export function SimulatorControl() {
  const [statuses, setStatuses] = useState<Record<string, SimulatorStatus>>({});
  const [loading, setLoading] = useState(true);
  const [selectedPreset, setSelectedPreset] = useState(0);
  const [customConfig, setCustomConfig] = useState<Partial<SimulatorConfig>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStatuses();
    const interval = setInterval(loadStatuses, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const loadStatuses = async () => {
    try {
      const response = await apiClient.request<Record<string, SimulatorStatus>>(
        '/iot/simulator/status'
      );
      setStatuses(response);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load simulator statuses:', err);
      setLoading(false);
    }
  };

  const handleStart = async () => {
    setError(null);
    
    const preset = SENSOR_PRESETS[selectedPreset];
    const config: SimulatorConfig = {
      sensor_id: `sim-${preset.sensor_type}-${Date.now()}`,
      sensor_type: preset.sensor_type,
      unit: preset.unit,
      base_value: customConfig.base_value ?? preset.base_value,
      variance: customConfig.variance ?? preset.variance,
      interval_seconds: customConfig.interval_seconds ?? 10,
      duration_minutes: customConfig.duration_minutes ?? 60,
      ...customConfig,
    };

    try {
      await apiClient.request('/iot/simulator/start', {
        method: 'POST',
        body: JSON.stringify(config),
      });
      
      // Refresh statuses
      await loadStatuses();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start simulator');
    }
  };

  const handleStop = async (sensorId: string) => {
    try {
      await apiClient.request(`/iot/simulator/stop/${sensorId}`, {
        method: 'POST',
      });
      await loadStatuses();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop simulator');
    }
  };

  const runningSimulators = Object.values(statuses).filter(s => s.is_running);

  return (
    <div className="space-y-6">
      {/* Info Banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertCircle size={20} className="text-blue-600 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-blue-900">
              Simulator Mode
            </p>
            <p className="text-xs text-blue-800 mt-1">
              Simulators generate synthetic sensor readings for testing and demonstration.
              All simulated data is clearly labeled in the metadata.
              Simulators run in the background and generate readings at configured intervals.
            </p>
          </div>
        </div>
      </div>

      {/* Running Simulators */}
      {runningSimulators.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <Activity size={20} className="text-green-600" />
            Running Simulators ({runningSimulators.length})
          </h3>
          <div className="space-y-3">
            {runningSimulators.map((status) => (
              <div
                key={status.sensor_id}
                className="border border-slate-200 rounded-lg p-4"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-semibold text-slate-900">
                      {status.sensor_id}
                    </p>
                    <p className="text-xs text-slate-500">
                      Started: {status.started_at ? new Date(status.started_at).toLocaleString() : 'N/A'}
                    </p>
                  </div>
                  <button
                    onClick={() => handleStop(status.sensor_id)}
                    className="flex items-center gap-1 px-3 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700"
                  >
                    <StopCircle size={14} />
                    Stop
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs text-slate-600">
                  <div>
                    Readings Generated: <span className="font-semibold">{status.readings_generated}</span>
                  </div>
                  {status.last_reading_at && (
                    <div>
                      Last Reading: <span className="font-semibold">
                        {new Date(status.last_reading_at).toLocaleTimeString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Start New Simulator */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
          <Play size={20} className="text-blue-600" />
          Start New Simulator
        </h3>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <div className="space-y-4">
          {/* Preset Selection */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Sensor Preset
            </label>
            <select
              value={selectedPreset}
              onChange={(e) => setSelectedPreset(Number(e.target.value))}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {SENSOR_PRESETS.map((preset, index) => (
                <option key={index} value={index}>
                  {preset.name}
                </option>
              ))}
            </select>
          </div>

          {/* Custom Configuration */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Base Value
              </label>
              <input
                type="number"
                step="0.1"
                value={customConfig.base_value ?? SENSOR_PRESETS[selectedPreset].base_value}
                onChange={(e) => setCustomConfig({ ...customConfig, base_value: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Variance
              </label>
              <input
                type="number"
                step="0.1"
                value={customConfig.variance ?? SENSOR_PRESETS[selectedPreset].variance}
                onChange={(e) => setCustomConfig({ ...customConfig, variance: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Interval (seconds)
              </label>
              <input
                type="number"
                min="1"
                max="3600"
                value={customConfig.interval_seconds ?? 10}
                onChange={(e) => setCustomConfig({ ...customConfig, interval_seconds: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Duration (minutes)
              </label>
              <input
                type="number"
                min="1"
                max="1440"
                value={customConfig.duration_minutes ?? 60}
                onChange={(e) => setCustomConfig({ ...customConfig, duration_minutes: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <button
            onClick={handleStart}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            <Play size={18} />
            Start Simulator
          </button>
        </div>
      </div>

      {/* MQTT Information */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">
          MQTT Integration
        </h3>
        <div className="space-y-3 text-sm text-slate-600">
          <p>
            In production, sensor data is ingested via MQTT. The MQTT worker service
            runs separately from the API and subscribes to sensor topics.
          </p>
          <div className="bg-slate-50 rounded-lg p-3 font-mono text-xs">
            <p className="font-semibold mb-2">Topic Structure:</p>
            <p>sangam/sensors/&#123;sensor_id&#125;/data</p>
            <p>sangam/sensors/&#123;sensor_id&#125;/status</p>
          </div>
          <p className="text-xs text-slate-500">
            MQTT credentials are configured via environment variables and never exposed to the frontend.
          </p>
        </div>
      </div>
    </div>
  );
}
