#!/usr/bin/env python3
"""
金价获取 - 浏览器方式

使用 browser_use 访问东方财富获取实时金价
"""

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoldPriceBrowser:
    """通过浏览器获取金价"""
    
    OUNCE_TO_GRAM = 31.1034768
    EXCHANGE_RATE = 7.25
    
    VALID_RANGES = {
        'international': (1800, 5500),
        'domestic': (450, 1200),
    }
    
    # 东方财富 COMEX 黄金页面
    EASTMONEY_URL = "http://quote.eastmoney.com/unify/r/101.GC00Y"
    
    def __init__(self):
        logger.info("[金价浏览器] 初始化完成")
    
    def fetch_with_browser(self) -> Optional[Dict]:
        """
        使用 browser_use 获取金价
        
        返回：
        {
            'price': float,  # 最新价
            'prev_price': float,  # 昨收
            'change': float,  # 涨跌额
            'change_pct': float,  # 涨跌幅
            'high': float,  # 最高
            'low': float,  # 最低
            'volume': str,  # 成交量
            'timestamp': str,  # 时间戳
        }
        """
        try:
            # 使用 browser_use 打开页面并获取内容
            from browser_use import Agent, Browser
            
            browser = Browser()
            
            # 打开页面
            page = browser.new_page()
            page.goto(self.EASTMONEY_URL)
            page.wait_for_timeout(5000)  # 等待 5 秒让数据加载
            
            # 获取页面文本
            content = page.evaluate("document.body.innerText")
            
            # 解析价格
            data = self.parse_eastmoney_content(content)
            
            browser.close()
            
            return data
        
        except ImportError:
            logger.warning("browser_use 未安装，尝试使用 subprocess 调用")
            return self.fetch_with_subprocess()
        
        except Exception as e:
            logger.error(f"浏览器获取失败：{e}")
            return None
    
    def fetch_with_subprocess(self) -> Optional[Dict]:
        """
        使用 subprocess 调用 browser_use 获取金价
        
        这是一个简化的实现，实际应该使用完整的 browser_use 流程
        """
        try:
            # 创建一个临时的 browser_use 脚本
            script = f"""
import asyncio
from playwright.async_api import async_playwright

async def fetch_gold_price():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('{self.EASTMONEY_URL}')
        await page.wait_for_timeout(5000)
        content = await page.evaluate('document.body.innerText')
        await browser.close()
        print(content)

asyncio.run(fetch_gold_price())
"""
            result = subprocess.run(
                ["python3", "-c", script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return self.parse_eastmoney_content(result.stdout)
            else:
                logger.error(f"subprocess 失败：{result.stderr}")
                return None
        
        except Exception as e:
            logger.error(f"subprocess 异常：{e}")
            return None
    
    def parse_eastmoney_content(self, content: str) -> Optional[Dict]:
        """
        从东方财富页面内容解析金价
        
        格式示例：
        COMEX 黄金 GC00Y（2026-04-03 05:00:00）
        4702.7
        -110.4 -2.29%
        成交量：18.64 万    今开：4783.0    最高：4825.9
        持仓量：26.59 万    昨结：4813.1    最低：4580.4
        """
        import re
        
        try:
            # 查找最新价（通常在"COMEX 黄金"之后）
            price_match = re.search(r'COMEX 黄金[^\d]*(\d{4,5})[\.．](\d)', content)
            if not price_match:
                # 尝试其他模式
                price_match = re.search(r'(\d{4,5})[\.．](\d)\s*[-+]?\d*\s*[-+]?\d+\.?\d*%', content)
            
            if price_match:
                price = float(f"{price_match.group(1)}.{price_match.group(2)}")
                
                # 查找昨收/昨结
                prev_match = re.search(r'昨 [收结][:：]\s*(\d{4,5})[\.．](\d)', content)
                prev_price = float(f"{prev_match.group(1)}.{prev_match.group(2)}") if prev_match else price
                
                # 查找涨跌额和涨跌幅
                change_match = re.search(r'([-+]?\d+\.?\d*)\s*([-+]?\d+\.?\d*)%', content)
                change = float(change_match.group(1)) if change_match else (price - prev_price)
                change_pct = float(change_match.group(2)) if change_match else ((price - prev_price) / prev_price * 100)
                
                # 查找最高最低
                high_match = re.search(r'最高[:：]\s*(\d{4,5})[\.．](\d)', content)
                low_match = re.search(r'最低[:：]\s*(\d{4,5})[\.．](\d)', content)
                
                # 查找时间戳
                time_match = re.search(r'（(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})）', content)
                
                return {
                    'price': price,
                    'prev_price': prev_price,
                    'change': round(change, 2),
                    'change_pct': round(change_pct, 2),
                    'high': float(f"{high_match.group(1)}.{high_match.group(2)}") if high_match else None,
                    'low': float(f"{low_match.group(1)}.{low_match.group(2)}") if low_match else None,
                    'timestamp': time_match.group(1) if time_match else datetime.now().isoformat(),
                    'source': '东方财富-COMEX 黄金期货'
                }
        
        except Exception as e:
            logger.error(f"解析失败：{e}")
        
        return None
    
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
    
    def get_price(self) -> Dict:
        """获取实时金价"""
        logger.info("[金价浏览器] 开始获取金价...")
        
        # 使用浏览器获取
        data = self.fetch_with_browser()
        
        if not data:
            raise Exception("无法通过浏览器获取金价数据")
        
        # 验证价格
        if not self.validate_price(data['price'], 'international'):
            raise Exception(f"价格超出合理区间：{data['price']}")
        
        # 计算国内金价
        domestic_price = self.calculate_domestic_price(data['price'])
        
        # 返回标准格式
        return {
            'international': {
                'price': data['price'],
                'unit': 'USD/oz',
                'change': data['change'],
                'change_pct': data['change_pct']
            },
            'domestic': {
                'price': domestic_price,
                'unit': 'CNY/g',
                'change': 0.0,
                'change_pct': 0.0
            },
            'metadata': {
                'source': data.get('source', '东方财富'),
                'timestamp': data.get('timestamp', datetime.now().isoformat()),
                'exchange_rate': self.EXCHANGE_RATE,
                'method': 'browser',
                'detail': {
                    'prev_price': data.get('prev_price'),
                    'high': data.get('high'),
                    'low': data.get('low'),
                }
            }
        }


def test_browser_gold():
    """测试浏览器获取金价"""
    print("="*70)
    print("🌐 浏览器金价测试")
    print("="*70)
    
    try:
        fetcher = GoldPriceBrowser()
        data = fetcher.get_price()
        
        print("\n" + "="*70)
        print("✅ 获取成功!")
        print("="*70)
        print(f"\n国际金价: ${data['international']['price']:.2f} {data['international']['unit']}")
        print(f"涨跌额：{data['international']['change']}")
        print(f"涨跌幅：{data['international']['change_pct']}%")
        print(f"\n国内金价：¥{data['domestic']['price']:.2f} {data['domestic']['unit']}")
        print(f"\n数据来源：{data['metadata']['source']}")
        print(f"更新时间：{data['metadata']['timestamp']}")
        
        if data['metadata'].get('detail'):
            detail = data['metadata']['detail']
            print(f"\n详细数据:")
            print(f"  昨收：{detail.get('prev_price')}")
            print(f"  最高：{detail.get('high')}")
            print(f"  最低：{detail.get('low')}")
        
        return data
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ 获取失败!")
        print("="*70)
        print(f"\n错误：{e}")
        return None


if __name__ == "__main__":
    test_browser_gold()
