/**
 * Common types used across the SANGAM platform.
 */

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface ApiError {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance: string;
  [key: string]: unknown;
}

export interface HealthStatus {
  status: 'healthy' | 'not_ready' | 'alive';
  service?: string;
  database?: string;
  timestamp: string;
  error?: string;
}

export interface GeoCoordinate {
  latitude: number;
  longitude: number;
}
