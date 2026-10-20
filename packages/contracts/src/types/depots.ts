/**
 * Depot types matching backend Pydantic schemas.
 */

import type { DepotType, DepotStatus } from './enums';

export interface Depot {
  id: string;
  name: string;
  code: string;
  depot_type: DepotType;
  status: DepotStatus;
  region: string;
  latitude: number;
  longitude: number;
  capacity_units: number;
  current_utilization: number;
  address: string | null;
  contact_email: string | null;
  contact_phone: string | null;
  created_at: string;
  updated_at: string;
}

export interface DepotCreate {
  name: string;
  code: string;
  depot_type: DepotType;
  status?: DepotStatus;
  region: string;
  latitude: number;
  longitude: number;
  capacity_units: number;
  address?: string;
  contact_email?: string;
  contact_phone?: string;
}

export interface DepotUpdate {
  name?: string;
  depot_type?: DepotType;
  status?: DepotStatus;
  region?: string;
  latitude?: number;
  longitude?: number;
  capacity_units?: number;
  current_utilization?: number;
  address?: string;
  contact_email?: string;
  contact_phone?: string;
}

export interface DepotListResponse {
  items: Depot[];
  total: number;
  skip: number;
  limit: number;
}
