/**
 * Simulation Comparison
 * 
 * Displays comparison between baseline and simulation results.
 */

import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Truck,
  Package,
  Route,
} from 'lucide-react';

interface SimulationScenario {
  id: string;
  name: string;
  description: string | null;
  scenario_type: string;
  parameters: Record<string, any>;
  baseline_snapshot: any;
  results: any;
  executed_at: string | null;
  execution_duration_ms: number | null;
  is_deterministic: boolean;
}

interface SimulationComparisonProps {
  scenario: SimulationScenario;
}

export function SimulationComparison({ scenario }: SimulationComparisonProps) {
  const results = scenario.results;

  if (!results) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <p className="text-slate-500">No results available</p>
      </div>
    );
  }

  const getScenarioTypeName = (type: string) => {
    const types: Record<string, string> = {
      route_closure: 'Route Closure',
      shipment_delay: 'Shipment Delay',
      increased_demand: 'Increased Demand',
      reduced_stock: 'Reduced Stock',
      delayed_replenishment: 'Delayed Replenishment',
      storage_conditions: 'Storage Conditions',
    };
    return types[type] || type;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-slate-900 mb-2">
          {scenario.name}
        </h2>
        <p className="text-sm text-slate-600 mb-4">
          {scenario.description || 'No description'}
        </p>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-slate-500">Type:</span>{' '}
            <span className="font-medium">{getScenarioTypeName(scenario.scenario_type)}</span>
          </div>
          <div>
            <span className="text-slate-500">Executed:</span>{' '}
            <span className="font-medium">
              {scenario.executed_at ? new Date(scenario.executed_at).toLocaleString() : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-slate-500">Duration:</span>{' '}
            <span className="font-medium">
              {scenario.execution_duration_ms ? `${scenario.execution_duration_ms}ms` : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-slate-500">Deterministic:</span>{' '}
            <span className="font-medium">
              {scenario.is_deterministic ? 'Yes' : 'No'}
            </span>
          </div>
        </div>
      </div>

      {/* Summary */}
      {results.summary && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4 flex items-center gap-2">
            <TrendingUp size={20} />
            Impact Summary
          </h3>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(results.summary).map(([key, value]) => (
              <div key={key} className="bg-white rounded-lg p-3">
                <p className="text-xs text-slate-500 mb-1">
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </p>
                <p className="text-lg font-bold text-slate-900">
                  {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Shipment Impacts */}
      {results.shipment_impacts && results.shipment_impacts.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <Truck size={20} className="text-green-600" />
            Shipment Impacts ({results.shipment_impacts.length})
          </h3>
          <div className="space-y-3">
            {results.shipment_impacts.map((impact: any, index: number) => (
              <div key={index} className="border border-slate-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-semibold text-slate-900">
                      {impact.tracking_number || 'Shipment'}
                    </p>
                    <p className="text-xs text-slate-500 font-mono">
                      {impact.shipment_id}
                    </p>
                  </div>
                  {impact.delay_hours && impact.delay_hours > 0 && (
                    <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-semibold">
                      +{impact.delay_hours.toFixed(1)}h delay
                    </span>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-slate-500">Baseline Arrival:</span>
                    <p className="font-medium">
                      {impact.baseline_arrival
                        ? new Date(impact.baseline_arrival).toLocaleString()
                        : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <span className="text-slate-500">Simulated Arrival:</span>
                    <p className="font-medium">
                      {impact.simulated_arrival
                        ? new Date(impact.simulated_arrival).toLocaleString()
                        : 'N/A'}
                    </p>
                  </div>
                </div>
                {impact.alternative_route_name && (
                  <div className="mt-2 text-sm">
                    <span className="text-slate-500">Alternative Route:</span>{' '}
                    <span className="font-medium text-blue-600">
                      {impact.alternative_route_name}
                    </span>
                  </div>
                )}
                <p className="text-xs text-slate-600 mt-2">
                  {impact.impact_description}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Inventory Impacts */}
      {results.inventory_impacts && results.inventory_impacts.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <Package size={20} className="text-orange-600" />
            Inventory Impacts ({results.inventory_impacts.length})
          </h3>
          <div className="space-y-3">
            {results.inventory_impacts.map((impact: any, index: number) => (
              <div key={index} className="border border-slate-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-semibold text-slate-900">{impact.item_name}</p>
                    <p className="text-xs text-slate-500">
                      {impact.sku} • {impact.depot_name}
                    </p>
                  </div>
                  {impact.stockout_risk && (
                    <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-semibold flex items-center gap-1">
                      <AlertTriangle size={12} />
                      Stockout Risk
                    </span>
                  )}
                </div>
                <div className="grid grid-cols-3 gap-3 text-sm">
                  <div>
                    <span className="text-slate-500">Baseline Stock:</span>
                    <p className="font-medium">{impact.baseline_stock.toFixed(0)}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Simulated Stock:</span>
                    <p className={`font-medium ${impact.simulated_stock < impact.baseline_stock ? 'text-red-600' : ''}`}>
                      {impact.simulated_stock.toFixed(0)}
                    </p>
                  </div>
                  <div>
                    <span className="text-slate-500">Change:</span>
                    <p className={`font-medium ${impact.stock_change < 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {impact.stock_change > 0 ? '+' : ''}{impact.stock_change.toFixed(0)}
                    </p>
                  </div>
                </div>
                {impact.days_until_stockout && (
                  <p className="text-xs text-red-600 mt-2">
                    ⚠️ Stockout in {impact.days_until_stockout.toFixed(1)} days
                  </p>
                )}
                <p className="text-xs text-slate-600 mt-2">
                  {impact.impact_description}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Route Impacts */}
      {results.route_impacts && results.route_impacts.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <Route size={20} className="text-purple-600" />
            Route Impacts ({results.route_impacts.length})
          </h3>
          <div className="space-y-3">
            {results.route_impacts.map((impact: any, index: number) => (
              <div key={index} className="border border-slate-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-semibold text-slate-900">{impact.route_name}</p>
                    <p className="text-xs text-slate-500 font-mono">
                      {impact.route_id}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 bg-slate-100 text-slate-800 rounded text-xs">
                      {impact.baseline_status}
                    </span>
                    <span className="text-slate-400">→</span>
                    <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-semibold">
                      {impact.simulated_status}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-slate-600">
                  {impact.affected_shipments} shipments affected
                </p>
                {impact.alternative_routes && impact.alternative_routes.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-slate-500 mb-1">Alternative Routes:</p>
                    <div className="flex flex-wrap gap-2">
                      {impact.alternative_routes.map((alt: any, i: number) => (
                        <span key={i} className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">
                          {alt.name} ({alt.distance_km?.toFixed(0)} km)
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                <p className="text-xs text-slate-600 mt-2">
                  {impact.impact_description}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {results.recommendations && results.recommendations.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-green-900 mb-4 flex items-center gap-2">
            <CheckCircle size={20} />
            Recommendations
          </h3>
          <ul className="space-y-2">
            {results.recommendations.map((rec: string, index: number) => (
              <li key={index} className="flex items-start gap-2 text-sm text-green-800">
                <span className="text-green-600 mt-0.5">•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Assumptions and Limitations */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-amber-900 mb-4 flex items-center gap-2">
          <AlertTriangle size={20} />
          Assumptions & Limitations
        </h3>
        {results.assumptions && results.assumptions.length > 0 && (
          <div className="mb-4">
            <p className="text-sm font-semibold text-amber-900 mb-2">Assumptions:</p>
            <ul className="space-y-1">
              {results.assumptions.map((assumption: string, index: number) => (
                <li key={index} className="flex items-start gap-2 text-xs text-amber-800">
                  <span className="text-amber-600 mt-0.5">•</span>
                  <span>{assumption}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        {results.limitations && results.limitations.length > 0 && (
          <div>
            <p className="text-sm font-semibold text-amber-900 mb-2">Limitations:</p>
            <ul className="space-y-1">
              {results.limitations.map((limitation: string, index: number) => (
                <li key={index} className="flex items-start gap-2 text-xs text-amber-800">
                  <span className="text-amber-600 mt-0.5">•</span>
                  <span>{limitation}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Read-Only Notice */}
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
        <p className="text-xs text-slate-600 text-center">
          ℹ️ This simulation is read-only. No operational data (inventory, shipments, routes) was modified.
          All results are based on synthetic data and simplified calculations for demonstration purposes.
        </p>
      </div>
    </div>
  );
}
