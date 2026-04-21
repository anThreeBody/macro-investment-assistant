#!/usr/bin/env python3
"""
股票分析服务
整合个股推荐升级和理由详化
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

# 导入相关模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.stock_recommender import StockRecommender
from analyzers.stock_reason_detailer import StockReasonDetailer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockAnalysisService:
    """股票分析服务"""
    
    def __init__(self):
        self.recommender = StockRecommender()
        self.detailer = StockReasonDetailer()
        
        logger.info("[股票服务] 初始化完成")
    
    def analyze_stock(self, code: str, name: str, industry: str,
                     current_price: float, price_history: List[float],
                     volume_history: List[float],
                     fundamental_data: Dict,
                     capital_data: Dict) -> Dict:
        """
        全面分析个股
        
        Returns:
            完整分析结果
        """
        # 生成推荐
        recommendation = self.recommender.generate_recommendation(
            code, name, industry, current_price,
            price_history, volume_history,
            fundamental_data, capital_data
        )
        
        # 获取交易策略
        strategy = self.recommender.get_trading_strategy(recommendation)
        
        # 准备技术分析数据
        technical_data = {
            "rsi": recommendation.technical_score * 100,  # 简化
            "macd": 0.1,
            "signal": -0.05,
            "ma5": current_price * 0.99,
            "ma10": current_price * 0.98,
            "ma20": current_price * 0.97,
            "ma60": current_price * 0.95,
            "bb_upper": current_price * 1.05,
            "bb_lower": current_price * 0.95,
            "current_price": current_price,
            "volume_ratio": 1.5,
            "trend": "UP" if recommendation.technical_score > 0.6 else "DOWN"
        }
        
        # 生成详细分析
        detailed = self.detailer.generate_detailed_analysis(
            code, name, industry,
            technical_data, fundamental_data, capital_data
        )
        
        # 格式化详细报告
        full_report = self.detailer.format_full_report(detailed)
        
        return {
            "code": recommendation.code,
            "name": recommendation.name,
            "industry": recommendation.industry,
            "current_price": recommendation.current_price,
            "signal": recommendation.signal,
            "confidence": recommendation.confidence,
            "target_price": recommendation.target_price,
            "stop_loss": recommendation.stop_loss,
            "take_profit": recommendation.take_profit,
            "position_size": recommendation.position_size,
            "holding_period": recommendation.holding_period,
            "risk_level": recommendation.risk_level,
            "technical_score": recommendation.technical_score,
            "fundamental_score": recommendation.fundamental_score,
            "capital_score": recommendation.capital_score,
            "overall_reason": recommendation.overall_reason,
            "strategy": strategy,
            "detailed_analysis": {
                "technical": detailed.technical_detail,
                "fundamental": detailed.fundamental_detail,
                "capital": detailed.capital_detail,
                "industry": detailed.industry_detail,
                "risk": detailed.risk_assessment,
                "logic": detailed.investment_logic,
                "catalysts": detailed.catalysts,
                "risks": detailed.risks
            },
            "full_report": full_report,
            "timestamp": recommendation.timestamp
        }
    
    def generate_stock_report(self, stocks_data: List[Dict]) -> str:
        """生成股票分析报告"""
        report = f"""# 📊 股票分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📈 个股推荐

"""
        
        for i, stock_data in enumerate(stocks_data, 1):
            result = self.analyze_stock(**stock_data)
            
            report += f"""
### {i}. {result['name']} ({result['code']}) - {result['signal']}

**基本信息**:
- 行业: {result['industry']}
- 当前价格: ¥{result['current_price']:.2f}
- 目标价格: ¥{result['target_price']:.2f}
- 止损价格: ¥{result['stop_loss']:.2f}
- 止盈价格: ¥{result['take_profit']:.2f}

**信号强度**: {result['signal']} | **置信度**: {result['confidence']:.1%}

**评分详情**:
- 技术面: {result['technical_score']:.1%}
- 基本面: {result['fundamental_score']:.1%}
- 资金面: {result['capital_score']:.1%}

**操作建议**:
- 仓位: {result['position_size']}
- 周期: {result['holding_period']}
- 风险: {result['risk_level']}

**核心逻辑**: {result['overall_reason']}

---

"""
        
        report += f"""
## ⚠️ 风险提示

