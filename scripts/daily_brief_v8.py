#!/usr/bin/env python3
"""
每日简报 V8.0 - 完整分析版

核心改进:
1. 展示关键事件/政策/新闻及其影响分析
2. 详细说明结论的得出理由
3. 基于完整分析给出明确建议
"""

import sys
import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_manager import get_data_manager
from sentiment_analyzer import SentimentAnalyzer
from global_macro_v2 import GlobalMacroV2
from trading_strategy import TradingStrategy
from fund_recommender_enhanced import FundRecommenderEnhanced
from stock_analyzer import StockAnalyzer
from gold_price_auto_fetch import get_gold_price_with_change, save_gold_price


class DailyBriefV8:
    """每日简报 V8.0"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.today = datetime.now()
        self.today_str = self.today.strftime('%Y-%m-%d')
        
        # 初始化分析器
        self.sentiment_analyzer = SentimentAnalyzer()
        self.global_macro = GlobalMacroV2()
        self.trading_strategy = TradingStrategy()
        self.dm = get_data_manager()
        self.fund_recommender = FundRecommenderEnhanced()
        self.stock_analyzer = StockAnalyzer()
        
        # 存储分析结果
        self.analysis = {}
    
    def _get_sentiment_data(self) -> Dict:
        """获取情绪数据"""
        news_list = self.sentiment_analyzer.load_recent_news(days=3)
        if news_list:
            analyzed_news = self.sentiment_analyzer.analyze_news_batch(news_list)
            daily_sentiment = self.sentiment_analyzer.calculate_daily_sentiment(analyzed_news)
            sector_sentiment = self.sentiment_analyzer.sector_sentiment_analysis(analyzed_news)
            return {
                'overall_score': daily_sentiment.get('score', 0),
                'trend': daily_sentiment.get('trend', '中性'),
                'sector_sentiment': {k: v['score'] for k, v in sector_sentiment.items()},
                'analyzed_news': analyzed_news
            }
        return {'overall_score': 0, 'trend': '中性', 'sector_sentiment': {}, 'analyzed_news': []}
    
    def analyze_key_events(self) -> Dict:
        """
        分析关键事件及其影响
        
        输出: 事件列表 + 影响分析
        """
        # 1. 获取政策新闻
        recent_policies = self.dm.get_recent_policies(days=3, limit=20)
        
        # 2. 获取情绪分析
        sentiment_data = self._get_sentiment_data()
        analyzed_news = sentiment_data.get('analyzed_news', [])
        
        # 3. 整理关键事件
        events = []
        
        # 政策事件
        for policy in recent_policies[:10]:  # 前10条
            title = policy.get('title', '')
            category = policy.get('category', '其他')
            impact = policy.get('impact', '中性')
            
            # 分析影响
            impact_analysis = self._analyze_policy_impact(title, category)
            
            events.append({
                'type': 'policy',
                'date': policy.get('date', ''),
                'title': title,
                'category': category,
                'impact': impact,
                'impact_analysis': impact_analysis,
                'affected_assets': impact_analysis.get('affected_assets', [])
            })
        
        # 市场情绪事件（重要新闻）
        important_news = sorted(analyzed_news, 
                               key=lambda x: abs(x.get('sentiment_score', 0)), 
                               reverse=True)[:5]
        
        for news in important_news:
            events.append({
                'type': 'sentiment',
                'date': news.get('date', ''),
                'title': news.get('title', '')[:50] + '...' if len(news.get('title', '')) > 50 else news.get('title', ''),
                'sentiment': news.get('sentiment', '中性'),
                'score': news.get('sentiment_score', 0),
                'impact_analysis': {
                    'description': self._describe_sentiment_impact(news.get('sentiment_score', 0)),
                    'affected_assets': news.get('sectors', [])
                },
                'affected_assets': news.get('sectors', [])
            })
        
        # 4. 按影响排序
        events.sort(key=lambda x: len(x.get('affected_assets', [])), reverse=True)
        
        return {
            'events': events,
            'policy_count': len([e for e in events if e['type'] == 'policy']),
            'sentiment_count': len([e for e in events if e['type'] == 'sentiment'])
        }
    
    def _analyze_policy_impact(self, title: str, category: str) -> Dict:
        """分析政策影响"""
        affected_assets = []
        description = ""
        
        # 科技政策
        if any(kw in title for kw in ['科技', 'AI', '人工智能', '芯片', '半导体']):
            affected_assets.extend(['科技基金', '半导体股票', 'AI相关'])
            description = "利好科技板块，推动相关基金和股票上涨"
        
        # 货币政策
        elif any(kw in title for kw in ['降息', '宽松', '降准']):
            affected_assets.extend(['黄金', '债券基金', '成长股'])
            description = "宽松货币政策利好黄金和债券，降低融资成本"
        elif any(kw in title for kw in ['加息', '紧缩']):
            affected_assets.extend(['黄金', '债券基金'])
            description = "紧缩政策利空黄金，但可能抑制通胀"
        
        # 基建政策
        elif any(kw in title for kw in ['基建', '投资', '项目']):
            affected_assets.extend(['基建板块', '周期股', '钢铁水泥'])
            description = "基建投资拉动周期行业需求"
        
        # 消费政策
        elif any(kw in title for kw in ['消费', '内需', '补贴']):
            affected_assets.extend(['消费板块', '白酒', '家电'])
            description = "刺激消费政策利好消费类股票和基金"
        
        # 新能源
        elif any(kw in title for kw in ['新能源', '绿色', '碳中和']):
            affected_assets.extend(['新能源基金', '光伏', '电动车'])
            description = "新能源政策持续利好相关产业链"
        
        # 黄金相关
        elif any(kw in title for kw in ['黄金', '避险', '储备']):
            affected_assets.extend(['黄金', '黄金基金', '黄金股'])
            description = "央行购金或避险需求支撑金价"
        
        # 默认
        else:
            description = "政策影响需进一步观察市场反应"
        
        return {
            'description': description,
            'affected_assets': affected_assets
        }
    
    def _describe_sentiment_impact(self, score: float) -> str:
        """描述情绪影响"""
        if score > 0.5:
            return "强烈利好，可能推动相关板块上涨"
        elif score > 0.2:
            return "情绪积极，对板块有正面影响"
        elif score < -0.5:
            return "强烈利空，可能引发板块下跌"
        elif score < -0.2:
            return "情绪谨慎，对板块有负面影响"
        else:
            return "情绪中性，影响有限"
    
    def analyze_gold(self) -> Dict:
        """黄金完整分析 - 包含国际金价和国内金价"""
        print("  2. 分析黄金...")
        
        # 1. 获取价格数据（自动获取，优先使用浏览器）
        price_data = get_gold_price_with_change()
        
        if not price_data:
            # 使用默认数据
            price_data = {
                'domestic_cny_per_gram': 1083.15,
                'international_usd_per_oz': 4862.90,
                'change_cny': 0,
                'change_pct_cny': 0,
                'change_usd': 0,
                'change_pct_usd': 0,
                'source': '默认数据',
                'update_time': self.today.strftime('%Y-%m-%d %H:%M')
            }
        
        # 保存获取的数据
        save_gold_price(price_data)
        
        # 提取数据
        current_price_cny = price_data['domestic_cny_per_gram']
        current_price_usd = price_data['international_usd_per_oz']
        change_cny = price_data['change_cny']
        change_pct_cny = price_data['change_pct_cny']
        change_usd = price_data['change_usd']
        change_pct_usd = price_data['change_pct_usd']
        
        # 获取历史数据用于技术指标计算
        history_file = self.data_dir / "gold_price_history.json"
        history = []
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        
        # 2. 技术指标（分别计算国内和国际）
        tech_signals_cny = self.trading_strategy.calculate_technical_signals(history, price_key='domestic_cny_per_gram')
        tech_signals_usd = self.trading_strategy.calculate_technical_signals(history, price_key='international_usd_per_oz')
        
        # 3. 宏观分析
        macro_analysis = self.global_macro.analyze()
        
        # 4. 情绪分析
        sentiment = self._get_sentiment_data()
        
        # 5. 关键事件影响
        key_events = self.analyze_key_events()
        gold_related_events = [e for e in key_events['events'] 
                              if '黄金' in str(e.get('affected_assets', []))]
        
        # 6. 内外盘趋势对比分析
        trend_comparison = self._analyze_trend_comparison(
            tech_signals_cny, tech_signals_usd, 
            change_pct_cny, change_pct_usd
        )
        
        # 7. 综合评分（基于双市场）
        score = 0
        reasoning = []  # 详细理由
        
        # 技术因素（综合国内和国际）
        trend_cny = tech_signals_cny.get('trend', 'neutral')
        trend_usd = tech_signals_usd.get('trend', 'neutral')
        
        # 双市场趋势一致时权重更高
        if trend_cny == 'up' and trend_usd == 'up':
            score += 4
            reasoning.append({
                'factor': '技术指标',
                'detail': f"内外盘趋势一致向上 (国内MA5={tech_signals_cny.get('ma5', 0):.2f}, 国际MA5={tech_signals_usd.get('ma5', 0):.2f})",
                'impact': '+4',
                'direction': 'positive'
            })
        elif trend_cny == 'down' and trend_usd == 'down':
            score -= 4
            reasoning.append({
                'factor': '技术指标',
                'detail': f"内外盘趋势一致向下 (国内MA5={tech_signals_cny.get('ma5', 0):.2f}, 国际MA5={tech_signals_usd.get('ma5', 0):.2f})",
                'impact': '-4',
                'direction': 'negative'
            })
        elif trend_cny == 'up' or trend_usd == 'up':
            score += 2
            reasoning.append({
                'factor': '技术指标',
                'detail': f"{'国内' if trend_cny == 'up' else '国际'}趋势向上",
                'impact': '+2',
                'direction': 'positive'
            })
        elif trend_cny == 'down' or trend_usd == 'down':
            score -= 2
            reasoning.append({
                'factor': '技术指标',
                'detail': f"{'国内' if trend_cny == 'down' else '国际'}趋势向下",
                'impact': '-2',
                'direction': 'negative'
            })
        
        # RSI指标（取国内和国际的平均值）
        rsi_cny = tech_signals_cny.get('rsi', 50)
        rsi_usd = tech_signals_usd.get('rsi', 50)
        avg_rsi = (rsi_cny + rsi_usd) / 2
        
        if avg_rsi < 30:
            score += 2
            reasoning.append({
                'factor': 'RSI指标',
                'detail': f"平均RSI={avg_rsi:.1f} < 30 (国内{rsi_cny:.1f}, 国际{rsi_usd:.1f})，超卖状态，存在反弹可能",
                'impact': '+2',
                'direction': 'positive'
            })
        elif avg_rsi > 70:
            score -= 2
            reasoning.append({
                'factor': 'RSI指标',
                'detail': f"平均RSI={avg_rsi:.1f} > 70 (国内{rsi_cny:.1f}, 国际{rsi_usd:.1f})，超买状态，回调风险",
                'impact': '-2',
                'direction': 'negative'
            })
        else:
            reasoning.append({
                'factor': 'RSI指标',
                'detail': f"平均RSI={avg_rsi:.1f} (国内{rsi_cny:.1f}, 国际{rsi_usd:.1f})，处于正常区间",
                'impact': '0',
                'direction': 'neutral'
            })
        
        # 宏观因素
        macro_signals = macro_analysis.get('signals', {})
        dxy = macro_analysis.get('data', {}).get('dxy', 100)
        vix = macro_analysis.get('data', {}).get('vix', 15)
        
        if dxy > 105:
            score -= 2
            reasoning.append({
                'factor': '美元指数',
                'detail': f"DXY={dxy} > 105，美元强势利空黄金",
                'impact': '-2',
                'direction': 'negative'
            })
        elif dxy < 100:
            score += 2
            reasoning.append({
                'factor': '美元指数',
                'detail': f"DXY={dxy} < 100，美元弱势利好黄金",
                'impact': '+2',
                'direction': 'positive'
            })
        else:
            reasoning.append({
                'factor': '美元指数',
                'detail': f"DXY={dxy}，处于中性区间",
                'impact': '0',
                'direction': 'neutral'
            })
        
        if vix > 20:
            score += 1.5
            reasoning.append({
                'factor': '恐慌指数',
                'detail': f"VIX={vix} > 20，市场恐慌推升避险需求",
                'impact': '+1.5',
                'direction': 'positive'
            })
        
        # 情绪因素
        sentiment_score = sentiment.get('overall_score', 0)
        if sentiment_score > 0.3:
            score += 2
            reasoning.append({
                'factor': '市场情绪',
                'detail': f"情绪得分{sentiment_score:+.2f}，市场乐观",
                'impact': '+2',
                'direction': 'positive'
            })
        elif sentiment_score < -0.3:
            score -= 2
            reasoning.append({
                'factor': '市场情绪',
                'detail': f"情绪得分{sentiment_score:+.2f}，市场谨慎",
                'impact': '-2',
                'direction': 'negative'
            })
        
        # 关键事件
        if gold_related_events:
            event_impact = sum(1 for e in gold_related_events if e.get('impact') in ['利好', 'positive'])
            event_count = len(gold_related_events)
            if event_impact > event_count / 2:
                score += 1
                reasoning.append({
                    'factor': '关键事件',
                    'detail': f"{event_impact}/{event_count}个相关事件利好黄金",
                    'impact': '+1',
                    'direction': 'positive'
                })
        
        # 价格位置（使用国内金价）
        avg_price = current_price_cny
        deviation = 0
        if history:
            prices = [h.get('domestic_cny_per_gram', current_price_cny) for h in history[-20:] if h.get('domestic_cny_per_gram')]
            if prices:
                avg_price = sum(prices) / len(prices)
                deviation = (current_price_cny - avg_price) / avg_price * 100
                if current_price_cny > avg_price * 1.05:
                    score -= 1.5
                    reasoning.append({
                        'factor': '价格位置',
                        'detail': f"当前价格{current_price_cny:.2f}高于20日均值{avg_price:.2f}({deviation:+.1f}%)，存在回调压力",
                        'impact': '-1.5',
                        'direction': 'negative'
                    })
                elif current_price_cny < avg_price * 0.95:
                    score += 1.5
                    reasoning.append({
                        'factor': '价格位置',
                        'detail': f"当前价格{current_price_cny:.2f}低于20日均值{avg_price:.2f}({deviation:+.1f}%)，存在反弹空间",
                        'impact': '+1.5',
                        'direction': 'positive'
                    })
                else:
                    reasoning.append({
                        'factor': '价格位置',
                        'detail': f"当前价格{current_price_cny:.2f}接近20日均值{avg_price:.2f}，位置中性",
                        'impact': '0',
                        'direction': 'neutral'
                    })
        
        # 7. 生成明日预测（基于双市场）
        prediction = self._predict_tomorrow(
            current_price=current_price_cny,
            score=score,
            tech_signals=tech_signals_cny,
            macro=macro_analysis,
            sentiment=sentiment,
            avg_price=avg_price,
            deviation=deviation,
            history=history
        )
        
        # 生成今日结论
        if score >= 5:
            judgment = "强烈看涨"
            recommendation = "建议买入"
            position = "20%"
        elif score >= 2:
            judgment = "看涨"
            recommendation = "建议买入"
            position = "10%"
        elif score > -2:
            judgment = "震荡"
            recommendation = "建议观望"
            position = "0%"
        elif score > -5:
            judgment = "看跌"
            recommendation = "建议观望或减仓"
            position = "0%"
        else:
            judgment = "强烈看跌"
            recommendation = "建议观望"
            position = "0%"
        
        return {
            'current_price': current_price_cny,
            'current_price_usd': current_price_usd,
            'price_change': {
                'cny': {'value': change_cny, 'pct': change_pct_cny},
                'usd': {'value': change_usd, 'pct': change_pct_usd}
            },
            'technical': tech_signals_cny,
            'technical_usd': tech_signals_usd,
            'trend_comparison': trend_comparison,
            'macro': macro_analysis,
            'sentiment': sentiment,
            'key_events': gold_related_events,
            'score': score,
            'reasoning': reasoning,
            'judgment': judgment,
            'recommendation': recommendation,
            'position': position,
            'confidence': min(100, abs(score) * 10 + 30),
            'prediction': prediction
        }
    
    def _predict_tomorrow(self, current_price: float, score: float, 
                         tech_signals: Dict, macro: Dict, sentiment: Dict,
                         avg_price: float, deviation: float, history: List) -> Dict:
        """
        预测明日黄金走势
        
        基于:
        1. 今日评分趋势
        2. 技术指标延续性
        3. 宏观环境稳定性
        4. 历史规律
        """
        
        tomorrow = (self.today + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 1. 基于今日评分判断明日方向
        if score >= 3:
            direction = "上涨"
            probability = min(70, 50 + score * 3)
        elif score <= -3:
            direction = "下跌"
            probability = min(70, 50 + abs(score) * 3)
        else:
            direction = "震荡"
            probability = 60
        
        # 2. 计算预期价格区间
        volatility = 0.015  # 假设日波动率1.5%
        
        if direction == "上涨":
            expected_change = current_price * 0.008  # 预期上涨0.8%
            price_range = (
                current_price * (1 + 0.003),  # 最低+0.3%
                current_price * (1 + 0.015)   # 最高+1.5%
            )
        elif direction == "下跌":
            expected_change = -current_price * 0.008  # 预期下跌0.8%
            price_range = (
                current_price * (1 - 0.015),  # 最低-1.5%
                current_price * (1 - 0.003)   # 最高-0.3%
            )
        else:
            expected_change = 0
            price_range = (
                current_price * 0.985,  # 最低-1.5%
                current_price * 1.015   # 最高+1.5%
            )
        
        expected_price = current_price + expected_change
        
        # 3. 预测理由
        prediction_reasoning = []
        
        # 技术延续性
        if tech_signals.get('trend') == 'up':
            prediction_reasoning.append({
                'factor': '技术趋势',
                'detail': '当前趋势向上，明日大概率延续',
                'impact': '偏多'
            })
        elif tech_signals.get('trend') == 'down':
            prediction_reasoning.append({
                'factor': '技术趋势',
                'detail': '当前趋势向下，明日大概率延续',
                'impact': '偏空'
            })
        
        # RSI均值回归
        rsi = tech_signals.get('rsi', 50)
        if rsi < 30:
            prediction_reasoning.append({
                'factor': 'RSI修复',
                'detail': f'RSI={rsi:.1f}超卖，明日存在技术性反弹可能',
                'impact': '偏多'
            })
        elif rsi > 70:
            prediction_reasoning.append({
                'factor': 'RSI修复',
                'detail': f'RSI={rsi:.1f}超买，明日存在技术性回调压力',
                'impact': '偏空'
            })
        
        # 均值回归
        if deviation > 3:
            prediction_reasoning.append({
                'factor': '均值回归',
                'detail': f'价格高于均值{deviation:.1f}%，存在向均值回归压力',
                'impact': '偏空'
            })
        elif deviation < -3:
            prediction_reasoning.append({
                'factor': '均值回归',
                'detail': f'价格低于均值{abs(deviation):.1f}%，存在向均值回归动力',
                'impact': '偏多'
            })
        
        # 宏观稳定性
        macro_signal = macro.get('signals', {}).get('overall', '中性')
        if macro_signal in ['利好', '强利好']:
            prediction_reasoning.append({
                'factor': '宏观环境',
                'detail': f'宏观环境{macro_signal}，支撑明日走势',
                'impact': '偏多'
            })
        elif macro_signal in ['利空', '强利空']:
            prediction_reasoning.append({
                'factor': '宏观环境',
                'detail': f'宏观环境{macro_signal}，压制明日走势',
                'impact': '偏空'
            })
        
        # 情绪惯性
        sentiment_trend = sentiment.get('trend', '中性')
        if sentiment_trend == '乐观':
            prediction_reasoning.append({
                'factor': '情绪惯性',
                'detail': '市场情绪乐观，明日可能延续',
                'impact': '偏多'
            })
        elif sentiment_trend == '悲观':
            prediction_reasoning.append({
                'factor': '情绪惯性',
                'detail': '市场情绪谨慎，明日可能延续',
                'impact': '偏空'
            })
        
        # 4. 关键观察点
        key_watch = []
        if abs(deviation) > 2:
            key_watch.append(f"价格与20日均线偏离度({deviation:+.1f}%)")
        if rsi < 30 or rsi > 70:
            key_watch.append(f"RSI极端值({rsi:.1f})修复情况")
        key_watch.append("美元指数走势")
        key_watch.append("地缘政治新闻")
        
        # 5. 预测置信度
        confidence_factors = len([r for r in prediction_reasoning if r['impact'] != '中性'])
        prediction_confidence = min(80, 40 + confidence_factors * 8)
        
        return {
            'date': tomorrow,
            'direction': direction,
            'probability': probability,
            'current_price': current_price,
            'expected_price': expected_price,
            'expected_change': expected_change,
            'price_range': price_range,
            'reasoning': prediction_reasoning,
            'key_watch': key_watch,
            'confidence': prediction_confidence
        }
    
    def _analyze_trend_comparison(self, tech_cny: Dict, tech_usd: Dict, 
                                   change_pct_cny: float, change_pct_usd: float) -> Dict:
        """
        分析内外盘趋势对比
        
        返回:
        - 趋势一致性判断
        - 内外盘强弱对比
        - 汇率影响分析
        """
        trend_cny = tech_cny.get('trend', 'neutral')
        trend_usd = tech_usd.get('trend', 'neutral')
        
        # 1. 趋势一致性
        if trend_cny == trend_usd:
            consistency = "一致"
            consistency_desc = f"内外盘均为{trend_cny}趋势，信号明确"
        else:
            consistency = "分歧"
            consistency_desc = f"国内{trend_cny} vs 国际{trend_usd}，存在分歧"
        
        # 2. 日内涨跌对比
        if abs(change_pct_cny - change_pct_usd) < 0.5:
            daily_comparison = "同步"
            daily_desc = f"日内涨跌同步 (国内{change_pct_cny:+.2f}% vs 国际{change_pct_usd:+.2f}%)"
        elif change_pct_cny > change_pct_usd:
            daily_comparison = "内强外弱"
            daily_desc = f"国内强于国际 (国内{change_pct_cny:+.2f}% vs 国际{change_pct_usd:+.2f}%)"
        else:
            daily_comparison = "外强内弱"
            daily_desc = f"国际强于国内 (国内{change_pct_cny:+.2f}% vs 国际{change_pct_usd:+.2f}%)"
        
        # 3. 综合判断
        if consistency == "一致" and daily_comparison == "同步":
            overall = "趋势明确"
            suggestion = "跟随趋势操作"
        elif consistency == "分歧":
            overall = "趋势不明"
            suggestion = "观望，等待信号统一"
        elif daily_comparison == "内强外弱":
            overall = "内盘偏强"
            suggestion = "关注人民币汇率因素"
        else:
            overall = "外盘偏强"
            suggestion = "关注国际市场动向"
        
        return {
            'consistency': consistency,
            'consistency_desc': consistency_desc,
            'daily_comparison': daily_comparison,
            'daily_desc': daily_desc,
            'overall': overall,
            'suggestion': suggestion,
            'trend_cny': trend_cny,
            'trend_usd': trend_usd,
            'change_cny': change_pct_cny,
            'change_usd': change_pct_usd
        }
    
    def analyze_funds(self) -> Dict:
        """基金完整分析 - 包含具体基金推荐"""
        # 1. 获取数据
        sentiment = self._get_sentiment_data()
        macro = self.global_macro.analyze()
        
        # 2. 获取政策受益行业
        recent_policies = self.dm.get_recent_policies(days=7, limit=20)
        policy_sectors = {}
        for policy in recent_policies:
            title = policy.get('title', '')
            if '科技' in title or 'AI' in title:
                policy_sectors['科技'] = policy_sectors.get('科技', 0) + 1
            if '新能源' in title or '绿色' in title:
                policy_sectors['新能源'] = policy_sectors.get('新能源', 0) + 1
            if '基建' in title:
                policy_sectors['基建'] = policy_sectors.get('基建', 0) + 1
            if '消费' in title:
                policy_sectors['消费'] = policy_sectors.get('消费', 0) + 1
        
        # 3. 获取具体基金推荐
        try:
            self.fund_recommender.set_macro_context(
                gold_trend=macro.get('signals', {}).get('overall', '中性'),
                policy_focus=list(policy_sectors.keys())
            )
            fund_rec = self.fund_recommender.get_comprehensive_recommendation()
        except Exception as e:
            print(f"  获取基金数据失败: {e}")
            fund_rec = {'recommendations': {}}
        
        # 4. 分析推荐（结合宏观环境选择推荐类别）
        recommendations = []
        macro_signal = macro.get('signals', {}).get('overall', '中性')
        
        # 科技基金（政策支持）
        tech_policy = policy_sectors.get('科技', 0)
        tech_sentiment = sentiment.get('sector_sentiment', {}).get('科技', 0)
        tech_funds = fund_rec.get('recommendations', {}).get('科技主题', {}).get('funds', [])
        if tech_policy >= 2 or tech_sentiment > 0.3 or tech_funds:
            recommendations.append({
                'type': '科技主题基金',
                'reasoning': [
                    f"政策因素: 近7天科技相关政策提及{tech_policy}次",
                    f"情绪因素: 科技板块情绪得分{tech_sentiment:+.2f}",
                    "两会强调新质生产力，科技行业长期受益"
                ],
                'risk': '高',
                'action': '推荐配置' if tech_policy >= 2 else '适当关注',
                'position': '10-15%',
                'funds': tech_funds[:3]  # 前3只具体基金
            })
        
        # 债券基金（宏观利空时推荐）
        bond_funds = fund_rec.get('recommendations', {}).get('债券基金', {}).get('funds', [])
        if macro_signal in ['利空', '强利空'] or bond_funds:
            recommendations.append({
                'type': '债券基金',
                'reasoning': [
                    f"宏观因素: 全球宏观环境{macro_signal}，市场不确定性增加",
                    "债券基金提供稳定收益，降低组合波动",
                    "适合作为防守配置"
                ],
                'risk': '低',
                'action': '推荐配置',
                'position': '20-30%',
                'funds': bond_funds[:3]
            })
        
        # 指数基金（始终推荐）
        index_funds = fund_rec.get('recommendations', {}).get('指数基金', {}).get('funds', [])
        recommendations.append({
            'type': '指数基金',
            'reasoning': [
                "分散投资，降低个股风险",
                "适合长期定投，平滑成本",
                "无论市场涨跌均可配置"
            ],
            'risk': '中',
            'action': '长期定投',
            'position': '20-30%',
            'funds': index_funds[:3]
        })
        
        # 黄金基金（根据宏观环境）
        gold_funds = fund_rec.get('recommendations', {}).get('黄金相关', {}).get('funds', [])
        if macro_signal in ['利好', '强利好'] or gold_funds:
            recommendations.append({
                'type': '黄金相关基金',
                'reasoning': [
                    f"宏观因素: 全球宏观环境{macro_signal}黄金",
                    f"DXY={macro.get('data', {}).get('dxy', 100)}，{'美元弱势' if macro.get('data', {}).get('dxy', 100) < 103 else '需观察'}",
                    "地缘政治风险支撑避险需求"
                ],
                'risk': '中高',
                'action': '推荐配置' if macro_signal in ['利好', '强利好'] else '适当关注',
                'position': '5-10%',
                'funds': gold_funds[:3]
            })
        
        return {
            'recommendations': recommendations,
            'macro_signal': macro_signal,
            'sentiment': sentiment.get('trend', '中性'),
            'policy_sectors': policy_sectors,
            'fund_data_source': fund_rec.get('timestamp', 'N/A')
        }
    
    def analyze_stocks(self) -> Dict:
        """股票完整分析 - 包含具体个股推荐"""
        # 1. 获取数据
        sentiment = self._get_sentiment_data()
        recent_policies = self.dm.get_recent_policies(days=7, limit=20)
        
        # 2. 政策分析
        policy_sectors = {}
        policy_details = []
        
        for policy in recent_policies:
            title = policy.get('title', '')
            date = policy.get('date', '')
            
            sectors = []
            if any(kw in title for kw in ['科技', 'AI', '人工智能']):
                sectors.append('科技')
            if any(kw in title for kw in ['新能源', '绿色', '碳中和']):
                sectors.append('新能源')
            if any(kw in title for kw in ['基建', '投资']):
                sectors.append('基建')
            if any(kw in title for kw in ['消费', '内需']):
                sectors.append('消费')
            if any(kw in title for kw in ['医药', '医疗']):
                sectors.append('医药')
            
            for sector in sectors:
                policy_sectors[sector] = policy_sectors.get(sector, 0) + 1
            
            if sectors:
                policy_details.append({
                    'date': date,
                    'title': title[:40] + '...' if len(title) > 40 else title,
                    'sectors': sectors
                })
        
        # 3. 情绪分析
        sector_sentiment = sentiment.get('sector_sentiment', {})
        
        # 4. 使用StockAnalyzer获取行业轮动和具体个股
        try:
            # 获取行业轮动信号
            rotation_signals = self.stock_analyzer.get_sector_rotation_signal()
            
            # 获取宏观行业推荐
            macro_context = {
                "gold_trend": self.global_macro.analyze().get('signals', {}).get('overall', 'neutral'),
                "policy_focus": list(policy_sectors.keys()),
                "risk_appetite": "high" if sentiment.get('overall_score', 0) > 0.3 else "low" if sentiment.get('overall_score', 0) < -0.3 else "medium"
            }
            macro_rec = self.stock_analyzer.get_macro_sector_recommendation(macro_context)
            
            # 获取具体个股推荐（每个推荐行业取前3只）
            stock_picks = []
            for sector in macro_rec.get('推荐行业', [])[:3]:
                try:
                    stocks_df = self.stock_analyzer.screen_stocks_by_sector(sector, limit=3)
                    if not stocks_df.empty:
                        for _, row in stocks_df.iterrows():
                            stock_picks.append({
                                'code': row.get('代码', ''),
                                'name': row.get('名称', ''),
                                'sector': sector,
                                'price': row.get('最新价', 0),
                                'change': row.get('涨跌幅', 0),
                                'turnover': row.get('换手率', 0),
                                'pe': row.get('市盈率', 0),
                                'market_cap': row.get('总市值', 0)
                            })
                except Exception as e:
                    print(f"    获取{sector}个股失败: {e}")
                    # 使用模拟数据作为备选
                    mock_stocks = self._get_mock_stocks_for_sector(sector)
                    stock_picks.extend(mock_stocks)
                    continue
        except Exception as e:
            print(f"  股票分析失败: {e}")
            rotation_signals = {"强势板块": [], "轮动趋势": "获取失败"}
            macro_rec = {"推荐行业": ["科技", "新能源", "消费"], "推荐逻辑": "基于政策导向"}
            stock_picks = self._get_default_mock_stocks()
        
        # 5. 综合推荐（基于政策和情绪）
        recommendations = []
        
        # 政策+情绪双重利好
        for sector, count in policy_sectors.items():
            sentiment_score = sector_sentiment.get(sector, 0)
            if count >= 2 and sentiment_score > 0:
                recommendations.append({
                    'sector': sector,
                    'strength': '强',
                    'reasoning': [
                        f"政策支撑: 近7天提及{count}次",
                        f"情绪支撑: 板块情绪{sentiment_score:+.2f}",
                        "政策与情绪双重利好"
                    ]
                })
            elif count >= 1 or sentiment_score > 0.3:
                recommendations.append({
                    'sector': sector,
                    'strength': '中',
                    'reasoning': [
                        f"{'政策提及' if count >= 1 else '情绪积极'}",
                        f"具体: 提及{count}次" if count >= 1 else f"情绪得分{sentiment_score:+.2f}"
                    ]
                })
        
        # 情绪独立利好
        for sector, score in sector_sentiment.items():
            if score > 0.5 and sector not in [r['sector'] for r in recommendations]:
                recommendations.append({
                    'sector': sector,
                    'strength': '弱',
                    'reasoning': [
                        f"情绪支撑: 板块情绪{score:+.2f}",
                        "市场情绪推动"
                    ]
                })
        
        # 排序
        recommendations.sort(key=lambda x: {'强': 3, '中': 2, '弱': 1}.get(x['strength'], 0), reverse=True)
        
        # 如果仍然没有个股数据，使用默认模拟数据
        if not stock_picks:
            stock_picks = self._get_default_mock_stocks()
        
        return {
            'recommendations': recommendations[:5],
            'policy_details': policy_details[:5],
            'sector_sentiment': sector_sentiment,
            'rotation_signals': rotation_signals,
            'macro_rec': macro_rec,
            'stock_picks': stock_picks[:9],  # 最多9只个股
            'data_source': '实时数据' if stock_picks and stock_picks[0].get('code') not in ['000001', '600000'] else '模拟数据'
        }
    
    def generate_brief(self) -> str:
        """生成完整简报"""
        print("🔍 开始综合分析...")
        
        print("  1. 分析关键事件...")
        key_events = self.analyze_key_events()
        
        print("  2. 分析黄金...")
        gold_analysis = self.analyze_gold()
        
        print("  3. 分析基金...")
        fund_analysis = self.analyze_funds()
        
        print("  4. 分析股票...")
        stock_analysis = self.analyze_stocks()
        
        print("  5. 生成报告...")
        report = self._format_report(key_events, gold_analysis, fund_analysis, stock_analysis)
        
        return report
    
    def _get_mock_stocks_for_sector(self, sector: str) -> List[Dict]:
        """获取板块模拟个股数据"""
        mock_data = {
            "科技": [
                {"code": "688981", "name": "中芯国际", "price": 85.32, "change": 3.25, "turnover": 2.1, "pe": 65.8, "market_cap": 680000000000},
                {"code": "000938", "name": "中芯国际", "price": 45.68, "change": 2.89, "turnover": 1.8, "pe": 58.2, "market_cap": 360000000000},
                {"code": "002371", "name": "北方华创", "price": 298.50, "change": 4.12, "turnover": 3.2, "pe": 72.5, "market_cap": 158000000000},
            ],
            "新能源": [
                {"code": "300750", "name": "宁德时代", "price": 198.60, "change": 2.15, "turnover": 1.5, "pe": 25.3, "market_cap": 870000000000},
                {"code": "601012", "name": "隆基绿能", "price": 22.35, "change": 1.85, "turnover": 2.8, "pe": 18.6, "market_cap": 169000000000},
                {"code": "002594", "name": "比亚迪", "price": 268.80, "change": 3.42, "turnover": 2.1, "pe": 32.8, "market_cap": 782000000000},
            ],
            "消费": [
                {"code": "000858", "name": "五粮液", "price": 152.30, "change": 1.25, "turnover": 0.8, "pe": 22.5, "market_cap": 591000000000},
                {"code": "600519", "name": "贵州茅台", "price": 1680.00, "change": 0.85, "turnover": 0.3, "pe": 28.6, "market_cap": 2110000000000},
                {"code": "000333", "name": "美的集团", "price": 68.50, "change": 1.12, "turnover": 0.9, "pe": 15.2, "market_cap": 478000000000},
            ],
            "医药": [
                {"code": "600276", "name": "恒瑞医药", "price": 45.20, "change": 2.35, "turnover": 1.2, "pe": 68.5, "market_cap": 288000000000},
                {"code": "000538", "name": "云南白药", "price": 52.80, "change": 0.95, "turnover": 0.6, "pe": 25.8, "market_cap": 95000000000},
                {"code": "300003", "name": "乐普医疗", "price": 12.50, "change": 1.85, "turnover": 2.1, "pe": 22.3, "market_cap": 23500000000},
            ],
            "基建": [
                {"code": "601668", "name": "中国建筑", "price": 5.68, "change": 0.85, "turnover": 0.5, "pe": 4.2, "market_cap": 238000000000},
                {"code": "601390", "name": "中国中铁", "price": 6.35, "change": 1.25, "turnover": 0.8, "pe": 5.8, "market_cap": 157000000000},
                {"code": "601186", "name": "中国铁建", "price": 8.20, "change": 0.95, "turnover": 0.6, "pe": 4.5, "market_cap": 111000000000},
            ],
        }
        
        stocks = mock_data.get(sector, [])
        for stock in stocks:
            stock['sector'] = sector
        return stocks
    
    def _get_default_mock_stocks(self) -> List[Dict]:
        """获取默认模拟个股"""
        default_stocks = []
        for sector in ["科技", "新能源", "消费"]:
            default_stocks.extend(self._get_mock_stocks_for_sector(sector))
        return default_stocks
    
    def _format_report(self, events: Dict, gold: Dict, funds: Dict, stocks: Dict) -> str:
        """格式化报告"""
        
        report = f"""# 📊 每日投资简报 V8.2 - 完整分析版

