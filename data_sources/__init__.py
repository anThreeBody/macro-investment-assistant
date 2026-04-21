"""
数据源模块 - 统一数据获取接口

职责：
- 采集原始数据（金价、基金、股票、新闻、宏观）
- 提供标准化数据格式
- 支持数据缓存和容错
"""

from .base import DataSource, DataSourceConfig
from .gold_source import GoldDataSource
from .fund_source import FundDataSource
from .stock_source import StockDataSource
from .news_source import NewsDataSource
from .macro_source import MacroDataSource

__all__ = [
    'DataSource',
    'DataSourceConfig',
    'GoldDataSource',
    'FundDataSource',
    'StockDataSource',
    'NewsDataSource',
    'MacroDataSource',
]

__version__ = '1.0.0'
