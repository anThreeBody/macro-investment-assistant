#!/usr/bin/env python3
"""
基金买卖点建议系统
提供具体的买入/卖出时机建议
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalStrength(Enum):
    """信号强度"""
    STRONG = "强烈"      # 强烈推荐
    MODERATE = "中等"    # 可以考虑
    WEAK = "较弱"        # 仅供参考


@dataclass
class FundSignal:
    """基金交易信号"""
    fund_code: str
    fund_name: str
    action: str              # BUY/SELL/HOLD
    strength: str            # 信号强度
    current_nav: float       # 当前净值
    target_price: float      # 目标价
    stop_loss: float         # 止损价
    take_profit: float       # 止盈价
    confidence: float        # 置信度 0-1
    reason: str              # 理由
    technical_factors: Dict  # 技术因子
    fundamental_factors: Dict # 基本面因子
    sentiment_factors: Dict  # 情绪因子
    timestamp: str


class FundTimingAdvisor:
    """基金时机顾问"""
    
    def __init__(self):
        # 技术指标权重
        self.weights = {
            "technical": 0.35,
            "fundamental": 0.35,
            "sentiment": 0.30
        }
        
        # 阈值配置
        self.thresholds = {
            "buy_rsi": 35,
            "sell_rsi": 65,
            "buy_ma_deviation": -0.05,   # 低于MA5 5%
            "sell_ma_deviation": 0.08,    # 高于MA5 8%
            "min_confidence": 0.6
        }
        
        logger.info("[基金时机] 初始化完成")
    
    def analyze_technical(self, nav_history: List[float]) -> Dict:
        """
        技术分析
        
        Args:
            nav_history: 历史净值列表（最近30天）
            
        Returns:
            技术分析结果
        """
        if len(nav_history) < 20:
            return {"score": 0.5, "signals": [], "rsi": 50}
        
        current_nav = nav_history[-1]
        
        # 计算MA5, MA10, MA20
        ma5 = sum(nav_history[-5:]) / 5
        ma10 = sum(nav_history[-10:]) / 10
        ma20 = sum(nav_history[-20:]) / 20
        
        # 计算偏离度
        deviation_5 = (current_nav - ma5) / ma5
        deviation_10 = (current_nav - ma10) / ma10
        deviation_20 = (current_nav - ma20) / ma20
        
        # 计算RSI
        rsi = self._calculate_rsi(nav_history)
        
        # 判断趋势
        trend = "UP" if ma5 > ma10 > ma20 else "DOWN" if ma5 < ma10 < ma20 else "SIDE"
        
        # 生成信号
        signals = []
        score = 0.5
        
        # RSI信号
        if rsi < self.thresholds["buy_rsi"]:
            signals.append(f"RSI超卖({rsi:.1f})")
            score += 0.2
        elif rsi > self.thresholds["sell_rsi"]:
            signals.append(f"RSI超买({rsi:.1f})")
            score -= 0.2
        
        # MA偏离信号
        if deviation_5 < self.thresholds["buy_ma_deviation"]:
            signals.append(f"低于MA5 {abs(deviation_5)*100:.1f}%")
            score += 0.15
        elif deviation_5 > self.thresholds["sell_ma_deviation"]:
            signals.append(f"高于MA5 {deviation_5*100:.1f}%")
            score -= 0.15
        
        # 趋势信号
        if trend == "UP":
            signals.append("趋势向上")
            score += 0.1
        elif trend == "DOWN":
            signals.append("趋势向下")
            score -= 0.1
        
        return {
            "score": min(max(score, 0), 1),
            "signals": signals,
            "rsi": rsi,
            "ma5": ma5,
            "ma10": ma10,
            "ma20": ma20,
            "deviation_5": deviation_5,
            "deviation_10": deviation_10,
            "deviation_20": deviation_20,
            "trend": trend
        }
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        recent_changes = changes[-period:]
        
        gains = [max(c, 0) for c in recent_changes]
        losses = [abs(min(c, 0)) for c in recent_changes]
        
        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def analyze_fundamental(self, fund_info: Dict) -> Dict:
        """
        基本面分析
        
        Args:
            fund_info: 基金信息
            
        Returns:
            基本面分析结果
        """
        score = 0.5
        signals = []
        
        # 基金经理评分
        manager_score = fund_info.get("manager_score", 3.0)
        if manager_score >= 4.5:
            signals.append("基金经理优秀")
            score += 0.15
        elif manager_score >= 4.0:
            signals.append("基金经理良好")
            score += 0.1
        elif manager_score < 3.0:
            signals.append("基金经理一般")
            score -= 0.1
        
        # 基金规模
        fund_size = fund_info.get("fund_size", 50)
        if 20 <= fund_size <= 200:
            signals.append("规模适中")
            score += 0.1
        elif fund_size > 500:
            signals.append("规模过大")
            score -= 0.05
        elif fund_size < 5:
            signals.append("规模过小")
            score -= 0.1
        
        # 费率
        expense_ratio = fund_info.get("expense_ratio", 0.015)
        if expense_ratio < 0.008:
            signals.append("费率较低")
            score += 0.05
        elif expense_ratio > 0.02:
            signals.append("费率较高")
            score -= 0.05
        
        # 历史业绩
        return_1y = fund_info.get("return_1y", 0)
        if return_1y > 0.20:
            signals.append("近1年业绩优秀")
            score += 0.15
        elif return_1y > 0.10:
            signals.append("近1年业绩良好")
            score += 0.1
        elif return_1y < 0:
            signals.append("近1年业绩不佳")
            score -= 0.1
        
        return {
            "score": min(max(score, 0), 1),
            "signals": signals,
            "manager_score": manager_score,
            "fund_size": fund_size,
            "expense_ratio": expense_ratio,
            "return_1y": return_1y
        }
    
    def analyze_sentiment(self, market_data: Dict) -> Dict:
        """
        情绪分析
        
        Args:
            market_data: 市场数据
            
        Returns:
            情绪分析结果
        """
        score = 0.5
        signals = []
        
        # 市场情绪
        market_sentiment = market_data.get("market_sentiment", "neutral")
        if market_sentiment == "bullish":
            signals.append("市场情绪乐观")
            score += 0.15
        elif market_sentiment == "bearish":
            signals.append("市场情绪悲观")
            score -= 0.15
        
        # 资金流向
        fund_flow = market_data.get("fund_flow", 0)
        if fund_flow > 100:  # 亿元
            signals.append("资金大幅流入")
            score += 0.1
        elif fund_flow < -100:
            signals.append("资金大幅流出")
            score -= 0.1
        
        # 政策环境
        policy = market_data.get("policy", "neutral")
        if policy == "supportive":
            signals.append("政策利好")
            score += 0.1
        elif policy == "restrictive":
            signals.append("政策收紧")
            score -= 0.1
        
        return {
            "score": min(max(score, 0), 1),
            "signals": signals,
            "market_sentiment": market_sentiment,
            "fund_flow": fund_flow,
            "policy": policy
        }
    
    def generate_signal(self, fund_code: str, fund_name: str,
                       current_nav: float, nav_history: List[float],
                       fund_info: Dict, market_data: Dict) -> FundSignal:
        """
        生成交易信号
        
        Returns:
            FundSignal: 交易信号
        """
        # 多维度分析
        technical = self.analyze_technical(nav_history)
        fundamental = self.analyze_fundamental(fund_info)
        sentiment = self.analyze_sentiment(market_data)
        
        # 综合评分
        total_score = (
            technical["score"] * self.weights["technical"] +
            fundamental["score"] * self.weights["fundamental"] +
            sentiment["score"] * self.weights["sentiment"]
        )
        
        # 确定操作
        if total_score >= 0.7:
            action = "BUY"
            strength = SignalStrength.STRONG
        elif total_score >= 0.6:
            action = "BUY"
            strength = SignalStrength.MODERATE
        elif total_score <= 0.3:
            action = "SELL"
            strength = SignalStrength.STRONG
        elif total_score <= 0.4:
            action = "SELL"
            strength = SignalStrength.MODERATE
        else:
            action = "HOLD"
            strength = SignalStrength.WEAK
        
        # 计算目标价、止损、止盈
        if action == "BUY":
            target_price = current_nav * 1.05
            stop_loss = current_nav * 0.97
            take_profit = current_nav * 1.10
        elif action == "SELL":
            target_price = current_nav * 0.95
            stop_loss = current_nav * 1.03
            take_profit = current_nav * 0.90
        else:
            target_price = current_nav
            stop_loss = current_nav * 0.95
            take_profit = current_nav * 1.05
        
        # 生成理由
        all_signals = []
        all_signals.extend([f"[技术]{s}" for s in technical["signals"]])
        all_signals.extend([f"[基本面]{s}" for s in fundamental["signals"]])
        all_signals.extend([f"[情绪]{s}" for s in sentiment["signals"]])
        
        reason = "；".join(all_signals[:5]) if all_signals else "综合分析结果"
        
        return FundSignal(
            fund_code=fund_code,
            fund_name=fund_name,
            action=action,
            strength=strength.value,
            current_nav=current_nav,
            target_price=target_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=total_score,
            reason=reason,
            technical_factors=technical,
            fundamental_factors=fundamental,
            sentiment_factors=sentiment,
            timestamp=datetime.now().isoformat()
        )
    
    def get_buying_strategy(self, signal: FundSignal) -> str:
        """获取买入策略"""
        if signal.action != "BUY":
            return "当前不建议买入"
        
        strategy = f"""
