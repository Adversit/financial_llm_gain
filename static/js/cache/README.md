# 浏览器缓存管理系统

完整的前端缓存管理解决方案，提供多种缓存策略、监控和工具函数。

## 📁 文件结构

```
static/js/cache/
├── index.js              # 主入口文件，整合所有模块
├── cache-config.js       # 缓存配置
├── cache-storage.js      # 缓存存储接口
├── cache-strategy.js     # 缓存策略实现
├── cache-monitor.js      # 缓存监控和统计
├── cache-utils.js        # 工具函数
└── README.md            # 本文档
```

## 🚀 快速开始

### 1. 引入文件

在 HTML 中按顺序引入：

```html
<!-- 配置 -->
<script src="/static/js/cache/cache-config.js"></script>
<!-- 工具函数 -->
<script src="/static/js/cache/cache-utils.js"></script>
<!-- 存储 -->
<script src="/static/js/cache/cache-storage.js"></script>
<!-- 策略 -->
<script src="/static/js/cache/cache-strategy.js"></script>
<!-- 监控 -->
<script src="/static/js/cache/cache-monitor.js"></script>
<!-- 主入口 -->
<script src="/static/js/cache/index.js"></script>
```

### 2. 基本使用

```javascript
// 使用全局实例
const cache = window.cacheManager;

// 发起带缓存的请求
const response = await cache.fetch('/api/reports');
const data = await response.json();

// 无缓存请求
const freshResponse = await cache.fetchNoCache('/api/reports');

// 清除缓存
await cache.clearUrl('/api/reports');

// 查看统计
const stats = cache.getStats();
console.log('缓存命中率:', stats.hitRate);
```

## 📚 模块说明

### 1. cache-config.js - 配置模块

定义所有缓存相关的配置项。

**主要配置**:
- `version`: 缓存版本
- `strategies`: 不同类型资源的缓存策略
- `cachePatterns`: 需要缓存的 URL 模式
- `noCachePatterns`: 不缓存的 URL 模式
- `cacheHeaders`: 缓存控制头

**示例**:
```javascript
// 修改配置
CacheConfig.strategies.api.maxAge = 10 * 60 * 1000; // 10分钟
CacheConfig.debug = true; // 开启调试模式
```

### 2. cache-storage.js - 存储模块

提供统一的缓存存储接口，支持多种存储方式。

**支持的存储方式**:
- Cache API (优先)
- IndexedDB
- LocalStorage
- Memory (内存)

**API**:
```javascript
const storage = new CacheStorage({ cacheName: 'my-cache' });

// 保存
await storage.set('key', { data: 'value' }, { maxAge: 3600000 });

// 获取
const value = await storage.get('key');

// 删除
await storage.delete('key');

// 清空
await storage.clear();
```

### 3. cache-strategy.js - 策略模块

实现多种缓存策略。

**可用策略**:

1. **Cache First** (缓存优先)
   ```javascript
   const response = await CacheStrategy.cacheFirst(
       request,
       'my-cache',
       { maxAge: 3600000 }
   );
   ```

2. **Network First** (网络优先)
   ```javascript
   const response = await CacheStrategy.networkFirst(
       request,
       'my-cache'
   );
   ```

3. **Cache Only** (仅缓存)
   ```javascript
   const response = await CacheStrategy.cacheOnly(
       request,
       'my-cache'
   );
   ```

4. **Network Only** (仅网络)
   ```javascript
   const response = await CacheStrategy.networkOnly(request);
   ```

5. **Stale While Revalidate** (过期重新验证)
   ```javascript
   const response = await CacheStrategy.staleWhileRevalidate(
       request,
       'my-cache'
   );
   ```

6. **Auto Strategy** (自动选择)
   ```javascript
   const response = await CacheStrategy.autoStrategy(request);
   ```

### 4. cache-monitor.js - 监控模块

监控缓存使用情况和性能。

**功能**:
- 记录缓存命中/未命中
- 统计缓存大小
- 计算命中率
- 生成性能报告

