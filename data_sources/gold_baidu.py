#!/usr/bin/env python3
"""
金价获取 - 百度搜索方式

使用百度搜索获取实时金价
"""

import logging
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
import urllib.request
import urllib.parse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoldPriceBaidu:
    """通过百度搜索获取金价"""
    
    OUNCE_TO_GRAM = 31.1034768
    EXCHANGE_RATE = 7.25
    
    VALID_RANGES = {
        'international': (1800, 3000),
        'domestic': (450, 800),
    }
    
    def search_baidu(self, keyword: str) -> str:
        """执行百度搜索"""
        try:
            encoded_keyword = urllib.parse.quote(keyword)
            url = f"https://www.baidu.com/s?wd={encoded_keyword}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='ignore')
                return html
                
        except Exception as e:
            logger.warning(f"百度搜索失败: {e}")
            return ""
    
    def extract_gold_price(self, html: str) -> Tuple[Optional[float], Optional[float]]:
        """从HTML中提取金价"""
        international_price = None
        domestic_price = None
        
        # 查找国内金价 - 多种模式
        domestic_patterns = [
            r'(\d{3})\s*[\.．]\s*(\d{2})\s*元\s*/\s*克',  # 548.23元/克
            r'国内金价[^\d]*(\d{3})[^\d]*(\d{2})',  # 国内金价 548 23
            r'上海金[^\d]*(\d{3})[^\d]*(\d{2})',  # 上海金 548 23
            r'黄金[^\d]*(\d{3})[^\d]*(\d{2})[^元]*元',  # 黄金 548 23 元
        ]
        
        for pattern in domestic_patterns:
            match = re.search(pattern, html)
            if match:
                try:
                    price = float(f"{match.group(1)}.{match.group(2)}")
                    if self.VALID_RANGES['domestic'][0] <= price <= self.VALID_RANGES['domestic'][1]:
                        domestic_price = price
                        logger.info(f"提取到国内金价: ¥{domestic_price}/g")
                        break
                except:
                    continue
        
        # 查找国际金价 - 多种模式
        international_patterns = [
            r'(\d{4})\s*[\.．]\s*(\d{2})\s*美元\s*/\s*盎司',  # 2345.67美元/盎司
            r'国际金价[^\d]*(\d{4})[^\d]*(\d{2})',  # 国际金价 2345 67
            r'伦敦金[^\d]*(\d{4})[^\d]*(\d{2})',  # 伦敦金 2345 67
            r'COMEX[^\d]*(\d{4})[^\d]*(\d{2})',  # COMEX 2345 67
        ]
        
        for pattern in international_patterns:
            match = re.search(pattern, html)
            if match:
                try:
                    price = float(f"{match.group(1)}.{match.group(2)}")
                    if self.VALID_RANGES['international'][0] <= price <= self.VALID_RANGES['international'][1]:
                        international_price = price
                        logger.info(f"提取到国际金价: ${international_price}/oz")
                        break
                except:
                    continue
        
        return international_price, domestic_price
    
    def calculate_missing(self, international: Optional[float], domestic: Optional[float]) -> Tuple[float, float]:
        """计算缺失的价格"""
        if international and not domestic:
            domestic = international * self.EXCHANGE_RATE / self.OUNCE_TO_GRAM
            domestic = round(domestic, 2)
            logger.info(f"计算国内金价: ¥{domestic}/g")
        elif domestic and not international:
            international = domestic * self.OUNCE_TO_GRAM / self.EXCHANGE_RATE
            international = round(international, 2)
            logger.info(f"计算国际金价: ${international}/oz")
        
        return international or 0, domestic or 0
    
    def get_price(self) -> Dict:
        """获取金价"""
        logger.info("[金价获取] 开始从百度搜索获取金价...")
        
        international_price = None
        domestic_price = None
        search_keywords = [
            "今日金价 黄金",
            "国际金价 伦敦金",
            "上海金交所 黄金价格",
        ]
        
        # 尝试多个搜索关键词
        for keyword in search_keywords:
            logger.info(f"[金价获取] 搜索: {keyword}")
            html = self.search_baidu(keyword)
            
            if html:
                intl, dom = self.extract_gold_price(html)
                if intl:
                    international_price = intl
                if dom:
                    domestic_price = dom
                
                # 如果都获取到了，跳出循环
                if international_price and domestic_price:
                    break
        
        # 计算缺失的价格
        international_price, domestic_price = self.calculate_missing(
            international_price, domestic_price
        )
        
        # 验证结果
        if not international_price or not domestic_price:
            raise Exception(
                "无法从百度搜索获取金价数据\n"
                "建议:\n"
                "1. 检查网络连接\n"
                "2. 稍后重试\n"
                "3. 访问 https://www.cngold.org 查看实时金价"
            )
        
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
                'source': '百度搜索',
                'timestamp': datetime.now().isoformat(),
                'exchange_rate': self.EXCHANGE_RATE,
                'method': 'baidu_search'
            }
        }


def test_baidu_gold():
    """测试百度搜索获取金价"""
    print("="*70)
    print("🔍 百度搜索金价测试")
    print("="*70)
    
    fetcher = GoldPriceBaidu()
    
    try:
        print("\n开始搜索...")
        data = fetcher.get_price()
        
        print("\n" + "="*70)
        print("✅ 获取成功!")
        print("="*70)
        print(f"\n国际金价: ${data['international']['price']:.2f} {data['international']['unit']}")
        print(f"国内金价: ¥{data['domestic']['price']:.2f} {data['domestic']['unit']}")
        print(f"数据来源: {data['metadata']['source']}")
        print(f"更新时间: {data['metadata']['timestamp']}")
        
        return data
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ 获取失败!")
        print("="*70)
        print(f"\n错误: {e}")
        return None


if __name__ == "__main__":
    test_baidu_gold()
