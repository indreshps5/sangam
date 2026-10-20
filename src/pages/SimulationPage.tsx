/**
 * Simulation Page
 * 
 * What-if disruption simulation interface.
 * Allows users to create, execute, and analyze simulation scenarios.
 */

import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api';
import {
  FlaskConical,
  Plus,
  Play,
  Trash2,
  Eye,
  AlertCircle,
  CheckCircle,
  Clock,
  XCircle,
} from 'lucide-react';
import { SimulationScenarioForm } from '../components/simulation/SimulationScenarioForm';
import { SimulationComparison } from '../components/simulation/SimulationComparison';

interface SimulationScenario {
  id: string;
  name: string;
  description: string | null;
  scenario_type: string;
  parameters: Record<string, any>;
  status: 'draft' | 'running' | 'completed' | 'failed';
  created_at: string;
  executed_at: string | null;
  execution_duration_ms: number | null;
  error_message: string | null;
  is_deterministic: boolean;
  baseline_snapshot: any;
  results: any;
}

export function SimulationPage() {
  const [scenarios, setScenarios] = useState<SimulationScenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState<SimulationScenario | null>(null);
  const [executing, setExecuting] = useState<string | null>(null);

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.request<{ items: SimulationScenario[] }>('/simulation', {
        params: { limit: 100 }
      });
      setScenarios(response.items);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scenarios');
      setLoading(false);
    }
  };

  const handleCreateScenario = async (data: any) => {
    try {
      await apiClient.request('/simulation', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      setShowForm(false);
      loadScenarios();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create scenario');
    }
  };

  const handleExecuteScenario = async (scenarioId: string) => {
    setExecuting(scenarioId);
    setError(null);

    try {
      await apiClient.request(`/simulation/${scenarioId}/execute`, {
        method: 'POST',
      });
      await loadScenarios();
      setExecuting(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute scenario');
      setExecuting(null);
    }
  };

  const handleDeleteScenario = async (scenarioId: string) => {
    if (!confirm('Are you sure you want to delete this scenario?')) {
      return;
    }

    try {
      await apiClient.request(`/simulation/${scenarioId}`, {
        method: 'DELETE',
      });
      await loadScenarios();
      if (selectedScenario?.id === scenarioId) {
        setSelectedScenario(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete scenario');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'draft':
        return <Clock size={16} className="text-slate-500" />;
      case 'running':
        return <Play size={16} className="text-blue-500 animate-pulse" />;
      case 'completed':
        return <CheckCircle size={16} className="text-green-500" />;
      case 'failed':
        return <XCircle size={16} className="text-red-500" />;
      default:
        return <Clock size={16} className="text-slate-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft':
        return 'bg-slate-100 text-slate-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-slate-100 text-slate-800';
    }
  };

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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
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
                <FlaskConical className="text-purple-600" size={28} />
                What-if Disruption Simulation
              </h1>
              <p className="text-sm text-slate-600 mt-1">
                Simulate supply chain disruptions and analyze impacts (read-only)
              </p>
            </div>
            <button
              onClick={() => setShowForm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              <Plus size={18} />
              New Scenario
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-3 text-red-800">
              <AlertCircle size={20} />
              <p>{error}</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Scenarios List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg">
              <div className="p-4 border-b border-slate-200">
                <h2 className="text-lg font-semibold text-slate-900">
                  Scenarios ({scenarios.length})
                </h2>
              </div>
              <div className="divide-y divide-slate-200 max-h-[600px] overflow-y-auto">
                {scenarios.length === 0 ? (
                  <div className="p-8 text-center text-slate-500">
                    <FlaskConical size={48} className="mx-auto mb-3 text-slate-300" />
                    <p>No scenarios yet</p>
                    <p className="text-sm mt-1">Create your first simulation scenario</p>
                  </div>
                ) : (
                  scenarios.map((scenario) => (
                    <div
                      key={scenario.id}
                      className={`p-4 hover:bg-slate-50 cursor-pointer transition-colors ${
                        selectedScenario?.id === scenario.id ? 'bg-purple-50' : ''
                      }`}
                      onClick={() => setSelectedScenario(scenario)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <h3 className="font-semibold text-slate-900 text-sm">
                            {scenario.name}
                          </h3>
                          <p className="text-xs text-slate-500 mt-1">
                            {getScenarioTypeName(scenario.scenario_type)}
                          </p>
                        </div>
                        <div className="flex items-center gap-1">
                          {getStatusIcon(scenario.status)}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 mt-2">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(scenario.status)}`}>
                          {scenario.status}
                        </span>
                        {scenario.is_deterministic && (
                          <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                            Deterministic
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 mt-3">
                        {scenario.status === 'draft' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleExecuteScenario(scenario.id);
                            }}
                            disabled={executing === scenario.id}
                            className="flex items-center gap-1 px-2 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700 disabled:opacity-50"
                          >
                            <Play size={12} />
                            {executing === scenario.id ? 'Running...' : 'Execute'}
                          </button>
                        )}
                        {scenario.status === 'completed' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedScenario(scenario);
                            }}
                            className="flex items-center gap-1 px-2 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700"
                          >
                            <Eye size={12} />
                            View Results
                          </button>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteScenario(scenario.id);
                          }}
                          className="flex items-center gap-1 px-2 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700"
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Scenario Details / Comparison */}
          <div className="lg:col-span-2">
            {selectedScenario ? (
              selectedScenario.status === 'completed' ? (
                <SimulationComparison scenario={selectedScenario} />
              ) : (
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h2 className="text-lg font-semibold text-slate-900 mb-4">
                    {selectedScenario.name}
                  </h2>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-slate-500">Type</p>
                      <p className="text-sm font-medium text-slate-900">
                        {getScenarioTypeName(selectedScenario.scenario_type)}
                      </p>
                    </div>
                    {selectedScenario.description && (
                      <div>
                        <p className="text-sm text-slate-500">Description</p>
                        <p className="text-sm text-slate-900">{selectedScenario.description}</p>
                      </div>
                    )}
                    <div>
                      <p className="text-sm text-slate-500">Parameters</p>
                      <pre className="text-xs bg-slate-50 p-3 rounded mt-1 overflow-x-auto">
                        {JSON.stringify(selectedScenario.parameters, null, 2)}
                      </pre>
                    </div>
                    {selectedScenario.status === 'failed' && selectedScenario.error_message && (
                      <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                        <p className="text-sm font-semibold text-red-900">Error</p>
                        <p className="text-xs text-red-700 mt-1">{selectedScenario.error_message}</p>
                      </div>
                    )}
                    {selectedScenario.status === 'draft' && (
                      <button
                        onClick={() => handleExecuteScenario(selectedScenario.id)}
                        disabled={executing === selectedScenario.id}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                      >
                        <Play size={18} />
                        {executing === selectedScenario.id ? 'Executing...' : 'Execute Simulation'}
                      </button>
                    )}
                  </div>
                </div>
              )
            ) : (
              <div className="bg-white rounded-lg shadow-lg p-12 text-center">
                <FlaskConical size={64} className="mx-auto mb-4 text-slate-300" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  No Scenario Selected
                </h3>
                <p className="text-sm text-slate-600">
                  Select a scenario from the list to view details and results
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Important Notice */}
        <div className="mt-6 bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle size={20} className="text-amber-600 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-amber-900">
                Read-Only Simulation
              </p>
              <p className="text-xs text-amber-800 mt-1">
                All simulations are read-only and do not modify operational data (inventory, shipments, routes).
                Results are stored for review and comparison only. Synthetic data is used where real data is unavailable.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Scenario Form Modal */}
      {showForm && (
        <SimulationScenarioForm
          onSubmit={handleCreateScenario}
          onClose={() => setShowForm(false)}
        />
      )}
    </div>
  );
}
