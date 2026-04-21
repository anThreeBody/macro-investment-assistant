#!/usr/bin/env python3
"""
金价获取 - 百度搜索方式

使用 baidu-search skill 获取实时金价
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


class GoldPriceBaiduSearch:
    """通过百度搜索获取金价"""
    
    OUNCE_TO_GRAM = 31.1034768
    EXCHANGE_RATE = 7.25
    
    VALID_RANGES = {
        'international': (1800, 5500),  # 扩大范围以容纳期货价格
        'domestic': (450, 1200),
    }
    
    def __init__(self):
        # 使用 baidu-search skill 的脚本
        self.script_dir = Path(__file__).parent.parent.parent.parent / "skills" / "baidu-search" / "scripts"
        self.search_script = self.script_dir / "search"
        
        if not self.search_script.exists():
            logger.error(f"搜索脚本不存在：{self.search_script}")
            raise FileNotFoundError(f"搜索脚本不存在：{self.search_script}")
        
        logger.info(f"[金价搜索] 初始化完成，脚本路径：{self.search_script}")
    
    def search(self, query: str, count: int = 10) -> list:
        """执行百度搜索"""
        try:
            cmd = [
                str(self.search_script),
                query,
                "--count", str(count),
                "--engine", "baidu"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('results', [])
            else:
                logger.error(f"搜索失败：{result.stderr}")
                return []
        
        except Exception as e:
            logger.error(f"搜索异常：{e}")
            return []
    
    def extract_price_from_text(self, text: str) -> Optional[Tuple[float, str]]:
        """
        从文本中提取金价
        
        返回：(价格，来源类型)
        """
        import re
        
        # 国际金价模式（美元/盎司）
        intl_patterns = [
            r'国际金价[^\d]*(\d{4,5})[^\d]*(\d{1,2})',  # 国际金价 4708.4
            r'现货黄金[^\d]*(\d{4,5})[^\d]*(\d{1,2})',  # 现货黄金 4708.4
            r'伦敦金[^\d]*(\d{4,5})[^\d]*(\d{1,2})',    # 伦敦金 4708.4
            r'COMEX 黄金[^\d]*(\d{4,5})[^\d]*(\d{1,2})', # COMEX 黄金 4708.4
            r'(\d{4,5})[\.．](\d{1,2})\s*美元\s*/\s*盎司',  # 4708.4 美元/盎司
        ]
        
        for pattern in intl_patterns:
            match = re.search(pattern, text)
            if match:
                price = float(f"{match.group(1)}.{match.group(2)}")
                if self.VALID_RANGES['international'][0] <= price <= self.VALID_RANGES['international'][1]:
                    return (price, 'international')
        
        # 国内金价模式（元/克）
        domestic_patterns = [
            r'国内金价[^\d]*(\d{3})[^\d]*(\d{1,2})',  # 国内金价 548.23
            r'上海金[^\d]*(\d{3})[^\d]*(\d{1,2})',    # 上海金 548.23
            r'黄金价格[^\d]*(\d{3})[^\d]*(\d{1,2})[^元]*元',  # 黄金价格 548.23 元
            r'(\d{3})[\.．](\d{1,2})\s*元\s*/\s*克',  # 548.23 元/克
        ]
        
        for pattern in domestic_patterns:
            match = re.search(pattern, text)
            if match:
                price = float(f"{match.group(1)}.{match.group(2)}")
                if self.VALID_RANGES['domestic'][0] <= price <= self.VALID_RANGES['domestic'][1]:
                    return (price, 'domestic')
        
        return None
    
    def fetch_url_content(self, url: str) -> Optional[str]:
        """抓取 URL 内容"""
        try:
            fetch_script = self.script_dir / "fetch.py"
            if not fetch_script.exists():
                # 尝试另一个路径
                fetch_script = self.script_dir.parent / "baidu-search" / "scripts" / "fetch.py"
            
            if not fetch_script.exists():
                logger.warning("fetch.py 不存在，跳过 URL 抓取")
                return None
            
            cmd = [
                "python3",
                str(fetch_script),
                url,
                "--max-chars", "10000"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('text', '')
            else:
                logger.warning(f"抓取失败：{result.stderr}")
                return None
        
        except Exception as e:
            logger.warning(f"抓取异常：{e}")
            return None
    
    def get_price(self) -> Dict:
        """
        获取实时金价
        
        策略：
        1. 搜索"今日金价"
        2. 从搜索结果中提取价格
        3. 如果搜索结果不够，抓取网页详情
        4. 验证价格合理性
        """
        logger.info("[金价搜索] 开始搜索金价...")
        
        # 搜索关键词
        search_queries = [
            "今日金价 黄金价格 2026",
            "国际金价 现货黄金 实时",
            "上海黄金交易所 金价",
        ]
        
        international_price = None
        domestic_price = None
        sources = []
        
        for query in search_queries:
            logger.info(f"[金价搜索] 搜索：{query}")
            results = self.search(query, count=10)
            
            if not results:
                continue
            
            # 从搜索结果摘要提取
            for result in results:
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                url = result.get('url', '')
                
                # 合并标题和摘要
                text = f"{title} {snippet}"
                
                # 提取价格
                extracted = self.extract_price_from_text(text)
                if extracted:
                    price, price_type = extracted
                    if price_type == 'international' and not international_price:
                        international_price = price
                        sources.append(f"国际金价：{url}")
                        logger.info(f"[金价搜索] 提取到国际金价：${price}/oz")
                    elif price_type == 'domestic' and not domestic_price:
                        domestic_price = price
                        sources.append(f"国内金价：{url}")
                        logger.info(f"[金价搜索] 提取到国内金价：¥{price}/g")
                
                # 如果都获取到了，跳出循环
                if international_price and domestic_price:
                    break
            
            # 如果都获取到了，跳出查询循环
            if international_price and domestic_price:
                break
        
        # 如果只获取到一个，计算另一个
        if international_price and not domestic_price:
            domestic_price = international_price * self.EXCHANGE_RATE / self.OUNCE_TO_GRAM
            domestic_price = round(domestic_price, 2)
            logger.info(f"[金价搜索] 计算国内金价：¥{domestic_price}/g")
        
        elif domestic_price and not international_price:
            international_price = domestic_price * self.OUNCE_TO_GRAM / self.EXCHANGE_RATE
            international_price = round(international_price, 2)
            logger.info(f"[金价搜索] 计算国际金价：${international_price}/oz")
        
        # 验证结果
        if not international_price or not domestic_price:
            error_msg = """
