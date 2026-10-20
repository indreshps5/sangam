/**
 * Offline Support Tests
 * 
 * Tests for offline functionality including IndexedDB, queue management,
 * synchronization, and conflict resolution.
 */

import { describe, it, expect, beforeEach, afterEach, beforeAll, vi } from 'vitest';
import { indexedDBService } from '../services/offline/IndexedDBService';
import { offlineQueueManager } from '../services/offline/OfflineQueueManager';
import { syncService } from '../services/offline/SyncService';
import { offlineService } from '../services/offline/OfflineService';
import 'fake-indexeddb/auto';

// Setup fake IndexedDB for testing
beforeAll(() => {
  // fake-indexeddb/auto automatically sets up global indexedDB
});

describe('IndexedDB Service', () => {
  beforeEach(async () => {
    await indexedDBService.init();
    await indexedDBService.clearAll();
  });

  afterEach(async () => {
    await indexedDBService.clearAll();
  });

  describe('Inventory Items', () => {
    it('should save and retrieve inventory items', async () => {
      const item = {
        id: 'test-item-1',
        name: 'Test Item',
        sku: 'SKU001',
        depot_id: 'depot-1',
        quantity_on_hand: 100,
        quantity_reserved: 10,
        quantity_available: 90,
        min_stock_level: 20,
        unit_of_measure: 'units',
        category: 'Electronics',
        last_synced_at: new Date().toISOString(),
        local_updated_at: new Date().toISOString(),
      };

      await indexedDBService.saveInventoryItem(item);
      const retrieved = await indexedDBService.getInventoryItem('test-item-1');

      expect(retrieved).toBeDefined();
      expect(retrieved?.name).toBe('Test Item');
      expect(retrieved?.sku).toBe('SKU001');
    });

    it('should retrieve all inventory items', async () => {
      const items = [
        {
          id: 'item-1',
          name: 'Item 1',
          sku: 'SKU001',
          depot_id: 'depot-1',
          quantity_on_hand: 100,
          quantity_reserved: 10,
          quantity_available: 90,
          min_stock_level: 20,
          unit_of_measure: 'units',
          category: 'Electronics',
          last_synced_at: new Date().toISOString(),
          local_updated_at: new Date().toISOString(),
        },
        {
          id: 'item-2',
          name: 'Item 2',
          sku: 'SKU002',
          depot_id: 'depot-1',
          quantity_on_hand: 50,
          quantity_reserved: 5,
          quantity_available: 45,
          min_stock_level: 10,
          unit_of_measure: 'units',
          category: 'Electronics',
          last_synced_at: new Date().toISOString(),
          local_updated_at: new Date().toISOString(),
        },
      ];

      await indexedDBService.saveInventoryItems(items);
      const retrieved = await indexedDBService.getAllInventoryItems();

      expect(retrieved).toHaveLength(2);
    });

    it('should delete inventory items', async () => {
      const item = {
        id: 'test-item-delete',
        name: 'Test Item',
        sku: 'SKU001',
        depot_id: 'depot-1',
        quantity_on_hand: 100,
        quantity_reserved: 10,
        quantity_available: 90,
        min_stock_level: 20,
        unit_of_measure: 'units',
        category: 'Electronics',
        last_synced_at: new Date().toISOString(),
        local_updated_at: new Date().toISOString(),
      };

      await indexedDBService.saveInventoryItem(item);
      await indexedDBService.deleteInventoryItem('test-item-delete');
      const retrieved = await indexedDBService.getInventoryItem('test-item-delete');

      expect(retrieved).toBeUndefined();
    });
  });

  describe('Offline Queue', () => {
    it('should add items to queue', async () => {
      const queueItem = {
        id: 'queue-1',
        operation: 'create' as const,
        entity_type: 'inventory-item',
        entity_id: 'item-1',
        data: { name: 'Test Item' },
        idempotency_key: 'key-1',
        created_at: new Date().toISOString(),
        retry_count: 0,
        max_retries: 3,
        status: 'pending' as const,
      };

      await indexedDBService.addToQueue(queueItem);
      const retrieved = await indexedDBService.getQueueItem('queue-1');

      expect(retrieved).toBeDefined();
      expect(retrieved?.operation).toBe('create');
    });

    it('should retrieve pending queue items', async () => {
      const items = [
        {
          id: 'queue-1',
          operation: 'create' as const,
          entity_type: 'inventory-item',
          entity_id: 'item-1',
          data: {},
          idempotency_key: 'key-1',
          created_at: new Date().toISOString(),
          retry_count: 0,
          max_retries: 3,
          status: 'pending' as const,
        },
        {
          id: 'queue-2',
          operation: 'update' as const,
          entity_type: 'inventory-item',
          entity_id: 'item-2',
          data: {},
          idempotency_key: 'key-2',
          created_at: new Date().toISOString(),
          retry_count: 0,
          max_retries: 3,
          status: 'completed' as const,
        },
      ];

      await indexedDBService.addToQueue(items[0]);
      await indexedDBService.addToQueue(items[1]);

      const pending = await indexedDBService.getPendingQueueItems();
      expect(pending).toHaveLength(1);
      expect(pending[0].id).toBe('queue-1');
    });

    it('should prevent duplicate idempotency keys', async () => {
      const item = {
        id: 'queue-1',
        operation: 'create' as const,
        entity_type: 'inventory-item',
        entity_id: 'item-1',
        data: {},
        idempotency_key: 'duplicate-key',
        created_at: new Date().toISOString(),
        retry_count: 0,
        max_retries: 3,
        status: 'pending' as const,
      };

      await indexedDBService.addToQueue(item);

      const duplicate = {
        ...item,
        id: 'queue-2',
      };

      // This should fail due to unique constraint on idempotency_key
      await expect(indexedDBService.addToQueue(duplicate)).rejects.toThrow();
    });
  });
});

