#!/usr/bin/env python3
"""
金价数据修复模块 V2
使用正确的数据源和计算方法
"""

import logging
import json
import requests
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoldPriceFixed:
    """
    金价数据修复器
    
    修复问题：
    1. 数据源失效 - 使用多个可靠数据源
    2. 期货价格误作现货 - 明确区分期货和现货
    3. 计算错误 - 使用正确的换算公式
    4. 缓存不更新 - 强制刷新机制
    """
    
    # 换算常数
    OUNCE_TO_GRAM = 31.1034768  # 1金衡盎司 = 31.1034768克
    
    # 价格合理性范围 (2024-2026年)
    VALID_RANGES = {
        'international': (1800, 3000),  # 美元/盎司
        'domestic': (450, 800),         # 元/克
    }
    
    def __init__(self):
        self.cache_dir = Path(__file__).parent.parent / "data" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.exchange_rate = 7.25  # 美元兑人民币汇率
        
        logger.info("[金价修复V2] 初始化完成")
    
    def fetch_sge_spot(self) -> Optional[Dict]:
        """
        从上海黄金交易所获取现货黄金价格
        
        这是国内最权威的金价数据源
        """
        try:
            url = "https://www.sge.com.cn/sjzx/mrhq"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml'
            }
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                html = response.text
                
                # 查找 Au99.99 价格
                # 格式: Au99.99  xxx.xx
                pattern = r'Au99\.99[^\d]*(\d{3}\.\d{2})'
                match = re.search(pattern, html)
                
                if match:
                    price = float(match.group(1))
                    
                    # 验证价格合理性
                    if self.VALID_RANGES['domestic'][0] <= price <= self.VALID_RANGES['domestic'][1]:
                        return {
                            'price': price,
                            'source': '上海黄金交易所',
                            'timestamp': datetime.now().isoformat(),
                            'type': 'spot',
                            'contract': 'Au99.99'
                        }
                    else:
                        logger.warning(f"[金价修复V2] 上金所价格 {price} 超出合理区间")
        except Exception as e:
            logger.warning(f"[金价修复V2] 上金所获取失败: {e}")
        
        return None
    
    def fetch_sina_gold(self) -> Optional[Dict]:
        """从新浪财经获取金价"""
        try:
            # 新浪财经黄金T+D
            url = "https://hq.sinajs.cn/list=hf_GC"
            headers = {
                'Referer': 'https://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200 and 'hq_str_hf_GC=' in response.text:
                # 解析: var hq_str_hf_GC="2345.6,1.23,4.56,..."
                text = response.text
                data_str = text.split('"')[1]
                parts = data_str.split(',')
                
                if len(parts) >= 1:
                    price = float(parts[0])
                    
                    # 新浪返回的是美元/盎司
                    if self.VALID_RANGES['international'][0] <= price <= self.VALID_RANGES['international'][1]:
                        return {
                            'price': price,
                            'source': '新浪财经',
                            'timestamp': datetime.now().isoformat(),
                            'type': 'international',
                            'unit': 'USD/oz'
                        }
        except Exception as e:
            logger.warning(f"[金价修复V2] 新浪财经获取失败: {e}")
        
        return None
    
    def fetch_baidu_gold(self) -> Optional[Dict]:
        """从百度获取金价"""
        try:
            url = "https://gushitong.baidu.com/opendata?resource_id=6017&query=黄金价格"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 解析百度返回的数据
                if 'data' in data and len(data['data']) > 0:
                    for item in data['data']:
                        if 'price' in item:
                            price = float(item['price'])
                            
                            # 判断是国内还是国际价格
                            if price > 1000:  # 美元/盎司
                                if self.VALID_RANGES['international'][0] <= price <= self.VALID_RANGES['international'][1]:
                                    return {
                                        'price': price,
                                        'source': '百度',
                                        'timestamp': datetime.now().isoformat(),
                                        'type': 'international',
                                        'unit': 'USD/oz'
                                    }
                            else:  # 元/克
                                if self.VALID_RANGES['domestic'][0] <= price <= self.VALID_RANGES['domestic'][1]:
                                    return {
                                        'price': price,
                                        'source': '百度',
                                        'timestamp': datetime.now().isoformat(),
                                        'type': 'domestic',
                                        'unit': 'CNY/g'
                                    }
        except Exception as e:
            logger.warning(f"[金价修复V2] 百度获取失败: {e}")
        
        return None
    
    def calculate_international_from_domestic(self, domestic_price: float) -> float:
        """
        根据国内金价计算国际金价
        
        公式：国际金价(美元/盎司) = 国内金价(元/克) × 31.1035 ÷ 汇率
        """
        international = domestic_price * self.OUNCE_TO_GRAM / self.exchange_rate
        return round(international, 2)
    
    def calculate_domestic_from_international(self, international_price: float) -> float:
        """
        根据国际金价计算国内金价
        
        公式：国内金价(元/克) = 国际金价(美元/盎司) × 汇率 ÷ 31.1035
        """
        domestic = international_price * self.exchange_rate / self.OUNCE_TO_GRAM
        return round(domestic, 2)
    
    def get_gold_price(self) -> Dict:
        """
        获取正确的金价数据
        
        策略：
        1. 优先获取国内现货（上金所）
        2. 其次获取国际金价（新浪）
        3. 互相校验
        4. 返回完整数据
        """
        logger.info("[金价修复V2] 开始获取金价数据...")
        
        domestic_price = None
        domestic_source = None
        international_price = None
        international_source = None
        
        # 1. 尝试获取国内现货
        domestic_data = self.fetch_sge_spot()
        if domestic_data:
            domestic_price = domestic_data['price']
            domestic_source = domestic_data['source']
            logger.info(f"[金价修复V2] 国内现货: ¥{domestic_price}/g ({domestic_source})")
        
        # 2. 尝试获取国际金价
        international_data = self.fetch_sina_gold()
        if not international_data:
            international_data = self.fetch_baidu_gold()
        
        if international_data:
            if international_data.get('type') == 'international':
                international_price = international_data['price']
                international_source = international_data['source']
                logger.info(f"[金价修复V2] 国际金价: ${international_price}/oz ({international_source})")
            elif international_data.get('type') == 'domestic':
                # 如果获取到的是国内价格
                if not domestic_price:
                    domestic_price = international_data['price']
                    domestic_source = international_data['source']
        
        # 3. 计算缺失的价格
        if domestic_price and not international_price:
            international_price = self.calculate_international_from_domestic(domestic_price)
            international_source = f"计算值(基于{domestic_source})"
            logger.info(f"[金价修复V2] 计算国际金价: ${international_price}/oz")
        
        elif international_price and not domestic_price:
            domestic_price = self.calculate_domestic_from_international(international_price)
            domestic_source = f"计算值(基于{international_source})"
            logger.info(f"[金价修复V2] 计算国内金价: ¥{domestic_price}/g")
        
        # 4. 互相校验
        if domestic_price and international_price:
            calculated_domestic = self.calculate_domestic_from_international(international_price)
            diff_pct = abs(domestic_price - calculated_domestic) / domestic_price * 100
            
            if diff_pct > 5:  # 差异超过5%
                logger.warning(f"[金价修复V2] 价格差异较大: {diff_pct:.2f}%")
                logger.warning(f"  国内价格: ¥{domestic_price}")
                logger.warning(f"  计算价格: ¥{calculated_domestic}")
        
        # 5. 返回结果
        if domestic_price and international_price:
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
                    'domestic_source': domestic_source,
                    'international_source': international_source,
                    'exchange_rate': self.exchange_rate,
                    'timestamp': datetime.now().isoformat(),
                    'method': 'multi_source'
                }
            }
        
        # 6. 兜底数据
        logger.error("[金价修复V2] 所有数据源失败，使用兜底数据")
        return {
            'international': {
                'price': 2350.0,
                'unit': 'USD/oz',
                'change': 0.0,
                'change_pct': 0.0
            },
            'domestic': {
                'price': self.calculate_domestic_from_international(2350.0),
                'unit': 'CNY/g',
                'change': 0.0,
                'change_pct': 0.0
            },
            'metadata': {
                'domestic_source': '兜底数据',
                'international_source': '兜底数据',
                'exchange_rate': self.exchange_rate,
                'timestamp': datetime.now().isoformat(),
                'method': 'fallback',
                'warning': '数据获取失败，使用参考值'
            }
        }
    
    def clear_old_cache(self):
        """清理旧缓存"""
        try:
            for f in self.cache_dir.glob("gold_*.json"):
                f.unlink()
                logger.info(f"[金价修复V2] 清理缓存: {f.name}")
        except Exception as e:
            logger.warning(f"[金价修复V2] 清理缓存失败: {e}")
    
    def save_cache(self, data: Dict):
        """保存缓存"""
        try:
            cache_file = self.cache_dir / f"gold_fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"[金价修复V2] 保存缓存: {cache_file.name}")
        except Exception as e:
            logger.warning(f"[金价修复V2] 保存缓存失败: {e}")


