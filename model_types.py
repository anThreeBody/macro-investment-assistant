#!/usr/bin/env python3
"""
统一数据类型定义

为整个投资分析系统提供标准化的数据结构，便于 AI 模型理解和集成。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime


# ==================== 枚举类型 ====================

class ConfidenceLevel(str, Enum):
    """置信度等级"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class Direction(str, Enum):
    """价格方向"""
    UP = "up"
    DOWN = "down"
    SIDEWAYS = "sideways"


class Signal(str, Enum):
    """交易信号"""
    BUY = "买入"
    SELL = "卖出"
    HOLD = "持有"


class DataQuality(str, Enum):
    """数据质量等级"""
    A = "A"  # >0.9 优秀
    B = "B"  # 0.7-0.9 良好
    C = "C"  # 0.5-0.7 合格
    D = "D"  # <0.5 不合格


# ==================== 基础数据类 ====================

@dataclass
class PriceData:
    """价格数据基础类"""
    price: float
    change: float = 0.0
    change_pct: float = 0.0
    currency: str = "CNY"
    unit: str = "g"
    source: str = ""
    timestamp: str = ""


@dataclass
class InternationalGoldPrice(PriceData):
    """国际金价 (美元/盎司)"""
    currency: str = "USD"
    unit: str = "oz"


@dataclass
class DomesticGoldPrice(PriceData):
    """国内金价 (元/克)"""
    currency: str = "CNY"
    unit: str = "g"


@dataclass
class GoldPrice:
    """完整金价数据"""
    international: InternationalGoldPrice
    domestic: DomesticGoldPrice
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'international': {
                'price': self.international.price,
                'change': self.international.change,
                'change_pct': self.international.change_pct,
                'currency': self.international.currency,
                'unit': self.international.unit
            },
            'domestic': {
                'price': self.domestic.price,
                'change': self.domestic.change,
                'change_pct': self.domestic.change_pct,
                'currency': self.domestic.currency,
                'unit': self.domestic.unit
            },
            'metadata': self.metadata
        }


# ==================== 宏观数据类 ====================

@dataclass
class MacroIndicator:
    """宏观指标"""
    name: str
    code: str
    value: float
    change: float = 0.0
    change_pct: float = 0.0
    source: str = ""
    timestamp: str = ""


@dataclass
class MacroData:
    """完整宏观数据"""
    dxy: MacroIndicator  # 美元指数
    vix: MacroIndicator  # 恐慌指数
    oil: MacroIndicator  # 原油价格
    treasury: MacroIndicator  # 美债收益率
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'dxy': {
                'name': self.dxy.name,
                'code': self.dxy.code,
                'value': self.dxy.value,
                'change': self.dxy.change,
                'change_pct': self.dxy.change_pct,
                'source': self.dxy.source
            },
            'vix': {
                'name': self.vix.name,
                'code': self.vix.code,
                'value': self.vix.value,
                'change': self.vix.change,
                'change_pct': self.vix.change_pct,
                'source': self.vix.source
            },
            'oil': {
                'name': self.oil.name,
                'code': self.oil.code,
                'value': self.oil.value,
                'change': self.oil.change,
                'change_pct': self.oil.change_pct,
                'source': self.oil.source
            },
            'treasury': {
                'name': self.treasury.name,
                'code': self.treasury.code,
                'value': self.treasury.value,
                'change': self.treasury.change,
                'change_pct': self.treasury.change_pct,
                'source': self.treasury.source
            }
        }


# ==================== 新闻数据类 ====================

@dataclass
class NewsItem:
    """单条新闻"""
    title: str
    summary: str
    url: str
    source: str
    publish_time: str
    sentiment: float = 0.0  # -1.0 到 1.0，负面向正面


@dataclass
class NewsData:
    """完整新闻数据"""
    items: List[NewsItem]
    avg_sentiment: float = 0.0
    total_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'items': [
                {
                    'title': item.title,
                    'summary': item.summary,
                    'url': item.url,
                    'source': item.source,
                    'publish_time': item.publish_time,
                    'sentiment': item.sentiment
                }
                for item in self.items
            ],
            'avg_sentiment': self.avg_sentiment,
            'total_count': self.total_count
        }


# ==================== 分析结果类 ====================

@dataclass
class TechnicalAnalysis:
    """技术分析结果"""
    rsi: float = 50.0
    macd: float = 0.0
    macd_signal: float = 0.0
    ma_5: float = 0.0
    ma_10: float = 0.0
    ma_20: float = 0.0
    trend: str = "sideways"
    score: float = 0.5
    signal: str = "持有"


@dataclass
class SentimentAnalysis:
    """情感分析结果"""
    avg_sentiment: float = 0.0
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    score: float = 0.5
    signal: str = "持有"


@dataclass
class MacroAnalysis:
    """宏观分析结果"""
    dxy_impact: float = 0.0  # 美元影响
    vix_impact: float = 0.0  # 恐慌影响
    oil_impact: float = 0.0  # 原油影响
    treasury_impact: float = 0.0  # 美债影响
    overall_impact: str = "neutral"
    score: float = 0.5
    signal: str = "持有"


@dataclass
class MomentumAnalysis:
    """动量分析结果"""
    trend_strength: float = 0.0  # 趋势强度 0-1
    momentum_score: float = 0.0
    acceleration: float = 0.0
    score: float = 0.5
    signal: str = "持有"


# ==================== 预测结果类 ====================

@dataclass
class TimeSeriesPrediction:
    """时序预测结果"""
    predicted_price: float
    trend: str = "sideways"
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    lower_bound: float = 0.0
    upper_bound: float = 0.0


