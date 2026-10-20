/**
 * Inventory types matching backend schemas.
 */

import type { InventoryTransactionType } from './enums';

export interface InventoryItem {
  id: string;
  depot_id: string;
  sku: string;
  name: string;
  description: string | null;
  category: string | null;
  unit_of_measure: string;
  quantity_on_hand: number;
  quantity_reserved: number;
  quantity_available: number;
  min_stock_level: number;
  max_stock_level: number;
  unit_cost: number;
  currency: string;
  location_code: string | null;
  batch_number: string | null;
  expiry_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface InventoryItemCreate {
  depot_id: string;
  sku: string;
  name: string;
  description?: string;
  category?: string;
  unit_of_measure?: string;
  quantity_on_hand?: number;
  quantity_reserved?: number;
  min_stock_level?: number;
  max_stock_level?: number;
  unit_cost?: number;
  currency?: string;
  location_code?: string;
  batch_number?: string;
  expiry_date?: string;
}

export interface InventoryItemListResponse {
  items: InventoryItem[];
  total: number;
  skip: number;
  limit: number;
}

export interface InventoryTransaction {
  id: string;
  inventory_item_id: string;
  depot_id: string;
  transaction_type: InventoryTransactionType;
  quantity: number;
  unit_of_measure: string;
  reference_id: string | null;
  reference_type: string | null;
  notes: string | null;
  performed_by: string | null;
  performed_at: string;
  created_at: string;
  updated_at: string;
}

export interface InventoryTransactionCreate {
  inventory_item_id: string;
  depot_id: string;
  transaction_type: InventoryTransactionType;
  quantity: number;
  unit_of_measure?: string;
  reference_id?: string;
  reference_type?: string;
  notes?: string;
  performed_by?: string;
  performed_at: string;
}

export interface InventoryTransactionListResponse {
  items: InventoryTransaction[];
  total: number;
  skip: number;
  limit: number;
}
