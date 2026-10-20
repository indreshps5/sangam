/**
 * SANGAM Map Component
 * 
 * Interactive map displaying depots, shipments, and routes using Leaflet.
 * Integrates with existing API client and contracts.
 */

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { apiClient } from '../../lib/api';
import {
  MapPin,
  Truck,
  Route as RouteIcon,
  AlertTriangle,
  Info,
  Layers,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';

// Fix Leaflet default icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons
const depotIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const shipmentIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const disruptedIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

interface Depot {
  id: string;
  name: string;
  code: string;
  latitude: number;
  longitude: number;
  status: string;
}

interface Shipment {
  id: string;
  tracking_number: string | null;
  status: string;
  origin_depot_id: string;
  destination_depot_id: string;
  route_id: string | null;
  current_location: {
    latitude: number;
    longitude: number;
    timestamp: string;
  } | null;
  priority: number;
}

interface Route {
  id: string;
  name: string;
  code: string;
  origin_depot_id: string;
  destination_depot_id: string;
  status: string;
  route_type: string;
  distance_km: number | null;
  duration_minutes: number | null;
  waypoints: Array<{ latitude: number; longitude: number }> | null;
  route_data: any;
  is_disrupted: boolean;
  disruption_reason?: string | null;
}

interface MapProps {
  selectedShipmentId?: string;
  onShipmentSelect?: (shipmentId: string) => void;
  height?: string;
}

export function SANGAMMap({ selectedShipmentId, onShipmentSelect, height = '600px' }: MapProps) {
  const [depots, setDepots] = useState<Depot[]>([]);
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [routes, setRoutes] = useState<Route[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDepots, setShowDepots] = useState(true);
  const [showShipments, setShowShipments] = useState(true);
  const [showRoutes, setShowRoutes] = useState(true);
  const [selectedShipment, setSelectedShipment] = useState<Shipment | null>(null);

  useEffect(() => {
    loadMapData();
  }, []);

  useEffect(() => {
    if (selectedShipmentId) {
      const shipment = shipments.find(s => s.id === selectedShipmentId);
      setSelectedShipment(shipment || null);
    }
  }, [selectedShipmentId, shipments]);

  const loadMapData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load depots
      const depotsResponse = await apiClient.request<{ items: Depot[] }>('/depots');
      setDepots(depotsResponse.items);

      // Load active shipments
      const shipmentsResponse = await apiClient.request<{ items: Shipment[] }>('/shipments', {
        params: {
          status: 'in_transit',
          limit: 50
        }
      });
      setShipments(shipmentsResponse.items);

      // Load routes
      const routesResponse = await apiClient.request<{ items: Route[] }>('/routes', {
        params: {
          limit: 50
        }
      });
      setRoutes(routesResponse.items);

      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load map data');
      setLoading(false);
    }
  };

  const handleShipmentClick = (shipment: Shipment) => {
    setSelectedShipment(shipment);
    if (onShipmentSelect) {
      onShipmentSelect(shipment.id);
    }
  };

  const getRouteColor = (route: Route) => {
    if (route.is_disrupted) return '#ef4444'; // red
    if (route.route_type === 'alternative') return '#f59e0b'; // amber
    if (route.route_type === 'emergency') return '#8b5cf6'; // purple
    return '#3b82f6'; // blue (primary)
  };

  const getRouteForShipment = (shipment: Shipment) => {
    if (!shipment.route_id) return null;
    return routes.find(r => r.id === shipment.route_id);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading map data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6" style={{ height }}>
        <div className="flex items-center gap-3 text-red-800">
          <AlertTriangle size={24} />
          <div>
            <p className="font-semibold">Failed to load map</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
        <button
          onClick={loadMapData}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  // Calculate map center based on depots
  const center: [number, number] = depots.length > 0
    ? [
        depots.reduce((sum, d) => sum + d.latitude, 0) / depots.length,
        depots.reduce((sum, d) => sum + d.longitude, 0) / depots.length,
      ]
    : [20.5937, 78.9629]; // Default to India

  return (
    <div className="relative" style={{ height }}>
      {/* Map Controls */}
      <div className="absolute top-4 right-4 z-[1000] bg-white rounded-lg shadow-lg p-3 space-y-2">
        <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
          <Layers size={16} />
          Layers
        </h3>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={showDepots}
            onChange={(e) => setShowDepots(e.target.checked)}
            className="rounded"
          />
          <MapPin size={14} className="text-blue-600" />
          Depots ({depots.length})
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={showShipments}
            onChange={(e) => setShowShipments(e.target.checked)}
            className="rounded"
          />
          <Truck size={14} className="text-green-600" />
          Shipments ({shipments.length})
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={showRoutes}
            onChange={(e) => setShowRoutes(e.target.checked)}
            className="rounded"
          />
          <RouteIcon size={14} className="text-purple-600" />
          Routes ({routes.length})
        </label>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-white rounded-lg shadow-lg p-3">
        <h3 className="text-sm font-semibold text-slate-900 mb-2">Legend</h3>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span>Depot</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span>Shipment</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-0.5 bg-blue-500"></div>
            <span>Primary Route</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-0.5 bg-amber-500"></div>
            <span>Alternative Route</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-0.5 bg-red-500"></div>
            <span>Disrupted Route</span>
          </div>
        </div>
        <div className="mt-2 pt-2 border-t border-slate-200">
          <p className="text-xs text-slate-500 italic">
            * Synthetic data for demonstration
          </p>
        </div>
      </div>

      {/* Selected Shipment Info */}
      {selectedShipment && (
        <div className="absolute top-4 left-4 z-[1000] bg-white rounded-lg shadow-lg p-4 max-w-sm">
          <div className="flex items-start justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Truck size={16} className="text-green-600" />
              Shipment Details
            </h3>
            <button
              onClick={() => setSelectedShipment(null)}
              className="text-slate-400 hover:text-slate-600"
            >
              ×
            </button>
          </div>
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-slate-500">Tracking:</span>{' '}
              <span className="font-mono">{selectedShipment.tracking_number || 'N/A'}</span>
            </div>
            <div>
              <span className="text-slate-500">Status:</span>{' '}
              <span className="font-semibold">{selectedShipment.status}</span>
            </div>
            <div>
              <span className="text-slate-500">Priority:</span>{' '}
              <span>{selectedShipment.priority}</span>
            </div>
            {selectedShipment.current_location && (
              <div>
                <span className="text-slate-500">Location:</span>{' '}
                <span className="font-mono text-xs">
                  {selectedShipment.current_location.latitude.toFixed(4)},{' '}
                  {selectedShipment.current_location.longitude.toFixed(4)}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Map */}
      <MapContainer
        center={center}
        zoom={5}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Depots */}
        {showDepots && depots.map((depot) => (
          <Marker
            key={depot.id}
            position={[depot.latitude, depot.longitude]}
            icon={depotIcon}
          >
            <Popup>
              <div className="text-sm">
                <strong className="text-blue-600">{depot.name}</strong>
                <br />
                <span className="text-slate-600">Code: {depot.code}</span>
                <br />
                <span className="text-slate-600">Status: {depot.status}</span>
                <br />
                <span className="text-xs text-slate-500">
                  {depot.latitude.toFixed(4)}, {depot.longitude.toFixed(4)}
                </span>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Shipments */}
        {showShipments && shipments.map((shipment) => {
          if (!shipment.current_location) return null;

          return (
            <Marker
              key={shipment.id}
              position={[
                shipment.current_location.latitude,
                shipment.current_location.longitude,
              ]}
              icon={shipmentIcon}
              eventHandlers={{
                click: () => handleShipmentClick(shipment),
              }}
            >
              <Popup>
                <div className="text-sm">
                  <strong className="text-green-600">Shipment</strong>
                  <br />
                  <span className="text-slate-600">
                    Tracking: {shipment.tracking_number || 'N/A'}
                  </span>
                  <br />
                  <span className="text-slate-600">Status: {shipment.status}</span>
                  <br />
                  <span className="text-slate-600">Priority: {shipment.priority}</span>
                  <br />
                  <button
                    onClick={() => handleShipmentClick(shipment)}
                    className="mt-2 px-2 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700"
                  >
                    View Details
                  </button>
                </div>
              </Popup>
            </Marker>
          );
        })}

        {/* Routes */}
        {showRoutes && routes.map((route) => {
          const originDepot = depots.find(d => d.id === route.origin_depot_id);
          const destinationDepot = depots.find(d => d.id === route.destination_depot_id);

          if (!originDepot || !destinationDepot) return null;

          // Build route path
          const path: [number, number][] = [
            [originDepot.latitude, originDepot.longitude],
          ];

          // Add waypoints if available
          if (route.waypoints) {
            route.waypoints.forEach(wp => {
              path.push([wp.latitude, wp.longitude]);
            });
          } else if (route.route_data?.segments) {
            // Use segments from route calculation
            route.route_data.segments.forEach((seg: any) => {
              seg.waypoints?.forEach((wp: any) => {
                path.push([wp.lat, wp.lng]);
              });
            });
          }

          path.push([destinationDepot.latitude, destinationDepot.longitude]);

          return (
            <Polyline
              key={route.id}
              positions={path}
              color={getRouteColor(route)}
              weight={route.is_disrupted ? 4 : 3}
              opacity={route.is_disrupted ? 0.8 : 0.6}
              dashArray={route.route_type === 'alternative' ? '10, 10' : undefined}
            >
              <Popup>
                <div className="text-sm">
                  <strong className="text-purple-600">{route.name}</strong>
                  <br />
                  <span className="text-slate-600">Code: {route.code}</span>
                  <br />
                  <span className="text-slate-600">Type: {route.route_type}</span>
                  <br />
                  <span className="text-slate-600">Status: {route.status}</span>
                  {route.distance_km && (
                    <>
                      <br />
                      <span className="text-slate-600">
                        Distance: {route.distance_km.toFixed(1)} km
                      </span>
                    </>
                  )}
                  {route.duration_minutes && (
                    <>
                      <br />
                      <span className="text-slate-600">
                        Duration: {(route.duration_minutes / 60).toFixed(1)} hours
                      </span>
                    </>
                  )}
                  {route.is_disrupted && route.disruption_reason && (
                    <>
                      <br />
                      <span className="text-red-600 font-semibold">
                        ⚠️ {route.disruption_reason}
                      </span>
                    </>
                  )}
                </div>
              </Popup>
            </Polyline>
          );
        })}
      </MapContainer>
    </div>
  );
}
