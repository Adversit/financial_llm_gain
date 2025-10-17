"""报告生成服务模块

模块结构：
- generator.py: 主报告生成器
- aggregator.py: 数据聚合
- formatter.py: 格式转换（HTML、Markdown）
- pdf_generator.py: PDF 生成
"""

from .generator import ReportGenerator

__all__ = ['ReportGenerator']
