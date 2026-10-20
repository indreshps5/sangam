/**
 * Service Worker Registration
 * 
 * Handles service worker registration and updates.
 */

export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  if (!('serviceWorker' in navigator)) {
    console.warn('[SW] Service workers are not supported in this browser');
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/',
    });

    console.log('[SW] Service worker registered:', registration.scope);

    // Check for updates periodically
    setInterval(() => {
      registration.update();
    }, 60 * 60 * 1000); // Check every hour

    // Handle updates
    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing;
      
      if (!newWorker) {
        return;
      }

      console.log('[SW] New service worker found');

      newWorker.addEventListener('statechange', () => {
        if (newWorker.state === 'installed') {
          if (navigator.serviceWorker.controller) {
            // New content available, prompt user to refresh
            console.log('[SW] New content available, please refresh');
            
            // You could show a UI prompt here
            if (confirm('New version available! Reload to update?')) {
              window.location.reload();
            }
          } else {
            // First install, no need to prompt
            console.log('[SW] Content cached for offline use');
          }
        }
      });
    });

    // Handle messages from service worker
    navigator.serviceWorker.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'SYNC_COMPLETE') {
        console.log('[SW] Sync completed:', event.data);
        // Handle sync completion
      }
    });

    return registration;
  } catch (error) {
    console.error('[SW] Service worker registration failed:', error);
    return null;
  }
}

export async function unregisterServiceWorker(): Promise<boolean> {
  if (!('serviceWorker' in navigator)) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    const result = await registration.unregister();
    
    if (result) {
      console.log('[SW] Service worker unregistered');
    }
    
    return result;
  } catch (error) {
    console.error('[SW] Failed to unregister service worker:', error);
    return false;
  }
}

export async function clearServiceWorkerCache(): Promise<void> {
  if (!('caches' in window)) {
    return;
  }

  try {
    const cacheNames = await caches.keys();
    await Promise.all(
      cacheNames.map((cacheName) => {
        console.log('[SW] Deleting cache:', cacheName);
        return caches.delete(cacheName);
      })
    );
    
    console.log('[SW] All caches cleared');
  } catch (error) {
    console.error('[SW] Failed to clear caches:', error);
  }
}

export function isServiceWorkerSupported(): boolean {
  return 'serviceWorker' in navigator;
}

export async function getServiceWorkerStatus(): Promise<{
  registered: boolean;
  active: boolean;
  waiting: boolean;
  installing: boolean;
}> {
  if (!('serviceWorker' in navigator)) {
    return {
      registered: false,
      active: false,
      waiting: false,
      installing: false,
    };
  }

  try {
    const registration = await navigator.serviceWorker.getRegistration();
    
    if (!registration) {
      return {
        registered: false,
        active: false,
        waiting: false,
        installing: false,
      };
    }

    return {
      registered: true,
      active: !!registration.active,
      waiting: !!registration.waiting,
      installing: !!registration.installing,
    };
  } catch (error) {
    console.error('[SW] Failed to get service worker status:', error);
    return {
      registered: false,
      active: false,
      waiting: false,
      installing: false,
    };
  }
}
