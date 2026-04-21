#!/usr/bin/env python3
"""
个股推荐升级系统
从"观察用"到具体买卖建议
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockSignal(Enum):
    """股票信号"""
    STRONG_BUY = "强烈买入"
    BUY = "买入"
    HOLD = "持有"
    SELL = "卖出"
    STRONG_SELL = "强烈卖出"


@dataclass
class StockRecommendation:
    """个股推荐"""
    code: str
    name: str
    industry: str
    current_price: float
    signal: str
    confidence: float
    target_price: float
    stop_loss: float
    take_profit: float
    position_size: str      # 建议仓位
    holding_period: str     # 建议持有周期
    technical_score: float
    fundamental_score: float
    capital_score: float
    overall_reason: str
    risk_level: str
    timestamp: str


class StockRecommender:
    """个股推荐器"""
    
    def __init__(self):
        # 权重配置
        self.weights = {
            "technical": 0.40,
            "fundamental": 0.35,
            "capital": 0.25
        }
        
        # 阈值配置
        self.thresholds = {
            "strong_buy": 0.80,
            "buy": 0.65,
            "sell": 0.35,
            "strong_sell": 0.20
        }
        
        logger.info("[个股推荐] 初始化完成")
    
    def analyze_technical(self, price_history: List[float], 
                         volume_history: List[float]) -> Dict:
        """
        技术分析
        
        Args:
            price_history: 价格历史（最近60天）
            volume_history: 成交量历史
            
        Returns:
            技术分析结果
        """
        if len(price_history) < 20:
            return {"score": 0.5, "signals": []}
        
        current_price = price_history[-1]
        
        # 计算均线
        ma5 = sum(price_history[-5:]) / 5
        ma10 = sum(price_history[-10:]) / 10
        ma20 = sum(price_history[-20:]) / 20
        ma60 = sum(price_history[-60:]) / 60 if len(price_history) >= 60 else ma20
        
        # 计算RSI
        rsi = self._calculate_rsi(price_history)
        
        # 计算MACD
        macd, signal, histogram = self._calculate_macd(price_history)
        
        # 计算布林带
        bb_upper, bb_lower, bb_middle = self._calculate_bollinger(price_history)
        
        # 成交量分析
        avg_volume = sum(volume_history[-20:]) / 20 if volume_history else 0
        recent_volume = volume_history[-1] if volume_history else 0
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        # 评分
        score = 0.5
        signals = []
        
        # 均线信号
        if current_price > ma5 > ma10 > ma20:
            signals.append("均线多头排列")
            score += 0.15
        elif current_price < ma5 < ma10 < ma20:
            signals.append("均线空头排列")
            score -= 0.15
        
        # RSI信号
        if rsi < 30:
            signals.append(f"RSI超卖({rsi:.1f})")
            score += 0.15
        elif rsi > 70:
            signals.append(f"RSI超买({rsi:.1f})")
            score -= 0.15
        elif 40 <= rsi <= 60:
            signals.append("RSI中性")
        
        # MACD信号
        if histogram > 0 and macd > signal:
            signals.append("MACD金叉")
            score += 0.1
        elif histogram < 0 and macd < signal:
            signals.append("MACD死叉")
            score -= 0.1
        
        # 布林带信号
        if current_price < bb_lower:
            signals.append("跌破布林带下轨")
            score += 0.1
        elif current_price > bb_upper:
            signals.append("突破布林带上轨")
            score -= 0.1
        
        # 成交量信号
        if volume_ratio > 2:
            signals.append("成交量放大")
            score += 0.05
        elif volume_ratio < 0.5:
            signals.append("成交量萎缩")
            score -= 0.05
        
        return {
            "score": min(max(score, 0), 1),
            "signals": signals,
            "rsi": rsi,
            "macd": macd,
            "signal": signal,
            "histogram": histogram,
            "ma5": ma5,
            "ma10": ma10,
            "ma20": ma20,
            "ma60": ma60,
            "bb_upper": bb_upper,
            "bb_lower": bb_lower,
            "volume_ratio": volume_ratio
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
    
    def _calculate_macd(self, prices: List[float]) -> Tuple[float, float, float]:
        """计算MACD"""
        if len(prices) < 26:
            return 0, 0, 0
        
        # 计算EMA12和EMA26
        ema12 = self._calculate_ema(prices, 12)
        ema26 = self._calculate_ema(prices, 26)
        
        # DIF线
        dif = ema12 - ema26
        
        # DEA线
        dif_list = [self._calculate_ema(prices[:i+1], 12) - self._calculate_ema(prices[:i+1], 26) 
                    for i in range(25, len(prices))]
        dea = self._calculate_ema(dif_list, 9) if len(dif_list) >= 9 else dif
        
        # MACD柱
        macd = (dif - dea) * 2
        
        return dif, dea, macd
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """计算EMA"""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def _calculate_bollinger(self, prices: List[float], period: int = 20, std_dev: int = 2) -> Tuple[float, float, float]:
        """计算布林带"""
        if len(prices) < period:
            return prices[-1] * 1.1, prices[-1] * 0.9, prices[-1] if prices else (0, 0, 0)
        
        recent_prices = prices[-period:]
        middle = sum(recent_prices) / period
        variance = sum((p - middle) ** 2 for p in recent_prices) / period
        std = variance ** 0.5
        
        upper = middle + std_dev * std
        lower = middle - std_dev * std
        
        return upper, lower, middle
    
    def analyze_fundamental(self, pe: float, pb: float, 
                           roe: float, revenue_growth: float,
                           profit_growth: float, debt_ratio: float) -> Dict:
        """
        基本面分析
        
        Args:
            pe: 市盈率
            pb: 市净率
            roe: 净资产收益率
            revenue_growth: 营收增长率
            profit_growth: 利润增长率
            debt_ratio: 负债率
            
        Returns:
            基本面分析结果
        """
        score = 0.5
        signals = []
        
        # PE评分
        if pe < 15:
            signals.append(f"PE较低({pe:.1f})")
            score += 0.15
        elif pe > 50:
            signals.append(f"PE较高({pe:.1f})")
            score -= 0.15
        else:
            signals.append(f"PE合理({pe:.1f})")
            score += 0.05
        
        # PB评分
        if pb < 2:
            signals.append(f"PB较低({pb:.1f})")
            score += 0.1
        elif pb > 5:
            signals.append(f"PB较高({pb:.1f})")
            score -= 0.1
        
        # ROE评分
        if roe > 20:
            signals.append(f"ROE优秀({roe:.1f}%)")
            score += 0.15
        elif roe > 15:
            signals.append(f"ROE良好({roe:.1f}%)")
            score += 0.1
        elif roe < 10:
            signals.append(f"ROE一般({roe:.1f}%)")
            score -= 0.1
        
        # 成长性评分
        if revenue_growth > 30:
            signals.append(f"营收高增长({revenue_growth:.1f}%)")
            score += 0.1
        elif revenue_growth < 0:
            signals.append(f"营收下滑({revenue_growth:.1f}%)")
            score -= 0.1
        
        if profit_growth > 30:
            signals.append(f"利润高增长({profit_growth:.1f}%)")
            score += 0.1
        elif profit_growth < 0:
            signals.append(f"利润下滑({profit_growth:.1f}%)")
            score -= 0.1
        
        # 负债率评分
        if debt_ratio < 40:
            signals.append("负债率低")
            score += 0.05
        elif debt_ratio > 70:
            signals.append("负债率高")
            score -= 0.05
        
        return {
            "score": min(max(score, 0), 1),
            "signals": signals,
            "pe": pe,
            "pb": pb,
            "roe": roe,
            "revenue_growth": revenue_growth,
            "profit_growth": profit_growth,
            "debt_ratio": debt_ratio
        }
    
    def analyze_capital(self, main_force: float, north_bound: float,
                       turnover: float, margin: float) -> Dict:
        """
        资金面分析
        
        Args:
            main_force: 主力资金流向（亿元）
            north_bound: 北向资金流向（亿元）
            turnover: 换手率
            margin: 融资融券余额变化
            
        Returns:
            资金面分析结果
        """
        score = 0.5
        signals = []
        
        # 主力资金
        if main_force > 1:
            signals.append(f"主力大幅流入({main_force:.1f}亿)")
            score += 0.2
        elif main_force > 0.5:
            signals.append(f"主力流入({main_force:.1f}亿)")
            score += 0.1
        elif main_force < -1:
            signals.append(f"主力大幅流出({main_force:.1f}亿)")
            score -= 0.2
        elif main_force < -0.5:
            signals.append(f"主力流出({main_force:.1f}亿)")
            score -= 0.1
        
        # 北向资金
        if north_bound > 0.5:
            signals.append(f"北向流入({north_bound:.1f}亿)")
            score += 0.1
        elif north_bound < -0.5:
            signals.append(f"北向流出({north_bound:.1f}亿)")
            score -= 0.1
        
        # 换手率
        if 3 <= turnover <= 10:
            signals.append(f"换手活跃({turnover:.1f}%)")
            score += 0.05
        elif turnover > 15:
            signals.append(f"换手过高({turnover:.1f}%)")
            score -= 0.05
        
        # 融资融券
        if margin > 10:
            signals.append("融资增加")
            score += 0.05
        elif margin < -10:
            signals.append("融资减少")
            score -= 0.05
        
        return {
            "score": min(max(score, 0), 1),
            "signals": signals,
            "main_force": main_force,
            "north_bound": north_bound,
            "turnover": turnover,
            "margin": margin
        }
    
    def generate_recommendation(self, code: str, name: str, industry: str,
                               current_price: float, price_history: List[float],
                               volume_history: List[float],
                               fundamental_data: Dict,
                               capital_data: Dict) -> StockRecommendation:
        """
        生成个股推荐
        
        Returns:
            StockRecommendation: 个股推荐
        """
        # 多维度分析
        technical = self.analyze_technical(price_history, volume_history)
        fundamental = self.analyze_fundamental(**fundamental_data)
        capital = self.analyze_capital(**capital_data)
        
        # 综合评分
        total_score = (
            technical["score"] * self.weights["technical"] +
            fundamental["score"] * self.weights["fundamental"] +
            capital["score"] * self.weights["capital"]
        )
        
        # 确定信号
        if total_score >= self.thresholds["strong_buy"]:
            signal = StockSignal.STRONG_BUY
        elif total_score >= self.thresholds["buy"]:
            signal = StockSignal.BUY
        elif total_score <= self.thresholds["strong_sell"]:
            signal = StockSignal.STRONG_SELL
        elif total_score <= self.thresholds["sell"]:
            signal = StockSignal.SELL
        else:
            signal = StockSignal.HOLD
        
        # 计算目标价、止损、止盈
        if signal in [StockSignal.STRONG_BUY, StockSignal.BUY]:
            target_price = current_price * 1.08
            stop_loss = current_price * 0.95
            take_profit = current_price * 1.15
            position_size = "20-30%" if signal == StockSignal.STRONG_BUY else "10-20%"
            holding_period = "1-3个月"
        elif signal in [StockSignal.STRONG_SELL, StockSignal.SELL]:
            target_price = current_price * 0.92
            stop_loss = current_price * 1.05
            take_profit = current_price * 0.85
            position_size = "清仓" if signal == StockSignal.STRONG_SELL else "减仓50%"
            holding_period = "立即执行"
        else:
            target_price = current_price
            stop_loss = current_price * 0.93
            take_profit = current_price * 1.08
            position_size = "持有观望"
            holding_period = "等待信号"
        
        # 风险等级
        if total_score >= 0.8 or total_score <= 0.2:
            risk_level = "高"
        elif total_score >= 0.65 or total_score <= 0.35:
            risk_level = "中"
        else:
            risk_level = "低"
        
        # 生成综合理由
        all_signals = []
        all_signals.extend([f"[技术]{s}" for s in technical["signals"]])
        all_signals.extend([f"[基本面]{s}" for s in fundamental["signals"]])
        all_signals.extend([f"[资金面]{s}" for s in capital["signals"]])
        
        overall_reason = "；".join(all_signals[:6]) if all_signals else "综合分析结果"
        
        return StockRecommendation(
            code=code,
            name=name,
            industry=industry,
            current_price=current_price,
            signal=signal.value,
            confidence=total_score,
            target_price=target_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            holding_period=holding_period,
            technical_score=technical["score"],
            fundamental_score=fundamental["score"],
            capital_score=capital["score"],
            overall_reason=overall_reason,
            risk_level=risk_level,
            timestamp=datetime.now().isoformat()
        )
    
    def get_trading_strategy(self, recommendation: StockRecommendation) -> str:
        """获取交易策略"""
        
        if recommendation.signal in ["强烈买入", "买入"]:
            strategy = f"""
