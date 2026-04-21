#!/usr/bin/env python3
"""
金价自动获取 V8.2 - 浏览器实时获取版

核心改进:
1. 使用浏览器访问东方财富获取 COMEX 黄金期货价格
2. 实时获取，不使用缓存
3. 获取失败直接报错，不给预估价

数据源：东方财富 COMEX 黄金期货
URL: http://quote.eastmoney.com/unify/r/101.GC00Y
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoldPriceAutoFetcherV82:
    """金价自动获取器 V8.2 - 东方财富浏览器版"""
    
    # 换算常数
    OUNCE_TO_GRAM = 31.1034768
    EXCHANGE_RATE = 7.25
    
    # 价格合理性范围
    VALID_RANGES = {
        'international': (1800, 5500),
        'domestic': (450, 1200),
    }
    
    def __init__(self):
        self.data_file = Path(__file__).parent.parent / "data" / "gold_price_cache.json"
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
    
    def fetch_from_eastmoney(self) -> Optional[Dict]:
        """
        从东方财富获取 COMEX 黄金期货价格
        URL: http://quote.eastmoney.com/unify/r/101.GC00Y
        """
        logger.info("从东方财富获取 COMEX 黄金价格...")
        
        try:
            # 使用 playwright 获取页面
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # 访问东方财富
                page.goto("http://quote.eastmoney.com/unify/r/101.GC00Y", timeout=30000)
                page.wait_for_timeout(5000)  # 等待数据加载
                
                # 获取页面文本
                content = page.evaluate("document.body.innerText")
                browser.close()
                
                # 解析价格
                return self.parse_eastmoney_content(content)
        
        except ImportError:
            logger.error("playwright 未安装，请运行：pip install playwright && playwright install chromium")
            return None
        
        except Exception as e:
            logger.error(f"东方财富获取失败：{e}")
            return None
    
    def parse_eastmoney_content(self, content: str) -> Optional[Dict]:
        """解析东方财富页面内容"""
        try:
            # 查找最新价
            price_match = re.search(r'(\d{4,5})[\.．](\d)\s*[-+]?\d*\s*[-+]?\d+\.?\d*%', content)
            if not price_match:
                price_match = re.search(r'COMEX 黄金[^\d]*(\d{4,5})[\.．](\d)', content)
            
            if not price_match:
                return None
            
            price = float(f"{price_match.group(1)}.{price_match.group(1)}")
            
            # 查找昨收
            prev_match = re.search(r'昨 [收结][:：]\s*(\d{4,5})[\.．](\d)', content)
            prev_price = float(f"{prev_match.group(1)}.{prev_match.group(2)}") if prev_match else price
            
            # 计算涨跌
            change = price - prev_price
            change_pct = (change / prev_price * 100) if prev_price else 0
            
            # 计算国内金价
            domestic = price * self.EXCHANGE_RATE / self.OUNCE_TO_GRAM
            
            return {
                'international_usd_per_oz': round(price, 2),
                'domestic_cny_per_gram': round(domestic, 2),
                'change_usd': round(change, 2),
                'change_pct': round(change_pct, 2),
                'prev_price': prev_price,
                'source': '东方财富-COMEX 黄金期货',
                'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        except Exception as e:
            logger.error(f"解析失败：{e}")
            return None
    
    def validate_price(self, price: float, price_type: str = 'international') -> bool:
        """验证价格合理性"""
        if price_type not in self.VALID_RANGES:
            return False
        min_val, max_val = self.VALID_RANGES[price_type]
        return min_val <= price <= max_val
    
    def fetch(self) -> Dict:
        """
        获取金价（主方法）
        
        Returns:
            Dict: 金价数据
        
        Raises:
            Exception: 获取失败时抛出异常
        """
        logger.info("开始获取金价...")
        
        # 尝试获取
        data = self.fetch_from_eastmoney()
        
        if not data:
            error_msg = """
╔══════════════════════════════════════════════════════════════════╗
║                    ❌ 无法获取实时金价数据                       ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  可能原因：                                                      ║
║  1. 网络连接问题                                                 ║
║  2. 浏览器启动失败                                               ║
║  3. 东方财富网站无法访问                                         ║
║                                                                  ║
║  解决方案：                                                      ║
║  1. 检查网络连接                                                 ║
║  2. 安装 playwright: pip install playwright                      ║
║  3. 安装浏览器：playwright install chromium                      ║
║  4. 手动查看：http://quote.eastmoney.com/unify/r/101.GC00Y      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
            logger.error(error_msg)
            raise Exception("无法获取金价数据")
        
        # 验证价格
        if not self.validate_price(data['international_usd_per_oz'], 'international'):
            raise Exception(f"价格超出合理区间：{data['international_usd_per_oz']}")
        
        if not self.validate_price(data['domestic_cny_per_gram'], 'domestic'):
            raise Exception(f"国内金价超出合理区间：{data['domestic_cny_per_gram']}")
        
        logger.info(f"获取成功：国际${data['international_usd_per_oz']}/oz, 国内¥{data['domestic_cny_per_gram']}/g")
        
        return data
    
    def save(self, data: Dict):
        """保存到缓存文件"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"数据已保存：{self.data_file}")


def main():
    """主函数"""
    print("="*70)
    print("📈 金价自动获取 V8.2")
    print("="*70)
    print()
    
    fetcher = GoldPriceAutoFetcherV82()
    
    try:
        data = fetcher.fetch()
        
        print("✅ 获取成功!")
        print()
        print(f"国际金价：${data['international_usd_per_oz']:.2f}/oz")
        print(f"涨跌额：{data['change_usd']:+.2f}")
        print(f"涨跌幅：{data['change_pct']:+.2f}%")
        print(f"国内金价：¥{data['domestic_cny_per_gram']:.2f}/g")
        print()
        print(f"数据来源：{data['source']}")
        print(f"更新时间：{data['update_time']}")
        print()
        
        # 保存数据
        fetcher.save(data)
        
        print("="*70)
        return 0
        
    except Exception as e:
        print("❌ 获取失败!")
        print()
        print(f"错误：{e}")
        print()
        print("="*70)
        return 1


if __name__ == "__main__":
    exit(main())
