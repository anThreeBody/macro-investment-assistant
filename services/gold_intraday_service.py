#!/usr/bin/env python3
"""
黄金日内交易服务
整合日内分析、实时推送和最佳时机识别
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json

# 导入相关模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.intraday_gold import GoldIntradayAnalyzer, SignalType, ConfidenceLevel
from notifiers.realtime_pusher import RealTimePusher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoldIntradayService:
    """黄金日内交易服务"""
    
    def __init__(self):
        self.analyzer = GoldIntradayAnalyzer()
        self.pusher = RealTimePusher()
        
        # 服务状态
        self.is_running = False
        self.last_check_time: Optional[datetime] = None
        
        # 今日统计
        self.today_signals: List[Dict] = []
        self.best_opportunities: List[Dict] = []
        
        logger.info("[日内交易服务] 初始化完成")
    
    def analyze_current_opportunity(self, current_price: float, 
                                   hourly_prices: List[float] = None) -> Dict:
        """
        分析当前交易机会
        
        Args:
            current_price: 当前金价
            hourly_prices: 小时价格历史
            
        Returns:
            完整分析结果
        """
        # 添加小时数据
        if hourly_prices:
            for i, price in enumerate(hourly_prices[-24:]):
                self.analyzer.add_hourly_data(i, price)
        
        # 生成信号
        signal = self.analyzer.generate_intraday_signal(current_price)
        
        # 获取最佳时段
        best_hours = self.analyzer.get_best_trading_hours()
        
        # 判断是否为最佳机会
        is_best_opportunity = self._is_best_opportunity(signal)
        
        # 构建结果
        result = {
            "timestamp": datetime.now().isoformat(),
            "current_price": current_price,
            "signal": signal.to_dict(),
            "best_trading_hours": best_hours,
            "is_best_opportunity": is_best_opportunity,
            "technical_analysis": {
                "rsi": self.analyzer.calculate_hourly_rsi(),
                "support_levels": self.analyzer.support_levels,
                "resistance_levels": self.analyzer.resistance_levels
            },
            "recommendation": self._generate_recommendation(signal, is_best_opportunity)
        }
        
        # 保存信号
        self.today_signals.append(result)
        
        if is_best_opportunity:
            self.best_opportunities.append(result)
        
        # 尝试推送
        if is_best_opportunity:
            self.pusher.push(signal.to_dict())
        
        self.last_check_time = datetime.now()
        
        return result
    
    def _is_best_opportunity(self, signal) -> bool:
        """判断是否为最佳机会"""
        # 高置信度买入/卖出信号
        if signal.confidence == ConfidenceLevel.HIGH:
            return True
        
        # 中置信度但接近支撑/阻力位
        if signal.confidence == ConfidenceLevel.MEDIUM and signal.signal_type != SignalType.HOLD:
            return True
        
        return False
    
    def _generate_recommendation(self, signal, is_best_opportunity: bool) -> str:
        """生成交易建议"""
        if not is_best_opportunity:
            return "当前不是最佳交易时机，建议观望。"
        
        if signal.signal_type == SignalType.BUY:
            return f"""
🟢 买入建议:
• 当前价格: ${signal.current_price:.2f}
• 建议买入价: ${signal.current_price:.2f} - ${signal.target_price:.2f}
• 止损设置: ${signal.stop_loss:.2f} (跌破止损)
• 目标止盈: ${signal.take_profit:.2f} (达到止盈)
• 仓位建议: 30-50% (根据风险偏好)
• 持有周期: 日内或隔夜

{signal.reason}
            """.strip()
        
        elif signal.signal_type == SignalType.SELL:
            return f"""
🔴 卖出建议:
• 当前价格: ${signal.current_price:.2f}
• 建议卖出价: ${signal.current_price:.2f} - ${signal.target_price:.2f}
• 止损设置: ${signal.stop_loss:.2f} (涨破止损)
• 目标止盈: ${signal.take_profit:.2f} (达到止盈)
• 仓位建议: 卖出持仓的50-100%

