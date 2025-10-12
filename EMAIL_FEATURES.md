# 邮件功能说明

## 功能概述

系统已实现完整的邮件自动发送功能，包括：
- ✅ 自动定时发送每日报告
- ✅ 前端邮件订阅管理
- ✅ 测试邮件发送
- ✅ 多收件人支持

---

## 1. 自动发送功能

### 工作流程

```
每天 08:00 (可配置)
    ↓
自动爬取昨天的文章
    ↓
生成 AI 摘要
    ↓
生成每日报告
    ↓
发送邮件给所有订阅者
```

### 配置文件

在 `config.yaml` 中配置：

```yaml
# 邮件配置
email:
  smtp_server: "${SMTP_SERVER}"      # SMTP 服务器
  smtp_port: 465                      # SMTP 端口
  use_ssl: true                       # 使用 SSL
  username: "${SMTP_USERNAME}"        # 发件人邮箱
  password: "${SMTP_PASSWORD}"        # 邮箱密码/授权码
  from_name: "金融日报系统"           # 发件人名称

# 任务调度配置
scheduler:
  daily_report_time: "08:00"          # 每日发送时间
  timezone: "Asia/Shanghai"           # 时区
```

### 环境变量配置

在 `.env` 文件中设置：

```bash
# 邮件配置
SMTP_SERVER=smtp.163.com              # 网易邮箱
SMTP_USERNAME=your_email@163.com     # 你的邮箱
SMTP_PASSWORD=your_auth_code         # 授权码（不是密码！）
```

### 支持的邮箱服务

| 邮箱服务 | SMTP 服务器 | 端口 | SSL |
|---------|------------|------|-----|
| 网易163 | smtp.163.com | 465 | ✅ |
| 网易126 | smtp.126.com | 465 | ✅ |
| QQ邮箱 | smtp.qq.com | 465 | ✅ |
| Gmail | smtp.gmail.com | 465 | ✅ |
| Outlook | smtp.office365.com | 587 | ❌ (TLS) |

---

## 2. 前端邮件管理

### 访问邮件管理页面

```
http://localhost:9998/emails.html
```

### 功能列表

1. **查看订阅列表**
   - 显示所有邮件订阅者
   - 显示启用/禁用状态

2. **添加订阅者**
   - 输入邮箱地址
   - 自动验证邮箱格式
   - 默认启用

3. **管理订阅**
   - 启用/禁用订阅
   - 删除订阅者

4. **发送测试邮件**
   - 验证邮件配置是否正确
   - 测试邮件发送功能

---

## 3. 邮件内容

### 邮件格式

- **主题**: `金融日报 - YYYY年MM月DD日`
- **格式**: HTML（完整样式）
- **附件**: 无（PDF 功能已禁用）

### 邮件内容包含

- 📋 每日综述（AI 生成）
- 🏛️ 政治层面文章和总结
- 💰 经济层面文章和总结
- 🔬 技术层面文章和总结
- 💳 金融科技层面文章和总结

每篇文章包含：
- 标题（可点击跳转）
- 来源和发布时间
- AI 摘要
- 关键词

---

## 4. API 接口

### 获取订阅列表

```http
GET /emails/
```

响应：
```json
{
  "subscriptions": [
    {
      "id": 1,
      "email": "user@example.com",
      "enabled": true,
      "created_at": "2025-10-12T10:00:00"
    }
  ]
}
```

### 添加订阅

```http
POST /emails/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### 更新订阅

```http
PUT /emails/{email_id}
Content-Type: application/json

{
  "enabled": false
}
```

### 删除订阅

```http
DELETE /emails/{email_id}
```

### 发送测试邮件

```http
POST /emails/test
Content-Type: application/json

{
  "email": "test@example.com"
}
```

---

## 5. 代码实现

### 邮件服务 (`app/services/email_service.py`)

```python
class EmailSender:
    def send_report(
        self,
        recipients: List[str],
        report_date: date,
        html_content: str,
        attach_pdf: bool = False  # 默认不附加 PDF
    ) -> bool:
        """发送报告邮件"""
        # 构建邮件
        # 发送给所有收件人
        # 支持重试机制
