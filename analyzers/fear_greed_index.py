#!/usr/bin/env python3
"""
恐慌贪婪指数 (Fear & Greed Index)

综合多个市场指标生成 0-100 的情绪指数
0 = 极度恐慌，100 = 极度贪婪

指标组成:
1. VIX 恐慌指数 (25%)
2. 股债性价比 (25%)
3. 北向资金流向 (20%)
4. 市场成交量 (15%)
5. 新闻情绪 (15%)
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class IndicatorSignal:
    """指标信号"""
    name: str
    value: float
    signal: str  # 极度恐慌/恐慌/中性/贪婪/极度贪婪
    score: float  # 0-100
    weight: float  # 权重
    emoji: str


class FearGreedIndex:
    """恐慌贪婪指数计算器"""
    
    def __init__(self):
        # 指标权重配置
        self.weights = {
            'vix': 0.25,        # VIX 恐慌指数
            'equity_bond': 0.25, # 股债性价比
            'northbound': 0.20,  # 北向资金
            'volume': 0.15,      # 成交量
            'sentiment': 0.15,   # 新闻情绪
        }
        
        # VIX 阈值配置
        self.vix_thresholds = {
            'extreme_fear': 30,   # VIX > 30 = 极度恐慌
            'fear': 25,           # VIX > 25 = 恐慌
            'neutral_high': 20,   # VIX > 20 = 中性偏高
            'neutral_low': 15,    # VIX > 15 = 中性偏低
            'greed': 12,          # VIX > 12 = 贪婪
            # VIX < 12 = 极度贪婪
        }
        
        # 股债性价比阈值（沪深 300 股息率 - 10 年国债收益率）
        self.equity_bond_thresholds = {
            'extreme_greed': 2.0,   # > 2% = 股票极具吸引力
            'greed': 1.5,           # > 1.5% = 股票有吸引力
            'neutral_high': 0.5,    # > 0.5% = 中性偏多
            'neutral_low': -0.5,    # > -0.5% = 中性偏空
            'fear': -1.0,           # > -1% = 债券更有吸引力
            # < -1% = 极度恐慌
        }
        
        # 北向资金阈值（亿元）
        self.northbound_thresholds = {
            'extreme_greed': 100,   # > 100 亿 = 极度贪婪
            'greed': 50,            # > 50 亿 = 贪婪
            'neutral_high': 20,     # > 20 亿 = 中性偏多
            'neutral_low': -20,     # > -20 亿 = 中性偏空
            'fear': -50,            # > -50 亿 = 恐慌
            # < -50 亿 = 极度恐慌
        }
        
        # 成交量阈值（亿元，指沪深两市总成交）
        self.volume_thresholds = {
            'extreme_greed': 12000,  # > 1.2 万亿 = 极度贪婪
            'greed': 10000,          # > 1 万亿 = 贪婪
            'neutral_high': 8000,    # > 8000 亿 = 中性偏多
            'neutral_low': 6000,     # > 6000 亿 = 中性偏空
            'fear': 5000,            # > 5000 亿 = 恐慌
            # < 5000 亿 = 极度恐慌
        }
        
        logger.info("[恐慌贪婪指数] 初始化完成")
    
    def calculate_vix_score(self, vix_value: float) -> IndicatorSignal:
        """
        计算 VIX 得分
        
        VIX 越低 = 越贪婪，VIX 越高 = 越恐慌
        """
        if vix_value >= self.vix_thresholds['extreme_fear']:
            score = 10
            signal = "极度恐慌"
            emoji = "🔴"
        elif vix_value >= self.vix_thresholds['fear']:
            score = 30
            signal = "恐慌"
            emoji = "🟠"
        elif vix_value >= self.vix_thresholds['neutral_high']:
            score = 45
            signal = "中性偏高"
            emoji = "🟡"
        elif vix_value >= self.vix_thresholds['neutral_low']:
            score = 55
            signal = "中性偏低"
            emoji = "🟡"
        elif vix_value >= self.vix_thresholds['greed']:
            score = 75
            signal = "贪婪"
            emoji = "🟢"
        else:
            score = 90
            signal = "极度贪婪"
            emoji = "🟢"
        
        return IndicatorSignal(
            name="VIX 恐慌指数",
            value=vix_value,
            signal=signal,
            score=score,
            weight=self.weights['vix'],
            emoji=emoji
        )
    
    def calculate_equity_bond_score(self, spread: float) -> IndicatorSignal:
        """
        计算股债性价比得分
        
        利差越大 = 股票越有吸引力 = 越贪婪
        """
        if spread >= self.equity_bond_thresholds['extreme_greed']:
            score = 90
            signal = "极度贪婪"
            emoji = "🟢"
        elif spread >= self.equity_bond_thresholds['greed']:
            score = 75
            signal = "贪婪"
            emoji = "🟢"
        elif spread >= self.equity_bond_thresholds['neutral_high']:
            score = 60
            signal = "中性偏多"
            emoji = "🟡"
        elif spread >= self.equity_bond_thresholds['neutral_low']:
            score = 40
            signal = "中性偏空"
            emoji = "🟡"
        elif spread >= self.equity_bond_thresholds['fear']:
            score = 25
            signal = "恐慌"
            emoji = "🟠"
        else:
            score = 10
            signal = "极度恐慌"
            emoji = "🔴"
        
        return IndicatorSignal(
            name="股债性价比",
            value=spread,
            signal=signal,
            score=score,
            weight=self.weights['equity_bond'],
            emoji=emoji
        )
    
    def calculate_northbound_score(self, northbound_flow: float) -> IndicatorSignal:
        """
        计算北向资金得分
        
        净流入越大 = 越贪婪
        """
        if northbound_flow >= self.northbound_thresholds['extreme_greed']:
            score = 90
            signal = "大幅流入"
            emoji = "🟢"
        elif northbound_flow >= self.northbound_thresholds['greed']:
            score = 75
            signal = "流入"
            emoji = "🟢"
        elif northbound_flow >= self.northbound_thresholds['neutral_high']:
            score = 60
            signal = "小幅流入"
            emoji = "🟡"
        elif northbound_flow >= self.northbound_thresholds['neutral_low']:
            score = 40
            signal = "小幅流出"
            emoji = "🟡"
        elif northbound_flow >= self.northbound_thresholds['fear']:
            score = 25
            signal = "流出"
            emoji = "🟠"
        else:
            score = 10
            signal = "大幅流出"
            emoji = "🔴"
        
        return IndicatorSignal(
            name="北向资金",
            value=northbound_flow,
            signal=signal,
            score=score,
            weight=self.weights['northbound'],
            emoji=emoji
        )
    
    def calculate_volume_score(self, volume: float) -> IndicatorSignal:
        """
        计算成交量得分
        
        成交量越大 = 市场越活跃 = 越贪婪
        """
        if volume >= self.volume_thresholds['extreme_greed']:
            score = 90
            signal = "极度活跃"
            emoji = "🟢"
        elif volume >= self.volume_thresholds['greed']:
            score = 75
            signal = "活跃"
            emoji = "🟢"
        elif volume >= self.volume_thresholds['neutral_high']:
            score = 60
            signal = "正常偏多"
            emoji = "🟡"
        elif volume >= self.volume_thresholds['neutral_low']:
            score = 40
            signal = "正常偏空"
            emoji = "🟡"
        elif volume >= self.volume_thresholds['fear']:
            score = 25
            signal = "低迷"
            emoji = "🟠"
        else:
            score = 10
            signal = "极度低迷"
            emoji = "🔴"
        
        return IndicatorSignal(
            name="市场成交量",
            value=volume,
            signal=signal,
            score=score,
            weight=self.weights['volume'],
            emoji=emoji
        )
    
    def calculate_sentiment_score(self, sentiment_score: float) -> IndicatorSignal:
        """
        计算新闻情绪得分
        
        sentiment_score: -1 到 1，-1=极度负面，1=极度正面
        转换为 0-100 分数
        """
        # 将 -1~1 映射到 0-100
        normalized_score = (sentiment_score + 1) * 50
        
        if normalized_score >= 90:
            signal = "极度正面"
            emoji = "🟢"
        elif normalized_score >= 70:
            signal = "正面"
            emoji = "🟢"
        elif normalized_score >= 55:
            signal = "中性偏多"
            emoji = "🟡"
        elif normalized_score >= 45:
            signal = "中性"
            emoji = "🟡"
        elif normalized_score >= 30:
            signal = "负面"
            emoji = "🟠"
        else:
            signal = "极度负面"
            emoji = "🔴"
        
        return IndicatorSignal(
            name="新闻情绪",
            value=sentiment_score,
            signal=signal,
            score=normalized_score,
            weight=self.weights['sentiment'],
            emoji=emoji
        )
    
    def calculate_index(self, 
                       vix: float,
                       equity_bond_spread: float,
                       northbound_flow: float,
                       volume: float,
                       sentiment: float) -> Dict:
        """
        计算综合恐慌贪婪指数
        
        Args:
            vix: VIX 恐慌指数值
            equity_bond_spread: 股债性价比（股息率 - 国债收益率）
            northbound_flow: 北向资金净流入（亿元）
            volume: 市场成交量（亿元）
            sentiment: 新闻情绪得分（-1 到 1）
        
        Returns:
            Dict: 包含综合指数和各子指标
        """
        logger.info("[恐慌贪婪指数] 开始计算...")
        
        # 计算各指标得分
        vix_signal = self.calculate_vix_score(vix)
        equity_bond_signal = self.calculate_equity_bond_score(equity_bond_spread)
        northbound_signal = self.calculate_northbound_score(northbound_flow)
        volume_signal = self.calculate_volume_score(volume)
        sentiment_signal = self.calculate_sentiment_score(sentiment)
        
        indicators = [
            vix_signal,
            equity_bond_signal,
            northbound_signal,
            volume_signal,
            sentiment_signal
        ]
        
        # 计算加权综合得分
        weighted_score = sum(ind.score * ind.weight for ind in indicators)
        final_score = round(weighted_score)
        
        # 确定综合信号
        if final_score >= 80:
            overall_signal = "极度贪婪"
            overall_emoji = "🟢"
            overall_desc = "市场情绪极度乐观，警惕回调风险"
        elif final_score >= 65:
            overall_signal = "贪婪"
            overall_emoji = "🟢"
            overall_desc = "市场情绪乐观，保持谨慎"
        elif final_score >= 55:
            overall_signal = "中性偏贪婪"
            overall_emoji = "🟡"
            overall_desc = "市场情绪略偏乐观"
        elif final_score >= 45:
            overall_signal = "中性"
            overall_emoji = "⚪"
            overall_desc = "市场情绪中性，观望为主"
        elif final_score >= 35:
            overall_signal = "中性偏恐慌"
            overall_emoji = "🟡"
            overall_desc = "市场情绪略偏谨慎"
        elif final_score >= 20:
            overall_signal = "恐慌"
            overall_emoji = "🟠"
            overall_desc = "市场情绪悲观，关注机会"
        else:
            overall_signal = "极度恐慌"
            overall_emoji = "🔴"
            overall_desc = "市场情绪极度悲观，可能是买入机会"
        
        result = {
            'index_value': final_score,
            'signal': overall_signal,
            'emoji': overall_emoji,
            'description': overall_desc,
            'indicators': indicators,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info(f"[恐慌贪婪指数] 计算完成：{final_score} ({overall_signal})")
        
        return result
    
    def get_default_data(self) -> Dict:
        """获取默认数据（当真实数据不可用时）"""
        # 尝试从东方财富 API 获取北向资金实时数据
        try:
            import requests
            # 东方财富北向资金 API
            response = requests.get(
                'http://push2.eastmoney.com/api/qt/kamt.rtmin/get?fields1=f1,f3&fields2=f51,f52,f54,f56&ut=b2884a393a59ad6400f5a713890dc5c6&cb=jQuery',
                timeout=5
            )
            if response.status_code == 200:
                # 解析数据（简化版，实际需要更复杂的解析）
                # 北向净流入（亿元）
                data = response.json()
                northbound = data.get('data', {}).get('hk2sh', {}).get('netAmt', 0)
                northbound = float(northbound) / 10000  # 转换为亿元
                
                # 只有北向资金使用真实数据，其他仍用默认值
                return {
                    'vix': 15.2,
                    'equity_bond_spread': 0.2,
                    'northbound_flow': round(northbound, 1),
                    'volume': 8500,
                    'sentiment': 0.35
                }
        except Exception as e:
            logger.warning(f"[北向资金] 获取失败：{e}，使用默认值")
        
        # 兜底：使用默认值
        return {
            'vix': 15.2,
            'equity_bond_spread': 0.2,  # 2.8% - 2.6%
            'northbound_flow': 0.0,  # 改为 0，表示数据不可用
            'volume': 8500,
            'sentiment': 0.35
        }


def main():
    """测试主函数"""
    print("=" * 70)
    print("📊 恐慌贪婪指数计算器")
    print("=" * 70)
    print()
    
    calculator = FearGreedIndex()
    
    # 使用默认数据测试
    data = calculator.get_default_data()
    
    print("输入数据:")
    print(f"  VIX 恐慌指数：{data['vix']}")
    print(f"  股债性价比：{data['equity_bond_spread']}%")
    print(f"  北向资金：{data['northbound_flow']} 亿")
    print(f"  市场成交量：{data['volume']} 亿")
    print(f"  新闻情绪：{data['sentiment']}")
    print()
    
    # 计算指数
    result = calculator.calculate_index(
        vix=data['vix'],
        equity_bond_spread=data['equity_bond_spread'],
        northbound_flow=data['northbound_flow'],
        volume=data['volume'],
        sentiment=data['sentiment']
    )
    
    print("=" * 70)
    print("📈 恐慌贪婪指数结果")
    print("=" * 70)
    print()
    print(f"**恐慌贪婪指数**: {result['index_value']}（{result['emoji']} {result['signal']}）")
    print()
    print(f"**解读**: {result['description']}")
    print()
    print("**各指标详情**:")
    print()
    print("| 指标 | 数值 | 信号 |")
    print("|------|------|------|")
    
    for ind in result['indicators']:
        if ind.name == "股债性价比":
            value_str = f"{ind.value}%"
        elif ind.name == "北向资金":
            value_str = f"{ind.value:+.1f} 亿"
        elif ind.name == "市场成交量":
            value_str = f"{ind.value} 亿"
        elif ind.name == "新闻情绪":
            value_str = f"{ind.value:+.2f}"
        else:
            value_str = str(ind.value)
        
        print(f"| {ind.name} | {value_str} | {ind.emoji} {ind.signal} |")
    
    print()
    print(f"**更新时间**: {result['update_time']}")
    print()
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    main()
