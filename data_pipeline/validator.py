#!/usr/bin/env python3
"""
数据验证器 - 验证数据完整性和有效性
"""

import logging
from typing import Any, Dict, List, Tuple
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.validation_rules = {
            'gold': self._validate_gold_data,
            'fund': self._validate_fund_data,
            'stock': self._validate_stock_data,
            'news': self._validate_news_data,
            'macro': self._validate_macro_data,
        }
        
        # 数据有效性范围（2024-2026 年合理范围）
        self.valid_ranges = {
            'gold_price_intl': (4000, 5000),    # 国际金价合理范围（美元/盎司）- 2026 年约$4500-4600
            'gold_price_domestic': (1000, 1200),  # 国内金价合理范围（元/克）- 2026 年约¥1070-1100
            'fund_net_value': (0, 100),  # 基金净值合理范围
            'stock_price': (0, 10000),  # 股价合理范围
            'change_pct': (-20, 20),  # 单日涨跌幅合理范围（A 股）
            'vix': (10, 100),  # VIX 合理范围
            'dxy': (50, 150),  # 美元指数合理范围
            'oil_price': (50, 150),  # 原油价格合理范围（美元/桶）
            'treasury_yield': (1, 10),  # 美债收益率合理范围（%）
        }
    
    def validate(self, data: Dict[str, Any], data_type: str) -> Tuple[bool, List[str]]:
        """
        验证数据
        
        Args:
            data: 待验证数据
            data_type: 数据类型
            
        Returns:
            Tuple[bool, List[str]]: (是否有效，错误信息列表)
        """
        logger.info(f"[数据验证] 开始验证 {data_type} 数据...")
        
        if data_type not in self.validation_rules:
            logger.warning(f"[数据验证] 未知数据类型：{data_type}")
            return True, []
        
        try:
            is_valid, errors = self.validation_rules[data_type](data)
            
            if is_valid:
                logger.info(f"[数据验证] 验证通过")
            else:
                logger.warning(f"[数据验证] 验证失败：{errors}")
            
            return is_valid, errors
        except Exception as e:
            logger.error(f"[数据验证] 验证异常：{e}")
            return False, [str(e)]
    
    def _validate_gold_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证金价数据"""
        errors = []
        warnings = []
        
        # 检查必需字段
        if 'international' not in data:
            errors.append("缺少国际金价数据")
        else:
            price = data['international'].get('price', 0)
            source = data['international'].get('source', '未知')
            
            # 检查价格范围
            if not self._in_range(price, 'gold_price_intl'):
                errors.append(f"国际金价异常：{price} (正常范围：${self.valid_ranges['gold_price_intl'][0]}-${self.valid_ranges['gold_price_intl'][1]})")
            else:
                logger.debug(f"[数据验证] 国际金价正常：${price} ({source})")
            
            # 检查数据源可信度
            if source == '兜底':
                warnings.append(f"⚠️ 国际金价使用兜底数据，可信度较低")
        
        if 'domestic' not in data:
            errors.append("缺少国内金价数据")
        else:
            price = data['domestic'].get('price', 0)
            source = data['domestic'].get('source', '未知')
            
            # 检查价格范围
            if not self._in_range(price, 'gold_price_domestic'):
                errors.append(f"国内金价异常：{price} (正常范围：¥{self.valid_ranges['gold_price_domestic'][0]}-¥{self.valid_ranges['gold_price_domestic'][1]})")
            else:
                logger.debug(f"[数据验证] 国内金价正常：¥{price} ({source})")
            
            # 检查数据源可信度
            if source == '兜底':
                warnings.append(f"⚠️ 国内金价使用兜底数据，可信度较低")
        
        # 打印警告
        for warning in warnings:
            logger.warning(f"[数据验证] {warning}")
        
        return len(errors) == 0, errors
    
    def _validate_fund_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证基金数据"""
        errors = []
        
        # 检查必需字段
        required = ['code', 'name', 'net_value']
        for field in required:
            if field not in data:
                errors.append(f"缺少必需字段：{field}")
        
        # 验证净值范围
        net_value = data.get('net_value', 0)
        if not self._in_range(net_value, 'fund_net_value'):
            errors.append(f"基金净值异常：{net_value}")
        
        # 验证涨跌幅
        change_pct = data.get('change_pct', 0)
        if not self._in_range(change_pct, 'change_pct'):
            errors.append(f"基金涨跌幅异常：{change_pct}%")
        
        return len(errors) == 0, errors
    
    def _validate_stock_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证股票数据"""
        errors = []
        
        # 检查必需字段
        required = ['code', 'name', 'price']
        for field in required:
            if field not in data:
                errors.append(f"缺少必需字段：{field}")
        
        # 验证股价范围
        price = data.get('price', 0)
        if not self._in_range(price, 'stock_price'):
            errors.append(f"股价异常：{price}")
        
        # 验证涨跌幅（A 股±10%，科创板±20%）
        change_pct = data.get('change_pct', 0)
        if abs(change_pct) > 30:  # 留一些缓冲
            errors.append(f"股价涨跌幅异常：{change_pct}%")
        
        return len(errors) == 0, errors
    
    def _validate_news_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证新闻数据"""
        errors = []
        
        # 检查必需字段
        if 'news' not in data:
            errors.append("缺少新闻列表")
            return len(errors) == 0, errors
        
        news_list = data['news']
        if not isinstance(news_list, list):
            errors.append("新闻列表格式错误")
            return len(errors) == 0, errors
        
        # 验证每条新闻
        for i, news in enumerate(news_list[:10]):  # 只检查前 10 条
            if 'title' not in news or not news['title']:
                errors.append(f"第{i+1}条新闻缺少标题")
        
        return len(errors) == 0, errors
    
    def _validate_macro_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证宏观数据"""
        errors = []
        
        # 验证 VIX
        if 'vix' in data:
            vix = data['vix'].get('value', 0)
            source = data['vix'].get('source', '未知')
            if vix > 0 and not self._in_range(vix, 'vix'):
                errors.append(f"VIX 异常：{vix} (正常范围：{self.valid_ranges['vix'][0]}-{self.valid_ranges['vix'][1]})")
            elif source == '兜底':
                logger.debug(f"[数据验证] VIX 使用兜底数据：{vix}")
        
        # 验证 DXY
        if 'dxy' in data:
            dxy = data['dxy'].get('value', 0)
            source = data['dxy'].get('source', '未知')
            if dxy > 0 and not self._in_range(dxy, 'dxy'):
                errors.append(f"DXY 异常：{dxy} (正常范围：{self.valid_ranges['dxy'][0]}-{self.valid_ranges['dxy'][1]})")
            elif source == '兜底':
                logger.debug(f"[数据验证] DXY 使用兜底数据：{dxy}")
        
        # 验证原油价格（新增）
        if 'oil' in data:
            oil = data['oil'].get('value', 0)
            source = data['oil'].get('source', '未知')
            if oil > 0 and not self._in_range(oil, 'oil_price'):
                errors.append(f"原油价格异常：${oil} (正常范围：${self.valid_ranges['oil_price'][0]}-${self.valid_ranges['oil_price'][1]})")
            elif source == '兜底':
                logger.debug(f"[数据验证] 原油使用兜底数据：${oil}")
        
        # 验证美债收益率（新增）
        if 'treasury' in data:
            treasury = data['treasury'].get('value', 0)
            source = data['treasury'].get('source', '未知')
            if treasury > 0 and not self._in_range(treasury, 'treasury_yield'):
                errors.append(f"美债收益率异常：{treasury}% (正常范围：{self.valid_ranges['treasury_yield'][0]}-{self.valid_ranges['treasury_yield'][1]}%)")
            elif source == '兜底':
                logger.debug(f"[数据验证] 美债使用兜底数据：{treasury}%")
        
        return len(errors) == 0, errors
    
    def _in_range(self, value: float, range_name: str) -> bool:
        """检查值是否在合理范围内"""
        if value == 0:
            return True  # 0 值可能是数据缺失，不视为异常
        
        if range_name not in self.valid_ranges:
            return True
        
        min_val, max_val = self.valid_ranges[range_name]
        return min_val <= value <= max_val
    
    def calculate_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算数据质量评分
        
        Args:
            data: 数据字典
            
        Returns:
            Dict: 包含评分、等级和问题列表
        """
        score = 100
        issues = []
        
        # 检查数据源
        for key in ['gold', 'fund', 'stock', 'macro']:
            if key not in data:
                continue
            
            data_item = data[key]
            if isinstance(data_item, dict):
                source = data_item.get('source', '')
                if source == '兜底':
                    score -= 10
                    issues.append(f'{key} 使用兜底数据')
                elif source == '缓存':
                    score -= 5
                    issues.append(f'{key} 使用缓存数据')
        
        # 检查数据时效性
        metadata = data.get('metadata', {})
        update_time = metadata.get('update_time', '')
        if update_time:
            try:
                update_dt = datetime.fromisoformat(update_time)
                age = (datetime.now() - update_dt).total_seconds()
                if age > 3600:  # 超过 1 小时
                    score -= 15
                    issues.append('数据过期 (>1 小时)')
                elif age > 300:  # 超过 5 分钟
                    score -= 5
                    issues.append('数据较旧 (>5 分钟)')
            except:
                pass
        
        # 检查数据完整性
        gold_prices = data.get('gold', {}).get('prices', [])
        if not gold_prices or len(gold_prices) < 10:
            score -= 10
            issues.append('金价数据不完整')
        
        # 计算等级
        if score >= 90:
            level = '优秀'
        elif score >= 70:
            level = '良好'
        elif score >= 50:
            level = '一般'
        else:
            level = '较差'
        
        return {
            'score': max(0, score),
            'level': level,
            'issues': issues,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_completeness(self, data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
        """
        检查数据完整性
        
        Args:
            data: 待检查数据
            required_fields: 必需字段列表
            
        Returns:
            Tuple[bool, List[str]]: (是否完整，缺失字段列表)
        """
        missing = []
        
        for field in required_fields:
            if field not in data:
                missing.append(field)
        
        return len(missing) == 0, missing
    
    def check_freshness(self, data: Dict[str, Any], max_age_hours: int = 24) -> Tuple[bool, str]:
        """
        检查数据新鲜度
        
        Args:
            data: 待检查数据
            max_age_hours: 最大允许年龄（小时）
            
        Returns:
            Tuple[bool, str]: (是否新鲜，数据时间)
        """
        metadata = data.get('metadata', {})
        fetched_at = metadata.get('fetched_at', '')
        
        if not fetched_at:
            return False, "无时间戳"
        
        try:
            fetch_time = datetime.fromisoformat(fetched_at)
            age = (datetime.now() - fetch_time).total_seconds() / 3600
            
            if age > max_age_hours:
                return False, f"{age:.1f}小时前"
            
            return True, f"{age:.1f}小时前"
        except Exception:
            return False, "时间解析失败"
