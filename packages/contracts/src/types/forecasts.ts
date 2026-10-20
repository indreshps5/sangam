/**
 * Forecast and demand observation types.
 */

import type { ForecastModelType } from './enums';

export interface ForecastDataPoint {
  id: string;
  forecast_id: string;
  forecast_date: string;
  predicted_demand: number;
  lower_bound: number;
  upper_bound: number;
}

export interface Forecast {
  id: string;
  depot_id: string;
  product_category: string | null;
  model_type: ForecastModelType;
  model_version: string;
  forecast_horizon_days: number;
  confidence_level: number;
  accuracy_score: number | null;
  training_data_end_date: string | null;
  parameters: string | null;
  status: string;
  data_points: ForecastDataPoint[];
  created_at: string;
  updated_at: string;
}

export interface ForecastCreate {
  depot_id: string;
  product_category?: string;
  model_type: ForecastModelType;
  model_version: string;
  forecast_horizon_days: number;
  confidence_level?: number;
  training_data_end_date?: string;
  parameters?: string;
}

export interface ForecastListResponse {
  items: Forecast[];
  total: number;
  skip: number;
  limit: number;
}

export interface DemandObservation {
  id: string;
  depot_id: string;
  product_category: string;
  sku: string | null;
  observation_date: string;
  demand_quantity: number;
  unit_of_measure: string;
  source: string;
  is_outlier: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface DemandObservationCreate {
  depot_id: string;
  product_category: string;
  sku?: string;
  observation_date: string;
  demand_quantity: number;
  unit_of_measure?: string;
  source?: string;
  is_outlier?: boolean;
  notes?: string;
}

export interface DemandObservationListResponse {
  items: DemandObservation[];
  total: number;
  skip: number;
  limit: number;
}
