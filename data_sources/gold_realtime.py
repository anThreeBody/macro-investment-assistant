#!/usr/bin/env python3
"""
金价实时获取模块

原则：
1. 每次执行都实时获取最新价格
2. 获取不到就报错，不给预估价
3. 统一使用浏览器搜索 + 百度搜索获取实时金价
"""

import logging
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoldPriceRealtime:
    """金价实时获取器"""
    
    # 换算常数
    OUNCE_TO_GRAM = 31.1034768
    
    # 价格合理性范围
    VALID_RANGES = {
        'international': (1800, 3000),  # 美元/盎司
        'domestic': (450, 800),         # 元/克
    }
    
    def __init__(self):
        self.exchange_rate = 7.25
        logger.info("[金价实时] 初始化完成")
    
    def fetch_from_baidu_search(self) -> Optional[Tuple[float, float]]:
        """
        从百度搜索获取金价
        
        搜索关键词：今日金价、国际金价
        """
        try:
            logger.info("[金价实时] 从百度搜索获取金价...")
            
            # 百度搜索今日金价
            search_url = "https://www.baidu.com/s?wd=今日金价+黄金+价格"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                html = response.text
                
                # 查找国内金价（元/克）
                # 百度通常显示：黄金价格 xxx元/克
                domestic_pattern = r'黄金价格[^\d]*(\d{3})[^\d]*(\d{2})[^元]*元/克'
                domestic_match = re.search(domestic_pattern, html)
                
                domestic_price = None
                if domestic_match:
                    # 提取价格，如 "548" + "23" = 548.23
                    domestic_price = float(f"{domestic_match.group(1)}.{domestic_match.group(2)}")
                    logger.info(f"[金价实时] 百度搜索到国内金价: ¥{domestic_price}/g")
                
                # 查找国际金价（美元/盎司）
                # 百度通常显示：国际金价 xxx美元/盎司
                international_pattern = r'国际金价[^\d]*(\d{4})[^\d]*(\d{2})[^美]*美元/盎司'
                international_match = re.search(international_pattern, html)
                
                international_price = None
                if international_match:
                    international_price = float(f"{international_match.group(1)}.{international_match.group(2)}")
                    logger.info(f"[金价实时] 百度搜索到国际金价: ${international_price}/oz")
                
                if domestic_price or international_price:
                    return international_price, domestic_price
        
        except Exception as e:
            logger.warning(f"[金价实时] 百度搜索失败: {e}")
        
        return None
    
    def fetch_from_sina_finance(self) -> Optional[Tuple[float, float]]:
        """从新浪财经获取金价"""
        try:
            logger.info("[金价实时] 从新浪财经获取金价...")
            
            # 新浪财经黄金行情
            url = "https://finance.sina.com.cn/money/gold/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                html = response.text
                
                # 查找国内金价
                domestic_pattern = r'上海金[^\d]*(\d{3})\.(\d{2})'
                domestic_match = re.search(domestic_pattern, html)
                
                domestic_price = None
                if domestic_match:
                    domestic_price = float(f"{domestic_match.group(1)}.{domestic_match.group(2)}")
                    logger.info(f"[金价实时] 新浪财经国内金价: ¥{domestic_price}/g")
                
                # 查找国际金价
                international_pattern = r'伦敦金[^\d]*(\d{4})\.(\d{2})'
                international_match = re.search(international_pattern, html)
                
                international_price = None
                if international_match:
                    international_price = float(f"{international_match.group(1)}.{international_match.group(2)}")
                    logger.info(f"[金价实时] 新浪财经国际金价: ${international_price}/oz")
                
                if domestic_price or international_price:
                    return international_price, domestic_price
        
        except Exception as e:
            logger.warning(f"[金价实时] 新浪财经获取失败: {e}")
        
        return None
    
    def fetch_from_gold_price_org(self) -> Optional[float]:
        """从GoldPrice.org获取国际金价"""
        try:
            logger.info("[金价实时] 从GoldPrice.org获取国际金价...")
            
            url = "https://data-asg.goldprice.io/dbXRates/USD"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'items' in data:
                    for item in data['items']:
                        if item.get('curr') == 'XAU':
                            price = float(item.get('xauPrice', 0))
                            if self.VALID_RANGES['international'][0] <= price <= self.VALID_RANGES['international'][1]:
                                logger.info(f"[金价实时] GoldPrice.org国际金价: ${price}/oz")
                                return price
        
        except Exception as e:
            logger.warning(f"[金价实时] GoldPrice.org获取失败: {e}")
        
        return None
    
    def validate_price(self, price: float, price_type: str) -> bool:
        """验证价格合理性"""
        if price_type not in self.VALID_RANGES:
            return False
        
        min_val, max_val = self.VALID_RANGES[price_type]
        return min_val <= price <= max_val
    
    def calculate_missing_price(self, international: Optional[float], domestic: Optional[float]) -> Tuple[float, float]:
        """
        根据已有价格计算缺失的价格
        
        公式：
        国际金价(美元/盎司) = 国内金价(元/克) × 31.1035 ÷ 汇率
        国内金价(元/克) = 国际金价(美元/盎司) × 汇率 ÷ 31.1035
        """
        if international and not domestic:
            # 有国际金价，计算国内金价
            domestic = international * self.exchange_rate / self.OUNCE_TO_GRAM
            domestic = round(domestic, 2)
            logger.info(f"[金价实时] 计算国内金价: ¥{domestic}/g")
        
        elif domestic and not international:
            # 有国内金价，计算国际金价
            international = domestic * self.OUNCE_TO_GRAM / self.exchange_rate
            international = round(international, 2)
            logger.info(f"[金价实时] 计算国际金价: ${international}/oz")
        
        return international or 0, domestic or 0
    
    def get_gold_price(self) -> Dict:
        """
        获取实时金价
        
        策略：
        1. 尝试多个数据源
        2. 验证价格合理性
        3. 计算缺失的价格
        4. 如果都失败，抛出异常
        """
        logger.info("[金价实时] 开始获取实时金价...")
        
        international_price = None
        domestic_price = None
        sources_used = []
        errors = []
        
        # 1. 尝试百度搜索
        try:
            result = self.fetch_from_baidu_search()
            if result:
                international_price, domestic_price = result
                sources_used.append('百度搜索')
        except Exception as e:
            errors.append(f"百度搜索: {e}")
        
        # 2. 尝试新浪财经
        if not domestic_price:
            try:
                result = self.fetch_from_sina_finance()
                if result:
                    intl, dom = result
                    if intl:
                        international_price = intl
                    if dom:
                        domestic_price = dom
                    sources_used.append('新浪财经')
            except Exception as e:
                errors.append(f"新浪财经: {e}")
        
        # 3. 尝试GoldPrice.org（国际金价）
        if not international_price:
            try:
                price = self.fetch_from_gold_price_org()
                if price:
                    international_price = price
                    sources_used.append('GoldPrice.org')
            except Exception as e:
                errors.append(f"GoldPrice.org: {e}")
        
        # 4. 计算缺失的价格
        if international_price or domestic_price:
            international_price, domestic_price = self.calculate_missing_price(
                international_price, domestic_price
            )
        
        # 5. 验证价格
        if international_price and not self.validate_price(international_price, 'international'):
            logger.error(f"[金价实时] 国际金价 {international_price} 超出合理区间")
            international_price = None
        
        if domestic_price and not self.validate_price(domestic_price, 'domestic'):
            logger.error(f"[金价实时] 国内金价 {domestic_price} 超出合理区间")
            domestic_price = None
        
        # 6. 检查是否获取成功
        if not international_price or not domestic_price:
            error_msg = "无法获取实时金价数据\n"
            error_msg += f"尝试的数据源: {', '.join(sources_used) if sources_used else '无'}\n"
            error_msg += f"错误信息: {'; '.join(errors) if errors else '未知错误'}\n"
            error_msg += "\n建议:\n"
            error_msg += "1. 检查网络连接\n"
            error_msg += "2. 稍后重试\n"
            error_msg += "3. 手动查看金价网站确认行情"
            
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # 7. 返回结果
        return {
            'international': {
                'price': international_price,
                'unit': 'USD/oz',
                'change': 0.0,
                'change_pct': 0.0
            },
            'domestic': {
                'price': domestic_price,
                'unit': 'CNY/g',
                'change': 0.0,
                'change_pct': 0.0
            },
            'metadata': {
                'sources': sources_used,
                'timestamp': datetime.now().isoformat(),
                'exchange_rate': self.exchange_rate,
                'method': 'realtime'
            }
        }


