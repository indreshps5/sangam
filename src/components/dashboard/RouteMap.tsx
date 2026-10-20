/**
 * Live Route & Shipment Tracking Map
 * Interactive map showing active shipments and routes
 */

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { Map as MapIcon, Loader2 } from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { apiClient } from '../../lib/api';

// Fix for default marker icons in Leaflet with webpack/vite
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface Depot {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
}

interface Shipment {
  id: string;
  origin_depot_id: string;
  destination_depot_id: string;
  status: string;
  carrier_name: string | null;
  tracking_number: string | null;
}

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

export function RouteMap() {
  const [depots, setDepots] = useState<Depot[]>([]);
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMapData = async () => {
      try {
        // Fetch depots
        const depotsResponse = await apiClient.request<{ items: Depot[] }>('/depots');
        setDepots(depotsResponse.items);

        // Fetch active shipments
        const shipmentsResponse = await apiClient.request<{ items: Shipment[] }>('/shipments', {
          params: { status: 'in_transit', limit: 10 },
        });
        setShipments(shipmentsResponse.items);

        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load map data');
        setLoading(false);
      }
    };

    fetchMapData();
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-blue-100 p-6">
        <div className="flex items-center justify-center h-96">
          <Loader2 className="animate-spin text-blue-600" size={32} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl border border-blue-100 p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  // Calculate map center based on depots
  const center: [number, number] = depots.length > 0
    ? [
        depots.reduce((sum, d) => sum + d.latitude, 0) / depots.length,
        depots.reduce((sum, d) => sum + d.longitude, 0) / depots.length,
      ]
    : [20.5937, 78.9629]; // Default to India center

  return (
    <div className="bg-white rounded-xl border border-blue-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
            <MapIcon className="text-blue-600" size={20} />
            Live Route & Shipment Tracking
          </h3>
          <p className="text-sm text-slate-500 mt-1">
            Active shipments and depot locations (simulated tracking)
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span className="text-slate-600">Depots ({depots.length})</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-slate-600">In Transit ({shipments.length})</span>
          </div>
        </div>
      </div>

      <div className="rounded-lg overflow-hidden border border-slate-200">
        <MapContainer
          center={center}
          zoom={5}
          style={{ height: '400px', width: '100%' }}
          scrollWheelZoom={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Depot markers */}
          {depots.map((depot) => (
            <Marker
              key={depot.id}
              position={[depot.latitude, depot.longitude]}
              icon={depotIcon}
            >
              <Popup>
                <div className="text-sm">
                  <strong>{depot.name}</strong>
                  <br />
                  <span className="text-slate-600">Depot</span>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Shipment routes (simplified - just show lines between depots) */}
          {shipments.map((shipment) => {
            const origin = depots.find((d) => d.id === shipment.origin_depot_id);
            const destination = depots.find((d) => d.id === shipment.destination_depot_id);

            if (!origin || !destination) return null;

            return (
              <Polyline
                key={shipment.id}
                positions={[
                  [origin.latitude, origin.longitude],
                  [destination.latitude, destination.longitude],
                ]}
                color="#10b981"
                weight={3}
                opacity={0.6}
                dashArray="10, 10"
              />
            );
          })}

          {/* Shipment markers at midpoint */}
          {shipments.map((shipment) => {
            const origin = depots.find((d) => d.id === shipment.origin_depot_id);
            const destination = depots.find((d) => d.id === shipment.destination_depot_id);

            if (!origin || !destination) return null;

            const midLat = (origin.latitude + destination.latitude) / 2;
            const midLng = (origin.longitude + destination.longitude) / 2;

            return (
              <Marker
                key={`shipment-${shipment.id}`}
                position={[midLat, midLng]}
                icon={shipmentIcon}
              >
                <Popup>
                  <div className="text-sm">
                    <strong>Shipment {shipment.tracking_number || shipment.id.slice(0, 8)}</strong>
                    <br />
                    <span className="text-slate-600">
                      {origin.name} → {destination.name}
                    </span>
                    <br />
                    <span className="text-slate-600">
                      Status: {shipment.status}
                    </span>
                    {shipment.carrier_name && (
                      <>
                        <br />
                        <span className="text-slate-600">
                          Carrier: {shipment.carrier_name}
                        </span>
                      </>
                    )}
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>

      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-xs text-blue-800">
          <strong>Note:</strong> Map displays simulated shipment tracking data. 
          Real-time GPS tracking requires integration with a logistics provider API.
        </p>
      </div>
    </div>
  );
}