1. 股票投资有风险，过往业绩不代表未来表现
2. 请根据自身风险承受能力选择合适标的
3. 建议分散投资，单只股票仓位不超过30%
4. 严格设置止损，控制单笔亏损
5. 定期关注基本面变化和市场环境

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def get_top_picks(self, market: str = "A股", top_n: int = 5) -> List[Dict]:
        """
        获取今日精选
        
        Args:
            market: 市场类型
            top_n: 数量
            
        Returns:
            精选股票列表
        """
        # 模拟今日精选数据
        picks = [
            {
                "code": "000001",
                "name": "平安银行",
                "industry": "银行",
                "signal": "买入",
                "confidence": 0.72,
                "reason": "估值偏低，主力资金流入"
            },
            {
                "code": "000858",
                "name": "五粮液",
                "industry": "白酒",
                "signal": "买入",
                "confidence": 0.75,
                "reason": "业绩稳健，北向资金增持"
            },
            {
                "code": "002594",
                "name": "比亚迪",
                "industry": "新能源",
                "signal": "持有",
                "confidence": 0.58,
                "reason": "行业龙头，等待回调买入"
            }
        ]
        
        return picks[:top_n]


def demo_stock_service():
    """演示股票分析服务"""
    print("="*70)
    print("🎯 股票分析服务演示")
    print("="*70)
    
    service = StockAnalysisService()
    
    # 模拟股票数据
    stock_data = {
        "code": "000001",
        "name": "平安银行",
        "industry": "银行",
        "current_price": 12.50,
        "price_history": [10.0 + i * 0.05 for i in range(60)],
        "volume_history": [1000000 + i * 1000 for i in range(60)],
        "fundamental_data": {
            "pe": 8.5,
            "pb": 0.9,
            "roe": 12.5,
            "revenue_growth": 8.0,
            "profit_growth": 10.0,
            "debt_ratio": 92.0
        },
        "capital_data": {
            "main_force": 1.5,
            "north_bound": 0.8,
            "turnover": 5.0,
            "margin": 15.0
        }
    }
    
    print(f"\n📊 分析股票: {stock_data['name']} ({stock_data['code']})")
    
    # 全面分析
    result = service.analyze_stock(**stock_data)
    
    print(f"\n{'='*70}")
    print("📈 分析结果")
    print(f"{'='*70}")
    
    print(f"\n信号: {result['signal']}")
    print(f"置信度: {result['confidence']:.1%}")
    print(f"目标价格: ¥{result['target_price']:.2f}")
    print(f"止损价格: ¥{result['stop_loss']:.2f}")
    print(f"止盈价格: ¥{result['take_profit']:.2f}")
    print(f"建议仓位: {result['position_size']}")
    print(f"风险等级: {result['risk_level']}")
    
    print(f"\n评分:")
    print(f"  技术面: {result['technical_score']:.1%}")
    print(f"  基本面: {result['fundamental_score']:.1%}")
    print(f"  资金面: {result['capital_score']:.1%}")
    
    print(f"\n{'='*70}")
    print("💡 交易策略")
    print(f"{'='*70}")
    print(result['strategy'][:800] + "...")
    
    print(f"\n{'='*70}")
    print("📊 详细分析")
    print(f"{'='*70}")
    print(f"技术面: {result['detailed_analysis']['technical'][:200]}...")
    print(f"\n基本面: {result['detailed_analysis']['fundamental'][:200]}...")
    print(f"\n资金面: {result['detailed_analysis']['capital'][:200]}...")
    
    # 获取今日精选
    print(f"\n{'='*70}")
    print("⭐ 今日精选")
    print(f"{'='*70}")
    
    picks = service.get_top_picks(top_n=3)
    for i, pick in enumerate(picks, 1):
        print(f"\n{i}. {pick['name']} ({pick['code']})")
        print(f"   信号: {pick['signal']} | 置信度: {pick['confidence']:.1%}")
        print(f"   理由: {pick['reason']}")
    
    # 生成报告
    print(f"\n{'='*70}")
    print("📄 生成股票分析报告")
    print(f"{'='*70}")
    
    report = service.generate_stock_report([stock_data])
    report_file = Path(__file__).parent.parent / "daily_brief" / f"stock_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 报告已保存: {report_file}")
    
    print("\n" + "="*70)
    print("✅ 股票分析服务演示完成!")
    print("="*70)


if __name__ == "__main__":
    demo_stock_service()
