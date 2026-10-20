/**
 * Canonical enumerations matching backend Python enums.
 */

export const DepotType = {
  WAREHOUSE: 'warehouse',
  DISTRIBUTION_CENTER: 'distribution_center',
  CROSS_DOCK: 'cross_dock',
  COLD_STORAGE: 'cold_storage',
  YARD: 'yard',
} as const;
export type DepotType = (typeof DepotType)[keyof typeof DepotType];

export const DepotStatus = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  MAINTENANCE: 'maintenance',
  DECOMMISSIONED: 'decommissioned',
} as const;
export type DepotStatus = (typeof DepotStatus)[keyof typeof DepotStatus];

export const InventoryTransactionType = {
  RECEIPT: 'receipt',
  SHIPMENT: 'shipment',
  TRANSFER: 'transfer',
  ADJUSTMENT: 'adjustment',
  RETURN: 'return',
  DAMAGE: 'damage',
  COUNT_CORRECTION: 'count_correction',
} as const;
export type InventoryTransactionType =
  (typeof InventoryTransactionType)[keyof typeof InventoryTransactionType];

export const ShipmentStatus = {
  PENDING: 'pending',
  PICKED_UP: 'picked_up',
  IN_TRANSIT: 'in_transit',
  AT_HUB: 'at_hub',
  OUT_FOR_DELIVERY: 'out_for_delivery',
  DELIVERED: 'delivered',
  DELAYED: 'delayed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
  RETURNED: 'returned',
} as const;
export type ShipmentStatus = (typeof ShipmentStatus)[keyof typeof ShipmentStatus];

export const RouteStatus = {
  PLANNED: 'planned',
  ACTIVE: 'active',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled',
} as const;
export type RouteStatus = (typeof RouteStatus)[keyof typeof RouteStatus];

export const RouteOptimizationObjective = {
  MINIMIZE_COST: 'minimize_cost',
  MINIMIZE_TIME: 'minimize_time',
  MINIMIZE_DISTANCE: 'minimize_distance',
  MINIMIZE_EMISSIONS: 'minimize_emissions',
  BALANCED: 'balanced',
} as const;
export type RouteOptimizationObjective =
  (typeof RouteOptimizationObjective)[keyof typeof RouteOptimizationObjective];

export const SensorType = {
  TEMPERATURE: 'temperature',
  HUMIDITY: 'humidity',
  GPS: 'gps',
  VIBRATION: 'vibration',
  PRESSURE: 'pressure',
  LIGHT: 'light',
  DOOR_OPEN: 'door_open',
  FUEL_LEVEL: 'fuel_level',
} as const;
export type SensorType = (typeof SensorType)[keyof typeof SensorType];

export const AlertSeverity = {
  INFO: 'info',
  WARNING: 'warning',
  CRITICAL: 'critical',
  EMERGENCY: 'emergency',
} as const;
export type AlertSeverity = (typeof AlertSeverity)[keyof typeof AlertSeverity];

export const AlertStatus = {
  TRIGGERED: 'triggered',
  ACKNOWLEDGED: 'acknowledged',
  INVESTIGATING: 'investigating',
  RESOLVED: 'resolved',
  FALSE_POSITIVE: 'false_positive',
} as const;
export type AlertStatus = (typeof AlertStatus)[keyof typeof AlertStatus];

export const SimulationStatus = {
  DRAFT: 'draft',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
  ARCHIVED: 'archived',
} as const;
export type SimulationStatus = (typeof SimulationStatus)[keyof typeof SimulationStatus];

export const RecommendationStatus = {
  GENERATED: 'generated',
  UNDER_REVIEW: 'under_review',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  IMPLEMENTED: 'implemented',
  EXPIRED: 'expired',
} as const;
export type RecommendationStatus =
  (typeof RecommendationStatus)[keyof typeof RecommendationStatus];

export const RecommendationCategory = {
  INVENTORY_REBALANCE: 'inventory_rebalance',
  ROUTE_OPTIMIZATION: 'route_optimization',
  DEMAND_FORECAST: 'demand_forecast',
  MAINTENANCE: 'maintenance',
  PROCUREMENT: 'procurement',
  CAPACITY_PLANNING: 'capacity_planning',
} as const;
export type RecommendationCategory =
  (typeof RecommendationCategory)[keyof typeof RecommendationCategory];

export const ApprovalStatus = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  ESCALATED: 'escalated',
  WITHDRAWN: 'withdrawn',
} as const;
export type ApprovalStatus = (typeof ApprovalStatus)[keyof typeof ApprovalStatus];

export const AuditAction = {
  CREATE: 'create',
  UPDATE: 'update',
  DELETE: 'delete',
  APPROVE: 'approve',
  REJECT: 'reject',
  LOGIN: 'login',
  LOGOUT: 'logout',
  EXPORT: 'export',
  IMPORT: 'import',
  CONFIG_CHANGE: 'config_change',
} as const;
export type AuditAction = (typeof AuditAction)[keyof typeof AuditAction];

export const UserRole = {
  SUPER_ADMIN: 'super_admin',
  ADMIN: 'admin',
  MANAGER: 'manager',
  OPERATOR: 'operator',
  ANALYST: 'analyst',
  VIEWER: 'viewer',
  DRIVER: 'driver',
  AUDITOR: 'auditor',
} as const;
export type UserRole = (typeof UserRole)[keyof typeof UserRole];

export const ForecastModelType = {
  ARIMA: 'arima',
  SARIMA: 'sarima',
  PROPHET: 'prophet',
  XGBOOST: 'xgboost',
  LSTM: 'lstm',
  ENSEMBLE: 'ensemble',
  EXPONENTIAL_SMOOTHING: 'exponential_smoothing',
} as const;
export type ForecastModelType =
  (typeof ForecastModelType)[keyof typeof ForecastModelType];
