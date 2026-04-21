#!/usr/bin/env python3
"""
数据清洗器 - 清洗和标准化原始数据
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """数据清洗器"""
    
    def __init__(self):
        self.cleaning_rules = {
            'gold': self._clean_gold_data,
            'fund': self._clean_fund_data,
            'stock': self._clean_stock_data,
            'news': self._clean_news_data,
            'macro': self._clean_macro_data,
        }
    
    def clean(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """
        清洗数据
        
        Args:
            data: 原始数据
            data_type: 数据类型
            
        Returns:
            Dict[str, Any]: 清洗后的数据
        """
        logger.info(f"[数据清洗] 开始清洗 {data_type} 数据...")
        
        if data_type not in self.cleaning_rules:
            logger.warning(f"[数据清洗] 未知数据类型：{data_type}")
            return data
        
        try:
            cleaned = self.cleaning_rules[data_type](data)
            logger.info(f"[数据清洗] 清洗完成")
            return cleaned
        except Exception as e:
            logger.error(f"[数据清洗] 清洗失败：{e}")
            return data
    
    def _clean_gold_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗金价数据"""
        cleaned = {}
        
        # 清洗国际金价
        if 'international' in data:
            intl = data['international']
            cleaned['international'] = {
                'price': self._safe_float(intl.get('price', 0)),
                'change': self._safe_float(intl.get('change', 0)),
                'change_pct': self._safe_float(intl.get('change_pct', 0)),
                'currency': intl.get('currency', 'USD'),
                'unit': intl.get('unit', 'oz'),
            }
        
        # 清洗国内金价
        if 'domestic' in data:
            dom = data['domestic']
            cleaned['domestic'] = {
                'price': self._safe_float(dom.get('price', 0)),
                'change': self._safe_float(dom.get('change', 0)),
                'change_pct': self._safe_float(dom.get('change_pct', 0)),
                'currency': dom.get('currency', 'CNY'),
                'unit': dom.get('unit', 'g'),
            }
        
        # 保留元数据
        if 'metadata' in data:
            cleaned['metadata'] = data['metadata']
        
        return cleaned
    
    def _clean_fund_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗基金数据"""
        cleaned = {
            'code': str(data.get('code', '')),
            'name': str(data.get('name', '')).strip(),
            'net_value': self._safe_float(data.get('net_value', 0)),
            'change': self._safe_float(data.get('change', 0)),
            'change_pct': self._safe_float(data.get('change_pct', 0)),
            'update_date': self._parse_date(data.get('update_date', '')),
        }
        
        if 'metadata' in data:
            cleaned['metadata'] = data['metadata']
        
        return cleaned
    
    def _clean_stock_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗股票数据"""
        cleaned = {
            'code': str(data.get('code', '')),
            'name': str(data.get('name', '')).strip(),
            'price': self._safe_float(data.get('price', 0)),
            'change': self._safe_float(data.get('change', 0)),
            'change_pct': self._safe_float(data.get('change_pct', 0)),
            'volume': self._safe_float(data.get('volume', 0)),
            'amount': self._safe_float(data.get('amount', 0)),
            'turnover': self._safe_float(data.get('turnover', 0)),
            'pe': self._safe_float(data.get('pe', 0)),
            'pb': self._safe_float(data.get('pb', 0)),
        }
        
        if 'metadata' in data:
            cleaned['metadata'] = data['metadata']
        
        return cleaned
    
    def _clean_news_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗新闻数据"""
        cleaned_news = []
        
        news_list = data.get('news', [])
        for news in news_list:
            cleaned_news.append({
                'title': str(news.get('title', '')).strip(),
                'content': str(news.get('content', '')).strip(),
                'url': str(news.get('url', '')),
                'source': str(news.get('source', '')),
                'publish_date': self._parse_date(news.get('publish_date', '')),
                'category': news.get('category', 'general'),
            })
        
        return {
            'news': cleaned_news,
            'count': len(cleaned_news),
            'sources': data.get('sources', []),
            'metadata': data.get('metadata', {}),
        }
    
    def _clean_macro_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗宏观数据"""
        cleaned = {}
        
        # 清洗各指标
        for key in ['dxy', 'vix', 'oil', 'treasury']:
            if key in data:
                indicator = data[key]
                if isinstance(indicator, dict):
                    cleaned[key] = {
                        'name': indicator.get('name', ''),
                        'code': indicator.get('code', ''),
                        'value': self._safe_float(indicator.get('value', 0)),
                        'change': self._safe_float(indicator.get('change', 0)),
                        'change_pct': self._safe_float(indicator.get('change_pct', 0)),
                        'update_date': self._parse_date(indicator.get('update_date', '')),
                    }
                else:
                    cleaned[key] = indicator
        
        if 'metadata' in data:
            cleaned['metadata'] = data['metadata']
        
        return cleaned
    
    def _safe_float(self, value: Any) -> float:
        """安全转换为浮点数"""
        try:
            if value is None or value == '':
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        # 尝试多种格式
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y%m%d',
            '%Y-%m-%d %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return date_str  # 无法解析则返回原值
    
    def remove_duplicates(self, data_list: List[Dict], key: str = 'url') -> List[Dict]:
        """
        去重
        
        Args:
            data_list: 数据列表
            key: 去重键
            
        Returns:
            List[Dict]: 去重后的列表
        """
        seen = set()
        unique = []
        
        for item in data_list:
            key_value = item.get(key, '')
            if key_value and key_value not in seen:
                seen.add(key_value)
                unique.append(item)
        
        logger.info(f"[数据清洗] 去重：{len(data_list)} → {len(unique)}")
        return unique
