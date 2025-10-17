# 邮件发送 API 修复

## 🐛 问题描述

**错误信息**：
```
INFO: 127.0.0.1:60946 - "POST /api/settings/send-email HTTP/1.1" 500 Internal Server Error
```

**问题原因**：
在 `app/api/settings.py` 的 `send_email_to_recipients` 函数中，代码尝试访问 `report.html_path` 字段并读取文件，但实际上：

1. `DailyReport` 模型中存储的是 `html_content`（HTML 内容本身）
2. 不是 `html_path`（文件路径）

## 🔧 修复方案

### 修改前的代码（错误）
```python
# 读取HTML报告
html_path = Path(report.html_path)  # ❌ 字段不存在
if not html_path.exists():
    raise HTTPException(status_code=404, detail="报告文件不存在")

with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()
```

### 修改后的代码（正确）
```python
# 获取HTML内容
if not report.html_content:  # ✅ 使用正确的字段
    raise HTTPException(status_code=404, detail="报告内容不存在")

html_content = report.html_content  # ✅ 直接使用内容
```

## 📊 DailyReport 模型字段

```python
class DailyReport(Base):
    id = Column(Integer, primary_key=True)
    report_date = Column(Date, nullable=False, unique=True)
    political_summary = Column(Text)
    economic_summary = Column(Text)
    technical_summary = Column(Text)
    fintech_summary = Column(Text)
    overall_summary = Column(Text)
    html_content = Column(Text)        # ✅ HTML 内容（存储在数据库）
    pdf_path = Column(String(500))     # ✅ PDF 文件路径
    created_at = Column(DateTime)
```

## ✅ 修复效果

### 修复前
- ❌ 尝试访问不存在的 `html_path` 字段
- ❌ 导致 500 错误
- ❌ 无法发送邮件

### 修复后
- ✅ 直接从数据库读取 `html_content`
- ✅ 避免文件系统操作
- ✅ 提高性能和可靠性
- ✅ 邮件发送正常

## 🧪 测试方法

### 方法 1：使用测试脚本
```bash
python test_email_api.py
```

### 方法 2：使用 curl
```bash
curl -X POST http://localhost:9998/api/settings/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "report_date": "2025-10-14",
    "recipients": ["test@example.com"],
    "attach_pdf": false
  }'
```

### 方法 3：在前端测试
1. 访问报告详情页面
2. 点击"发送邮件"按钮
3. 输入收件人邮箱
4. 点击发送

## 📝 相关文件

- `app/api/settings.py` - 邮件发送 API（已修复）
- `app/models/daily_report.py` - 报告模型定义
- `app/services/email_service.py` - 邮件发送服务
- `test_email_api.py` - API 测试脚本

## 💡 设计说明

### 为什么存储 HTML 内容而不是文件路径？

**优点**：
1. **数据完整性**：HTML 内容和报告数据在同一个数据库中
2. **简化部署**：不需要管理文件系统
3. **易于备份**：数据库备份包含所有内容
4. **提高性能**：避免文件 I/O 操作
5. **支持分布式**：多个服务器实例可以共享数据库

**缺点**：
1. 数据库体积较大（但现代数据库可以很好地处理）
2. 对于超大 HTML 可能有性能影响（但报告通常不会太大）

### PDF 为什么存储路径？

PDF 文件通常较大，存储路径更合适：
- 减少数据库体积
- 可以使用 CDN 或对象存储
- 便于单独管理和清理

## 🎯 后续优化建议

1. **添加缓存**
   - 缓存常用的 HTML 内容
   - 减少数据库查询

2. **压缩存储**
   - 对 HTML 内容进行 gzip 压缩
   - 节省数据库空间

3. **异步发送**
   - 使用消息队列
   - 避免阻塞 API 响应

4. **批量发送**
   - 支持一次发送到多个收件人
   - 提高效率

## ✅ 修复确认

- ✅ 代码已修复
- ✅ 使用正确的字段名
- ✅ 避免文件系统操作
- ✅ 提高可靠性和性能

修复完成！邮件发送 API 现在应该可以正常工作了。🎉
