/**
 * Route types matching backend schemas.
 */

import type { RouteStatus, RouteOptimizationObjective } from './enums';

export interface Route {
  id: string;
  name: string;
  code: string;
  origin_depot_id: string;
  destination_depot_id: string;
  status: RouteStatus;
  distance_km: number;
  estimated_duration_hours: number;
  optimization_objective: RouteOptimizationObjective;
  waypoint_data: string | null;
  vehicle_type: string | null;
  max_weight_kg: number;
  max_volume_m3: number;
  cost_per_km: number;
  carbon_emission_factor: number;
  created_at: string;
  updated_at: string;
}

export interface RouteCreate {
  name: string;
  code: string;
  origin_depot_id: string;
  destination_depot_id: string;
  status?: RouteStatus;
  distance_km: number;
  estimated_duration_hours: number;
  optimization_objective?: RouteOptimizationObjective;
  waypoint_data?: string;
  vehicle_type?: string;
  max_weight_kg?: number;
  max_volume_m3?: number;
  cost_per_km?: number;
  carbon_emission_factor?: number;
}

export interface RouteListResponse {
  items: Route[];
  total: number;
  skip: number;
  limit: number;
}
