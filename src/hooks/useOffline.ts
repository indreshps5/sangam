/**
 * React Hooks for Offline Support
 * 
 * Provides hooks for using offline functionality in React components.
 */

import { useState, useEffect, useCallback } from 'react';
import { offlineService, OfflineStatus } from '../services/offline/OfflineService';

/**
 * Hook for tracking online/offline status
 */
export function useOnlineStatus(): boolean {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}

/**
 * Hook for accessing offline service status
 */
export function useOfflineStatus(): OfflineStatus {
  const [status, setStatus] = useState<OfflineStatus>({
    isOnline: navigator.onLine,
    isSyncing: false,
    pendingOperations: 0,
    lastSyncAt: null,
  });

  useEffect(() => {
    // Get initial status
    offlineService.getDetailedStatus().then(setStatus);

    // Subscribe to status changes
    const unsubscribe = offlineService.subscribe(setStatus);

    return unsubscribe;
  }, []);

  return status;
}

/**
 * Hook for syncing data
 */
export function useSync() {
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSyncResult, setLastSyncResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const sync = useCallback(async () => {
    setIsSyncing(true);
    setError(null);

    try {
      const result = await offlineService.sync();
      setLastSyncResult(result);
      
      if (!result.success) {
        setError(result.errors.join(', '));
      }
      
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Sync failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsSyncing(false);
    }
  }, []);

  return {
    sync,
    isSyncing,
    lastSyncResult,
    error,
  };
}

/**
 * Hook for managing offline queue
 */
export function useOfflineQueue() {
  const [pendingCount, setPendingCount] = useState(0);
  const [isSyncing, setIsSyncing] = useState(false);

  const refreshStats = useCallback(async () => {
    const stats = await offlineService.getQueueStats();
    setPendingCount(stats.pending);
    setIsSyncing(stats.syncing > 0);
  }, []);

  useEffect(() => {
    refreshStats();

    // Refresh stats periodically
    const interval = setInterval(refreshStats, 5000);

    return () => clearInterval(interval);
  }, [refreshStats]);

  const retryOperation = useCallback(async (id: string) => {
    await offlineService.retryOperation(id);
    await refreshStats();
  }, [refreshStats]);

  const removeOperation = useCallback(async (id: string) => {
    await offlineService.removeOperation(id);
    await refreshStats();
  }, [refreshStats]);

  const clearCompleted = useCallback(async () => {
    await offlineService.clearCompletedOperations();
    await refreshStats();
  }, [refreshStats]);

  const clearAll = useCallback(async () => {
    await offlineService.clearAllOperations();
    await refreshStats();
  }, [refreshStats]);

  return {
    pendingCount,
    isSyncing,
    retryOperation,
    removeOperation,
    clearCompleted,
    clearAll,
    refreshStats,
  };
}

/**
 * Hook for caching data offline
 */
export function useOfflineCache<T>(entityType: string) {
  const [data, setData] = useState<T[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadCachedData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const cachedData = await offlineService.getCachedData(entityType);
      setData(cachedData as T[]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load cached data';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [entityType]);

  const cacheData = useCallback(async (newData: T[]) => {
    try {
      await offlineService.cacheData(entityType, newData);
      setData(newData);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to cache data';
      setError(errorMessage);
      throw err;
    }
  }, [entityType]);

  const clearCache = useCallback(async () => {
    try {
      await offlineService.clearCache();
      setData([]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to clear cache';
      setError(errorMessage);
      throw err;
    }
  }, []);

  useEffect(() => {
    loadCachedData();
  }, [loadCachedData]);

  return {
    data,
    isLoading,
    error,
    cacheData,
    clearCache,
    refresh: loadCachedData,
  };
}

/**
 * Hook for queueing operations
 */
export function useOfflineQueueOperation() {
  const [isQueuing, setIsQueuing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const queueOperation = useCallback(async (
    operation: 'create' | 'update' | 'delete',
    entityType: string,
    entityId: string,
    data: any
  ) => {
    setIsQueuing(true);
    setError(null);

    try {
      const result = await offlineService.queueOperation({
        operation,
        entityType,
        entityId,
        data,
      });

      if (!result.success) {
        throw new Error(result.error || 'Failed to queue operation');
      }

      return result.queueItemId;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to queue operation';
      setError(errorMessage);
      throw err;
    } finally {
      setIsQueuing(false);
    }
  }, []);

  return {
    queueOperation,
    isQueuing,
    error,
  };
}

/**
 * Hook for database statistics
 */
export function useDatabaseStats() {
  const [stats, setStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const refreshStats = useCallback(async () => {
    setIsLoading(true);

    try {
      const dbStats = await offlineService.getDatabaseStats();
      setStats(dbStats);
    } catch (err) {
      console.error('Failed to load database stats:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshStats();
  }, [refreshStats]);

  return {
    stats,
    isLoading,
    refresh: refreshStats,
  };
}
