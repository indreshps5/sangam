/**
 * Route Inspector Panel
 * 
 * Displays detailed information about a selected route.
 */

import { useState, useEffect } from 'react';
import { apiClient } from '../../lib/api';
import {
  Route as RouteIcon,
  MapPin,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
} from 'lucide-react';

interface Coordinate {
  latitude: number;
  longitude: number;
}

interface RouteSegment {
  start: Coordinate;
  end: Coordinate;
  distance_km: number;
  duration_minutes: number;
  waypoints: Coordinate[];
}

interface Route {
  id: string;
  name: string;
  code: string;
  origin_depot_id: string;
  destination_depot_id: string;
  route_type: string;
  status: string;
  vehicle_type: string;
  distance_km: number | null;
  duration_minutes: number | null;
  max_weight_kg: number;
  max_volume_m3: number;
  waypoints: Coordinate[] | null;
  disruption_reason: string | null;
  disruption_severity: string | null;
  route_data: any;
  notes: string | null;
  origin_depot_name: string | null;
  destination_depot_name: string | null;
  is_calculated: boolean;
  is_disrupted: boolean;
  segments?: RouteSegment[];
  created_at: string;
  updated_at: string;
}

interface RouteInspectorProps {
  routeId: string | null;
  onClose: () => void;
}

export function RouteInspector({ routeId, onClose }: RouteInspectorProps) {
  const [route, setRoute] = useState<Route | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (routeId) {
      loadRoute(routeId);
    }
  }, [routeId]);

  const loadRoute = async (id: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.request<Route>(`/routes/${id}`);
      setRoute(response);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load route');
      setLoading(false);
    }
  };

  if (!routeId) return null;

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-slate-200 rounded w-3/4"></div>
          <div className="h-4 bg-slate-200 rounded w-1/2"></div>
          <div className="h-4 bg-slate-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center gap-3 text-red-800">
          <XCircle size={20} />
          <div>
            <p className="font-semibold">Failed to load route</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!route) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'planned':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'completed':
        return 'bg-slate-100 text-slate-800 border-slate-200';
      case 'disrupted':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'cancelled':
        return 'bg-slate-100 text-slate-600 border-slate-300';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  const getRouteTypeColor = (type: string) => {
    switch (type) {
      case 'primary':
        return 'text-blue-600';
      case 'alternative':
        return 'text-amber-600';
      case 'emergency':
        return 'text-purple-600';
      default:
        return 'text-slate-600';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4 text-white">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-bold flex items-center gap-2">
              <RouteIcon size={20} />
              {route.name}
            </h2>
            <p className="text-sm text-blue-100 font-mono">{route.code}</p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:text-blue-200 transition-colors"
          >
            <XCircle size={24} />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Status Badges */}
        <div className="flex flex-wrap gap-2">
          <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(route.status)}`}>
            {route.status.toUpperCase()}
          </span>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getRouteTypeColor(route.route_type)}`}>
            {route.route_type.toUpperCase()}
          </span>
          {route.is_disrupted && (
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800 border border-red-200">
              ⚠️ DISRUPTED
            </span>
          )}
        </div>

        {/* Route Info */}
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <MapPin size={18} className="text-green-600 mt-0.5" />
            <div className="flex-1">
              <p className="text-xs text-slate-500">Origin</p>
              <p className="text-sm font-semibold text-slate-900">
                {route.origin_depot_name || 'Unknown'}
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <MapPin size={18} className="text-red-600 mt-0.5" />
            <div className="flex-1">
              <p className="text-xs text-slate-500">Destination</p>
              <p className="text-sm font-semibold text-slate-900">
                {route.destination_depot_name || 'Unknown'}
              </p>
            </div>
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-3">
          {route.distance_km && (
            <div className="bg-slate-50 rounded-lg p-3">
              <div className="flex items-center gap-2 text-slate-500 mb-1">
                <TrendingUp size={14} />
                <span className="text-xs">Distance</span>
              </div>
              <p className="text-lg font-bold text-slate-900">
                {route.distance_km.toFixed(1)} km
              </p>
            </div>
          )}

          {route.duration_minutes && (
            <div className="bg-slate-50 rounded-lg p-3">
              <div className="flex items-center gap-2 text-slate-500 mb-1">
                <Clock size={14} />
                <span className="text-xs">Duration</span>
              </div>
              <p className="text-lg font-bold text-slate-900">
                {(route.duration_minutes / 60).toFixed(1)} hrs
              </p>
            </div>
          )}

          <div className="bg-slate-50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-slate-500 mb-1">
              <span className="text-xs">Max Weight</span>
            </div>
            <p className="text-lg font-bold text-slate-900">
              {route.max_weight_kg.toLocaleString()} kg
            </p>
          </div>

          <div className="bg-slate-50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-slate-500 mb-1">
              <span className="text-xs">Max Volume</span>
            </div>
            <p className="text-lg font-bold text-slate-900">
              {route.max_volume_m3.toFixed(1)} m³
            </p>
          </div>
        </div>

        {/* Disruption Info */}
        {route.is_disrupted && route.disruption_reason && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-start gap-2">
              <AlertTriangle size={18} className="text-red-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-semibold text-red-900">Route Disrupted</p>
                <p className="text-xs text-red-700 mt-1">{route.disruption_reason}</p>
                {route.disruption_severity && (
                  <p className="text-xs text-red-600 mt-1">
                    Severity: {route.disruption_severity}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Route Calculation Status */}
        {!route.is_calculated && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
            <div className="flex items-start gap-2">
              <AlertTriangle size={18} className="text-amber-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-semibold text-amber-900">Route Not Calculated</p>
                <p className="text-xs text-amber-700 mt-1">
                  Distance and duration will be shown after route calculation.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Vehicle Type */}
        <div>
          <p className="text-xs text-slate-500 mb-1">Vehicle Type</p>
          <p className="text-sm font-semibold text-slate-900">
            {route.vehicle_type || 'Not specified'}
          </p>
        </div>

        {/* Notes */}
        {route.notes && (
          <div>
            <p className="text-xs text-slate-500 mb-1">Notes</p>
            <p className="text-sm text-slate-700">{route.notes}</p>
          </div>
        )}

        {/* Metadata */}
        <div className="pt-3 border-t border-slate-200">
          <div className="grid grid-cols-2 gap-2 text-xs text-slate-500">
            <div>
              <span className="font-semibold">Created:</span>{' '}
              {new Date(route.created_at).toLocaleDateString()}
            </div>
            <div>
              <span className="font-semibold">Updated:</span>{' '}
              {new Date(route.updated_at).toLocaleDateString()}
            </div>
          </div>
        </div>

        {/* Synthetic Data Notice */}
        <div className="bg-slate-50 rounded-lg p-3">
          <p className="text-xs text-slate-600 italic">
            ℹ️ Route data is synthetic and for demonstration purposes only.
            Distance and duration calculations use simplified algorithms.
          </p>
        </div>
      </div>
    </div>
  );
}