def test_realtime_gold():
    """测试实时金价获取"""
    print("="*70)
    print("🌐 实时金价获取测试")
    print("="*70)
    
    fetcher = GoldPriceRealtime()
    
    try:
        print("\n1️⃣ 获取实时金价...")
        data = fetcher.get_gold_price()
        
        print("\n2️⃣ 结果:")
        print(f"  国际金价: ${data['international']['price']:.2f} {data['international']['unit']}")
        print(f"  国内金价: ¥{data['domestic']['price']:.2f} {data['domestic']['unit']}")
        print(f"  数据来源: {', '.join(data['metadata']['sources'])}")
        print(f"  更新时间: {data['metadata']['timestamp']}")
        
        print("\n3️⃣ 验证:")
        if fetcher.validate_price(data['international']['price'], 'international'):
            print(f"  ✅ 国际金价合理")
        else:
            print(f"  ❌ 国际金价异常")
        
        if fetcher.validate_price(data['domestic']['price'], 'domestic'):
            print(f"  ✅ 国内金价合理")
        else:
            print(f"  ❌ 国内金价异常")
        
        print("\n" + "="*70)
        print("✅ 实时金价获取成功!")
        print("="*70)
        
        return data
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ 实时金价获取失败!")
        print("="*70)
        print(f"\n错误: {e}")
        return None


if __name__ == "__main__":
    test_realtime_gold()
