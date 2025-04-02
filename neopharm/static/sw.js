const CACHE_NAME = 'neopharm-cache-v1';
const OFFLINE_URL = '/offline/';

const ASSETS_TO_CACHE = [
  '/',
  '/static/manifest.json',
  '/static/css/bootstrap.min.css',
  '/static/js/htmx.min.js',
  // Add other static assets
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS_TO_CACHE))
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method === 'GET') {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const clonedResponse = response.clone();
          caches.open(CACHE_NAME)
            .then((cache) => cache.put(event.request, clonedResponse));
          return response;
        })
        .catch(() => caches.match(event.request))
    );
  }
});

// Background sync for offline transactions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-transactions') {
    event.waitUntil(syncTransactions());
  }
});

async function syncTransactions() {
  const db = await openIndexedDB();
  const transactions = await db.getAll('offlineTransactions');
  
  for (const transaction of transactions) {
    try {
      const response = await fetch('/api/sync-transaction/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transaction),
      });
      
      if (response.ok) {
        await db.delete('offlineTransactions', transaction.id);
      }
    } catch (error) {
      console.error('Sync failed:', error);
    }
  }
}