/**
 * Offline Queue Manager
 * 
 * Manages the queue of operations to be synchronized when online.
 * Handles idempotency, retries, and conflict detection.
 */

import { v4 as uuidv4 } from 'uuid';
import { indexedDBService, OfflineQueueItem } from './IndexedDBService';
import { apiClient } from '../../lib/api';

export type QueueOperation = 'create' | 'update' | 'delete';

export interface QueueOperationRequest {
  operation: QueueOperation;
  entityType: string;
  entityId: string;
  data: any;
  idempotencyKey?: string;
}

export interface QueueOperationResult {
  success: boolean;
  queueItemId: string;
  error?: string;
}

export interface SyncResult {
  success: boolean;
  synced: number;
  failed: number;
  conflicts: number;
  errors: Array<{
    queueItemId: string;
    error: string;
    conflict?: boolean;
  }>;
}

class OfflineQueueManager {
  private maxRetries = 3;
  private retryDelayMs = 5000; // 5 seconds

  /**
   * Add an operation to the offline queue
   */
  async enqueue(request: QueueOperationRequest): Promise<QueueOperationResult> {
    // Generate idempotency key if not provided
    const idempotencyKey = request.idempotencyKey || this.generateIdempotencyKey(request);

    // Check for duplicate
    const existing = await indexedDBService.getQueueItemByIdempotencyKey(idempotencyKey);
    if (existing) {
      console.log('[OfflineQueue] Duplicate operation detected:', idempotencyKey);
      return {
        success: true,
        queueItemId: existing.id,
      };
    }

    // Create queue item
    const queueItem: OfflineQueueItem = {
      id: uuidv4(),
      operation: request.operation,
      entity_type: request.entityType,
      entity_id: request.entityId,
      data: request.data,
      idempotency_key: idempotencyKey,
      created_at: new Date().toISOString(),
      retry_count: 0,
      max_retries: this.maxRetries,
      status: 'pending',
    };

    await indexedDBService.addToQueue(queueItem);

    console.log('[OfflineQueue] Operation queued:', queueItem.id);

    return {
      success: true,
      queueItemId: queueItem.id,
    };
  }

