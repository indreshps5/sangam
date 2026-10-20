/**
 * Offline Service
 * 
 * Main entry point for offline functionality.
 * Coordinates IndexedDB, queue manager, and sync service.
 */

import { indexedDBService } from './IndexedDBService';
import { offlineQueueManager, QueueOperationRequest } from './OfflineQueueManager';
import { syncService, SyncResult, ConflictResolutionStrategy } from './SyncService';

export interface OfflineStatus {
  isOnline: boolean;
  isSyncing: boolean;
  pendingOperations: number;
  lastSyncAt: string | null;
}

export interface OfflineConfig {
  enabled: boolean;
  autoSync: boolean;
  syncIntervalMs: number;
  conflictResolution: ConflictResolutionStrategy;
}

class OfflineService {
  private isOnline: boolean = navigator.onLine;
  private isSyncing: boolean = false;
  private syncIntervalId: number | null = null;
  private config: OfflineConfig = {
    enabled: true,
    autoSync: true,
    syncIntervalMs: 300000, // 5 minutes
    conflictResolution: 'server-wins',
  };

  private listeners: Set<(status: OfflineStatus) => void> = new Set();

  /**
   * Initialize offline service
   */
  async init(): Promise<void> {
    console.log('[OfflineService] Initializing');

    // Initialize IndexedDB
    await indexedDBService.init();

    // Set conflict resolution strategy
    syncService.setConflictResolutionStrategy(this.config.conflictResolution);

    // Setup online/offline listeners
    window.addEventListener('online', this.handleOnline.bind(this));
    window.addEventListener('offline', this.handleOffline.bind(this));

    // Start auto-sync if enabled
    if (this.config.autoSync) {
      this.startAutoSync();
    }

    // Initial sync if online
    if (this.isOnline) {
      await this.sync();
    }

    console.log('[OfflineService] Initialized');
  }

  /**
   * Configure offline service
   */
  configure(config: Partial<OfflineConfig>): void {
    this.config = { ...this.config, ...config };
    syncService.setConflictResolutionStrategy(this.config.conflictResolution);

    if (this.config.autoSync && !this.syncIntervalId) {
      this.startAutoSync();
    } else if (!this.config.autoSync && this.syncIntervalId) {
      this.stopAutoSync();
    }

    this.notifyListeners();
  }

  /**
   * Get current offline status
   */
  getStatus(): OfflineStatus {
    return {
      isOnline: this.isOnline,
      isSyncing: this.isSyncing,
      pendingOperations: 0, // Will be updated async
      lastSyncAt: null, // Will be updated async
    };
  }

  /**
   * Get detailed status (async)
   */
  async getDetailedStatus(): Promise<OfflineStatus> {
    const queueStats = await offlineQueueManager.getStats();
    const syncStatus = await syncService.getSyncStatus();

    return {
      isOnline: this.isOnline,
      isSyncing: this.isSyncing,
      pendingOperations: queueStats.pending,
      lastSyncAt: syncStatus.lastSyncAt,
    };
  }