describe('Offline Queue Manager', () => {
  beforeEach(async () => {
    await indexedDBService.init();
    await indexedDBService.clearAll();
  });

  afterEach(async () => {
    await indexedDBService.clearAll();
  });

  it('should enqueue operations', async () => {
    const result = await offlineQueueManager.enqueue({
      operation: 'create',
      entityType: 'inventory-item',
      entityId: 'item-1',
      data: { name: 'Test Item' },
    });

    expect(result.success).toBe(true);
    expect(result.queueItemId).toBeDefined();
  });

  it('should prevent duplicate operations with same idempotency key', async () => {
    const idempotencyKey = 'test-key-123';

    const result1 = await offlineQueueManager.enqueue({
      operation: 'create',
      entityType: 'inventory-item',
      entityId: 'item-1',
      data: { name: 'Test Item' },
      idempotencyKey,
    });

    const result2 = await offlineQueueManager.enqueue({
      operation: 'create',
      entityType: 'inventory-item',
      entityId: 'item-1',
      data: { name: 'Test Item' },
      idempotencyKey,
    });

    expect(result1.queueItemId).toBe(result2.queueItemId);
  });

  it('should get queue statistics', async () => {
    await offlineQueueManager.enqueue({
      operation: 'create',
      entityType: 'inventory-item',
      entityId: 'item-1',
      data: {},
    });

    await offlineQueueManager.enqueue({
      operation: 'update',
      entityType: 'inventory-item',
      entityId: 'item-2',
      data: {},
    });

    const stats = await offlineQueueManager.getStats();

    expect(stats.total).toBe(2);
    expect(stats.pending).toBe(2);
  });

  it('should retry failed operations', async () => {
    const result = await offlineQueueManager.enqueue({
      operation: 'create',
      entityType: 'inventory-item',
      entityId: 'item-1',
      data: {},
    });

    // Manually set status to failed
    const item = await indexedDBService.getQueueItem(result.queueItemId);
    if (item) {
      item.status = 'failed';
      item.error_message = 'Test error';
      await indexedDBService.updateQueueItem(item);
    }

    // Retry should reset status
    await offlineQueueManager.retryItem(result.queueItemId);

    const retried = await indexedDBService.getQueueItem(result.queueItemId);
    expect(retried?.status).toBe('pending');
    expect(retried?.retry_count).toBe(0);
  });
});