🟢 买入策略 - {signal.fund_name} ({signal.fund_code})

【当前状态】
• 当前净值: {signal.current_nav:.4f}
• 信号强度: {signal.strength}
• 综合置信度: {signal.confidence:.1%}

【买入方案】
• 建议买入价: {signal.current_nav:.4f} - {signal.target_price:.4f}
• 目标涨幅: +{(signal.target_price/signal.current_nav-1)*100:.1f}%
• 止损设置: {signal.stop_loss:.4f} (-{(1-signal.stop_loss/signal.current_nav)*100:.1f}%)
• 止盈目标: {signal.take_profit:.4f} (+{(signal.take_profit/signal.current_nav-1)*100:.1f}%)

【仓位建议】
• {signal.strength}信号: 建议仓位 20-30%
• 分批买入: 首次10%，回调5%加仓10%
• 最大仓位: 不超过总资产的30%

【买入时机】
• 立即买入: 净值在 {signal.current_nav*0.995:.4f} 以下
• 分批买入: 净值在 {signal.current_nav:.4f} - {signal.target_price:.4f}
• 暂停买入: 净值高于 {signal.target_price:.4f}

【持有周期】
• 短期: 1-3个月，目标收益 5-10%
• 中期: 3-6个月，目标收益 10-20%
• 长期: 6-12个月，目标收益 20%+

