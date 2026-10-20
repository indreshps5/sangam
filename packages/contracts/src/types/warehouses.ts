/**
 * Warehouse types matching backend Pydantic schemas.
 */

export interface Warehouse {
  id: string;
  name: string;
  code: string;
  region: string;
  latitude: number;
  longitude: number;
  capacity_units: number;
  current_utilization: number;
  address: string | null;
  created_at: string;
  updated_at: string;
}

export interface WarehouseCreate {
  name: string;
  code: string;
  region: string;
  latitude: number;
  longitude: number;
  capacity_units: number;
  address?: string;
}

export interface WarehouseListResponse {
  items: Warehouse[];
  total: number;
  skip: number;
  limit: number;
}
