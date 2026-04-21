#!/usr/bin/env python3
"""
宏观分析器 - 分析宏观经济数据

支持：
- 美元指数分析
- 美联储政策分析
- 全球经济形势
"""

import logging
from typing import Any, Dict, List, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.base import Analyzer, AnalyzerConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MacroAnalyzer(Analyzer):
    """宏观分析器"""
    
    def __init__(self):
        config = AnalyzerConfig(
            name='宏观分析器',
            analyzer_type='macro',
            enabled=True,
            weight=0.25,  # 宏观分析权重 25%
            params={
                'dxy_bullish': 105,  # DXY 高于此值看多美元
                'dxy_bearish': 95,   # DXY 低于此值看空美元
            }
        )
        super().__init__(config)
    
    def analyze(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        执行宏观分析
        
        Args:
            data: 宏观数据
                {
                    'dxy': float,  # 美元指数
                    'vix': float,  # VIX 指数
                    'oil': float,  # 原油价格
                    'treasury_10y': float,  # 10 年期美债收益率
                }
            
        Returns:
            Dict[str, Any]: {
                'dxy_signal': str,  # 美元信号
                'risk_environment': str,  # 风险环境
                'score': float,  # 综合得分
                'signal': str,  # buy/sell/hold
            }
        """
        logger.info("[宏观分析] 开始分析...")
        
        dxy = data.get('dxy', {}).get('value', 0)
        vix = data.get('vix', {}).get('value', 0)
        oil = data.get('oil', {}).get('value', 0)
        treasury_10y = data.get('treasury', {}).get('10y', {}).get('value', 0)
        
        # 分析美元
        dxy_signal = self._analyze_dxy(dxy)
        
        # 分析风险环境
        risk_environment = self._analyze_risk_environment(vix, dxy)
        
        # 分析美债
        treasury_signal = self._analyze_treasury(treasury_10y)
        
        # 综合得分
        score = self._calculate_score(dxy_signal, risk_environment, treasury_signal)
        
        # 生成信号
        signal = self._generate_signal(score, risk_environment)
        
        result = {
            'dxy': dxy,
            'dxy_signal': dxy_signal,
            'vix': vix,
            'risk_environment': risk_environment,
            'treasury_10y': treasury_10y,
            'treasury_signal': treasury_signal,
            'score': round(score, 3),
            'signal': signal,
        }
        
        logger.info(f"[宏观分析] DXY={dxy}, 风险环境={risk_environment}, 得分={score:.3f}")
        return result
    
    def _analyze_dxy(self, dxy: float) -> str:
        """分析美元指数"""
        if dxy <= 0:
            return 'neutral'
        
        if dxy > self.config.params['dxy_bullish']:
            return 'bullish'  # 美元强势
        elif dxy < self.config.params['dxy_bearish']:
            return 'bearish'  # 美元弱势
        else:
            return 'neutral'
    
    def _analyze_risk_environment(self, vix: float, dxy: float) -> str:
        """分析风险环境"""
        if vix <= 0:
            return 'neutral'
        
        # VIX 低 + 美元稳定 = risk_on
        if vix < 20 and 95 < dxy < 105:
            return 'risk_on'
        # VIX 高 = risk_off
        elif vix > 30:
            return 'risk_off'
        else:
            return 'neutral'
    
    def _analyze_treasury(self, treasury_10y: float) -> str:
        """分析美债收益率"""
        if treasury_10y <= 0:
            return 'neutral'
        
        # 收益率过高可能预示经济衰退
        if treasury_10y > 5:
            return 'bearish'
        elif treasury_10y < 3:
            return 'bullish'
        else:
            return 'neutral'
    
    def _calculate_score(self, dxy_signal: str, risk_env: str, treasury_signal: str) -> float:
        """计算综合得分"""
        score = 0.0
        
        # DXY 得分
        if dxy_signal == 'bullish':
            score += 0.2  # 美元强势，利好美元资产
        elif dxy_signal == 'bearish':
            score -= 0.2
        
        # 风险环境得分
        if risk_env == 'risk_on':
            score += 0.3  # 风险偏好上升，利好风险资产
        elif risk_env == 'risk_off':
            score -= 0.3  # 风险偏好下降，利好避险资产
        
        # 美债得分
        if treasury_signal == 'bullish':
            score += 0.2
        elif treasury_signal == 'bearish':
            score -= 0.2
        
        return max(-1.0, min(1.0, score))
    
    def _generate_signal(self, score: float, risk_environment: str) -> str:
        """生成交易信号"""
        # 根据风险环境调整信号
        if risk_environment == 'risk_off':
            # 避险环境，利好黄金等避险资产
            if score < -0.3:
                return 'buy'  # 买入避险资产
            elif score > 0.3:
                return 'sell'
        elif risk_environment == 'risk_on':
            # 风险环境，利好股票等风险资产
            if score > 0.3:
                return 'buy'
            elif score < -0.3:
                return 'sell'
        
        return 'hold'
    
    def get_gold_bias(self, risk_environment: str, dxy_signal: str) -> str:
        """
        获取黄金偏向
        
        黄金通常在以下情况上涨：
        - risk_off（避险需求）
        - 美元弱势
        """
        if risk_environment == 'risk_off':
            return 'bullish'  # 避险需求
        elif dxy_signal == 'bearish':
            return 'bullish'  # 美元弱势利好黄金
        elif risk_environment == 'risk_on' and dxy_signal == 'bullish':
            return 'bearish'  # 风险偏好 + 美元强势利空黄金
        else:
            return 'neutral'
