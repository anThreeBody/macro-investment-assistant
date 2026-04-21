#!/usr/bin/env python3
"""
分析器基类 - 定义所有分析器的标准接口
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AnalyzerConfig:
    """分析器配置"""
    name: str                          # 分析器名称
    analyzer_type: str                 # 分析器类型：technical/sentiment/macro/momentum
    enabled: bool = True               # 是否启用
    weight: float = 0.25              # 权重（用于多因子综合）
    params: Dict[str, Any] = field(default_factory=dict)  # 分析参数


class Analyzer(ABC):
    """分析器基类"""
    
    def __init__(self, config: AnalyzerConfig):
        self.config = config
    
    @abstractmethod
    def analyze(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        执行分析（抽象方法，子类必须实现）
        
        Args:
            data: 输入数据
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        pass
    
    def get_signal(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据分析结果生成交易信号
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            Dict[str, Any]: 交易信号 {signal: 'buy'/'sell'/'hold', strength: float}
        """
        # 默认实现，子类可重写
        return {
            'signal': 'hold',
            'strength': 0.0,
            'reason': '默认持有',
        }
    
    def get_score(self, analysis_result: Dict[str, Any]) -> float:
        """
        计算分析得分（-1 到 1）
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            float: 得分（-1=强烈看空，1=强烈看多）
        """
        # 默认实现，子类可重写
        return 0.0
    
    def validate_result(self, result: Dict[str, Any]) -> bool:
        """验证分析结果有效性"""
        if not result:
            return False
        
        # 检查必需字段
        required = ['score', 'signal']
        for field in required:
            if field not in result:
                logger.warning(f"[{self.config.name}] 分析结果缺少字段：{field}")
                return False
        
        return True