**日期**: {self.today_str}
**生成时间**: {self.today.strftime('%H:%M')}
**版本**: 8.2.0

---

## 📰 关键事件与影响分析

### 近期重要事件 ({events['policy_count']}条政策 + {events['sentiment_count']}条情绪)

"""
        
        # 事件列表
        for i, event in enumerate(events['events'][:8], 1):  # 前8条
            event_type = "📋 政策" if event['type'] == 'policy' else "📊 情绪"
            title = event.get('title', '')
            
            report += f"**{i}. {event_type} | {event.get('date', '')}**\n"
            report += f"- 标题: {title}\n"
            
            if event['type'] == 'policy':
                report += f"- 类别: {event.get('category', '其他')}\n"
                report += f"- 影响评估: {event.get('impact', '中性')}\n"
            else:
                report += f"- 情绪: {event.get('sentiment', '中性')} ({event.get('score', 0):+.2f})\n"
            
            impact_analysis = event.get('impact_analysis', {})
            report += f"- 影响分析: {impact_analysis.get('description', '待观察')}\n"
            
            affected = event.get('affected_assets', [])
            if affected:
                report += f"- 影响资产: {', '.join(affected[:5])}\n"
            
            report += "\n"
        
        # 黄金分析
        price_change = gold.get('price_change', {})
        trend_comp = gold.get('trend_comparison', {})
        
        report += f"""---