🟢 {recommendation.signal}策略 - {recommendation.name} ({recommendation.code})

【当前状态】
• 当前价格: ¥{recommendation.current_price:.2f}
• 所属行业: {recommendation.industry}
• 信号强度: {recommendation.signal}
• 综合置信度: {recommendation.confidence:.1%}
• 风险等级: {recommendation.risk_level}

【买入方案】
• 建议买入价: ¥{recommendation.current_price:.2f} - ¥{recommendation.target_price:.2f}
• 目标涨幅: +{(recommendation.target_price/recommendation.current_price-1)*100:.1f}%
• 止损设置: ¥{recommendation.stop_loss:.2f} (-{(1-recommendation.stop_loss/recommendation.current_price)*100:.1f}%)
• 止盈目标: ¥{recommendation.take_profit:.2f} (+{(recommendation.take_profit/recommendation.current_price-1)*100:.1f}%)

【仓位建议】
• {recommendation.signal}信号: 建议仓位 {recommendation.position_size}
• 分批买入: 首次10%，回调3%加仓10%
• 最大仓位: 单只股票不超过总资产的30%

【买入时机】
• 立即买入: 价格在 ¥{recommendation.current_price*0.995:.2f} 以下
• 分批买入: 价格在 ¥{recommendation.current_price:.2f} - ¥{recommendation.target_price:.2f}
• 暂停买入: 价格高于 ¥{recommendation.target_price:.2f}

