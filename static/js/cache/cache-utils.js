/**
 * 缓存工具函数模块
 * 提供各种缓存相关的实用函数
 */

const CacheUtils = {
    /**
     * 生成缓存键
     */
    generateCacheKey(url, params = {}) {
        const urlObj = new URL(url, window.location.origin);
        
        // 添加参数
        Object.keys(params).forEach(key => {
            urlObj.searchParams.set(key, params[key]);
        });
        
        return urlObj.toString();
    },
    
    /**
     * 检查 URL 是否应该被缓存
     */
    shouldCache(url, patterns = []) {
        return patterns.some(pattern => pattern.test(url));
    },
    
    /**
     * 检查 URL 是否不应该被缓存
     */
    shouldNotCache(url, patterns = []) {
        return patterns.some(pattern => pattern.test(url));
    },
    
    /**
     * 添加时间戳参数（缓存破坏）
     */
    addTimestamp(url) {
        const separator = url.includes('?') ? '&' : '?';
        return `${url}${separator}_t=${Date.now()}`;
    },
    
    /**
     * 添加版本参数
     */
    addVersion(url, version) {
        const separator = url.includes('?') ? '&' : '?';
        return `${url}${separator}_v=${version}`;
    },
    
    /**
     * 解析缓存控制头
     */
    parseCacheControl(cacheControl) {
        if (!cacheControl) return {};
        
        const directives = {};
        cacheControl.split(',').forEach(directive => {
            const [key, value] = directive.trim().split('=');
            directives[key] = value ? parseInt(value) : true;
        });
        
        return directives;
    },
    
    /**
     * 计算缓存过期时间
     */
    calculateExpiry(response) {
        // 检查 Cache-Control
        const cacheControl = response.headers.get('Cache-Control');
        if (cacheControl) {
            const directives = this.parseCacheControl(cacheControl);
            if (directives['max-age']) {
                return Date.now() + directives['max-age'] * 1000;
            }
        }
        
        // 检查 Expires
        const expires = response.headers.get('Expires');
        if (expires) {
            return new Date(expires).getTime();
        }
        
        // 默认1小时
        return Date.now() + 3600000;
    },
    
    /**
     * 检查响应是否可缓存
     */
    isCacheable(response) {
        // 检查状态码
        if (response.status !== 200) {
            return false;
        }
        
        // 检查 Cache-Control
        const cacheControl = response.headers.get('Cache-Control');
        if (cacheControl) {
            const directives = this.parseCacheControl(cacheControl);
            if (directives['no-store'] || directives['no-cache']) {
                return false;
            }
        }
        
        return true;
    },
    
    /**
     * 克隆响应并添加自定义头
     */
    async cloneResponseWithHeaders(response, headers = {}) {
        const newHeaders = new Headers(response.headers);
        Object.keys(headers).forEach(key => {
            newHeaders.set(key, headers[key]);
        });
        
        const blob = await response.blob();
        return new Response(blob, {
            status: response.status,
            statusText: response.statusText,
            headers: newHeaders
        });
    },
    
    /**
     * 获取响应的内容类型
     */
    getContentType(response) {
        return response.headers.get('Content-Type') || 'unknown';
    },
    
    /**
     * 检查是否支持 Cache API
     */
    isCacheAPISupported() {
        return 'caches' in window;
    },
    
    /**
     * 检查是否支持 Service Worker
     */
    isServiceWorkerSupported() {
        return 'serviceWorker' in navigator;
    },
    
    /**
     * 检查是否支持 IndexedDB
     */
    isIndexedDBSupported() {
        return 'indexedDB' in window;
    },
    
    /**
     * 获取浏览器支持的存储方式
     */
    getSupportedStorage() {
        const supported = [];
        
        if (this.isCacheAPISupported()) {
            supported.push('Cache API');
        }
        if (this.isServiceWorkerSupported()) {
            supported.push('Service Worker');
        }
        if (this.isIndexedDBSupported()) {
            supported.push('IndexedDB');
        }
        if ('localStorage' in window) {
            supported.push('LocalStorage');
        }
        if ('sessionStorage' in window) {
            supported.push('SessionStorage');
        }
        
        return supported;
    },
    
    /**
     * 估算存储配额
     */
    async getStorageQuota() {
        if (!navigator.storage || !navigator.storage.estimate) {
            return { supported: false };
        }
        
        try {
            const estimate = await navigator.storage.estimate();
            return {
                supported: true,
                usage: estimate.usage,
                quota: estimate.quota,
                usagePercent: ((estimate.usage / estimate.quota) * 100).toFixed(2) + '%',
                available: estimate.quota - estimate.usage
            };
        } catch (error) {
            return { supported: true, error: error.message };
        }
    },
    
    /**
     * 清理过期缓存
     */
    async cleanExpiredCache(cacheName) {
        if (!this.isCacheAPISupported()) {
            return { cleaned: 0 };
        }
        
        try {
            const cache = await caches.open(cacheName);
            const keys = await cache.keys();
            let cleaned = 0;
            
            for (const request of keys) {
                const response = await cache.match(request);
                if (response) {
                    const expiry = response.headers.get('X-Cache-Expiry');
                    if (expiry && Date.now() > parseInt(expiry)) {
                        await cache.delete(request);
                        cleaned++;
                    }
                }
            }
            
            return { cleaned: cleaned };
        } catch (error) {
            return { error: error.message };
        }
    },
    
    /**
     * 预加载资源
     */
    async preloadResources(urls, cacheName = 'preload-cache') {
        if (!this.isCacheAPISupported()) {
            return { success: false, message: 'Cache API not supported' };
        }
        
        try {
            const cache = await caches.open(cacheName);
            const results = await Promise.allSettled(
                urls.map(url => fetch(url).then(response => {
                    if (response.ok) {
                        return cache.put(url, response);
                    }
                }))
            );
            
            const successful = results.filter(r => r.status === 'fulfilled').length;
            const failed = results.filter(r => r.status === 'rejected').length;
            
            return {
                success: true,
                total: urls.length,
                successful: successful,
                failed: failed
            };
        } catch (error) {
            return { success: false, error: error.message };
        }
    },
    
    /**
     * 格式化时间戳
     */
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    },
    
    /**
     * 计算时间差
     */
    timeDiff(timestamp) {
        const diff = Date.now() - timestamp;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `${days}天前`;
        if (hours > 0) return `${hours}小时前`;
        if (minutes > 0) return `${minutes}分钟前`;
        return `${seconds}秒前`;
    }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CacheUtils;
}