@dataclass
class MultiFactorPrediction:
    """多因子预测结果"""
    current_price: float
    predicted_price: float
    price_lower: float
    price_upper: float
    direction: Direction
    confidence: ConfidenceLevel
    signal: Signal
    scores: Dict[str, float] = field(default_factory=dict)
    weights: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'current_price': self.current_price,
            'predicted_price': self.predicted_price,
            'price_lower': self.price_lower,
            'price_upper': self.price_upper,
            'direction': self.direction.value,
            'confidence': self.confidence.value,
            'signal': self.signal.value,
            'scores': self.scores,
            'weights': self.weights
        }


@dataclass
class CompletePrediction:
    """完整预测结果"""
    current_price: float
    predicted_price: float
    price_lower: float
    price_upper: float
    direction: Direction
    confidence: ConfidenceLevel
    signal: Signal
    analysis: Dict[str, Any] = field(default_factory=dict)
    time_series: Optional[TimeSeriesPrediction] = None
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'current_price': self.current_price,
            'predicted_price': self.predicted_price,
            'price_lower': self.price_lower,
            'price_upper': self.price_upper,
            'direction': self.direction.value,
            'confidence': self.confidence.value,
            'signal': self.signal.value,
            'analysis': self.analysis,
            'time_series': {
                'predicted_price': self.time_series.predicted_price,
                'trend': self.time_series.trend,
                'confidence': self.time_series.confidence.value,
                'lower_bound': self.time_series.lower_bound,
                'upper_bound': self.time_series.upper_bound
            } if self.time_series else None,
            'timestamp': self.timestamp
        }


# ==================== 数据质量类 ====================

@dataclass
class DataQualityReport:
    """数据质量报告"""
    score: float
    level: DataQuality
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'score': self.score,
            'level': self.level.value,
            'valid': self.valid,
            'errors': self.errors,
            'warnings': self.warnings
        }


# ==================== 简报数据类 ====================

@dataclass
class DailyBrief:
    """每日简报数据"""
    date: str
    timestamp: str
    gold_price: GoldPrice
    macro_data: MacroData
    news_data: NewsData
    prediction: CompletePrediction
    brief_content: str
    charts: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'date': self.date,
            'timestamp': self.timestamp,
            'gold_price': self.gold_price.to_dict(),
            'macro_data': self.macro_data.to_dict(),
            'news_data': self.news_data.to_dict(),
            'prediction': self.prediction.to_dict(),
            'brief_content': self.brief_content,
            'charts': self.charts
        }


# ==================== 预测验证类 ====================

@dataclass
class PredictionVerification:
    """预测验证结果"""
    date: str
    predicted_price: float
    actual_price: float
    error: float
    error_pct: float
    accuracy: float
    predicted_direction: Direction
    actual_direction: Direction
    direction_correct: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'date': self.date,
            'predicted_price': self.predicted_price,
            'actual_price': self.actual_price,
            'error': self.error,
            'error_pct': self.error_pct,
            'accuracy': self.accuracy,
            'predicted_direction': self.predicted_direction.value,
            'actual_direction': self.actual_direction.value,
            'direction_correct': self.direction_correct
        }


@dataclass
class AccuracyStats:
    """准确率统计"""
    total_predictions: int
    correct_predictions: int
    accuracy: float
    success_rate: float
    avg_error: float
    avg_error_pct: float
    period_days: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total': self.total_predictions,
            'correct': self.correct_predictions,
            'accuracy': self.accuracy,
            'success_rate': self.success_rate,
            'avg_error': self.avg_error,
            'avg_error_pct': self.avg_error_pct,
            'period_days': self.period_days
        }


# ==================== 工具函数 ====================

def create_empty_gold_price() -> GoldPrice:
    """创建空金价数据"""
    return GoldPrice(
        international=InternationalGoldPrice(price=0.0),
        domestic=DomesticGoldPrice(price=0.0),
        metadata={'source': 'fallback', 'update_time': ''}
    )


def create_empty_macro_data() -> MacroData:
    """创建空宏观数据"""
    return MacroData(
        dxy=MacroIndicator(name='美元指数', code='DXY', value=0.0),
        vix=MacroIndicator(name='恐慌指数', code='VIX', value=0.0),
        oil=MacroIndicator(name='原油', code='OIL', value=0.0),
        treasury=MacroIndicator(name='美债收益率', code='TREASURY', value=0.0)
    )


def create_empty_news_data() -> NewsData:
    """创建空新闻数据"""
    return NewsData(items=[], avg_sentiment=0.0, total_count=0)


# ==================== 常量定义 ====================

# 验证阈值
VALIDATION_THRESHOLDS = {
    'gold_price_domestic': (500, 1500),  # 元/克
    'gold_price_international': (150, 350),  # 美元/盎司
    'dxy': (50, 150),
    'vix': (10, 100),
    'oil_price': (50, 150),  # 美元/桶
    'treasury_yield': (1, 10),  # %
}

# 预测权重
PREDICTION_WEIGHTS = {
    'technical': 0.255,
    'sentiment': 0.2125,
    'macro': 0.2125,
    'momentum': 0.17,
    'time_series': 0.15,
}

# 置信度阈值
CONFIDENCE_THRESHOLDS = {
    'high': 0.8,
    'medium': 0.6,
    'low': 0.4,
}

# 交易信号阈值
SIGNAL_THRESHOLDS = {
    'buy': 0.7,
    'sell': 0.3,
    'hold': 0.5,
}
