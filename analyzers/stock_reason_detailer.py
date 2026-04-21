#!/usr/bin/env python3
"""
个股理由详化系统
技术面 + 基本面 + 资金面详细分析
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DetailedAnalysis:
    """详细分析结果"""
    technical_detail: str     # 技术面详细分析
    fundamental_detail: str   # 基本面详细分析
    capital_detail: str       # 资金面详细分析
    industry_detail: str      # 行业分析
    risk_assessment: str      # 风险评估
    investment_logic: str     # 投资逻辑
    catalysts: List[str]      # 催化剂
    risks: List[str]          # 风险点
    comparable_analysis: str  # 可比公司分析
    valuation_analysis: str   # 估值分析


class StockReasonDetailer:
    """个股理由详化器"""
    
    def __init__(self):
        # 行业基准数据
        self.industry_benchmarks = {
            "银行": {"pe": 6, "pb": 0.8, "roe": 10},
            "保险": {"pe": 12, "pb": 1.5, "roe": 15},
            "券商": {"pe": 20, "pb": 1.8, "roe": 8},
            "白酒": {"pe": 30, "pb": 8, "roe": 25},
            "医药": {"pe": 35, "pb": 5, "roe": 15},
            "科技": {"pe": 50, "pb": 6, "roe": 12},
            "新能源": {"pe": 40, "pb": 4, "roe": 15},
            "消费": {"pe": 25, "pb": 4, "roe": 18},
            "制造": {"pe": 20, "pb": 2, "roe": 12},
            "地产": {"pe": 8, "pb": 1, "roe": 15}
        }
        
        logger.info("[理由详化] 初始化完成")
    
    def detail_technical(self, rsi: float, macd: float, signal: float,
                        ma5: float, ma10: float, ma20: float, ma60: float,
                        bb_upper: float, bb_lower: float, current_price: float,
                        volume_ratio: float, trend: str) -> str:
        """
        技术面详细分析
        """
        analysis_parts = []
        
        # 趋势分析
        analysis_parts.append("【趋势分析】")
        if current_price > ma5 > ma10 > ma20 > ma60:
            analysis_parts.append("✅ 股价处于多头排列，各周期均线向上发散，中期趋势强劲。")
        elif current_price > ma5 > ma10:
            analysis_parts.append("⚠️ 短期均线多头排列，但中长期均线走平，短期趋势向好但需关注中期压力。")
        elif current_price < ma5 < ma10 < ma20:
            analysis_parts.append("❌ 股价处于空头排列，各周期均线向下，趋势偏弱。")
        else:
            analysis_parts.append("➡️ 均线交织，趋势不明朗，处于震荡整理阶段。")
        
        # RSI分析
        analysis_parts.append("\n【RSI指标】")
        if rsi < 30:
            analysis_parts.append(f"✅ RSI为{rsi:.1f}，处于超卖区域，短期存在反弹需求。")
        elif rsi > 70:
            analysis_parts.append(f"⚠️ RSI为{rsi:.1f}，处于超买区域，短期存在回调压力。")
        elif 40 <= rsi <= 60:
            analysis_parts.append(f"➡️ RSI为{rsi:.1f}，处于中性区域，多空力量均衡。")
        else:
            analysis_parts.append(f"📊 RSI为{rsi:.1f}，偏向{'强势' if rsi > 50 else '弱势'}区域。")
        
        # MACD分析
        analysis_parts.append("\n【MACD指标】")
        if macd > signal and macd > 0:
            analysis_parts.append("✅ MACD金叉且在零轴上方，上涨动能增强，多头占优。")
        elif macd > signal and macd < 0:
            analysis_parts.append("⚠️ MACD金叉但在零轴下方，反弹动能较弱，需观察能否突破零轴。")
        elif macd < signal and macd > 0:
            analysis_parts.append("⚠️ MACD死叉且在零轴上方，上涨动能减弱，需警惕回调。")
        else:
            analysis_parts.append("❌ MACD死叉且在零轴下方，下跌动能较强，空头占优。")
        
        # 布林带分析
        analysis_parts.append("\n【布林带】")
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) * 100
        if current_price > bb_upper:
            analysis_parts.append(f"⚠️ 股价突破布林带上轨({bb_upper:.2f})，短期超买，注意回调风险。")
        elif current_price < bb_lower:
            analysis_parts.append(f"✅ 股价跌破布林带下轨({bb_lower:.2f})，短期超卖，存在反弹机会。")
        elif bb_position > 70:
            analysis_parts.append(f"📈 股价位于布林带上轨附近({bb_position:.0f}%)，相对强势。")
        elif bb_position < 30:
            analysis_parts.append(f"📉 股价位于布林带下轨附近({bb_position:.0f}%)，相对弱势。")
        else:
            analysis_parts.append(f"➡️ 股价位于布林带中轨附近({bb_position:.0f}%)，处于正常波动区间。")
        
        # 成交量分析
        analysis_parts.append("\n【成交量】")
        if volume_ratio > 2:
            analysis_parts.append(f"✅ 成交量放大至均量的{volume_ratio:.1f}倍，资金关注度提升，量价配合良好。")
        elif volume_ratio > 1.5:
            analysis_parts.append(f"📊 成交量温和放大至{volume_ratio:.1f}倍，交投活跃度提升。")
        elif volume_ratio < 0.5:
            analysis_parts.append(f"⚠️ 成交量萎缩至{volume_ratio:.1f}倍，市场参与度低，需等待放量信号。")
        else:
            analysis_parts.append(f"➡️ 成交量正常({volume_ratio:.1f}倍)，交投平稳。")
        
        return "\n".join(analysis_parts)
    
    def detail_fundamental(self, pe: float, pb: float, roe: float,
                          revenue_growth: float, profit_growth: float,
                          debt_ratio: float, industry: str) -> str:
        """
        基本面详细分析
        """
        analysis_parts = []
        
        # 获取行业基准
        benchmark = self.industry_benchmarks.get(industry, {"pe": 20, "pb": 2, "roe": 12})
        
        analysis_parts.append("【估值分析】")
        
        # PE分析
        pe_vs_industry = (pe / benchmark["pe"] - 1) * 100
        if pe < benchmark["pe"] * 0.8:
            analysis_parts.append(f"✅ PE为{pe:.1f}倍，低于行业平均{benchmark['pe']:.1f}倍({pe_vs_industry:.0f}%)，估值偏低，具备安全边际。")
        elif pe > benchmark["pe"] * 1.2:
            analysis_parts.append(f"⚠️ PE为{pe:.1f}倍，高于行业平均{benchmark['pe']:.1f}倍(+{pe_vs_industry:.0f}%)，估值偏高，需业绩支撑。")
        else:
            analysis_parts.append(f"➡️ PE为{pe:.1f}倍，与行业平均{benchmark['pe']:.1f}倍基本持平，估值合理。")
        
        # PB分析
        pb_vs_industry = (pb / benchmark["pb"] - 1) * 100
        if pb < benchmark["pb"] * 0.8:
            analysis_parts.append(f"✅ PB为{pb:.1f}倍，低于行业平均{benchmark['pb']:.1f}倍({pb_vs_industry:.0f}%)，资产价值被低估。")
        elif pb > benchmark["pb"] * 1.2:
            analysis_parts.append(f"⚠️ PB为{pb:.1f}倍，高于行业平均{benchmark['pb']:.1f}倍(+{pb_vs_industry:.0f}%)，资产溢价较高。")
        else:
            analysis_parts.append(f"➡️ PB为{pb:.1f}倍，与行业平均{benchmark['pb']:.1f}倍基本持平。")
        
        analysis_parts.append("\n【盈利能力】")
        
        # ROE分析
        roe_vs_industry = (roe / benchmark["roe"] - 1) * 100
        if roe > benchmark["roe"] * 1.2:
            analysis_parts.append(f"✅ ROE为{roe:.1f}%，高于行业平均{benchmark['roe']:.1f}%({roe_vs_industry:.0f}%)，盈利能力优秀。")
        elif roe < benchmark["roe"] * 0.8:
            analysis_parts.append(f"⚠️ ROE为{roe:.1f}%，低于行业平均{benchmark['roe']:.1f}%({roe_vs_industry:.0f}%)，盈利能力有待提升。")
        else:
            analysis_parts.append(f"➡️ ROE为{roe:.1f}%，与行业平均{benchmark['roe']:.1f}%基本持平。")
        
        analysis_parts.append("\n【成长性】")
        
        # 营收增长
        if revenue_growth > 30:
            analysis_parts.append(f"✅ 营收同比增长{revenue_growth:.1f}%，高速增长，业务扩张强劲。")
        elif revenue_growth > 15:
            analysis_parts.append(f"📈 营收同比增长{revenue_growth:.1f}%，稳健增长，业务发展良好。")
        elif revenue_growth > 0:
            analysis_parts.append(f"➡️ 营收同比增长{revenue_growth:.1f}%，增速放缓，需关注业务变化。")
        else:
            analysis_parts.append(f"❌ 营收同比增长{revenue_growth:.1f}%，出现下滑，需警惕经营风险。")
        
        # 利润增长
        if profit_growth > 30:
            analysis_parts.append(f"✅ 净利润同比增长{profit_growth:.1f}%，利润增速强劲，盈利能力提升。")
        elif profit_growth > 15:
            analysis_parts.append(f"📈 净利润同比增长{profit_growth:.1f}%，利润稳健增长。")
        elif profit_growth > 0:
            analysis_parts.append(f"➡️ 净利润同比增长{profit_growth:.1f}%，利润增速放缓。")
        else:
            analysis_parts.append(f"❌ 净利润同比增长{profit_growth:.1f}%，利润下滑，需关注成本控制和业务调整。")
        
        analysis_parts.append("\n【财务健康】")
        
        # 负债率
        if debt_ratio < 40:
            analysis_parts.append(f"✅ 负债率为{debt_ratio:.1f}%，财务结构稳健，偿债压力小。")
        elif debt_ratio < 60:
            analysis_parts.append(f"➡️ 负债率为{debt_ratio:.1f}%，财务结构合理，处于行业正常水平。")
        elif debt_ratio < 80:
            analysis_parts.append(f"⚠️ 负债率为{debt_ratio:.1f}%，负债水平较高，需关注偿债能力。")
        else:
            analysis_parts.append(f"❌ 负债率为{debt_ratio:.1f}%，负债率过高，财务风险较大。")
        
        return "\n".join(analysis_parts)
    
    def detail_capital(self, main_force: float, north_bound: float,
                      turnover: float, margin: float) -> str:
        """
        资金面详细分析
        """
        analysis_parts = []
        
        analysis_parts.append("【主力资金】")
        if main_force > 2:
            analysis_parts.append(f"✅ 主力资金大幅净流入{main_force:.1f}亿元，机构资金积极布局，看好后市。")
        elif main_force > 1:
            analysis_parts.append(f"📈 主力资金净流入{main_force:.1f}亿元，资金持续流入，态度积极。")
        elif main_force > 0:
            analysis_parts.append(f"➡️ 主力资金小幅净流入{main_force:.1f}亿元，资金态度中性。")
        elif main_force > -1:
            analysis_parts.append(f"➡️ 主力资金小幅净流出{abs(main_force):.1f}亿元，资金态度中性。")
        elif main_force > -2:
            analysis_parts.append(f"📉 主力资金净流出{abs(main_force):.1f}亿元，资金持续流出，态度谨慎。")
        else:
            analysis_parts.append(f"❌ 主力资金大幅净流出{abs(main_force):.1f}亿元，机构资金撤离，需警惕。")
        
        analysis_parts.append("\n【北向资金】")
        if north_bound > 1:
            analysis_parts.append(f"✅ 北向资金净流入{north_bound:.1f}亿元，外资积极买入，看好A股配置价值。")
        elif north_bound > 0.5:
            analysis_parts.append(f"📈 北向资金净流入{north_bound:.1f}亿元，外资持续流入。")
        elif north_bound > -0.5:
            analysis_parts.append(f"➡️ 北向资金小幅波动，外资态度中性。")
        elif north_bound > -1:
            analysis_parts.append(f"📉 北向资金净流出{abs(north_bound):.1f}亿元，外资小幅减持。")
        else:
            analysis_parts.append(f"❌ 北向资金净流出{abs(north_bound):.1f}亿元，外资大幅减持，需关注。")
        
        analysis_parts.append("\n【市场活跃度】")
        if turnover > 10:
            analysis_parts.append(f"⚠️ 换手率为{turnover:.1f}%，交易异常活跃，可能存在炒作风险。")
        elif 5 <= turnover <= 10:
            analysis_parts.append(f"✅ 换手率为{turnover:.1f}%，交易活跃，市场关注度高。")
        elif 2 <= turnover < 5:
            analysis_parts.append(f"➡️ 换手率为{turnover:.1f}%，交易正常，流动性良好。")
        else:
            analysis_parts.append(f"⚠️ 换手率为{turnover:.1f}%，交易清淡，流动性不足。")
        
        analysis_parts.append("\n【融资融券】")
        if margin > 20:
            analysis_parts.append(f"✅ 融资余额增加{margin:.1f}%，杠杆资金积极加仓，市场情绪乐观。")
        elif margin > 10:
            analysis_parts.append(f"📈 融资余额增加{margin:.1f}%，杠杆资金流入。")
        elif margin > -10:
            analysis_parts.append(f"➡️ 融资余额变化不大，杠杆资金态度中性。")
        elif margin > -20:
            analysis_parts.append(f"📉 融资余额减少{abs(margin):.1f}%，杠杆资金减仓。")
        else:
            analysis_parts.append(f"❌ 融资余额大幅减少{abs(margin):.1f}%，杠杆资金撤离，情绪悲观。")
        
        return "\n".join(analysis_parts)
    
    def generate_detailed_analysis(self, code: str, name: str, industry: str,
                                  technical_data: Dict, fundamental_data: Dict,
                                  capital_data: Dict) -> DetailedAnalysis:
        """
        生成详细分析
        """
        # 技术面详细分析
        technical_detail = self.detail_technical(
            technical_data.get("rsi", 50),
            technical_data.get("macd", 0),
            technical_data.get("signal", 0),
            technical_data.get("ma5", 0),
            technical_data.get("ma10", 0),
            technical_data.get("ma20", 0),
            technical_data.get("ma60", 0),
            technical_data.get("bb_upper", 0),
            technical_data.get("bb_lower", 0),
            technical_data.get("current_price", 0),
            technical_data.get("volume_ratio", 1),
            technical_data.get("trend", "SIDE")
        )
        
        # 基本面详细分析
        fundamental_detail = self.detail_fundamental(
            fundamental_data.get("pe", 20),
            fundamental_data.get("pb", 2),
            fundamental_data.get("roe", 10),
            fundamental_data.get("revenue_growth", 0),
            fundamental_data.get("profit_growth", 0),
            fundamental_data.get("debt_ratio", 50),
            industry
        )
        
        # 资金面详细分析
        capital_detail = self.detail_capital(
            capital_data.get("main_force", 0),
            capital_data.get("north_bound", 0),
            capital_data.get("turnover", 5),
            capital_data.get("margin", 0)
        )
        
        # 行业分析
        industry_detail = f"【{industry}行业分析】\n"
        if industry in self.industry_benchmarks:
            benchmark = self.industry_benchmarks[industry]
            industry_detail += f"该行业平均PE为{benchmark['pe']}倍，PB为{benchmark['pb']}倍，ROE为{benchmark['roe']}%。"
        else:
            industry_detail += "该行业数据暂缺，建议参考可比公司进行分析。"
        
        # 风险评估
        risks = []
        if fundamental_data.get("debt_ratio", 0) > 70:
            risks.append("负债率过高，财务风险较大")
        if fundamental_data.get("pe", 0) > 50:
            risks.append("估值偏高，存在估值回调风险")
        if capital_data.get("main_force", 0) < -1:
            risks.append("主力资金持续流出")
        if technical_data.get("rsi", 50) > 70:
            risks.append("技术指标超买，存在回调压力")
        
        risk_assessment = "【风险评估】\n"
        if risks:
            risk_assessment += "主要风险点：\n" + "\n".join([f"• {r}" for r in risks])
        else:
            risk_assessment += "当前风险可控，无重大风险点。"
        
        # 投资逻辑
        investment_logic = "【投资逻辑】\n"
        investment_logic += "基于技术面、基本面、资金面综合分析，该股票具备以下投资逻辑：\n"
        
        catalysts = []
        if fundamental_data.get("profit_growth", 0) > 20:
            catalysts.append("业绩高增长")
        if capital_data.get("main_force", 0) > 1:
            catalysts.append("主力资金流入")
        if technical_data.get("rsi", 50) < 30:
            catalysts.append("技术超卖反弹")
        if fundamental_data.get("pe", 20) < 15:
            catalysts.append("估值修复")
        
        if catalysts:
            investment_logic += "催化剂：" + "、".join(catalysts)
        else:
            investment_logic += "等待更明确的催化剂出现。"
        
        # 可比公司分析
        comparable_analysis = "【可比公司分析】\n"
        comparable_analysis += "建议对比同行业龙头公司的估值水平和盈利能力，寻找相对优势。"
        
        # 估值分析
        pe = fundamental_data.get("pe", 20)
        pb = fundamental_data.get("pb", 2)
        valuation_analysis = f"【估值分析】\n当前PE为{pe:.1f}倍，PB为{pb:.1f}倍。"
        
        return DetailedAnalysis(
            technical_detail=technical_detail,
            fundamental_detail=fundamental_detail,
            capital_detail=capital_detail,
            industry_detail=industry_detail,
            risk_assessment=risk_assessment,
            investment_logic=investment_logic,
            catalysts=catalysts,
            risks=risks,
            comparable_analysis=comparable_analysis,
            valuation_analysis=valuation_analysis
        )
    
    def format_full_report(self, analysis: DetailedAnalysis) -> str:
        """格式化完整报告"""
        report = f"""