╔══════════════════════════════════════════════════════════════════╗
║                    ⚠️  无法从百度搜索获取金价数据                ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  可能原因：                                                      ║
║  1. 网络连接问题                                                 ║
║  2. 百度搜索反爬限制                                             ║
║  3. 搜索结果中没有金价信息                                       ║
║                                                                  ║
║  建议：                                                          ║
║  1. 稍后重试                                                     ║
║  2. 手动查看金价网站：                                           ║
║     - 金投网：https://www.cngold.org                            ║
║     - 东方财富：http://quote.eastmoney.com/unify/r/101.GC00Y   ║
║  3. 使用环境变量配置：                                           ║
║     export GOLD_PRICE_INTL=2350                                  ║
║     export GOLD_PRICE_DOMESTIC=548                               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # 返回结果
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
                'sources_detail': sources,
                'timestamp': datetime.now().isoformat(),
                'exchange_rate': self.EXCHANGE_RATE,
                'method': 'baidu_search'
            }
        }


def test_baidu_search():
    """测试百度搜索获取金价"""
    print("="*70)
    print("🔍 百度搜索金价测试")
    print("="*70)
    
    try:
        fetcher = GoldPriceBaiduSearch()
        data = fetcher.get_price()
        
        print("\n" + "="*70)
        print("✅ 获取成功!")
        print("="*70)
        print(f"\n国际金价: ${data['international']['price']:.2f} {data['international']['unit']}")
        print(f"国内金价: ¥{data['domestic']['price']:.2f} {data['domestic']['unit']}")
        print(f"\n数据来源:")
        for source in data['metadata']['sources_detail']:
            print(f"  - {source}")
        print(f"\n更新时间: {data['metadata']['timestamp']}")
        
        return data
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ 获取失败!")
        print("="*70)
        print(f"\n错误: {e}")
        return None


if __name__ == "__main__":
    test_baidu_search()
