"""报告生成服务 - 向后兼容的导入接口

此文件保持向后兼容性，实际实现已拆分到 report 子模块中。
"""

from .report import ReportGenerator

__all__ = ['ReportGenerator']