【持有周期】
• 建议周期: {recommendation.holding_period}
• 短期目标: 收益 5-10%
• 中期目标: 收益 10-20%

【风险控制】
• 严格止损: 跌破 ¥{recommendation.stop_loss:.2f} 立即止损
• 分批止盈: 达到 ¥{recommendation.take_profit*0.9:.2f} 可止盈50%
• 定期复盘: 每周检查技术信号变化

【评分详情】
• 技术面: {recommendation.technical_score:.1%}
• 基本面: {recommendation.fundamental_score:.1%}
• 资金面: {recommendation.capital_score:.1%}

【买入理由】
{recommendation.overall_reason}
            """.strip()
        
        elif recommendation.signal in ["强烈卖出", "卖出"]:
            strategy = f"""
🔴 {recommendation.signal}策略 - {recommendation.name} ({recommendation.code})

【当前状态】
• 当前价格: ¥{recommendation.current_price:.2f}
• 所属行业: {recommendation.industry}
• 信号强度: {recommendation.signal}
• 综合置信度: {recommendation.confidence:.1%}

【卖出方案】
• 建议卖出价: ¥{recommendation.current_price:.2f} - ¥{recommendation.target_price:.2f}
• 目标跌幅: {(recommendation.target_price/recommendation.current_price-1)*100:.1f}%
• 止损设置: ¥{recommendation.stop_loss:.2f} (+{(recommendation.stop_loss/recommendation.current_price-1)*100:.1f}%)
• 止盈目标: ¥{recommendation.take_profit:.2f} ({(recommendation.take_profit/recommendation.current_price-1)*100:.1f}%)

