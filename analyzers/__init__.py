"""
分析器模块 - 技术、情绪、宏观、动量分析

职责：
- 技术分析（RSI、MACD、均线等）
- 情绪分析（新闻情绪、市场情绪）
- 宏观分析（政策解读、全球经济）
- 动量分析（价格动量、资金流向）
"""

from .base import Analyzer, AnalyzerConfig
from .technical import TechnicalAnalyzer
from .sentiment import SentimentAnalyzer
from .macro import MacroAnalyzer
from .momentum import MomentumAnalyzer

__all__ = [
    'Analyzer',
    'AnalyzerConfig',
    'TechnicalAnalyzer',
    'SentimentAnalyzer',
    'MacroAnalyzer',
    'MomentumAnalyzer',
]

__version__ = '1.0.0'
