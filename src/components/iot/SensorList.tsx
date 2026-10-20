/**
 * Sensor List Component
 * 
 * Displays a list of sensors with status indicators.
 */

import { Sensor } from '../../pages/IoTMonitoringPage';

interface SensorListProps {
  sensors: Sensor[];
  selectedSensor: Sensor | null;
  onSelectSensor: (sensor: Sensor) => void;
  getSensorIcon: (type: string) => React.ReactNode;
  getSensorStatus: (sensor: Sensor) => { icon: React.ReactNode; text: string; color: string };
}

export function SensorList({
  sensors,
  selectedSensor,
  onSelectSensor,
  getSensorIcon,
  getSensorStatus,
}: SensorListProps) {
  if (sensors.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <p className="text-slate-500">No sensors found</p>
        <p className="text-sm text-slate-400 mt-2">
          Create a sensor or start the simulator
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg">
      <div className="p-4 border-b border-slate-200">
        <h2 className="text-lg font-semibold text-slate-900">Sensors</h2>
      </div>
      <div className="divide-y divide-slate-200 max-h-[600px] overflow-y-auto">
        {sensors.map((sensor) => {
          const status = getSensorStatus(sensor);
          const isSelected = selectedSensor?.id === sensor.id;

          return (
            <div
              key={sensor.id}
              onClick={() => onSelectSensor(sensor)}
              className={`p-4 cursor-pointer transition-colors ${
                isSelected ? 'bg-blue-50' : 'hover:bg-slate-50'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getSensorIcon(sensor.sensor_type)}
                  <div>
                    <h3 className="font-semibold text-slate-900 text-sm">
                      {sensor.name}
                    </h3>
                    <p className="text-xs text-slate-500 font-mono">
                      {sensor.sensor_id}
                    </p>
                  </div>
                </div>
                <div className={`flex items-center gap-1 text-xs ${status.color}`}>
                  {status.icon}
                  <span>{status.text}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-slate-500">Type:</span>{' '}
                  <span className="font-medium text-slate-700">
                    {sensor.sensor_type}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500">Unit:</span>{' '}
                  <span className="font-medium text-slate-700">{sensor.unit}</span>
                </div>
                {sensor.last_reading_value !== null && (
                  <div className="col-span-2">
                    <span className="text-slate-500">Last Reading:</span>{' '}
                    <span className="font-semibold text-slate-900">
                      {sensor.last_reading_value.toFixed(2)} {sensor.unit}
                    </span>
                  </div>
                )}
                {sensor.last_seen_at && (
                  <div className="col-span-2 text-slate-500">
                    Last seen: {new Date(sensor.last_seen_at).toLocaleString()}
                  </div>
                )}
              </div>

              {(sensor.min_threshold !== null || sensor.max_threshold !== null) && (
                <div className="mt-2 pt-2 border-t border-slate-100 text-xs text-slate-500">
                  Thresholds:{' '}
                  {sensor.min_threshold !== null && (
                    <span>Min: {sensor.min_threshold} </span>
                  )}
                  {sensor.max_threshold !== null && (
                    <span>Max: {sensor.max_threshold}</span>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