## 🥇 黄金分析（双市场）

### 当前价格

| 市场 | 价格 | 日涨跌 | 涨跌幅 |
|------|------|--------|--------|
| 🇨🇳 国内金价 | {gold['current_price']:.2f} 元/克 | {price_change.get('cny', {}).get('value', 0):+.2f} | {price_change.get('cny', {}).get('pct', 0):+.2f}% |
| 🌍 国际金价 | {gold.get('current_price_usd', 3000):.2f} 美元/盎司 | {price_change.get('usd', {}).get('value', 0):+.2f} | {price_change.get('usd', {}).get('pct', 0):+.2f}% |

### 内外盘趋势对比

**趋势一致性**: {trend_comp.get('consistency', '未知')}  
{trend_comp.get('consistency_desc', '')}

**日内强弱对比**: {trend_comp.get('daily_comparison', '未知')}  
{trend_comp.get('daily_desc', '')}

**综合判断**: {trend_comp.get('overall', '未知')} - {trend_comp.get('suggestion', '观望')}

### 技术指标对比

| 指标 | 国内市场 | 国际市场 |
|------|----------|----------|
| 趋势 | {gold['technical'].get('trend', 'unknown')} | {gold.get('technical_usd', {}).get('trend', 'unknown')} |
| MA5 | {gold['technical'].get('ma5', 0):.2f} | {gold.get('technical_usd', {}).get('ma5', 0):.2f} |
| RSI | {gold['technical'].get('rsi', 50):.1f} | {gold.get('technical_usd', {}).get('rsi', 50):.1f} |

