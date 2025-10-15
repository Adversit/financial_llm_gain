# Firecrawl配置指南

## 快速配置

### 步骤1: 获取API密钥

1. 访问 https://firecrawl.dev
2. 注册账号
3. 获取API密钥

### 步骤2: 配置到.env文件

打开项目根目录的 `.env` 文件，添加或修改以下配置：

```bash
# Firecrawl配置
FIRECRAWL_API_KEY=your_api_key_here
FIRECRAWL_API_URL=https://api.firecrawl.dev/v0
```

**示例：**
```bash
# Firecrawl配置（可选 - 用于难以爬取的网站）
# 获取API密钥: https://firecrawl.dev
# 留空则不使用Firecrawl策略
FIRECRAWL_API_KEY=fc-1234567890abcdef
FIRECRAWL_API_URL=https://api.firecrawl.dev/v0
```

### 步骤3: 重启服务

```bash
# 停止服务
Ctrl+C

# 重新启动
python start_server.py
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `FIRECRAWL_API_KEY` | Firecrawl API密钥 | 无 | 否* |
| `FIRECRAWL_API_URL` | Firecrawl API地址 | `https://api.firecrawl.dev/v0` | 否 |

*如果不配置API密钥，Firecrawl策略会被自动跳过，不影响其他策略的使用。

### config.yaml配置

系统会自动从环境变量读取配置，也可以在 `config.yaml` 中查看配置：

```yaml
# Firecrawl配置（可选）
firecrawl:
  api_key: "${FIRECRAWL_API_KEY}"
  api_url: "${FIRECRAWL_API_URL}"
  enabled: true  # 是否启用Firecrawl策略
  timeout: 60  # API请求超时时间（秒）
```

## 使用方式

### 自动配置（推荐）

配置好.env后，所有Firecrawl策略会自动读取配置：

```python
from app.crawlers.strategies import FirecrawlStrategy

# API密钥自动从配置读取
strategy = FirecrawlStrategy(
    source_name="网站名称",
    source_url="https://example.com"
)

articles = strategy.fetch()
```

### 手动指定（可选）

如果需要使用不同的API密钥：

```python
strategy = FirecrawlStrategy(
    source_name="网站名称",
    source_url="https://example.com",
    api_key="另一个API密钥"  # 手动指定
)
```

## 验证配置

### 运行测试脚本

```bash
python test_firecrawl_config.py
```

**预期输出：**
```
✓ 配置加载成功
  - API密钥: 已配置
  - API URL: https://api.firecrawl.dev/v0
  - 启用状态: True
  - 超时时间: 60秒

当前状态: ✓ 已配置（Firecrawl策略可用）
```

### 检查配置

```python
from app.config import get_config

config = get_config()
firecrawl_config = config.get('firecrawl', {})

print(f"API密钥: {firecrawl_config.get('api_key')}")
print(f"API URL: {firecrawl_config.get('api_url')}")
```

## 常见问题

### Q: 必须配置Firecrawl吗？

**A:** 不是。Firecrawl是可选的。如果不配置：
- Firecrawl策略会被自动跳过
- 不影响其他策略（RSS、HTTP、Selenium等）
- 系统仍然可以正常工作

### Q: 如何知道Firecrawl是否配置成功？

**A:** 运行测试脚本：
```bash
python test_firecrawl_config.py
```

或者查看日志，如果配置成功，会看到：
```
[INFO] 添加Firecrawl策略作为备选
```

### Q: API密钥配置错误会怎样？

**A:** 
- Firecrawl策略的 `can_handle()` 会返回 `False`
- 策略管理器会自动跳过Firecrawl
- 尝试使用其他可用的策略
- 不会导致程序崩溃

### Q: 如何临时禁用Firecrawl？

**A:** 有两种方式：

**方式1：清空API密钥**
```bash
# .env文件
FIRECRAWL_API_KEY=
```

**方式2：在config.yaml中禁用**
```yaml
firecrawl:
  enabled: false
```

### Q: 可以使用自己部署的Firecrawl服务吗？

**A:** 可以。修改API URL：
```bash
# .env文件
FIRECRAWL_API_URL=http://your-firecrawl-server.com/v0
```

### Q: 如何查看Firecrawl的使用情况？

**A:** 查看日志文件 `logs/app.log`，搜索 "Firecrawl"：
```bash
grep "Firecrawl" logs/app.log
```

## 安全建议

### 1. 保护API密钥

- ✅ 使用.env文件存储
- ✅ 不要提交到Git仓库
- ✅ 定期更换API密钥
- ❌ 不要硬编码在代码中
- ❌ 不要在日志中打印

### 2. .gitignore配置

确保 `.env` 文件在 `.gitignore` 中：
```
# .gitignore
.env
```

### 3. 环境变量优先级

配置读取优先级：
1. 代码中手动传入的参数
2. 环境变量（.env文件）
3. config.yaml中的默认值

## 成本控制

### 监控使用量

Firecrawl是付费服务，建议：

1. **设置使用限制**
   - 只在其他策略失败时使用
   - 设置为最低优先级（已默认）

2. **记录使用情况**
   ```python
   # 在日志中记录Firecrawl调用
   self.logger.info(f"使用Firecrawl爬取: {url}")
   ```

3. **定期检查账单**
   - 访问 Firecrawl 控制台
   - 查看API调用统计
   - 设置预算告警

### 优化建议

- 优先使用免费策略（RSS、HTTP）
- 只对难爬的网站使用Firecrawl
- 实现缓存机制避免重复调用
- 批量处理以减少API调用次数

## 示例配置

### 开发环境

```bash
# .env
FIRECRAWL_API_KEY=fc-dev-key-123
FIRECRAWL_API_URL=https://api.firecrawl.dev/v0
```

### 生产环境

```bash
# .env
FIRECRAWL_API_KEY=fc-prod-key-456
FIRECRAWL_API_URL=https://api.firecrawl.dev/v0
```

### 测试环境（不使用Firecrawl）

```bash
# .env
FIRECRAWL_API_KEY=
FIRECRAWL_API_URL=https://api.firecrawl.dev/v0
```

## 总结

✅ **配置简单**
- 只需在.env中添加API密钥
- 自动读取，无需手动传参

✅ **完全可选**
- 不配置不影响其他功能
- 可以随时启用/禁用

✅ **安全可靠**
- API密钥存储在.env
- 不会泄露到代码仓库

✅ **灵活使用**
- 可以全局配置
- 也可以单独指定

**配置完成后，Firecrawl将作为最后的备选方案，提高爬取成功率！** 🎉