```

### 任务调度器 (`app/scheduler/tasks.py`)

```python
class TaskScheduler:
    def run_daily_pipeline(self, target_date: date = None):
        """执行完整的每日流程"""
        # 1. 数据采集
        # 2. 生成摘要
        # 3. 生成报告
        # 4. 发送邮件 ✅
        
        recipients = self._get_active_recipients(db)
        email_sender.send_report(
            recipients=recipients,
            report_date=target_date,
            html_content=report.html_content,
            attach_pdf=False  # 不附加 PDF
        )
```

---

## 6. 使用指南

### 首次配置

1. **获取邮箱授权码**（以网易邮箱为例）
   - 登录网易邮箱
   - 设置 → POP3/SMTP/IMAP
   - 开启 SMTP 服务
   - 获取授权码（不是登录密码！）

2. **配置环境变量**
   ```bash
   # 编辑 .env 文件
   SMTP_SERVER=smtp.163.com
   SMTP_USERNAME=your_email@163.com
   SMTP_PASSWORD=your_auth_code
   ```

3. **添加订阅者**
   - 访问 http://localhost:9998/emails.html
   - 点击"添加订阅"
   - 输入邮箱地址

4. **测试邮件**
   - 点击"发送测试邮件"
   - 检查收件箱

### 手动发送报告

如果需要立即发送报告：

```python
from app.database import SessionLocal
from app.services.email_service import EmailSender
from app.models.daily_report import DailyReport
from app.config import load_config
from datetime import date, timedelta

config = load_config()
db = SessionLocal()

# 获取昨天的报告
yesterday = date.today() - timedelta(days=1)
report = db.query(DailyReport).filter(
    DailyReport.report_date == yesterday
).first()

if report:
    # 创建邮件发送器
    email_sender = EmailSender(
        smtp_server=config['email']['smtp_server'],
        smtp_port=config['email']['smtp_port'],
        username=config['email']['username'],
        password=config['email']['password']
    )
    
    # 发送邮件
    recipients = ['user1@example.com', 'user2@example.com']
    success = email_sender.send_report(
        recipients=recipients,
        report_date=yesterday,
        html_content=report.html_content
    )
    
    print("发送成功" if success else "发送失败")

db.close()
```

---

## 7. 常见问题

### Q1: 邮件发送失败

**可能原因：**
1. SMTP 配置错误
2. 授权码错误（不是登录密码）
3. 邮箱未开启 SMTP 服务
4. 网络问题

**解决方案：**
1. 检查 `.env` 配置
2. 重新获取授权码
3. 使用测试邮件功能验证
4. 查看日志 `logs/email.log`

### Q2: 收不到邮件

**检查：**
1. 垃圾邮件箱
2. 邮箱地址是否正确
3. 订阅是否启用
4. 服务器日志是否显示发送成功

### Q3: 如何修改发送时间

编辑 `config.yaml`:
```yaml
scheduler:
  daily_report_time: "09:00"  # 改为 9:00
```

重启服务器生效。

### Q4: 如何禁用自动发送

方法1: 禁用所有订阅
- 访问邮件管理页面
- 禁用所有订阅者

方法2: 停止调度器
- 修改代码不启动调度器

---

## 8. 邮件模板

邮件使用 HTML 模板，位于 `templates/email_template.html`

可以自定义样式和内容。

---

## 9. 监控和日志

### 查看邮件日志

```bash
# Windows
type logs\email.log

# Linux/Mac
tail -f logs/email.log
```

### 日志内容

- 邮件发送时间
- 收件人列表
- 发送结果（成功/失败）
- 错误信息

---

## 10. 安全建议

1. ✅ 使用授权码，不要使用登录密码
2. ✅ 不要将 `.env` 文件提交到 Git
3. ✅ 定期更换授权码
4. ✅ 限制收件人数量，避免被标记为垃圾邮件
5. ✅ 使用专用邮箱发送，不要使用个人主邮箱

---

## 总结

✅ **已实现的功能：**
- 自动定时发送
- 前端订阅管理
- 测试邮件
- 多收件人
- HTML 格式
- 重试机制

❌ **暂未实现：**
- PDF 附件（已禁用）
- 邮件模板自定义（需手动编辑）
- 发送历史记录
- 邮件统计分析

💡 **使用建议：**
1. 先配置邮箱并测试
2. 添加少量订阅者测试
3. 确认无误后添加更多订阅者
4. 定期检查日志
