# 测试文件说明

## 测试文件列表

### 爬虫相关测试

#### test_crawler_strategies.py
**功能：** 测试爬虫策略架构

**测试内容：**
- 策略模块导入
- 策略优先级验证
- RSS策略创建
- 策略管理器功能
- 策略构建器功能
- Selenium依赖检查
- 示例爬虫检查

**运行方式：**
```bash
python tests/test_crawler_strategies.py
```

**预期结果：**
```
✓ 所有策略模块导入成功
✓ 优先级顺序正确
✓ RSS策略创建成功
✓ 策略管理器工作正常
✓ 策略构建器工作正常
```

---

#### test_migration.py
**功能：** 测试爬虫架构迁移

**测试内容：**
- 检查旧文件是否已删除
- 检查新策略文件是否存在
- 测试工厂类更新
- 测试已迁移的爬虫
- 测试未迁移的爬虫（向后兼容）
- 测试策略管理器

**运行方式：**
```bash
python tests/test_migration.py
```

**预期结果：**
```
✓ 旧文件已删除
✓ 新策略文件已创建
✓ 工厂类已更新
✓ 第一财经爬虫已迁移
✓ 未迁移的爬虫仍然可用（向后兼容）
```

---

#### test_firecrawl_strategy.py
**功能：** 测试Firecrawl策略

**测试内容：**
- Firecrawl策略导入
- 策略优先级检查
- Firecrawl策略实例创建
- 策略管理器集成
- 示例爬虫测试
- 文档完整性检查

**运行方式：**
```bash
python tests/test_firecrawl_strategy.py
```

**预期结果：**
```
✓ Firecrawl策略已添加
✓ 优先级设置正确（6 - 最低）
✓ 策略管理器支持Firecrawl
✓ 示例代码已创建
```

---

#### test_firecrawl_config.py
**功能：** 测试Firecrawl配置读取

**测试内容：**
- 环境变量检查
- 配置加载验证
- Firecrawl策略自动读取配置
- 示例爬虫配置
- 策略管理器自动配置

**运行方式：**
```bash
python tests/test_firecrawl_config.py
```

**预期结果：**
```
✓ 配置加载成功
✓ Firecrawl策略创建成功
✓ API密钥会自动从配置读取
当前状态: ✓ 已配置（Firecrawl策略可用）
```

---

### AI相关测试

#### test_ai_timeout.py
**功能：** 测试AI服务超时配置

**测试内容：**
- AI服务配置加载
- 超时时间设置
- 简单文章摘要生成
- 复杂报告生成

**运行方式：**
```bash
python tests/test_ai_timeout.py
```

**预期结果：**
```
✓ 超时时间: 120秒
✓ 简单摘要生成: 5.16秒
✓ 复杂报告生成: 47.76秒
```

---

### 邮件相关测试

#### test_email_api.py
**功能：** 测试邮件API数据格式

**测试内容：**
- 数据库邮件订阅查询
- 邮件字段验证
- 数据格式检查

**运行方式：**
```bash
python tests/test_email_api.py
```

---

### 前端功能测试

#### test_new_features.py
**功能：** 测试新增的前端功能

**测试内容：**
- 新增文件检查
- API导入测试
- 配置加载测试
- 邮件服务测试
- 模板文件更新检查
- 路由注册验证

**运行方式：**
```bash
python tests/test_new_features.py
```

---

## 运行所有测试

### 方式1：逐个运行
```bash
python tests/test_crawler_strategies.py
python tests/test_migration.py
python tests/test_firecrawl_strategy.py
python tests/test_firecrawl_config.py
python tests/test_ai_timeout.py
python tests/test_email_api.py
python tests/test_new_features.py
```

### 方式2：使用脚本批量运行
```bash
# Windows
for %f in (tests\test_*.py) do python %f

# Linux/Mac
for f in tests/test_*.py; do python "$f"; done
```

### 方式3：使用pytest（如果安装）
```bash
pytest tests/
```

---

## 测试分类

### 核心功能测试
- ✅ test_crawler_strategies.py - 爬虫策略
- ✅ test_migration.py - 架构迁移
- ✅ test_ai_timeout.py - AI服务

### 新功能测试
- ✅ test_firecrawl_strategy.py - Firecrawl策略
- ✅ test_firecrawl_config.py - Firecrawl配置
- ✅ test_new_features.py - 前端功能

### 数据测试
- ✅ test_email_api.py - 邮件数据

---

## 测试覆盖范围

### 爬虫模块
- [x] 策略架构
- [x] 策略优先级
- [x] 策略管理器
- [x] 策略构建器
- [x] RSS策略
- [x] RSSHub策略
- [x] HTTP策略
- [x] Selenium策略
- [x] Firecrawl策略
- [x] 向后兼容性

### 配置模块
- [x] 环境变量读取
- [x] 配置文件加载
- [x] AI配置
- [x] Firecrawl配置
- [x] 邮件配置

### 服务模块
- [x] AI服务
- [x] 邮件服务
- [x] 超时处理

### 前端模块
- [x] API路由
- [x] 模板文件
- [x] 邮件管理

---

## 添加新测试

### 测试文件命名规范
- 文件名：`test_<功能名>.py`
- 放置位置：`tests/` 目录下

### 测试文件模板
```python
"""测试<功能名>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("<功能名>测试")
print("=" * 60)

# 测试1: ...
print("\n测试1: ...")
print("-" * 60)

try:
    # 测试代码
    print("✓ 测试通过")
except Exception as e:
    print(f"✗ 测试失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
```

---

## 持续集成

### GitHub Actions（示例）
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: |
          for f in tests/test_*.py; do
            python "$f" || exit 1
          done
```

---

## 注意事项

1. **测试独立性**
   - 每个测试文件应该独立运行
   - 不依赖其他测试的结果

2. **测试数据**
   - 使用测试数据，不影响生产数据
   - 测试后清理临时数据

3. **环境配置**
   - 确保.env文件配置正确
   - 某些测试需要API密钥

4. **错误处理**
   - 测试失败应该有清晰的错误信息
   - 提供修复建议

---

## 常见问题

### Q: 测试失败怎么办？
**A:** 查看错误信息，检查：
1. 依赖是否安装完整
2. 配置文件是否正确
3. 数据库是否初始化

### Q: 如何跳过某些测试？
**A:** 注释掉对应的测试文件，或使用pytest的skip功能。

### Q: 测试需要多长时间？
**A:** 
- 快速测试（配置、导入）：< 1秒
- 中等测试（策略创建）：1-5秒
- 慢速测试（AI、网络请求）：5-60秒

---

## 更新日志

- 2025-01-14: 创建tests目录
- 2025-01-14: 移动所有测试文件到tests/
- 2025-01-14: 添加测试文档

---

## 相关文档

- [爬虫架构文档](../CRAWLER_ARCHITECTURE.md)
- [Firecrawl集成文档](../FIRECRAWL_INTEGRATION.md)
- [Firecrawl配置指南](../FIRECRAWL_CONFIG_GUIDE.md)
- [迁移完成文档](../MIGRATION_COMPLETE.md)
