/**
 * Sync Service
 * 
 * Handles synchronization between offline data and server.
 * Manages conflict detection and resolution.
 */

import { indexedDBService, StoredInventoryItem, StoredDepot, StoredSensor } from './IndexedDBService';
import { offlineQueueManager } from './OfflineQueueManager';
import { apiClient } from '../../lib/api';

export interface SyncConflict {
  entityType: string;
  entityId: string;
  localVersion: any;
  serverVersion: any;
  conflictType: 'modified' | 'deleted' | 'created';
  resolution?: 'local' | 'server' | 'merged';
}

export interface SyncResult {
  success: boolean;
  synced: number;
  conflicts: SyncConflict[];
  errors: string[];
}

export type ConflictResolutionStrategy = 'local-wins' | 'server-wins' | 'manual';

class SyncService {
  private conflictResolutionStrategy: ConflictResolutionStrategy = 'server-wins';

  /**
   * Set conflict resolution strategy
   */
  setConflictResolutionStrategy(strategy: ConflictResolutionStrategy): void {
    this.conflictResolutionStrategy = strategy;
  }

  /**
   * Sync all data with server
   */
  async syncAll(): Promise<SyncResult> {
    console.log('[SyncService] Starting full sync');

    const result: SyncResult = {
      success: true,
      synced: 0,
      conflicts: [],
      errors: [],
    };

    try {
      // Sync inventory items
      const inventoryResult = await this.syncInventoryItems();
      result.synced += inventoryResult.synced;
      result.conflicts.push(...inventoryResult.conflicts);
      result.errors.push(...inventoryResult.errors);

      // Sync depots
      const depotResult = await this.syncDepots();
      result.synced += depotResult.synced;
      result.conflicts.push(...depotResult.conflicts);
      result.errors.push(...depotResult.errors);

      // Sync sensors
      const sensorResult = await this.syncSensors();
      result.synced += sensorResult.synced;
      result.conflicts.push(...sensorResult.conflicts);
      result.errors.push(...sensorResult.errors);

      // Sync offline queue
      const queueResult = await offlineQueueManager.syncAll();
      result.synced += queueResult.synced;
      result.errors.push(...queueResult.errors.map(e => e.error));

      if (result.conflicts.length > 0 || result.errors.length > 0) {
        result.success = false;
      }

      console.log(`[SyncService] Sync completed: ${result.synced} synced, ${result.conflicts.length} conflicts, ${result.errors.length} errors`);
    } catch (error) {
      result.success = false;
      result.errors.push(error instanceof Error ? error.message : 'Unknown error');
      console.error('[SyncService] Sync failed:', error);
    }

    return result;
  }

  /**
   * Sync inventory items
   */
  private async syncInventoryItems(): Promise<{
    synced: number;
    conflicts: SyncConflict[];
    errors: string[];
  }> {
    const result = {
      synced: 0,
      conflicts: [] as SyncConflict[],
      errors: [] as string[],
    };

    try {
      // Fetch from server
      const response = await apiClient.request<{ items: any[] }>('/api/v1/inventory/items', {
        params: { limit: 1000 },
      });

      const serverItems = response.items || [];

      // Get local items
      const localItems = await indexedDBService.getAllInventoryItems();

      // Create maps for comparison
      const serverMap = new Map(serverItems.map(item => [item.id, item]));
      const localMap = new Map(localItems.map(item => [item.id, item]));

      // Check for conflicts and sync
      for (const serverItem of serverItems) {
        const localItem = localMap.get(serverItem.id);

        if (localItem) {
          // Item exists in both - check for conflicts
          const conflict = await this.detectConflict('inventory-item', serverItem.id, localItem, serverItem);
          
          if (conflict) {
            result.conflicts.push(conflict);
            
            // Resolve conflict based on strategy
            await this.resolveConflict(conflict);
          } else {
            // No conflict, update local with server data
            const storedItem = this.mapToStoredInventoryItem(serverItem);
            await indexedDBService.saveInventoryItem(storedItem);
            result.synced++;
          }
        } else {
          // New item from server
          const storedItem = this.mapToStoredInventoryItem(serverItem);
          await indexedDBService.saveInventoryItem(storedItem);
          result.synced++;
        }
      }

      // Remove local items that no longer exist on server
      for (const localItem of localItems) {
        if (!serverMap.has(localItem.id)) {
          await indexedDBService.deleteInventoryItem(localItem.id);
        }
      }
    } catch (error) {
      result.errors.push(error instanceof Error ? error.message : 'Failed to sync inventory items');
    }

    return result;
  }