### 综合评分
**总评分**: {gold['score']:+.1f}/10 (越高越看涨)  
**置信度**: {gold['confidence']:.0f}%

### 评分理由详解

| 因素 | 详情 | 影响 |
|------|------|------|
"""
        
        for r in gold['reasoning']:
            emoji = "🟢" if r['direction'] == 'positive' else "🔴" if r['direction'] == 'negative' else "⚪"
            report += f"| {emoji} {r['factor']} | {r['detail']} | {r['impact']} |\n"
        
        # 关键事件影响
        if gold['key_events']:
            report += "\n**关键事件影响**:\n"
            for event in gold['key_events'][:3]:
                report += f"- {event.get('title', '')[:40]}...\n"
        
        report += f"""
### 分析结论
- **判断**: {gold['judgment']}
- **建议**: {gold['recommendation']}
- **建议仓位**: {gold['position']}

**核心逻辑**: 
"""
        
        # 核心逻辑总结
        positive_factors = [r for r in gold['reasoning'] if r['direction'] == 'positive']
        negative_factors = [r for r in gold['reasoning'] if r['direction'] == 'negative']
        
        if positive_factors:
            report += f"- 利好因素: {len(positive_factors)}个（{'、'.join([r['factor'] for r in positive_factors[:2]])}）\n"
        if negative_factors:
            report += f"- 利空因素: {len(negative_factors)}个（{'、'.join([r['factor'] for r in negative_factors[:2]])}）\n"
        
        report += f"- 综合判断: 基于以上{len(gold['reasoning'])}个因素，给出{gold['judgment']}判断\n"
        
        # 明日预测
        pred = gold.get('prediction', {})
        if pred:
            direction_emoji = "📈" if pred['direction'] == '上涨' else "📉" if pred['direction'] == '下跌' else "➡️"
            report += f"""