**API**:
```javascript
const monitor = new CacheMonitor();

// 记录命中
monitor.recordHit('/api/reports', 'cache');

// 记录未命中
monitor.recordMiss('/api/reports');

// 获取统计
const stats = monitor.getStats();
console.log('命中率:', stats.hitRate);

// 获取缓存大小
const size = await monitor.getCacheSize();
console.log('总大小:', size.totalSize);

// 生成报告
const report = await monitor.generateReport();

// 在控制台显示报告
await monitor.logReport();
```

### 5. cache-utils.js - 工具模块

提供各种缓存相关的实用函数。

**常用函数**:

```javascript
// 添加时间戳（缓存破坏）
const url = CacheUtils.addTimestamp('/api/reports');
// 结果: /api/reports?_t=1697520000000

// 检查是否应该缓存
const shouldCache = CacheUtils.shouldCache(
    '/static/css/style.css',
    CacheConfig.cachePatterns.static
);

// 检查浏览器支持
const supported = CacheUtils.getSupportedStorage();
console.log('支持的存储:', supported);

// 获取存储配额
const quota = await CacheUtils.getStorageQuota();
console.log('已使用:', quota.usagePercent);

// 清理过期缓存
const result = await CacheUtils.cleanExpiredCache('my-cache');
console.log('清理了', result.cleaned, '个过期项');

// 预加载资源
const result = await CacheUtils.preloadResources([
    '/static/css/style.css',
    '/static/js/main.js'
]);
console.log('预加载成功:', result.successful);
```

### 6. index.js - 主入口

整合所有模块，提供统一的接口。

**全局实例**:
```javascript
// 使用全局实例
const cache = window.cacheManager;
```

**完整 API**:
```javascript
// 发起请求（自动选择策略）
const response = await cache.fetch('/api/reports');

// 指定策略
const response = await cache.fetch('/api/reports', {
    strategy: 'cache-first',
    cacheName: 'api-cache',
    maxAge: 300000
});

// 无缓存请求
const response = await cache.fetchNoCache('/api/reports');

// 保存到缓存
await cache.set('myKey', { data: 'value' }, { maxAge: 3600000 });

// 从缓存获取
const value = await cache.get('myKey');

// 删除缓存
await cache.delete('myKey');

// 清空所有缓存
await cache.clear();

// 清除指定 URL
await cache.clearUrl('/api/reports');

// 预加载资源
await cache.preload(['/static/css/style.css']);

// 获取统计
const stats = cache.getStats();

// 获取缓存大小
const size = await cache.getCacheSize();

// 获取存储配额
const quota = await cache.getStorageQuota();

// 生成报告
const report = await cache.generateReport();

// 显示报告
await cache.logReport();

// 重新加载页面
cache.reloadPage(true); // 清除缓存并刷新
```

## 🎯 使用场景

### 场景 1: 报告详情页面

```javascript
// 加载报告（使用缓存）
async function loadReport(date) {
    try {
        const response = await cacheManager.fetch(`/api/reports/${date}`, {
            strategy: 'cache-first',
            maxAge: 3600000 // 1小时
        });
        const report = await response.json();
        displayReport(report);
    } catch (error) {
        console.error('加载失败:', error);
    }
}

// 刷新报告（清除缓存）
async function refreshReport(date) {
    await cacheManager.clearUrl(`/api/reports/${date}`);
    await loadReport(date);
}
```

### 场景 2: 文章列表

```javascript
// 加载文章列表
async function loadArticles(date) {
    const response = await cacheManager.fetch(`/api/articles?date=${date}`, {
        strategy: 'network-first', // 优先获取最新数据
        maxAge: 300000 // 5分钟
    });
    const articles = await response.json();
    return articles;
}
```

### 场景 3: 静态资源预加载

```javascript
// 预加载关键资源
async function preloadCriticalResources() {
    await cacheManager.preload([
        '/static/css/style.css',
        '/static/js/main.js',
        '/static/images/logo.png'
    ]);
}

// 在页面加载时执行
document.addEventListener('DOMContentLoaded', preloadCriticalResources);
```

### 场景 4: 性能监控

```javascript
// 定期检查缓存性能
setInterval(async () => {
    const stats = cacheManager.getStats();
    
    // 如果命中率低于 50%，记录警告
    if (parseFloat(stats.hitRate) < 50) {
        console.warn('缓存命中率较低:', stats.hitRate);
    }
    
    // 检查存储空间
    const quota = await cacheManager.getStorageQuota();
    if (parseFloat(quota.usagePercent) > 80) {
        console.warn('存储空间使用率过高:', quota.usagePercent);
        // 清理过期缓存
        await cacheManager.clear();
    }
}, 60000); // 每分钟检查一次
```