  /**
   * Generate idempotency key for an operation
   */
  private generateIdempotencyKey(request: QueueOperationRequest): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(7);
    return `${request.operation}:${request.entityType}:${request.entityId}:${timestamp}:${random}`;
  }

  /**
   * Get all pending queue items
   */
  async getPendingItems(): Promise<OfflineQueueItem[]> {
    return indexedDBService.getPendingQueueItems();
  }

  /**
   * Get all queue items
   */
  async getAllItems(): Promise<OfflineQueueItem[]> {
    return indexedDBService.getAllQueueItems();
  }

  /**
   * Get queue statistics
   */
  async getStats(): Promise<{
    total: number;
    pending: number;
    syncing: number;
    completed: number;
    failed: number;
  }> {
    const items = await indexedDBService.getAllQueueItems();
    
    return {
      total: items.length,
      pending: items.filter(i => i.status === 'pending').length,
      syncing: items.filter(i => i.status === 'syncing').length,
      completed: items.filter(i => i.status === 'completed').length,
      failed: items.filter(i => i.status === 'failed').length,
    };
  }

  /**
   * Synchronize all pending items with the server
   */
  async syncAll(): Promise<SyncResult> {
    const pendingItems = await this.getPendingItems();
    
    if (pendingItems.length === 0) {
      return {
        success: true,
        synced: 0,
        failed: 0,
        conflicts: 0,
        errors: [],
      };
    }

    console.log(`[OfflineQueue] Starting sync of ${pendingItems.length} items`);

    const result: SyncResult = {
      success: true,
      synced: 0,
      failed: 0,
      conflicts: 0,
      errors: [],
    };

    // Process items sequentially to avoid conflicts
    for (const item of pendingItems) {
      try {
        await this.syncItem(item);
        result.synced++;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        const isConflict = errorMessage.includes('conflict') || errorMessage.includes('409');
        
        if (isConflict) {
          result.conflicts++;
        } else {
          result.failed++;
        }

        result.errors.push({
          queueItemId: item.id,
          error: errorMessage,
          conflict: isConflict,
        });

        result.success = false;
      }
    }

    console.log(`[OfflineQueue] Sync completed: ${result.synced} synced, ${result.failed} failed, ${result.conflicts} conflicts`);

    return result;
  }

  /**
   * Synchronize a single queue item
   */
  private async syncItem(item: OfflineQueueItem): Promise<void> {
    // Mark as syncing
    item.status = 'syncing';
    item.last_attempt_at = new Date().toISOString();
    await indexedDBService.updateQueueItem(item);

    try {
      // Execute the operation
      await this.executeOperation(item);

      // Mark as completed
      item.status = 'completed';
      await indexedDBService.updateQueueItem(item);

      console.log('[OfflineQueue] Item synced successfully:', item.id);
    } catch (error) {
      // Increment retry count
      item.retry_count++;
      
      if (item.retry_count >= item.max_retries) {
        // Max retries reached, mark as failed
        item.status = 'failed';
        item.error_message = error instanceof Error ? error.message : 'Unknown error';
        await indexedDBService.updateQueueItem(item);
        
        console.error('[OfflineQueue] Item failed after max retries:', item.id);
        throw error;
      } else {
        // Reset to pending for retry
        item.status = 'pending';
        item.error_message = error instanceof Error ? error.message : 'Unknown error';
        await indexedDBService.updateQueueItem(item);
        
        console.log(`[OfflineQueue] Item retry ${item.retry_count}/${item.max_retries}:`, item.id);
        
        // Wait before retry
        await this.delay(this.retryDelayMs * item.retry_count);
        
        // Retry
        await this.syncItem(item);
      }
    }
  }

  /**
   * Execute the actual API operation
   */
  private async executeOperation(item: OfflineQueueItem): Promise<void> {
    const { operation, entity_type, entity_id, data, idempotency_key } = item;

    // Build API endpoint and method based on operation
    let endpoint: string;
    let method: 'POST' | 'PUT' | 'DELETE';
    let body: any;

    switch (operation) {
      case 'create':
        endpoint = this.getEndpoint(entity_type);
        method = 'POST';
        body = { ...data, idempotency_key };
        break;

      case 'update':
        endpoint = `${this.getEndpoint(entity_type)}/${entity_id}`;
        method = 'PUT';
        body = { ...data, idempotency_key };
        break;

      case 'delete':
        endpoint = `${this.getEndpoint(entity_type)}/${entity_id}`;
        method = 'DELETE';
        body = undefined;
        break;

      default:
        throw new Error(`Unknown operation: ${operation}`);
    }

    // Execute API call
    try {
      await apiClient.request(endpoint, {
        method,
        body: body ? JSON.stringify(body) : undefined,
        headers: {
          'Idempotency-Key': idempotency_key,
        },
      });
    } catch (error) {
      // Check if it's a conflict error
      if (error instanceof Error && error.message.includes('409')) {
        throw new Error(`Conflict: Resource conflict detected`);
      }
      
      // Re-throw other errors
      throw error;
    }
  }

  /**
   * Get API endpoint for entity type
   */
  private getEndpoint(entityType: string): string {
    const endpoints: Record<string, string> = {
      'inventory-item': '/api/v1/inventory/items',
      'depot': '/api/v1/depots',
      'sensor': '/api/v1/iot/sensors',
      'shipment': '/api/v1/shipments',
    };

    const endpoint = endpoints[entityType];
    if (!endpoint) {
      throw new Error(`Unknown entity type: ${entityType}`);
    }

    return endpoint;
  }

  /**
   * Remove a queue item
   */
  async removeItem(id: string): Promise<void> {
    await indexedDBService.removeQueueItem(id);
  }

  /**
   * Clear completed items from queue
   */
  async clearCompleted(): Promise<void> {
    await indexedDBService.clearCompletedQueueItems();
  }

  /**
   * Clear all items from queue
   */
  async clearAll(): Promise<void> {
    await indexedDBService.clearQueue();
  }

  /**
   * Retry a failed item
   */
  async retryItem(id: string): Promise<void> {
    const item = await indexedDBService.getQueueItem(id);
    if (!item) {
      throw new Error(`Queue item not found: ${id}`);
    }

    if (item.status !== 'failed') {
      throw new Error(`Item is not in failed state: ${item.status}`);
    }

    // Reset retry count and status
    item.retry_count = 0;
    item.status = 'pending';
    item.error_message = undefined;
    
    await indexedDBService.updateQueueItem(item);

    // Attempt sync
    await this.syncItem(item);
  }

  /**
   * Delay helper
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Singleton instance
export const offlineQueueManager = new OfflineQueueManager();