# 📊 个股详细分析报告

## 📈 技术面分析

{analysis.technical_detail}

---

## 💼 基本面分析

{analysis.fundamental_detail}

---

## 💰 资金面分析

{analysis.capital_detail}

---

## 🏭 行业分析

{analysis.industry_detail}

---

## ⚠️ 风险评估

{analysis.risk_assessment}

---

## 💡 投资逻辑

{analysis.investment_logic}

**催化剂**: {', '.join(analysis.catalysts) if analysis.catalysts else '暂无'}

---

## 📊 估值分析

{analysis.valuation_analysis}

---

## 🏢 可比公司分析

{analysis.comparable_analysis}

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
        """.strip()
        
        return report


def demo_stock_detailer():
    """演示个股理由详化系统"""
    print("="*70)
    print("🎯 个股理由详化系统演示")
    print("="*70)
    
    detailer = StockReasonDetailer()
    
    # 模拟数据
    code = "000001"
    name = "平安银行"
    industry = "银行"
    
    technical_data = {
        "rsi": 45,
        "macd": 0.1,
        "signal": -0.05,
        "ma5": 12.45,
        "ma10": 12.40,
        "ma20": 12.35,
        "ma60": 12.20,
        "bb_upper": 13.0,
        "bb_lower": 11.8,
        "current_price": 12.50,
        "volume_ratio": 1.5,
        "trend": "UP"
    }
    
    fundamental_data = {
        "pe": 8.5,
        "pb": 0.9,
        "roe": 12.5,
        "revenue_growth": 8.0,
        "profit_growth": 10.0,
        "debt_ratio": 92.0
    }
    
    capital_data = {
        "main_force": 1.5,
        "north_bound": 0.8,
        "turnover": 5.0,
        "margin": 15.0
    }
    
    print(f"\n📊 分析股票: {name} ({code})")
    print(f"行业: {industry}")
    
    # 生成详细分析
    analysis = detailer.generate_detailed_analysis(
        code, name, industry,
        technical_data, fundamental_data, capital_data
    )
    
    print(f"\n{'='*70}")
    print("📈 技术面详细分析")
    print(f"{'='*70}")
    print(analysis.technical_detail[:500] + "...")
    
    print(f"\n{'='*70}")
    print("💼 基本面详细分析")
    print(f"{'='*70}")
    print(analysis.fundamental_detail[:500] + "...")
    
    print(f"\n{'='*70}")
    print("💰 资金面详细分析")
    print(f"{'='*70}")
    print(analysis.capital_detail[:500] + "...")
    
    print(f"\n{'='*70}")
    print("💡 投资逻辑")
    print(f"{'='*70}")
    print(analysis.investment_logic)
    print(f"\n催化剂: {', '.join(analysis.catalysts) if analysis.catalysts else '暂无'}")
    
    print(f"\n{'='*70}")
    print("⚠️ 风险评估")
    print(f"{'='*70}")
    print(analysis.risk_assessment)
    
    print("\n" + "="*70)
    print("✅ 演示完成!")
    print("="*70)


if __name__ == "__main__":
    demo_stock_detailer()