  /**
   * Sync depots
   */
  private async syncDepots(): Promise<{
    synced: number;
    conflicts: SyncConflict[];
    errors: string[];
  }> {
    const result = {
      synced: 0,
      conflicts: [] as SyncConflict[],
      errors: [] as string[],
    };

    try {
      // Fetch from server
      const response = await apiClient.request<{ items: any[] }>('/api/v1/depots', {
        params: { limit: 1000 },
      });

      const serverDepots = response.items || [];

      // Get local depots
      const localDepots = await indexedDBService.getAllDepots();

      // Create maps for comparison
      const serverMap = new Map(serverDepots.map(depot => [depot.id, depot]));
      const localMap = new Map(localDepots.map(depot => [depot.id, depot]));

      // Sync depots
      for (const serverDepot of serverDepots) {
        const storedDepot: StoredDepot = {
          id: serverDepot.id,
          name: serverDepot.name,
          code: serverDepot.code,
          latitude: serverDepot.latitude,
          longitude: serverDepot.longitude,
          last_synced_at: new Date().toISOString(),
        };

        await indexedDBService.saveDepot(storedDepot);
        result.synced++;
      }

      // Remove local depots that no longer exist on server
      for (const localDepot of localDepots) {
        if (!serverMap.has(localDepot.id)) {
          await indexedDBService.deleteDepot(localDepot.id);
        }
      }
    } catch (error) {
      result.errors.push(error instanceof Error ? error.message : 'Failed to sync depots');
    }

    return result;
  }

  /**
   * Sync sensors
   */
  private async syncSensors(): Promise<{
    synced: number;
    conflicts: SyncConflict[];
    errors: string[];
  }> {
    const result = {
      synced: 0,
      conflicts: [] as SyncConflict[],
      errors: [] as string[],
    };

    try {
      // Fetch from server
      const response = await apiClient.request<{ items: any[] }>('/api/v1/iot/sensors', {
        params: { limit: 1000 },
      });

      const serverSensors = response.items || [];

      // Get local sensors
      const localSensors = await indexedDBService.getAllSensors();

      // Create maps for comparison
      const serverMap = new Map(serverSensors.map(sensor => [sensor.id, sensor]));
      const localMap = new Map(localSensors.map(sensor => [sensor.id, sensor]));

      // Sync sensors
      for (const serverSensor of serverSensors) {
        const storedSensor: StoredSensor = {
          id: serverSensor.id,
          sensor_id: serverSensor.sensor_id,
          name: serverSensor.name,
          sensor_type: serverSensor.sensor_type,
          unit: serverSensor.unit,
          last_reading_value: serverSensor.last_reading_value,
          last_seen_at: serverSensor.last_seen_at,
          last_synced_at: new Date().toISOString(),
        };

        await indexedDBService.saveSensor(storedSensor);
        result.synced++;
      }

      // Remove local sensors that no longer exist on server
      for (const localSensor of localSensors) {
        if (!serverMap.has(localSensor.id)) {
          await indexedDBService.deleteSensor(localSensor.id);
        }
      }
    } catch (error) {
      result.errors.push(error instanceof Error ? error.message : 'Failed to sync sensors');
    }

    return result;
  }

