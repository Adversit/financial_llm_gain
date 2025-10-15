# 📚 信息源测试工具使用指南

本目录包含用于测试和管理信息源的工具脚本。

---

## 🛠️ 可用工具

### 1. `list_sources.py` - 快速查看信息源

**用途**: 快速列出所有配置的信息源及其状态

**使用方法**:
```bash
python list_sources.py
```

**输出示例**:
```
【RSS源】
状态       名称                    类别         爬取方式
✓ 可用     移动支付网                金融科技      RSSStrategy
✓ 可用     金融监管研究              政治         RSSStrategy
...

统计信息:
RSS源:      24/24 可用
RSSHub源:   7/16 可用
自定义爬虫: 2/7 可用
总计:       33/47 可用 (70.2%)
```

---

### 2. `test_all_sources.py` - 完整测试所有信息源

**用途**: 测试所有启用的信息源，验证其可用性并统计文章数量

**使用方法**:
```bash
python test_all_sources.py
```

**功能**:
- 测试所有启用的信息源
- 显示每个源获取的文章数量
- 生成详细的测试报告
- 自动保存结果到文件

**输出文件**: `source_test_results_YYYYMMDD_HHMMSS.txt`

**测试时间**: 约2-3分钟（取决于网络速度）

---

### 3. `tests/test_sources_detailed.py` - 详细测试（开发用）

**用途**: 开发和调试时使用的详细测试脚本

**使用方法**:
```bash
python -m pytest tests/test_sources_detailed.py -v
```

---

## 📊 生成的报告文档

### 1. `SOURCES_STATUS_REPORT.md`
- 最详细的状态报告
- 包含所有源的详细信息
- 按类别和领域分组
- 包含数据量预估

### 2. `SOURCE_INTEGRATION_SUMMARY.md`
- 集成工作总结
- 问题分析和解决方案
- 系统建议

### 3. `FINAL_INTEGRATION_REPORT.md`
- 最终完成报告
- 核心成果展示
- 使用指南
- 优化建议

---

## 🎯 常见使用场景

### 场景1: 快速检查系统状态

```bash
# 查看哪些源是启用的
python list_sources.py
```

### 场景2: 验证所有源是否正常工作

```bash
# 完整测试（需要2-3分钟）
python test_all_sources.py
```

### 场景3: 添加新信息源后验证

```bash
# 1. 编辑 config.yaml 添加新源
# 2. 运行测试
python test_all_sources.py

# 3. 查看结果
python list_sources.py
```

### 场景4: 调试特定信息源

```python
# 使用Python交互式测试
from app.crawlers.factory import CrawlerFactory

# 测试RSS源
crawler = CrawlerFactory.create_crawler(
    source_type='rss',
    source_name='测试源',
    url='http://example.com/feed.rss'
)
articles = crawler.fetch()
print(f"获取到 {len(articles)} 篇文章")

# 测试RSSHub源
crawler = CrawlerFactory.create_crawler(
    source_type='rsshub',
    source_name='测试源',
    rsshub_base='http://rsshub.app',
    rsshub_route='gov/pbc/zcyj'
)
articles = crawler.fetch()

# 测试自定义爬虫
crawler = CrawlerFactory.create_crawler(
    source_type='custom',
    source_name='测试源',
    url='http://example.com',
    crawler_class='YourCrawler'
)
articles = crawler.fetch()
```

---

## 📝 配置文件说明

### `config.yaml` 结构

```yaml
sources:
  # RSS源
  rss:
    - name: "源名称"
      category: "类别"  # 技术/政治/经济/金融科技
      url: "RSS地址"
      enabled: true/false
  
  # RSSHub源
  rsshub:
    - name: "源名称"
      category: "类别"
      route: "RSSHub路由"
      enabled: true/false
  
  # 自定义爬虫
  custom:
    - name: "源名称"
      category: "类别"
      crawler_class: "爬虫类名"
      url: "网站地址"
      enabled: true/false
```

---

## 🔧 故障排查

### 问题1: RSS源测试失败

**可能原因**:
- RSS服务器不可达
- URL配置错误
- 网络连接问题

**解决方法**:
```bash
# 1. 检查URL是否正确
curl -I "RSS地址"

# 2. 测试单个源
python -c "from app.crawlers.factory import CrawlerFactory; c = CrawlerFactory.create_crawler('rss', '测试', 'URL'); print(c.fetch())"
```

### 问题2: RSSHub源返回503

**可能原因**:
- RSSHub服务器负载过高
- 路由已失效
- RSSHub实例不可用

**解决方法**:
```bash
# 1. 检查RSSHub服务器
curl "http://rsshub服务器地址/gov/pbc/zcyj"

# 2. 尝试其他RSSHub实例
# 编辑 config.yaml 中的 rsshub.base_url
```

### 问题3: 自定义爬虫无法加载

**可能原因**:
- 爬虫类名错误
- 文件名不匹配
- 爬虫未实现必需方法

**解决方法**:
```bash
# 1. 检查爬虫文件是否存在
ls app/crawlers/custom/*_crawler.py

# 2. 检查类名是否正确
grep "class.*Crawler" app/crawlers/custom/your_crawler.py

# 3. 验证爬虫实现
python -c "from app.crawlers.custom.your_crawler import YourCrawler; c = YourCrawler(); print(c.fetch())"
```

---

## 📈 性能优化建议

### 1. 并行测试（高级）

```python
# 使用多线程加速测试
from concurrent.futures import ThreadPoolExecutor

def test_source(source):
    # 测试逻辑
    pass

with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(test_source, sources)
```

### 2. 缓存测试结果

```bash
# 保存测试结果供后续分析
python test_all_sources.py > test_results.log 2>&1
```

### 3. 定期自动测试

```bash
# Linux/Mac - 添加到crontab
0 */6 * * * cd /path/to/project && python test_all_sources.py

# Windows - 使用任务计划程序
```

---

## 🎓 最佳实践

### 1. 添加新信息源的流程

1. 在 `config.yaml` 中添加源配置
2. 设置 `enabled: false` 先禁用
3. 运行 `python test_all_sources.py` 测试
4. 如果测试通过，设置 `enabled: true`
5. 重新测试确认

### 2. 定期维护

- 每周运行一次完整测试
- 检查失效的源
- 更新配置和爬虫
- 记录变更日志

### 3. 监控建议

- 记录每次测试的成功率
- 追踪文章数量变化
- 及时发现异常源
- 建立告警机制

---

## 📞 获取帮助

如果遇到问题：

1. 查看日志文件: `logs/app.log`
2. 运行详细测试: `python test_all_sources.py`
3. 检查配置文件: `config.yaml`
4. 查看文档: `SOURCES_STATUS_REPORT.md`

---

## 🎉 总结

这些工具帮助您：
- ✅ 快速了解系统状态
- ✅ 验证信息源可用性
- ✅ 调试和排查问题
- ✅ 监控系统健康度

**保持信息源的健康运行，确保系统稳定可靠！** 🚀
