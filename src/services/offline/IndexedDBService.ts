/**
 * IndexedDB Service for SANGAM
 * 
 * Provides typed access to IndexedDB for offline data storage.
 * Handles database creation, migrations, and CRUD operations.
 */

import { openDB, IDBPDatabase } from 'idb';

// Database name and version
const DB_NAME = 'sangam-offline-db';
const DB_VERSION = 1;

// Store names
export const STORES = {
  INVENTORY_ITEMS: 'inventory-items',
  DEPOTS: 'depots',
  SENSORS: 'sensors',
  OFFLINE_QUEUE: 'offline-queue',
  SYNC_STATUS: 'sync-status',
  USER_PREFERENCES: 'user-preferences',
} as const;

// Types for stored data
export interface StoredInventoryItem {
  id: string;
  name: string;
  sku: string;
  depot_id: string;
  quantity_on_hand: number;
  quantity_reserved: number;
  quantity_available: number;
  min_stock_level: number;
  unit_of_measure: string;
  category: string | null;
  last_synced_at: string;
  local_updated_at: string;
}

export interface StoredDepot {
  id: string;
  name: string;
  code: string;
  latitude: number;
  longitude: number;
  last_synced_at: string;
}

export interface StoredSensor {
  id: string;
  sensor_id: string;
  name: string;
  sensor_type: string;
  unit: string;
  last_reading_value: number | null;
  last_seen_at: string | null;
  last_synced_at: string;
}

export interface OfflineQueueItem {
  id: string;
  operation: 'create' | 'update' | 'delete';
  entity_type: string;
  entity_id: string;
  data: any;
  idempotency_key: string;
  created_at: string;
  retry_count: number;
  max_retries: number;
  status: 'pending' | 'syncing' | 'completed' | 'failed';
  error_message?: string;
  last_attempt_at?: string;
}

export interface SyncStatus {
  id: string;
  entity_type: string;
  entity_id: string;
  last_synced_at: string;
  sync_version: number;
  local_version: number;
}

export interface UserPreferences {
  id: string;
  user_id: string;
  last_inventory_filter: any;
  cached_views: string[];
  offline_mode_enabled: boolean;
}

class IndexedDBService {
  private db: IDBPDatabase | null = null;
  private initPromise: Promise<void> | null = null;

  /**
   * Initialize the database
   */
  async init(): Promise<void> {
    if (this.db) {
      return;
    }

    if (this.initPromise) {
      return this.initPromise;
    }

    this.initPromise = this.createDatabase();
    await this.initPromise;
  }

  /**
   * Create and configure the database
   */
  private async createDatabase(): Promise<void> {
    this.db = await openDB(DB_NAME, DB_VERSION, {
      upgrade(db: any, oldVersion: number, newVersion: number | null, transaction: any) {
        // Create object stores
        if (!db.objectStoreNames.contains(STORES.INVENTORY_ITEMS)) {
          const inventoryStore = db.createObjectStore(STORES.INVENTORY_ITEMS, {
            keyPath: 'id',
          });
          inventoryStore.createIndex('depot_id', 'depot_id', { unique: false });
          inventoryStore.createIndex('sku', 'sku', { unique: false });
          inventoryStore.createIndex('category', 'category', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.DEPOTS)) {
          const depotStore = db.createObjectStore(STORES.DEPOTS, {
            keyPath: 'id',
          });
          depotStore.createIndex('code', 'code', { unique: true });
        }

        if (!db.objectStoreNames.contains(STORES.SENSORS)) {
          const sensorStore = db.createObjectStore(STORES.SENSORS, {
            keyPath: 'id',
          });
          sensorStore.createIndex('sensor_id', 'sensor_id', { unique: true });
          sensorStore.createIndex('sensor_type', 'sensor_type', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.OFFLINE_QUEUE)) {
          const queueStore = db.createObjectStore(STORES.OFFLINE_QUEUE, {
            keyPath: 'id',
          });
          queueStore.createIndex('status', 'status', { unique: false });
          queueStore.createIndex('entity_type', 'entity_type', { unique: false });
          queueStore.createIndex('idempotency_key', 'idempotency_key', { unique: true });
          queueStore.createIndex('created_at', 'created_at', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.SYNC_STATUS)) {
          const syncStore = db.createObjectStore(STORES.SYNC_STATUS, {
            keyPath: 'id',
          });
          syncStore.createIndex('entity_type', 'entity_type', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.USER_PREFERENCES)) {
          db.createObjectStore(STORES.USER_PREFERENCES, {
            keyPath: 'id',
          });
        }
      },
    });
  }

