/**
 * 缓存配置模块
 * 管理所有缓存相关的配置项
 */

const CacheConfig = {
    // 缓存版本
    version: '1.0.0',
    
    // 缓存名称前缀
    cachePrefix: 'financial-report-',
    
    // 缓存策略
    strategies: {
        // 静态资源缓存策略
        static: {
            cacheName: 'static-cache',
            maxAge: 30 * 24 * 60 * 60 * 1000, // 30天
            maxEntries: 100
        },
        
        // API 数据缓存策略
        api: {
            cacheName: 'api-cache',
            maxAge: 5 * 60 * 1000, // 5分钟
            maxEntries: 50
        },
        
        // 报告缓存策略
        reports: {
            cacheName: 'reports-cache',
            maxAge: 60 * 60 * 1000, // 1小时
            maxEntries: 20
        },
        
        // 图片缓存策略
        images: {
            cacheName: 'images-cache',
            maxAge: 7 * 24 * 60 * 60 * 1000, // 7天
            maxEntries: 200
        }
    },
    
    // 需要缓存的 URL 模式
    cachePatterns: {
        static: [
            /\/static\/css\/.+\.css$/,
            /\/static\/js\/.+\.js$/,
            /\/static\/fonts\/.+$/
        ],
        api: [
            /\/api\/reports$/,
            /\/api\/articles$/,
            /\/api\/sources$/
        ],
        reports: [
            /\/reports\/\d{4}-\d{2}-\d{2}$/
        ],
        images: [
            /\/static\/images\/.+\.(png|jpg|jpeg|gif|svg|webp)$/,
            /\/api\/wordcloud\/.+$/
        ]
    },
    
    // 不缓存的 URL 模式
    noCachePatterns: [
        /\/api\/settings/,
        /\/api\/.*\/test$/,
        /\/api\/.*\/send$/,
        /\/health$/
    ],
    
    // 缓存控制头
    cacheHeaders: {
        noCache: {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        },
        shortCache: {
            'Cache-Control': 'public, max-age=300' // 5分钟
        },
        longCache: {
            'Cache-Control': 'public, max-age=2592000' // 30天
        }
    },
    
    // 调试模式
    debug: false,
    
    // 日志级别: 'none', 'error', 'warn', 'info', 'debug'
    logLevel: 'info'
};

// 导出配置
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CacheConfig;
}