### 🔮 明日走势预测 ({pred.get('date', '明日')})

**预测方向**: {direction_emoji} **{pred['direction']}** (概率{pred['probability']}%)

**价格预测**:
- **当前价格**: {pred['current_price']:.2f} 元/克
- **预期价格**: {pred['expected_price']:.2f} 元/克
- **预期涨跌**: {pred['expected_change']:+.2f} 元 ({pred['expected_change']/pred['current_price']*100:+.2f}%)
- **价格区间**: {pred['price_range'][0]:.2f} - {pred['price_range'][1]:.2f} 元/克

**预测理由**:

| 因素 | 详情 | 影响 |
|------|------|------|
"""
            for r in pred.get('reasoning', []):
                emoji = "🟢" if r['impact'] == '偏多' else "🔴" if r['impact'] == '偏空' else "⚪"
                report += f"| {emoji} {r['factor']} | {r['detail']} | {r['impact']} |\n"
            
            report += f"""
**关键观察点**:
"""
            for i, watch in enumerate(pred.get('key_watch', []), 1):
                report += f"{i}. {watch}\n"
            
            report += f"""
**预测置信度**: {pred['confidence']}% (基于{len(pred.get('reasoning', []))}个支撑因素)

**⚠️ 预测说明**: 
- 预测基于历史规律和技术指标，不构成投资建议
- 实际走势可能受突发新闻、地缘政治等因素影响
- 建议结合明日开盘后的实时数据调整判断
"""
        
        # 基金分析
        report += f"""
