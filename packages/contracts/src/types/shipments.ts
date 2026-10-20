/**
 * Shipment types matching backend Pydantic schemas.
 */

export type ShipmentStatus = 'pending' | 'in_transit' | 'delivered' | 'delayed' | 'cancelled';

export interface Shipment {
  id: string;
  origin_warehouse_id: string;
  destination_warehouse_id: string;
  status: ShipmentStatus;
  weight_kg: number;
  volume_m3: number;
  priority: number;
  estimated_arrival: string | null;
  actual_arrival: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ShipmentCreate {
  origin_warehouse_id: string;
  destination_warehouse_id: string;
  status?: ShipmentStatus;
  weight_kg: number;
  volume_m3: number;
  priority?: number;
  estimated_arrival?: string;
  notes?: string;
}

export interface ShipmentListResponse {
  items: Shipment[];
  total: number;
  skip: number;
  limit: number;
}
