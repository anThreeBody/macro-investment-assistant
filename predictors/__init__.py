"""
预测器模块 - 多因子预测引擎

职责：
- 多因子加权预测
- Prophet 时序预测
- 机器学习预测（LightGBM）
- 预测验证与优化
"""

from .base import Predictor, PredictorConfig
from .multi_factor import MultiFactorPredictor

__all__ = [
    'Predictor',
    'PredictorConfig',
    'MultiFactorPredictor',
]

__version__ = '1.0.0'
