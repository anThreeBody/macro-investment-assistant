#!/usr/bin/env python3
"""
金价浏览器抓取模块

使用浏览器访问东方财富等网站获取实时金价
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoldBrowserScraper:
    """金价浏览器抓取器"""
    
    OUNCE_TO_GRAM = 31.1034768
    EXCHANGE_RATE = 7.25
    
    VALID_RANGES = {
        'international': (1800, 5500),  # 扩大范围以容纳期货价格
        'domestic': (450, 1200),
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_eastmoney_snapshot(self, snapshot_text: str) -> Optional[Dict]:
        """
        从东方财富页面snapshot解析金价
        
        从东方财富COMEX黄金页面可以获取：
        - 最新价: 4708.4
        - 昨收: 4813.1
        - 涨跌额: -104.7
        - 涨跌幅: -2.18%
        """
        try:
            # 查找最新价
            price_match = re.search(r'最新[:：]\s*(\d{4,5}\.?\d{0,2})', snapshot_text)
            if not price_match:
                price_match = re.search(r'最新价[:：]\s*(\d{4,5}\.?\d{0,2})', snapshot_text)
            
            if price_match:
                price = float(price_match.group(1))
                
                # 查找昨收
                prev_match = re.search(r'昨收[:：]\s*(\d{4,5}\.?\d{0,2})', snapshot_text)
                prev_price = float(prev_match.group(1)) if prev_match else price
                
                # 计算涨跌
                change = price - prev_price
                change_pct = (change / prev_price * 100) if prev_price else 0
                
                # 查找最高最低
                high_match = re.search(r'最高[:：]\s*(\d{4,5}\.?\d{0,2})', snapshot_text)
                low_match = re.search(r'最低[:：]\s*(\d{4,5}\.?\d{0,2})', snapshot_text)
                
                return {
                    'price': price,
                    'prev_price': prev_price,
                    'change': round(change, 2),
                    'change_pct': round(change_pct, 2),
                    'high': float(high_match.group(1)) if high_match else None,
                    'low': float(low_match.group(1)) if low_match else None,
                    'source': '东方财富-COMEX黄金'
                }
        
        except Exception as e:
            self.logger.warning(f"解析东方财富数据失败: {e}")
        
        return None
    
    def parse_cngold_snapshot(self, snapshot_text: str) -> Optional[Dict]:
        """
        从金投网页面snapshot解析金价
        
        金投网页面结构：
        - 现货黄金: ---- (需要JS加载)
        - 通常显示: 买价、卖价、今开、昨收等
        """
        try:
            # 尝试查找金价数据
            # 格式: "现货黄金\t最新价\t涨跌" 或类似表格
            
            # 查找国内金价（元/克）
            domestic_patterns = [
                r'上海金[^\d]*(\d{3})\s*[\.．]\s*(\d{2})',
                r'国内金价[^\d]*(\d{3})\s*[\.．]\s*(\d{2})',
                r'黄金[^\d]*(\d{3})\s*[\.．]\s*(\d{2})[^元]*元',
            ]
            
            for pattern in domestic_patterns:
                match = re.search(pattern, snapshot_text)
                if match:
                    price = float(f"{match.group(1)}.{match.group(2)}")
                    if self.VALID_RANGES['domestic'][0] <= price <= self.VALID_RANGES['domestic'][1]:
                        return {
                            'price': price,
                            'source': '金投网-国内金价',
                            'is_domestic': True
                        }
            
            # 查找国际金价（美元/盎司）
            international_patterns = [
                r'国际金价[^\d]*(\d{4})\s*[\.．]\s*(\d{2})',
                r'伦敦金[^\d]*(\d{4})\s*[\.．]\s*(\d{2})',
                r'现货黄金[^\d]*(\d{4})\s*[\.．]\s*(\d{2})',
            ]
            
            for pattern in international_patterns:
                match = re.search(pattern, snapshot_text)
                if match:
                    price = float(f"{match.group(1)}.{match.group(2)}")
                    if self.VALID_RANGES['international'][0] <= price <= self.VALID_RANGES['international'][1]:
                        return {
                            'price': price,
                            'source': '金投网-国际金价',
                            'is_domestic': False
                        }
        
        except Exception as e:
            self.logger.warning(f"解析金投网数据失败: {e}")
        
        return None
    
    def convert_futures_to_spot(self, futures_price: float) -> float:
        """
        将期货价格转换为现货价格估算
        
        COMEX黄金期货通常比现货高/低一定幅度
        根据市场情况，期货与现货价差通常在 ±20美元内
        """
        # 简化处理：期货价格直接作为参考
        # 实际应用中应该使用期货-现货价差调整
        return futures_price
    
    def calculate_domestic_price(self, international_price: float) -> float:
        """根据国际金价计算国内金价"""
        domestic = international_price * self.EXCHANGE_RATE / self.OUNCE_TO_GRAM
        return round(domestic, 2)
    
    def validate_price(self, price: float, price_type: str = 'international') -> bool:
        """验证价格合理性"""
        if price_type not in self.VALID_RANGES:
            return False
        min_val, max_val = self.VALID_RANGES[price_type]
        return min_val <= price <= max_val


def extract_gold_from_snapshot(snapshot_file: str) -> Optional[Dict]:
    """
    从snapshot文件提取金价
    
    用于手动分析浏览器抓取的数据
    """
    scraper = GoldBrowserScraper()
    
    try:
        with open(snapshot_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试东方财富格式
        result = scraper.parse_eastmoney_snapshot(content)
        if result:
            return result
        
        # 尝试金投网格式
        result = scraper.parse_cngold_snapshot(content)
        if result:
            return result
        
    except Exception as e:
        logger.error(f"读取snapshot文件失败: {e}")
    
    return None


if __name__ == "__main__":
    # 测试解析
    scraper = GoldBrowserScraper()
    
    # 模拟东方财富数据
    test_text = """
    COMEX黄金 GC00Y（2026-04-02 11:08:55）
    最新：4708.4 昨收：4813.1
    涨幅：-2.18% 涨跌额：-104.7
    最高：4825.9 最低：4675.7
    """
    
    result = scraper.parse_eastmoney_snapshot(test_text)
    if result:
        print(f"✅ 解析成功:")
        print(f"  价格: {result['price']}")
        print(f"  昨收: {result['prev_price']}")
        print(f"  涨跌: {result['change']} ({result['change_pct']}%)")
        print(f"  来源: {result['source']}")
        
        # 计算国内金价
        domestic = scraper.calculate_domestic_price(result['price'])
        print(f"  估算国内金价: ¥{domestic}/g")
    else:
        print("❌ 解析失败")
