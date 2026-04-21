#!/usr/bin/env python3
"""
基金理由增强系统
整合政策分析、情绪分析、业绩分析
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EnhancedReason:
    """增强推荐理由"""
    policy_analysis: str      # 政策分析
    sentiment_analysis: str   # 情绪分析
    performance_analysis: str # 业绩分析
    technical_analysis: str   # 技术分析
    risk_analysis: str        # 风险分析
    overall_reason: str       # 综合理由
    confidence_score: float   # 置信度
    key_factors: List[str]    # 关键因素
    warnings: List[str]       # 风险提示


class FundReasonEnhancer:
    """基金理由增强器"""
    
    def __init__(self):
        # 政策关键词库
        self.policy_keywords = {
            "positive": ["利好", "支持", "扶持", "鼓励", "促进", "推动", "加快", "深化", "改革"],
            "negative": ["收紧", "限制", "调控", "监管", "规范", "防范", "抑制", "降温"],
            "neutral": ["平稳", "稳定", "维持", "观察", "审慎"]
        }
        
        # 行业政策映射
        self.sector_policies = {
            "科技": ["科技创新", "数字经济", "人工智能", "半导体", "芯片"],
            "新能源": ["新能源", "碳中和", "光伏", "风电", "储能", "电动车"],
            "消费": ["消费", "内需", "扩大消费", "消费升级"],
            "医药": ["医疗", "医药", "健康", "养老", "创新药"],
            "金融": ["金融", "银行", "保险", "资本市场", "注册制"],
            "基建": ["基建", "投资", "稳增长", "新基建", "一带一路"]
        }
        
        logger.info("[理由增强] 初始化完成")
    
    def analyze_policy(self, fund_category: str, recent_news: List[str]) -> Dict:
        """
        政策分析
        
        Args:
            fund_category: 基金类别/行业
            recent_news: 近期新闻列表
            
        Returns:
            政策分析结果
        """
        # 识别相关行业
        related_sectors = []
        for sector, keywords in self.sector_policies.items():
            if any(kw in fund_category for kw in keywords):
                related_sectors.append(sector)
        
        if not related_sectors:
            related_sectors = ["通用"]
        
        # 分析新闻情绪
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        relevant_news = []
        
        for news in recent_news:
            # 检查是否与基金相关
            is_relevant = any(sector in news for sector in related_sectors)
            
            if is_relevant:
                relevant_news.append(news)
                
                # 判断情绪
                if any(kw in news for kw in self.policy_keywords["positive"]):
                    positive_count += 1
                elif any(kw in news for kw in self.policy_keywords["negative"]):
                    negative_count += 1
                else:
                    neutral_count += 1
        
        # 计算政策得分
        total = positive_count + negative_count + neutral_count
        if total == 0:
            policy_score = 0.5
            policy_trend = "neutral"
        else:
            policy_score = (positive_count - negative_count * 0.5) / total
            policy_score = max(0, min(1, policy_score + 0.5))  # 归一化到0-1
            
            if policy_score > 0.7:
                policy_trend = "positive"
            elif policy_score < 0.4:
                policy_trend = "negative"
            else:
                policy_trend = "neutral"
        
        # 生成分析文本
        if policy_trend == "positive":
            analysis = f"政策面利好{fund_category}。近期相关政策持续出台，{'、'.join(related_sectors)}领域获得政策支持，有利于基金持仓标的表现。"
        elif policy_trend == "negative":
            analysis = f"政策面偏紧，{fund_category}面临一定监管压力。建议关注政策变化，控制仓位。"
        else:
            analysis = f"政策面中性，{fund_category}政策环境稳定，无重大政策风险。"
        
        return {
            "score": policy_score,
            "trend": policy_trend,
            "analysis": analysis,
            "related_sectors": related_sectors,
            "relevant_news_count": len(relevant_news),
            "positive_news": positive_count,
            "negative_news": negative_count
        }
    
    def analyze_sentiment(self, fund_flow: float, market_sentiment: str,
                         social_media: Optional[List[str]] = None) -> Dict:
        """
        情绪分析
        
        Args:
            fund_flow: 资金流向（亿元）
            market_sentiment: 市场情绪
            social_media: 社交媒体情绪（可选）
            
        Returns:
            情绪分析结果
        """
        # 资金流向评分
        if fund_flow > 200:
            flow_score = 1.0
            flow_desc = "资金大幅流入"
        elif fund_flow > 100:
            flow_score = 0.8
            flow_desc = "资金明显流入"
        elif fund_flow > 0:
            flow_score = 0.6
            flow_desc = "资金小幅流入"
        elif fund_flow > -100:
            flow_score = 0.4
            flow_desc = "资金小幅流出"
        elif fund_flow > -200:
            flow_score = 0.2
            flow_desc = "资金明显流出"
        else:
            flow_score = 0.0
            flow_desc = "资金大幅流出"
        
        # 市场情绪评分
        sentiment_scores = {
            "extreme_greed": 1.0,
            "greed": 0.8,
            "neutral": 0.5,
            "fear": 0.3,
            "extreme_fear": 0.1
        }
        sentiment_score = sentiment_scores.get(market_sentiment, 0.5)
        
        # 综合情绪得分
        overall_score = flow_score * 0.6 + sentiment_score * 0.4
        
        # 生成分析文本
        if overall_score > 0.7:
            analysis = f"市场情绪乐观，{flow_desc}，投资者信心较强，有利于基金净值上涨。"
        elif overall_score > 0.4:
            analysis = f"市场情绪中性，{flow_desc}，建议观望或分批建仓。"
        else:
            analysis = f"市场情绪偏悲观，{flow_desc}，投资者需谨慎，等待情绪修复。"
        
        return {
            "score": overall_score,
            "flow_score": flow_score,
            "sentiment_score": sentiment_score,
            "analysis": analysis,
            "fund_flow": fund_flow,
            "market_sentiment": market_sentiment
        }
    
    def analyze_performance(self, return_1m: float, return_3m: float,
                           return_6m: float, return_1y: float,
                           benchmark_return: float, alpha: float,
                           sharpe_ratio: float, max_drawdown: float) -> Dict:
        """
        业绩分析
        
        Args:
            return_1m: 近1月收益
            return_3m: 近3月收益
            return_6m: 近6月收益
            return_1y: 近1年收益
            benchmark_return: 基准收益
            alpha: 超额收益
            sharpe_ratio: 夏普比率
            max_drawdown: 最大回撤
            
        Returns:
            业绩分析结果
        """
        # 短期业绩评分
        short_term = (return_1m + return_3m) / 2
        if short_term > 0.10:
            short_score = 1.0
        elif short_term > 0.05:
            short_score = 0.8
        elif short_term > 0:
            short_score = 0.6
        elif short_term > -0.05:
            short_score = 0.4
        else:
            short_score = 0.2
        
        # 长期业绩评分
        long_term = return_1y
        if long_term > 0.30:
            long_score = 1.0
        elif long_term > 0.20:
            long_score = 0.8
        elif long_term > 0.10:
            long_score = 0.6
        elif long_term > 0:
            long_score = 0.4
        else:
            long_score = 0.2
        
        # 风险调整收益评分
        if sharpe_ratio > 1.5:
            risk_adj_score = 1.0
        elif sharpe_ratio > 1.0:
            risk_adj_score = 0.8
        elif sharpe_ratio > 0.5:
            risk_adj_score = 0.6
        else:
            risk_adj_score = 0.4
        
        # 回撤控制评分
        if max_drawdown < 0.10:
            drawdown_score = 1.0
        elif max_drawdown < 0.15:
            drawdown_score = 0.8
        elif max_drawdown < 0.20:
            drawdown_score = 0.6
        elif max_drawdown < 0.30:
            drawdown_score = 0.4
        else:
            drawdown_score = 0.2
        
        # 综合业绩得分
        overall_score = (short_score * 0.2 + long_score * 0.3 + 
                        risk_adj_score * 0.3 + drawdown_score * 0.2)
        
        # 生成分析文本
        analysis_parts = []
        
        if return_1y > 0.20:
            analysis_parts.append(f"近1年收益优秀({return_1y*100:.1f}%)")
        elif return_1y > 0.10:
            analysis_parts.append(f"近1年收益良好({return_1y*100:.1f}%)")
        
        if alpha > 0.05:
            analysis_parts.append(f"超额收益显著({alpha*100:.1f}%)")
        elif alpha > 0:
            analysis_parts.append("跑赢基准")
        
        if sharpe_ratio > 1.0:
            analysis_parts.append(f"风险调整后收益优秀(夏普{sharpe_ratio:.2f})")
        
        if max_drawdown < 0.15:
            analysis_parts.append("回撤控制良好")
        
        if analysis_parts:
            analysis = "业绩表现" + "，".join(analysis_parts) + "。"
        else:
            analysis = "业绩表现一般，需关注后续表现。"
        
        return {
            "score": overall_score,
            "short_term_score": short_score,
            "long_term_score": long_score,
            "risk_adj_score": risk_adj_score,
            "drawdown_score": drawdown_score,
            "analysis": analysis,
            "return_1y": return_1y,
            "alpha": alpha,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown
        }
    
    def generate_enhanced_reason(self, fund_name: str, fund_category: str,
                                policy_news: List[str], fund_flow: float,
                                market_sentiment: str,
                                performance_data: Dict) -> EnhancedReason:
        """
        生成增强推荐理由
        
        Returns:
            EnhancedReason: 完整分析理由
        """
        # 多维度分析
        policy = self.analyze_policy(fund_category, policy_news)
        sentiment = self.analyze_sentiment(fund_flow, market_sentiment)
        performance = self.analyze_performance(**performance_data)
        
        # 综合评分
        weights = {"policy": 0.25, "sentiment": 0.25, "performance": 0.50}
        confidence_score = (
            policy["score"] * weights["policy"] +
            sentiment["score"] * weights["sentiment"] +
            performance["score"] * weights["performance"]
        )
        
        # 关键因素
        key_factors = []
        if policy["score"] > 0.7:
            key_factors.append("政策利好")
        if sentiment["score"] > 0.7:
            key_factors.append("情绪乐观")
        if performance["score"] > 0.7:
            key_factors.append("业绩优秀")
        if performance["sharpe_ratio"] > 1.0:
            key_factors.append("风险收益比优秀")
        
        # 风险提示
        warnings = []
        if policy["score"] < 0.4:
            warnings.append("政策面存在不确定性")
        if sentiment["score"] < 0.4:
            warnings.append("市场情绪偏悲观")
        if performance["max_drawdown"] > 0.25:
            warnings.append("历史回撤较大")
        if performance["return_1y"] < 0:
            warnings.append("近1年收益为负")
        
        # 综合理由
        overall_parts = [
            f"【政策】{policy['analysis']}",
            f"【情绪】{sentiment['analysis']}",
            f"【业绩】{performance['analysis']}"
        ]
        
        overall_reason = "\n\n".join(overall_parts)
        
        return EnhancedReason(
            policy_analysis=policy["analysis"],
            sentiment_analysis=sentiment["analysis"],
            performance_analysis=performance["analysis"],
            technical_analysis="建议结合技术分析确定具体买卖点",
            risk_analysis="；".join(warnings) if warnings else "风险可控",
            overall_reason=overall_reason,
            confidence_score=confidence_score,
            key_factors=key_factors,
            warnings=warnings
        )
    
    def format_reason_report(self, reason: EnhancedReason) -> str:
        """格式化理由报告"""
        report = f"""
