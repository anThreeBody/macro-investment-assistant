#!/usr/bin/env python3
"""
基金个性化推荐系统
根据用户风险偏好推荐基金
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskProfile(Enum):
    """风险偏好类型"""
    CONSERVATIVE = "保守型"      # 低风险，追求稳定收益
    MODERATE = "稳健型"          # 中等风险，平衡收益
    BALANCED = "平衡型"          # 风险收益平衡
    AGGRESSIVE = "进取型"        # 较高风险，追求高收益
    SPECULATIVE = "激进型"       # 高风险，追求最大收益


@dataclass
class FundProfile:
    """基金档案"""
    code: str
    name: str
    category: str           # 股票型、债券型、混合型、指数型、QDII
    risk_level: int         # 1-5，1最低，5最高
    return_1y: float        # 近1年收益率
    return_3y: float        # 近3年收益率
    volatility: float       # 波动率
    sharpe_ratio: float     # 夏普比率
    max_drawdown: float     # 最大回撤
    fund_size: float        # 基金规模（亿）
    manager_score: float    # 基金经理评分
    expense_ratio: float    # 管理费率


class FundRecommender:
    """基金推荐器"""
    
    def __init__(self):
        # 风险偏好配置
        self.risk_configs = {
            RiskProfile.CONSERVATIVE: {
                "max_risk_level": 2,
                "min_return_1y": 0.02,
                "max_volatility": 0.10,
                "max_drawdown": 0.05,
                "categories": ["债券型", "货币型"],
                "description": "追求本金安全，接受较低收益"
            },
            RiskProfile.MODERATE: {
                "max_risk_level": 3,
                "min_return_1y": 0.03,
                "max_volatility": 0.15,
                "max_drawdown": 0.10,
                "categories": ["债券型", "混合型", "指数型"],
                "description": "平衡风险与收益，稳健增值"
            },
            RiskProfile.BALANCED: {
                "max_risk_level": 3,
                "min_return_1y": 0.05,
                "max_volatility": 0.20,
                "max_drawdown": 0.15,
                "categories": ["混合型", "指数型", "股票型"],
                "description": "风险收益平衡，适度进取"
            },
            RiskProfile.AGGRESSIVE: {
                "max_risk_level": 4,
                "min_return_1y": 0.08,
                "max_volatility": 0.30,
                "max_drawdown": 0.25,
                "categories": ["股票型", "混合型", "QDII"],
                "description": "追求较高收益，能承受较大波动"
            },
            RiskProfile.SPECULATIVE: {
                "max_risk_level": 5,
                "min_return_1y": 0.10,
                "max_volatility": 0.50,
                "max_drawdown": 0.40,
                "categories": ["股票型", "QDII", "行业主题"],
                "description": "追求最大收益，能承受大幅回撤"
            }
        }
        
        logger.info("[基金推荐] 初始化完成")
    
    def assess_risk_profile(self, 
                          age: Optional[int] = None,
                          investment_horizon: Optional[int] = None,
                          income_stability: Optional[str] = None,
                          risk_tolerance: Optional[str] = None,
                          investment_experience: Optional[str] = None) -> RiskProfile:
        """
        评估用户风险偏好
        
        Args:
            age: 年龄
            investment_horizon: 投资期限（年）
            income_stability: 收入稳定性 (stable/moderate/unstable)
            risk_tolerance: 风险承受能力 (low/medium/high)
            investment_experience: 投资经验 (novice/intermediate/expert)
            
        Returns:
            RiskProfile: 风险偏好类型
        """
        score = 0
        
        # 年龄评分 (年轻=高分)
        if age:
            if age < 30:
                score += 4
            elif age < 40:
                score += 3
            elif age < 50:
                score += 2
            elif age < 60:
                score += 1
            else:
                score += 0
        
        # 投资期限评分
        if investment_horizon:
            if investment_horizon >= 10:
                score += 4
            elif investment_horizon >= 5:
                score += 3
            elif investment_horizon >= 3:
                score += 2
            elif investment_horizon >= 1:
                score += 1
            else:
                score += 0
        
        # 收入稳定性评分
        if income_stability:
            if income_stability == "stable":
                score += 2
            elif income_stability == "moderate":
                score += 1
            else:
                score += 0
        
        # 风险承受能力评分
        if risk_tolerance:
            if risk_tolerance == "high":
                score += 3
            elif risk_tolerance == "medium":
                score += 2
            else:
                score += 1
        
        # 投资经验评分
        if investment_experience:
            if investment_experience == "expert":
                score += 3
            elif investment_experience == "intermediate":
                score += 2
            else:
                score += 1
        
        # 根据总分确定风险偏好
        if score >= 12:
            return RiskProfile.SPECULATIVE
        elif score >= 9:
            return RiskProfile.AGGRESSIVE
        elif score >= 6:
            return RiskProfile.BALANCED
        elif score >= 4:
            return RiskProfile.MODERATE
        else:
            return RiskProfile.CONSERVATIVE
    
    def filter_funds(self, funds: List[FundProfile], 
                    risk_profile: RiskProfile) -> List[FundProfile]:
        """根据风险偏好筛选基金"""
        config = self.risk_configs[risk_profile]
        
        filtered = []
        for fund in funds:
            # 风险等级检查
            if fund.risk_level > config["max_risk_level"]:
                continue
            
            # 收益率检查
            if fund.return_1y < config["min_return_1y"]:
                continue
            
            # 波动率检查
            if fund.volatility > config["max_volatility"]:
                continue
            
            # 最大回撤检查
            if fund.max_drawdown > config["max_drawdown"]:
                continue
            
            # 基金类型检查
            if fund.category not in config["categories"]:
                continue
            
            filtered.append(fund)
        
        return filtered
    
    def score_fund(self, fund: FundProfile, risk_profile: RiskProfile) -> float:
        """为基金打分"""
        score = 0.0
        
        # 收益评分 (30%)
        score += min(fund.return_1y * 100, 30)
        
        # 风险调整收益 (25%)
        if fund.volatility > 0:
            risk_adj_return = fund.return_1y / fund.volatility
            score += min(risk_adj_return * 10, 25)
        
        # 夏普比率 (20%)
        score += min(fund.sharpe_ratio * 5, 20)
        
        # 回撤控制 (15%)
        score += max(0, 15 - fund.max_drawdown * 100)
        
        # 规模评分 (5%)
        if 10 <= fund.fund_size <= 100:
            score += 5
        elif fund.fund_size > 100:
            score += 3
        else:
            score += 1
        
        # 基金经理 (5%)
        score += min(fund.manager_score, 5)
        
        return score
    
    def recommend(self, funds: List[FundProfile], 
                 risk_profile: RiskProfile,
                 top_n: int = 5) -> List[Tuple[FundProfile, float, str]]:
        """
        推荐基金
        
        Returns:
            List of (基金, 得分, 推荐理由)
        """
        # 筛选
        filtered = self.filter_funds(funds, risk_profile)
        
        if not filtered:
            logger.warning(f"[基金推荐] 没有符合 {risk_profile.value} 的基金")
            return []
        
        # 打分
        scored = [(fund, self.score_fund(fund, risk_profile)) 
                  for fund in filtered]
        
        # 排序
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # 生成推荐理由
        results = []
        for fund, score in scored[:top_n]:
            reason = self._generate_reason(fund, risk_profile)
            results.append((fund, score, reason))
        
        logger.info(f"[基金推荐] 为 {risk_profile.value} 推荐 {len(results)} 只基金")
        return results
    
    def _generate_reason(self, fund: FundProfile, risk_profile: RiskProfile) -> str:
        """生成推荐理由"""
        reasons = []
        
        # 收益理由
        if fund.return_1y > 0.20:
            reasons.append(f"近1年收益优秀({fund.return_1y*100:.1f}%)")
        elif fund.return_1y > 0.10:
            reasons.append(f"近1年收益良好({fund.return_1y*100:.1f}%)")
        
        # 风险理由
        if fund.max_drawdown < 0.10:
            reasons.append("回撤控制优秀")
        elif fund.max_drawdown < 0.15:
            reasons.append("回撤控制良好")
        
        # 夏普比率
        if fund.sharpe_ratio > 1.5:
            reasons.append("风险调整后收益优秀")
        elif fund.sharpe_ratio > 1.0:
            reasons.append("风险调整后收益良好")
        
        # 基金经理
        if fund.manager_score >= 4.5:
            reasons.append("基金经理优秀")
        elif fund.manager_score >= 4.0:
            reasons.append("基金经理良好")
        
        # 规模
        if 20 <= fund.fund_size <= 200:
            reasons.append("规模适中")
        
        return "；".join(reasons) if reasons else "符合风险偏好"
    
    def get_portfolio_suggestion(self, risk_profile: RiskProfile) -> Dict:
        """获取组合配置建议"""
        suggestions = {
            RiskProfile.CONSERVATIVE: {
                "债券型": 60,
                "货币型": 30,
                "混合型": 10,
                "description": "以债券基金为主，追求稳定收益"
            },
            RiskProfile.MODERATE: {
                "债券型": 40,
                "混合型": 40,
                "指数型": 20,
                "description": "股债平衡，稳健增值"
            },
            RiskProfile.BALANCED: {
                "混合型": 40,
                "股票型": 30,
                "债券型": 20,
                "指数型": 10,
                "description": "股债均衡，适度进取"
            },
            RiskProfile.AGGRESSIVE: {
                "股票型": 50,
                "混合型": 30,
                "QDII": 20,
                "description": "以股票基金为主，追求高收益"
            },
            RiskProfile.SPECULATIVE: {
                "股票型": 60,
                "行业主题": 25,
                "QDII": 15,
                "description": "集中配置高波动品种，追求最大收益"
            }
        }
        
        return suggestions.get(risk_profile, suggestions[RiskProfile.MODERATE])


# 模拟基金数据生成器
def generate_sample_funds() -> List[FundProfile]:
    """生成示例基金数据"""
    return [
        # 保守型基金
        FundProfile("000171", "易方达天天理财货币A", "货币型", 1, 0.025, 0.08, 0.01, 0.5, 0.001, 500, 4.2, 0.003),
        FundProfile("110007", "易方达稳健收益债券A", "债券型", 2, 0.045, 0.12, 0.03, 0.8, 0.02, 80, 4.5, 0.008),
        
        # 稳健型基金
        FundProfile("163402", "兴全趋势投资混合", "混合型", 3, 0.08, 0.15, 0.15, 1.0, 0.12, 120, 4.3, 0.015),
        FundProfile("110022", "易方达消费行业股票", "股票型", 3, 0.12, 0.25, 0.20, 1.2, 0.18, 200, 4.4, 0.015),
        
        # 平衡型基金
        FundProfile("000961", "天弘沪深300指数A", "指数型", 3, 0.10, 0.20, 0.18, 0.9, 0.15, 150, 3.8, 0.005),
        FundProfile("001938", "中欧时代先锋股票A", "股票型", 4, 0.15, 0.30, 0.25, 1.3, 0.22, 80, 4.6, 0.015),
        
        # 进取型基金
        FundProfile("005911", "广发双擎升级混合A", "混合型", 4, 0.18, 0.35, 0.28, 1.4, 0.25, 60, 4.2, 0.015),
        FundProfile("000828", "泰达宏利转型机遇股票", "股票型", 4, 0.22, 0.40, 0.30, 1.5, 0.28, 45, 4.1, 0.015),
        
        # 激进型基金
        FundProfile("001691", "南方香港成长灵活配置", "QDII", 5, 0.25, 0.45, 0.35, 1.3, 0.35, 30, 3.9, 0.018),
        FundProfile("005968", "创金合信新能源汽车股票", "行业主题", 5, 0.30, 0.50, 0.40, 1.6, 0.40, 25, 3.8, 0.015),
    ]


def demo_fund_recommender():
    """演示基金推荐系统"""
    print("="*70)
    print("🎯 基金个性化推荐系统演示")
    print("="*70)
    
    recommender = FundRecommender()
    
    # 生成示例基金
    funds = generate_sample_funds()
    print(f"\n📊 基金池: {len(funds)} 只基金")
    
    # 测试不同风险偏好
    test_profiles = [
        (RiskProfile.CONSERVATIVE, {"age": 55, "investment_horizon": 3, "risk_tolerance": "low"}),
        (RiskProfile.MODERATE, {"age": 40, "investment_horizon": 5, "risk_tolerance": "medium"}),
        (RiskProfile.BALANCED, {"age": 35, "investment_horizon": 7, "risk_tolerance": "medium"}),
        (RiskProfile.AGGRESSIVE, {"age": 30, "investment_horizon": 10, "risk_tolerance": "high"}),
        (RiskProfile.SPECULATIVE, {"age": 25, "investment_horizon": 15, "risk_tolerance": "high"}),
    ]
    
    for profile, params in test_profiles:
        print(f"\n{'='*70}")
        print(f"🎭 风险偏好: {profile.value}")
        print(f"{'='*70}")
        
        # 显示配置
        config = recommender.risk_configs[profile]
        print(f"\n📋 配置说明: {config['description']}")
        print(f"   最大风险等级: {config['max_risk_level']}")
        print(f"   最低1年收益: {config['min_return_1y']*100:.1f}%")
        print(f"   最大波动率: {config['max_volatility']*100:.1f}%")
        print(f"   最大回撤: {config['max_drawdown']*100:.1f}%")
        print(f"   推荐类型: {', '.join(config['categories'])}")
        
        # 获取组合建议
        portfolio = recommender.get_portfolio_suggestion(profile)
        print(f"\n💼 组合配置建议:")
        for fund_type, percentage in portfolio.items():
            if fund_type != "description":
                print(f"   {fund_type}: {percentage}%")
        print(f"   说明: {portfolio['description']}")
        
        # 推荐基金
        recommendations = recommender.recommend(funds, profile, top_n=3)
        
        if recommendations:
            print(f"\n⭐ 推荐基金 (Top {len(recommendations)}):")
            for i, (fund, score, reason) in enumerate(recommendations, 1):
                print(f"\n   {i}. {fund.name} ({fund.code})")
                print(f"      类型: {fund.category} | 风险等级: {fund.risk_level}")
                print(f"      近1年收益: {fund.return_1y*100:.1f}% | 波动率: {fund.volatility*100:.1f}%")
                print(f"      最大回撤: {fund.max_drawdown*100:.1f}% | 夏普比率: {fund.sharpe_ratio:.2f}")
                print(f"      综合得分: {score:.1f}")
                print(f"      推荐理由: {reason}")
        else:
            print("\n⚠️ 没有符合该风险偏好的基金")
    
    print("\n" + "="*70)
    print("✅ 演示完成!")
    print("="*70)


if __name__ == "__main__":
    demo_fund_recommender()
