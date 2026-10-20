/**
 * Sensor Detail Component
 * 
 * Displays detailed information about a sensor including readings and trends.
 */

import { useState, useEffect } from 'react';
import { apiClient } from '../../lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, TrendingUp, Clock } from 'lucide-react';
import { Sensor } from '../../pages/IoTMonitoringPage';

interface SensorReading {
  id: string;
  sensor_id: string;
  value: number;
  unit: string;
  timestamp: string;
  quality: string | null;
  message_version: string;
  received_at: string;
}

interface SensorDetailProps {
  sensor: Sensor;
}

export function SensorDetail({ sensor }: SensorDetailProps) {
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [trendData, setTrendData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(24); // hours

  useEffect(() => {
    loadData();
  }, [sensor.id, timeRange]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load recent readings
      const readingsResponse = await apiClient.request<{ items: SensorReading[] }>(
        `/iot/sensors/${sensor.id}/readings`,
        { params: { limit: 50 } }
      );
      setReadings(readingsResponse.items);

      // Load trend data
      const trendResponse = await apiClient.request<any>(
        `/iot/sensors/${sensor.id}/trend`,
        { params: { hours: timeRange, interval_minutes: 60 } }
      );
      setTrendData(trendResponse.data_points || []);

      setLoading(false);
    } catch (err) {
      console.error('Failed to load sensor data:', err);
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getQualityColor = (quality: string | null) => {
    switch (quality) {
      case 'good':
        return 'text-green-600';
      case 'warning':
        return 'text-yellow-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-slate-600';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-12 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="text-slate-600 mt-4">Loading sensor data...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Sensor Info */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-slate-900">{sensor.name}</h2>
            <p className="text-sm text-slate-500 font-mono">{sensor.sensor_id}</p>
          </div>
          <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
            sensor.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
          }`}>
            {sensor.is_active ? 'Active' : 'Inactive'}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-slate-500">Type:</span>{' '}
            <span className="font-medium">{sensor.sensor_type}</span>
          </div>
          <div>
            <span className="text-slate-500">Unit:</span>{' '}
            <span className="font-medium">{sensor.unit}</span>
          </div>
          {sensor.min_threshold !== null && (
            <div>
              <span className="text-slate-500">Min Threshold:</span>{' '}
              <span className="font-medium">{sensor.min_threshold}</span>
            </div>
          )}
          {sensor.max_threshold !== null && (
            <div>
              <span className="text-slate-500">Max Threshold:</span>{' '}
              <span className="font-medium">{sensor.max_threshold}</span>
            </div>
          )}
          {sensor.last_reading_value !== null && (
            <div className="col-span-2">
              <span className="text-slate-500">Last Reading:</span>{' '}
              <span className="text-lg font-bold text-slate-900">
                {sensor.last_reading_value.toFixed(2)} {sensor.unit}
              </span>
            </div>
          )}
          {sensor.last_seen_at && (
            <div className="col-span-2 flex items-center gap-2 text-slate-500">
              <Clock size={14} />
              <span>Last seen: {formatTimestamp(sensor.last_seen_at)}</span>
            </div>
          )}
        </div>
      </div>

      {/* Trend Chart */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
            <TrendingUp size={20} className="text-blue-600" />
            Trend ({timeRange}h)
          </h3>
          <div className="flex gap-2">
            {[6, 24, 48, 168].map((hours) => (
              <button
                key={hours}
                onClick={() => setTimeRange(hours)}
                className={`px-3 py-1 rounded text-xs font-medium ${
                  timeRange === hours
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {hours}h
              </button>
            ))}
          </div>
        </div>

        {trendData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                stroke="#64748b"
                fontSize={12}
              />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip
                labelFormatter={(value) => new Date(value).toLocaleString()}
                formatter={(value: number) => [`${value.toFixed(2)} ${sensor.unit}`, 'Value']}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: '#3b82f6', r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[300px] flex items-center justify-center text-slate-500">
            No trend data available
          </div>
        )}
      </div>

      {/* Recent Readings */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-slate-900 flex items-center gap-2 mb-4">
          <Activity size={20} className="text-green-600" />
          Recent Readings
        </h3>

        {readings.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Value
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Quality
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Version
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {readings.map((reading) => (
                  <tr key={reading.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-sm text-slate-900">
                      {formatTimestamp(reading.timestamp)}
                    </td>
                    <td className="px-4 py-3 text-sm font-semibold text-slate-900">
                      {reading.value.toFixed(2)} {reading.unit}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={getQualityColor(reading.quality)}>
                        {reading.quality || 'N/A'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-500 font-mono">
                      {reading.message_version}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500">
            No readings available
          </div>
        )}
      </div>
    </div>
  );
}
