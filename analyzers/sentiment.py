#!/usr/bin/env python3
"""
情绪分析器 - 分析市场情绪

支持：
- 新闻情绪分析
- 市场恐慌/贪婪指数
- 社交媒体情绪
"""

import logging
from typing import Any, Dict, List, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.base import Analyzer, AnalyzerConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer(Analyzer):
    """情绪分析器"""
    
    def __init__(self):
        config = AnalyzerConfig(
            name='情绪分析器',
            analyzer_type='sentiment',
            enabled=True,
            weight=0.25,  # 情绪分析权重 25%
            params={
                'positive_keywords': ['上涨', '利好', '增长', '突破', '创新高', '复苏', '回暖', '牛市'],
                'negative_keywords': ['下跌', '利空', '下滑', '暴跌', '风险', '衰退', '亏损', '熊市'],
            }
        )
        super().__init__(config)
    
    def analyze(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        执行情绪分析
        
        Args:
            data: 情绪相关数据
                {
                    'news': List[Dict],  # 新闻列表
                    'vix': float,  # VIX 指数（可选）
                }
            
        Returns:
            Dict[str, Any]: {
                'news_sentiment': float,  # 新闻情绪得分（-1 到 1）
                'market_sentiment': str,  # 市场情绪（risk_on/risk_off/neutral）
                'score': float,  # 综合得分（-1 到 1）
                'signal': str,  # buy/sell/hold
            }
        """
        logger.info("[情绪分析] 开始分析...")
        
        news_list = data.get('news', [])
        vix = data.get('vix', 0)
        
        # 分析新闻情绪
        news_sentiment = self._analyze_news_sentiment(news_list)
        
        # 分析 VIX 情绪
        vix_sentiment = self._analyze_vix(vix)
        
        # 综合情绪得分
        score = (news_sentiment + vix_sentiment) / 2
        
        # 判断市场情绪
        if score > 0.3:
            market_sentiment = 'risk_on'
        elif score < -0.3:
            market_sentiment = 'risk_off'
        else:
            market_sentiment = 'neutral'
        
        # 生成信号
        signal = self._generate_signal(score)
        
        result = {
            'news_sentiment': round(news_sentiment, 3),
            'vix_sentiment': round(vix_sentiment, 3),
            'market_sentiment': market_sentiment,
            'score': round(score, 3),
            'signal': signal,
            'news_count': len(news_list),
        }
        
        logger.info(f"[情绪分析] 新闻情绪={news_sentiment:.3f}, VIX 情绪={vix_sentiment:.3f}, 综合={score:.3f}")
        return result
    
    def _analyze_news_sentiment(self, news_list: List[Dict]) -> float:
        """分析新闻情绪"""
        if not news_list:
            return 0.0
        
        positive_count = 0
        negative_count = 0
        
        positive_keywords = self.config.params['positive_keywords']
        negative_keywords = self.config.params['negative_keywords']
        
        for news in news_list:
            title = news.get('title', '').lower()
            content = news.get('content', '').lower()
            text = title + ' ' + content
            
            has_positive = any(kw in text for kw in positive_keywords)
            has_negative = any(kw in text for kw in negative_keywords)
            
            if has_positive and not has_negative:
                positive_count += 1
            elif has_negative and not has_positive:
                negative_count += 1
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        # 计算情绪得分
        score = (positive_count - negative_count) / total
        return score
    
    def _analyze_vix(self, vix: float) -> float:
        """分析 VIX 情绪"""
        if vix <= 0:
            return 0.0
        
        # VIX 越低越乐观
        if vix < 15:
            return 0.5  # 低恐慌，乐观
        elif vix < 20:
            return 0.2  # 正常
        elif vix < 30:
            return -0.2  # 偏高
        else:
            return -0.5  # 高恐慌，悲观
    
    def _generate_signal(self, score: float) -> str:
        """生成交易信号"""
        if score > 0.5:
            return 'buy'  # 情绪乐观，买入
        elif score < -0.5:
            return 'sell'  # 情绪悲观，卖出
        else:
            return 'hold'
    
    def get_sentiment_label(self, score: float) -> str:
        """获取情绪标签"""
        if score > 0.5:
            return '极度乐观'
        elif score > 0.2:
            return '乐观'
        elif score > -0.2:
            return '中性'
        elif score > -0.5:
            return '悲观'
        else:
            return '极度悲观'
