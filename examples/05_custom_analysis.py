#!/usr/bin/env python3
"""
示例 5: 自定义分析 - 使用各个分析器进行独立分析

展示如何单独使用技术、情感、宏观、动量分析器。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.data_api import DataAPI
from analyzers.technical import TechnicalAnalyzer
from analyzers.sentiment import SentimentAnalyzer
from analyzers.macro import MacroAnalyzer
from analyzers.momentum import MomentumAnalyzer


def main():
    """自定义分析示例"""
    print("=" * 60)
    print("投资分析系统 - 自定义分析示例")
    print("=" * 60)
    
    # 1. 获取数据
    print("\n1️⃣  获取市场数据...")
    api = DataAPI()
    data = api.get_all_data()
    print("   ✅ 完成")
    
    # 2. 技术分析
    print("\n2️⃣  技术分析 (Technical Analysis)...")
    print("-" * 60)
    
    tech_analyzer = TechnicalAnalyzer()
    tech_result = tech_analyzer.analyze(data)
    
    print(f"RSI:          {tech_result.get('rsi', 0):.2f}")
    print(f"MACD:         {tech_result.get('macd', 0):.2f}")
    print(f"MACD Signal:  {tech_result.get('macd_signal', 0):.2f}")
    print(f"5 日均线：     {tech_result.get('ma_5', 0):.2f}")
    print(f"10 日均线：    {tech_result.get('ma_10', 0):.2f}")
    print(f"20 日均线：    {tech_result.get('ma_20', 0):.2f}")
    print(f"趋势：        {tech_result.get('trend', 'N/A')}")
    print(f"得分：        {tech_result.get('score', 0):.3f}")
    print(f"信号：        {tech_result.get('signal', 'N/A')}")
    
    # 3. 情感分析
    print("\n3️⃣  情感分析 (Sentiment Analysis)...")
    print("-" * 60)
    
    sent_analyzer = SentimentAnalyzer()
    sent_result = sent_analyzer.analyze(data)
    
    print(f"平均情感：    {sent_result.get('avg_sentiment', 0):.3f}")
    print(f"正面新闻：    {sent_result.get('positive_count', 0)} 条")
    print(f"负面新闻：    {sent_result.get('negative_count', 0)} 条")
    print(f"中性新闻：    {sent_result.get('neutral_count', 0)} 条")
    print(f"得分：        {sent_result.get('score', 0):.3f}")
    print(f"信号：        {sent_result.get('signal', 'N/A')}")
    
    # 4. 宏观分析
    print("\n4️⃣  宏观分析 (Macro Analysis)...")
    print("-" * 60)
    
    macro_analyzer = MacroAnalyzer()
    macro_result = macro_analyzer.analyze(data)
    
    print(f"DXY 影响：     {macro_result.get('dxy_impact', 0):.3f}")
    print(f"VIX 影响：     {macro_result.get('vix_impact', 0):.3f}")
    print(f"原油影响：    {macro_result.get('oil_impact', 0):.3f}")
    print(f"美债影响：    {macro_result.get('treasury_impact', 0):.3f}")
    print(f"整体影响：    {macro_result.get('overall_impact', 'N/A')}")
    print(f"得分：        {macro_result.get('score', 0):.3f}")
    print(f"信号：        {macro_result.get('signal', 'N/A')}")
    
    # 5. 动量分析
    print("\n5️⃣  动量分析 (Momentum Analysis)...")
    print("-" * 60)
    
    momentum_analyzer = MomentumAnalyzer()
    momentum_result = momentum_analyzer.analyze(data)
    
    print(f"趋势强度：    {momentum_result.get('trend_strength', 0):.3f}")
    print(f"动量得分：    {momentum_result.get('momentum_score', 0):.3f}")
    print(f"加速度：      {momentum_result.get('acceleration', 0):.3f}")
    print(f"得分：        {momentum_result.get('score', 0):.3f}")
    print(f"信号：        {momentum_result.get('signal', 'N/A')}")
    
    # 6. 综合分析
    print("\n6️⃣  综合分析...")
    print("-" * 60)
    
    scores = [
        tech_result.get('score', 0),
        sent_result.get('score', 0),
        macro_result.get('score', 0),
        momentum_result.get('score', 0)
    ]
    
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    print(f"平均得分：    {avg_score:.3f}")
    print(f"最高得分：    {max_score:.3f}")
    print(f"最低得分：    {min_score:.3f}")
    print(f"分歧度：      {max_score - min_score:.3f}")
    
    # 7. 生成自定义信号
    print("\n7️⃣  生成自定义交易信号...")
    print("-" * 60)
    
    if avg_score > 0.7:
        signal = "强烈买入"
    elif avg_score > 0.6:
        signal = "买入"
    elif avg_score > 0.4:
        signal = "持有"
    elif avg_score > 0.3:
        signal = "卖出"
    else:
        signal = "强烈卖出"
    
    print(f"自定义信号：  {signal}")
    print(f"置信度：      {'高' if avg_score > 0.7 or avg_score < 0.3 else '中' if avg_score > 0.5 else '低'}")
    
    print("\n✅ 示例完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
