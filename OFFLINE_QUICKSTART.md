# Offline Support - Quick Start Guide

## Overview

SANGAM now supports offline functionality! Users can continue working even without internet connectivity, with automatic synchronization when they reconnect.

## What Works Offline

### ✅ Available Offline
- View cached inventory items
- View cached depot information
- View cached sensor data
- Queue new operations (create, update, delete)
- View pending operations
- See online/offline status

### ❌ Requires Online Connection
- User authentication
- Real-time data updates
- Audit log viewing
- Report generation
- User management

## Quick Start

### 1. Check Your Status

Look at the bottom-right corner of the screen:
- 🟢 **Green WiFi icon**: You're online
- 🔴 **Red WiFi icon**: You're offline
- 🔢 **Number badge**: Pending operations to sync

### 2. Working Offline

When you go offline:

1. **Orange banner appears** at the top: "You are offline. Changes will be saved locally..."
2. **Continue working normally** - all operations are queued
3. **Status indicator** shows pending operation count
4. **Data is cached** for offline viewing

### 3. Coming Back Online

When you reconnect:

1. **Automatic sync starts** (if enabled)
2. **Status indicator** shows sync progress
3. **Green checkmark** appears when sync completes
4. **Banner disappears** when all operations are synced

### 4. Manual Sync

If auto-sync is disabled or you want to sync manually:

1. Click the **"Sync Now"** button in the status indicator
2. Wait for sync to complete
3. Check the result message

## Using the Offline Queue Viewer

### View Pending Operations

1. Click the status indicator (bottom-right)
2. Click **"View Queue"** (if available)
3. See all pending operations with status

### Retry Failed Operations

1. Find the failed operation in the queue
2. Click **"Retry"** button
3. Operation will be attempted again

### Remove Operations

1. Find the operation in the queue
2. Click **"Remove"** button
3. Confirm removal

### Clear Queue

- **"Clear Completed"**: Remove all completed operations
- **"Clear All"**: Remove all operations (use with caution!)

## Common Scenarios

### Scenario 1: Working in a Warehouse (Poor Connectivity)

1. **Before entering warehouse**: Ensure app is loaded
2. **Inside warehouse**: App works offline
3. **Perform operations**: Scan items, update stock, etc.
4. **Operations are queued**: See pending count increase
5. **Leave warehouse**: Auto-sync when connectivity returns
6. **Verify sync**: Check status indicator shows success

### Scenario 2: Long Offline Period

1. **Go offline**: Status indicator turns red
2. **Work normally**: All operations are queued
3. **Check queue**: See pending operations
4. **Stay offline**: Data is cached locally
5. **Return online**: Auto-sync all queued operations
6. **Resolve conflicts**: If any conflicts occur, resolve them

### Scenario 3: Conflict Resolution

If you see a conflict warning:

1. **Understand the conflict**: Same item modified offline and online
2. **Choose resolution**:
   - **Server-wins**: Use server version (default)
   - **Local-wins**: Use your local version
   - **Manual**: Review and merge manually
3. **Apply resolution**: Click the appropriate button
4. **Verify sync**: Check that data is correct

## Status Indicators

### Online Status

| Icon | Meaning | Action |
|------|---------|--------|
| 🟢 Green WiFi | Online | Normal operation |
| 🔴 Red WiFi | Offline | Changes queued locally |
| 🔄 Spinning | Syncing | Wait for completion |
| ✅ Green Check | Synced | All operations synced |

### Pending Operations

| Number | Meaning | Action |
|--------|---------|--------|
| 0 | All synced | Nothing to do |
| 1-5 | Few pending | Will sync automatically |
| 6-20 | Many pending | Consider manual sync |
| 20+ | Very many | Check queue, may need attention |

### Sync Results

| Message | Meaning | Action |
|---------|---------|--------|
| "Synced X items" | Success | Nothing |
| "Sync failed" | Error | Check error details, retry |
| "X conflicts" | Conflicts | Resolve conflicts |

## Tips for Best Experience

### Before Going Offline

1. ✅ **Sync first**: Ensure all pending operations are synced
2. ✅ **Cache data**: View the data you'll need offline
3. ✅ **Check status**: Verify you're online and synced
4. ✅ **Note pending count**: Know how many operations are queued

### While Offline

1. ✅ **Work normally**: All operations are queued
2. ✅ **Monitor queue**: Keep an eye on pending count
3. ✅ **Avoid large operations**: Queue may get large
4. ✅ **Note conflicts**: Be aware of potential conflicts

### When Returning Online

