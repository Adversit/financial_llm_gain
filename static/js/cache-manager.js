/**
 * 缓存管理模块
 * 用于处理浏览器缓存，确保获取最新数据
 */

const CacheManager = {
    /**
     * 为 URL 添加缓存破坏参数
     * @param {string} url - 原始 URL
     * @returns {string} 添加时间戳后的 URL
     */
    addCacheBuster: function(url) {
        const timestamp = new Date().getTime();
        const separator = url.includes('?') ? '&' : '?';
        return `${url}${separator}_t=${timestamp}`;
    },

    /**
     * 发起不缓存的 fetch 请求
     * @param {string} url - 请求 URL
     * @param {object} options - fetch 选项
     * @returns {Promise} fetch Promise
     */
    fetchNoCache: function(url, options = {}) {
        const urlWithTimestamp = this.addCacheBuster(url);
        
        // 添加缓存控制头
        const headers = {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            ...options.headers
        };
        
        return fetch(urlWithTimestamp, {
            ...options,
            headers
        });
    },

    /**
     * 强制刷新当前页面
     * @param {boolean} clearCache - 是否清除缓存
     */
    reloadPage: function(clearCache = true) {
        if (clearCache) {
            // 清除当前页面的缓存并重新加载
            window.location.reload(true);
        } else {
            window.location.reload();
        }
    },

    /**
     * 清除指定 URL 的缓存
     * @param {string} url - 要清除缓存的 URL
     */
    clearUrlCache: function(url) {
        // 使用 Cache API 清除缓存（如果支持）
        if ('caches' in window) {
            caches.keys().then(function(names) {
                names.forEach(function(name) {
                    caches.open(name).then(function(cache) {
                        cache.delete(url);
                    });
                });
            });
        }
    },

    /**
     * 清除所有缓存
     */
    clearAllCache: function() {
        if ('caches' in window) {
            caches.keys().then(function(names) {
                names.forEach(function(name) {
                    caches.delete(name);
                });
            });
        }
        
        // 清除 localStorage
        if (window.localStorage) {
            localStorage.clear();
        }
        
        // 清除 sessionStorage
        if (window.sessionStorage) {
            sessionStorage.clear();
        }
    },

    /**
     * 获取缓存统计信息
     * @returns {Promise<object>} 缓存统计
     */
    getCacheStats: async function() {
        if (!('caches' in window)) {
            return { supported: false };
        }

        const names = await caches.keys();
        const stats = {
            supported: true,
            cacheCount: names.length,
            caches: []
        };

        for (const name of names) {
            const cache = await caches.open(name);
            const keys = await cache.keys();
            stats.caches.push({
                name: name,
                urlCount: keys.length
            });
        }

        return stats;
    }
};

// 导出到全局
window.CacheManager = CacheManager;
