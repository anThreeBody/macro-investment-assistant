#!/usr/bin/env python3
"""
金价自动获取 V8.3 - 多数据源对比验证版

核心改进:
1. 多个数据源对比（东方财富、金投网、新浪财经）
2. 价格交叉验证，识别异常数据
3. 标注数据来源和误差范围
4. 修复解析逻辑 bug

数据源:
1. 东方财富 COMEX 黄金期货
2. 金投网 (cngold.org)
3. 新浪财经黄金频道
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoldPriceFetcherV83:
    """金价自动获取器 V8.3 - 多数据源对比版"""
    
    # 换算常数
    OUNCE_TO_GRAM = 31.1034768
    EXCHANGE_RATE = 7.25
    
    # 价格合理性范围
    VALID_RANGES = {
        'international': (1800, 5500),
        'domestic': (450, 1200),
    }
    
    # 数据源间最大允许差异（百分比）
    MAX_PRICE_DIFF = 0.02  # 2%
    
    def __init__(self):
        self.data_file = Path(__file__).parent.parent / "data" / "gold_price_cache.json"
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
    
    def fetch_from_eastmoney(self) -> Optional[Dict]:
        """
        从东方财富获取 COMEX 黄金期货价格
        URL: http://quote.eastmoney.com/unify/r/101.GC00Y
        """
        logger.info("[数据源 1] 东方财富 COMEX 黄金期货...")
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # 访问东方财富
                page.goto("http://quote.eastmoney.com/unify/r/101.GC00Y", timeout=30000)
                page.wait_for_timeout(5000)
                
                # 获取页面文本
                content = page.evaluate("document.body.innerText")
                browser.close()
                
                # 解析价格
                return self._parse_eastmoney(content)
        
        except Exception as e:
            logger.error(f"[数据源 1] 东方财富获取失败：{e}")
            return None
    
    def _parse_eastmoney(self, content: str) -> Optional[Dict]:
        """解析东方财富页面内容"""
        try:
            # 查找价格模式：数字。数字 涨跌 涨跌幅
            # 示例：4989.30 +45.40 +0.92%
            pattern = r'(\d{4,5})\.(\d{1,2})\s*([+-]?\d+\.?\d*)\s*([+-]?\d+\.?\d*)%'
            matches = re.findall(pattern, content)
            
            if not matches:
                logger.warning("[数据源 1] 未找到价格模式")
                return None
            
            # 取第一个匹配（通常是最新价）
            integer_part, decimal_part, change, change_pct = matches[0]
            
            # 修复：正确组合价格
            price = float(f"{integer_part}.{decimal_part}")
            
            # 查找昨收价
            prev_pattern = r'昨 [收结] [：:]\s*(\d{4,5})\.(\d{1,2})'
            prev_match = re.search(prev_pattern, content)
            if prev_match:
                prev_price = float(f"{prev_match.group(1)}.{prev_match.group(2)}")
            else:
                prev_price = price - float(change) if change else price
            
            # 计算国内金价
            domestic = price * self.EXCHANGE_RATE / self.OUNCE_TO_GRAM
            
            result = {
                'international_usd_per_oz': round(price, 2),
                'domestic_cny_per_gram': round(domestic, 2),
                'change_usd': round(float(change) if change else 0, 2),
                'change_pct': round(float(change_pct) if change_pct else 0, 2),
                'prev_price': prev_price,
                'source': '东方财富-COMEX 黄金期货',
                'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"[数据源 1] 东方财富：${price:.2f}/oz")
            return result
            
        except Exception as e:
            logger.error(f"[数据源 1] 解析失败：{e}")
            return None
    
    def fetch_from_cngold(self) -> Optional[Dict]:
        """
        从金投网获取金价
        URL: https://gold.cngold.org/
        """
        logger.info("[数据源 2] 金投网实时金价...")
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.goto("https://gold.cngold.org/", timeout=30000)
                page.wait_for_timeout(5000)
                
                content = page.evaluate("document.body.innerText")
                browser.close()
                
                return self._parse_cngold(content)
        
        except Exception as e:
            logger.error(f"[数据源 2] 金投网获取失败：{e}")
            return None
    
    def _parse_cngold(self, content: str) -> Optional[Dict]:
        """解析金投网内容"""
        try:
            # 查找国际金价模式
            int_pattern = r'国际黄金 [^\d]*(\d{4,5})\.(\d{1,2})'
            int_match = re.search(int_pattern, content)
            
            if not int_match:
                # 尝试其他模式
                int_pattern = r'COMEX 黄金 [^\d]*(\d{4,5})\.(\d{1,2})'
                int_match = re.search(int_pattern, content)
            
            if not int_match:
                logger.warning("[数据源 2] 未找到国际金价")
                return None
            
            price = float(f"{int_match.group(1)}.{int_match.group(2)}")
            
            # 计算国内金价
            domestic = price * self.EXCHANGE_RATE / self.OUNCE_TO_GRAM
            
            result = {
                'international_usd_per_oz': round(price, 2),
                'domestic_cny_per_gram': round(domestic, 2),
                'change_usd': 0.0,
                'change_pct': 0.0,
                'prev_price': price,
                'source': '金投网',
                'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"[数据源 2] 金投网：${price:.2f}/oz")
            return result
            
        except Exception as e:
            logger.error(f"[数据源 2] 解析失败：{e}")
            return None
    
    def fetch_from_sina(self) -> Optional[Dict]:
        """
        从新浪财经获取金价
        URL: https://finance.sina.com.cn/realstock/companies/
        """
        logger.info("[数据源 3] 新浪财经黄金...")
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.goto("https://finance.sina.com.cn/realstock/companies/GC00Y.shtml", timeout=30000)
                page.wait_for_timeout(5000)
                
                content = page.evaluate("document.body.innerText")
                browser.close()
                
                return self._parse_sina(content)
        
        except Exception as e:
            logger.error(f"[数据源 3] 新浪财经获取失败：{e}")
            return None
    
    def _parse_sina(self, content: str) -> Optional[Dict]:
        """解析新浪财经内容"""
        try:
            # 查找价格
            pattern = r'(\d{4,5})\.(\d{1,2})'
            matches = re.findall(pattern, content)
            
            if not matches:
                return None
            
            # 查找接近 2000-5000 范围的价格（国际金价）
            for integer_part, decimal_part in matches:
                price = float(f"{integer_part}.{decimal_part}")
                if 2000 <= price <= 5500:
                    domestic = price * self.EXCHANGE_RATE / self.OUNCE_TO_GRAM
                    
                    result = {
                        'international_usd_per_oz': round(price, 2),
                        'domestic_cny_per_gram': round(domestic, 2),
                        'change_usd': 0.0,
                        'change_pct': 0.0,
                        'prev_price': price,
                        'source': '新浪财经',
                        'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    logger.info(f"[数据源 3] 新浪财经：${price:.2f}/oz")
                    return result
            
            return None
            
        except Exception as e:
            logger.error(f"[数据源 3] 解析失败：{e}")
            return None
    
    def validate_and_merge(self, sources: List[Optional[Dict]]) -> Dict:
        """
        验证并合并多个数据源
        
        Args:
            sources: 多个数据源的结果列表
            
        Returns:
            Dict: 合并后的结果
        """
        # 过滤掉 None
        valid_sources = [s for s in sources if s is not None]
        
        if not valid_sources:
            raise Exception("所有数据源均获取失败")
        
        # 提取价格
        prices = [s['international_usd_per_oz'] for s in valid_sources]
        
        # 计算统计
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        price_diff_pct = (price_range / avg_price) * 100 if avg_price else 0
        
        # 检查数据源间差异
        if price_diff_pct > self.MAX_PRICE_DIFF * 100:
            logger.warning(f"数据源间差异过大：{price_diff_pct:.2f}% (阈值：{self.MAX_PRICE_DIFF * 100}%)")
        
        # 使用中位数价格（更稳健）
        sorted_prices = sorted(prices)
        median_price = sorted_prices[len(sorted_prices) // 2]
        
        # 选择最接近中位数的数据源作为基准
        best_source = min(valid_sources, 
                         key=lambda s: abs(s['international_usd_per_oz'] - median_price))
        
        # 构建结果
        result = best_source.copy()
        result['data_sources'] = {
            'total_sources': len(sources),
            'successful_sources': len(valid_sources),
            'source_names': [s['source'] for s in valid_sources],
            'price_range': {
                'min': min_price,
                'max': max_price,
                'avg': avg_price,
                'median': median_price,
                'diff_pct': round(price_diff_pct, 2)
            },
            'confidence': '高' if len(valid_sources) >= 2 and price_diff_pct < 1 else '中' if len(valid_sources) >= 1 else '低'
        }
        
        # 调整价格为中位数
        result['international_usd_per_oz'] = round(median_price, 2)
        result['domestic_cny_per_gram'] = round(median_price * self.EXCHANGE_RATE / self.OUNCE_TO_GRAM, 2)
        
        logger.info(f"数据验证完成：{len(valid_sources)}/{len(sources)} 个数据源成功，差异：{price_diff_pct:.2f}%")
        
        return result
    
    def fetch(self) -> Dict:
        """
        获取金价（主方法）- 多数据源对比
        
        Returns:
            Dict: 金价数据
        """
        logger.info("=" * 60)
        logger.info("开始获取金价（多数据源对比）...")
        logger.info("=" * 60)
        
        # 并行获取多个数据源
        sources = []
        
        # 数据源 1: 东方财富
        eastmoney_data = self.fetch_from_eastmoney()
        sources.append(eastmoney_data)
        
        # 数据源 2: 金投网
        cngold_data = self.fetch_from_cngold()
        sources.append(cngold_data)
        
        # 数据源 3: 新浪财经
        sina_data = self.fetch_from_sina()
        sources.append(sina_data)
        
        # 验证并合并
        result = self.validate_and_merge(sources)
        
        # 最终验证
        if not self._validate_price(result['international_usd_per_oz'], 'international'):
            raise Exception(f"国际金价超出合理区间：{result['international_usd_per_oz']}")
        
        if not self._validate_price(result['domestic_cny_per_gram'], 'domestic'):
            raise Exception(f"国内金价超出合理区间：{result['domestic_cny_per_gram']}")
        
        logger.info(f"获取成功：国际${result['international_usd_per_oz']}/oz, 国内¥{result['domestic_cny_per_gram']}/g")
        logger.info(f"数据来源：{', '.join(result['data_sources']['source_names'])}")
        logger.info(f"置信度：{result['data_sources']['confidence']}")
        
        return result
    
    def _validate_price(self, price: float, price_type: str = 'international') -> bool:
        """验证价格合理性"""
        if price_type not in self.VALID_RANGES:
            return False
        min_val, max_val = self.VALID_RANGES[price_type]
        return min_val <= price <= max_val
    
    def save(self, data: Dict):
        """保存到缓存文件"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"数据已保存：{self.data_file}")


