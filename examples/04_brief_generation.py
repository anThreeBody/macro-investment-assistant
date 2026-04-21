#!/usr/bin/env python3
"""
示例 4: 简报生成 - 生成完整的每日简报和图表

展示如何使用输出生成器创建简报和可视化图表。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.data_api import DataAPI
from predictors.multi_factor import MultiFactorPredictor
from presenters.brief_generator import BriefGenerator
from presenters.chart_generator import ChartGenerator


def main():
    """简报生成示例"""
    print("=" * 60)
    print("投资分析系统 - 简报生成示例")
    print("=" * 60)
    
    # 1. 获取数据和预测
    print("\n1️⃣  获取数据和预测...")
    api = DataAPI()
    data = api.get_all_data()
    
    predictor = MultiFactorPredictor()
    prediction = predictor.predict(data)
    print("   ✅ 完成")
    
    # 2. 生成简报
    print("\n2️⃣  生成 Markdown 简报...")
    gen = BriefGenerator()
    brief_content = gen.generate(data, prediction)
    
    # 显示简报结构
    sections = ['市场概览', '金价分析', '宏观数据', '新闻资讯', '价格预测', '风险提示']
    print("   简报包含以下部分:")
    for section in sections:
        print(f"     - {section}")
    print("   ✅ 完成")
    
    # 3. 保存简报
    from datetime import datetime
    date_str = datetime.now().strftime('%Y%m%d')
    brief_file = f'daily_brief/brief_example_{date_str}.md'
    
    with open(brief_file, 'w', encoding='utf-8') as f:
        f.write(brief_content)
    
    print(f"\n3️⃣  简报已保存：{brief_file}")
    
    # 4. 生成图表
    print("\n4️⃣  生成可视化图表...")
    chart_gen = ChartGenerator()
    
    # 获取历史价格
    prices = data.get('prices', [])
    
    if prices:
        # 价格趋势图
        chart1 = chart_gen.generate_price_chart(prices, title="金价走势")
        print(f"   📊 价格趋势图：{chart1}")
        
        # 预测对比图
        current_price = data.get('gold', {}).get('domestic', {}).get('price', 0)
        chart2 = chart_gen.generate_prediction_chart(current_price, prediction)
        print(f"   📊 预测对比图：{chart2}")
    
    # 因子热力图
    analysis = prediction.get('analysis', {})
    scores = analysis.get('scores', {})
    weights = analysis.get('weights', {})
    
    chart3 = chart_gen.generate_factor_heatmap(scores, weights)
    print(f"   📊 因子热力图：{chart3}")
    
    print("   ✅ 完成")
    
    # 5. 显示简报预览
    print("\n5️⃣  简报预览 (前 800 字符):")
    print("-" * 60)
    print(brief_content[:800] + "...")
    print("-" * 60)
    
    # 6. 统计信息
    print("\n📊 统计信息:")
    print("-" * 60)
    print(f"简报长度：   {len(brief_content)} 字符")
    print(f"图表数量：   3 张")
    print(f"输出文件：   {brief_file}")
    if prices:
        print(f"历史数据：   {len(prices)} 天")
    
    print("\n✅ 示例完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