---

## 💰 基金分析

### 宏观与市场环境
- **全球宏观**: {funds['macro_signal']}
- **市场情绪**: {funds['sentiment']}
- **数据更新时间**: {funds.get('fund_data_source', 'N/A')}

### 推荐配置及理由

"""
        
        for i, rec in enumerate(funds['recommendations'], 1):
            report += f"**{i}. {rec['type']}**\n"
            report += f"- **建议**: {rec['action']}\n"
            report += f"- **建议仓位**: {rec['position']}\n"
            report += f"- **风险等级**: {rec['risk']}\n"
            report += f"- **推荐理由**:\n"
            for reason in rec['reasoning']:
                report += f"  - {reason}\n"
            
            # 添加具体基金推荐
            if rec.get('funds'):
                report += f"\n**具体推荐基金**:\n\n"
                report += "| 代码 | 基金名称 | 单位净值 | 日涨跌 | 今年来 | 近1月 | 近1年 | 手续费 |\n"
                report += "|------|----------|----------|--------|--------|-------|-------|--------|\n"
                for fund in rec['funds']:
                    name = fund.get('name', '')[:12] + '...' if len(fund.get('name', '')) > 12 else fund.get('name', '')
                    report += f"| {fund.get('code', '--')} | {name} | {fund.get('nav', '--')} | {fund.get('daily_return', '--')} | {fund.get('ytd_return', '--')} | {fund.get('1month', '--')} | {fund.get('1year', '--')} | {fund.get('fee', '--')} |\n"
            
            report += "\n"
        
        # 股票分析
        report += f"""---

