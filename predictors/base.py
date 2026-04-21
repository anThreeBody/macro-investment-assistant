#!/usr/bin/env python3
"""
预测器基类
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PredictorConfig:
    """预测器配置"""
    name: str                          # 预测器名称
    predictor_type: str                # 预测器类型
    enabled: bool = True
    target_days: int = 1              # 预测目标天数
    params: Dict[str, Any] = field(default_factory=dict)


class Predictor(ABC):
    """预测器基类"""
    
    def __init__(self, config: PredictorConfig):
        self.config = config
    
    @abstractmethod
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行预测（抽象方法）
        
        Args:
            data: 输入数据
            
        Returns:
            Dict[str, Any]: 预测结果
        """
        pass
    
    def get_prediction_range(self, current_price: float, volatility: float = 0.01) -> Dict[str, float]:
        """
        计算预测区间
        
        Args:
            current_price: 当前价格
            volatility: 波动率（默认 1%，更精确的区间）
            
        Returns:
            Dict[str, float]: {lower, upper}
        """
        lower = current_price * (1 - volatility)
        upper = current_price * (1 + volatility)
        
        return {
            'lower': round(lower, 2),
            'upper': round(upper, 2),
        }
    
    def get_confidence_label(self, score: float) -> str:
        """
        获取置信度标签
        
        Args:
            score: 置信度得分（0-1）
            
        Returns:
            str: 高/中/低
        """
        if score >= 0.7:
            return '高'
        elif score >= 0.4:
            return '中'
        else:
            return '低'
    
    def format_prediction(self, result: Dict[str, Any]) -> str:
        """格式化预测结果（用于输出）"""
        lines = [
            f"📊 {self.config.name} 预测结果",
            f"  预测周期：{self.config.target_days}天",
            f"  当前价格：{result.get('current_price', 'N/A')}",
            f"  预测价格：{result.get('predicted_price', 'N/A')}",
            f"  预测区间：{result.get('price_lower', 'N/A')} - {result.get('price_upper', 'N/A')}",
            f"  预测方向：{result.get('direction', 'N/A')}",
            f"  置信度：{result.get('confidence', 'N/A')}",
        ]
        return '\n'.join(lines)
