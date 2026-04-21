"""
输出展示模块 - 简报、图表、报告生成

职责：
- 生成每日简报（Markdown）
- 生成可视化图表（matplotlib）
- 生成分析报告（PDF/Markdown）
"""

from .brief_generator import BriefGenerator
from .chart_generator import ChartGenerator

__all__ = [
    'BriefGenerator',
    'ChartGenerator',
]

__version__ = '1.0.0'
