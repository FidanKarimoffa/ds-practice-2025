// frontend/src/sw.js
// Minimal service worker that does nothing
self.addEventListener('install', function(event) {
    console.log('Service Worker installing.');
  });
  self.addEventListener('fetch', function(event) {
    // Optionally you can serve something here or simply pass-through
    event.respondWith(fetch(event.request));
  });
  