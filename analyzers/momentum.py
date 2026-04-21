#!/usr/bin/env python3
"""
动量分析器 - 分析价格动量和资金流向

支持：
- 价格动量
- 成交量分析
- 资金流向
"""

import logging
from typing import Any, Dict, List, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.base import Analyzer, AnalyzerConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MomentumAnalyzer(Analyzer):
    """动量分析器"""
    
    def __init__(self):
        config = AnalyzerConfig(
            name='动量分析器',
            analyzer_type='momentum',
            enabled=True,
            weight=0.20,  # 动量分析权重 20%
            params={
                'momentum_periods': [5, 10, 20],  # 动量周期
            }
        )
        super().__init__(config)
    
    def analyze(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        执行动量分析
        
        Args:
            data: 价格和成交量数据
                {
                    'prices': List[float],  # 价格列表
                    'volumes': List[float],  # 成交量列表（可选）
                    'current_price': float,
                }
            
        Returns:
            Dict[str, Any]: {
                'momentum': Dict[str, float],  # 各周期动量
                'volume_trend': str,  # 成交量趋势
                'score': float,  # 综合得分
                'signal': str,  # buy/sell/hold
            }
        """
        logger.info("[动量分析] 开始分析...")
        
        prices = data.get('prices', [])
        volumes = data.get('volumes', [])
        current_price = data.get('current_price', 0)
        
        if len(prices) < 20:
            logger.warning(f"[动量分析] 数据不足（{len(prices)}条）")
            return self._get_default_result()
        
        # 计算价格动量
        momentum = self._calculate_momentum(prices)
        
        # 分析成交量趋势
        volume_trend = self._analyze_volume(volumes) if volumes else 'neutral'
        
        # 计算综合得分
        score = self._calculate_score(momentum, volume_trend)
        
        # 生成信号
        signal = self._generate_signal(score, momentum)
        
        result = {
            'momentum': momentum,
            'volume_trend': volume_trend,
            'score': round(score, 3),
            'signal': signal,
            'current_price': current_price,
        }
        
        logger.info(f"[动量分析] 5 日动量={momentum.get('mom_5d', 0):.2f}%, 得分={score:.3f}, 信号={signal}")
        return result
    
    def _calculate_momentum(self, prices: List[float]) -> Dict[str, float]:
        """计算价格动量"""
        momentum = {}
        
        for period in self.config.params['momentum_periods']:
            if len(prices) >= period:
                # 动量 = (当前价 - N 日前价) / N 日前价 * 100
                past_price = prices[-period]
                current = prices[-1]
                
                if past_price > 0:
                    mom = ((current - past_price) / past_price) * 100
                else:
                    mom = 0
                
                momentum[f'mom_{period}d'] = round(mom, 2)
            else:
                momentum[f'mom_{period}d'] = 0.0
        
        return momentum
    
    def _analyze_volume(self, volumes: List[float]) -> str:
        """分析成交量趋势"""
        if len(volumes) < 10:
            return 'neutral'
        
        # 比较最近 5 日和前 5 日的平均成交量
        recent_avg = sum(volumes[-5:]) / 5
        past_avg = sum(volumes[-10:-5]) / 5
        
        if past_avg == 0:
            return 'neutral'
        
        change = (recent_avg - past_avg) / past_avg
        
        if change > 0.2:
            return 'increasing'  # 放量
        elif change < -0.2:
            return 'decreasing'  # 缩量
        else:
            return 'neutral'
    
    def _calculate_score(self, momentum: Dict[str, float], volume_trend: str) -> float:
        """计算综合得分"""
        score = 0.0
        
        # 短期动量（5 日）
        mom_5d = momentum.get('mom_5d', 0)
        if mom_5d > 5:
            score += 0.3  # 强势上涨
        elif mom_5d < -5:
            score -= 0.3  # 强势下跌
        
        # 中期动量（10 日）
        mom_10d = momentum.get('mom_10d', 0)
        if mom_10d > 8:
            score += 0.2
        elif mom_10d < -8:
            score -= 0.2
        
        # 成交量
        if volume_trend == 'increasing':
            score += 0.1  # 放量上涨是好事
        elif volume_trend == 'decreasing':
            score -= 0.1
        
        return max(-1.0, min(1.0, score))
    
    def _generate_signal(self, score: float, momentum: Dict[str, float]) -> str:
        """生成交易信号"""
        if score > 0.5:
            return 'buy'
        elif score < -0.5:
            return 'sell'
        else:
            return 'hold'
    
    def is_momentum_strong(self, momentum: Dict[str, float]) -> bool:
        """判断动量是否强劲"""
        mom_5d = momentum.get('mom_5d', 0)
        mom_10d = momentum.get('mom_10d', 0)
        
        # 短期和中期动量同向且强劲
        return (mom_5d > 5 and mom_10d > 5) or (mom_5d < -5 and mom_10d < -5)
    
    def _get_default_result(self) -> Dict[str, Any]:
        """返回默认结果"""
        return {
            'momentum': {'mom_5d': 0, 'mom_10d': 0, 'mom_20d': 0},
            'volume_trend': 'neutral',
            'score': 0.0,
            'signal': 'hold',
        }