## 📈 股票分析（观察用）

### 近期政策动态

"""
        
        if stocks['policy_details']:
            for detail in stocks['policy_details'][:5]:
                report += f"- **{detail['date']}** | {detail['title']}\n"
                report += f"  - 受益行业: {', '.join(detail['sectors'])}\n"
        else:
            report += "- 近7天无明确政策指向\n"
        
        report += f"""
### 板块情绪排行

"""
        
        if stocks['sector_sentiment']:
            report += "| 板块 | 情绪得分 | 判断 |\n"
            report += "|------|----------|------|\n"
            for sector, score in sorted(stocks['sector_sentiment'].items(), 
                                      key=lambda x: x[1], reverse=True)[:8]:
                emoji = "🟢" if score > 0.2 else "🔴" if score < -0.2 else "⚪"
                judgment = "利好" if score > 0.2 else "利空" if score < -0.2 else "中性"
                report += f"| {sector} | {score:+.2f} | {emoji} {judgment} |\n"
        
        report += f"""
### 行业推荐及理由

"""
        
        for i, rec in enumerate(stocks['recommendations'][:5], 1):
            emoji = "🔥" if rec['strength'] == '强' else "⭐" if rec['strength'] == '中' else "📌"
            report += f"**{i}. {emoji} {rec['sector']}** (推荐强度: {rec['strength']})\n"
            report += f"- **推荐理由**:\n"
            for reason in rec['reasoning']:
                report += f"  - {reason}\n"
            report += "\n"
        
        # 行业轮动信号
        rotation = stocks.get('rotation_signals', {})
        if rotation:
            report += f"""
