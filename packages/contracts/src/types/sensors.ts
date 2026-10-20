/**
 * Sensor reading and alert types.
 */

import type { SensorType, AlertSeverity, AlertStatus } from './enums';

export interface SensorReading {
  id: string;
  device_id: string;
  depot_id: string | null;
  shipment_id: string | null;
  sensor_type: SensorType;
  reading_value: number;
  unit: string;
  reading_timestamp: string;
  quality_flag: string;
  raw_payload: string | null;
  created_at: string;
  updated_at: string;
}

export interface SensorReadingCreate {
  device_id: string;
  depot_id?: string;
  shipment_id?: string;
  sensor_type: SensorType;
  reading_value: number;
  unit: string;
  reading_timestamp: string;
  quality_flag?: string;
  raw_payload?: string;
}

export interface SensorReadingListResponse {
  items: SensorReading[];
  total: number;
  skip: number;
  limit: number;
}

export interface Alert {
  id: string;
  title: string;
  description: string | null;
  severity: AlertSeverity;
  status: AlertStatus;
  source_type: string;
  source_id: string | null;
  depot_id: string | null;
  shipment_id: string | null;
  triggered_by: string | null;
  acknowledged_by: string | null;
  acknowledged_at: string | null;
  resolved_at: string | null;
  resolution_notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AlertCreate {
  title: string;
  description?: string;
  severity: AlertSeverity;
  status?: AlertStatus;
  source_type: string;
  source_id?: string;
  depot_id?: string;
  shipment_id?: string;
  triggered_by?: string;
}

export interface AlertUpdate {
  status?: AlertStatus;
  acknowledged_by?: string;
  acknowledged_at?: string;
  resolved_at?: string;
  resolution_notes?: string;
}

export interface AlertListResponse {
  items: Alert[];
  total: number;
  skip: number;
  limit: number;
}
