#!/usr/bin/env python3
"""
金价数据源 - 多数据源对比验证版 V8.3

使用多个数据源对比验证获取实时金价
数据来源：
1. 东方财富 COMEX 黄金期货
2. 金投网 (cngold.org)
3. 新浪财经黄金频道

特点：
1. 多数据源对比验证
2. 识别异常数据
3. 标注数据来源和误差范围
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from data_sources.base import DataSource, DataSourceConfig

# 导入多数据源获取模块
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from gold_price_auto_v83 import GoldPriceFetcherV83
    MULTI_SOURCE_AVAILABLE = True
except ImportError as e:
    MULTI_SOURCE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.error(f"GoldPriceFetcherV83 导入失败：{e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoldDataSource(DataSource):
    """
    金价数据源 V8.3
    
    获取策略：
    1. 使用多数据源对比验证
    2. 如果获取失败，报错并提示
    3. 提供数据来源和置信度信息
    """
    
    def __init__(self):
        config = DataSourceConfig(
            name='多数据源对比',
            source_type='gold',
            cache_enabled=False,  # 不使用缓存
            retry_times=0,
            timeout=60,
        )
        super().__init__(config)
        
        # 初始化多数据源获取模块
        if MULTI_SOURCE_AVAILABLE:
            self.fetcher = GoldPriceFetcherV83()
            logger.info("[金价数据] 多数据源已加载")
        else:
            self.fetcher = None
            logger.error("[金价数据] 多数据源未加载")
    
    def fetch(self, **kwargs) -> Dict[str, Any]:
        """
        获取金价数据（多数据源对比）
        
        Returns:
            Dict[str, Any]: 金价数据
        
        Raises:
            Exception: 如果无法获取金价数据
        """
        logger.info("[金价数据] 开始获取金价（多数据源对比）...")
        
        if not self.fetcher:
            raise Exception("金价多数据源未加载")
        
        try:
            # 使用多数据源获取实时金价
            data = self.fetcher.fetch()
            
            # 获取昨天的国内金价（用于计算涨跌）
            yesterday_price = self._get_yesterday_domestic_price()
            
            # 计算国内金价涨跌
            domestic_price = data['domestic_cny_per_gram']
            if yesterday_price and yesterday_price > 0:
                domestic_change = domestic_price - yesterday_price
                domestic_change_pct = (domestic_change / yesterday_price) * 100
                logger.info(f"[金价数据] 国内金价涨跌计算：昨收={yesterday_price}, 今收={domestic_price}, 涨跌={domestic_change:.2f}, 涨跌幅={domestic_change_pct:.2f}%")
            else:
                domestic_change = 0.0
                domestic_change_pct = 0.0
                logger.warning(f"[金价数据] 未找到昨天价格，无法计算涨跌")
            
            # 转换为标准格式
            result = {
                'international': {
                    'price': data['international_usd_per_oz'],
                    'change': data.get('change_usd', 0),
                    'change_pct': data.get('change_pct', 0),
                    'currency': 'USD',
                    'unit': 'oz',
                },
                'domestic': {
                    'price': domestic_price,
                    'change': round(domestic_change, 2),
                    'change_pct': round(domestic_change_pct, 2),
                    'currency': 'CNY',
                    'unit': 'g',
                },
                'metadata': {
                    'source': ', '.join(data['data_sources']['source_names']),
                    'confidence': data['data_sources']['confidence'],
                    'price_range': data['data_sources']['price_range'],
                    'update_time': data['update_time'],
                }
            }
            
            logger.info(f"[金价数据] 获取成功 - 国际：${result['international']['price']}, 国内：¥{result['domestic']['price']}")
            logger.info(f"[金价数据] 数据来源：{result['metadata']['source']}")
            logger.info(f"[金价数据] 置信度：{result['metadata']['confidence']}")
            
            return result
            
        except Exception as e:
            logger.error(f"[金价数据] 获取失败：{e}")
            raise
    
    def _get_yesterday_domestic_price(self) -> Optional[float]:
        """
        获取昨天的国内金价（用于计算涨跌）
        
        Returns:
            Optional[float]: 昨天的金价，如果获取失败返回 None
        """
        try:
            import sqlite3
            from datetime import datetime, timedelta
            
            db_path = Path(__file__).parent.parent / "data" / "predictions.db"
            if not db_path.exists():
                logger.warning("[金价数据] 预测数据库不存在")
                return None
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # 获取最近一次的国内金价记录（昨天的）
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT current_price 
                FROM predictions 
                WHERE predict_date <= ? 
                ORDER BY predict_date DESC, created_at DESC 
                LIMIT 1
            ''', (yesterday,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0]:
                price = float(row[0])
                logger.info(f"[金价数据] 获取到昨天价格：¥{price:.2f}")
                return price
            else:
                logger.warning(f"[金价数据] 未找到昨天的价格记录")
                return None
                
        except Exception as e:
            logger.error(f"[金价数据] 获取昨天价格失败：{e}")
            return None
    
    def fetch_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取历史金价数据
        
        ⚠️ 注意：当前版本只支持实时数据，历史数据需要额外实现
        
        Args:
            days: 获取天数
            
        Returns:
            List[Dict]: 历史数据列表（空列表）
        """
        logger.warning("[金价数据] 历史数据功能暂不可用")
        return []


def test_gold_source():
    """测试金价数据源"""
    print("="*70)
    print("🎯 金价数据源测试")
    print("="*70)
    
    ds = GoldDataSource()
    
    try:
        print("\n开始获取实时金价...")
        data = ds.fetch()
        
        print("\n" + "="*70)
        print("✅ 获取成功!")
        print("="*70)
        print(f"\n国际金价：${data['international']['price']:.2f}/{data['international']['unit']}")
        print(f"涨跌额：{data['international']['change']:+.2f}")
        print(f"涨跌幅：{data['international']['change_pct']:+.2f}%")
        print(f"\n国内金价：¥{data['domestic']['price']:.2f}/{data['domestic']['unit']}")
        print(f"\n数据来源：{data['metadata']['source']}")
        print(f"更新时间：{data['metadata']['timestamp']}")
        print(f"获取方式：{data['metadata']['method']}")
        
        return data
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ 获取失败!")
        print("="*70)
        print(f"\n错误：{e}")
        return None


if __name__ == "__main__":
    test_gold_source()