def main():
    """主函数"""
    print("=" * 70)
    print("📈 金价自动获取 V8.3 - 多数据源对比验证版")
    print("=" * 70)
    print()
    
    fetcher = GoldPriceFetcherV83()
    
    try:
        data = fetcher.fetch()
        
        print()
        print("✅ 获取成功!")
        print()
        print(f"国际金价：${data['international_usd_per_oz']:.2f}/oz")
        print(f"涨跌额：{data.get('change_usd', 0):+.2f}")
        print(f"涨跌幅：{data.get('change_pct', 0):+.2f}%")
        print(f"国内金价：¥{data['domestic_cny_per_gram']:.2f}/g")
        print()
        print(f"数据来源：{', '.join(data['data_sources']['source_names'])}")
        print(f"数据置信度：{data['data_sources']['confidence']}")
        print()
        
        # 显示价格范围
        pr = data['data_sources']['price_range']
        print(f"价格对比:")
        print(f"  最低：${pr['min']:.2f}")
        print(f"  最高：${pr['max']:.2f}")
        print(f"  平均：${pr['avg']:.2f}")
        print(f"  差异：{pr['diff_pct']:.2f}%")
        print()
        
        if pr['diff_pct'] > 2:
            print("⚠️  警告：数据源间差异超过 2%，请谨慎参考")
            print()
        
        print(f"更新时间：{data['update_time']}")
        print()
        
        # 保存数据
        fetcher.save(data)
        
        print("=" * 70)
        return 0
        
    except Exception as e:
        print()
        print("❌ 获取失败!")
        print()
        print(f"错误：{e}")
        print()
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit(main())