  /**
   * Subscribe to status changes
   */
  subscribe(listener: (status: OfflineStatus) => void): () => void {
    this.listeners.add(listener);
    
    // Return unsubscribe function
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * Notify all listeners of status change
   */
  private notifyListeners(): void {
    const status = this.getStatus();
    this.listeners.forEach(listener => listener(status));
  }

  /**
   * Handle online event
   */
  private async handleOnline(): Promise<void> {
    console.log('[OfflineService] Online');
    this.isOnline = true;
    this.notifyListeners();

    // Auto-sync when coming online
    if (this.config.autoSync) {
      await this.sync();
    }
  }

  /**
   * Handle offline event
   */
  private handleOffline(): void {
    console.log('[OfflineService] Offline');
    this.isOnline = false;
    this.notifyListeners();
  }

  /**
   * Start auto-sync interval
   */
  private startAutoSync(): void {
    if (this.syncIntervalId) {
      return;
    }

    console.log(`[OfflineService] Starting auto-sync every ${this.config.syncIntervalMs}ms`);

    this.syncIntervalId = window.setInterval(async () => {
      if (this.isOnline && !this.isSyncing) {
        await this.sync();
      }
    }, this.config.syncIntervalMs);
  }

  /**
   * Stop auto-sync interval
   */
  private stopAutoSync(): void {
    if (this.syncIntervalId) {
      console.log('[OfflineService] Stopping auto-sync');
      window.clearInterval(this.syncIntervalId);
      this.syncIntervalId = null;
    }
  }

  /**
   * Sync all data with server
   */
  async sync(): Promise<SyncResult> {
    if (!this.isOnline) {
      console.log('[OfflineService] Cannot sync while offline');
      return {
        success: false,
        synced: 0,
        conflicts: [],
        errors: ['Cannot sync while offline'],
      };
    }

    if (this.isSyncing) {
      console.log('[OfflineService] Sync already in progress');
      return {
        success: false,
        synced: 0,
        conflicts: [],
        errors: ['Sync already in progress'],
      };
    }

    this.isSyncing = true;
    this.notifyListeners();

    try {
      console.log('[OfflineService] Starting sync');
      const result = await syncService.syncAll();
      console.log('[OfflineService] Sync completed', result);
      
      this.notifyListeners();
      return result;
    } catch (error) {
      console.error('[OfflineService] Sync failed:', error);
      
      const result: SyncResult = {
        success: false,
        synced: 0,
        conflicts: [],
        errors: [error instanceof Error ? error.message : 'Unknown error'],
      };
      
      this.notifyListeners();
      return result;
    } finally {
      this.isSyncing = false;
      this.notifyListeners();
    }
  }

  /**
   * Queue an operation for later sync
   */
  async queueOperation(request: QueueOperationRequest): Promise<{
    success: boolean;
    queueItemId: string;
    error?: string;
  }> {
    if (!this.config.enabled) {
      return {
        success: false,
        queueItemId: '',
        error: 'Offline mode is disabled',
      };
    }

    return offlineQueueManager.enqueue(request);
  }

  /**
   * Get pending queue items
   */
  async getPendingOperations() {
    return offlineQueueManager.getPendingItems();
  }

  /**
   * Get all queue items
   */
  async getAllOperations() {
    return offlineQueueManager.getAllItems();
  }

  /**
   * Get queue statistics
   */
  async getQueueStats() {
    return offlineQueueManager.getStats();
  }

  /**
   * Retry a failed operation
   */
  async retryOperation(id: string): Promise<void> {
    await offlineQueueManager.retryItem(id);
  }

  /**
   * Remove an operation from queue
   */
  async removeOperation(id: string): Promise<void> {
    await offlineQueueManager.removeItem(id);
  }

  /**
   * Clear completed operations from queue
   */
  async clearCompletedOperations(): Promise<void> {
    await offlineQueueManager.clearCompleted();
  }

  /**
   * Clear all operations from queue
   */
  async clearAllOperations(): Promise<void> {
    await offlineQueueManager.clearAll();
  }

  /**
   * Cache data for offline use
   */
  async cacheData(entityType: string, data: any[]): Promise<void> {
    switch (entityType) {
      case 'inventory-items':
        await indexedDBService.saveInventoryItems(data);
        break;
      case 'depots':
        await indexedDBService.saveDepots(data);
        break;
      case 'sensors':
        await indexedDBService.saveSensors(data);
        break;
      default:
        throw new Error(`Unknown entity type: ${entityType}`);
    }
  }

  /**
   * Get cached data
   */
  async getCachedData(entityType: string): Promise<any[]> {
    switch (entityType) {
      case 'inventory-items':
        return indexedDBService.getAllInventoryItems();
      case 'depots':
        return indexedDBService.getAllDepots();
      case 'sensors':
        return indexedDBService.getAllSensors();
      default:
        throw new Error(`Unknown entity type: ${entityType}`);
    }
  }

  /**
   * Clear all cached data
   */
  async clearCache(): Promise<void> {
    await indexedDBService.clearAll();
  }

  /**
   * Get database statistics
   */
  async getDatabaseStats() {
    return indexedDBService.getDatabaseStats();
  }

  /**
   * Cleanup and shutdown
   */
  async shutdown(): Promise<void> {
    console.log('[OfflineService] Shutting down');

    this.stopAutoSync();
    
    window.removeEventListener('online', this.handleOnline.bind(this));
    window.removeEventListener('offline', this.handleOffline.bind(this));
    
    await indexedDBService.close();
    
    this.listeners.clear();
  }
}

// Singleton instance
export const offlineService = new OfflineService();

// Auto-initialize on import
offlineService.init().catch(error => {
  console.error('[OfflineService] Failed to initialize:', error);
});
