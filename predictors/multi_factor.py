#!/usr/bin/env python3
"""
多因子预测器 - 综合技术、情绪、宏观、动量四维度预测
"""

import logging
from typing import Any, Dict, List, Optional
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from predictors.base import Predictor, PredictorConfig
from analyzers import (
    TechnicalAnalyzer,
    SentimentAnalyzer,
    MacroAnalyzer,
    MomentumAnalyzer,
)

# 导入时序预测器（新增）
try:
    from predictors.simple_ts_predictor import SimpleTimeSeriesPredictor
    TS_PREDICTOR_AVAILABLE = True
except ImportError:
    TS_PREDICTOR_AVAILABLE = False
    logger.warning("SimpleTimeSeriesPredictor 不可用")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiFactorPredictor(Predictor):
    """多因子预测器"""
    
    def __init__(self):
        config = PredictorConfig(
            name='多因子预测器',
            predictor_type='multi_factor',
            enabled=True,
            target_days=1,
            params={
                'weights': {
                    'technical': 0.30,
                    'sentiment': 0.25,
                    'macro': 0.25,
                    'momentum': 0.20,
                }
            }
        )
        super().__init__(config)
        
        # 初始化分析器
        self.technical = TechnicalAnalyzer()
        self.sentiment = SentimentAnalyzer()
        self.macro = MacroAnalyzer()
        self.momentum = MomentumAnalyzer()
        
        # 时序预测器（新增）
        if TS_PREDICTOR_AVAILABLE:
            self.ts_predictor = SimpleTimeSeriesPredictor()
            logger.debug("[多因子预测] 时序预测器已初始化")
        else:
            self.ts_predictor = None
    
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行多因子预测
        
        Args:
            data: 完整数据包
                {
                    'gold': {...},  # 金价数据
                    'news': {...},  # 新闻数据
                    'macro': {...},  # 宏观数据
                    'prices': [...],  # 历史价格
                }
            
        Returns:
            Dict[str, Any]: 预测结果
        """
        logger.info("[多因子预测] 开始预测...")
        
        # 1. 时序预测（新增）
        ts_prediction = None
        if self.ts_predictor:
            prices = data.get('prices', [])
            if len(prices) >= 10:
                if self.ts_predictor.train(prices):
                    ts_prediction = self.ts_predictor.predict(days=1)
                    logger.info(f"[多因子预测] 时序预测：¥{ts_prediction['predicted_price']:.2f}")
        
        # 2. 执行各维度分析
        tech_analysis = self._run_technical_analysis(data)
        sent_analysis = self._run_sentiment_analysis(data)
        macro_analysis = self._run_macro_analysis(data)
        mom_analysis = self._run_momentum_analysis(data)
        
        # 3. 提取各维度得分
        scores = {
            'technical': tech_analysis.get('score', 0),
            'sentiment': sent_analysis.get('score', 0),
            'macro': macro_analysis.get('score', 0),
            'momentum': mom_analysis.get('score', 0),
        }
        
        # 4. 加权计算综合得分
        weights = self.config.params['weights']
        composite_score = sum(scores[k] * weights[k] for k in scores)
        
        # 5. 结合时序预测（新增）
        if ts_prediction:
            # 时序预测作为第 5 个因子，权重 15%
            ts_score = 1 if ts_prediction['trend'] == 'up' else (-1 if ts_prediction['trend'] == 'down' else 0)
            composite_score = composite_score * 0.85 + ts_score * 0.15
        
        # 6. 生成预测
        current_price = data.get('gold', {}).get('domestic', {}).get('price', 0)
        prediction = self._generate_prediction(current_price, composite_score, scores)
        
        # 7. 添加时序预测信息（新增）
        if ts_prediction:
            prediction['time_series'] = ts_prediction
        
        # 8. 添加分析详情
        prediction['analysis'] = {
            'technical': tech_analysis,
            'sentiment': sent_analysis,
            'macro': macro_analysis,
            'momentum': mom_analysis,
            'scores': scores,
            'weights': weights,
        }
        
        logger.info(f"[多因子预测] 综合得分={composite_score:.3f}, 预测方向={prediction['direction']}")
        return prediction
    
    def _run_technical_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """运行技术分析"""
        gold = data.get('gold', {})
        prices = data.get('prices', [])
        
        # 准备技术分析数据
        tech_data = {
            'prices': prices,
            'current_price': gold.get('domestic', {}).get('price', 0),
        }
        
        return self.technical.analyze(tech_data)
    
    def _run_sentiment_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """运行情绪分析"""
        news = data.get('news', {})
        macro = data.get('macro', {})
        
        sent_data = {
            'news': news.get('news', []),
            'vix': macro.get('vix', {}).get('value', 0),
        }
        
        return self.sentiment.analyze(sent_data)
    
    def _run_macro_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """运行宏观分析"""
        macro = data.get('macro', {})
        
        return self.macro.analyze(macro)
    
    def _run_momentum_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """运行动量分析"""
        prices = data.get('prices', [])
        gold = data.get('gold', {})
        
        mom_data = {
            'prices': prices,
            'current_price': gold.get('domestic', {}).get('price', 0),
        }
        
        return self.momentum.analyze(mom_data)
    
    def _generate_prediction(self, current_price: float, composite_score: float, 
                            scores: Dict[str, float]) -> Dict[str, Any]:
        """生成预测"""
        # 判断方向（取消震荡，只保留上涨/下跌）
        if composite_score > 0:
            direction = 'up'
            direction_label = '看涨'
        else:
            direction = 'down'
            direction_label = '看跌'
        
        # 计算预测价格（基于当前价格和得分）
        price_change_pct = composite_score * 2  # 得分转换为涨跌幅百分比
        predicted_price = current_price * (1 + price_change_pct / 100)
        
        # 计算预测区间（基于波动率，缩小到±1%）
        volatility = 0.01  # 固定为 1%，更精确的区间
        price_range = self.get_prediction_range(predicted_price, volatility)
        
        # 计算置信度
        # 各因子一致性越高，置信度越高
        score_values = list(scores.values())
        score_std = (max(score_values) - min(score_values)) / 2
        confidence_score = 1 - score_std  # 标准差越小，置信度越高
        confidence = self.get_confidence_label(confidence_score)
        
        # 生成交易信号
        if composite_score > 0.5:
            signal = 'buy'
            signal_label = '买入'
        elif composite_score < -0.5:
            signal = 'sell'
            signal_label = '卖出'
        else:
            signal = 'hold'
            signal_label = '持有'
        
        prediction = {
            'current_price': round(current_price, 2),
            'predicted_price': round(predicted_price, 2),
            'price_lower': price_range['lower'],
            'price_upper': price_range['upper'],
            'direction': direction,
            'direction_label': direction_label,
            'change_pct': round(price_change_pct, 2),
            'signal': signal,
            'signal_label': signal_label,
            'confidence': confidence,
            'confidence_score': round(confidence_score, 3),
            'composite_score': round(composite_score, 3),
            'prediction_date': datetime.now().strftime('%Y-%m-%d'),
            'target_date': (datetime.now() + timedelta(days=self.config.target_days)).strftime('%Y-%m-%d'),
        }
        
        return prediction
    
    def get_factor_contribution(self, scores: Dict[str, float], 
                               weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        获取各因子贡献度
        
        Returns:
            List[Dict]: 因子贡献列表
        """
        contributions = []
        
        for factor, score in scores.items():
            weight = weights.get(factor, 0)
            contribution = score * weight
            
            contributions.append({
                'factor': factor,
                'score': round(score, 3),
                'weight': round(weight, 3),
                'contribution': round(contribution, 3),
                'bias': 'bullish' if score > 0 else ('bearish' if score < 0 else 'neutral'),
            })
        
        # 按贡献度排序
        contributions.sort(key=lambda x: abs(x['contribution']), reverse=True)
        
        return contributions
