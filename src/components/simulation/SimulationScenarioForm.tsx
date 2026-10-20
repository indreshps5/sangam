/**
 * Simulation Scenario Form
 * 
 * Form for creating new simulation scenarios.
 */

import { useState } from 'react';
import { X } from 'lucide-react';

interface SimulationScenarioFormProps {
  onSubmit: (data: any) => void;
  onClose: () => void;
}

const SCENARIO_TYPES = [
  { value: 'route_closure', label: 'Route Closure' },
  { value: 'shipment_delay', label: 'Shipment Delay' },
  { value: 'increased_demand', label: 'Increased Demand' },
  { value: 'reduced_stock', label: 'Reduced Stock' },
  { value: 'delayed_replenishment', label: 'Delayed Replenishment' },
  { value: 'storage_conditions', label: 'Storage Conditions' },
];

export function SimulationScenarioForm({ onSubmit, onClose }: SimulationScenarioFormProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [scenarioType, setScenarioType] = useState('route_closure');
  const [isDeterministic, setIsDeterministic] = useState(true);
  const [randomSeed, setRandomSeed] = useState<number | null>(null);
  const [parameters, setParameters] = useState<Record<string, any>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    onSubmit({
      name,
      description: description || null,
      scenario_type: scenarioType,
      parameters,
      is_deterministic: isDeterministic,
      random_seed: isDeterministic ? (randomSeed || Math.floor(Math.random() * 1000000)) : null,
    });
  };

  const renderParameterInputs = () => {
    switch (scenarioType) {
      case 'route_closure':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Route ID *
              </label>
              <input
                type="text"
                required
                value={parameters.route_id || ''}
                onChange={(e) => setParameters({ ...parameters, route_id: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="UUID of route"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Duration (hours) *
              </label>
              <input
                type="number"
                required
                min="0.1"
                step="0.1"
                value={parameters.duration_hours || ''}
                onChange={(e) => setParameters({ ...parameters, duration_hours: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Reason
              </label>
              <input
                type="text"
                value={parameters.reason || ''}
                onChange={(e) => setParameters({ ...parameters, reason: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Optional reason"
              />
            </div>
          </>
        );
      
      case 'shipment_delay':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Shipment ID *
              </label>
              <input
                type="text"
                required
                value={parameters.shipment_id || ''}
                onChange={(e) => setParameters({ ...parameters, shipment_id: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="UUID of shipment"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Delay (hours) *
              </label>
              <input
                type="number"
                required
                min="0.1"
                step="0.1"
                value={parameters.delay_hours || ''}
                onChange={(e) => setParameters({ ...parameters, delay_hours: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Reason
              </label>
              <input
                type="text"
                value={parameters.reason || ''}
                onChange={(e) => setParameters({ ...parameters, reason: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Optional reason"
              />
            </div>
          </>
        );
      
      case 'increased_demand':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Inventory Item ID *
              </label>
              <input
                type="text"
                required
                value={parameters.inventory_item_id || ''}
                onChange={(e) => setParameters({ ...parameters, inventory_item_id: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="UUID of inventory item"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Demand Increase (%) *
              </label>
              <input
                type="number"
                required
                min="1"
                max="500"
                value={parameters.demand_increase_percent || ''}
                onChange={(e) => setParameters({ ...parameters, demand_increase_percent: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Duration (days) *
              </label>
              <input
                type="number"
                required
                min="1"
                max="365"
                value={parameters.duration_days || ''}
                onChange={(e) => setParameters({ ...parameters, duration_days: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
          </>
        );
      
      case 'reduced_stock':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Inventory Item ID *
              </label>
              <input
                type="text"
                required
                value={parameters.inventory_item_id || ''}
                onChange={(e) => setParameters({ ...parameters, inventory_item_id: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="UUID of inventory item"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Stock Reduction (%) *
              </label>
              <input
                type="number"
                required
                min="1"
                max="100"
                value={parameters.stock_reduction_percent || ''}
                onChange={(e) => setParameters({ ...parameters, stock_reduction_percent: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Reason
              </label>
              <input
                type="text"
                value={parameters.reason || ''}
                onChange={(e) => setParameters({ ...parameters, reason: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Optional reason"
              />
            </div>
          </>
        );
      
      case 'delayed_replenishment':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Inventory Item ID *
              </label>
              <input
                type="text"
                required
                value={parameters.inventory_item_id || ''}
                onChange={(e) => setParameters({ ...parameters, inventory_item_id: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="UUID of inventory item"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Delay (days) *
              </label>
              <input
                type="number"
                required
                min="1"
                max="365"
                value={parameters.delay_days || ''}
                onChange={(e) => setParameters({ ...parameters, delay_days: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Reason
              </label>
              <input
                type="text"
                value={parameters.reason || ''}
                onChange={(e) => setParameters({ ...parameters, reason: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Optional reason"
              />
            </div>
          </>
        );
      
      case 'storage_conditions':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Depot ID *
              </label>
              <input
                type="text"
                required
                value={parameters.depot_id || ''}
                onChange={(e) => setParameters({ ...parameters, depot_id: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="UUID of depot"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Temperature Change (°C)
              </label>
              <input
                type="number"
                step="0.1"
                value={parameters.temperature_change || ''}
                onChange={(e) => setParameters({ ...parameters, temperature_change: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Humidity Change (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={parameters.humidity_change || ''}
                onChange={(e) => setParameters({ ...parameters, humidity_change: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Duration (hours) *
              </label>
              <input
                type="number"
                required
                min="0.1"
                step="0.1"
                value={parameters.duration_hours || ''}
                onChange={(e) => setParameters({ ...parameters, duration_hours: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Reason
              </label>
              <input
                type="text"
                value={parameters.reason || ''}
                onChange={(e) => setParameters({ ...parameters, reason: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Optional reason"
              />
            </div>
          </>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-slate-200 p-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">
            Create Simulation Scenario
          </h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Scenario Name *
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="e.g., Mumbai-Delhi Route Closure"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Optional description"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Scenario Type *
            </label>
            <select
              required
              value={scenarioType}
              onChange={(e) => {
                setScenarioType(e.target.value);
                setParameters({});
              }}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              {SCENARIO_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div className="border-t border-slate-200 pt-4">
            <h3 className="text-sm font-semibold text-slate-900 mb-3">
              Scenario Parameters
            </h3>
            <div className="space-y-3">
              {renderParameterInputs()}
            </div>
          </div>

          <div className="border-t border-slate-200 pt-4">
            <h3 className="text-sm font-semibold text-slate-900 mb-3">
              Simulation Settings
            </h3>
            <div className="space-y-3">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={isDeterministic}
                  onChange={(e) => setIsDeterministic(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm text-slate-700">
                  Deterministic simulation (reproducible results)
                </span>
              </label>
              {isDeterministic && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Random Seed (optional)
                  </label>
                  <input
                    type="number"
                    value={randomSeed || ''}
                    onChange={(e) => setRandomSeed(e.target.value ? parseInt(e.target.value) : null)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Auto-generated if empty"
                  />
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3 pt-4 border-t border-slate-200">
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Create Scenario
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
