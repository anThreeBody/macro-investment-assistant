#!/usr/bin/env python3
"""
股票数据源 - 从 AKShare/东方财富获取 A 股数据

支持：
- 股票实时行情
- 股票基本信息
- 行业板块数据
- 历史 K 线数据
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from data_sources.base import DataSource, DataSourceConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataSource(DataSource):
    """股票数据源"""
    
    def __init__(self):
        config = DataSourceConfig(
            name='AKShare/东方财富',
            source_type='stock',
            cache_enabled=True,
            cache_ttl=120,  # 股票缓存 2 分钟（交易时段实时性要求高）
            retry_times=3,
            timeout=30,
        )
        super().__init__(config)
        
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch(self, stock_code: str, **kwargs) -> Dict[str, Any]:
        """
        获取单只股票数据
        
        Args:
            stock_code: 股票代码（如：000001 或 sh600000）
            
        Returns:
            Dict[str, Any]: {
                'code': str,
                'name': str,
                'price': float,
                'change': float,
                'change_pct': float,
                'volume': float,
                'amount': float,
                'metadata': {...}
            }
        """
        logger.info(f"[AKShare] 获取股票 {stock_code} 数据...")
        
        try:
            import akshare as ak
            
            # 处理股票代码格式
            if stock_code.startswith('sh') or stock_code.startswith('sz'):
                symbol = stock_code
            else:
                if stock_code.startswith('6'):
                    symbol = f"sh{stock_code}"
                else:
                    symbol = f"sz{stock_code}"
            
            # 获取实时行情
            stock_df = ak.stock_zh_a_spot_em()
            stock_row = stock_df[stock_df['代码'] == stock_code]
            
            if stock_row.empty:
                logger.warning(f"[AKShare] 未找到股票 {stock_code}")
                return self._get_fallback_data(stock_code)
            
            result = {
                'code': stock_code,
                'name': stock_row.iloc[0]['名称'],
                'price': float(stock_row.iloc[0]['最新价']),
                'change': float(stock_row.iloc[0].get('涨跌额', 0)),
                'change_pct': float(stock_row.iloc[0].get('涨跌幅', 0)),
                'volume': float(stock_row.iloc[0].get('成交量', 0)),
                'amount': float(stock_row.iloc[0].get('成交额', 0)),
                'turnover': float(stock_row.iloc[0].get('换手率', 0)),
                'pe': float(stock_row.iloc[0].get('市盈率 - 动态', 0)),
                'pb': float(stock_row.iloc[0].get('市净率', 0)),
                'metadata': self.get_standard_metadata()
            }
            
            logger.info(f"[AKShare] 获取成功 - {result['name']}: {result['price']} ({result['change_pct']}%)")
            return result
            
        except ImportError:
            logger.warning("[AKShare] AKShare 未安装")
            return self._get_fallback_data(stock_code)
        except Exception as e:
            logger.error(f"[AKShare] 获取数据失败：{e}")
            return self._get_fallback_data(stock_code)
    
    def fetch_industry(self, industry_name: str) -> List[Dict[str, Any]]:
        """
        获取行业板块数据
        
        Args:
            industry_name: 行业名称
            
        Returns:
            List[Dict]: 行业内股票列表
        """
        logger.info(f"[AKShare] 获取行业 {industry_name} 数据...")
        
        try:
            import akshare as ak
            
            # 获取板块成分
            industry_df = ak.stock_board_industry_cons_em(symbol=industry_name)
            
            stocks = []
            for _, row in industry_df.iterrows():
                stocks.append({
                    'code': row.get('代码', ''),
                    'name': row.get('名称', ''),
                    'price': float(row.get('最新价', 0)),
                    'change_pct': float(row.get('涨跌幅', 0)),
                })
            
            logger.info(f"[AKShare] 获取到{len(stocks)}只股票")
            return stocks
            
        except Exception as e:
            logger.error(f"[AKShare] 获取行业数据失败：{e}")
            return []
    
    def fetch_market_overview(self) -> Dict[str, Any]:
        """
        获取市场概览
        
        Returns:
            Dict[str, Any]: 市场整体情况
        """
        logger.info("[AKShare] 获取市场概览...")
        
        try:
            import akshare as ak
            
            # 获取上证指数
            sh_index = ak.stock_zh_index_spot_em()
            sh_row = sh_index[sh_index['名称'] == '上证指数']
            
            # 获取深证成指
            sz_row = sh_index[sh_index['名称'] == '深证成指']
            
            # 获取创业板指
            cyb_row = sh_index[sh_index['名称'] == '创业板指']
            
            result = {
                'shanghai': {
                    'name': '上证指数',
                    'price': float(sh_row.iloc[0]['最新价']) if not sh_row.empty else 0,
                    'change_pct': float(sh_row.iloc[0]['涨跌幅']) if not sh_row.empty else 0,
                },
                'shenzhen': {
                    'name': '深证成指',
                    'price': float(sz_row.iloc[0]['最新价']) if not sz_row.empty else 0,
                    'change_pct': float(sz_row.iloc[0]['涨跌幅']) if not sz_row.empty else 0,
                },
                'chinext': {
                    'name': '创业板指',
                    'price': float(cyb_row.iloc[0]['最新价']) if not cyb_row.empty else 0,
                    'change_pct': float(cyb_row.iloc[0]['涨跌幅']) if not cyb_row.empty else 0,
                },
                'metadata': self.get_standard_metadata()
            }
            
            logger.info(f"[AKShare] 上证指数：{result['shanghai']['price']} ({result['shanghai']['change_pct']}%)")
            return result
            
        except Exception as e:
            logger.error(f"[AKShare] 获取市场概览失败：{e}")
            return {}
    
    def fetch_history(self, stock_code: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取股票历史 K 线数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期（YYYYMMDD）
            end_date: 结束日期（YYYYMMDD）
            
        Returns:
            List[Dict]: K 线数据列表
        """
        logger.info(f"[AKShare] 获取股票 {stock_code} 历史 K 线...")
        
        try:
            import akshare as ak
            
            stock_df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
            )
            
            klines = []
            for _, row in stock_df.iterrows():
                klines.append({
                    'date': str(row.get('日期', '')),
                    'open': float(row.get('开盘', 0)),
                    'high': float(row.get('最高', 0)),
                    'low': float(row.get('最低', 0)),
                    'close': float(row.get('收盘', 0)),
                    'volume': float(row.get('成交量', 0)),
                    'amount': float(row.get('成交额', 0)),
                })
            
            logger.info(f"[AKShare] 获取到{len(klines)}条 K 线数据")
            return klines
            
        except Exception as e:
            logger.error(f"[AKShare] 获取 K 线数据失败：{e}")
            return []
    
    def _get_fallback_data(self, stock_code: str) -> Dict[str, Any]:
        """获取兜底数据"""
        return {
            'code': stock_code,
            'name': '未知',
            'price': 0.0,
            'change': 0.0,
            'change_pct': 0.0,
            'volume': 0.0,
            'amount': 0.0,
            'metadata': self.get_standard_metadata(),
            'error': '数据获取失败'
        }
