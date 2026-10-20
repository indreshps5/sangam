# Offline Support for SANGAM

## Overview

SANGAM now supports offline functionality using IndexedDB for local storage and Service Workers for caching. This allows users to continue working with the application even when they lose internet connectivity, with automatic synchronization when connectivity is restored.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Components                          │
│  - OfflineStatusIndicator                                   │
│  - OfflineBanner                                            │
│  - OfflineQueueViewer                                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    React Hooks                               │
│  - useOnlineStatus                                          │
│  - useOfflineStatus                                         │
│  - useSync                                                  │
│  - useOfflineQueue                                          │
│  - useOfflineCache                                          │
│  - useOfflineQueueOperation                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Offline Service Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │OfflineService│  │SyncService   │  │QueueManager  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    IndexedDB Service                         │
│  - inventory-items                                          │
│  - depots                                                   │
│  - sensors                                                  │
│  - offline-queue                                            │
│  - sync-status                                              │
│  - user-preferences                                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Worker                            │
│  - App shell caching                                        │
│  - Static asset caching                                     │
│  - API response caching (read-only)                         │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 1. Application Shell Caching

The Service Worker caches the application shell and static assets for instant loading:

- HTML, CSS, and JavaScript files
- Images and fonts
- Manifest and icons

**Strategy**: Cache-first for static assets, network-first for API calls.

### 2. Offline Data Storage

Selected read-only data is cached in IndexedDB:

- **Inventory Items**: Stock levels, locations, categories
- **Depots**: Warehouse locations and details
- **Sensors**: IoT sensor data and readings

**Note**: Sensitive data (passwords, tokens, personal information) is NEVER cached offline.

### 3. Offline Queue

User edits are queued when offline and synchronized when connectivity returns:

- **Create operations**: New inventory items, depots, etc.
- **Update operations**: Stock adjustments, status changes
- **Delete operations**: Record deletions

**Features**:
- Idempotency keys prevent duplicate operations
- Automatic retry with exponential backoff
- Conflict detection and resolution
- Status tracking (pending, syncing, completed, failed)

### 4. Online/Offline Status

Real-time status indicators show:

- Current connectivity status
- Number of pending operations
- Last sync timestamp
- Sync progress and results

### 5. Automatic Synchronization

When connectivity is restored:

1. Service Worker detects online status
2. Offline service triggers sync
3. Queued operations are sent to server
4. Conflicts are detected and resolved
5. Local cache is updated with server data

### 6. Conflict Resolution

Three conflict resolution strategies are supported:

- **Server-wins** (default): Server data overwrites local changes
- **Local-wins**: Local changes are sent to server
- **Manual**: User must resolve conflicts manually

**Conflict Detection**:
- Compares local modification timestamp with last sync timestamp
- Identifies items modified both locally and on server
- Tracks sync versions for each entity

### 7. Idempotency Protection

All queued operations include idempotency keys to prevent duplicates:

```typescript
{
  operation: 'create',
  entityType: 'inventory-item',
  entityId: 'item-1',
  data: { ... },
  idempotency_key: 'create:inventory-item:item-1:1234567890:abc123'
}
```

**Key Generation**:
- Combines operation type, entity type, entity ID, timestamp, and random string
- Ensures unique key for each operation
- Server validates and rejects duplicates

## Security Considerations

### What is Cached Offline

✅ **Safe to cache**:
- Inventory item metadata (names, SKUs, quantities)
- Depot information (names, locations)
- Sensor metadata (names, types, units)
- Read-only reference data

❌ **Never cached**:
- User passwords
- Authentication tokens
- API keys
- Personal user data
- Sensitive operational data

### Access Control

Offline operations respect user permissions:

- Users can only queue operations they're authorized to perform
- Server validates permissions during sync
- Unauthorized operations are rejected

### Data Sensitivity

The offline service enforces data sensitivity rules:

```typescript
const CACHEABLE_DATA = {
  'inventory-items': true,  // Safe to cache
  'depots': true,           // Safe to cache
  'sensors': true,          // Safe to cache
  'users': false,           // Never cache
  'audit-logs': false,      // Never cache
};
```

## API Endpoints

### Offline-Specific Endpoints

#### Get Sync Status
```http
GET /api/v1/offline/sync-status
```

**Response**:
```json
{
  "last_sync_at": "2024-01-15T10:30:00Z",
  "pending_operations": 5,
  "conflicts": 0
}
```

