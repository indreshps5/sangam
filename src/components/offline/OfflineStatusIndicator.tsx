/**
 * Offline Status Indicator Component
 * 
 * Displays online/offline status and pending sync operations.
 */

import React, { useState, useEffect } from 'react';
import { useOfflineStatus, useSync, useOfflineQueue } from '../../hooks/useOffline';
import { offlineService } from '../../services/offline/OfflineService';
import { Wifi, WifiOff, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';

export function OfflineStatusIndicator() {
  const status = useOfflineStatus();
  const { sync, isSyncing, lastSyncResult, error: syncError } = useSync();
  const { pendingCount, refreshStats } = useOfflineQueue();

  const handleSync = async () => {
    await sync();
    await refreshStats();
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-3 min-w-[200px]">
        {/* Online/Offline Status */}
        <div className="flex items-center gap-2 mb-2">
          {status.isOnline ? (
            <>
              <Wifi className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium text-green-600">Online</span>
            </>
          ) : (
            <>
              <WifiOff className="w-5 h-5 text-red-600" />
              <span className="text-sm font-medium text-red-600">Offline</span>
            </>
          )}
        </div>

        {/* Pending Operations */}
        {pendingCount > 0 && (
          <div className="flex items-center gap-2 mb-2 text-sm text-orange-600">
            <AlertCircle className="w-4 h-4" />
            <span>{pendingCount} pending operation{pendingCount !== 1 ? 's' : ''}</span>
          </div>
        )}

        {/* Sync Button */}
        {status.isOnline && (
          <button
            onClick={handleSync}
            disabled={isSyncing}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          >
            <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
            {isSyncing ? 'Syncing...' : 'Sync Now'}
          </button>
        )}

        {/* Last Sync Result */}
        {lastSyncResult && (
          <div className="mt-2 pt-2 border-t border-gray-200">
            {lastSyncResult.success ? (
              <div className="flex items-center gap-2 text-sm text-green-600">
                <CheckCircle className="w-4 h-4" />
                <span>Synced {lastSyncResult.synced} items</span>
              </div>
            ) : (
              <div className="text-sm text-red-600">
                <div className="flex items-center gap-2 mb-1">
                  <AlertCircle className="w-4 h-4" />
                  <span>Sync failed</span>
                </div>
                {lastSyncResult.errors.length > 0 && (
                  <div className="text-xs text-gray-600 ml-6">
                    {lastSyncResult.errors.slice(0, 2).join(', ')}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Sync Error */}
        {syncError && !lastSyncResult && (
          <div className="mt-2 pt-2 border-t border-gray-200">
            <div className="text-sm text-red-600">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                <span>{syncError}</span>
              </div>
            </div>
          </div>
        )}

        {/* Last Sync Time */}
        {status.lastSyncAt && (
          <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500">
            Last sync: {new Date(status.lastSyncAt).toLocaleTimeString()}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Offline Banner Component
 * 
 * Displays a banner when offline or when there are pending operations.
 */
export function OfflineBanner() {
  const status = useOfflineStatus();
  const { pendingCount } = useOfflineQueue();

  if (status.isOnline && pendingCount === 0) {
    return null;
  }

  return (
    <div className={`w-full px-4 py-2 text-sm text-white ${
      status.isOnline ? 'bg-orange-600' : 'bg-red-600'
    }`}>
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-2">
          {status.isOnline ? (
            <>
              <AlertCircle className="w-4 h-4" />
              <span>
                You have {pendingCount} pending operation{pendingCount !== 1 ? 's' : ''} that will sync when possible
              </span>
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4" />
              <span>You are offline. Changes will be saved locally and synced when you reconnect.</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Offline Queue Viewer Component
 * 
 * Displays the offline queue with options to retry or remove operations.
 */
export function OfflineQueueViewer() {
  const { pendingCount, retryOperation, removeOperation, clearCompleted, clearAll } = useOfflineQueue();
  const [operations, setOperations] = useState<Array<{
    id: string;
    operation: string;
    entity_type: string;
    entity_id: string;
    status: string;
    created_at: string;
    error_message?: string;
  }>>([]);
  const [isLoading, setIsLoading] = useState(false);

  const loadOperations = async () => {
    setIsLoading(true);
    try {
      const ops = await offlineService.getAllOperations();
      setOperations(ops);
    } catch (err) {
      console.error('Failed to load operations:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadOperations();
  }, []);

  const handleRetry = async (id: string) => {
    await retryOperation(id);
    await loadOperations();
  };

  const handleRemove = async (id: string) => {
    if (confirm('Are you sure you want to remove this operation?')) {
      await removeOperation(id);
      await loadOperations();
    }
  };

  const handleClearCompleted = async () => {
    await clearCompleted();
    await loadOperations();
  };

  const handleClearAll = async () => {
    if (confirm('Are you sure you want to clear all operations? This cannot be undone.')) {
      await clearAll();
      await loadOperations();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Offline Queue ({pendingCount} pending)
        </h3>
        <div className="flex gap-2">
          <button
            onClick={handleClearCompleted}
            className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900"
          >
            Clear Completed
          </button>
          <button
            onClick={handleClearAll}
            className="px-3 py-1 text-sm text-red-600 hover:text-red-900"
          >
            Clear All
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-8">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400" />
        </div>
      ) : operations.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No operations in queue
        </div>
      ) : (
        <div className="space-y-2 max-h-[400px] overflow-y-auto">
          {operations.map((op) => (
            <div
              key={op.id}
              className="border border-gray-200 rounded p-3"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <div className="font-medium text-sm text-gray-900">
                    {op.operation.toUpperCase()} {op.entity_type}
                  </div>
                  <div className="text-xs text-gray-500">
                    ID: {op.entity_id}
                  </div>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  op.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  op.status === 'syncing' ? 'bg-blue-100 text-blue-800' :
                  op.status === 'completed' ? 'bg-green-100 text-green-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {op.status}
                </span>
              </div>

              <div className="text-xs text-gray-600 mb-2">
                Created: {new Date(op.created_at).toLocaleString()}
              </div>

              {op.error_message && (
                <div className="text-xs text-red-600 mb-2">
                  Error: {op.error_message}
                </div>
              )}

              <div className="flex gap-2">
                {op.status === 'failed' && (
                  <button
                    onClick={() => handleRetry(op.id)}
                    className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Retry
                  </button>
                )}
                <button
                  onClick={() => handleRemove(op.id)}
                  className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
