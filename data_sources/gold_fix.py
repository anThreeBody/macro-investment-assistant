#!/usr/bin/env python3
"""
金价数据修复模块
解决数据源失效、价格错误、缓存不更新等问题
"""

import logging
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoldPriceFix:
    """金价数据修复器"""
    
    # 正确的换算系数
    # 1 盎司 = 31.1035 克
    # 国际金价(美元/盎司) = 国内金价(元/克) × 汇率 ÷ 31.1035
    # 国内金价(元/克) = 国际金价(美元/盎司) × 汇率 ÷ 31.1035
    OUNCE_TO_GRAM = 31.1035
    
    # 正常价格区间 (2024-2026年)
    VALID_RANGES = {
        'international': (1800, 3000),  # 美元/盎司
        'domestic': (500, 800),         # 元/克
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            cache_dir = str(Path(__file__).parent.parent / "data" / "cache")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 汇率缓存
        self.exchange_rate = 7.2  # 默认汇率
        
        logger.info("[金价修复] 初始化完成")
    
    def fetch_from_sina(self) -> Optional[Dict]:
        """从新浪财经获取金价"""
        try:
            # 新浪财经黄金现货
            url = "https://hq.sinajs.cn/list=hf_GC"
            headers = {
                'Referer': 'https://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # 解析返回数据
                # var hq_str_hf_GC="2345.6,...
                text = response.text
                if 'hq_str_hf_GC=' in text:
                    data_str = text.split('"')[1]
                    parts = data_str.split(',')
                    if len(parts) >= 1:
                        price = float(parts[0])
                        if self.VALID_RANGES['international'][0] <= price <= self.VALID_RANGES['international'][1]:
                            return {
                                'price': price,
                                'source': '新浪财经',
                                'timestamp': datetime.now().isoformat()
                            }
        except Exception as e:
            logger.warning(f"[金价修复] 新浪财经获取失败: {e}")
        return None
    
    def fetch_from_shfe(self) -> Optional[Dict]:
        """从上海期货交易所获取金价（期货价格，需要折算）"""
        try:
            # 上海期货交易所黄金主力合约
            url = "http://www.shfe.com.cn/data/dailydata/kx/kx20260401.dat"
            # 注意：这是期货价格，通常比现货高，需要折价
            # 期货价格 - 现货价格 = 持有成本（利息 + 仓储）
            # 一般折价 2-5%
            
            # 由于期货价格不能直接用作现货，这里返回None
            # 实际使用时需要折算
            logger.info("[金价修复] 期货价格需要折算，暂不使用")
            return None
        except Exception as e:
            logger.warning(f"[金价修复] 上期所获取失败: {e}")
        return None
    
    def fetch_from_investing(self) -> Optional[Dict]:
        """从Investing.com获取金价"""
        try:
            # Investing.com API
            url = "https://api.investing.com/api/financialdata/8830"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'last' in data:
                    price = float(data['last'])
                    if self.VALID_RANGES['international'][0] <= price <= self.VALID_RANGES['international'][1]:
                        return {
                            'price': price,
                            'source': 'Investing.com API',
                            'timestamp': datetime.now().isoformat()
                        }
        except Exception as e:
            logger.warning(f"[金价修复] Investing.com获取失败: {e}")
        return None
    
    def fetch_from_yahoo(self) -> Optional[Dict]:
        """从Yahoo Finance获取金价"""
        try:
            # Yahoo Finance API for Gold Futures
            url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    if 'meta' in result and 'regularMarketPrice' in result['meta']:
                        price = float(result['meta']['regularMarketPrice'])
                        if self.VALID_RANGES['international'][0] <= price <= self.VALID_RANGES['international'][1]:
                            return {
                                'price': price,
                                'source': 'Yahoo Finance',
                                'timestamp': datetime.now().isoformat()
                            }
        except Exception as e:
            logger.warning(f"[金价修复] Yahoo Finance获取失败: {e}")
        return None
    
    def fetch_from_goldprice(self) -> Optional[Dict]:
        """从GoldPrice.org获取金价"""
        try:
            url = "https://data-asg.goldprice.io/dbXRates/USD"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and len(data['items']) > 0:
                    # 找到XAU/USD
                    for item in data['items']:
                        if item.get('curr') == 'XAU':
                            price = float(item.get('xauPrice', 0))
                            if self.VALID_RANGES['international'][0] <= price <= self.VALID_RANGES['international'][1]:
                                return {
                                    'price': price,
                                    'source': 'GoldPrice.org',
                                    'timestamp': datetime.now().isoformat()
                                }
        except Exception as e:
            logger.warning(f"[金价修复] GoldPrice.org获取失败: {e}")
        return None
    
    def calculate_domestic_price(self, international_price: float, exchange_rate: float = 7.2) -> float:
        """
        根据国际金价计算国内金价
        
        公式：国内金价(元/克) = 国际金价(美元/盎司) × 汇率 ÷ 31.1035
        """
        domestic = international_price * exchange_rate / self.OUNCE_TO_GRAM
        return round(domestic, 2)
    
    def calculate_international_price(self, domestic_price: float, exchange_rate: float = 7.2) -> float:
        """
        根据国内金价计算国际金价
        
        公式：国际金价(美元/盎司) = 国内金价(元/克) × 31.1035 ÷ 汇率
        """
        international = domestic_price * self.OUNCE_TO_GRAM / exchange_rate
        return round(international, 2)
    
    def validate_price(self, price: float, price_type: str) -> bool:
        """验证价格是否在合理区间"""
        if price_type not in self.VALID_RANGES:
            return False
        
        min_val, max_val = self.VALID_RANGES[price_type]
        return min_val <= price <= max_val
    
    def get_correct_gold_price(self) -> Dict:
        """
        获取正确的金价数据
        
        策略：
        1. 尝试多个数据源
        2. 验证价格合理性
        3. 国际和国内价格互相校验
        4. 返回最可靠的数据
        """
        logger.info("[金价修复] 开始获取正确金价数据...")
        
        # 尝试获取国际金价
        international_sources = [
            self.fetch_from_yahoo,
            self.fetch_from_goldprice,
            self.fetch_from_sina,
            self.fetch_from_investing,
        ]
        
        international_price = None
        international_source = None
        
        for source_func in international_sources:
            result = source_func()
            if result and self.validate_price(result['price'], 'international'):
                international_price = result['price']
                international_source = result['source']
                logger.info(f"[金价修复] 获取国际金价: ${international_price} ({international_source})")
                break
        
        # 如果获取到国际金价，计算国内金价
        if international_price:
            domestic_price = self.calculate_domestic_price(international_price)
            
            # 验证计算出的国内金价
            if self.validate_price(domestic_price, 'domestic'):
                return {
                    'international': {
                        'price': international_price,
                        'change': 0.0,
                        'change_pct': 0.0,
                        'unit': 'USD/oz'
                    },
                    'domestic': {
                        'price': domestic_price,
                        'change': 0.0,
                        'change_pct': 0.0,
                        'unit': 'CNY/g'
                    },
                    'metadata': {
                        'source': international_source,
                        'timestamp': datetime.now().isoformat(),
                        'exchange_rate': self.exchange_rate,
                        'method': 'calculated'
                    }
                }
        
        # 如果都失败了，使用兜底数据（但明确标记）
        logger.warning("[金价修复] 所有数据源失败，使用兜底数据")
        return {
            'international': {
                'price': 2350.0,  # 2024-2025年合理价格
                'change': 0.0,
                'change_pct': 0.0,
                'unit': 'USD/oz'
            },
            'domestic': {
                'price': self.calculate_domestic_price(2350.0),
                'change': 0.0,
                'change_pct': 0.0,
                'unit': 'CNY/g'
            },
            'metadata': {
                'source': '兜底数据',
                'timestamp': datetime.now().isoformat(),
                'exchange_rate': self.exchange_rate,
                'method': 'fallback',
                'warning': '数据可能不是实时数据，仅供参考'
            }
        }
    
    def clear_cache(self):
        """清理缓存"""
        try:
            cache_files = list(self.cache_dir.glob("gold_*.json"))
            for f in cache_files:
                f.unlink()
                logger.info(f"[金价修复] 清理缓存: {f}")
        except Exception as e:
            logger.warning(f"[金价修复] 清理缓存失败: {e}")
    
    def save_to_cache(self, data: Dict):
        """保存到缓存"""
        try:
            cache_file = self.cache_dir / f"gold_fixed_{datetime.now().strftime('%Y%m%d')}.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"[金价修复] 保存缓存: {cache_file}")
        except Exception as e:
            logger.warning(f"[金价修复] 保存缓存失败: {e}")


def test_gold_fix():
    """测试金价修复"""
    print("="*70)
    print("🛠️ 金价数据修复测试")
    print("="*70)
    
    fix = GoldPriceFix()
    
    # 清理旧缓存
    print("\n1️⃣ 清理旧缓存...")
    fix.clear_cache()
    
    # 获取正确金价
    print("\n2️⃣ 获取正确金价...")
    data = fix.get_correct_gold_price()
    
    print("\n3️⃣ 验证结果:")
    print(f"  国际金价: ${data['international']['price']:.2f}/oz")
    print(f"  国内金价: ¥{data['domestic']['price']:.2f}/g")
    print(f"  数据来源: {data['metadata']['source']}")
    print(f"  汇率: {data['metadata']['exchange_rate']}")
    print(f"  更新时间: {data['metadata']['timestamp']}")
    
    # 验证价格合理性
    print("\n4️⃣ 价格合理性检查:")
    intl_price = data['international']['price']
    dom_price = data['domestic']['price']
    
    if fix.validate_price(intl_price, 'international'):
        print(f"  ✅ 国际金价 ${intl_price:.2f} 在合理区间 (1800-3000)")
    else:
        print(f"  ❌ 国际金价 ${intl_price:.2f} 超出合理区间")
    
    if fix.validate_price(dom_price, 'domestic'):
        print(f"  ✅ 国内金价 ¥{dom_price:.2f} 在合理区间 (500-800)")
    else:
        print(f"  ❌ 国内金价 ¥{dom_price:.2f} 超出合理区间")
    
    # 保存到缓存
    print("\n5️⃣ 保存到缓存...")
    fix.save_to_cache(data)
    
    print("\n" + "="*70)
    print("✅ 金价数据修复测试完成!")
    print("="*70)
    
    return data


if __name__ == "__main__":
    test_gold_fix()
