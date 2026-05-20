// Service Worker for Kaizer News push notifications
self.addEventListener('push', function(event) {
  if (!event.data) return;
  const data = event.data.json();
  
  event.waitUntil(
    self.registration.showNotification(data.title || 'Kaizer News', {
      body: data.body || 'New breaking news!',
      icon: '/kaizer-logo.png',
      badge: '/kaizer-logo.png',
      tag: 'kaizer-breaking',
      renotify: true,
      data: { url: data.url || '/' }
    })
  );
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  const url = event.notification.data?.url || '/';
  event.waitUntil(clients.openWindow(url));
});
