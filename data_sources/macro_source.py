#!/usr/bin/env python3
"""
宏观数据源 - 获取全球宏观经济数据

支持：
- 美元指数 (DXY)
- 恐慌指数 (VIX)
- 原油价格
- 美债收益率
- 美联储利率

数据源层级（fallback 机制）：
1. AKShare (主数据源)
2. Yahoo Finance API (备用 - 新增)
3. Investing.com 网络抓取 (补充 - 新增)
4. 百度搜索 (备用)
5. 兜底数据 (最后)
"""

import logging
import subprocess
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from data_sources.base import DataSource, DataSourceConfig

# 导入备用数据源
try:
    from data_sources.macro_api_source import MacroAPISource
    API_SOURCE_AVAILABLE = True
except ImportError:
    API_SOURCE_AVAILABLE = False
    logger.warning("MacroAPISource 不可用")

try:
    from data_sources.macro_web_source import MacroWebSource
    WEB_SOURCE_AVAILABLE = True
except ImportError:
    WEB_SOURCE_AVAILABLE = False
    logger.warning("MacroWebSource 不可用")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MacroDataSource(DataSource):
    """宏观数据源"""
    
    def __init__(self):
        config = DataSourceConfig(
            name='宏观数据聚合',
            source_type='macro',
            cache_enabled=True,
            cache_ttl=300,  # 宏观数据缓存 5 分钟
            retry_times=2,
            timeout=30,
        )
        super().__init__(config)
        
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化备用数据源
        if API_SOURCE_AVAILABLE:
            self.api_source = MacroAPISource()
            logger.debug("[宏观数据] API 源已初始化")
        else:
            self.api_source = None
        
        if WEB_SOURCE_AVAILABLE:
            self.web_source = MacroWebSource()
            logger.debug("[宏观数据] Web 源已初始化")
        else:
            self.web_source = None
        
        # 查找 search 脚本（多个可能位置）
        possible_paths = [
            Path(__file__).parent.parent.parent.parent / "scripts" / "search",
            Path(__file__).parent.parent / "baidu-search" / "scripts" / "search",
            Path("~//workspaces/YOUR_WORKSPACEH/customized_skills/baidu-search/scripts/search"),
            Path("~//workspaces/YOUR_WORKSPACEH/skills/baidu-search/scripts/search"),
        ]
        
        self.search_script = None
        for path in possible_paths:
            if path.exists():
                self.search_script = path
                logger.info(f"[宏观数据] 找到搜索脚本：{path}")
                break
        
        if not self.search_script:
            logger.warning("[宏观数据] 未找到搜索脚本，将使用兜底数据")
    
    def fetch(self, indicators: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """获取宏观指标数据"""
        logger.info("[宏观数据] 获取宏观指标数据...")
        
        result = {
            'dxy': self._fetch_dxy(),
            'vix': self._fetch_vix(),
            'oil': self._fetch_oil(),
            'treasury': self._fetch_treasury(),
            'metadata': self.get_standard_metadata()
        }
        
        logger.info(f"[宏观数据] DXY:{result['dxy']['value']}, VIX:{result['vix']['value']}, 原油:${result['oil']['value']}")
        return result
    
    def _search_web(self, query: str, count: int = 3) -> List[Dict[str, Any]]:
        """
        使用浏览器获取信息（备用方案）
        
        Args:
            query: 搜索关键词
            count: 结果数量
            
        Returns:
            List[Dict]: 搜索结果
        """
        # 搜索脚本不可用，返回空列表
        logger.warning(f"[宏观数据] 搜索脚本不可用，跳过搜索：{query}")
        return []
    
    def _extract_number(self, text: str, pattern: str, min_val: float, max_val: float) -> float:
        """从文本中提取数字"""
        try:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1))
                if min_val < value < max_val:
                    return value
        except:
            pass
        return 0.0
    
    def _fetch_dxy(self) -> Dict[str, Any]:
        """获取美元指数"""
        # 尝试 1: AKShare
        try:
            import akshare as ak
            dxy_df = ak.currency_boc_sina(symbol="美元指数")
            
            if not dxy_df.empty:
                latest = dxy_df.iloc[-1]
                return {
                    'name': '美元指数',
                    'code': 'DXY',
                    'value': float(latest.get('收盘', 0)),
                    'change': float(latest.get('涨跌额', 0)),
                    'change_pct': float(latest.get('涨跌幅', 0)),
                    'update_date': str(latest.get('日期', '')),
                    'source': 'AKShare'
                }
        except Exception as e:
            logger.warning(f"[宏观数据] AKShare 获取 DXY 失败：{e}")
        
        # 尝试 2: Yahoo Finance API (新增)
        if self.api_source:
            try:
                api_data = self.api_source.fetch_all()
                if api_data['dxy']['value'] > 0:
                    return api_data['dxy']
            except Exception as e:
                logger.warning(f"[宏观数据] API 源获取 DXY 失败：{e}")
        
        # 尝试 3: Investing.com 网络抓取 (新增)
        if self.web_source:
            try:
                web_data = self.web_source.fetch_all()
                if web_data['dxy']['value'] > 0:
                    return web_data['dxy']
            except Exception as e:
                logger.warning(f"[宏观数据] Web 源获取 DXY 失败：{e}")
        
        # 尝试 4: 百度搜索
        try:
            results = self._search_web("美元指数 实时行情", 3)
            for r in results:
                text = r.get('title', '') + ' ' + r.get('description', '')
                value = self._extract_number(text, r'(\d+\.?\d*)', 50, 150)
                if value > 0:
                    return {
                        'name': '美元指数',
                        'code': 'DXY',
                        'value': value,
                        'change': 0.0,
                        'change_pct': 0.0,
                        'update_date': datetime.now().strftime('%Y-%m-%d'),
                        'source': '百度搜索'
                    }
        except Exception as e:
            logger.warning(f"[宏观数据] 百度搜索 DXY 失败：{e}")
        
        return {'name': '美元指数', 'code': 'DXY', 'value': 0.0, 'change': 0.0, 'change_pct': 0.0, 'update_date': '', 'source': '兜底'}
    
    def _fetch_vix(self) -> Dict[str, Any]:
        """获取恐慌指数 VIX"""
        # 尝试 1: AKShare
        try:
            import akshare as ak
            vix_df = ak.index_vix_sina()
            
            if not vix_df.empty:
                latest = vix_df.iloc[-1]
                return {
                    'name': '恐慌指数',
                    'code': 'VIX',
                    'value': float(latest.get('close', 0)),
                    'change': float(latest.get('change', 0)),
                    'change_pct': float(latest.get('change_percent', 0)),
                    'update_date': str(latest.get('date', '')),
                    'source': 'AKShare'
                }
        except Exception as e:
            logger.warning(f"[宏观数据] AKShare 获取 VIX 失败：{e}")
        
        # 尝试 2: Yahoo Finance API (新增)
        if self.api_source:
            try:
                api_data = self.api_source.fetch_all()
                if api_data['vix']['value'] > 0:
                    return api_data['vix']
            except Exception as e:
                logger.warning(f"[宏观数据] API 源获取 VIX 失败：{e}")
        
        # 尝试 3: Investing.com 网络抓取 (新增)
        if self.web_source:
            try:
                web_data = self.web_source.fetch_all()
                if web_data['vix']['value'] > 0:
                    return web_data['vix']
            except Exception as e:
                logger.warning(f"[宏观数据] Web 源获取 VIX 失败：{e}")
        
        # 尝试 4: 百度搜索
        try:
            results = self._search_web("VIX 恐慌指数 实时", 3)
            for r in results:
                text = r.get('title', '') + ' ' + r.get('description', '')
                value = self._extract_number(text, r'(\d+\.?\d*)', 10, 100)
                if value > 0:
                    return {
                        'name': '恐慌指数',
                        'code': 'VIX',
                        'value': value,
                        'change': 0.0,
                        'change_pct': 0.0,
                        'update_date': datetime.now().strftime('%Y-%m-%d'),
                        'source': '百度搜索'
                    }
        except Exception as e:
            logger.warning(f"[宏观数据] 百度搜索 VIX 失败：{e}")
        
        return {'name': '恐慌指数', 'code': 'VIX', 'value': 0.0, 'change': 0.0, 'change_pct': 0.0, 'update_date': '', 'source': '兜底'}
    
    def _fetch_oil(self) -> Dict[str, Any]:
        """获取原油价格"""
        # 尝试 1: AKShare
        try:
            import akshare as ak
            oil_df = ak.futures_display_main_sina()
            
            for symbol in ['原油 2401', '原油 2402', '原油 2403', '原油主力']:
                oil_row = oil_df[oil_df['symbol'] == symbol]
                if not oil_row.empty:
                    latest = oil_row.iloc[0]
                    return {
                        'name': '原油期货',
                        'code': 'OIL',
                        'value': float(latest.get('price', 0)),
                        'change': float(latest.get('change', 0)),
                        'change_pct': float(latest.get('changepercent', 0)),
                        'update_date': str(latest.get('date', '')),
                        'source': 'AKShare'
                    }
        except Exception as e:
            logger.warning(f"[宏观数据] AKShare 获取原油失败：{e}")
        
        # 尝试 2: Yahoo Finance API (新增)
        if self.api_source:
            try:
                api_data = self.api_source.fetch_all()
                if api_data['oil']['value'] > 0:
                    return api_data['oil']
            except Exception as e:
                logger.warning(f"[宏观数据] API 源获取原油失败：{e}")
        
        # 尝试 3: Investing.com 网络抓取 (新增)
        if self.web_source:
            try:
                web_data = self.web_source.fetch_all()
                if web_data['oil']['value'] > 0:
                    return web_data['oil']
            except Exception as e:
                logger.warning(f"[宏观数据] Web 源获取原油失败：{e}")
        
        # 尝试 4: 百度搜索
        try:
            results = self._search_web("国际原油价格 实时 美元", 3)
            for r in results:
                text = r.get('title', '') + ' ' + r.get('description', '')
                value = self._extract_number(text, r'(\d+\.?\d*)', 50, 150)
                if value > 0:
                    return {
                        'name': '原油期货',
                        'code': 'OIL',
                        'value': value,
                        'change': 0.0,
                        'change_pct': 0.0,
                        'update_date': datetime.now().strftime('%Y-%m-%d'),
                        'source': '百度搜索'
                    }
        except Exception as e:
            logger.warning(f"[宏观数据] 百度搜索原油失败：{e}")
        
        return {'name': '原油期货', 'code': 'OIL', 'value': 0.0, 'change': 0.0, 'change_pct': 0.0, 'update_date': '', 'source': '兜底'}
    
    def _fetch_treasury(self) -> Dict[str, Any]:
        """获取美债收益率"""
        # 尝试 1: AKShare
        try:
            import akshare as ak
            treasury_df = ak.bond_zh_us_rate()
            
            if not treasury_df.empty:
                latest = treasury_df.iloc[-1]
                # 修复：使用正确的字段名
                value = latest.get('美国国债收益率 10 年', 0)
                if value and value > 0:
                    return {
                        'name': '10 年期美债收益率',
                        'code': 'US10Y',
                        'value': float(value),
                        'change': 0.0,
                        'change_pct': 0.0,
                        'update_date': str(latest.get('日期', '')),
                        'source': 'AKShare'
                    }
        except Exception as e:
            logger.warning(f"[宏观数据] AKShare 获取美债失败：{e}")
        
        # 尝试 2: Yahoo Finance API (新增)
        if self.api_source:
            try:
                api_data = self.api_source.fetch_all()
                if api_data['treasury']['value'] > 0:
                    return api_data['treasury']
            except Exception as e:
                logger.warning(f"[宏观数据] API 源获取美债失败：{e}")
        
        # 尝试 3: Investing.com 网络抓取 (新增)
        if self.web_source:
            try:
                web_data = self.web_source.fetch_all()
                if web_data['treasury']['value'] > 0:
                    return web_data['treasury']
            except Exception as e:
                logger.warning(f"[宏观数据] Web 源获取美债失败：{e}")
        
        # 尝试 4: 百度搜索
        try:
            results = self._search_web("美国 10 年期国债收益率", 3)
            for r in results:
                text = r.get('title', '') + ' ' + r.get('description', '')
                value = self._extract_number(text, r'(\d+\.?\d*)%', 1, 10)
                if value > 0:
                    return {
                        'name': '10 年期美债收益率',
                        'code': 'US10Y',
                        'value': value,
                        'change': 0.0,
                        'change_pct': 0.0,
                        'update_date': datetime.now().strftime('%Y-%m-%d'),
                        'source': '百度搜索'
                    }
        except Exception as e:
            logger.warning(f"[宏观数据] 百度搜索美债失败：{e}")
        
        return {'name': '10 年期美债收益率', 'code': 'US10Y', 'value': 0.0, 'change': 0.0, 'change_pct': 0.0, 'update_date': '', 'source': '兜底'}
    
    def analyze_market_sentiment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析市场情绪"""
        score = 0.0
        
        vix = data['vix']['value']
        if vix > 0:
            if vix < 15:
                score += 0.3
            elif vix > 30:
                score -= 0.3
        
        dxy = data['dxy']['value']
        if dxy > 0:
            if 95 < dxy < 105:
                score += 0.1
            elif dxy > 110 or dxy < 90:
                score -= 0.1
        
        if score > 0.2:
            sentiment = 'risk_on'
        elif score < -0.2:
            sentiment = 'risk_off'
        else:
            sentiment = 'neutral'
        
        result = {
            'sentiment': sentiment,
            'score': round(score, 3),
            'vix_level': 'low' if vix < 20 else ('high' if vix > 30 else 'normal'),
            'dxy_level': 'high' if dxy > 105 else ('low' if dxy < 95 else 'normal'),
        }
        
        logger.info(f"[宏观数据] 市场情绪：{sentiment} (score: {score})")
        return result
    
    def get_market_sentiment(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """获取市场情绪（兼容旧接口）"""
        if data is None:
            data = self.fetch()
        return self.analyze_market_sentiment(data)