#### Resolve Conflict
```http
POST /api/v1/offline/conflicts/{conflict_id}/resolve
```

**Request**:
```json
{
  "resolution": "server-wins" | "local-wins" | "merged",
  "merged_data": { ... }  // Only for "merged" resolution
}
```

### Idempotency Support

All mutation endpoints support idempotency keys:

```http
POST /api/v1/inventory/items
Headers:
  Idempotency-Key: unique-key-123
```

**Behavior**:
- First request: Creates resource, returns 201
- Duplicate request with same key: Returns existing resource, returns 200
- Different key: Creates new resource, returns 201

## Usage Examples

### Checking Online Status

```typescript
import { useOnlineStatus } from './hooks/useOffline';

function MyComponent() {
  const isOnline = useOnlineStatus();
  
  return (
    <div>
      {isOnline ? 'Online' : 'Offline'}
    </div>
  );
}
```

### Queueing an Operation

```typescript
import { useOfflineQueueOperation } from './hooks/useOffline';

function InventoryForm() {
  const { queueOperation, isQueuing } = useOfflineQueueOperation();
  
  const handleSubmit = async (data) => {
    try {
      await queueOperation('create', 'inventory-item', 'new-item', data);
      alert('Operation queued for sync');
    } catch (error) {
      alert('Failed to queue operation');
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button disabled={isQueuing}>
        {isQueuing ? 'Queueing...' : 'Submit'}
      </button>
    </form>
  );
}
```

### Manual Sync

```typescript
import { useSync } from './hooks/useOffline';

function SyncButton() {
  const { sync, isSyncing, lastSyncResult } = useSync();
  
  return (
    <button onClick={sync} disabled={isSyncing}>
      {isSyncing ? 'Syncing...' : 'Sync Now'}
      {lastSyncResult && (
        <span>
          Synced {lastSyncResult.synced} items
        </span>
      )}
    </button>
  );
}
```

### Caching Data for Offline Use

```typescript
import { useOfflineCache } from './hooks/useOffline';

function InventoryList() {
  const { data: inventoryItems, cacheData, isLoading } = useOfflineCache('inventory-items');
  
  useEffect(() => {
    // Fetch from server and cache
    fetchInventoryItems().then(items => {
      cacheData(items);
    });
  }, []);
  
  if (isLoading) return <div>Loading...</div>;
  
  return (
    <ul>
      {inventoryItems.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}
```

## Configuration

### Offline Service Configuration

```typescript
import { offlineService } from './services/offline/OfflineService';

offlineService.configure({
  enabled: true,
  autoSync: true,
  syncIntervalMs: 300000, // 5 minutes
  conflictResolution: 'server-wins', // or 'local-wins' or 'manual'
});
```

### Service Worker Configuration

Edit `public/sw.js` to customize caching behavior:

```javascript
// Assets to cache immediately
const PRECACHE_URLS = [
  '/',
  '/index.html',
  '/manifest.json',
];

// API endpoints that can be cached
const CACHEABLE_API_PATTERNS = [
  /\/api\/v1\/inventory\/items$/,
  /\/api\/v1\/depots$/,
];
```

## Testing

### Unit Tests

Run offline service tests:

```bash
npm test src/tests/offline.test.ts
```

**Test Coverage**:
- IndexedDB operations
- Queue management
- Sync service
- Conflict detection
- Idempotency
- Offline scenarios

### Manual Testing

1. **Offline Startup**:
   - Disable network in browser DevTools
   - Reload application
   - Verify cached data loads
   - Verify offline indicator appears

2. **Queue Operations**:
   - Go offline
   - Create/update inventory items
   - Verify operations are queued
   - Check pending count in UI

3. **Reconnection**:
   - Re-enable network
   - Verify automatic sync triggers
   - Check sync status indicator
   - Verify data is synchronized

4. **Conflict Resolution**:
   - Modify same item offline and online
   - Reconnect and sync
   - Verify conflict is detected
   - Test different resolution strategies

5. **Duplicate Prevention**:
   - Queue same operation multiple times
   - Verify only one operation is queued
   - Check idempotency key in queue

## Actions That Require Online Connectivity

The following actions **cannot** be performed offline and will be queued:

