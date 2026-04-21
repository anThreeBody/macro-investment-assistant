#!/usr/bin/env python3
"""
技术分析器 - 计算技术指标并生成信号

支持指标：
- RSI（相对强弱指标）
- MACD（移动平均收敛散度）
- 均线系统（MA5/10/20/60）
- 布林带
"""

import logging
from typing import Any, Dict, List, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.base import Analyzer, AnalyzerConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalAnalyzer(Analyzer):
    """技术分析器"""
    
    def __init__(self):
        config = AnalyzerConfig(
            name='技术分析器',
            analyzer_type='technical',
            enabled=True,
            weight=0.30,  # 技术分析权重 30%
            params={
                'rsi_period': 14,
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9,
                'ma_periods': [5, 10, 20, 60],
            }
        )
        super().__init__(config)
    
    def analyze(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        执行技术分析
        
        Args:
            data: 价格数据（需要包含历史价格）
                {
                    'prices': [p1, p2, ...],  # 价格列表（从旧到新）
                    'current_price': float,    # 当前价格
                }
            
        Returns:
            Dict[str, Any]: {
                'rsi': float,
                'macd': {...},
                'ma': {...},
                'bollinger': {...},
                'trend': str,  # up/down/sideways
                'score': float,  # -1 到 1
                'signal': str,  # buy/sell/hold
            }
        """
        logger.info("[技术分析] 开始分析...")
        
        prices = data.get('prices', [])
        current_price = data.get('current_price', 0)
        
        if len(prices) < 60:
            logger.warning(f"[技术分析] 数据不足（{len(prices)}条），需要至少 60 条")
            return self._get_default_result()
        
        # 计算各项指标
        rsi = self._calculate_rsi(prices, self.config.params['rsi_period'])
        macd = self._calculate_macd(prices)
        ma = self._calculate_ma(prices, self.config.params['ma_periods'])
        bollinger = self._calculate_bollinger(prices)
        
        # 判断趋势
        trend = self._determine_trend(prices, ma)
        
        # 计算综合得分
        score = self._calculate_score(rsi, macd, ma, trend, current_price)
        
        # 生成信号
        signal = self._generate_signal(score, rsi, trend)
        
        result = {
            'rsi': round(rsi, 2),
            'macd': macd,
            'ma': ma,
            'bollinger': bollinger,
            'trend': trend,
            'score': round(score, 3),
            'signal': signal,
            'current_price': current_price,
        }
        
        logger.info(f"[技术分析] RSI={rsi:.2f}, 趋势={trend}, 得分={score:.3f}, 信号={signal}")
        return result
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算 RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        # 计算价格变化
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # 分离涨跌
        gains = [max(0, c) for c in changes[-period:]]
        losses = [max(0, -c) for c in changes[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: List[float]) -> Dict[str, Any]:
        """计算 MACD"""
        fast = self.config.params['macd_fast']
        slow = self.config.params['macd_slow']
        signal = self.config.params['macd_signal']
        
        if len(prices) < slow + signal:
            return {'macd': 0, 'signal': 0, 'histogram': 0, 'trend': 'neutral'}
        
        # 计算 EMA
        ema_fast = self._ema(prices, fast)
        ema_slow = self._ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = self._ema([macd_line], signal) if isinstance(macd_line, list) else macd_line * 0.9
        histogram = macd_line - signal_line
        
        # 判断 MACD 趋势
        if histogram > 0:
            trend = 'bullish'
        elif histogram < 0:
            trend = 'bearish'
        else:
            trend = 'neutral'
        
        return {
            'macd': round(macd_line, 4),
            'signal': round(signal_line, 4),
            'histogram': round(histogram, 4),
            'trend': trend,
        }
    
    def _calculate_ma(self, prices: List[float], periods: List[int]) -> Dict[str, float]:
        """计算均线"""
        ma = {}
        
        for period in periods:
            if len(prices) >= period:
                ma[f'ma{period}'] = round(sum(prices[-period:]) / period, 2)
            else:
                ma[f'ma{period}'] = 0.0
        
        return ma
    
    def _calculate_bollinger(self, prices: List[float], period: int = 20) -> Dict[str, Any]:
        """计算布林带"""
        if len(prices) < period:
            return {'upper': 0, 'middle': 0, 'lower': 0, 'width': 0}
        
        # 中轨（20 日均线）
        middle = sum(prices[-period:]) / period
        
        # 标准差
        variance = sum((p - middle) ** 2 for p in prices[-period:]) / period
        std = variance ** 0.5
        
        # 上下轨
        upper = middle + 2 * std
        lower = middle - 2 * std
        
        # 带宽
        width = (upper - lower) / middle if middle > 0 else 0
        
        return {
            'upper': round(upper, 2),
            'middle': round(middle, 2),
            'lower': round(lower, 2),
            'width': round(width, 4),
        }
    
    def _determine_trend(self, prices: List[float], ma: Dict[str, float]) -> str:
        """判断趋势"""
        if not ma.get('ma20') or not ma.get('ma60'):
            return 'sideways'
        
        current = prices[-1]
        ma20 = ma['ma20']
        ma60 = ma['ma60']
        
        # 多头排列
        if current > ma20 > ma60:
            return 'up'
        # 空头排列
        elif current < ma20 < ma60:
            return 'down'
        # 震荡
        else:
            return 'sideways'
    
    def _calculate_score(self, rsi: float, macd: Dict, ma: Dict, trend: str, current_price: float) -> float:
        """计算综合得分"""
        score = 0.0
        
        # RSI 得分（30-70 为中性）
        if rsi < 30:
            score += 0.3  # 超卖，看多
        elif rsi > 70:
            score -= 0.3  # 超买，看空
        
        # MACD 得分
        macd_trend = macd.get('trend', 'neutral')
        if macd_trend == 'bullish':
            score += 0.3
        elif macd_trend == 'bearish':
            score -= 0.3
        
        # 趋势得分
        if trend == 'up':
            score += 0.2
        elif trend == 'down':
            score -= 0.2
        
        # 均线得分
        if ma.get('ma5', 0) > ma.get('ma10', 0):
            score += 0.1
        else:
            score -= 0.1
        
        # 限制在 -1 到 1 之间
        return max(-1.0, min(1.0, score))
    
    def _generate_signal(self, score: float, rsi: float, trend: str) -> str:
        """生成交易信号"""
        if score > 0.5:
            return 'buy'
        elif score < -0.5:
            return 'sell'
        else:
            return 'hold'
    
    def _ema(self, prices: List[float], period: int) -> float:
        """计算 EMA"""
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def _get_default_result(self) -> Dict[str, Any]:
        """返回默认结果"""
        return {
            'rsi': 50.0,
            'macd': {'macd': 0, 'signal': 0, 'histogram': 0, 'trend': 'neutral'},
            'ma': {},
            'bollinger': {'upper': 0, 'middle': 0, 'lower': 0, 'width': 0},
            'trend': 'sideways',
            'score': 0.0,
            'signal': 'hold',
        }
