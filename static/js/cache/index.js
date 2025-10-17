/**
 * 缓存管理系统主入口
 * 整合所有缓存模块，提供统一的接口
 */

// 导入所有模块（如果使用模块系统）
// import CacheConfig from './cache-config.js';
// import CacheStorage from './cache-storage.js';
// import CacheStrategy from './cache-strategy.js';
// import CacheMonitor from './cache-monitor.js';
// import CacheUtils from './cache-utils.js';

/**
 * 缓存管理器主类
 */
class CacheManagerCore {
    constructor(config = {}) {
        // 合并配置
        this.config = {
            ...CacheConfig,
            ...config
        };
        
        // 初始化存储
        this.storage = new CacheStorage(this.config);
        
        // 初始化监控
        this.monitor = new CacheMonitor();
        
        // 工具函数
        this.utils = CacheUtils;
        
        // 策略
        this.strategy = CacheStrategy;
        
        // 初始化
        this._init();
    }
    
    /**
     * 初始化
     */
    _init() {
        if (this.config.debug) {
            console.log('🚀 Cache Manager initialized');
            console.log('Config:', this.config);
            console.log('Supported storage:', this.utils.getSupportedStorage());
        }
        
        // 清理过期缓存
        this._cleanExpiredCaches();
    }
    
    /**
     * 清理过期缓存
     */
    async _cleanExpiredCaches() {
        if (!this.utils.isCacheAPISupported()) return;
        
        try {
            const cacheNames = await caches.keys();
            for (const cacheName of cacheNames) {
                await this.utils.cleanExpiredCache(cacheName);
            }
        } catch (error) {
            console.error('Error cleaning expired caches:', error);
        }
    }
    
    /**
     * 发起请求（带缓存）
     */
    async fetch(url, options = {}) {
        const request = new Request(url, options);
        const strategy = options.strategy || 'auto';
        
        try {
            let response;
            
            // 根据策略获取响应
            switch (strategy) {
                case 'cache-first':
                    response = await this.strategy.cacheFirst(
                        request,
                        options.cacheName || 'default-cache',
                        options
                    );
                    break;
                case 'network-first':
                    response = await this.strategy.networkFirst(
                        request,
                        options.cacheName || 'default-cache',
                        options
                    );
                    break;
                case 'cache-only':
                    response = await this.strategy.cacheOnly(
                        request,
                        options.cacheName || 'default-cache'
                    );
                    break;
                case 'network-only':
                    response = await this.strategy.networkOnly(request);
                    break;
                case 'stale-while-revalidate':
                    response = await this.strategy.staleWhileRevalidate(
                        request,
                        options.cacheName || 'default-cache',
                        options
                    );
                    break;
                case 'auto':
                default:
                    response = await this.strategy.autoStrategy(request, this.config);
                    break;
            }
            
            // 记录命中
            const fromCache = response.headers.get('X-Cache-Time') !== null;
            if (fromCache) {
                this.monitor.recordHit(url, 'cache');
            } else {
                this.monitor.recordMiss(url);
            }
            
            return response;
        } catch (error) {
            this.monitor.recordError(url, error);
            throw error;
        }
    }
    
    /**
     * 无缓存请求
     */
    async fetchNoCache(url, options = {}) {
        const headers = {
            ...this.config.cacheHeaders.noCache,
            ...options.headers
        };
        
        const urlWithTimestamp = this.utils.addTimestamp(url);
        
        return fetch(urlWithTimestamp, {
            ...options,
            headers: headers
        });
    }
    
    /**
     * 保存到缓存
     */
    async set(key, value, options = {}) {
        return await this.storage.set(key, value, options);
    }
    
    /**
     * 从缓存获取
     */
    async get(key) {
        return await this.storage.get(key);
    }
    
    /**
     * 删除缓存
     */
    async delete(key) {
        return await this.storage.delete(key);
    }
    
    /**
     * 清空所有缓存
     */
    async clear() {
        if (this.utils.isCacheAPISupported()) {
            const cacheNames = await caches.keys();
            await Promise.all(cacheNames.map(name => caches.delete(name)));
        }
        
        if ('localStorage' in window) {
            localStorage.clear();
        }
        
        if ('sessionStorage' in window) {
            sessionStorage.clear();
        }
        
        this.monitor.reset();
    }
    
    /**
     * 清除指定 URL 的缓存
     */
    async clearUrl(url) {
        if (!this.utils.isCacheAPISupported()) return;
        
        const cacheNames = await caches.keys();
        for (const cacheName of cacheNames) {
            const cache = await caches.open(cacheName);
            await cache.delete(url);
        }
    }
    
    /**
     * 预加载资源
     */
    async preload(urls) {
        return await this.utils.preloadResources(urls);
    }
    
    /**
     * 获取统计信息
     */
    getStats() {
        return this.monitor.getStats();
    }
    
    /**
     * 获取缓存大小
     */
    async getCacheSize() {
        return await this.monitor.getCacheSize();
    }
    
    /**
     * 获取存储配额
     */
    async getStorageQuota() {
        return await this.utils.getStorageQuota();
    }
    
    /**
     * 生成性能报告
     */
    async generateReport() {
        return await this.monitor.generateReport();
    }
    
    /**
     * 在控制台显示报告
     */
    async logReport() {
        await this.monitor.logReport();
    }
    
    /**
     * 重新加载页面
     */
    reloadPage(clearCache = false) {
        if (clearCache) {
            // 强制刷新（清除缓存）
            window.location.reload(true);
        } else {
            // 普通刷新
            window.location.reload();
        }
    }
}

// 创建全局实例
const cacheManager = new CacheManagerCore();

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CacheManagerCore,
        CacheConfig,
        CacheStorage,
        CacheStrategy,
        CacheMonitor,
        CacheUtils,
        cacheManager
    };
}

// 全局访问
if (typeof window !== 'undefined') {
    window.CacheManagerCore = CacheManagerCore;
    window.cacheManager = cacheManager;
}
