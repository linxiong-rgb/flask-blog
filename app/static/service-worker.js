// Service Worker for Push Notifications

const CACHE_NAME = 'blog-cache-v1';

self.addEventListener('install', (event) => {
    console.log('Service Worker 安装成功');
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll([
                '/',
                '/static/css/style.css',
                '/static/vendor/bootstrap/bootstrap.min.css',
                '/static/vendor/bootstrap/bootstrap.bundle.min.js'
            ]);
        })
    );
});

self.addEventListener('activate', (event) => {
    console.log('Service Worker 激活成功');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});

// 处理推送通知
self.addEventListener('push', (event) => {
    const options = {
        body: event.data ? event.data.text() : '您有新消息',
        icon: '/static/img/og-image.png',
        badge: '/static/img/og-image.png',
        vibrate: [200, 100, 200],
        tag: 'blog-notification',
        requireInteraction: false,
        data: {
            url: '/'
        }
    };

    if (event.data) {
        try {
            const data = event.data.json();
            options.body = data.body || options.body;
            options.title = data.title || '博客通知';
            options.data.url = data.url || '/';
        } catch (e) {
            options.body = event.data.text();
        }
    }

    event.waitUntil(
        self.registration.showNotification(options.title || '博客通知', options)
    );
});

// 处理通知点击
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    event.waitUntil(
        clients.openWindow(event.notification.data.url || '/')
    );
});
