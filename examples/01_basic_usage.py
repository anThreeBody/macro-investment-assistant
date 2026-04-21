#!/usr/bin/env python3
"""
示例 1: 基础使用 - 生成每日简报

展示如何使用投资分析系统生成完整的每日简报。
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.data_api import DataAPI
from predictors.multi_factor import MultiFactorPredictor
from presenters.brief_generator import BriefGenerator


def main():
    """生成每日简报"""
    print("=" * 60)
    print("投资分析系统 - 基础使用示例")
    print("=" * 60)
    
    # 1. 初始化组件
    print("\n1️⃣  初始化系统组件...")
    api = DataAPI()
    predictor = MultiFactorPredictor()
    gen = BriefGenerator()
    print("   ✅ 完成")
    
    # 2. 获取数据
    print("\n2️⃣  获取市场数据...")
    data = api.get_all_data()
    
    # 显示数据摘要
    gold = data.get('gold', {})
    print(f"   📊 国际金价：${gold.get('international', {}).get('price', 0):.2f}/盎司")
    print(f"   📊 国内金价：¥{gold.get('domestic', {}).get('price', 0):.2f}/克")
    
    macro = data.get('macro', {})
    print(f"   📈 DXY: {macro.get('dxy', {}).get('value', 0):.2f}")
    print(f"   📈 VIX: {macro.get('vix', {}).get('value', 0):.2f}")
    
    news = data.get('news', {})
    print(f"   📰 新闻数量：{len(news.get('items', []))}")
    print("   ✅ 完成")
    
    # 3. 生成预测
    print("\n3️⃣  生成价格预测...")
    prediction = predictor.predict(data)
    
    print(f"   🔮 当前价格：¥{prediction['current_price']:.2f}")
    print(f"   🔮 预测价格：¥{prediction['predicted_price']:.2f}")
    print(f"   🔮 方向：{prediction['direction']}")
    print(f"   🔮 置信度：{prediction['confidence']}")
    print(f"   🔮 信号：{prediction['signal']}")
    print("   ✅ 完成")
    
    # 4. 生成简报
    print("\n4️⃣  生成每日简报...")
    brief_content = gen.generate(data, prediction)
    
    # 显示简报前 500 字符
    print("\n📝 简报预览:")
    print("-" * 60)
    print(brief_content[:500] + "...")
    print("-" * 60)
    print("   ✅ 完成")
    
    # 5. 保存简报
    from datetime import datetime
    date_str = datetime.now().strftime('%Y%m%d')
    output_file = f'daily_brief/brief_example_{date_str}.md'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(brief_content)
    
    print(f"\n💾 简报已保存：{output_file}")
    print("\n✅ 示例完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
