self.addEventListener('fetch', (event) => {
    console.log('Service Worker fetching:', event.request.url);
    event.respondWith(
        fetch(event.request).catch(() => {
            return new Response('Offline');
        })
    );
});