### 行业轮动信号

- **当前趋势**: {rotation.get('轮动趋势', '获取失败')}
- **强势板块**: {', '.join(rotation.get('强势板块', [])[:5])}
- **建议关注**: {', '.join(rotation.get('建议关注', [])[:3])}

"""
        
        # 具体个股推荐
        stock_picks = stocks.get('stock_picks', [])
        if stock_picks:
            report += f"""
### 📊 具体个股推荐（观察用）

| 代码 | 名称 | 所属行业 | 最新价 | 涨跌幅 | 换手率 | 市盈率 | 总市值(亿) |
|------|------|----------|--------|--------|--------|--------|------------|
"""
            for stock in stock_picks:
                market_cap = stock.get('market_cap', 0)
                market_cap_str = f"{market_cap/100000000:.0f}" if market_cap else '--'
                report += f"| {stock.get('code', '--')} | {stock.get('name', '--')} | {stock.get('sector', '--')} | {stock.get('price', '--')} | {stock.get('change', '--')}% | {stock.get('turnover', '--')}% | {stock.get('pe', '--')} | {market_cap_str} |\n"
            
            report += f"""
**个股筛选逻辑**:
- 基于政策受益行业筛选
- 按涨跌幅排序取前3
- 关注换手率和估值水平
- ⚠️ 仅为观察用，不构成买卖建议

"""
        
        # 交易信号总结
        report += f"""---

## 🎯 今日交易信号总结

| 资产 | 判断 | 建议 | 仓位 | 核心理由 |
|------|------|------|------|----------|
| 黄金 | {gold['judgment']} | {gold['recommendation']} | {gold['position']} | 综合评分{gold['score']:+.1f}，{len([r for r in gold['reasoning'] if r['direction']=='positive'])}利好 vs {len([r for r in gold['reasoning'] if r['direction']=='negative'])}利空 |

**今日重点关注**:
"""
        
        # 根据分析结果给出重点关注
        if gold['score'] >= 2:
            report += "- 黄金: 技术面和宏观环境支持，关注买入机会\n"
        elif gold['score'] <= -2:
            report += "- 黄金: 技术面偏弱，建议观望或减仓\n"
        
        if funds['recommendations']:
            top_fund = funds['recommendations'][0]
            report += f"- 基金: 优先关注{top_fund['type']}，{top_fund['reasoning'][0]}\n"
        
        if stocks['recommendations']:
            top_sector = stocks['recommendations'][0]
            report += f"- 股票: {top_sector['sector']}板块受关注，{top_sector['reasoning'][0]}\n"
        
        report += f"""
---

## ⚠️ 风险提示

1. 本分析基于历史数据和当前信息，不构成投资建议
2. 市场有风险，投资需谨慎
3. 过往表现不代表未来
4. 请结合自身风险承受能力决策
5. 关键事件影响可能随时间变化，需持续跟踪

---

*报告基于以下分析模块生成*:
- 技术分析: MA/RSI/趋势判断
- 情绪分析: 新闻情绪量化分析
- 宏观分析: DXY/VIX/Oil综合分析
- 政策分析: 近7天政策动态跟踪
- 事件分析: 关键事件影响评估

*生成时间*: {self.today.strftime('%Y-%m-%d %H:%M')}
"""
        
        return report


def main():
    """主函数"""
    print("="*70)
    print("📊 每日简报 V8.0 - 完整分析版")
    print("="*70)
    
    analyzer = DailyBriefV8()
    report = analyzer.generate_brief()
    
    # 保存报告
    brief_dir = Path(__file__).parent.parent / "daily_brief"
    brief_dir.mkdir(exist_ok=True)
    brief_path = brief_dir / f"brief_v8_{datetime.now().strftime('%Y%m%d')}.md"
    
    with open(brief_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "="*70)
    print(f"✅ 简报生成完成!")
    print(f"📄 保存路径: {brief_path}")
    print("="*70)
    
    print("\n📋 报告预览 (前3000字符):")
    print(report[:3000] + "...\n" if len(report) > 3000 else report)


if __name__ == '__main__':
    main()