### Inventory Management
- ✅ View inventory (cached)
- ❌ Create inventory items (queued)
- ❌ Update stock levels (queued)
- ❌ Delete inventory items (queued)

### Depot Management
- ✅ View depots (cached)
- ❌ Create depots (queued)
- ❌ Update depot details (queued)
- ❌ Delete depots (queued)

### Sensor Monitoring
- ✅ View sensor data (cached)
- ❌ Create sensors (queued)
- ❌ Update sensor configuration (queued)
- ❌ Delete sensors (queued)

### User Management
- ❌ All user management operations (require online)
- ❌ Authentication (require online)
- ❌ Password changes (require online)

### Audit and Reporting
- ❌ View audit logs (require online)
- ❌ Generate reports (require online)
- ❌ Export data (require online)

## Troubleshooting

### Service Worker Not Registering

**Symptoms**: No offline support, no caching

**Solutions**:
1. Check browser console for errors
2. Verify `/sw.js` is accessible
3. Clear browser cache and reload
4. Check service worker scope matches app scope

### IndexedDB Not Working

**Symptoms**: Data not persisting, queue not working

**Solutions**:
1. Check browser supports IndexedDB
2. Verify database initialization in console
3. Check for quota exceeded errors
4. Clear IndexedDB and reinitialize

### Sync Not Triggering

**Symptoms**: Operations stay in queue, no sync

**Solutions**:
1. Check network connectivity
2. Verify auto-sync is enabled
3. Check console for sync errors
4. Manually trigger sync via UI

### Conflicts Not Detected

**Symptoms**: Data overwrites without warning

**Solutions**:
1. Verify sync status is tracked
2. Check conflict resolution strategy
3. Review sync timestamps
4. Enable debug logging

### Duplicate Operations

**Symptoms**: Same operation queued multiple times

**Solutions**:
1. Verify idempotency keys are unique
2. Check queue before adding
3. Review operation generation logic
4. Enable duplicate detection logging

## Performance Considerations

### Storage Limits

IndexedDB storage limits vary by browser:

- **Chrome**: 60% of available disk space
- **Firefox**: 50% of available disk space
- **Safari**: 1GB (approximate)

**Recommendations**:
- Monitor storage usage
- Implement data cleanup policies
- Cache only necessary data
- Clear old data regularly

### Sync Performance

Large queues can impact sync performance:

**Optimizations**:
- Batch operations when possible
- Prioritize critical operations
- Implement progressive sync
- Show sync progress to users

### Cache Size

Service Worker cache can grow large:

**Optimizations**:
- Cache only essential assets
- Implement cache size limits
- Clean up old cache versions
- Use cache-busting for updates

## Best Practices

### For Developers

1. **Always check online status** before making API calls
2. **Queue operations** when offline instead of failing
3. **Provide feedback** to users about offline status
4. **Test offline scenarios** thoroughly
5. **Handle conflicts** gracefully with user-friendly UI
6. **Monitor sync status** and show progress
7. **Clear old data** to prevent storage bloat
8. **Validate data** before queueing operations

### For Users

1. **Check sync status** before closing the app
2. **Wait for sync** when possible before going offline
3. **Review pending operations** periodically
4. **Resolve conflicts** promptly when they occur
5. **Report issues** if sync fails repeatedly

## Future Enhancements

### Planned Features

1. **Background Sync API**: More reliable background synchronization
2. **Push Notifications**: Notify users of sync status
3. **Conflict Resolution UI**: Interactive conflict resolution
4. **Selective Sync**: Choose which data to sync
5. **Bandwidth Awareness**: Adjust sync based on connection quality
6. **Collaborative Editing**: Real-time collaboration with conflict resolution
7. **Offline Analytics**: Track offline usage patterns
8. **Data Compression**: Reduce storage and bandwidth usage

### Integration Opportunities

1. **Web Push API**: Push notifications for sync events
2. **Background Fetch API**: Large file downloads
3. **Periodic Background Sync**: Regular background synchronization
4. **Storage API**: Better storage management
5. **Network Information API**: Adapt to connection quality

## Support

For issues and questions:
- Check browser console for errors
- Review this documentation
- Check application logs
- Contact development team

## References

- [MDN: IndexedDB](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
- [MDN: Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web Workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API)
- [Offline Web Applications](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Offline)

---

**Status**: ✅ Implemented and Production-Ready
**Version**: 1.0.0
**Last Updated**: 2024-01-15
