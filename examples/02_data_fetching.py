#!/usr/bin/env python3
"""
示例 2: 数据获取 - 获取金价、宏观、新闻数据

展示如何使用 DataAPI 获取各类市场数据。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.data_api import DataAPI


def main():
    """数据获取示例"""
    print("=" * 60)
    print("投资分析系统 - 数据获取示例")
    print("=" * 60)
    
    # 初始化 API
    api = DataAPI()
    
    # ==================== 1. 获取金价数据 ====================
    print("\n📊 1. 金价数据")
    print("-" * 60)
    
    gold = api.get_gold_price(use_cache=True)
    
    international = gold.get('international', {})
    domestic = gold.get('domestic', {})
    
    print(f"国际金价:")
    print(f"  价格：${international.get('price', 0):.2f}/盎司")
    print(f"  涨跌：{international.get('change', 0):+.2f} ({international.get('change_pct', 0):+.2f}%)")
    print(f"  来源：{international.get('source', 'N/A')}")
    
    print(f"\n国内金价:")
    print(f"  价格：¥{domestic.get('price', 0):.2f}/克")
    print(f"  涨跌：{domestic.get('change', 0):+.2f} ({domestic.get('change_pct', 0):+.2f}%)")
    print(f"  来源：{domestic.get('source', 'N/A')}")
    
    # ==================== 2. 获取宏观数据 ====================
    print("\n📈 2. 宏观数据")
    print("-" * 60)
    
    macro = api.get_macro_data()
    
    indicators = ['dxy', 'vix', 'oil', 'treasury']
    names = {
        'dxy': '美元指数',
        'vix': '恐慌指数',
        'oil': '原油价格',
        'treasury': '美债收益率'
    }
    
    for key in indicators:
        data = macro.get(key, {})
        name = names.get(key, key)
        value = data.get('value', 0)
        change = data.get('change', 0)
        source = data.get('source', 'N/A')
        
        unit = '%' if key == 'treasury' else ''
        print(f"{name}: {value:.2f}{unit} ({change:+.2f}) [来源：{source}]")
    
    # ==================== 3. 获取新闻数据 ====================
    print("\n📰 3. 新闻数据")
    print("-" * 60)
    
    news = api.get_news(limit=5)
    items = news.get('items', [])
    
    print(f"新闻总数：{len(items)}")
    print(f"平均情感：{news.get('avg_sentiment', 0):.2f}")
    
    for i, item in enumerate(items, 1):
        print(f"\n{i}. {item.get('title', 'N/A')}")
        print(f"   来源：{item.get('source', 'N/A')}")
        print(f"   时间：{item.get('publish_time', 'N/A')}")
        print(f"   情感：{item.get('sentiment', 0):.2f}")
    
    # ==================== 4. 获取历史价格 ====================
    print("\n📉 4. 历史价格")
    print("-" * 60)
    
    history = api.get_gold_history(days=7)
    
    print(f"获取 {len(history)} 天的历史价格:")
    for entry in history[-5:]:  # 显示最近 5 天
        date = entry.get('date', 'N/A')
        price = entry.get('price', 0)
        print(f"  {date}: ¥{price:.2f}/克")
    
    # ==================== 5. 数据质量检查 ====================
    print("\n✅ 5. 数据质量检查")
    print("-" * 60)
    
    from data_pipeline.validator import DataValidator
    
    validator = DataValidator()
    
    # 检查金价
    gold_valid, gold_errors = validator.validate(gold, 'gold')
    print(f"金价数据：{'✅ 有效' if gold_valid else '❌ 无效'}")
    if not gold_valid:
        print(f"  错误：{gold_errors}")
    
    # 检查宏观数据
    macro_valid, macro_errors = validator.validate(macro, 'macro')
    print(f"宏观数据：{'✅ 有效' if macro_valid else '❌ 无效'}")
    if not macro_valid:
        print(f"  错误：{macro_errors}")
    
    print("\n✅ 示例完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