  /**
   * Detect conflict between local and server data
   */
  private async detectConflict(
    entityType: string,
    entityId: string,
    localData: any,
    serverData: any
  ): Promise<SyncConflict | null> {
    // Get sync status
    const syncStatus = await indexedDBService.getSyncStatusByEntity(entityType, entityId);

    if (!syncStatus) {
      // No sync status, no conflict
      return null;
    }

    // Check if local data has been modified since last sync
    const localUpdatedAt = new Date(localData.local_updated_at || localData.updated_at).getTime();
    const lastSyncedAt = new Date(syncStatus.last_synced_at).getTime();

    if (localUpdatedAt > lastSyncedAt) {
      // Local data has been modified - potential conflict
      return {
        entityType,
        entityId,
        localVersion: localData,
        serverVersion: serverData,
        conflictType: 'modified',
      };
    }

    return null;
  }

  /**
   * Resolve a conflict based on strategy
   */
  private async resolveConflict(conflict: SyncConflict): Promise<void> {
    console.log(`[SyncService] Resolving conflict for ${conflict.entityType}:${conflict.entityId}`);

    switch (this.conflictResolutionStrategy) {
      case 'server-wins':
        // Use server data
        await this.applyServerData(conflict);
        conflict.resolution = 'server';
        break;

      case 'local-wins':
        // Use local data
        await this.applyLocalData(conflict);
        conflict.resolution = 'local';
        break;

      case 'manual':
        // Mark for manual resolution
        conflict.resolution = undefined;
        console.warn('[SyncService] Manual conflict resolution required for:', conflict.entityId);
        break;
    }
  }

  /**
   * Apply server data to local storage
   */
  private async applyServerData(conflict: SyncConflict): Promise<void> {
    switch (conflict.entityType) {
      case 'inventory-item':
        const storedItem = this.mapToStoredInventoryItem(conflict.serverVersion);
        await indexedDBService.saveInventoryItem(storedItem);
        break;

      // Add other entity types as needed
    }
  }

  /**
   * Apply local data to server
   */
  private async applyLocalData(conflict: SyncConflict): Promise<void> {
    // Queue local data for upload
    await offlineQueueManager.enqueue({
      operation: 'update',
      entityType: conflict.entityType,
      entityId: conflict.entityId,
      data: conflict.localVersion,
    });
  }

  /**
   * Map server inventory item to stored format
   */
  private mapToStoredInventoryItem(serverItem: any): StoredInventoryItem {
    return {
      id: serverItem.id,
      name: serverItem.name,
      sku: serverItem.sku,
      depot_id: serverItem.depot_id,
      quantity_on_hand: serverItem.quantity_on_hand,
      quantity_reserved: serverItem.quantity_reserved,
      quantity_available: serverItem.quantity_available,
      min_stock_level: serverItem.min_stock_level,
      unit_of_measure: serverItem.unit_of_measure,
      category: serverItem.category,
      last_synced_at: new Date().toISOString(),
      local_updated_at: serverItem.updated_at || new Date().toISOString(),
    };
  }

  /**
   * Force sync specific entity
   */
  async forceSyncEntity(entityType: string, entityId: string): Promise<void> {
    console.log(`[SyncService] Force syncing ${entityType}:${entityId}`);

    // This would fetch the specific entity from server and update local
    // Implementation depends on entity type
  }

  /**
   * Get sync status for all entities
   */
  async getSyncStatus(): Promise<{
    lastSyncAt: string | null;
    pendingSyncs: number;
    conflicts: number;
  }> {
    const queueStats = await offlineQueueManager.getStats();
    
    // Get last sync time from most recent sync status
    // This is simplified - in production you'd track this properly
    
    return {
      lastSyncAt: null, // Would track this properly
      pendingSyncs: queueStats.pending,
      conflicts: 0, // Would track conflicts
    };
  }
}

// Singleton instance
export const syncService = new SyncService();