  /**
   * Get database instance
   */
  private getDB(): IDBPDatabase {
    if (!this.db) {
      throw new Error('Database not initialized. Call init() first.');
    }
    return this.db;
  }

  // ============================================
  // Inventory Items
  // ============================================

  async getInventoryItem(id: string): Promise<StoredInventoryItem | undefined> {
    await this.init();
    return this.getDB().get(STORES.INVENTORY_ITEMS, id);
  }

  async getAllInventoryItems(): Promise<StoredInventoryItem[]> {
    await this.init();
    return this.getDB().getAll(STORES.INVENTORY_ITEMS);
  }

  async getInventoryItemsByDepot(depotId: string): Promise<StoredInventoryItem[]> {
    await this.init();
    return this.getDB().getAllFromIndex(STORES.INVENTORY_ITEMS, 'depot_id', depotId);
  }

  async saveInventoryItem(item: StoredInventoryItem): Promise<void> {
    await this.init();
    await this.getDB().put(STORES.INVENTORY_ITEMS, item);
  }

  async saveInventoryItems(items: StoredInventoryItem[]): Promise<void> {
    await this.init();
    const tx = this.getDB().transaction(STORES.INVENTORY_ITEMS, 'readwrite');
    await Promise.all(items.map(item => tx.store.put(item)));
    await tx.done;
  }

  async deleteInventoryItem(id: string): Promise<void> {
    await this.init();
    await this.getDB().delete(STORES.INVENTORY_ITEMS, id);
  }

  async clearInventoryItems(): Promise<void> {
    await this.init();
    await this.getDB().clear(STORES.INVENTORY_ITEMS);
  }

  // ============================================
  // Depots
  // ============================================

  async getDepot(id: string): Promise<StoredDepot | undefined> {
    await this.init();
    return this.getDB().get(STORES.DEPOTS, id);
  }

  async getAllDepots(): Promise<StoredDepot[]> {
    await this.init();
    return this.getDB().getAll(STORES.DEPOTS);
  }

  async saveDepot(depot: StoredDepot): Promise<void> {
    await this.init();
    await this.getDB().put(STORES.DEPOTS, depot);
  }

  async saveDepots(depots: StoredDepot[]): Promise<void> {
    await this.init();
    const tx = this.getDB().transaction(STORES.DEPOTS, 'readwrite');
    await Promise.all(depots.map(depot => tx.store.put(depot)));
    await tx.done;
  }

  async clearDepots(): Promise<void> {
    await this.init();
    await this.getDB().clear(STORES.DEPOTS);
  }

  async deleteDepot(id: string): Promise<void> {
    await this.init();
    await this.getDB().delete(STORES.DEPOTS, id);
  }

  // ============================================
  // Sensors
  // ============================================

  async getSensor(id: string): Promise<StoredSensor | undefined> {
    await this.init();
    return this.getDB().get(STORES.SENSORS, id);
  }

  async getAllSensors(): Promise<StoredSensor[]> {
    await this.init();
    return this.getDB().getAll(STORES.SENSORS);
  }

  async saveSensor(sensor: StoredSensor): Promise<void> {
    await this.init();
    await this.getDB().put(STORES.SENSORS, sensor);
  }

  async saveSensors(sensors: StoredSensor[]): Promise<void> {
    await this.init();
    const tx = this.getDB().transaction(STORES.SENSORS, 'readwrite');
    await Promise.all(sensors.map(sensor => tx.store.put(sensor)));
    await tx.done;
  }

  async clearSensors(): Promise<void> {
    await this.init();
    await this.getDB().clear(STORES.SENSORS);
  }

  async deleteSensor(id: string): Promise<void> {
    await this.init();
    await this.getDB().delete(STORES.SENSORS, id);
  }

  // ============================================
  // Offline Queue
  // ============================================

  async addToQueue(item: OfflineQueueItem): Promise<void> {
    await this.init();
    await this.getDB().put(STORES.OFFLINE_QUEUE, item);
  }

