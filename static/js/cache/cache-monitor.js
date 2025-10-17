/**
 * 缓存监控模块
 * 监控缓存使用情况和性能
 */

class CacheMonitor {
    constructor() {
        this.stats = {
            hits: 0,
            misses: 0,
            errors: 0,
            totalSize: 0,
            requests: []
        };
        
        this.maxRequestHistory = 100;
    }
    
    /**
     * 记录缓存命中
     */
    recordHit(url, source = 'cache') {
        this.stats.hits++;
        this._recordRequest(url, 'hit', source);
    }
    
    /**
     * 记录缓存未命中
     */
    recordMiss(url) {
        this.stats.misses++;
        this._recordRequest(url, 'miss', 'network');
    }
    
    /**
     * 记录错误
     */
    recordError(url, error) {
        this.stats.errors++;
        this._recordRequest(url, 'error', null, error);
    }
    
    /**
     * 记录请求
     */
    _recordRequest(url, type, source, error = null) {
        const request = {
            url: url,
            type: type,
            source: source,
            timestamp: Date.now(),
            error: error ? error.message : null
        };
        
        this.stats.requests.unshift(request);
        
        // 限制历史记录数量
        if (this.stats.requests.length > this.maxRequestHistory) {
            this.stats.requests.pop();
        }
    }
    
    /**
     * 获取缓存命中率
     */
    getHitRate() {
        const total = this.stats.hits + this.stats.misses;
        if (total === 0) return 0;
        return (this.stats.hits / total * 100).toFixed(2);
    }
    
    /**
     * 获取统计信息
     */
    getStats() {
        return {
            ...this.stats,
            hitRate: this.getHitRate() + '%',
            totalRequests: this.stats.hits + this.stats.misses
        };
    }
    
    /**
     * 获取缓存大小
     */
    async getCacheSize() {
        if (!('caches' in window)) {
            return { supported: false };
        }
        
        try {
            const cacheNames = await caches.keys();
            let totalSize = 0;
            const cacheDetails = [];
            
            for (const cacheName of cacheNames) {
                const cache = await caches.open(cacheName);
                const keys = await cache.keys();
                let cacheSize = 0;
                
                for (const request of keys) {
                    const response = await cache.match(request);
                    if (response) {
                        const blob = await response.blob();
                        cacheSize += blob.size;
                    }
                }
                
                totalSize += cacheSize;
                cacheDetails.push({
                    name: cacheName,
                    size: this._formatBytes(cacheSize),
                    entries: keys.length
                });
            }
            
            this.stats.totalSize = totalSize;
            
            return {
                supported: true,
                totalSize: this._formatBytes(totalSize),
                totalSizeBytes: totalSize,
                caches: cacheDetails
            };
        } catch (error) {
            console.error('Error calculating cache size:', error);
            return { supported: true, error: error.message };
        }
    }
    
    /**
     * 格式化字节大小
     */
    _formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    /**
     * 获取最近的请求
     */
    getRecentRequests(count = 10) {
        return this.stats.requests.slice(0, count);
    }
    
    /**
     * 获取错误请求
     */
    getErrorRequests() {
        return this.stats.requests.filter(req => req.type === 'error');
    }
    
    /**
     * 重置统计
     */
    reset() {
        this.stats = {
            hits: 0,
            misses: 0,
            errors: 0,
            totalSize: 0,
            requests: []
        };
    }
    
    /**
     * 导出统计数据
     */
    exportStats() {
        return JSON.stringify(this.getStats(), null, 2);
    }
    
    /**
     * 生成性能报告
     */
    async generateReport() {
        const stats = this.getStats();
        const cacheSize = await this.getCacheSize();
        const recentRequests = this.getRecentRequests(20);
        const errorRequests = this.getErrorRequests();
        
        return {
            summary: {
                hitRate: stats.hitRate,
                totalRequests: stats.totalRequests,
                hits: stats.hits,
                misses: stats.misses,
                errors: stats.errors
            },
            cacheSize: cacheSize,
            recentRequests: recentRequests,
            errorRequests: errorRequests,
            timestamp: new Date().toISOString()
        };
    }
    
    /**
     * 在控制台显示报告
     */
    async logReport() {
        const report = await this.generateReport();
        
        console.group('📊 Cache Performance Report');
        console.log('Hit Rate:', report.summary.hitRate);
        console.log('Total Requests:', report.summary.totalRequests);
        console.log('Hits:', report.summary.hits);
        console.log('Misses:', report.summary.misses);
        console.log('Errors:', report.summary.errors);
        
        if (report.cacheSize.supported) {
            console.log('Total Cache Size:', report.cacheSize.totalSize);
            console.table(report.cacheSize.caches);
        }
        
        if (report.errorRequests.length > 0) {
            console.warn('Error Requests:', report.errorRequests);
        }
        
        console.groupEnd();
    }
}

// 创建全局实例
const cacheMonitor = new CacheMonitor();

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CacheMonitor;
}
