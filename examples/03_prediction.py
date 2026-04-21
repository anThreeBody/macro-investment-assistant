#!/usr/bin/env python3
"""
示例 3: 预测生成 - 使用多因子模型生成价格预测

展示如何使用预测引擎生成价格预测。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.data_api import DataAPI
from predictors.multi_factor import MultiFactorPredictor


def main():
    """预测生成示例"""
    print("=" * 60)
    print("投资分析系统 - 预测生成示例")
    print("=" * 60)
    
    # 1. 获取数据
    print("\n1️⃣  获取市场数据...")
    api = DataAPI()
    data = api.get_all_data()
    current_price = data.get('gold', {}).get('domestic', {}).get('price', 0)
    print(f"   当前金价：¥{current_price:.2f}/克")
    
    # 2. 生成预测
    print("\n2️⃣  生成多因子预测...")
    predictor = MultiFactorPredictor()
    prediction = predictor.predict(data)
    
    # 3. 显示预测结果
    print("\n3️⃣  预测结果:")
    print("-" * 60)
    print(f"当前价格：   ¥{prediction['current_price']:.2f}")
    print(f"预测价格：   ¥{prediction['predicted_price']:.2f}")
    print(f"置信区间：   [¥{prediction['price_lower']:.2f}, ¥{prediction['price_upper']:.2f}]")
    print(f"方向：       {prediction['direction']}")
    print(f"置信度：     {prediction['confidence']}")
    print(f"交易信号：   {prediction['signal']}")
    
    # 4. 显示因子分析
    print("\n4️⃣  因子分析:")
    print("-" * 60)
    
    analysis = prediction.get('analysis', {})
    scores = analysis.get('scores', {})
    weights = analysis.get('weights', {})
    
    factor_names = {
        'technical': '技术面',
        'sentiment': '情绪面',
        'macro': '宏观面',
        'momentum': '动量面',
        'time_series': '时序预测'
    }
    
    print(f"{'因子':<10} {'得分':<8} {'权重':<8} {'贡献':<8}")
    print("-" * 60)
    
    for factor_key, factor_name in factor_names.items():
        score = scores.get(factor_key, 0)
        weight = weights.get(factor_key, 0)
        contribution = score * weight
        
        # 得分可视化
        score_bar = '█' * int(score * 10)
        
        print(f"{factor_name:<10} {score:.3f} {score_bar:<8} {weight:.2%}    {contribution:.3f}")
    
    # 5. 显示时序预测
    print("\n5️⃣  时序预测:")
    print("-" * 60)
    
    ts = prediction.get('time_series', {})
    if ts:
        print(f"预测价格：   ¥{ts.get('predicted_price', 0):.2f}")
        print(f"趋势：       {ts.get('trend', 'N/A')}")
        print(f"置信度：     {ts.get('confidence', 'N/A')}")
    
    # 6. 保存预测
    print("\n6️⃣  保存预测到数据库...")
    from predictors.validator import PredictionValidator
    
    validator = PredictionValidator()
    validator.save(prediction, data)
    print("   ✅ 预测已保存，等待次日验证")
    
    # 7. 解释说明
    print("\n📝 预测说明:")
    print("-" * 60)
    print("• 多因子模型综合了技术面、情绪面、宏观面、动量面四个维度")
    print("• 时序预测作为补充，提供统计视角的预测")
    print("• 置信度基于各因子的一致性和历史准确率")
    print("• 预测结果仅供参考，不构成投资建议")
    
    print("\n✅ 示例完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
