#!/usr/bin/env python3
"""
基金分析服务
整合个性化推荐、买卖点建议、理由增强
"""

import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

# 导入相关模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.fund_recommender import FundRecommender, RiskProfile, generate_sample_funds
from analyzers.fund_timing_advisor import FundTimingAdvisor
from analyzers.fund_reason_enhancer import FundReasonEnhancer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FundAnalysisService:
    """基金分析服务"""
    
    def __init__(self):
        self.recommender = FundRecommender()
        self.timing_advisor = FundTimingAdvisor()
        self.reason_enhancer = FundReasonEnhancer()
        
        logger.info("[基金服务] 初始化完成")
    
    def get_personalized_recommendations(self, 
                                       risk_profile: RiskProfile,
                                       top_n: int = 5) -> Dict:
        """
        获取个性化基金推荐
        
        Args:
            risk_profile: 风险偏好
            top_n: 推荐数量
            
        Returns:
            推荐结果
        """
        # 获取基金池
        funds = generate_sample_funds()
        
        # 获取推荐
        recommendations = self.recommender.recommend(funds, risk_profile, top_n)
        
        # 获取组合建议
        portfolio = self.recommender.get_portfolio_suggestion(risk_profile)
        
        # 格式化推荐
        formatted_recommendations = []
        for fund, score, reason in recommendations:
            formatted_recommendations.append({
                "code": fund.code,
                "name": fund.name,
                "category": fund.category,
                "risk_level": fund.risk_level,
                "return_1y": fund.return_1y,
                "volatility": fund.volatility,
                "max_drawdown": fund.max_drawdown,
                "fund_size": fund.fund_size,
                "score": score,
                "reason": reason
            })
        
        return {
            "risk_profile": risk_profile.value,
            "portfolio_suggestion": portfolio,
            "recommendations": formatted_recommendations,
            "total_recommended": len(formatted_recommendations)
        }
    
    def get_timing_advice(self, fund_code: str, fund_name: str,
                         current_nav: float, nav_history: List[float],
                         fund_info: Dict, market_data: Dict) -> Dict:
        """
        获取买卖点建议
        
        Returns:
            交易建议
        """
        # 生成信号
        signal = self.timing_advisor.generate_signal(
            fund_code, fund_name, current_nav,
            nav_history, fund_info, market_data
        )
        
        # 获取策略
        if signal.action == "BUY":
            strategy = self.timing_advisor.get_buying_strategy(signal)
        elif signal.action == "SELL":
            strategy = self.timing_advisor.get_selling_strategy(signal)
        else:
            strategy = "当前建议持有观望"
        
        return {
            "fund_code": signal.fund_code,
            "fund_name": signal.fund_name,
            "action": signal.action,
            "strength": signal.strength,
            "confidence": signal.confidence,
            "current_nav": signal.current_nav,
            "target_price": signal.target_price,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "reason": signal.reason,
            "technical_factors": signal.technical_factors,
            "fundamental_factors": signal.fundamental_factors,
            "sentiment_factors": signal.sentiment_factors,
            "strategy": strategy,
            "timestamp": signal.timestamp
        }
    
    def get_enhanced_reason(self, fund_name: str, fund_category: str,
                           policy_news: List[str], fund_flow: float,
                           market_sentiment: str,
                           performance_data: Dict) -> Dict:
        """
        获取增强推荐理由
        
        Returns:
            增强理由
        """
        reason = self.reason_enhancer.generate_enhanced_reason(
            fund_name, fund_category,
            policy_news, fund_flow, market_sentiment,
            performance_data
        )
        
        return {
            "confidence_score": reason.confidence_score,
            "key_factors": reason.key_factors,
            "policy_analysis": reason.policy_analysis,
            "sentiment_analysis": reason.sentiment_analysis,
            "performance_analysis": reason.performance_analysis,
            "risk_analysis": reason.risk_analysis,
            "overall_reason": reason.overall_reason,
            "warnings": reason.warnings,
            "full_report": self.reason_enhancer.format_reason_report(reason)
        }
    
    def generate_fund_report(self, risk_profile: RiskProfile) -> str:
        """生成基金分析报告"""
        # 获取推荐
        recommendations = self.get_personalized_recommendations(risk_profile)
        
        # 构建报告
        report = f"""
# 📊 基金分析报告

**风险偏好**: {recommendations['risk_profile']}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 💼 组合配置建议

{recommendations['portfolio_suggestion']['description']}

| 类型 | 配置比例 |
|------|----------|
"""
        
        for fund_type, percentage in recommendations['portfolio_suggestion'].items():
            if fund_type != 'description':
                report += f"| {fund_type} | {percentage}% |\n"
        
        report += f"""
---

## ⭐ 推荐基金 (Top {recommendations['total_recommended']})

"""
        
        for i, rec in enumerate(recommendations['recommendations'], 1):
            report += f"""
### {i}. {rec['name']} ({rec['code']})

- **类型**: {rec['category']} | **风险等级**: {rec['risk_level']}
- **近1年收益**: {rec['return_1y']*100:.1f}% | **波动率**: {rec['volatility']*100:.1f}%
- **最大回撤**: {rec['max_drawdown']*100:.1f}% | **规模**: {rec['fund_size']}亿
- **综合得分**: {rec['score']:.1f}
- **推荐理由**: {rec['reason']}

---

"""
        
        report += f"""
## ⚠️ 风险提示

1. 基金投资有风险，过往业绩不代表未来表现
2. 请根据自身风险承受能力选择合适产品
3. 建议分散投资，不要集中单一基金
4. 定期关注基金净值变化和基金经理变动
5. 长期投资更有利于平滑短期波动

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
        """.strip()
        
        return report
    
    def interactive_assessment(self) -> RiskProfile:
        """交互式风险评估"""
        print("\n" + "="*70)
        print("🎯 风险偏好评估")
        print("="*70)
        
        print("\n请回答以下问题（帮助我们了解您的风险偏好）：\n")
        
        # 年龄
        age = int(input("1. 您的年龄: "))
        
        # 投资期限
        print("\n2. 您的投资期限:")
        print("   1) 1年以内")
        print("   2) 1-3年")
        print("   3) 3-5年")
        print("   4) 5-10年")
        print("   5) 10年以上")
        horizon_choice = int(input("   请选择 (1-5): "))
        horizon_map = {1: 1, 2: 2, 3: 4, 4: 7, 5: 15}
        investment_horizon = horizon_map.get(horizon_choice, 5)
        
        # 收入稳定性
        print("\n3. 您的收入稳定性:")
        print("   1) 不稳定")
        print("   2) 一般")
        print("   3) 稳定")
        stability_choice = int(input("   请选择 (1-3): "))
        stability_map = {1: "unstable", 2: "moderate", 3: "stable"}
        income_stability = stability_map.get(stability_choice, "moderate")
        
        # 风险承受能力
        print("\n4. 您能承受的最大亏损:")
        print("   1) 5%以内")
        print("   2) 10%以内")
        print("   3) 20%以内")
        print("   4) 30%以内")
        print("   5) 30%以上")
        risk_choice = int(input("   请选择 (1-5): "))
        risk_map = {1: "low", 2: "low", 3: "medium", 4: "high", 5: "high"}
        risk_tolerance = risk_map.get(risk_choice, "medium")
        
        # 投资经验
        print("\n5. 您的投资经验:")
        print("   1) 新手")
        print("   2) 有一定经验")
        print("   3) 经验丰富")
        exp_choice = int(input("   请选择 (1-3): "))
        exp_map = {1: "novice", 2: "intermediate", 3: "expert"}
        investment_experience = exp_map.get(exp_choice, "intermediate")
        
        # 评估风险偏好
        risk_profile = self.recommender.assess_risk_profile(
            age=age,
            investment_horizon=investment_horizon,
            income_stability=income_stability,
            risk_tolerance=risk_tolerance,
            investment_experience=investment_experience
        )
        
        print(f"\n{'='*70}")
        print(f"🎭 评估结果: {risk_profile.value}")
        print(f"{'='*70}")
        
        config = self.recommender.risk_configs[risk_profile]
        print(f"\n📋 配置说明: {config['description']}")
        print(f"   最大风险等级: {config['max_risk_level']}")
        print(f"   最低1年收益: {config['min_return_1y']*100:.1f}%")
        print(f"   最大波动率: {config['max_volatility']*100:.1f}%")
        print(f"   最大回撤: {config['max_drawdown']*100:.1f}%")
        
        return risk_profile