{signal.reason}
            """.strip()
        
        else:
            return "持有观望，等待更明确信号。"
    
    def get_today_summary(self) -> Dict:
        """获取今日汇总"""
        buy_signals = [s for s in self.today_signals if s["signal"]["signal_type"] == "BUY"]
        sell_signals = [s for s in self.today_signals if s["signal"]["signal_type"] == "SELL"]
        hold_signals = [s for s in self.today_signals if s["signal"]["signal_type"] == "HOLD"]
        
        return {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "total_signals": len(self.today_signals),
            "buy_signals": len(buy_signals),
            "sell_signals": len(sell_signals),
            "hold_signals": len(hold_signals),
            "best_opportunities": len(self.best_opportunities),
            "last_check": self.last_check_time.isoformat() if self.last_check_time else None,
            "push_stats": self.pusher.get_push_stats()
        }
    
    def generate_intraday_report(self) -> str:
        """生成日内交易报告"""
        summary = self.get_today_summary()
        
        report = f"""
# 📊 黄金日内交易报告

**日期**: {summary['date']}  
**生成时间**: {datetime.now().strftime('%H:%M:%S')}

---

## 📈 今日信号统计

| 类型 | 数量 |
|------|------|
| 买入信号 | {summary['buy_signals']} |
| 卖出信号 | {summary['sell_signals']} |
| 观望信号 | {summary['hold_signals']} |
| **最佳机会** | **{summary['best_opportunities']}** |

## 🔔 推送统计

- 今日推送: {summary['push_stats']['today_pushes']}
- 推送上限: {summary['push_stats']['daily_limit']}
- 剩余次数: {summary['push_stats']['remaining_today']}

## ⏰ 最佳交易时段

- **亚洲时段**: 09:00-17:00 (波动中)
- **欧洲时段**: 15:00-23:00 (波动高)
- **美洲时段**: 21:00-05:00 (波动最高)
- **重叠时段**: 21:00-23:00 (欧美重叠，最佳)

## 💡 交易建议

1. **优先关注**: 21:00-23:00 欧美重叠时段
2. **设置提醒**: 价格接近支撑/阻力位时
3. **严格止损**: 单笔亏损不超过本金的2%
4. **分批操作**: 不要一次性满仓

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
        """.strip()
        
        return report


def demo_intraday_service():
    """演示日内交易服务"""
    print("="*70)
    print("🎯 黄金日内交易服务演示")
    print("="*70)
    
    service = GoldIntradayService()
    
    # 模拟当前金价和小时数据
    current_price = 4576.30
    hourly_prices = [
        4550.0, 4560.0, 4565.0, 4570.0, 4568.0,
        4572.0, 4575.0, 4578.0, 4576.0, 4574.0,
        4576.30, 4575.0, 4574.0, 4573.0, 4572.0
    ]
    
    print(f"\n当前金价: ${current_price}/盎司")
    print(f"数据点数: {len(hourly_prices)} 小时")
    
    # 分析当前机会
    print("\n" + "-"*70)
    print("🔍 分析当前交易机会...")
    print("-"*70)
    
    result = service.analyze_current_opportunity(current_price, hourly_prices)
    
    print(f"\n信号类型: {result['signal']['signal_type']}")
    print(f"置信度: {result['signal']['confidence']} ({result['signal']['confidence_score']})")
    print(f"是否为最佳机会: {'是' if result['is_best_opportunity'] else '否'}")
    
    print(f"\n技术指标:")
    print(f"  RSI: {result['technical_analysis']['rsi']:.2f}")
    print(f"  支撑位: {result['technical_analysis']['support_levels']}")
    print(f"  阻力位: {result['technical_analysis']['resistance_levels']}")
    
    print(f"\n交易建议:")
    print(result['recommendation'])
    
    # 显示今日汇总
    print("\n" + "="*70)
    print("📊 今日汇总")
    print("="*70)
    
    summary = service.get_today_summary()
    print(f"总信号数: {summary['total_signals']}")
    print(f"买入信号: {summary['buy_signals']}")
    print(f"卖出信号: {summary['sell_signals']}")
    print(f"最佳机会: {summary['best_opportunities']}")
    
    # 生成报告
    print("\n" + "="*70)
    print("📄 生成日内交易报告")
    print("="*70)
    
    report = service.generate_intraday_report()
    print(report)
    
    # 保存报告
    report_file = Path(__file__).parent.parent / "daily_brief" / f"intraday_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存: {report_file}")


if __name__ == "__main__":
    demo_intraday_service()
