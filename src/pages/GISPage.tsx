/**
 * GIS Page
 * 
 * Full-page GIS view with map and route inspector.
 */

import { useState } from 'react';
import { SANGAMMap } from '../components/gis/SANGAMMap';
import { RouteInspector } from '../components/gis/RouteInspector';
import { Map as MapIcon, X } from 'lucide-react';

export function GISPage() {
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);
  const [selectedShipmentId, setSelectedShipmentId] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                <MapIcon className="text-blue-600" size={28} />
                GIS & Route Management
              </h1>
              <p className="text-sm text-slate-600 mt-1">
                Interactive map showing depots, shipments, and routes
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Map */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                <SANGAMMap
                  selectedShipmentId={selectedShipmentId || undefined}
                  onShipmentSelect={setSelectedShipmentId}
                  height="700px"
                />
              </div>
            </div>
          {/* Sidebar */}
          <div className="space-y-6">
            {/* Route Inspector */}
            {selectedRouteId ? (
              <RouteInspector
                routeId={selectedRouteId}
                onClose={() => setSelectedRouteId(null)}
              />
            ) : (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="text-center py-12">
                  <MapIcon size={48} className="mx-auto text-slate-300 mb-4" />
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    No Route Selected
                  </h3>
                  <p className="text-sm text-slate-600">
                    Click on a route in the map to view details
                  </p>
                </div>
              </div>
            )}

            {/* Quick Stats */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">
                Map Statistics
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Active Shipments</span>
                  <span className="text-lg font-bold text-green-600">
                    {/* Will be populated from map component */}
                    -
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Total Routes</span>
                  <span className="text-lg font-bold text-blue-600">
                    {/* Will be populated from map component */}
                    -
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Disrupted Routes</span>
                  <span className="text-lg font-bold text-red-600">
                    {/* Will be populated from map component */}
                    -
                  </span>
                </div>
              </div>
            </div>

            {/* Instructions */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-blue-900 mb-2">
                How to Use
              </h4>
              <ul className="text-xs text-blue-800 space-y-1">
                <li>• Click on markers to view details</li>
                <li>• Toggle layers using the control panel</li>
                <li>• Click on routes to inspect them</li>
                <li>• Use mouse wheel to zoom</li>
                <li>• Drag to pan the map</li>
              </ul>
            </div>

            {/* Data Notice */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <p className="text-xs text-amber-800">
                <strong>Note:</strong> All coordinates and routes shown are synthetic data
                for demonstration purposes. They do not represent real locations or
                operational routes.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
