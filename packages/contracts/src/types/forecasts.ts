/**
 * Forecast types matching backend Pydantic schemas.
 */

export interface ForecastDataPoint {
  date: string;
  predicted_demand: number;
  lower_bound: number;
  upper_bound: number;
  confidence: number;
}

export interface Forecast {
  id: string;
  warehouse_id: string;
  product_category: string | null;
  forecast_horizon_days: number;
  confidence_level: number;
  data_points: ForecastDataPoint[];
  model_version: string;
  created_at: string;
  accuracy_score: number | null;
}

export interface ForecastRequest {
  warehouse_id: string;
  forecast_horizon_days?: number;
  product_category?: string;
  confidence_level?: number;
}

export interface ForecastListResponse {
  items: Forecast[];
  total: number;
}