def test_fixed_gold_price():
    """测试修复后的金价获取"""
    print("="*70)
    print("🛠️ 金价数据修复测试 V2")
    print("="*70)
    
    fix = GoldPriceFixed()
    
    # 清理旧缓存
    print("\n1️⃣ 清理旧缓存...")
    fix.clear_old_cache()
    
    # 获取金价
    print("\n2️⃣ 获取金价数据...")
    data = fix.get_gold_price()
    
    # 显示结果
    print("\n3️⃣ 结果:")
    print(f"  国际金价: ${data['international']['price']:.2f} {data['international']['unit']}")
    print(f"  国内金价: ¥{data['domestic']['price']:.2f} {data['domestic']['unit']}")
    print(f"  国内来源: {data['metadata']['domestic_source']}")
    print(f"  国际来源: {data['metadata']['international_source']}")
    print(f"  汇率: {data['metadata']['exchange_rate']}")
    print(f"  时间: {data['metadata']['timestamp']}")
    
    # 验证
    print("\n4️⃣ 验证:")
    intl_price = data['international']['price']
    dom_price = data['domestic']['price']
    
    if fix.VALID_RANGES['international'][0] <= intl_price <= fix.VALID_RANGES['international'][1]:
        print(f"  ✅ 国际金价 ${intl_price:.2f} 在合理区间")
    else:
        print(f"  ❌ 国际金价 ${intl_price:.2f} 超出合理区间")
    
    if fix.VALID_RANGES['domestic'][0] <= dom_price <= fix.VALID_RANGES['domestic'][1]:
        print(f"  ✅ 国内金价 ¥{dom_price:.2f} 在合理区间")
    else:
        print(f"  ❌ 国内金价 ¥{dom_price:.2f} 超出合理区间")
    
    # 交叉验证
    calculated_domestic = fix.calculate_domestic_from_international(intl_price)
    diff = abs(dom_price - calculated_domestic)
    print(f"\n5️⃣ 交叉验证:")
    print(f"  计算国内价: ¥{calculated_domestic:.2f}")
    print(f"  实际国内价: ¥{dom_price:.2f}")
    print(f"  差异: ¥{diff:.2f} ({diff/dom_price*100:.2f}%)")
    
    if diff / dom_price < 0.05:
        print("  ✅ 价格一致性良好")
    else:
        print("  ⚠️ 价格差异较大")
    
    # 保存缓存
    print("\n6️⃣ 保存缓存...")
    fix.save_cache(data)
    
    print("\n" + "="*70)
    print("✅ 测试完成!")
    print("="*70)
    
    return data


if __name__ == "__main__":
    test_fixed_gold_price()
