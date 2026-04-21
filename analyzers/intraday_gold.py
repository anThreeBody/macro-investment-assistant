#!/usr/bin/env python3
"""
黄金日内分析模块
提供小时级金价数据采集和日内最佳买卖时机识别
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalType(Enum):
    """信号类型"""
    BUY = "买入"
    SELL = "卖出"
    HOLD = "持有"
    NONE = "无信号"


class ConfidenceLevel(Enum):
    """置信度等级"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


@dataclass
class IntradaySignal:
    """日内交易信号"""
    signal_type: SignalType
    confidence: ConfidenceLevel
    confidence_score: float
    current_price: float
    target_price: float
    stop_loss: float
    take_profit: float
    reason: str
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "signal_type": self.signal_type.value,
            "confidence": self.confidence.value,
            "confidence_score": round(self.confidence_score, 2),
            "current_price": self.current_price,
            "target_price": self.target_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat()
        }


class GoldIntradayAnalyzer:
    """黄金日内分析器"""
    
    def __init__(self):
        self.hourly_data: List[Dict] = []
        self.support_levels: List[float] = []
        self.resistance_levels: List[float] = []
        
        # 信号阈值配置
        self.signal_thresholds = {
            "buy_rsi": 30,      # RSI低于30买入
            "sell_rsi": 70,     # RSI高于70卖出
            "min_confidence": 0.6,  # 最小置信度
        }
    
    def add_hourly_data(self, hour: int, price: float, volume: float = 0):
        """添加小时数据"""
        self.hourly_data.append({
            "hour": hour,
            "price": price,
            "volume": volume,
            "timestamp": datetime.now().replace(hour=hour, minute=0, second=0)
        })
        
        # 保持最近24小时数据
        if len(self.hourly_data) > 24:
            self.hourly_data = self.hourly_data[-24:]
    
    def calculate_hourly_rsi(self, period: int = 14) -> float:
        """计算小时级RSI"""
        if len(self.hourly_data) < period + 1:
            return 50.0  # 数据不足返回中性
        
        prices = [d["price"] for d in self.hourly_data[-period-1:]]
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_hourly_macd(self) -> Tuple[float, float, float]:
        """计算小时级MACD"""
        if len(self.hourly_data) < 26:
            return 0.0, 0.0, 0.0
        
        prices = [d["price"] for d in self.hourly_data]
        
        # 计算EMA12和EMA26
        ema12 = self._calculate_ema(prices, 12)
        ema26 = self._calculate_ema(prices, 26)
        
        # DIF线
        dif = ema12 - ema26
        
        # DEA线 (DIF的9日EMA)
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
    
    def identify_support_resistance(self) -> Tuple[List[float], List[float]]:
        """识别支撑和阻力位"""
        if len(self.hourly_data) < 5:
            return [], []
        
        prices = [d["price"] for d in self.hourly_data]
        
        # 简单识别：最近5小时的最低/最高
        recent_prices = prices[-5:]
        
        support = min(recent_prices) * 0.998  # 支撑位略低于最低
        resistance = max(recent_prices) * 1.002  # 阻力位略高于最高
        
        self.support_levels = [support]
        self.resistance_levels = [resistance]
        
        return [support], [resistance]
    
    def generate_intraday_signal(self, current_price: float) -> IntradaySignal:
        """生成日内交易信号"""
        
        # 计算技术指标
        rsi = self.calculate_hourly_rsi()
        dif, dea, macd = self.calculate_hourly_macd()
        
        # 识别支撑阻力
        supports, resistances = self.identify_support_resistance()
        
        # 初始化信号
        signal_type = SignalType.HOLD
        confidence_score = 0.5
        reason = ""
        
        # 买入信号判断
        buy_signals = []
        
        # RSI超卖
        if rsi < self.signal_thresholds["buy_rsi"]:
            buy_signals.append(f"RSI超卖({rsi:.1f})")
            confidence_score += 0.15
        
        # MACD金叉
        if dif > dea and macd > 0:
            buy_signals.append("MACD金叉")
            confidence_score += 0.15
        
        # 价格接近支撑位
        if supports and current_price <= supports[0] * 1.005:
            buy_signals.append(f"接近支撑位({supports[0]:.2f})")
            confidence_score += 0.1
        
        # 卖出信号判断
        sell_signals = []
        
        # RSI超买
        if rsi > self.signal_thresholds["sell_rsi"]:
            sell_signals.append(f"RSI超买({rsi:.1f})")
            confidence_score += 0.15
        
        # MACD死叉
        if dif < dea and macd < 0:
            sell_signals.append("MACD死叉")
            confidence_score += 0.15
        
        # 价格接近阻力位
        if resistances and current_price >= resistances[0] * 0.995:
            sell_signals.append(f"接近阻力位({resistances[0]:.2f})")
            confidence_score += 0.1
        
        # 确定信号类型
        if len(buy_signals) >= 2 and confidence_score >= self.signal_thresholds["min_confidence"]:
            signal_type = SignalType.BUY
            reason = "买入信号: " + "; ".join(buy_signals)
        elif len(sell_signals) >= 2 and confidence_score >= self.signal_thresholds["min_confidence"]:
            signal_type = SignalType.SELL
            reason = "卖出信号: " + "; ".join(sell_signals)
        else:
            reason = "观望: 信号不足"
            if buy_signals:
                reason += " | 潜在买入: " + "; ".join(buy_signals)
            if sell_signals:
                reason += " | 潜在卖出: " + "; ".join(sell_signals)
        
        # 确定置信度
        if confidence_score >= 0.8:
            confidence = ConfidenceLevel.HIGH
        elif confidence_score >= 0.6:
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW
        
        # 计算目标价和止损
        if signal_type == SignalType.BUY:
            target_price = current_price * 1.005  # 目标涨0.5%
            stop_loss = current_price * 0.995     # 止损跌0.5%
            take_profit = current_price * 1.01    # 止盈涨1%
        elif signal_type == SignalType.SELL:
            target_price = current_price * 0.995  # 目标跌0.5%
            stop_loss = current_price * 1.005     # 止损涨0.5%
            take_profit = current_price * 0.99    # 止盈跌1%
        else:
            target_price = current_price
            stop_loss = current_price * 0.99
            take_profit = current_price * 1.01
        
        return IntradaySignal(
            signal_type=signal_type,
            confidence=confidence,
            confidence_score=min(confidence_score, 1.0),
            current_price=current_price,
            target_price=target_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason=reason,
            timestamp=datetime.now()
        )
    
    def get_best_trading_hours(self) -> Dict:
        """获取最佳交易时段"""
        # 基于历史数据分析最佳时段
        # 简化版：返回常见的黄金活跃时段
        return {
            "亚洲时段": {"start": "09:00", "end": "17:00", "volatility": "中"},
            "欧洲时段": {"start": "15:00", "end": "23:00", "volatility": "高"},
            "美洲时段": {"start": "21:00", "end": "05:00", "volatility": "最高"},
            "重叠时段": {
                "欧美的重叠": "21:00-23:00 (高波动)",
                "亚欧的重叠": "15:00-17:00 (中波动)"
            }
        }