【仓位建议】
• {recommendation.signal}信号: {recommendation.position_size}
• 分批卖出: 首次卖出50%，反弹卖出剩余

【卖出理由】
{recommendation.overall_reason}

【后续操作】
• 卖出后观望 1-2周
• 等待回调至支撑位再考虑买入
• 关注基本面变化
            """.strip()
        
        else:
            strategy = f"""
⚪ 持有观望策略 - {recommendation.name} ({recommendation.code})

【当前状态】
• 当前价格: ¥{recommendation.current_price:.2f}
• 信号: {recommendation.signal}
• 置信度: {recommendation.confidence:.1%}

【建议】
• 继续持有，等待更明确信号
• 设置止损: ¥{recommendation.stop_loss:.2f}
• 设置止盈: ¥{recommendation.take_profit:.2f}

【关注要点】
{recommendation.overall_reason}
            """.strip()
        
        return strategy


def demo_stock_recommender():
    """演示个股推荐系统"""
    print("="*70)
    print("🎯 个股推荐升级系统演示")
    print("="*70)
    
    recommender = StockRecommender()
    
    # 模拟股票数据
    code = "000001"
    name = "平安银行"
    industry = "银行"
    current_price = 12.50
    
    # 模拟60天价格历史（上涨趋势）
    price_history = [10.0 + i * 0.05 + (i % 5) * 0.1 for i in range(60)]
    price_history[-1] = current_price
    
    # 模拟成交量
    volume_history = [1000000 + i * 1000 for i in range(60)]
    
    # 基本面数据
    fundamental_data = {
        "pe": 8.5,
        "pb": 0.9,
        "roe": 12.5,
        "revenue_growth": 8.0,
        "profit_growth": 10.0,
        "debt_ratio": 92.0
    }
    
    # 资金面数据
    capital_data = {
        "main_force": 1.5,
        "north_bound": 0.8,
        "turnover": 5.0,
        "margin": 15.0
    }
    
    print(f"\n📊 分析股票: {name} ({code})")
    print(f"行业: {industry}")
    print(f"当前价格: ¥{current_price}")
    
    # 生成推荐
    recommendation = recommender.generate_recommendation(
        code, name, industry, current_price,
        price_history, volume_history,
        fundamental_data, capital_data
    )
    
    print(f"\n{'='*70}")
    print("  📈 推荐结果")
    print(f"{'='*70}")
    
    print(f"\n信号: {recommendation.signal}")
    print(f"置信度: {recommendation.confidence:.1%}")
    print(f"目标价格: ¥{recommendation.target_price:.2f}")
    print(f"止损价格: ¥{recommendation.stop_loss:.2f}")
    print(f"止盈价格: ¥{recommendation.take_profit:.2f}")
    print(f"建议仓位: {recommendation.position_size}")
    print(f"持有周期: {recommendation.holding_period}")
    print(f"风险等级: {recommendation.risk_level}")
    
    print(f"\n评分详情:")
    print(f"  技术面: {recommendation.technical_score:.1%}")
    print(f"  基本面: {recommendation.fundamental_score:.1%}")
    print(f"  资金面: {recommendation.capital_score:.1%}")
    
    print(f"\n综合理由:")
    print(f"  {recommendation.overall_reason}")
    
    # 显示交易策略
    print(f"\n{'='*70}")
    print("💡 交易策略")
    print(f"{'='*70}")
    
    strategy = recommender.get_trading_strategy(recommendation)
    print(strategy)
    
    print("\n" + "="*70)
    print("✅ 演示完成!")
    print("="*70)


if __name__ == "__main__":
    demo_stock_recommender()
