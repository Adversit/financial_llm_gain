# PDF 功能说明

## 当前状态

PDF 功能已实现，但**暂时隐藏**，不在前端显示和邮件发送中使用。

## 配置说明

在 `config.yaml` 中可以控制 PDF 相关功能：

```yaml
report:
  generate_pdf: true              # 是否生成 PDF（后台生成）
  show_pdf_in_frontend: false     # 是否在前端显示 PDF 下载链接
  attach_pdf_in_email: false      # 是否在邮件中附加 PDF
```

## PDF 生成方式

系统支持多种 PDF 生成方式，按优先级尝试：

1. **WeasyPrint** - 质量最好，需要 GTK3 运行时
2. **pdfkit** - 需要 wkhtmltopdf
3. **Markdown → reportlab** - 通过 Markdown 中间格式生成
4. **xhtml2pdf** - 最简单，但中文支持有限

## 当前实现

### 后台生成
- ✅ 报告生成时会自动生成 PDF 文件
- ✅ PDF 文件保存在 `data/reports/` 目录
- ✅ 数据库中记录 PDF 路径

### 前端隐藏
- ✅ API 返回空的 `pdf_path`
- ✅ 前端不显示 PDF 下载按钮
- ✅ 邮件不附加 PDF 文件

## 启用 PDF 功能

如果将来需要启用 PDF 功能，只需修改以下位置：

### 1. 前端显示 PDF

修改 API 返回：
```python
# app/api/custom_reports.py
return CustomReportResponse(
    success=True,
    message="个性化报告生成成功",
    html_content=html_content,
    pdf_path=pdf_path  # 返回实际的 PDF 路径
)
```

### 2. 邮件附加 PDF

修改调度器：
```python
# app/scheduler/tasks.py
success = email_sender.send_report(
    recipients=recipients,
    report_date=target_date,
    html_content=report.html_content,
    pdf_path=report.pdf_path,
    attach_pdf=True  # 改为 True
)
```

### 3. 配置文件

```yaml
# config.yaml
report:
  generate_pdf: true
  show_pdf_in_frontend: true   # 改为 true
  attach_pdf_in_email: true    # 改为 true
```

## PDF 生成库安装

### WeasyPrint（推荐）

**Windows:**
1. 下载 GTK3 运行时：https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. 安装后重启终端
3. WeasyPrint 已在 requirements.txt 中

**Linux:**
```bash
sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0
pip install weasyprint
```

### pdfkit

1. 下载 wkhtmltopdf：https://wkhtmltopdf.org/downloads.html
2. 安装 Python 包：
```bash
pip install pdfkit
```

### 其他库（已安装）

```bash
pip install markdown2 xhtml2pdf reportlab
```

## 文件位置

- 报告生成服务：`app/services/report_service.py`
- 邮件服务：`app/services/email_service.py`
- 调度器：`app/scheduler/tasks.py`
- API：`app/api/custom_reports.py`
- 配置：`config.yaml`

## 注意事项

1. PDF 生成失败不会影响主流程（HTML 报告和邮件发送）
2. PDF 文件会占用磁盘空间，建议定期清理旧文件
3. 不同的 PDF 生成库对中文和样式的支持程度不同