# 便捷函数
def analyze_intraday_gold(current_price: float, hourly_prices: List[float] = None) -> Dict:
    """
    分析黄金日内交易机会
    
    Args:
        current_price: 当前金价
        hourly_prices: 最近24小时价格列表（可选）
        
    Returns:
        交易信号字典
    """
    analyzer = GoldIntradayAnalyzer()
    
    # 添加小时数据
    if hourly_prices:
        for i, price in enumerate(hourly_prices[-24:]):
            analyzer.add_hourly_data(i, price)
    else:
        # 模拟一些数据用于测试
        for i in range(10):
            analyzer.add_hourly_data(i, current_price * (1 + (i-5)*0.001))
    
    # 生成信号
    signal = analyzer.generate_intraday_signal(current_price)
    
    # 获取最佳时段
    best_hours = analyzer.get_best_trading_hours()
    
    return {
        "signal": signal.to_dict(),
        "best_trading_hours": best_hours,
        "technical_indicators": {
            "rsi": analyzer.calculate_hourly_rsi(),
            "support_levels": analyzer.support_levels,
            "resistance_levels": analyzer.resistance_levels
        }
    }


if __name__ == "__main__":
    # 测试
    print("=== 黄金日内分析测试 ===\n")
    
    current_price = 4576.30  # 当前国际金价
    
    # 模拟最近10小时价格（有波动）
    hourly_prices = [
        4560.0, 4565.0, 4570.0, 4568.0, 4572.0,
        4575.0, 4578.0, 4576.0, 4574.0, 4576.30
    ]
    
    result = analyze_intraday_gold(current_price, hourly_prices)
    
    print(f"当前金价: ${current_price}/盎司")
    print(f"\n交易信号: {result['signal']['signal_type']}")
    print(f"置信度: {result['signal']['confidence']} ({result['signal']['confidence_score']})")
    print(f"目标价: ${result['signal']['target_price']:.2f}")
    print(f"止损价: ${result['signal']['stop_loss']:.2f}")
    print(f"止盈价: ${result['signal']['take_profit']:.2f}")
    print(f"\n理由: {result['signal']['reason']}")
    
    print("\n=== 技术指标 ===")
    print(f"RSI: {result['technical_indicators']['rsi']:.2f}")
    print(f"支撑位: {result['technical_indicators']['support_levels']}")
    print(f"阻力位: {result['technical_indicators']['resistance_levels']}")
    
    print("\n=== 最佳交易时段 ===")
    for period, info in result['best_trading_hours'].items():
        print(f"{period}: {info}")