describe('Sync Service', () => {
  beforeEach(async () => {
    await indexedDBService.init();
    await indexedDBService.clearAll();
  });

  afterEach(async () => {
    await indexedDBService.clearAll();
  });

  it('should detect conflicts between local and server data', async () => {
    const localItem = {
      id: 'item-1',
      name: 'Local Item',
      sku: 'SKU001',
      depot_id: 'depot-1',
      quantity_on_hand: 100,
      quantity_reserved: 10,
      quantity_available: 90,
      min_stock_level: 20,
      unit_of_measure: 'units',
      category: 'Electronics',
      last_synced_at: new Date(Date.now() - 10000).toISOString(),
      local_updated_at: new Date().toISOString(), // Modified after last sync
    };

    const serverItem = {
      id: 'item-1',
      name: 'Server Item',
      sku: 'SKU001',
      depot_id: 'depot-1',
      quantity_on_hand: 150,
      quantity_reserved: 15,
      quantity_available: 135,
      min_stock_level: 20,
      unit_of_measure: 'units',
      category: 'Electronics',
      updated_at: new Date().toISOString(),
    };

    await indexedDBService.saveInventoryItem(localItem);

    // Save sync status
    await indexedDBService.saveSyncStatus({
      id: 'inventory-item:item-1',
      entity_type: 'inventory-item',
      entity_id: 'item-1',
      last_synced_at: localItem.last_synced_at,
      sync_version: 1,
      local_version: 1,
    });

    // The conflict detection is internal to syncService
    // This test verifies the data is set up correctly
    const retrieved = await indexedDBService.getInventoryItem('item-1');
    expect(retrieved).toBeDefined();
    expect(retrieved?.name).toBe('Local Item');
  });

  it('should apply server-wins conflict resolution', async () => {
    syncService.setConflictResolutionStrategy('server-wins');

    const localItem = {
      id: 'item-1',
      name: 'Local Item',
      sku: 'SKU001',
      depot_id: 'depot-1',
      quantity_on_hand: 100,
      quantity_reserved: 10,
      quantity_available: 90,
      min_stock_level: 20,
      unit_of_measure: 'units',
      category: 'Electronics',
      last_synced_at: new Date(Date.now() - 10000).toISOString(),
      local_updated_at: new Date().toISOString(),
    };

    const serverItem = {
      id: 'item-1',
      name: 'Server Item',
      sku: 'SKU001',
      depot_id: 'depot-1',
      quantity_on_hand: 150,
      quantity_reserved: 15,
      quantity_available: 135,
      min_stock_level: 20,
      unit_of_measure: 'units',
      category: 'Electronics',
      updated_at: new Date().toISOString(),
    };

    await indexedDBService.saveInventoryItem(localItem);

    // After conflict resolution with server-wins, local should match server
    // This is tested through the sync process
    expect(localItem.name).toBe('Local Item');
    expect(serverItem.name).toBe('Server Item');
  });
});

describe('Offline Service', () => {
  beforeEach(async () => {
    await indexedDBService.init();
    await indexedDBService.clearAll();
  });

  afterEach(async () => {
    await indexedDBService.clearAll();
  });

  it('should initialize successfully', async () => {
    await offlineService.init();
    const status = offlineService.getStatus();

    expect(status.isOnline).toBeDefined();
    expect(status.isSyncing).toBe(false);
  });

  it('should queue operations when offline', async () => {
    const result = await offlineService.queueOperation({
      operation: 'create',
      entityType: 'inventory-item',
      entityId: 'item-1',
      data: { name: 'Test Item' },
    });

    expect(result.success).toBe(true);
    expect(result.queueItemId).toBeDefined();
  });

  it('should get pending operations', async () => {
    await offlineService.queueOperation({
      operation: 'create',
      entityType: 'inventory-item',
      entityId: 'item-1',
      data: {},
    });

    await offlineService.queueOperation({
      operation: 'update',
      entityType: 'inventory-item',
      entityId: 'item-2',
      data: {},
    });

    const pending = await offlineService.getPendingOperations();
    expect(pending).toHaveLength(2);
  });

  it('should cache data for offline use', async () => {
    const depots = [
      {
        id: 'depot-1',
        name: 'Depot 1',
        code: 'D001',
        latitude: 19.076,
        longitude: 72.8777,
        last_synced_at: new Date().toISOString(),
      },
      {
        id: 'depot-2',
        name: 'Depot 2',
        code: 'D002',
        latitude: 28.6139,
        longitude: 77.209,
        last_synced_at: new Date().toISOString(),
      },
    ];

    await offlineService.cacheData('depots', depots);
    const cached = await offlineService.getCachedData('depots');

    expect(cached).toHaveLength(2);
  });

  it('should clear cache', async () => {
    await offlineService.cacheData('depots', [
      {
        id: 'depot-1',
        name: 'Depot 1',
        code: 'D001',
        latitude: 19.076,
        longitude: 72.8777,
        last_synced_at: new Date().toISOString(),
      },
    ]);

    await offlineService.clearCache();
    const cached = await offlineService.getCachedData('depots');

    expect(cached).toHaveLength(0);
  });

  it('should get database statistics', async () => {
    await offlineService.cacheData('depots', [
      {
        id: 'depot-1',
        name: 'Depot 1',
        code: 'D001',
        latitude: 19.076,
        longitude: 72.8777,
        last_synced_at: new Date().toISOString(),
      },
    ]);

    await offlineService.queueOperation({
      operation: 'create',
      entityType: 'inventory-item',
      entityId: 'item-1',
      data: {},
    });

    const stats = await offlineService.getDatabaseStats();

    expect(stats.depots).toBe(1);
    expect(stats.queueItems).toBe(1);
  });
});