【风险提示】
• 严格止损: 跌破 {signal.stop_loss:.4f} 立即止损
• 分批止盈: 达到 {signal.take_profit*0.9:.4f} 可止盈50%
• 定期复盘: 每周检查信号变化

【买入理由】
{signal.reason}
        """.strip()
        
        return strategy
    
    def get_selling_strategy(self, signal: FundSignal) -> str:
        """获取卖出策略"""
        if signal.action != "SELL":
            return "当前不建议卖出"
        
        strategy = f"""
🔴 卖出策略 - {signal.fund_name} ({signal.fund_code})

【当前状态】
• 当前净值: {signal.current_nav:.4f}
• 信号强度: {signal.strength}
• 综合置信度: {signal.confidence:.1%}

【卖出方案】
• 建议卖出价: {signal.current_nav:.4f} - {signal.target_price:.4f}
• 目标跌幅: {(signal.target_price/signal.current_nav-1)*100:.1f}%
• 止损设置: {signal.stop_loss:.4f} (+{(signal.stop_loss/signal.current_nav-1)*100:.1f}%)
• 止盈目标: {signal.take_profit:.4f} ({(signal.take_profit/signal.current_nav-1)*100:.1f}%)

【仓位建议】
• {signal.strength}信号: 建议卖出 50-100%
• 分批卖出: 首次卖出50%，反弹卖出剩余50%
• 清仓线: 净值低于 {signal.take_profit:.4f} 全部清仓

