#!/usr/bin/env python3
"""
基金数据源 - 从 AKShare 获取基金数据

支持：
- 基金净值
- 基金基本信息
- 基金历史净值
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from data_sources.base import DataSource, DataSourceConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FundDataSource(DataSource):
    """基金数据源"""
    
    def __init__(self):
        config = DataSourceConfig(
            name='AKShare',
            source_type='fund',
            cache_enabled=True,
            cache_ttl=3600,  # 基金缓存 1 小时（日频更新）
            retry_times=3,
            timeout=30,
        )
        super().__init__(config)
        
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch(self, fund_code: str, **kwargs) -> Dict[str, Any]:
        """
        获取单只基金数据
        
        Args:
            fund_code: 基金代码
            
        Returns:
            Dict[str, Any]: {
                'code': str,
                'name': str,
                'net_value': float,
                'change': float,
                'change_pct': float,
                'update_date': str,
                'metadata': {...}
            }
        """
        logger.info(f"[AKShare] 获取基金 {fund_code} 数据...")
        
        try:
            import akshare as ak
            import pandas as pd
            
            # 获取基金实时行情
            fund_em_open_fund_daily_df = ak.fund_open_fund_daily_em()
            
            # 查找指定基金
            fund_row = fund_em_open_fund_daily_df[
                fund_em_open_fund_daily_df['基金代码'] == fund_code
            ]
            
            if fund_row.empty:
                logger.warning(f"[AKShare] 未找到基金 {fund_code}")
                return self._get_fallback_data(fund_code)
            
            result = {
                'code': fund_code,
                'name': fund_row.iloc[0]['基金名称'],
                'net_value': float(fund_row.iloc[0]['单位净值']),
                'change': float(fund_row.iloc[0].get('日增长值', 0)),
                'change_pct': float(fund_row.iloc[0].get('日增长率', 0)),
                'update_date': str(fund_row.iloc[0].get('日期', '')),
                'metadata': self.get_standard_metadata()
            }
            
            logger.info(f"[AKShare] 获取成功 - {result['name']}: {result['net_value']} ({result['change_pct']}%)")
            return result
            
        except ImportError:
            logger.warning("[AKShare] AKShare 未安装，使用缓存数据")
            return self._get_fallback_data(fund_code)
        except Exception as e:
            logger.error(f"[AKShare] 获取数据失败：{e}")
            return self._get_fallback_data(fund_code)
    
    def fetch_all(self, fund_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取所有基金数据
        
        Args:
            fund_type: 基金类型筛选（可选）
            
        Returns:
            List[Dict]: 基金列表
        """
        logger.info("[AKShare] 获取所有基金数据...")
        
        try:
            import akshare as ak
            from datetime import datetime, timedelta
            
            fund_df = ak.fund_open_fund_daily_em()
            
            # 动态获取最新净值列名
            # AKShare 返回的列名格式：YYYY-MM-DD-单位净值
            # 需要找到最新的净值列
            
            nav_column = None
            latest_nav_col = None
            
            # 查找所有包含"-单位净值"的列
            nav_columns = [col for col in fund_df.columns if '-单位净值' in col]
            
            if nav_columns:
                # 选择第一个（通常是最新的）
                nav_column = nav_columns[0]
                logger.info(f"[AKShare] 找到净值列：{nav_column} (共{len(nav_columns)}个)")
            else:
                # 兜底：尝试标准列名
                fallback_columns = ['单位净值', '最新净值', 'net_value']
                for col in fallback_columns:
                    if col in fund_df.columns:
                        nav_column = col
                        logger.info(f"[AKShare] 使用兜底净值列：{col}")
                        break
            
            if nav_column is None:
                logger.error(f"[AKShare] 未找到净值列，可用列：{list(fund_df.columns)[:10]}")
                return []
            
            funds = []
            for _, row in fund_df.iterrows():
                try:
                    net_value = row.get(nav_column, 0)
                    change_pct = row.get('日增长率', 0)
                    
                    # 处理空字符串和 None
                    if net_value == '' or net_value is None:
                        net_value = 0
                    if change_pct == '' or change_pct is None:
                        change_pct = 0
                    
                    # 跳过净值为 0 的基金（无效数据）
                    if net_value == 0:
                        continue
                    
                    fund = {
                        'code': row['基金代码'],
                        'name': row['基金简称'],
                        'net_value': float(net_value),
                        'change_pct': float(change_pct),
                        'type': row.get('基金类型', '混合型'),
                        '手续费': row.get('手续费', 'N/A'),
                    }
                    
                    if fund_type and fund['type'] != fund_type:
                        continue
                        
                    funds.append(fund)
                except (ValueError, TypeError) as e:
                    # 跳过无法转换的行
                    continue
            
            logger.info(f"[AKShare] 获取到{len(funds)}只基金")
            return funds
            
        except Exception as e:
            logger.error(f"[AKShare] 获取全部基金失败：{e}")
            return []
    
    def fetch_history(self, fund_code: str, days: int = 90) -> List[Dict[str, Any]]:
        """
        获取基金历史净值
        
        Args:
            fund_code: 基金代码
            days: 获取天数
            
        Returns:
            List[Dict]: 历史净值列表
        """
        logger.info(f"[AKShare] 获取基金 {fund_code} 最近{days}天历史净值...")
        
        try:
            import akshare as ak
            
            fund_df = ak.fund_open_fund_info_em(fund=fund_code, indicator="单位净值走势")
            
            history = []
            for _, row in fund_df.head(days).iterrows():
                history.append({
                    'date': str(row.get('日期', '')),
                    'net_value': float(row.get('单位净值', 0)),
                    'accumulated_value': float(row.get('累计净值', 0)),
                })
            
            logger.info(f"[AKShare] 获取到{len(history)}条历史数据")
            return history
            
        except Exception as e:
            logger.error(f"[AKShare] 获取历史净值失败：{e}")
            return []
    
    def _get_fallback_data(self, fund_code: str) -> Dict[str, Any]:
        """获取兜底数据"""
        return {
            'code': fund_code,
            'name': '未知',
            'net_value': 0.0,
            'change': 0.0,
            'change_pct': 0.0,
            'update_date': '',
            'metadata': self.get_standard_metadata(),
            'error': '数据获取失败'
        }