def demo_fund_service():
    """演示基金服务"""
    print("="*70)
    print("🎯 基金分析服务演示")
    print("="*70)
    
    service = FundAnalysisService()
    
    # 1. 个性化推荐
    print("\n" + "="*70)
    print("1️⃣ 个性化基金推荐")
    print("="*70)
    
    risk_profile = RiskProfile.BALANCED
    print(f"\n风险偏好: {risk_profile.value}")
    
    recommendations = service.get_personalized_recommendations(risk_profile, top_n=3)
    
    print(f"\n💼 组合配置建议:")
    for fund_type, percentage in recommendations['portfolio_suggestion'].items():
        if fund_type != 'description':
            print(f"  {fund_type}: {percentage}%")
    print(f"  说明: {recommendations['portfolio_suggestion']['description']}")
    
    print(f"\n⭐ 推荐基金:")
    for i, rec in enumerate(recommendations['recommendations'], 1):
        print(f"\n  {i}. {rec['name']} ({rec['code']})")
        print(f"     类型: {rec['category']} | 风险: {rec['risk_level']}")
        print(f"     收益: {rec['return_1y']*100:.1f}% | 回撤: {rec['max_drawdown']*100:.1f}%")
        print(f"     得分: {rec['score']:.1f}")
        print(f"     理由: {rec['reason']}")
    
    # 2. 买卖点建议
    print("\n" + "="*70)
    print("2️⃣ 买卖点建议")
    print("="*70)
    
    fund_code = "005911"
    fund_name = "广发双擎升级混合A"
    current_nav = 2.4567
    
    nav_history = [
        2.60, 2.58, 2.59, 2.57, 2.55, 2.56, 2.54, 2.52, 2.53, 2.51,
        2.50, 2.48, 2.49, 2.47, 2.46, 2.45, 2.44, 2.45, 2.43, 2.42,
        2.44, 2.43, 2.45, 2.44, 2.46, 2.45, 2.46, 2.45, 2.47, 2.4567
    ]
    
    fund_info = {
        "manager_score": 4.2,
        "fund_size": 60,
        "expense_ratio": 0.015,
        "return_1y": 0.18
    }
    
    market_data = {
        "market_sentiment": "neutral",
        "fund_flow": 50,
        "policy": "supportive"
    }
    
    timing = service.get_timing_advice(
        fund_code, fund_name, current_nav,
        nav_history, fund_info, market_data
    )
    
    print(f"\n📊 基金: {timing['fund_name']}")
    print(f"操作建议: {timing['action']}")
    print(f"信号强度: {timing['strength']}")
    print(f"置信度: {timing['confidence']:.1%}")
    print(f"当前净值: {timing['current_nav']:.4f}")
    print(f"目标价格: {timing['target_price']:.4f}")
    print(f"止损价格: {timing['stop_loss']:.4f}")
    print(f"止盈价格: {timing['take_profit']:.4f}")
    
    # 3. 增强理由
    print("\n" + "="*70)
    print("3️⃣ 增强推荐理由")
    print("="*70)
    
    policy_news = [
        "国家支持科技创新政策出台",
        "数字经济获得政策扶持",
        "半导体产业迎来利好"
    ]
    
    performance_data = {
        "return_1m": 0.05,
        "return_3m": 0.12,
        "return_6m": 0.18,
        "return_1y": 0.25,
        "benchmark_return": 0.15,
        "alpha": 0.10,
        "sharpe_ratio": 1.3,
        "max_drawdown": 0.18
    }
    
    enhanced = service.get_enhanced_reason(
        fund_name, "科技成长",
        policy_news, 150.5, "neutral",
        performance_data
    )
    
    print(f"\n✅ 置信度: {enhanced['confidence_score']:.1%}")
    print(f"✅ 关键因素: {', '.join(enhanced['key_factors'])}")
    print(f"\n📰 政策: {enhanced['policy_analysis']}")
    print(f"😊 情绪: {enhanced['sentiment_analysis']}")
    print(f"📈 业绩: {enhanced['performance_analysis']}")
    
    # 4. 生成报告
    print("\n" + "="*70)
    print("4️⃣ 生成基金分析报告")
    print("="*70)
    
    report = service.generate_fund_report(RiskProfile.MODERATE)
    print(report[:800] + "...")
    
    # 保存报告
    report_file = Path(__file__).parent.parent / "daily_brief" / f"fund_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存: {report_file}")
    
    print("\n" + "="*70)
    print("✅ 基金分析服务演示完成!")
    print("="*70)


if __name__ == "__main__":
    demo_fund_service()
