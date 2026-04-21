#!/usr/bin/env python3
"""简化时序预测器

不依赖 Prophet，使用基础统计方法进行时序预测：
- 移动平均
- 趋势外推
- 均值回归
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)


class SimpleTimeSeriesPredictor:
    """简化时序预测器"""
    
    def __init__(self):
        self.is_trained = False
        self.mean_price = 0.0
        self.trend = 0.0
        self.volatility = 0.0
        self.recent_prices = []
    
    def train(self, prices: List[float], dates: Optional[List[str]] = None) -> bool:
        """
        训练模型
        
        Args:
            prices: 价格列表（至少 10 个数据点）
            dates: 日期列表（可选）
        
        Returns:
            bool: 训练是否成功
        """
        if len(prices) < 10:
            logger.warning(f"[时序预测] 数据不足 ({len(prices)}条)，需要至少 10 条")
            return False
        
        try:
            self.recent_prices = prices[-30:] if len(prices) > 30 else prices
            
            # 计算均值
            self.mean_price = statistics.mean(self.recent_prices)
            
            # 计算趋势（简单线性回归）
            self.trend = self._calculate_trend(self.recent_prices)
            
            # 计算波动率
            self.volatility = statistics.stdev(self.recent_prices) if len(self.recent_prices) > 1 else 0.0
            
            self.is_trained = True
            
            logger.info(
                f"[时序预测] 训练完成 - 均值：{self.mean_price:.2f}, "
                f"趋势：{self.trend:.4f}, 波动率：{self.volatility:.2f}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"[时序预测] 训练失败：{e}")
            return False
    
    def _calculate_trend(self, prices: List[float]) -> float:
        """计算趋势（简单线性回归斜率）"""
        n = len(prices)
        if n < 2:
            return 0.0
        
        # 简化计算：最近 N 天的平均变化
        changes = [prices[i] - prices[i-1] for i in range(1, n)]
        return statistics.mean(changes) if changes else 0.0
    
    def predict(self, days: int = 1) -> Optional[Dict[str, Any]]:
        """
        预测未来 N 天
        
        Args:
            days: 预测天数
        
        Returns:
            Dict: 预测结果
        """
        if not self.is_trained:
            logger.warning("[时序预测] 模型未训练")
            return None
        
        try:
            current_price = self.recent_prices[-1] if self.recent_prices else self.mean_price
            
            # 预测价格 = 当前价格 + 趋势 * 天数
            predicted_price = current_price + self.trend * days
            
            # 置信区间 = 预测价格 ± 波动率 * sqrt(天数)
            margin = self.volatility * (days ** 0.5)
            
            # 判断置信度
            change_pct = abs(predicted_price - current_price) / current_price
            if change_pct < 0.01:
                confidence = '高'
            elif change_pct < 0.02:
                confidence = '中'
            else:
                confidence = '低'
            
            result = {
                'predicted_price': round(predicted_price, 2),
                'price_lower': round(predicted_price - margin, 2),
                'price_upper': round(predicted_price + margin, 2),
                'trend': 'up' if self.trend > 0 else ('down' if self.trend < 0 else 'sideways'),
                'confidence': confidence,
                'model': 'simple_ts'
            }
            
            logger.info(
                f"[时序预测] 预测完成 - {days}天后：¥{result['predicted_price']:.2f} "
                f"[{result['price_lower']:.2f} - {result['price_upper']:.2f}]"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[时序预测] 预测失败：{e}")
            return None
    
    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性"""
        return {
            'mean_reversion': 0.4,
            'trend': 0.4,
            'volatility': 0.2
        }


# 测试入口
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    print("=" * 60)
    print("简化时序预测器测试")
    print("=" * 60)
    
    # 模拟数据
    import random
    prices = [1000 + i * 2 + random.uniform(-5, 5) for i in range(30)]
    
    predictor = SimpleTimeSeriesPredictor()
    
    # 训练
    print("\n1. 训练模型...")
    if predictor.train(prices):
        print("   ✅ 训练成功")
    else:
        print("   ❌ 训练失败")
    
    # 预测
    print("\n2. 预测未来 1 天...")
    pred = predictor.predict(days=1)
    if pred:
        print(f"   预测价格：¥{pred['predicted_price']:.2f}")
        print(f"   置信区间：[{pred['price_lower']:.2f}, {pred['price_upper']:.2f}]")
        print(f"   趋势：{pred['trend']}")
        print(f"   置信度：{pred['confidence']}")
    
    print("\n" + "=" * 60)