  async getQueueItem(id: string): Promise<OfflineQueueItem | undefined> {
    await this.init();
    return this.getDB().get(STORES.OFFLINE_QUEUE, id);
  }

  async getQueueItemByIdempotencyKey(key: string): Promise<OfflineQueueItem | undefined> {
    await this.init();
    return this.getDB().getFromIndex(STORES.OFFLINE_QUEUE, 'idempotency_key', key);
  }

  async getAllQueueItems(): Promise<OfflineQueueItem[]> {
    await this.init();
    return this.getDB().getAll(STORES.OFFLINE_QUEUE);
  }

  async getPendingQueueItems(): Promise<OfflineQueueItem[]> {
    await this.init();
    return this.getDB().getAllFromIndex(STORES.OFFLINE_QUEUE, 'status', 'pending');
  }

  async updateQueueItem(item: OfflineQueueItem): Promise<void> {
    await this.init();
    await this.getDB().put(STORES.OFFLINE_QUEUE, item);
  }

  async removeQueueItem(id: string): Promise<void> {
    await this.init();
    await this.getDB().delete(STORES.OFFLINE_QUEUE, id);
  }

  async clearCompletedQueueItems(): Promise<void> {
    await this.init();
    const items = await this.getDB().getAllFromIndex(STORES.OFFLINE_QUEUE, 'status', 'completed');
    const tx = this.getDB().transaction(STORES.OFFLINE_QUEUE, 'readwrite');
    await Promise.all(items.map((item: OfflineQueueItem) => tx.store.delete(item.id)));
    await tx.done;
  }

  async clearQueue(): Promise<void> {
    await this.init();
    await this.getDB().clear(STORES.OFFLINE_QUEUE);
  }

  // ============================================
  // Sync Status
  // ============================================

  async getSyncStatus(id: string): Promise<SyncStatus | undefined> {
    await this.init();
    return this.getDB().get(STORES.SYNC_STATUS, id);
  }

  async saveSyncStatus(status: SyncStatus): Promise<void> {
    await this.init();
    await this.getDB().put(STORES.SYNC_STATUS, status);
  }

  async getSyncStatusByEntity(entityType: string, entityId: string): Promise<SyncStatus | undefined> {
    await this.init();
    const id = `${entityType}:${entityId}`;
    return this.getDB().get(STORES.SYNC_STATUS, id);
  }

  // ============================================
  // User Preferences
  // ============================================

  async getUserPreferences(userId: string): Promise<UserPreferences | undefined> {
    await this.init();
    return this.getDB().get(STORES.USER_PREFERENCES, userId);
  }

  async saveUserPreferences(preferences: UserPreferences): Promise<void> {
    await this.init();
    await this.getDB().put(STORES.USER_PREFERENCES, preferences);
  }

  // ============================================
  // Utility Methods
  // ============================================

  async clearAll(): Promise<void> {
    await this.init();
    const storeNames = Object.values(STORES);
    const tx = this.getDB().transaction(storeNames, 'readwrite');
    await Promise.all(storeNames.map(store => tx.objectStore(store).clear()));
    await tx.done;
  }

  async getDatabaseStats(): Promise<{
    inventoryItems: number;
    depots: number;
    sensors: number;
    queueItems: number;
    pendingQueueItems: number;
  }> {
    await this.init();
    const [inventoryItems, depots, sensors, queueItems, pendingItems] = await Promise.all([
      this.getDB().count(STORES.INVENTORY_ITEMS),
      this.getDB().count(STORES.DEPOTS),
      this.getDB().count(STORES.SENSORS),
      this.getDB().count(STORES.OFFLINE_QUEUE),
      this.getDB().count(STORES.OFFLINE_QUEUE),
    ]);

    return {
      inventoryItems,
      depots,
      sensors,
      queueItems,
      pendingQueueItems: pendingItems,
    };
  }

  async close(): Promise<void> {
    if (this.db) {
      this.db.close();
      this.db = null;
      this.initPromise = null;
    }
  }
}

// Singleton instance
export const indexedDBService = new IndexedDBService();

// Initialize on import
indexedDBService.init().catch(error => {
  console.error('[IndexedDB] Failed to initialize:', error);
});
