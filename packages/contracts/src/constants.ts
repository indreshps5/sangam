/**
 * Shared constants for the SANGAM platform.
 */

export const SHIPMENT_STATUSES = [
  'pending',
  'in_transit',
  'delivered',
  'delayed',
  'cancelled',
] as const;

export const PRIORITY_LEVELS = {
  1: 'Critical',
  2: 'High',
  3: 'Medium',
  4: 'Low',
  5: 'Minimal',
} as const;

export const API_VERSION = 'v1';
export const DEFAULT_PAGE_SIZE = 20;
export const MAX_PAGE_SIZE = 100;

export const REGIONS = [
  'North America',
  'Europe',
  'Asia Pacific',
  'Latin America',
  'Middle East & Africa',
  'South Asia',
] as const;