【卖出时机】
• 立即卖出: 净值在 {signal.current_nav:.4f} 以上
• 分批卖出: 净值在 {signal.target_price:.4f} - {signal.current_nav:.4f}
• 暂停卖出: 净值低于 {signal.target_price:.4f}

【卖出理由】
{signal.reason}

【后续操作】
• 卖出后观望 1-2周
• 等待回调至支撑位再考虑买入
• 关注基本面变化
        """.strip()
        
        return strategy


def demo_fund_timing():
    """演示基金时机建议"""
    print("="*70)
    print("🎯 基金买卖点建议系统演示")
    print("="*70)
    
    advisor = FundTimingAdvisor()
    
    # 模拟基金数据
    fund_code = "005911"
    fund_name = "广发双擎升级混合A"
    current_nav = 2.4567
    
    # 模拟30天净值历史（下跌趋势，适合买入）
    nav_history = [
        2.60, 2.58, 2.59, 2.57, 2.55,
        2.56, 2.54, 2.52, 2.53, 2.51,
        2.50, 2.48, 2.49, 2.47, 2.46,
        2.45, 2.44, 2.45, 2.43, 2.42,
        2.44, 2.43, 2.45, 2.44, 2.46,
        2.45, 2.46, 2.45, 2.47, 2.4567
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
    
    print(f"\n📊 分析基金: {fund_name} ({fund_code})")
    print(f"当前净值: {current_nav}")
    print(f"历史数据: {len(nav_history)} 天")
    
    # 生成信号
    signal = advisor.generate_signal(
        fund_code, fund_name, current_nav,
        nav_history, fund_info, market_data
    )
    
    print(f"\n{'='*70}")
    print(f"📈 交易信号")
    print(f"{'='*70}")
    
    print(f"\n操作建议: {signal.action}")
    print(f"信号强度: {signal.strength}")
    print(f"置信度: {signal.confidence:.1%}")
    print(f"当前净值: {signal.current_nav:.4f}")
    print(f"目标价格: {signal.target_price:.4f}")
    print(f"止损价格: {signal.stop_loss:.4f}")
    print(f"止盈价格: {signal.take_profit:.4f}")
    
    print(f"\n技术因子得分: {signal.technical_factors['score']:.2f}")
    print(f"  RSI: {signal.technical_factors['rsi']:.1f}")
    print(f"  MA5: {signal.technical_factors['ma5']:.4f}")
    print(f"  趋势: {signal.technical_factors['trend']}")
    
    print(f"\n基本面因子得分: {signal.fundamental_factors['score']:.2f}")
    print(f"  基金经理: {signal.fundamental_factors['manager_score']}")
    print(f"  规模: {signal.fundamental_factors['fund_size']}亿")
    
    print(f"\n情绪因子得分: {signal.sentiment_factors['score']:.2f}")
    print(f"  市场情绪: {signal.sentiment_factors['market_sentiment']}")
    
    print(f"\n综合理由: {signal.reason}")
    
    # 显示策略
    if signal.action == "BUY":
        print(f"\n{'='*70}")
        print(advisor.get_buying_strategy(signal))
    elif signal.action == "SELL":
        print(f"\n{'='*70}")
        print(advisor.get_selling_strategy(signal))
    
    print("\n" + "="*70)
    print("✅ 演示完成!")
    print("="*70)


if __name__ == "__main__":
    demo_fund_timing()
