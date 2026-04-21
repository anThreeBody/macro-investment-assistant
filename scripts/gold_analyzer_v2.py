#!/usr/bin/env python3
"""
增强版黄金分析模块 V2.0

明确标注价格来源：
- 上海黄金交易所现货合约价格（单位：元/100克 或特定合约单位）
- 估算国际金价（美元/盎司）
"""

import numpy as np
import akshare as ak
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from data_manager import get_data_manager


class GoldAnalyzerEnhancedV2:
    """增强版黄金分析器 V2.0"""
    
    def __init__(self):
        self.dm = get_data_manager()
        self.grams_per_ounce = 31.1035
    
    def get_usd_cny_rate(self) -> float:
        """获取美元兑人民币汇率"""
        try:
            fx = ak.fx_spot_quote()
            usd_cny = fx[fx['货币对'] == 'USD/CNY']['买报价'].values[0]
            return float(usd_cny)
        except Exception as e:
            logger.error(f"Error getting USD/CNY rate: {e}")
            return 6.90
    
    def calculate_international_price(self, sge_price: float, usd_cny: float) -> float:
        """
        估算国际金价
        
        注意：由于上海金价数据单位不确定，这里使用比例法估算
        假设当前上海金价与国际金价的比例关系
        """
        if sge_price <= 0 or usd_cny <= 0:
            return 0
        
        # 简化估算：假设上海金价与国际金价的比例相对稳定
        # 这个比例需要根据实际数据校准
        # 如果上海金价是 1112，国际金价约 2000，比例约 0.556
        estimated_ratio = 0.556  # 这个值需要根据实际情况调整
        
        international_price = sge_price / estimated_ratio
        return international_price
    
    def analyze(self) -> Dict:
        """完整分析黄金走势"""
        # 获取历史数据
        prices = self.dm.get_gold_prices(limit=60)
        
        if not prices:
            logger.warning("No gold data in database, trying to fetch...")
            return {"error": "无数据，请先运行数据同步"}
        
        # 转换为 DataFrame 格式
        df = self._prepare_data(prices)
        
        if len(df) < 5:
            return {"error": "数据不足，至少需要 5 天数据"}
        
        # 计算技术指标
        df = self._calculate_ma(df)
        df = self._calculate_rsi(df)
        df = self._calculate_macd(df)
        
        # 获取最新数据
        latest = df.iloc[-1]
        
        # 获取汇率
        usd_cny = self.get_usd_cny_rate()
        
        # 估算国际金价
        sge_price = latest['close']
        international_price = self.calculate_international_price(sge_price, usd_cny)
        
        # 分析趋势
        trend = self._analyze_trend(df)
        
        # 计算涨跌幅
        week_change = self._calculate_change(df, 5)
        month_change = self._calculate_change(df, 20)
        
        # 生成建议
        suggestion = self._generate_suggestion(df, trend)
        
        return {
            # 价格信息
            "current_price_sge": round(sge_price, 2),
            "current_price_international": round(international_price, 2),
            "price_unit_sge": "元/合约单位（上海金交所现货）",
            "price_unit_international": "美元/盎司（估算）",
            "usd_cny_rate": round(usd_cny, 4),
            
            # 涨跌幅
            "week_change": round(week_change, 2) if week_change else None,
            "month_change": round(month_change, 2) if month_change else None,
            
            # 技术指标
            "ma5": round(latest.get('ma5', 0), 2) if 'ma5' in latest else None,
            "ma10": round(latest.get('ma10', 0), 2) if 'ma10' in latest else None,
            "ma20": round(latest.get('ma20', 0), 2) if 'ma20' in latest else None,
            "rsi": round(latest.get('rsi', 0), 2) if 'rsi' in latest else None,
            "rsi_signal": self._interpret_rsi(latest.get('rsi', 50)),
            "macd_signal": self._interpret_macd(df),
            
            # 趋势
            "trend": trend['direction'],
            "trend_strength": trend['strength'],
            "support": round(latest.get('support', sge_price * 0.95), 2),
            "resistance": round(latest.get('resistance', sge_price * 1.05), 2),
            
            # 驱动因素
            "drivers": ["美元走势", "实际利率", "地缘政治风险", "央行购金需求"],
            
            # 建议
            "suggestion": suggestion,
            
            # 数据信息
            "data_points": len(df),
            "last_update": df.index[-1].strftime('%Y-%m-%d'),
            
            # 说明
            "note": "上海金价为上海黄金交易所现货合约价格，国际金价为基于比例估算"
        }
    
    def _prepare_data(self, prices: List[Dict]) -> 'pd.DataFrame':
        """准备数据"""
        import pandas as pd
        
        df = pd.DataFrame(prices)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        df = df.sort_index()
        
        # 使用平均价格
        df['close'] = (df['morning_price'] + df['evening_price']) / 2
        
        return df
    
    def _calculate_ma(self, df: 'pd.DataFrame') -> 'pd.DataFrame':
        """计算移动平均线"""
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        return df
    
    def _calculate_rsi(self, df: 'pd.DataFrame', period: int = 14) -> 'pd.DataFrame':
        """计算RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
    
    def _calculate_macd(self, df: 'pd.DataFrame') -> 'pd.DataFrame':
        """计算MACD"""
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['histogram'] = df['macd'] - df['signal']
        return df
    
    def _analyze_trend(self, df: 'pd.DataFrame') -> Dict:
        """分析趋势"""
        if len(df) < 20:
            return {"direction": "震荡", "strength": "弱"}
        
        latest = df.iloc[-1]
        ma5 = latest.get('ma5', 0)
        ma20 = latest.get('ma20', 0)
        
        if ma5 > ma20 * 1.02:
            direction = "上涨"
            strength = "强" if ma5 > ma20 * 1.05 else "中"
        elif ma5 < ma20 * 0.98:
            direction = "下跌"
            strength = "强" if ma5 < ma20 * 0.95 else "中"
        else:
            direction = "震荡"
            strength = "弱"
        
        return {"direction": direction, "strength": strength}
    
    def _calculate_change(self, df: 'pd.DataFrame', days: int) -> Optional[float]:
        """计算涨跌幅"""
        if len(df) < days + 1:
            return None
        
        current = df['close'].iloc[-1]
        past = df['close'].iloc[-days-1]
        
        return (current - past) / past * 100
    
    def _interpret_rsi(self, rsi: float) -> str:
        """解读RSI"""
        if rsi > 70:
            return "超买"
        elif rsi < 30:
            return "超卖"
        elif rsi > 50:
            return "偏多"
        else:
            return "偏空"
    
    def _interpret_macd(self, df: 'pd.DataFrame') -> str:
        """解读MACD"""
        if len(df) < 2:
            return "N/A"
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        macd = latest.get('macd', 0)
        signal = latest.get('signal', 0)
        prev_macd = prev.get('macd', 0)
        prev_signal = prev.get('signal', 0)
        
        if macd > signal and prev_macd <= prev_signal:
            return "金叉向上"
        elif macd < signal and prev_macd >= prev_signal:
            return "死叉向下"
        elif macd > signal:
            return "多头"
        else:
            return "空头"
    
    def _generate_suggestion(self, df: 'pd.DataFrame', trend: Dict) -> str:
        """生成操作建议"""
        if len(df) == 0:
            return "数据不足"
        
        latest = df.iloc[-1]
        rsi = latest.get('rsi', 50)
        
        if rsi > 70:
            return "超买区域，考虑减仓"
        elif rsi < 30:
            return "超卖区域，可小仓位试探"
        elif trend['direction'] == "上涨":
            return "趋势向上，持仓观望"
        elif trend['direction'] == "下跌":
            return "趋势向下，谨慎观望"
        else:
            return "震荡整理，等待方向"


def main():
    """测试"""
    analyzer = GoldAnalyzerEnhancedV2()
    result = analyzer.analyze()
    
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