1. ✅ **Wait for auto-sync**: Let it complete
2. ✅ **Check status**: Verify sync succeeded
3. ✅ **Resolve conflicts**: Handle any conflicts
4. ✅ **Verify data**: Ensure data is correct

## Troubleshooting

### "I'm offline but the app won't load"

**Solution**: 
- The app needs to be loaded at least once while online
- Service Worker caches the app shell on first visit
- Clear browser cache and reload while online

### "My operations aren't syncing"

**Check**:
1. Are you actually online? (Check status indicator)
2. Is auto-sync enabled? (Check settings)
3. Are there errors in the queue? (Check queue viewer)
4. Is the server accessible? (Try manual sync)

### "I have conflicts, what do I do?"

**Steps**:
1. Open the conflict resolution dialog
2. Review the differences between local and server
3. Choose resolution strategy:
   - Server-wins: Use server data
   - Local-wins: Use your data
   - Manual: Merge manually
4. Apply resolution
5. Verify the result

### "The queue is very large"

**Options**:
1. **Wait**: Let auto-sync handle it
2. **Manual sync**: Click "Sync Now"
3. **Clear completed**: Remove completed operations
4. **Review**: Check if all operations are needed

### "I lost my offline data"

**Causes**:
- Cleared browser data
- Uninstalled the app
- Storage quota exceeded
- Browser update cleared cache

**Prevention**:
- Don't clear browser data
- Keep app installed
- Monitor storage usage
- Sync regularly

## Best Practices

### For Regular Users

1. **Sync before going offline**: Ensure clean state
2. **Monitor pending count**: Don't let it get too large
3. **Check sync status**: Verify operations are synced
4. **Resolve conflicts promptly**: Don't let them pile up
5. **Report issues**: Let us know if sync fails

### For Power Users

1. **Use queue viewer**: Monitor and manage operations
2. **Manual sync when needed**: Don't rely only on auto-sync
3. **Clear completed regularly**: Keep queue clean
4. **Review conflicts carefully**: Choose right resolution
5. **Test offline mode**: Ensure it works for your workflow

### For Administrators

1. **Monitor sync metrics**: Track sync success rates
2. **Review conflict patterns**: Identify common issues
3. **Adjust sync intervals**: Optimize for your use case
4. **Train users**: Ensure everyone understands offline mode
5. **Collect feedback**: Improve the offline experience

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Manual sync (when online) |
| `Ctrl+Q` | Open queue viewer |
| `Ctrl+O` | Toggle offline mode (for testing) |

## Mobile Considerations

### On Mobile Devices

1. **Battery impact**: Sync uses battery, monitor usage
2. **Data usage**: Sync uses data, consider Wi-Fi
3. **Storage limits**: Mobile has less storage, monitor usage
4. **Background sync**: May be limited by OS
5. **Push notifications**: Enable for sync updates

### Mobile Best Practices

1. **Sync on Wi-Fi**: Avoid mobile data usage
2. **Charge while syncing**: Prevent battery drain
3. **Clear old data**: Free up storage space
4. **Test offline mode**: Ensure it works on your device
5. **Update regularly**: Get latest offline improvements

## API Reference

### Offline Service

```typescript
// Get status
const status = offlineService.getStatus();

// Manual sync
await offlineService.sync();

// Queue operation
await offlineService.queueOperation({
  operation: 'create',
  entityType: 'inventory-item',
  entityId: 'item-1',
  data: { name: 'New Item' }
});

// Get pending operations
const pending = await offlineService.getPendingOperations();

// Get queue stats
const stats = await offlineService.getQueueStats();
```

### React Hooks

```typescript
// Online status
const isOnline = useOnlineStatus();

// Offline status
const status = useOfflineStatus();

// Sync
const { sync, isSyncing } = useSync();

// Queue management
const { pendingCount, retryOperation } = useOfflineQueue();

// Cache data
const { data, cacheData } = useOfflineCache('inventory-items');
```

## Support

### Documentation
- **Full Guide**: `docs/OFFLINE_SUPPORT.md`
- **Implementation**: `OFFLINE_IMPLEMENTATION.md`
- **API Docs**: `/docs` (when running)

### Getting Help
1. Check this quick start guide
2. Review full documentation
3. Check browser console for errors
4. Contact support team

### Reporting Issues
When reporting offline issues, include:
- Browser and version
- Online/offline status
- Pending operation count
- Error messages
- Steps to reproduce

---

**You're all set!** 🎉

The offline support system is ready to use. Start working offline and enjoy seamless synchronization when you reconnect!
