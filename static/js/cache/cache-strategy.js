/**
 * 缓存策略模块
 * 实现不同的缓存策略
 */

class CacheStrategy {
    /**
     * 缓存优先策略 (Cache First)
     * 优先从缓存读取，缓存未命中时从网络获取
     */
    static async cacheFirst(request, cacheName, options = {}) {
        const cache = await caches.open(cacheName);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            // 检查是否过期
            const cacheTime = cachedResponse.headers.get('X-Cache-Time');
            const maxAge = options.maxAge || 3600000; // 默认1小时
            
            if (cacheTime && Date.now() - parseInt(cacheTime) < maxAge) {
                return cachedResponse;
            }
        }
        
        // 从网络获取
        try {
            const networkResponse = await fetch(request);
            if (networkResponse.ok) {
                // 克隆响应并添加缓存时间
                const responseToCache = networkResponse.clone();
                const headers = new Headers(responseToCache.headers);
                headers.set('X-Cache-Time', Date.now().toString());
                
                const cachedResponse = new Response(
                    await responseToCache.blob(),
                    {
                        status: responseToCache.status,
                        statusText: responseToCache.statusText,
                        headers: headers
                    }
                );
                
                await cache.put(request, cachedResponse);
            }
            return networkResponse;
        } catch (error) {
            // 网络失败，返回缓存（即使过期）
            if (cachedResponse) {
                return cachedResponse;
            }
            throw error;
        }
    }
    
    /**
     * 网络优先策略 (Network First)
     * 优先从网络获取，网络失败时使用缓存
     */
    static async networkFirst(request, cacheName, options = {}) {
        const cache = await caches.open(cacheName);
        
        try {
            const networkResponse = await fetch(request);
            if (networkResponse.ok) {
                // 更新缓存
                const responseToCache = networkResponse.clone();
                await cache.put(request, responseToCache);
            }
            return networkResponse;
        } catch (error) {
            // 网络失败，使用缓存
            const cachedResponse = await cache.match(request);
            if (cachedResponse) {
                return cachedResponse;
            }
            throw error;
        }
    }
    
    /**
     * 仅缓存策略 (Cache Only)
     * 只从缓存读取，不访问网络
     */
    static async cacheOnly(request, cacheName) {
        const cache = await caches.open(cacheName);
        const cachedResponse = await cache.match(request);
        
        if (!cachedResponse) {
            throw new Error('No cache available');
        }
        
        return cachedResponse;
    }
    
    /**
     * 仅网络策略 (Network Only)
     * 只从网络获取，不使用缓存
     */
    static async networkOnly(request) {
        return await fetch(request);
    }
    
    /**
     * 过期重新验证策略 (Stale While Revalidate)
     * 立即返回缓存，同时在后台更新缓存
     */
    static async staleWhileRevalidate(request, cacheName, options = {}) {
        const cache = await caches.open(cacheName);
        const cachedResponse = await cache.match(request);
        
        // 后台更新缓存
        const fetchPromise = fetch(request).then(networkResponse => {
            if (networkResponse.ok) {
                cache.put(request, networkResponse.clone());
            }
            return networkResponse;
        }).catch(error => {
            console.error('Background fetch failed:', error);
        });
        
        // 立即返回缓存或等待网络响应
        return cachedResponse || fetchPromise;
    }
    
    /**
     * 自定义策略选择器
     * 根据请求类型自动选择合适的策略
     */
    static async autoStrategy(request, config = {}) {
        const url = new URL(request.url);
        const pathname = url.pathname;
        
        // 静态资源：缓存优先
        if (/\.(css|js|png|jpg|jpeg|gif|svg|woff|woff2|ttf)$/.test(pathname)) {
            return this.cacheFirst(request, 'static-cache', {
                maxAge: 30 * 24 * 60 * 60 * 1000 // 30天
            });
        }
        
        // API 请求：网络优先
        if (pathname.startsWith('/api/')) {
            return this.networkFirst(request, 'api-cache', {
                maxAge: 5 * 60 * 1000 // 5分钟
            });
        }
        
        // 报告页面：过期重新验证
        if (pathname.startsWith('/reports/')) {
            return this.staleWhileRevalidate(request, 'reports-cache');
        }
        
        // 默认：网络优先
        return this.networkFirst(request, 'default-cache');
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CacheStrategy;
}