## 🔧 高级配置

### 自定义缓存策略

```javascript
// 创建自定义实例
const customCache = new CacheManagerCore({
    version: '2.0.0',
    strategies: {
        api: {
            cacheName: 'custom-api-cache',
            maxAge: 10 * 60 * 1000, // 10分钟
            maxEntries: 100
        }
    },
    debug: true
});

// 使用自定义实例
const response = await customCache.fetch('/api/custom');
```

### 扩展缓存策略

```javascript
// 添加自定义策略
CacheStrategy.customStrategy = async function(request, cacheName, options) {
    // 自定义逻辑
    const cache = await caches.open(cacheName);
    
    // 先尝试缓存
    let response = await cache.match(request);
    
    // 如果缓存不存在或已过期，从网络获取
    if (!response || isExpired(response)) {
        response = await fetch(request);
        if (response.ok) {
            await cache.put(request, response.clone());
        }
    }
    
    return response;
};

// 使用自定义策略
const response = await cacheManager.fetch('/api/data', {
    strategy: 'custom'
});
```

## 📊 性能优化建议

1. **合理设置缓存时间**
   - 静态资源: 30天
   - API 数据: 5-10分钟
   - 报告: 1小时
   - 图片: 7天

2. **使用合适的缓存策略**
   - 静态资源: Cache First
   - API 数据: Network First
   - 实时数据: Network Only
   - 报告: Stale While Revalidate

3. **定期清理过期缓存**
   ```javascript
   // 每天清理一次
   setInterval(async () => {
       const cacheNames = await caches.keys();
       for (const name of cacheNames) {
           await CacheUtils.cleanExpiredCache(name);
       }
   }, 24 * 60 * 60 * 1000);
   ```

4. **监控缓存性能**
   ```javascript
   // 定期生成报告
   setInterval(async () => {
       await cacheManager.logReport();
   }, 3600000); // 每小时
   ```

## 🐛 调试

### 开启调试模式

```javascript
CacheConfig.debug = true;
CacheConfig.logLevel = 'debug';
```

### 查看缓存内容

```javascript
// 在控制台查看所有缓存
const cacheNames = await caches.keys();
for (const name of cacheNames) {
    const cache = await caches.open(name);
    const keys = await cache.keys();
    console.log(`Cache: ${name}`, keys);
}
```

### 查看性能报告

```javascript
// 生成并显示详细报告
await cacheManager.logReport();
```

## 🔒 安全注意事项

1. **不要缓存敏感数据**
   - 用户凭证
   - 个人信息
   - 支付信息

2. **使用 HTTPS**
   - Cache API 仅在 HTTPS 下可用

3. **设置合理的缓存时间**
   - 避免缓存过期数据
   - 定期清理缓存

4. **验证缓存数据**
   - 检查数据完整性
   - 处理缓存失效情况

## 📝 浏览器兼容性

| 功能 | Chrome | Firefox | Safari | Edge |
|------|--------|---------|--------|------|
| Cache API | ✅ 40+ | ✅ 41+ | ✅ 11.1+ | ✅ 17+ |
| Service Worker | ✅ 40+ | ✅ 44+ | ✅ 11.1+ | ✅ 17+ |
| IndexedDB | ✅ 24+ | ✅ 16+ | ✅ 10+ | ✅ 12+ |
| LocalStorage | ✅ 4+ | ✅ 3.5+ | ✅ 4+ | ✅ 8+ |

## 📖 参考资源

- [MDN - Cache API](https://developer.mozilla.org/en-US/docs/Web/API/Cache)
- [MDN - Service Worker](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web.dev - Caching Strategies](https://web.dev/offline-cookbook/)

## 🎉 总结

这个缓存管理系统提供了：

- ✅ 完整的缓存管理功能
- ✅ 多种缓存策略
- ✅ 性能监控和统计
- ✅ 丰富的工具函数
- ✅ 易于使用的 API
- ✅ 良好的浏览器兼容性

现在你可以轻松管理前端缓存，提升应用性能！🚀
