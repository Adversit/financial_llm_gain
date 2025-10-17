/**
 * 缓存存储模块
 * 提供统一的缓存存储接口，支持多种存储方式
 */

class CacheStorage {
    constructor(config = {}) {
        this.config = config;
        this.storageType = this.detectBestStorage();
    }
    
    /**
     * 检测最佳存储方式
     */
    detectBestStorage() {
        // 优先级: Cache API > IndexedDB > LocalStorage > Memory
        if ('caches' in window) {
            return 'cache-api';
        } else if ('indexedDB' in window) {
            return 'indexeddb';
        } else if ('localStorage' in window) {
            return 'localstorage';
        } else {
            return 'memory';
        }
    }
    
    /**
     * 保存数据到缓存
     */
    async set(key, value, options = {}) {
        const data = {
            value: value,
            timestamp: Date.now(),
            maxAge: options.maxAge || null
        };
        
        switch (this.storageType) {
            case 'cache-api':
                return await this._setCacheAPI(key, data);
            case 'indexeddb':
                return await this._setIndexedDB(key, data);
            case 'localstorage':
                return this._setLocalStorage(key, data);
            case 'memory':
                return this._setMemory(key, data);
        }
    }
    
    /**
     * 从缓存获取数据
     */
    async get(key) {
        let data;
        
        switch (this.storageType) {
            case 'cache-api':
                data = await this._getCacheAPI(key);
                break;
            case 'indexeddb':
                data = await this._getIndexedDB(key);
                break;
            case 'localstorage':
                data = this._getLocalStorage(key);
                break;
            case 'memory':
                data = this._getMemory(key);
                break;
        }
        
        if (!data) return null;
        
        // 检查是否过期
        if (data.maxAge && Date.now() - data.timestamp > data.maxAge) {
            await this.delete(key);
            return null;
        }
        
        return data.value;
    }
    
    /**
     * 删除缓存
     */
    async delete(key) {
        switch (this.storageType) {
            case 'cache-api':
                return await this._deleteCacheAPI(key);
            case 'indexeddb':
                return await this._deleteIndexedDB(key);
            case 'localstorage':
                return this._deleteLocalStorage(key);
            case 'memory':
                return this._deleteMemory(key);
        }
    }
    
    /**
     * 清空所有缓存
     */
    async clear() {
        switch (this.storageType) {
            case 'cache-api':
                return await this._clearCacheAPI();
            case 'indexeddb':
                return await this._clearIndexedDB();
            case 'localstorage':
                return this._clearLocalStorage();
            case 'memory':
                return this._clearMemory();
        }
    }
    
    // ========== Cache API 实现 ==========
    
    async _setCacheAPI(key, data) {
        const cacheName = this.config.cacheName || 'default-cache';
        const cache = await caches.open(cacheName);
        const response = new Response(JSON.stringify(data));
        await cache.put(key, response);
    }
    
    async _getCacheAPI(key) {
        const cacheName = this.config.cacheName || 'default-cache';
        const cache = await caches.open(cacheName);
        const response = await cache.match(key);
        if (!response) return null;
        return await response.json();
    }
    
    async _deleteCacheAPI(key) {
        const cacheName = this.config.cacheName || 'default-cache';
        const cache = await caches.open(cacheName);
        await cache.delete(key);
    }
    
    async _clearCacheAPI() {
        const cacheName = this.config.cacheName || 'default-cache';
        await caches.delete(cacheName);
    }
    
    // ========== IndexedDB 实现 ==========
    
    async _setIndexedDB(key, data) {
        // IndexedDB 实现（简化版）
        console.warn('IndexedDB implementation not yet complete');
    }
    
    async _getIndexedDB(key) {
        console.warn('IndexedDB implementation not yet complete');
        return null;
    }
    
    async _deleteIndexedDB(key) {
        console.warn('IndexedDB implementation not yet complete');
    }
    
    async _clearIndexedDB() {
        console.warn('IndexedDB implementation not yet complete');
    }
    
    // ========== LocalStorage 实现 ==========
    
    _setLocalStorage(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
        } catch (e) {
            console.error('LocalStorage set error:', e);
        }
    }
    
    _getLocalStorage(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.error('LocalStorage get error:', e);
            return null;
        }
    }
    
    _deleteLocalStorage(key) {
        localStorage.removeItem(key);
    }
    
    _clearLocalStorage() {
        localStorage.clear();
    }
    
    // ========== Memory 实现 ==========
    
    _memoryCache = new Map();
    
    _setMemory(key, data) {
        this._memoryCache.set(key, data);
    }
    
    _getMemory(key) {
        return this._memoryCache.get(key) || null;
    }
    
    _deleteMemory(key) {
        this._memoryCache.delete(key);
    }
    
    _clearMemory() {
        this._memoryCache.clear();
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CacheStorage;
}
