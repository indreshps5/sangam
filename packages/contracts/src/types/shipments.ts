/**
 * Shipment types matching backend schemas.
 */

import type { ShipmentStatus } from './enums';

export interface Shipment {
  id: string;
  origin_depot_id: string;
  destination_depot_id: string;
  route_id: string | null;
  status: ShipmentStatus;
  weight_kg: number;
  volume_m3: number;
  priority: number;
  shipment_type: string;
  carrier_name: string | null;
  tracking_number: string | null;
  estimated_departure: string | null;
  actual_departure: string | null;
  estimated_arrival: string | null;
  actual_arrival: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ShipmentCreate {
  origin_depot_id: string;
  destination_depot_id: string;
  route_id?: string;
  status?: ShipmentStatus;
  weight_kg: number;
  volume_m3: number;
  priority?: number;
  shipment_type?: string;
  carrier_name?: string;
  tracking_number?: string;
  estimated_departure?: string;
  estimated_arrival?: string;
  notes?: string;
}

export interface ShipmentUpdate {
  status?: ShipmentStatus;
  route_id?: string;
  weight_kg?: number;
  volume_m3?: number;
  priority?: number;
  carrier_name?: string;
  tracking_number?: string;
  estimated_departure?: string;
  actual_departure?: string;
  estimated_arrival?: string;
  actual_arrival?: string;
  notes?: string;
}

export interface ShipmentListResponse {
  items: Shipment[];
  total: number;
  skip: number;
  limit: number;
}
