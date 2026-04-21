#!/usr/bin/env python3
"""
金价获取 - 最终方案

由于网络限制，无法自动获取实时金价
本模块提供：
1. 清晰的错误提示
2. 用户手动输入接口
3. 环境变量配置
4. 文件配置

使用方法：
1. 环境变量: export GOLD_PRICE_INTL=2350; export GOLD_PRICE_DOMESTIC=548
2. 配置文件: data/gold_config.json
3. 手动输入: 调用时传入参数
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoldPriceFinal:
    """金价获取 - 最终方案"""
    
    OUNCE_TO_GRAM = 31.1034768
    EXCHANGE_RATE = 7.25
    
    VALID_RANGES = {
        'international': (1800, 3000),
        'domestic': (450, 800),
    }
    
    def __init__(self):
        self.config_file = Path(__file__).parent.parent / "data" / "gold_config.json"
        logger.info("[金价获取] 初始化完成")
    
    def get_from_env(self) -> Optional[Dict]:
        """从环境变量获取"""
        intl = os.getenv('GOLD_PRICE_INTL')
        domestic = os.getenv('GOLD_PRICE_DOMESTIC')
        
        if intl and domestic:
            try:
                return {
                    'international': {'price': float(intl), 'unit': 'USD/oz', 'change': 0.0, 'change_pct': 0.0},
                    'domestic': {'price': float(domestic), 'unit': 'CNY/g', 'change': 0.0, 'change_pct': 0.0},
                    'metadata': {
                        'source': '环境变量',
                        'timestamp': datetime.now().isoformat(),
                        'exchange_rate': self.EXCHANGE_RATE,
                        'method': 'env'
                    }
                }
            except:
                pass
        return None
    
    def get_from_file(self) -> Optional[Dict]:
        """从配置文件获取"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 检查数据是否过期（24小时）
                timestamp = data.get('metadata', {}).get('timestamp', '')
                if timestamp:
                    saved_time = datetime.fromisoformat(timestamp)
                    hours_old = (datetime.now() - saved_time).total_seconds() / 3600
                    
                    if hours_old > 24:
                        data['metadata']['warning'] = f'数据已过期 {hours_old:.1f} 小时'
                
                return data
            except:
                pass
        return None
    
    def get_from_manual(self, international: float, domestic: float) -> Dict:
        """从手动输入获取"""
        return {
            'international': {'price': international, 'unit': 'USD/oz', 'change': 0.0, 'change_pct': 0.0},
            'domestic': {'price': domestic, 'unit': 'CNY/g', 'change': 0.0, 'change_pct': 0.0},
            'metadata': {
                'source': '手动输入',
                'timestamp': datetime.now().isoformat(),
                'exchange_rate': self.EXCHANGE_RATE,
                'method': 'manual'
            }
        }
    
    def save_to_file(self, data: Dict):
        """保存到配置文件"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"[金价获取] 已保存到: {self.config_file}")
    
    def validate(self, data: Dict) -> bool:
        """验证价格合理性"""
        intl_price = data.get('international', {}).get('price', 0)
        dom_price = data.get('domestic', {}).get('price', 0)
        
        if not (self.VALID_RANGES['international'][0] <= intl_price <= self.VALID_RANGES['international'][1]):
            return False
        
        if not (self.VALID_RANGES['domestic'][0] <= dom_price <= self.VALID_RANGES['domestic'][1]):
            return False
        
        return True
    
    def get_price(self, international: Optional[float] = None, domestic: Optional[float] = None) -> Dict:
        """
        获取金价
        
        优先级：
        1. 手动输入参数
        2. 环境变量
        3. 配置文件
        4. 报错
        """
        # 1. 手动输入
        if international is not None and domestic is not None:
            data = self.get_from_manual(international, domestic)
            if self.validate(data):
                self.save_to_file(data)
                return data
            else:
                raise ValueError(f"价格超出合理区间: 国际{international}, 国内{domestic}")
        
        # 2. 环境变量
        data = self.get_from_env()
        if data and self.validate(data):
            logger.info("[金价获取] 从环境变量获取")
            return data
        
        # 3. 配置文件
        data = self.get_from_file()
        if data and self.validate(data):
            logger.info("[金价获取] 从配置文件获取")
            return data
        
        # 4. 报错
        error_msg = """
╔══════════════════════════════════════════════════════════════════╗
║                    ⚠️  无法获取实时金价数据                      ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  由于网络限制，系统无法自动获取实时金价。                        ║
║                                                                  ║
║  请通过以下方式之一提供金价数据：                                ║
║                                                                  ║
║  方法1 - 环境变量（推荐）：                                      ║
║    export GOLD_PRICE_INTL=2350                                   ║
║    export GOLD_PRICE_DOMESTIC=548                                ║
║                                                                  ║
║  方法2 - 配置文件：                                              ║
║    编辑文件: data/gold_config.json                               ║
║    格式: {"international": {"price": 2350}, "domestic": {"price": 548}} ║
║                                                                  ║
║  方法3 - 手动输入：                                              ║
║    在代码中调用: get_price(international=2350, domestic=548)     ║
║                                                                  ║
║  参考价格（2024-2025）：                                         ║
║    国际金价: 2200-2500 美元/盎司                                 ║
║    国内金价: 500-600 元/克                                       ║
║                                                                  ║
║  查询实时金价：                                                  ║
║    - 金投网: https://www.cngold.org                              ║
║    - 新浪财经: https://finance.sina.com.cn/money/gold/          ║
║    - 百度搜索: "今日金价"                                        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
        logger.error(error_msg)
        raise Exception(error_msg)


def test_final():
    """测试"""
    print("="*70)
    print("🎯 金价获取 - 最终方案测试")
    print("="*70)
    
    fetcher = GoldPriceFinal()
    
    # 测试1: 无数据时报错
    print("\n1️⃣ 测试无数据情况...")
    try:
        data = fetcher.get_price()
        print("❌ 应该报错但没有")
    except Exception as e:
        print("✅ 正确报错")
        print(f"   错误信息: {str(e)[:100]}...")
    
    # 测试2: 手动输入
    print("\n2️⃣ 测试手动输入...")
    try:
        data = fetcher.get_price(international=2350, domestic=548)
        print(f"✅ 获取成功")
        print(f"   国际: ${data['international']['price']}")
        print(f"   国内: ¥{data['domestic']['price']}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    # 测试3: 环境变量
    print("\n3️⃣ 测试环境变量...")
    os.environ['GOLD_PRICE_INTL'] = '2400'
    os.environ['GOLD_PRICE_DOMESTIC'] = '560'
    try:
        data = fetcher.get_price()
        print(f"✅ 从环境变量获取成功")
        print(f"   国际: ${data['international']['price']}")
        print(f"   国内: ¥{data['domestic']['price']}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print("\n" + "="*70)
    print("✅ 测试完成!")
    print("="*70)


if __name__ == "__main__":
    test_final()