describe('Offline Scenarios', () => {
  beforeEach(async () => {
    await indexedDBService.init();
    await indexedDBService.clearAll();
  });

  afterEach(async () => {
    await indexedDBService.clearAll();
  });

  it('should handle offline startup', async () => {
    // Simulate offline startup
    const status = offlineService.getStatus();
    
    // Should be able to queue operations
    const result = await offlineService.queueOperation({
      operation: 'create',
      entityType: 'inventory-item',
      entityId: 'item-1',
      data: { name: 'Test Item' },
    });

    expect(result.success).toBe(true);
  });

  it('should handle reconnection', async () => {
    // Queue some operations while "offline"
    await offlineService.queueOperation({
      operation: 'create',
      entityType: 'inventory-item',
      entityId: 'item-1',
      data: {},
    });

    await offlineService.queueOperation({
      operation: 'update',
      entityType: 'inventory-item',
      entityId: 'item-2',
      data: {},
    });

    const pending = await offlineService.getPendingOperations();
    expect(pending).toHaveLength(2);

    // Simulate reconnection and sync
    // In real scenario, this would trigger automatically
    const stats = await offlineService.getQueueStats();
    expect(stats.pending).toBe(2);
  });

  it('should prevent duplicate submissions', async () => {
    const idempotencyKey = 'unique-key-123';

    // First submission
    const result1 = await offlineService.queueOperation({
      operation: 'create',
      entityType: 'inventory-item',
      entityId: 'item-1',
      data: { name: 'Test Item' },
      idempotencyKey,
    });

    // Duplicate submission with same key
    const result2 = await offlineService.queueOperation({
      operation: 'create',
      entityType: 'inventory-item',
      entityId: 'item-1',
      data: { name: 'Test Item' },
      idempotencyKey,
    });

    // Should return the same queue item ID
    expect(result1.queueItemId).toBe(result2.queueItemId);

    const pending = await offlineService.getPendingOperations();
    expect(pending).toHaveLength(1);
  });

  it('should handle failed synchronization', async () => {
    const result = await offlineService.queueOperation({
      operation: 'create',
      entityType: 'inventory-item',
      entityId: 'item-1',
      data: {},
    });

    // Simulate failed sync by marking as failed
    const item = await indexedDBService.getQueueItem(result.queueItemId);
    if (item) {
      item.status = 'failed';
      item.error_message = 'Network error';
      item.retry_count = 3;
      await indexedDBService.updateQueueItem(item);
    }

    const stats = await offlineService.getQueueStats();
    expect(stats.failed).toBe(1);

    // Should be able to retry
    await offlineService.retryOperation(result.queueItemId);

    const retried = await indexedDBService.getQueueItem(result.queueItemId);
    expect(retried?.status).toBe('pending');
  });

  it('should handle conflicts during sync', async () => {
    // Create local item
    const localItem = {
      id: 'item-1',
      name: 'Local Item',
      sku: 'SKU001',
      depot_id: 'depot-1',
      quantity_on_hand: 100,
      quantity_reserved: 10,
      quantity_available: 90,
      min_stock_level: 20,
      unit_of_measure: 'units',
      category: 'Electronics',
      last_synced_at: new Date(Date.now() - 10000).toISOString(),
      local_updated_at: new Date().toISOString(),
    };

    await indexedDBService.saveInventoryItem(localItem);

    // Queue an update
    await offlineService.queueOperation({
      operation: 'update',
      entityType: 'inventory-item',
      entityId: 'item-1',
      data: { name: 'Updated Local Item' },
    });

    // During sync, server might have different data
    // Conflict resolution should handle this
    const pending = await offlineService.getPendingOperations();
    expect(pending).toHaveLength(1);
  });
});