# 📊 基金推荐理由增强分析

## 🎯 综合评分

**置信度**: {reason.confidence_score:.1%}
**关键因素**: {', '.join(reason.key_factors) if reason.key_factors else '综合分析'}

---

## 📰 政策分析

{reason.policy_analysis}

---

## 😊 情绪分析

{reason.sentiment_analysis}

---

## 📈 业绩分析

{reason.performance_analysis}

---

## 📊 技术分析

{reason.technical_analysis}

---

## ⚠️ 风险提示

{reason.risk_analysis}

---

## 💡 综合建议

{reason.overall_reason}

---

*分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
        """.strip()
        
        return report


def demo_reason_enhancer():
    """演示理由增强系统"""
    print("="*70)
    print("🎯 基金理由增强系统演示")
    print("="*70)
    
    enhancer = FundReasonEnhancer()
    
    # 模拟数据
    fund_name = "中欧时代先锋股票A"
    fund_category = "科技成长"
    
    policy_news = [
        "国家支持科技创新政策出台",
        "数字经济获得政策扶持",
        "半导体产业迎来利好",
        "监管规范科技行业发展"
    ]
    
    fund_flow = 150.5  # 亿元
    market_sentiment = "neutral"
    
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
    
    print(f"\n📊 分析基金: {fund_name}")
    print(f"类别: {fund_category}")
    
    # 生成增强理由
    reason = enhancer.generate_enhanced_reason(
        fund_name, fund_category,
        policy_news, fund_flow, market_sentiment,
        performance_data
    )
    
    print(f"\n{'='*70}")
    print("📋 分析结果")
    print(f"{'='*70}")
    
    print(f"\n✅ 置信度: {reason.confidence_score:.1%}")
    print(f"✅ 关键因素: {', '.join(reason.key_factors)}")
    
    print(f"\n📰 政策分析:")
    print(f"  {reason.policy_analysis}")
    
    print(f"\n😊 情绪分析:")
    print(f"  {reason.sentiment_analysis}")
    
    print(f"\n📈 业绩分析:")
    print(f"  {reason.performance_analysis}")
    
    print(f"\n⚠️ 风险提示:")
    if reason.warnings:
        for warning in reason.warnings:
            print(f"  • {warning}")
    else:
        print("  • 风险可控")
    
    print(f"\n{'='*70}")
    print("📄 完整报告")
    print(f"{'='*70}")
    
    report = enhancer.format_reason_report(reason)
    print(report)
    
    print("\n" + "="*70)
    print("✅ 演示完成!")
    print("="*70)


if __name__ == "__main__":
    demo_reason_enhancer()
