#!/usr/bin/env python3
"""
金价紧急修复模块

问题：
1. 数据源失效 - 多个数据源无法访问
2. 价格错误 - 期货价格误作现货，计算错误
3. 缓存问题 - 旧数据不更新

解决方案：
1. 使用手动配置的合理价格
2. 提供价格更新接口
3. 明确标记数据来源
4. 添加价格合理性检查

使用方法：
1. 手动更新价格: python gold_emergency_fix.py --update --intl 2350 --domestic 548
2. 获取价格: python gold_emergency_fix.py
3. 在系统中使用: from data_sources.gold_emergency_fix import get_gold_price
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# 默认合理价格 (2024-2025年参考)
# 这些价格需要定期手动更新
DEFAULT_PRICES = {
    'international': 2350.0,  # 美元/盎司
    'domestic': 548.0,        # 元/克
    'exchange_rate': 7.25,    # 美元兑人民币
}

# 价格合理性范围
VALID_RANGES = {
    'international': (1800, 3000),  # 美元/盎司
    'domestic': (450, 800),         # 元/克
}

# 换算常数
OUNCE_TO_GRAM = 31.1034768


def get_price_file() -> Path:
    """获取价格文件路径"""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "gold_price_manual.json"


def save_price(international: float, domestic: float, exchange_rate: float = 7.25):
    """保存手动设置的价格"""
    price_file = get_price_file()
    
    data = {
        'international': {
            'price': international,
            'unit': 'USD/oz',
            'change': 0.0,
            'change_pct': 0.0
        },
        'domestic': {
            'price': domestic,
            'unit': 'CNY/g',
            'change': 0.0,
            'change_pct': 0.0
        },
        'metadata': {
            'source': '手动配置',
            'timestamp': datetime.now().isoformat(),
            'exchange_rate': exchange_rate,
            'method': 'manual',
            'warning': '请定期更新价格数据'
        }
    }
    
    with open(price_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 价格已保存: {price_file}")
    print(f"   国际金价: ${international}/oz")
    print(f"   国内金价: ¥{domestic}/g")
    print(f"   汇率: {exchange_rate}")


def load_price() -> Optional[Dict]:
    """加载保存的价格"""
    price_file = get_price_file()
    
    if price_file.exists():
        with open(price_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return None


def get_gold_price() -> Dict:
    """
    获取金价数据
    
    优先使用手动配置的价格，如果没有则使用默认值
    """
    # 尝试加载保存的价格
    saved = load_price()
    if saved:
        # 检查价格是否过期（超过24小时）
        timestamp = saved.get('metadata', {}).get('timestamp', '')
        if timestamp:
            try:
                saved_time = datetime.fromisoformat(timestamp)
                hours_old = (datetime.now() - saved_time).total_seconds() / 3600
                if hours_old > 24:
                    saved['metadata']['warning'] = f'数据已过期 {hours_old:.1f} 小时，请更新'
            except:
                pass
        return saved
    
    # 使用默认价格
    return {
        'international': {
            'price': DEFAULT_PRICES['international'],
            'unit': 'USD/oz',
            'change': 0.0,
            'change_pct': 0.0
        },
        'domestic': {
            'price': DEFAULT_PRICES['domestic'],
            'unit': 'CNY/g',
            'change': 0.0,
            'change_pct': 0.0
        },
        'metadata': {
            'source': '默认配置',
            'timestamp': datetime.now().isoformat(),
            'exchange_rate': DEFAULT_PRICES['exchange_rate'],
            'method': 'default',
            'warning': '使用默认价格，请手动更新为实时数据'
        }
    }


def validate_price(price: float, price_type: str) -> bool:
    """验证价格合理性"""
    if price_type not in VALID_RANGES:
        return False
    min_val, max_val = VALID_RANGES[price_type]
    return min_val <= price <= max_val


def calculate_domestic(international: float, exchange_rate: float = 7.25) -> float:
    """根据国际金价计算国内金价"""
    return round(international * exchange_rate / OUNCE_TO_GRAM, 2)


def calculate_international(domestic: float, exchange_rate: float = 7.25) -> float:
    """根据国内金价计算国际金价"""
    return round(domestic * OUNCE_TO_GRAM / exchange_rate, 2)


def main():
    parser = argparse.ArgumentParser(description='金价紧急修复工具')
    parser.add_argument('--update', '-u', action='store_true', help='更新价格')
    parser.add_argument('--intl', '-i', type=float, help='国际金价 (美元/盎司)')
    parser.add_argument('--domestic', '-d', type=float, help='国内金价 (元/克)')
    parser.add_argument('--rate', '-r', type=float, default=7.25, help='汇率 (默认7.25)')
    parser.add_argument('--show', '-s', action='store_true', help='显示当前价格')
    
    args = parser.parse_args()
    
    if args.update:
        # 更新价格
        if args.intl and args.domestic:
            # 验证价格
            if not validate_price(args.intl, 'international'):
                print(f"❌ 国际金价 {args.intl} 超出合理区间 {VALID_RANGES['international']}")
                return
            if not validate_price(args.domestic, 'domestic'):
                print(f"❌ 国内金价 {args.domestic} 超出合理区间 {VALID_RANGES['domestic']}")
                return
            
            save_price(args.intl, args.domestic, args.rate)
        
        elif args.intl:
            # 只提供国际金价，计算国内金价
            if not validate_price(args.intl, 'international'):
                print(f"❌ 国际金价 {args.intl} 超出合理区间")
                return
            
            domestic = calculate_domestic(args.intl, args.rate)
            save_price(args.intl, domestic, args.rate)
        
        elif args.domestic:
            # 只提供国内金价，计算国际金价
            if not validate_price(args.domestic, 'domestic'):
                print(f"❌ 国内金价 {args.domestic} 超出合理区间")
                return
            
            international = calculate_international(args.domestic, args.rate)
            save_price(international, args.domestic, args.rate)
        
        else:
            print("❌ 请提供价格参数: --intl 或 --domestic")
            print("\n示例:")
            print("  python gold_emergency_fix.py --update --intl 2350 --domestic 548")
            print("  python gold_emergency_fix.py --update --intl 2350")
            print("  python gold_emergency_fix.py --update --domestic 548")
    
    elif args.show or not args.update:
        # 显示当前价格
        data = get_gold_price()
        
        print("="*60)
        print("📊 当前金价数据")
        print("="*60)
        print(f"\n国际金价: ${data['international']['price']:.2f} {data['international']['unit']}")
        print(f"国内金价: ¥{data['domestic']['price']:.2f} {data['domestic']['unit']}")
        print(f"\n数据来源: {data['metadata']['source']}")
        print(f"更新时间: {data['metadata']['timestamp']}")
        print(f"汇率: {data['metadata']['exchange_rate']}")
        
        warning = data['metadata'].get('warning', '')
        if warning:
            print(f"\n⚠️  {warning}")
        
        # 验证价格
        print("\n" + "="*60)
        print("✅ 价格验证:")
        if validate_price(data['international']['price'], 'international'):
            print(f"  国际金价: 合理 (${data['international']['price']:.2f})")
        else:
            print(f"  国际金价: ❌ 异常")
        
        if validate_price(data['domestic']['price'], 'domestic'):
            print(f"  国内金价: 合理 (¥{data['domestic']['price']:.2f})")
        else:
            print(f"  国内金价: ❌ 异常")
        
        print("="*60)


if __name__ == "__main__":
    main()
