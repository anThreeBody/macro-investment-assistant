#!/usr/bin/env python3
"""
系统测试脚本 - 验证 V8.0 重构是否成功
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """测试模块导入"""
    print("=" * 50)
    print("测试 1: 模块导入")
    print("=" * 50)
    
    try:
        from api.data_api import DataAPI
        print("✅ DataAPI 导入成功")
        
        from analyzers.technical import TechnicalAnalyzer
        from analyzers.sentiment import SentimentAnalyzer
        from analyzers.macro import MacroAnalyzer
        from analyzers.momentum import MomentumAnalyzer
        print("✅ 所有分析器导入成功")
        
        from predictors.multi_factor import MultiFactorPredictor
        print("✅ 多因子预测器导入成功")
        
        from data_sources import GoldDataSource, NewsDataSource, MacroDataSource
        print("✅ 所有数据源导入成功")
        
        from data_pipeline import DataCleaner, DataValidator, DataStorage
        print("✅ 数据管道导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败：{e}")
        return False

def test_data_api():
    """测试数据 API"""
    print("\n" + "=" * 50)
    print("测试 2: 数据 API")
    print("=" * 50)
    
    try:
        from api.data_api import DataAPI
        
        api = DataAPI()
        
        # 测试金价获取
        gold = api.get_gold_price()
        if gold.get('domestic', {}).get('price', 0) > 0:
            print(f"✅ 金价获取成功：¥{gold['domestic']['price']}")
        else:
            print("⚠️  金价数据为空（可能使用缓存）")
        
        # 测试宏观数据
        macro = api.get_macro()
        print(f"✅ 宏观数据获取成功")
        
        # 测试新闻
        news = api.get_news(days=1)
        print(f"✅ 新闻获取成功：{news.get('count', 0)}条")
        
        api.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据 API 测试失败：{e}")
        return False

def test_analyzers():
    """测试分析器"""
    print("\n" + "=" * 50)
    print("测试 3: 分析器")
    print("=" * 50)
    
    try:
        from analyzers.technical import TechnicalAnalyzer
        from analyzers.sentiment import SentimentAnalyzer
        from analyzers.macro import MacroAnalyzer
        from analyzers.momentum import MomentumAnalyzer
        
        # 测试技术分析器
        tech = TechnicalAnalyzer()
        tech_data = {
            'prices': [450 + i * 0.5 for i in range(60)],  # 模拟价格
            'current_price': 480.0,
        }
        tech_result = tech.analyze(tech_data)
        print(f"✅ 技术分析器工作正常：RSI={tech_result.get('rsi', 'N/A')}")
        
        # 测试情绪分析器
        sent = SentimentAnalyzer()
        sent_data = {
            'news': [
                {'title': '金价上涨，突破新高', 'content': '利好消息'},
                {'title': '市场风险增加', 'content': '利空消息'},
            ],
            'vix': 20.0,
        }
        sent_result = sent.analyze(sent_data)
        print(f"✅ 情绪分析器工作正常：得分={sent_result.get('score', 'N/A')}")
        
        # 测试宏观分析器
        macro = MacroAnalyzer()
        macro_data = {
            'dxy': {'value': 102.0},
            'vix': {'value': 20.0},
            'oil': {'value': 80.0},
            'treasury': {'10y': {'value': 4.0}},
        }
        macro_result = macro.analyze(macro_data)
        print(f"✅ 宏观分析器工作正常：风险环境={macro_result.get('risk_environment', 'N/A')}")
        
        # 测试动量分析器
        mom = MomentumAnalyzer()
        mom_data = {
            'prices': [450 + i * 0.5 for i in range(30)],
            'current_price': 465.0,
        }
        mom_result = mom.analyze(mom_data)
        print(f"✅ 动量分析器工作正常：信号={mom_result.get('signal', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析器测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False

def test_predictor():
    """测试预测器"""
    print("\n" + "=" * 50)
    print("测试 4: 预测器")
    print("=" * 50)
    
    try:
        from predictors.multi_factor import MultiFactorPredictor
        
        predictor = MultiFactorPredictor()
        
        # 准备测试数据
        test_data = {
            'gold': {
                'domestic': {'price': 480.0},
                'international': {'price': 2000.0},
            },
            'news': {
                'news': [
                    {'title': '金价上涨', 'content': '利好'},
                ],
            },
            'macro': {
                'dxy': {'value': 102.0},
                'vix': {'value': 20.0},
                'oil': {'value': 80.0},
                'treasury': {'10y': {'value': 4.0}},
            },
            'prices': [450 + i * 0.5 for i in range(60)],
        }
        
        prediction = predictor.predict(test_data)
        
        print(f"✅ 预测器工作正常")
        print(f"   当前价格：¥{prediction.get('current_price', 'N/A')}")
        print(f"   预测价格：¥{prediction.get('predicted_price', 'N/A')}")
        print(f"   预测方向：{prediction.get('direction_label', 'N/A')}")
        print(f"   置信度：{prediction.get('confidence', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 预测器测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 50)
    print("🧪 投资分析系统 V8.0 - 系统测试")
    print("=" * 50)
    
    results = []
    
    results.append(("模块导入", test_imports()))
    results.append(("数据 API", test_data_api()))
    results.append(("分析器", test_analyzers()))
    results.append(("预测器", test_predictor()))
    
    # 汇总
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    print(f"\n总计：{passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统重构成功！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查")
        return 1

if __name__ == '__main__':
    sys.exit(main())
